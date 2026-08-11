#!/usr/bin/env python3
"""Verify ST1-072 assurance-summary and exception-queue contracts."""
from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = ROOT / "implementation" / "ingestion-service"
IMAGE = "enterprise-ai-st1-072-summary-test"

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
        q.execute("SELECT verification_result, passport_count FROM ingestion.sdas_assurance_passport_portfolio_summary")
        baseline_summary = dict(q.fetchall())
        q.execute("SELECT verification_result, count(*) FROM ingestion.sdas_assurance_passport_exception_queue GROUP BY verification_result")
        baseline_queue = dict(q.fetchall())
        q.execute("SELECT count(*) FROM ingestion.sdas_assurance_passport_exception_queue")
        baseline_queue_total = q.fetchone()[0]

        def mk_case(name, *, source_authority='authoritative', authority_state='eligible', business_time_state='valid',
                    currentness='current_eligible', reliance='not_eligible',
                    base_result='VERIFIED', risk='low', post_event=None,
                    limitation_codes=None):
            actor = f"st1-072-actor-{name}"
            source_id = f"st1-072-source-{name}"
            record_fp = h({'record': name})
            knowledge_id = h({'knowledge': name})
            cert_ts = now - timedelta(minutes=len(results) + 1)
            q.execute(
                "INSERT INTO ingestion.sdas_actor_registry (actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality) VALUES (%s,'synthetic operator','[]'::jsonb,'synthetic',%s,'native')",
                (actor, now),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_source_registry (source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,effective_from,evidence_quality) VALUES (%s,'synthetic_workbook','runtime_local_only',%s,'synthetic verification',%s,%s::jsonb,%s,'native')",
                (source_id, actor, source_authority, json.dumps({'project_scope': 'synthetic_project'}), now),
            )
            q.execute(
                "INSERT INTO ingestion.credibility_records (record_fingerprint,canonical_record,provenance,source_id,record_id,observed_at,disposition,quality_gate_outcome,lifecycle_state,certification_timestamp,certification_actor,certification_policy_version) VALUES (%s,%s::jsonb,%s::jsonb,%s,%s,%s,'certification_candidate','passed','certified',%s,%s,'synthetic-cert-v1')",
                (record_fp, json.dumps({'source_id': source_id, 'record_id': name, 'payload': {'statement': name}}), json.dumps({'source_reference': 'runtime_local_only'}), source_id, name, now - timedelta(days=1), cert_ts, actor),
            )
            q.execute(
                "INSERT INTO ingestion.certification_audit_events (record_fingerprint,previous_lifecycle_state,new_lifecycle_state,certification_timestamp,actor_identifier,policy_version) VALUES (%s,'certification_candidate','certified',%s,%s,'synthetic-cert-v1') RETURNING event_id",
                (record_fp, cert_ts, actor),
            )
            cert_event_id = q.fetchone()[0]
            q.execute(
                "INSERT INTO ingestion.certified_knowledge_items (knowledge_id,source_fingerprint,source_record_id,certification_event_id,knowledge_text,provenance,certifying_actor,certification_timestamp,certification_policy_version,lifecycle_state) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s,'synthetic-cert-v1','certified')",
                (knowledge_id, record_fp, name, cert_event_id, f'synthetic knowledge {name}', json.dumps({'source_reference': 'runtime_local_only'}), actor, cert_ts),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_assurance_envelopes (knowledge_id,source_fingerprint,assessment_policy_version,assurance_level,assurance_state,dimensions,gaps,assessed_by,envelope_fingerprint) VALUES (%s,%s,'st1-072-summary-v1','SDAS-2','certified_assured','{}'::jsonb,'[]'::jsonb,%s,%s)",
                (knowledge_id, record_fp, actor, h({'env': name})),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_assurance_decisions (record_fingerprint,authority_inheritance_state,business_time_state,risk_tier,currentness_state,reliance_state,outcome,reason_codes,policy_version,decided_at,actor_id,evidence_fingerprint,event_hash) VALUES (%s,%s,%s,%s,%s,%s,'policy_automatic',%s::jsonb,'v1',%s,'sahra_policy_engine',%s,%s)",
                (record_fp, authority_state, business_time_state, risk, currentness, reliance, json.dumps(['synthetic']), now, h({'ev': name}), h({'hash': name})),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_assurance_events (knowledge_id,previous_state,new_state,actor_identifier,policy_version,reason_code,event_payload,previous_event_hash,event_hash,recorded_at) VALUES (%s,NULL,'assessed_partial',%s,'st1-072-summary-v1','synthetic','{}'::jsonb,NULL,%s,%s)",
                (knowledge_id, actor, h({'event': name, 'i': 0}), now),
            )
            previous = h({'event': name, 'i': 0})
            q.execute(
                "INSERT INTO ingestion.sdas_assurance_events (knowledge_id,previous_state,new_state,actor_identifier,policy_version,reason_code,event_payload,previous_event_hash,event_hash,recorded_at) VALUES (%s,'assessed_partial','evidence_complete',%s,'st1-072-summary-v1','synthetic','{}'::jsonb,%s,%s,%s)",
                (knowledge_id, actor, previous, h({'event': name, 'i': 1}), now + timedelta(seconds=1)),
            )
            previous = h({'event': name, 'i': 1})
            q.execute(
                "INSERT INTO ingestion.sdas_assurance_events (knowledge_id,previous_state,new_state,actor_identifier,policy_version,reason_code,event_payload,previous_event_hash,event_hash,recorded_at) VALUES (%s,'evidence_complete','certified_assured',%s,'st1-072-summary-v1','synthetic','{}'::jsonb,%s,%s,%s)",
                (knowledge_id, actor, previous, h({'event': name, 'i': 2}), now + timedelta(seconds=2)),
            )
            if authority_state == 'eligible':
                q.execute(
                    "INSERT INTO ingestion.sdas_authority_assertions (subject_type,subject_id,authority_basis,authority_scope,accountable_actor_id,evidence_reference,evidence_fingerprint,effective_from,asserted_at,verification_method,policy_version,assertion_state,event_hash) VALUES ('record',%s,'corroborated_authority',%s::jsonb,%s,'synthetic',%s,%s,%s,'synthetic','v1','asserted',%s)",
                    (record_fp, json.dumps({'project_scope': 'synthetic_project'}), actor, h({'auth': name}), now - timedelta(days=1), now, h({'auth-event': name})),
                )
            if business_time_state == 'valid':
                q.execute(
                    "INSERT INTO ingestion.sdas_business_time_evidence (record_fingerprint,time_kind,start_at,end_at,value_text,evidence_reference,evidence_fingerprint,captured_at,actor_id,verification_method,evidence_quality,event_hash) VALUES (%s,'report_period',%s,%s,%s,'synthetic',%s,%s,%s,'synthetic','native',%s)",
                    (record_fp, now - timedelta(days=14), now - timedelta(days=7), 'synthetic-period', h({'bt': name}), now, actor, h({'bt-event': name})),
                )
            if post_event:
                q.execute(
                    "INSERT INTO ingestion.sdas_post_registration_events (knowledge_id,event_type,actor_id,evidence_reference,evidence_fingerprint,reason_code,details,event_hash) VALUES (%s,%s,%s,'synthetic',%s,'synthetic','{}'::jsonb,%s)",
                    (knowledge_id, post_event, actor, h({'post': name}), h({'post-event': name})),
                )
            results[name] = knowledge_id

        mk_case('verified', limitation_codes=[])
        mk_case('limitations', currentness='historical', reliance='not_eligible', base_result='VERIFIED_WITH_LIMITATIONS', limitation_codes=['currentness_limited','reliance_not_eligible'])
        mk_case('human', source_authority='declared_unverified', authority_state='missing', limitation_codes=['authority_missing','governance_waiting_for_external_evidence'])
        mk_case('quarantine', risk='high', limitation_codes=['high_risk_fact'])
        mk_case('revoked', post_event='revocation', limitation_codes=['post_registration_terminal_event'])

        q.execute("SELECT count(*) FROM information_schema.views WHERE table_schema='ingestion' AND table_name='sdas_assurance_passport_portfolio_summary'")
        results['summary_view_exists'] = q.fetchone()[0] == 1
        q.execute("SELECT count(*) FROM information_schema.views WHERE table_schema='ingestion' AND table_name='sdas_assurance_passport_exception_queue'")
        results['queue_view_exists'] = q.fetchone()[0] == 1
        q.execute("SELECT has_table_privilege('enterprise_ai_ingestion_runtime','ingestion.sdas_assurance_passport_portfolio_summary','SELECT')")
        results['runtime_summary_select_granted'] = q.fetchone()[0]
        q.execute("SELECT has_table_privilege('enterprise_ai_ingestion_runtime','ingestion.sdas_assurance_passport_exception_queue','SELECT')")
        results['runtime_queue_select_granted'] = q.fetchone()[0]
        q.execute("SELECT verification_result, passport_count, limitation_code_counts FROM ingestion.sdas_assurance_passport_portfolio_summary ORDER BY verification_result")
        summary_rows = q.fetchall()
        q.execute("SELECT verification_result, count(*) FROM ingestion.sdas_assurance_passport_exception_queue GROUP BY verification_result ORDER BY verification_result")
        queue_counts = q.fetchall()
        q.execute("SELECT count(*) FROM ingestion.sdas_assurance_passport_exception_queue WHERE verification_result='HUMAN_REQUIRED'")
        human_queue = q.fetchone()[0]
        q.execute("SELECT count(*) FROM ingestion.sdas_assurance_passport_exception_queue WHERE verification_result='QUARANTINED'")
        quarantine_queue = q.fetchone()[0]
        q.execute("SELECT count(*) FROM ingestion.sdas_assurance_passport_exception_queue WHERE verification_result='REVOKED_OR_SUPERSEDED'")
        revoked_queue = q.fetchone()[0]
        q.execute("SELECT count(*) FROM ingestion.sdas_assurance_passport_exception_queue WHERE verification_result='VERIFIED'")
        verified_queue = q.fetchone()[0]
        q.execute("SELECT count(*) FROM ingestion.sdas_assurance_passport_exception_queue")
        queue_total = q.fetchone()[0]
        q.execute("SAVEPOINT mutate")
        try:
            q.execute("UPDATE ingestion.sdas_assurance_envelopes SET assurance_state='revoked' WHERE knowledge_id=%s", (results['verified'],))
            results['unauthorized_mutation_rejected'] = False
        except psycopg.Error:
            q.execute("ROLLBACK TO SAVEPOINT mutate")
            results['unauthorized_mutation_rejected'] = True
    c.rollback()

results['summary_rows'] = summary_rows
results['queue_counts'] = queue_counts
results['baseline_summary'] = baseline_summary
results['baseline_queue'] = baseline_queue
results['baseline_queue_total'] = baseline_queue_total
results['human_queue'] = human_queue
results['quarantine_queue'] = quarantine_queue
results['revoked_queue'] = revoked_queue
results['verified_queue'] = verified_queue
results['queue_total'] = queue_total
print(json.dumps(results,sort_keys=True,separators=(',',':')))
'''


def main() -> None:
    docker_build = subprocess.run(["docker", "build", "-t", IMAGE, str(SERVICE_DIR)], text=True, capture_output=True)
    if docker_build.returncode:
        raise SystemExit(docker_build.stderr.strip() or "ST1-072 local image build failed")
    local_smoke = subprocess.run(
        [
            "docker", "run", "--rm", "--entrypoint", "python", IMAGE, "-c",
            "import json,threading,time,urllib.request,urllib.error,app; from http.server import ThreadingHTTPServer; srv=ThreadingHTTPServer(('127.0.0.1',8083), app.IngestionHandler); t=threading.Thread(target=srv.serve_forever,daemon=True); t.start(); time.sleep(0.3); out=[]\nfor path in ['/health','/v1/sdas/passports/summary']:\n    try:\n        with urllib.request.urlopen('http://127.0.0.1:8083'+path) as r:\n            out.append({'path':path,'status':r.status})\n    except urllib.error.HTTPError as e:\n        out.append({'path':path,'status':e.code})\nprint(json.dumps(out,separators=(',',':'))); srv.shutdown()"
        ],
        text=True,
        capture_output=True,
    )
    if local_smoke.returncode:
        raise SystemExit(local_smoke.stderr.strip() or "ST1-072 local route smoke failed")
    payload = base64.b64encode(REMOTE.encode()).decode()
    command = "docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('" + payload + "'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], text=True, capture_output=True)
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "ST1-072 verification failed")
    observed = json.loads(run.stdout)
    summary_counts = {row[0]: row[1] for row in observed["summary_rows"]}
    queue_counts = {row[0]: row[1] for row in observed["queue_counts"]}
    baseline_summary = observed["baseline_summary"]
    baseline_queue = observed["baseline_queue"]
    summary_delta = {key: summary_counts.get(key, 0) - baseline_summary.get(key, 0) for key in set(summary_counts) | set(baseline_summary)}
    queue_delta = {key: queue_counts.get(key, 0) - baseline_queue.get(key, 0) for key in set(queue_counts) | set(baseline_queue)}
    output = {
        "summary_view_exists": observed["summary_view_exists"],
        "queue_view_exists": observed["queue_view_exists"],
        "runtime_summary_select_granted": observed["runtime_summary_select_granted"],
        "runtime_queue_select_granted": observed["runtime_queue_select_granted"],
        "summary_counts": summary_counts,
        "queue_counts": queue_counts,
        "summary_delta": summary_delta,
        "queue_delta": queue_delta,
        "expected_summary_delta": {
            "VERIFIED": 0,
            "VERIFIED_WITH_LIMITATIONS": 0,
            "HUMAN_REQUIRED": 1,
            "NOT_RELIANCE_ELIGIBLE": 2,
            "QUARANTINED": 1,
            "REVOKED_OR_SUPERSEDED": 1,
        },
        "expected_queue_delta": {
            "HUMAN_REQUIRED": 1,
            "NOT_RELIANCE_ELIGIBLE": 2,
            "QUARANTINED": 1,
            "REVOKED_OR_SUPERSEDED": 1,
        },
        "verified_not_in_queue": observed["verified_queue"] == 0,
        "queue_total_delta": observed["queue_total"] - observed["baseline_queue_total"],
        "unauthorized_mutation_rejected": observed["unauthorized_mutation_rejected"],
        "real_active_delegations": observed["real_active_delegations"],
        "local_smoke": json.loads(local_smoke.stdout),
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
