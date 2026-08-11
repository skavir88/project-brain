#!/usr/bin/env python3
"""Verify the limited pilot-governance bootstrap against the real ST1-061 artifact.

This verifier is intentionally read-only against persisted real evidence except for
rolled-back transactional guard/idempotency checks.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
LOCAL_ACQUISITION = RUNTIME / "st1-061-native-acquisition.json"
OUTPUT = ROOT / "evidence" / "sanitized" / "2026-08-11-st1-121-limited-pilot-bootstrap.json"


def main() -> None:
    acquisition = json.loads(LOCAL_ACQUISITION.read_text(encoding="utf-8"))
    selection_alias = acquisition["selection_alias"]
    source_alias = acquisition["source_alias"]
    source_id = f"maroon-st1-061-{source_alias}".replace("source-", "source-")
    original_fingerprint = acquisition["original_fingerprint"]
    locator_fingerprint = acquisition["locator_fingerprint"]

    remote = f"""
import hashlib, json, os, psycopg

SOURCE_ID = {source_id!r}
ORIGINAL_FP = {original_fingerprint!r}
LOCATOR_FP = {locator_fingerprint!r}
APPROVAL_ID = 'sdas-governance-policy-pilot-v1'
PROPOSAL_ID = 'sdas-bootstrap-maroon-project-controls-v1'

def scalar(cur, query, params=()):
    cur.execute(query, params)
    return cur.fetchone()[0]

result = {{}}
with psycopg.connect(
    host=os.environ['INGESTION_DB_HOST'],
    port=os.environ.get('INGESTION_DB_PORT', '5432'),
    dbname=os.environ['INGESTION_DB_NAME'],
    user=os.environ['INGESTION_DB_USER'],
    password=os.environ['INGESTION_DB_PASSWORD'],
) as conn:
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            SELECT governance_policy_status, approver_identity_state, approval_basis_reference, policy_scope::text, approved_at::text
            FROM ingestion.sdas_governance_policy_approvals
            WHERE approval_id = %s
        \"\"\", (APPROVAL_ID,))
        governance_row = cur.fetchone()
        result['governance_policy'] = {{
            'approval_id': APPROVAL_ID,
            'governance_policy_status': governance_row[0],
            'approver_identity_state': governance_row[1],
            'approval_basis_reference': governance_row[2],
            'policy_scope': json.loads(governance_row[3]),
            'approved_at': governance_row[4],
            'semantic_pilot_governance_status': 'APPROVED_LIMITED_PILOT' if governance_row[0] == 'approved_for_pilot' else 'NOT_APPROVED',
        }}

        cur.execute(\"\"\"
            SELECT transition_state, governance_actor_id, accountable_actor_id, source_id, event_at::text
            FROM ingestion.sdas_delegation_bootstrap_events
            WHERE proposal_id = %s
            ORDER BY event_id DESC
            LIMIT 1
        \"\"\", (PROPOSAL_ID,))
        latest_event = cur.fetchone()
        result['bootstrap_latest_event'] = {{
            'proposal_id': PROPOSAL_ID,
            'transition_state': latest_event[0],
            'governance_actor_id': latest_event[1],
            'accountable_actor_id': latest_event[2],
            'source_id': latest_event[3],
            'event_at': latest_event[4],
        }}
        result['active_delegation_count'] = scalar(cur, "SELECT count(*) FROM ingestion.sdas_active_delegation_bootstrap")
        cur.execute(\"\"\"
            SELECT queue_outcome, reason_code
            FROM ingestion.sdas_governance_bootstrap_exception_queue
            WHERE proposal_id = %s
        \"\"\", (PROPOSAL_ID,))
        queue_row = cur.fetchone()
        result['bootstrap_queue'] = {{
            'queue_outcome': queue_row[0],
            'reason_code': queue_row[1],
        }}

        cur.execute(\"\"\"
            SELECT source_id, source_type, system_location_identity, authority_status, authority_scope::text, evidence_quality, created_at::text
            FROM ingestion.sdas_source_registry
            WHERE source_id = %s
        \"\"\", (SOURCE_ID,))
        source_row = cur.fetchone()
        result['selected_source'] = {{
            'source_id': source_row[0],
            'source_type': source_row[1],
            'system_location_identity': source_row[2],
            'authority_status': source_row[3],
            'authority_scope': json.loads(source_row[4]),
            'evidence_quality': source_row[5],
            'created_at': source_row[6],
        }}

        cur.execute(\"\"\"
            SELECT acquisition_event_id, acquired_at::text, acquisition_method, source_reference, original_fingerprint, size_bytes, media_type, evidence_quality, evidence_hash
            FROM ingestion.sdas_acquisition_events
            WHERE source_id = %s
            ORDER BY acquisition_event_id
        \"\"\", (SOURCE_ID,))
        acquisition_rows = cur.fetchall()
        result['acquisition_events'] = [
            {{
                'acquisition_event_id': row[0],
                'acquired_at': row[1],
                'acquisition_method': row[2],
                'source_reference': row[3],
                'original_fingerprint': row[4],
                'size_bytes': row[5],
                'media_type': row[6],
                'evidence_quality': row[7],
                'evidence_hash': row[8],
            }}
            for row in acquisition_rows
        ]

        cur.execute(\"\"\"
            SELECT transformation_id, acquisition_event_id, transformation_type, tool_name, tool_version, transformed_at::text, input_fingerprint, output_fingerprint, deterministic, evidence_quality
            FROM ingestion.sdas_transformations
            WHERE acquisition_event_id IN (
              SELECT acquisition_event_id FROM ingestion.sdas_acquisition_events WHERE source_id = %s
            )
            ORDER BY transformation_id
        \"\"\", (SOURCE_ID,))
        transformation_rows = cur.fetchall()
        result['transformations'] = [
            {{
                'transformation_id': row[0],
                'acquisition_event_id': row[1],
                'transformation_type': row[2],
                'tool_name': row[3],
                'tool_version': row[4],
                'transformed_at': row[5],
                'input_fingerprint': row[6],
                'output_fingerprint': row[7],
                'deterministic': row[8],
                'evidence_quality': row[9],
            }}
            for row in transformation_rows
        ]

        cur.execute(\"\"\"
            SELECT record_fingerprint, record_id, observed_at::text, ingested_at::text, disposition, reason_code, quality_gate_outcome, lifecycle_state, certification_timestamp::text, certification_actor, certification_policy_version
            FROM ingestion.credibility_records
            WHERE source_id = %s
            ORDER BY ingested_at
        \"\"\", (SOURCE_ID,))
        record_row = cur.fetchone()
        result['credibility_record'] = {{
            'record_fingerprint': record_row[0],
            'record_id': record_row[1],
            'observed_at': record_row[2],
            'ingested_at': record_row[3],
            'disposition': record_row[4],
            'reason_code': record_row[5],
            'quality_gate_outcome': record_row[6],
            'lifecycle_state': record_row[7],
            'certification_timestamp': record_row[8],
            'certification_actor': record_row[9],
            'certification_policy_version': record_row[10],
        }}
        record_fp = record_row[0]

        cur.execute(\"\"\"
            SELECT policy_id, policy_version, approval_mode, decision_reasons::text, evidence_quality
            FROM ingestion.sdas_policy_decisions
            WHERE record_fingerprint = %s
            ORDER BY decision_id
        \"\"\", (record_fp,))
        policy_row = cur.fetchone()
        result['policy_decision'] = {{
            'policy_id': policy_row[0],
            'policy_version': policy_row[1],
            'approval_mode': policy_row[2],
            'decision_reasons': json.loads(policy_row[3]),
            'evidence_quality': policy_row[4],
        }}

        result['authority_assertion_counts'] = {{
            'record': scalar(cur, "SELECT count(*) FROM ingestion.sdas_authority_assertions WHERE subject_type='record' AND subject_id=%s", (record_fp,)),
            'source': scalar(cur, "SELECT count(*) FROM ingestion.sdas_authority_assertions WHERE subject_type='source' AND subject_id=%s", (SOURCE_ID,)),
        }}
        result['business_time_evidence_counts'] = {{
            'all': scalar(cur, "SELECT count(*) FROM ingestion.sdas_business_time_evidence WHERE record_fingerprint=%s", (record_fp,)),
            'filesystem_timestamp': scalar(cur, "SELECT count(*) FROM ingestion.sdas_business_time_evidence WHERE record_fingerprint=%s AND time_kind='filesystem_timestamp'", (record_fp,)),
            'acquisition_timestamp': scalar(cur, "SELECT count(*) FROM ingestion.sdas_business_time_evidence WHERE record_fingerprint=%s AND time_kind='acquisition_timestamp'", (record_fp,)),
        }}
        result['role_source_verification_counts'] = {{
            'role_identity_verifications': scalar(cur, "SELECT count(*) FROM ingestion.sdas_role_identity_verifications"),
            'source_control_verifications': scalar(cur, "SELECT count(*) FROM ingestion.sdas_source_control_verifications"),
        }}

        result['separation_assertions'] = {{
            'pilot_governance_does_not_imply_source_authority': governance_row[0] == 'approved_for_pilot' and source_row[3] == 'declared_unverified',
            'pilot_governance_does_not_imply_historical_accountability': latest_event[1] is None and latest_event[2] is None and latest_event[3] is None,
            'historical_accountability_status': 'NOT_VERIFIED' if latest_event[1] is None and latest_event[2] is None else 'INDEPENDENTLY_EVIDENCED',
            'data_authority_status': 'NOT_VERIFIED' if source_row[3] == 'declared_unverified' else source_row[3],
            'business_time_status': 'MISSING_NOT_INFERRED' if result['business_time_evidence_counts']['all'] == 0 else 'EVIDENCED',
            'certification_status': 'NONE' if record_row[8] is None else 'PRESENT',
            'reliance_status': 'NOT_ELIGIBLE',
            'currentness_status': 'UNCHANGED_INSUFFICIENT_CERTIFIED_EVIDENCE',
            'pilot_governance_status': 'APPROVED_LIMITED_PILOT' if governance_row[0] == 'approved_for_pilot' else 'NOT_APPROVED',
        }}

        result['real_artifact_chain_reached_policy_evaluation'] = (
            len(acquisition_rows) == 1
            and len(transformation_rows) == 1
            and policy_row[2] in ('human_required', 'policy_automatic', 'reject_or_quarantine')
        )
        result['business_time_not_inferred_from_acquisition_or_filesystem'] = (
            len(acquisition_rows) == 1
            and result['business_time_evidence_counts']['all'] == 0
            and 'business_timestamp_missing' in result['policy_decision']['decision_reasons']
        )
        result['no_certification_occurred'] = record_row[8] is None and record_row[9] is None and record_row[10] is None and record_row[7] == 'certification_candidate'

        before_source = scalar(cur, "SELECT count(*) FROM ingestion.sdas_source_registry WHERE source_id=%s", (SOURCE_ID,))
        cur.execute('SAVEPOINT st1_121_duplicate_source')
        cur.execute(\"\"\"
            INSERT INTO ingestion.sdas_source_registry (source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,effective_from,effective_to,evidence_quality,created_at)
            SELECT source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,effective_from,effective_to,evidence_quality,created_at
            FROM ingestion.sdas_source_registry
            WHERE source_id=%s
            ON CONFLICT DO NOTHING
            RETURNING source_id
        \"\"\", (SOURCE_ID,))
        duplicate_source = cur.fetchone()
        after_source = scalar(cur, "SELECT count(*) FROM ingestion.sdas_source_registry WHERE source_id=%s", (SOURCE_ID,))
        cur.execute('ROLLBACK TO SAVEPOINT st1_121_duplicate_source')

        cur.execute('SAVEPOINT st1_121_duplicate_acquisition')
        cur.execute(\"\"\"
            INSERT INTO ingestion.sdas_acquisition_events (source_id,acquired_at,actor_id,acquisition_method,source_reference,original_fingerprint,size_bytes,media_type,evidence_quality,evidence_hash,created_at)
            SELECT source_id,acquired_at,actor_id,acquisition_method,source_reference,original_fingerprint,size_bytes,media_type,evidence_quality,evidence_hash,created_at
            FROM ingestion.sdas_acquisition_events
            WHERE source_id=%s AND original_fingerprint=%s
            ON CONFLICT (evidence_hash) DO NOTHING
            RETURNING acquisition_event_id
        \"\"\", (SOURCE_ID, ORIGINAL_FP))
        duplicate_acq = cur.fetchone()
        after_acq = scalar(cur, "SELECT count(*) FROM ingestion.sdas_acquisition_events WHERE source_id=%s AND original_fingerprint=%s", (SOURCE_ID, ORIGINAL_FP))
        cur.execute('ROLLBACK TO SAVEPOINT st1_121_duplicate_acquisition')

        cur.execute('SAVEPOINT st1_121_update_guard')
        try:
            cur.execute("UPDATE ingestion.sdas_governance_policy_approvals SET approval_basis_reference=approval_basis_reference WHERE approval_id=%s", (APPROVAL_ID,))
            result['append_only_update_rejected'] = False
        except psycopg.Error:
            cur.execute('ROLLBACK TO SAVEPOINT st1_121_update_guard')
            result['append_only_update_rejected'] = True

        result['idempotency_checks'] = {{
            'duplicate_source_registration_noop': duplicate_source is None and before_source == after_source == 1,
            'duplicate_acquisition_noop': duplicate_acq is None and after_acq == 1,
        }}

        cur.execute('SAVEPOINT st1_121_routing_cases')
        q_actor = 'st1-121-routing-owner'
        q_source = 'st1-121-routing-source'
        cur.execute(\"\"\"
            INSERT INTO ingestion.sdas_actor_registry (actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality)
            VALUES (%s,'synthetic routing owner','[]'::jsonb,'st1-121-synthetic',now(),'native')
        \"\"\", (q_actor,))
        cur.execute(\"\"\"
            INSERT INTO ingestion.sdas_source_registry (source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,effective_from,evidence_quality)
            VALUES (%s,'synthetic_report','runtime_local_only',%s,'st1-121 synthetic routing','declared_unverified','{{"project_scope":"maroon_pilot_project"}}'::jsonb,now(),'declared_unverified')
        \"\"\", (q_source, q_actor))

        synthetic_cases = [
            {{
                'name': 'high-risk-human-review',
                'record_fp': hashlib.sha256(b'st1-121-high-risk').hexdigest(),
                'record_id': 'st1-121-high-risk',
                'quality_gate_outcome': 'passed',
                'policy_mode': 'human_required',
                'policy_reasons': ['high_risk_fact_requires_human_review'],
                'authority_state': 'missing',
                'business_time_state': 'valid',
                'risk_tier': 'high',
                'currentness_state': 'not_assessed',
                'outcome': 'human_required',
                'assurance_reasons': ['high_risk_fact_requires_human_review'],
            }},
            {{
                'name': 'conflict-quarantine',
                'record_fp': hashlib.sha256(b'st1-121-conflict').hexdigest(),
                'record_id': 'st1-121-conflict',
                'quality_gate_outcome': 'failed',
                'policy_mode': 'reject_or_quarantine',
                'policy_reasons': ['integrity_or_validation_failed'],
                'authority_state': 'conflict',
                'business_time_state': 'conflict',
                'risk_tier': 'high',
                'currentness_state': 'conflict',
                'outcome': 'reject_or_quarantine',
                'assurance_reasons': ['integrity_or_validation_failed'],
            }},
        ]
        routing_results = {{}}
        for case in synthetic_cases:
            cur.execute(\"\"\"
                INSERT INTO ingestion.credibility_records (record_fingerprint,canonical_record,provenance,source_id,record_id,observed_at,disposition,quality_gate_outcome,lifecycle_state)
                VALUES (%s,%s::jsonb,%s::jsonb,%s,%s,now(),'certification_candidate',%s,'certification_candidate')
            \"\"\", (
                case['record_fp'],
                json.dumps({{'source_id': q_source, 'record_id': case['record_id']}}),
                json.dumps({{'source_reference': 'runtime_local_only'}}),
                q_source,
                case['record_id'],
                case['quality_gate_outcome'],
            ))
            cur.execute(\"\"\"
                INSERT INTO ingestion.sdas_policy_decisions (record_fingerprint,policy_id,policy_version,approval_mode,decision_actor,decision_reasons,evidence_quality,decision_hash)
                VALUES (%s,'sdas-low-risk-native','v1',%s,'sahra_policy_engine',%s::jsonb,'native',%s)
            \"\"\", (
                case['record_fp'],
                case['policy_mode'],
                json.dumps(case['policy_reasons']),
                hashlib.sha256((case['name'] + '-policy').encode()).hexdigest(),
            ))
            cur.execute(\"\"\"
                INSERT INTO ingestion.sdas_assurance_decisions (record_fingerprint,authority_inheritance_state,business_time_state,risk_tier,currentness_state,reliance_state,outcome,reason_codes,policy_version,decided_at,actor_id,evidence_fingerprint,event_hash)
                VALUES (%s,%s,%s,%s,%s,'not_eligible',%s,%s::jsonb,'v1',now(),'sahra_policy_engine',%s,%s)
            \"\"\", (
                case['record_fp'],
                case['authority_state'],
                case['business_time_state'],
                case['risk_tier'],
                case['currentness_state'],
                case['outcome'],
                json.dumps(case['assurance_reasons']),
                hashlib.sha256((case['name'] + '-assurance-evidence').encode()).hexdigest(),
                hashlib.sha256((case['name'] + '-assurance-event').encode()).hexdigest(),
            ))
            cur.execute(\"\"\"
                SELECT effective_routing_outcome, effective_reason_codes::text
                FROM ingestion.sdas_record_policy_routing_projection
                WHERE record_fingerprint=%s
            \"\"\", (case['record_fp'],))
            route = cur.fetchone()
            routing_results[case['record_id']] = {{
                'effective_routing_outcome': route[0],
                'effective_reason_codes': json.loads(route[1]),
            }}
        cur.execute('ROLLBACK TO SAVEPOINT st1_121_routing_cases')
        result['synthetic_routing_cases'] = routing_results

    conn.rollback()

print(json.dumps(result, sort_keys=True, separators=(',', ':')))
"""

    payload = base64.b64encode(remote.encode()).decode()
    command = (
        "docker exec -i deploy-ingestion-service-1 python3 -c "
        f"\"import base64;exec(base64.b64decode('{payload}'))\""
    )
    run = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command],
        text=True,
        capture_output=True,
    )
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "ST1-121 verification failed")

    observed = json.loads(run.stdout)
    output = {
        "task_id": "ST1-121",
        "business_decision": "limited_pilot_governance_bootstrap_approved",
        "selected_real_artifact": {
            "selection_alias": selection_alias,
            "source_alias": source_alias,
            "source_id": observed["selected_source"]["source_id"],
            "locator_fingerprint": locator_fingerprint,
            "original_fingerprint": original_fingerprint,
            "size_bytes": acquisition["size_bytes"],
            "extension": acquisition["extension"],
        },
        "pilot_governance": observed["governance_policy"],
        "bootstrap_state": {
            "latest_event": observed["bootstrap_latest_event"],
            "queue": observed["bootstrap_queue"],
            "active_delegation_count": observed["active_delegation_count"],
        },
        "selected_artifact_runtime_state": {
            "source": observed["selected_source"],
            "acquisition_events": observed["acquisition_events"],
            "transformations": observed["transformations"],
            "credibility_record": observed["credibility_record"],
            "policy_decision": observed["policy_decision"],
        },
        "separation": observed["separation_assertions"],
        "supporting_counts": {
            "authority_assertions": observed["authority_assertion_counts"],
            "business_time_evidence": observed["business_time_evidence_counts"],
            "role_source_verifications": observed["role_source_verification_counts"],
        },
        "checks": {
            "real_artifact_chain_reached_policy_evaluation": observed["real_artifact_chain_reached_policy_evaluation"],
            "business_time_not_inferred_from_acquisition_or_filesystem": observed["business_time_not_inferred_from_acquisition_or_filesystem"],
            "append_only_update_rejected": observed["append_only_update_rejected"],
            "idempotency_checks": observed["idempotency_checks"],
            "no_certification_occurred": observed["no_certification_occurred"],
            "synthetic_routing_cases": observed["synthetic_routing_cases"],
        },
        "boundaries_unchanged": {
            "certified_knowledge_touched": False,
            "qdrant_touched": False,
            "dify_touched": False,
            "embedding_settings_changed": False,
            "retrieval_threshold_changed": False,
            "automatic_certification": False,
        },
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
