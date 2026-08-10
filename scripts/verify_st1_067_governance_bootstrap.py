#!/usr/bin/env python3
"""Verify ST1-067 lifecycle guards with a rolled-back synthetic transaction."""

from __future__ import annotations

import base64
import subprocess


REMOTE = r'''
import hashlib, json, os, psycopg
from datetime import datetime, timezone

def h(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def scalar(cur, query, params=()):
    cur.execute(query, params)
    return cur.fetchone()[0]

now = datetime.now(timezone.utc)
actual_policy = 'sdas-governance-policy-pilot-v1'
actual_proposal = 'sdas-bootstrap-maroon-project-controls-v1'
result = {}
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'], port=os.environ.get('INGESTION_DB_PORT', '5432'), dbname=os.environ['INGESTION_DB_NAME'], user=os.environ['INGESTION_DB_USER'], password=os.environ['INGESTION_DB_PASSWORD']) as conn:
  with conn.cursor() as cur:
    result['policy_approved_for_pilot'] = scalar(cur, "SELECT count(*) FROM ingestion.sdas_governance_policy_approvals WHERE approval_id=%s AND governance_policy_status='approved_for_pilot'", (actual_policy,)) == 1
    result['pending_proposal'] = scalar(cur, "SELECT count(*) FROM ingestion.sdas_delegation_bootstrap_proposals WHERE proposal_id=%s", (actual_proposal,)) == 1
    result['active_real_delegations'] = scalar(cur, "SELECT count(*) FROM ingestion.sdas_active_delegation_bootstrap")
    result['st1_061_authority_assertions'] = scalar(cur, "SELECT count(*) FROM ingestion.sdas_authority_assertions")
    result['st1_061_business_time_evidence'] = scalar(cur, "SELECT count(*) FROM ingestion.sdas_business_time_evidence")

    # Every test write below remains inside this transaction and is rolled back.
    approval = 'st1-067-test-approval'
    proposal = 'st1-067-test-proposal'
    gov = 'st1-067-test-governance-role'
    pmo = 'st1-067-test-project-controls-role'
    source = 'st1-067-test-verified-source'
    cur.execute("INSERT INTO ingestion.sdas_governance_policy_approvals (approval_id,policy_id,policy_version,governance_policy_status,approver_identity_state,approval_basis_reference,policy_scope,approved_at,evidence_fingerprint,event_hash) VALUES (%s,'test','v1','approved_for_pilot','unverified','synthetic_test', '{}'::jsonb,%s,%s,%s)", (approval,now,h({'a':approval}),h({'e':approval})))
    cur.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_proposals (proposal_id,approval_id,intended_role_class,project_scope,source_system_identity_state,document_data_classes,permitted_fact_classes,prohibited_fact_classes,business_time_rule,policy_version,initial_state,created_at,evidence_fingerprint,event_hash) VALUES (%s,%s,'synthetic project controls','synthetic_project','required','[]'::jsonb,'[]'::jsonb,'[]'::jsonb,'{}'::jsonb,'v1','PROPOSED',%s,%s,%s)", (proposal,approval,now,h({'p':proposal}),h({'ep':proposal})))
    cur.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'GOVERNANCE_APPROVED',%s,'synthetic_test',%s,%s)", (proposal,now,h({'p':proposal,'s':'g'}),h({'p':proposal,'e':'g'})))
    result['inactive_not_usable'] = scalar(cur, "SELECT count(*) FROM ingestion.sdas_active_delegation_bootstrap WHERE proposal_id=%s", (proposal,)) == 0

    cur.execute('SAVEPOINT premature_activation')
    try:
      cur.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'ACTIVE',%s,'synthetic_test',%s,%s)", (proposal,now,h({'p':proposal,'s':'bad'}),h({'p':proposal,'e':'bad'})))
      result['premature_activation_rejected'] = False
    except psycopg.Error:
      cur.execute('ROLLBACK TO SAVEPOINT premature_activation')
      result['premature_activation_rejected'] = True

    cur.execute("INSERT INTO ingestion.sdas_actor_registry (actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality) VALUES (%s,'synthetic governance role','[]'::jsonb,'synthetic_test',%s,'native'),(%s,'synthetic project controls role','[]'::jsonb,'synthetic_test',%s,'native')", (gov,now,pmo,now))
    cur.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,governance_actor_id,accountable_actor_id,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'IDENTITY_VERIFIED',%s,%s,%s,'synthetic_test',%s,%s)", (proposal,gov,pmo,now,h({'p':proposal,'s':'i'}),h({'p':proposal,'e':'i'})))
    cur.execute("INSERT INTO ingestion.sdas_source_registry (source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,evidence_quality) VALUES (%s,'synthetic_test','private_runtime',%s,'synthetic test','verified_limited',%s::jsonb,'native')", (source,pmo,json.dumps({'project_scope':'synthetic_project'})))
    cur.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,source_id,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'SOURCE_VERIFIED',%s,%s,'synthetic_test',%s,%s)", (proposal,source,now,h({'p':proposal,'s':'s'}),h({'p':proposal,'e':'s'})))
    cur.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'ACTIVE',%s,'synthetic_test',%s,%s)", (proposal,now,h({'p':proposal,'s':'a'}),h({'p':proposal,'e':'a'})))
    result['fully_verified_synthetic_active'] = scalar(cur, "SELECT count(*) FROM ingestion.sdas_active_delegation_bootstrap WHERE proposal_id=%s", (proposal,)) == 1

    cur.execute('SAVEPOINT append_only')
    try:
      cur.execute("UPDATE ingestion.sdas_delegation_bootstrap_proposals SET project_scope='changed' WHERE proposal_id=%s", (proposal,))
      result['append_only_update_rejected'] = False
    except psycopg.Error:
      cur.execute('ROLLBACK TO SAVEPOINT append_only')
      result['append_only_update_rejected'] = True
  conn.rollback()

result['automatic_certification'] = False
result['synthetic_test_persisted'] = False
print(json.dumps(result, separators=(',', ':'), sort_keys=True))
'''


def main() -> None:
    payload = base64.b64encode(REMOTE.encode()).decode()
    command = (
        "docker exec -i deploy-ingestion-service-1 python3 -c "
        f"\"import base64;exec(base64.b64decode('{payload}'))\""
    )
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "ST1-067 verification failed")
    print(result.stdout.strip())


if __name__ == "__main__":
    main()
