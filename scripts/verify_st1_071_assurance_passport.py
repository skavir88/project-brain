#!/usr/bin/env python3
"""Verify ST1-071 assurance-passport projection and classifier semantics."""
from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = ROOT / "implementation" / "ingestion-service"
IMAGE = "enterprise-ai-st1-071-passport-test"

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

        def mk_case(name, *, source_authority='authoritative', record_authority='asserted',
                    business_time=True, decision_outcome='policy_automatic',
                    currentness='current_eligible', risk='low',
                    envelope_state='certified_assured', post_event=None,
                    conflicting_authority=False, malformed_chain=False,
                    provenance_mismatch=False):
            actor = f"st1-071-actor-{name}"
            reviewer = f"st1-071-reviewer-{name}"
            source_id = f"st1-071-source-{name}"
            record_fp = h({'record': name})
            alt_record_fp = h({'record': f'{name}-alt'})
            knowledge_id = h({'knowledge': name})
            policy_id = f"st1-071-policy-{name}"
            policy_hash = h({'policy': name})
            evidence_hash = h({'evidence': name})
            decision_hash = h({'decision': name})
            assurance_hash = h({'assurance': name})
            audit_ts = now - timedelta(minutes=5)
            q.execute(
                "INSERT INTO ingestion.sdas_actor_registry (actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality) VALUES (%s,'synthetic operator','[]'::jsonb,'synthetic',%s,'native'),(%s,'synthetic reviewer','[]'::jsonb,'synthetic',%s,'native')",
                (actor, now, reviewer, now),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_source_registry (source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,effective_from,evidence_quality) VALUES (%s,'synthetic_workbook','runtime_local_only',%s,'synthetic verification',%s,%s::jsonb,%s,'native')",
                (source_id, actor, source_authority, json.dumps({'project_scope': 'synthetic_project'}), now),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_acquisition_events (source_id,acquired_at,actor_id,acquisition_method,source_reference,original_fingerprint,size_bytes,media_type,evidence_quality,evidence_hash) VALUES (%s,%s,%s,'read_only','runtime_local_only',%s,1024,'application/json','native',%s)",
                (source_id, now - timedelta(minutes=20), actor, record_fp, h({'acq': name})),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_transformations (acquisition_event_id,transformation_type,tool_name,tool_version,transformed_at,input_fingerprint,output_fingerprint,deterministic,extraction_coordinates,evidence_quality,evidence_hash) VALUES ((SELECT acquisition_event_id FROM ingestion.sdas_acquisition_events WHERE evidence_hash=%s),'normalize','synthetic','1.0',%s,%s,%s,true,'{}'::jsonb,'native',%s)",
                (h({'acq': name}), now - timedelta(minutes=19), record_fp, record_fp, h({'tx': name})),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_policy_versions (policy_id,policy_version,effective_from,enabled,allowed_source_types,allowed_data_classes,required_evidence,risk_class,decision_reason_codes,actor_authority_requirements,policy_hash) VALUES (%s,'v1',%s,true,'[\"synthetic_workbook\"]'::jsonb,'[\"synthetic_fact\"]'::jsonb,'[\"authority\",\"business_time\"]'::jsonb,%s,'[]'::jsonb,'[]'::jsonb,%s)",
                (policy_id, now - timedelta(days=1), risk, policy_hash),
            )
            q.execute(
                "INSERT INTO ingestion.credibility_records (record_fingerprint,canonical_record,provenance,source_id,record_id,observed_at,disposition,quality_gate_outcome,lifecycle_state,certification_timestamp,certification_actor,certification_policy_version) VALUES (%s,%s::jsonb,%s::jsonb,%s,%s,%s,'certification_candidate','passed','certified',%s,%s,'synthetic-cert-v1')",
                (record_fp, json.dumps({'source_id': source_id, 'record_id': f'{name}-record', 'payload': {'statement': name}}), json.dumps({'source_reference': 'runtime_local_only'}), source_id, f'{name}-record', now - timedelta(days=1), audit_ts, reviewer),
            )
            q.execute(
                "INSERT INTO ingestion.certification_audit_events (record_fingerprint,previous_lifecycle_state,new_lifecycle_state,certification_timestamp,actor_identifier,policy_version) VALUES (%s,'certification_candidate','certified',%s,%s,'synthetic-cert-v1') RETURNING event_id",
                (record_fp, audit_ts, reviewer),
            )
            cert_event_id = q.fetchone()[0]
            if provenance_mismatch:
                q.execute(
                    "INSERT INTO ingestion.credibility_records (record_fingerprint,canonical_record,provenance,source_id,record_id,disposition,quality_gate_outcome,lifecycle_state) VALUES (%s,'{}'::jsonb,'{}'::jsonb,%s,%s,'rejected','failed','rejected')",
                    (alt_record_fp, source_id, f'{name}-alt'),
                )
            q.execute(
                "INSERT INTO ingestion.certified_knowledge_items (knowledge_id,source_fingerprint,source_record_id,certification_event_id,knowledge_text,provenance,certifying_actor,certification_timestamp,certification_policy_version,lifecycle_state) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s,'synthetic-cert-v1','certified')",
                (knowledge_id, record_fp, f'{name}-record', cert_event_id, f'synthetic knowledge {name}', json.dumps({'source_reference': 'runtime_local_only'}), reviewer, audit_ts),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_policy_decisions (record_fingerprint,policy_id,policy_version,approval_mode,decision_actor,decision_reasons,evidence_quality,decision_hash) VALUES (%s,%s,'v1',%s,'sahra_policy_engine',%s::jsonb,'native',%s)",
                (record_fp, policy_id, decision_outcome, json.dumps(['authority_not_verified'] if decision_outcome == 'human_required' else ['all_required_policy_evidence_present']), decision_hash),
            )
            if record_authority == 'asserted':
                q.execute(
                    "INSERT INTO ingestion.sdas_authority_assertions (subject_type,subject_id,authority_basis,authority_scope,accountable_actor_id,evidence_reference,evidence_fingerprint,effective_from,asserted_at,verification_method,policy_version,assertion_state,event_hash) VALUES ('record',%s,%s,%s::jsonb,%s,'synthetic',%s,%s,%s,'synthetic','v1','asserted',%s)",
                    (record_fp, 'conflicting_authority' if conflicting_authority else 'corroborated_authority', json.dumps({'project_scope': 'synthetic_project'}), actor, h({'auth': name}), now - timedelta(days=1), now, h({'auth-event': name})),
                )
            elif record_authority == 'revoked':
                q.execute(
                    "INSERT INTO ingestion.sdas_authority_assertions (subject_type,subject_id,authority_basis,authority_scope,accountable_actor_id,evidence_reference,evidence_fingerprint,effective_from,asserted_at,verification_method,policy_version,assertion_state,event_hash) VALUES ('record',%s,'corroborated_authority',%s::jsonb,%s,'synthetic',%s,%s,%s,'synthetic','v1','revoked',%s)",
                    (record_fp, json.dumps({'project_scope': 'synthetic_project'}), actor, h({'auth': name}), now - timedelta(days=1), now, h({'auth-event': name})),
                )
            if business_time:
                q.execute(
                    "INSERT INTO ingestion.sdas_business_time_evidence (record_fingerprint,time_kind,start_at,end_at,value_text,evidence_reference,evidence_fingerprint,captured_at,actor_id,verification_method,evidence_quality,event_hash) VALUES (%s,'report_period',%s,%s,%s,'synthetic',%s,%s,%s,'synthetic','native',%s)",
                    (record_fp, now - timedelta(days=14), now - timedelta(days=7), 'synthetic-period', h({'bt': name}), now, actor, h({'bt-event': name})),
                )
            q.execute(
                "INSERT INTO ingestion.sdas_assurance_decisions (record_fingerprint,authority_inheritance_state,business_time_state,risk_tier,currentness_state,reliance_state,outcome,reason_codes,policy_version,decided_at,actor_id,evidence_fingerprint,event_hash) VALUES (%s,%s,%s,%s,%s,'not_eligible',%s,%s::jsonb,'v1',%s,'sahra_policy_engine',%s,%s)",
                (
                    record_fp,
                    'eligible' if record_authority == 'asserted' and not conflicting_authority and source_authority in ('verified_limited', 'authoritative') else 'missing',
                    'valid' if business_time else 'missing',
                    risk,
                    currentness,
                    decision_outcome,
                    json.dumps(['synthetic']),
                    now,
                    evidence_hash,
                    assurance_hash,
                ),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_assurance_envelopes (knowledge_id,source_fingerprint,assessment_policy_version,assurance_level,assurance_state,dimensions,gaps,assessed_by,envelope_fingerprint) VALUES (%s,%s,'st1-071-passport-v1','SDAS-2',%s,'{}'::jsonb,'[]'::jsonb,%s,%s)",
                (knowledge_id, alt_record_fp if provenance_mismatch else record_fp, envelope_state, reviewer, h({'env': name})),
            )
            sequence = ['assessed_partial', 'evidence_complete']
            if envelope_state == 'certified_assured':
                sequence.append('certified_assured')
            elif envelope_state not in sequence:
                sequence.append(envelope_state)
            prev = None
            previous_state = None
            for idx, state in enumerate(sequence):
                event_hash = h({'assurance-event': name, 'idx': idx})
                previous_hash = ('broken-chain' if malformed_chain and idx == 1 else prev)
                q.execute(
                    "INSERT INTO ingestion.sdas_assurance_events (knowledge_id,previous_state,new_state,actor_identifier,policy_version,reason_code,event_payload,previous_event_hash,event_hash,recorded_at) VALUES (%s,%s,%s,%s,'st1-071-passport-v1','synthetic',%s::jsonb,%s,%s,%s)",
                    (
                        knowledge_id,
                        previous_state,
                        state,
                        reviewer,
                        json.dumps({'index': idx}),
                        previous_hash,
                        event_hash,
                        now + timedelta(seconds=idx),
                    ),
                )
                prev = event_hash
                previous_state = state
            q.execute(
                "INSERT INTO ingestion.sdas_consumption_events (knowledge_id,consumer_identifier,purpose_class,outcome_class,retrieval_policy_version,retrieval_threshold,provenance_set_fingerprint,output_fingerprint,idempotency_key,previous_event_hash,event_hash) VALUES (%s,'synthetic_consumer','verification','grounded_answer','v1',0.70,%s,%s,%s,NULL,%s) ON CONFLICT DO NOTHING",
                (knowledge_id, h({'prov': name}), h({'out': name}), h({'idem': name}), h({'consume': name})),
            )
            q.execute(
                "INSERT INTO ingestion.sdas_consumption_events (knowledge_id,consumer_identifier,purpose_class,outcome_class,retrieval_policy_version,retrieval_threshold,provenance_set_fingerprint,output_fingerprint,idempotency_key,previous_event_hash,event_hash) VALUES (%s,'synthetic_consumer','verification','grounded_answer','v1',0.70,%s,%s,%s,NULL,%s) ON CONFLICT DO NOTHING",
                (knowledge_id, h({'prov': name}), h({'out': name}), h({'idem': name}), h({'consume': f'{name}-dup'})),
            )
            if post_event:
                q.execute(
                    "INSERT INTO ingestion.sdas_post_registration_events (knowledge_id,event_type,actor_id,evidence_reference,evidence_fingerprint,reason_code,details,event_hash) VALUES (%s,%s,%s,'synthetic',%s,'synthetic','{}'::jsonb,%s)",
                    (knowledge_id, post_event, actor, h({'post': name}), h({'post-event': name})),
                )
            q.execute(
                "SELECT base_verification_result, limitation_codes, passport_authority_state, passport_business_time_state, provenance_link_valid, assurance_event_chain_valid, consumption_count FROM ingestion.sdas_assurance_passport_projection WHERE knowledge_id=%s",
                (knowledge_id,),
            )
            return q.fetchone()

        results['complete_valid_assurance_chain'] = mk_case('complete')
        results['missing_authority'] = mk_case('missing-authority', source_authority='declared_unverified', record_authority='missing', decision_outcome='human_required')
        results['missing_business_time'] = mk_case('missing-business-time', business_time=False, decision_outcome='human_required')
        results['revoked_authority'] = mk_case('revoked-authority', record_authority='revoked')
        results['superseded_evidence'] = mk_case('superseded-evidence', post_event='supersession')
        results['conflicting_evidence'] = mk_case('conflicting-evidence', conflicting_authority=True)
        results['expired_currentness_failure'] = mk_case('stale-currentness', currentness='stale')
        results['malformed_evidence'] = mk_case('malformed-chain', malformed_chain=True)
        results['hash_provenance_mismatch'] = mk_case('provenance-mismatch', provenance_mismatch=True)
        results['high_risk_fact'] = mk_case('high-risk', risk='high')

        q.execute(
            "SELECT count(*) FROM information_schema.views WHERE table_schema='ingestion' AND table_name='sdas_assurance_passport_projection'"
        )
        results['projection_exists'] = q.fetchone()[0] == 1
        q.execute(
            "SELECT has_table_privilege('enterprise_ai_ingestion_runtime','ingestion.sdas_assurance_passport_projection','SELECT')"
        )
        results['runtime_select_granted'] = q.fetchone()[0]
        q.execute("SAVEPOINT mutate")
        try:
            q.execute("UPDATE ingestion.sdas_assurance_envelopes SET assurance_state='revoked' WHERE knowledge_id=%s", (h({'knowledge': 'complete'}),))
            results['unauthorized_mutation_rejected'] = False
        except psycopg.Error:
            q.execute("ROLLBACK TO SAVEPOINT mutate")
            results['unauthorized_mutation_rejected'] = True
    c.rollback()

print(json.dumps(results,sort_keys=True,separators=(',',':')))
'''

def main() -> None:
    docker_build = subprocess.run(["docker", "build", "-t", IMAGE, str(SERVICE_DIR)], text=True, capture_output=True)
    if docker_build.returncode:
        raise SystemExit(docker_build.stderr.strip() or "ST1-071 local image build failed")
    finalize_run = subprocess.run(
        ["docker", "run", "--rm", "--entrypoint", "python", IMAGE, "-c", "import json,app; print(json.dumps({'result': app.finalize_passport_verification_result('VERIFIED','not_eligible',True)}))"],
        text=True,
        capture_output=True,
    )
    if finalize_run.returncode:
        raise SystemExit(finalize_run.stderr.strip() or "ST1-071 local classifier verification failed")
    finalized = json.loads(finalize_run.stdout)
    payload = base64.b64encode(REMOTE.encode()).decode()
    command = "docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('" + payload + "'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], text=True, capture_output=True)
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "ST1-071 verification failed")
    observed = json.loads(run.stdout)
    complete = observed["complete_valid_assurance_chain"]
    output = {
        "projection_exists": observed["projection_exists"],
        "runtime_select_granted": observed["runtime_select_granted"],
        "cases": {
            "complete_valid_assurance_chain": {
                "base_result": complete[0],
                "expected": "VERIFIED",
            },
            "missing_authority": {
                "base_result": observed["missing_authority"][0],
                "expected": "HUMAN_REQUIRED",
            },
            "missing_business_time": {
                "base_result": observed["missing_business_time"][0],
                "expected": "HUMAN_REQUIRED",
            },
            "revoked_authority": {
                "base_result": observed["revoked_authority"][0],
                "expected": "REVOKED_OR_SUPERSEDED",
            },
            "superseded_evidence": {
                "base_result": observed["superseded_evidence"][0],
                "expected": "REVOKED_OR_SUPERSEDED",
            },
            "conflicting_evidence": {
                "base_result": observed["conflicting_evidence"][0],
                "expected": "QUARANTINED",
            },
            "expired_currentness_failure": {
                "base_result": observed["expired_currentness_failure"][0],
                "expected": "VERIFIED_WITH_LIMITATIONS",
            },
            "malformed_evidence": {
                "base_result": observed["malformed_evidence"][0],
                "expected": "INTEGRITY_FAILURE",
            },
            "hash_provenance_mismatch": {
                "base_result": observed["hash_provenance_mismatch"][0],
                "expected": "INTEGRITY_FAILURE",
            },
            "high_risk_fact": {
                "base_result": observed["high_risk_fact"][0],
                "expected": "QUARANTINED",
            },
            "reliance_not_eligible": {
                "finalized_result": finalized["result"],
                "expected": "NOT_RELIANCE_ELIGIBLE",
            },
        },
        "duplicate_idempotent_operation": {
            "complete_case_consumption_count": complete[6],
            "expected_count": 1,
        },
        "unauthorized_mutation_rejected": observed["unauthorized_mutation_rejected"],
        "real_active_delegations": observed["real_active_delegations"],
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
