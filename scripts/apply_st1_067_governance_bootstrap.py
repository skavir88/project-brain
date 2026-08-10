#!/usr/bin/env python3
"""Record only ST1-067's pilot policy approval and pending proposal.

This uses no organizational actor or source identity.  It is idempotent and
does not create an active delegation, authority assertion, policy decision,
or certification.
"""

from __future__ import annotations

import base64
import subprocess


REMOTE = r'''
import hashlib, json, os, psycopg
from datetime import datetime, timezone

def h(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

approval_id = 'sdas-governance-policy-pilot-v1'
proposal_id = 'sdas-bootstrap-maroon-project-controls-v1'
policy_version = 'project-controls-progress-low-risk/v1'
scope = {
  'project_scope': 'maroon_pilot_project',
  'intended_role_class': 'Project Controls / PMO accountable owner',
  'source_system_identity': 'REQUIRED_INPUT',
  'document_data_classes': [
    'recurring_project_controls_progress_report',
    'recurring_project_controls_status_report',
    'recurring_project_controls_progress_workbook'
  ],
  'permitted_fact_classes': [
    'report_period', 'reported_plan', 'reported_actual', 'reported_progress',
    'reported_activity', 'reported_milestone', 'reported_project_control_issue'
  ],
  'prohibited_fact_classes': [
    'contractual_delay_determination', 'entitlement', 'claim_validity',
    'payment_authorization', 'financial_liability', 'legal_conclusion',
    'safety_or_compliance_certification', 'final_completion',
    'current_executive_status_outside_certified_currentness_policy',
    'reliance_eligibility', 'insured_or_guaranteed_status'
  ]
}
business_time = {
  'accepted': ['approved_report_header', 'registered_source_system_period_field',
               'document_control_evidence', 'accountable_owner_attestation'],
  'disallowed': ['filesystem_timestamp', 'acquisition_timestamp']
}
now = datetime.now(timezone.utc)
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'], port=os.environ.get('INGESTION_DB_PORT', '5432'), dbname=os.environ['INGESTION_DB_NAME'], user=os.environ['INGESTION_DB_USER'], password=os.environ['INGESTION_DB_PASSWORD']) as conn:
  with conn.cursor() as cur:
    cur.execute("""INSERT INTO ingestion.sdas_governance_policy_approvals
      (approval_id, policy_id, policy_version, governance_policy_status,
       approver_identity_state, approval_basis_reference, policy_scope,
       approved_at, evidence_fingerprint, event_hash)
      VALUES (%s, %s, %s, 'approved_for_pilot', 'unverified',
              'user_directed_ST1_067_governance_policy_model', %s::jsonb,
              %s, %s, %s)
      ON CONFLICT (approval_id) DO NOTHING""",
      (approval_id, 'sdas-governance-bootstrap', policy_version, json.dumps(scope), now,
       h({'approval_id': approval_id, 'scope': scope}), h({'approval_id': approval_id, 'event': 'approved_for_pilot'})))
    cur.execute("""INSERT INTO ingestion.sdas_governance_policy_approval_events
      (approval_id, event_type, event_at, evidence_reference, evidence_fingerprint, event_hash)
      VALUES (%s, 'approved_for_pilot', %s,
              'user_directed_ST1_067_governance_policy_model', %s, %s)
      ON CONFLICT (event_hash) DO NOTHING""",
      (approval_id, now, h({'approval_id': approval_id, 'event': 'approved_for_pilot'}), h({'approval_id': approval_id, 'event_hash': 'approval'})))
    cur.execute("""INSERT INTO ingestion.sdas_delegation_bootstrap_proposals
      (proposal_id, approval_id, intended_role_class, project_scope,
       source_system_identity_state, document_data_classes, permitted_fact_classes,
       prohibited_fact_classes, business_time_rule, policy_version, initial_state,
       created_at, evidence_fingerprint, event_hash)
      VALUES (%s, %s, %s, 'maroon_pilot_project', 'required', %s::jsonb,
              %s::jsonb, %s::jsonb, %s::jsonb, %s, 'PROPOSED', %s, %s, %s)
      ON CONFLICT (proposal_id) DO NOTHING""",
      (proposal_id, approval_id, scope['intended_role_class'],
       json.dumps(scope['document_data_classes']), json.dumps(scope['permitted_fact_classes']),
       json.dumps(scope['prohibited_fact_classes']), json.dumps(business_time), policy_version,
       now, h({'proposal_id': proposal_id, 'scope': scope, 'business_time': business_time}),
       h({'proposal_id': proposal_id, 'event': 'proposed'})))
    cur.execute("SELECT EXISTS(SELECT 1 FROM ingestion.sdas_delegation_bootstrap_events WHERE proposal_id=%s AND transition_state='GOVERNANCE_APPROVED')", (proposal_id,))
    if not cur.fetchone()[0]:
      cur.execute("""INSERT INTO ingestion.sdas_delegation_bootstrap_events
        (proposal_id, transition_state, event_at, evidence_reference,
         evidence_fingerprint, event_hash)
        VALUES (%s, 'GOVERNANCE_APPROVED', %s,
                'user_directed_ST1_067_governance_policy_model', %s, %s)""",
        (proposal_id, now, h({'proposal_id': proposal_id, 'state': 'GOVERNANCE_APPROVED'}),
         h({'proposal_id': proposal_id, 'event': 'governance_approved'})))
    cur.execute("SELECT (SELECT count(*) FROM ingestion.sdas_governance_policy_approvals WHERE approval_id=%s), (SELECT count(*) FROM ingestion.sdas_delegation_bootstrap_proposals WHERE proposal_id=%s), (SELECT count(*) FROM ingestion.sdas_active_delegation_bootstrap WHERE proposal_id=%s)", (approval_id, proposal_id, proposal_id))
    policy_count, proposal_count, active_count = cur.fetchone()
    print(json.dumps({'governance_policy_approved_for_pilot': policy_count == 1, 'pending_proposal': proposal_count == 1, 'active_delegation': active_count == 1, 'automatic_certification': False}, separators=(',', ':')))
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
        raise SystemExit(result.stderr.strip() or "ST1-067 bootstrap failed")
    print(result.stdout.strip())


if __name__ == "__main__":
    main()
