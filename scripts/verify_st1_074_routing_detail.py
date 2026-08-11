#!/usr/bin/env python3
"""Verify ST1-074 per-record routing-detail contracts."""
from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = ROOT / "implementation" / "ingestion-service"
IMAGE = "enterprise-ai-st1-074-routing-detail-test"

REMOTE = r'''
import hashlib,json,os,psycopg
from datetime import datetime,timezone,timedelta

def h(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

now = datetime.now(timezone.utc)
results = {}

with psycopg.connect(
    host=os.environ['INGESTION_DB_HOST'],
    port=os.environ.get('INGESTION_DB_PORT','5432'),
    dbname=os.environ['INGESTION_DB_NAME'],
    user=os.environ['INGESTION_DB_USER'],
    password=os.environ['INGESTION_DB_PASSWORD'],
) as c:
    with c.cursor() as q:
        q.execute("SELECT count(*) FROM ingestion.sdas_active_delegation_bootstrap")
        results['real_active_delegations'] = q.fetchone()[0]
        q.execute("INSERT INTO ingestion.sdas_policy_versions (policy_id,policy_version,effective_from,enabled,allowed_source_types,allowed_data_classes,required_evidence,risk_class,decision_reason_codes,actor_authority_requirements,policy_hash) VALUES ('project-controls-progress-low-risk','v1',%s,true,%s::jsonb,%s::jsonb,%s::jsonb,'low',%s::jsonb,%s::jsonb,%s) ON CONFLICT (policy_id,policy_version) DO NOTHING", (now - timedelta(days=1), json.dumps(['synthetic_detail_report']), json.dumps(['synthetic_detail_report']), json.dumps(['all_required_policy_evidence_present']), json.dumps(['human_required']), json.dumps(['delegation_or_human_review']), h({'policy-version': 'st1-074'})))

        def insert_delegation(project_scope, document_class):
            approval = f"st1-074-approval-{project_scope}"
            proposal = f"st1-074-proposal-{project_scope}"
            gov = f"st1-074-governance-{project_scope}"
            pmo = f"st1-074-pmo-{project_scope}"
            source = f"st1-074-source-{project_scope}"
            q.execute("INSERT INTO ingestion.sdas_governance_policy_approvals (approval_id,policy_id,policy_version,governance_policy_status,approver_identity_state,approval_basis_reference,policy_scope,approved_at,evidence_fingerprint,event_hash) VALUES (%s,'test','v1','approved_for_pilot','verified','synthetic_test',%s::jsonb,%s,%s,%s)", (approval, json.dumps({'project_scope': project_scope}), now, h({'approval': approval}), h({'approval-event': approval})))
            q.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_proposals (proposal_id,approval_id,intended_role_class,project_scope,source_system_identity_state,document_data_classes,permitted_fact_classes,prohibited_fact_classes,business_time_rule,policy_version,initial_state,created_at,evidence_fingerprint,event_hash) VALUES (%s,%s,'synthetic project controls',%s,'verified',%s::jsonb,'[]'::jsonb,'[]'::jsonb,'{}'::jsonb,'v1','PROPOSED',%s,%s,%s)", (proposal, approval, project_scope, json.dumps([document_class]), now, h({'proposal': proposal}), h({'proposal-event': proposal})))
            q.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'GOVERNANCE_APPROVED',%s,'synthetic_test',%s,%s)", (proposal, now, h({'proposal': proposal, 's': 'g'}), h({'proposal': proposal, 'e': 'g'})))
            q.execute("INSERT INTO ingestion.sdas_actor_registry (actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality) VALUES (%s,'synthetic governance','[]'::jsonb,'synthetic_test',%s,'native'),(%s,'synthetic pmo','[]'::jsonb,'synthetic_test',%s,'native')", (gov, now, pmo, now))
            q.execute("INSERT INTO ingestion.sdas_role_identity_verifications (actor_id,role_class,project_scope,evidence_reference,evidence_fingerprint,verification_method,evidence_quality,effective_from,event_hash) VALUES (%s,'CEO / Executive Governance Authority',%s,'synthetic_test',%s,'synthetic','native',%s,%s),(%s,'synthetic project controls',%s,'synthetic_test',%s,'synthetic','native',%s,%s)", (gov, project_scope, h({'verify': gov}), now, h({'verify-event': gov}), pmo, project_scope, h({'verify': pmo}), now, h({'verify-event': pmo})))
            q.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,governance_actor_id,accountable_actor_id,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'IDENTITY_VERIFIED',%s,%s,%s,'synthetic_test',%s,%s)", (proposal, gov, pmo, now, h({'proposal': proposal, 's': 'i'}), h({'proposal': proposal, 'e': 'i'})))
            q.execute("INSERT INTO ingestion.sdas_source_registry (source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,effective_from,evidence_quality) VALUES (%s,%s,'runtime_local_only',%s,'synthetic verification','verified_limited',%s::jsonb,%s,'native')", (source, document_class, pmo, json.dumps({'project_scope': project_scope}), now))
            q.execute("INSERT INTO ingestion.sdas_source_control_verifications (source_id,accountable_actor_id,project_scope,document_data_class,business_time_rule,evidence_reference,evidence_fingerprint,evidence_quality,effective_from,event_hash) VALUES (%s,%s,%s,%s,'approved_report_header','synthetic_test',%s,'native',%s,%s)", (source, pmo, project_scope, document_class, h({'source-control': source}), now, h({'source-control-event': source})))
            q.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,source_id,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'SOURCE_VERIFIED',%s,%s,'synthetic_test',%s,%s)", (proposal, source, now, h({'proposal': proposal, 's': 's'}), h({'proposal': proposal, 'e': 's'})))
            q.execute("INSERT INTO ingestion.sdas_delegation_bootstrap_events (proposal_id,transition_state,event_at,evidence_reference,evidence_fingerprint,event_hash) VALUES (%s,'ACTIVE',%s,'synthetic_test',%s,%s)", (proposal, now, h({'proposal': proposal, 's': 'a'}), h({'proposal': proposal, 'e': 'a'})))
            return source

        matched_source = insert_delegation('synthetic_project_detail_matched', 'synthetic_detail_report')
        waiting_source = 'st1-074-source-waiting'
        q.execute("INSERT INTO ingestion.sdas_actor_registry (actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality) VALUES ('st1-074-owner-waiting','synthetic owner','[]'::jsonb,'synthetic_test',%s,'native')", (now,))
        q.execute("INSERT INTO ingestion.sdas_source_registry (source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,effective_from,evidence_quality) VALUES (%s,'synthetic_detail_report','runtime_local_only','st1-074-owner-waiting','synthetic verification','declared_unverified',%s::jsonb,%s,'declared_unverified')", (waiting_source, json.dumps({'project_scope': 'synthetic_project_detail_waiting'}), now))

        def insert_record(name, *, source_id, policy_mode=None, assurance_outcome=None, assurance_reasons=None, authority='eligible', business_time='valid', currentness='current_eligible', reliance='not_eligible', risk='low'):
            record_fp = h({'record': name})
            q.execute("INSERT INTO ingestion.credibility_records (record_fingerprint,canonical_record,provenance,source_id,record_id,observed_at,disposition,quality_gate_outcome,lifecycle_state) VALUES (%s,%s::jsonb,%s::jsonb,%s,%s,%s,'certification_candidate','passed','certification_candidate')", (record_fp, json.dumps({'source_id': source_id, 'record_id': name, 'payload': {'statement': name}}), json.dumps({'source_reference': 'runtime_local_only'}), source_id, name, now - timedelta(days=1)))
            if policy_mode is not None:
                q.execute("INSERT INTO ingestion.sdas_policy_decisions (record_fingerprint,policy_id,policy_version,approval_mode,decision_actor,decision_reasons,evidence_quality,decision_hash) VALUES (%s,'project-controls-progress-low-risk','v1',%s,'sahra_policy_engine',%s::jsonb,'native',%s)", (record_fp, policy_mode, json.dumps(['synthetic_policy']), h({'policy': name})))
            if assurance_outcome is not None:
                q.execute("INSERT INTO ingestion.sdas_assurance_decisions (record_fingerprint,authority_inheritance_state,business_time_state,risk_tier,currentness_state,reliance_state,outcome,reason_codes,policy_version,decided_at,actor_id,evidence_fingerprint,event_hash) VALUES (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,'v1',%s,'sahra_policy_engine',%s,%s)", (record_fp, authority, business_time, risk, currentness, reliance, assurance_outcome, json.dumps(assurance_reasons or []), now, h({'evidence': name}), h({'assurance': name})))
            return record_fp

        fingerprints = {
            'matched_auto': insert_record('matched-auto', source_id=matched_source, policy_mode='policy_automatic', assurance_outcome='policy_automatic', assurance_reasons=['all_required_policy_evidence_present']),
            'waiting_external': insert_record('waiting-external', source_id=waiting_source, policy_mode='policy_automatic', assurance_outcome='policy_automatic', assurance_reasons=['authority_not_verified'], authority='missing'),
            'explicit_human': insert_record('explicit-human', source_id=waiting_source, policy_mode='human_required', assurance_outcome='human_required', assurance_reasons=['evidence_conflict'], authority='missing', business_time='missing'),
            'quarantine': insert_record('quarantine', source_id=waiting_source, policy_mode='reject_or_quarantine', assurance_outcome='reject_or_quarantine', assurance_reasons=['integrity_or_validation_failed'], authority='conflict', business_time='conflict', risk='high'),
            'missing_policy': insert_record('missing-policy', source_id=waiting_source),
        }

        q.execute("SELECT count(*) FROM information_schema.views WHERE table_schema='ingestion' AND table_name='sdas_record_policy_routing_detail'")
        results['detail_view_exists'] = q.fetchone()[0] == 1
        q.execute("SELECT has_table_privilege('enterprise_ai_ingestion_runtime','ingestion.sdas_record_policy_routing_detail','SELECT')")
        results['runtime_detail_select_granted'] = q.fetchone()[0]
        detail_rows = {}
        for name, fp in fingerprints.items():
            q.execute("SELECT effective_routing_outcome, governance_dependency_state, effective_reason_codes, triage_signals, jsonb_array_length(matched_active_delegations) FROM ingestion.sdas_record_policy_routing_detail WHERE record_fingerprint=%s", (fp,))
            detail_rows[name] = q.fetchone()
        q.execute("SAVEPOINT mutate")
        try:
            q.execute("UPDATE ingestion.sdas_source_registry SET authority_status='authoritative' WHERE source_id=%s", (waiting_source,))
            results['unauthorized_mutation_rejected'] = False
        except psycopg.Error:
            q.execute("ROLLBACK TO SAVEPOINT mutate")
            results['unauthorized_mutation_rejected'] = True
    c.rollback()

results['detail_rows'] = {
    key: {
        'effective_routing_outcome': value[0],
        'governance_dependency_state': value[1],
        'effective_reason_codes': value[2],
        'triage_signals': value[3],
        'matched_active_delegation_length': value[4],
    }
    for key, value in detail_rows.items()
}
print(json.dumps(results, sort_keys=True, separators=(',', ':')))
'''


def main() -> None:
    docker_build = subprocess.run(["docker", "build", "-t", IMAGE, str(SERVICE_DIR)], text=True, capture_output=True)
    if docker_build.returncode:
        raise SystemExit(docker_build.stderr.strip() or "ST1-074 local image build failed")
    local_smoke = subprocess.run(
        [
            "docker", "run", "--rm", "--entrypoint", "python", IMAGE, "-c",
            "import json,threading,time,urllib.request,urllib.error,app; from http.server import ThreadingHTTPServer; srv=ThreadingHTTPServer(('127.0.0.1',8085), app.IngestionHandler); t=threading.Thread(target=srv.serve_forever,daemon=True); t.start(); time.sleep(0.3); out=[]\nfor path in ['/health','/v1/sdas/routing/detail?record_fingerprint=bad']:\n    try:\n        with urllib.request.urlopen('http://127.0.0.1:8085'+path) as r:\n            out.append({'path':path,'status':r.status})\n    except urllib.error.HTTPError as e:\n        out.append({'path':path,'status':e.code})\nprint(json.dumps(out,separators=(',',':'))); srv.shutdown()"
        ],
        text=True,
        capture_output=True,
    )
    if local_smoke.returncode:
        raise SystemExit(local_smoke.stderr.strip() or "ST1-074 local route smoke failed")
    payload = base64.b64encode(REMOTE.encode()).decode()
    command = "docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('" + payload + "'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], text=True, capture_output=True)
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "ST1-074 verification failed")
    observed = json.loads(run.stdout)
    output = {
        "detail_view_exists": observed["detail_view_exists"],
        "runtime_detail_select_granted": observed["runtime_detail_select_granted"],
        "matched_auto": observed["detail_rows"]["matched_auto"],
        "waiting_external": observed["detail_rows"]["waiting_external"],
        "explicit_human": observed["detail_rows"]["explicit_human"],
        "quarantine": observed["detail_rows"]["quarantine"],
        "missing_policy": observed["detail_rows"]["missing_policy"],
        "unauthorized_mutation_rejected": observed["unauthorized_mutation_rejected"],
        "real_active_delegations": observed["real_active_delegations"],
        "local_smoke": json.loads(local_smoke.stdout),
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
