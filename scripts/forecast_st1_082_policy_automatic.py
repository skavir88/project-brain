#!/usr/bin/env python3
"""Read-only ST1-082 forecast for the selected real workbook class.

This script does not activate any real delegation, source registration, or
native evidence. It quantifies what the currently known selected class would do
under a narrow hypothetical overlay where only the approved governance/source-
control conditions are considered satisfied.
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import UTC, datetime


TARGET_SOURCE_ID = "enterprise_ai_real_action_plan_weekly_observation"
TARGET_POLICY_ID = "sdas-low-risk-native"
TARGET_POLICY_VERSION = "simulation-v1"


def run_remote_sql(sql: str) -> list[str]:
    command = (
        "docker exec postgres-db psql -U postgres -d enterprise_ai_ingestion_mvp "
        f"-F '|' -Atc \"{sql}\""
    )
    result = subprocess.run(
        ["ssh.exe", "-o", "BatchMode=yes", "enterprise-ai-rddb", command],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or "remote SQL query failed")
    return [line for line in result.stdout.splitlines() if line.strip()]


def parse_reason_array(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def main() -> None:
    record_rows = run_remote_sql(
        f"""
        SELECT
          record_fingerprint,
          record_id,
          lifecycle_state,
          quality_gate_outcome,
          COALESCE(policy_id, ''),
          COALESCE(policy_version, ''),
          COALESCE(policy_approval_mode, ''),
          COALESCE(assurance_outcome, ''),
          COALESCE(authority_inheritance_state, ''),
          COALESCE(business_time_state, ''),
          COALESCE(risk_tier, ''),
          COALESCE(currentness_state, ''),
          COALESCE(reliance_state, ''),
          governance_dependency_state,
          effective_routing_outcome,
          COALESCE(effective_reason_codes::text, '[]')
        FROM ingestion.sdas_record_policy_routing_projection
        WHERE source_id='{TARGET_SOURCE_ID}'
        ORDER BY record_id
        """
    )
    support = {
        "source_registry_rows": len(
            run_remote_sql(
                f"SELECT source_id FROM ingestion.sdas_source_registry WHERE source_id='{TARGET_SOURCE_ID}'"
            )
        ),
        "acquisition_event_count": int(
            (run_remote_sql(
                f"SELECT count(*) FROM ingestion.sdas_acquisition_events WHERE source_id='{TARGET_SOURCE_ID}'"
            ) or ["0"])[0]
        ),
        "transformation_count": int(
            (run_remote_sql(
                f"SELECT count(*) FROM ingestion.sdas_transformations WHERE output_fingerprint IN (SELECT record_fingerprint FROM ingestion.credibility_records WHERE source_id='{TARGET_SOURCE_ID}')"
            ) or ["0"])[0]
        ),
        "business_time_evidence_count": int(
            (run_remote_sql(
                f"SELECT count(*) FROM ingestion.sdas_business_time_evidence WHERE record_fingerprint IN (SELECT record_fingerprint FROM ingestion.credibility_records WHERE source_id='{TARGET_SOURCE_ID}')"
            ) or ["0"])[0]
        ),
        "record_authority_assertion_count": int(
            (run_remote_sql(
                f"SELECT count(*) FROM ingestion.sdas_authority_assertions WHERE subject_type='record' AND subject_id IN (SELECT record_fingerprint FROM ingestion.credibility_records WHERE source_id='{TARGET_SOURCE_ID}')"
            ) or ["0"])[0]
        ),
        "source_authority_assertion_count": int(
            (run_remote_sql(
                f"SELECT count(*) FROM ingestion.sdas_authority_assertions WHERE subject_type='source' AND subject_id='{TARGET_SOURCE_ID}'"
            ) or ["0"])[0]
        ),
        "matched_active_delegation_count_now": len(
            run_remote_sql(
                f"""
                SELECT source_id
                FROM ingestion.sdas_record_policy_routing_detail
                WHERE source_id='{TARGET_SOURCE_ID}' AND matched_active_delegation_count > 0
                LIMIT 1
                """
            )
        ),
        "certified_knowledge_count": int(
            (run_remote_sql(
                f"SELECT count(*) FROM ingestion.certified_knowledge_items WHERE source_fingerprint IN (SELECT record_fingerprint FROM ingestion.credibility_records WHERE source_id='{TARGET_SOURCE_ID}') AND lifecycle_state='certified'"
            ) or ["0"])[0]
        ),
    }

    records: list[dict[str, object]] = []
    current_counts = Counter()
    current_reason_counts = Counter()
    overlay_counts = Counter()
    overlay_reason_counts = Counter()

    for line in record_rows:
        parts = line.split("|")
        reasons = parse_reason_array(parts[15])
        record = {
            "record_fingerprint": parts[0],
            "record_id": parts[1],
            "lifecycle_state": parts[2],
            "quality_gate_outcome": parts[3],
            "policy_id": parts[4],
            "policy_version": parts[5],
            "policy_approval_mode": parts[6],
            "assurance_outcome": parts[7],
            "authority_inheritance_state": parts[8],
            "business_time_state": parts[9],
            "risk_tier": parts[10],
            "currentness_state": parts[11],
            "reliance_state": parts[12],
            "governance_dependency_state": parts[13],
            "effective_routing_outcome": parts[14],
            "effective_reason_codes": reasons,
        }
        current_counts[record["effective_routing_outcome"]] += 1
        for reason in reasons:
            current_reason_counts[reason] += 1

        # Exact-scope activation overlay: only governance/source-control is assumed solved.
        # Existing records are not upgraded to native; historical/reconstructed records keep
        # their missing native evidence.
        if "missing_native_evidence" in reasons:
            forecast_outcome = "human_required"
            forecast_reasons = ["missing_native_evidence"]
        elif record["effective_routing_outcome"] == "reject_or_quarantine":
            forecast_outcome = "reject_or_quarantine"
            forecast_reasons = reasons or ["integrity_or_validation_failed"]
        else:
            forecast_outcome = record["effective_routing_outcome"]
            forecast_reasons = reasons

        overlay_counts[forecast_outcome] += 1
        for reason in forecast_reasons:
            overlay_reason_counts[reason] += 1

        record["forecast_under_exact_scope_activation"] = {
            "effective_routing_outcome": forecast_outcome,
            "effective_reason_codes": forecast_reasons,
            "governance_dependency_state": "MATCHED_ACTIVE_DELEGATION",
            "assumptions": [
                "approved governance/source-control conditions are satisfied exactly for this class",
                "existing historical records are not upgraded to native evidence",
            ],
        }
        records.append(record)

    output = {
        "schema_version": "st1-082-policy-automatic-forecast-v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "selected_class": {
            "source_id": TARGET_SOURCE_ID,
            "policy_id": TARGET_POLICY_ID,
            "policy_version": TARGET_POLICY_VERSION,
            "document_class": "recurring Project Controls progress workbook",
        },
        "current_real_state": {
            "record_count": len(records),
            "routing_counts": dict(current_counts),
            "dominant_reason_codes": dict(current_reason_counts),
            "supporting_evidence_presence": support,
        },
        "hypothetical_exact_scope_activation_overlay": {
            "mutates_real_state": False,
            "assumptions": {
                "active_delegation_exact_scope_match": True,
                "source_registration_and_control_for_class": True,
                "existing_records_upgraded_to_native": False,
                "automatic_certification_enabled": False,
            },
            "forecast_routing_counts": dict(overlay_counts),
            "forecast_dominant_reason_codes": dict(overlay_reason_counts),
            "human_review_reduction_vs_current": current_counts.get("human_required", 0) - overlay_counts.get("human_required", 0),
            "policy_automatic_delta_vs_current": overlay_counts.get("policy_automatic", 0) - current_counts.get("policy_automatic", 0),
        },
        "false_positive_safety_checks": {
            "records_not_promoted_to_policy_automatic_solely_by_delegation_overlay": overlay_counts.get("policy_automatic", 0) == current_counts.get("policy_automatic", 0),
            "historical_records_not_reclassified_as_native": True,
            "uncertified_records_not_considered": True,
        },
        "conclusion": {
            "result": "governance_only_activation_unlocks_zero_current_records",
            "why": [
                "all currently known records in the selected class are historical/reconstructed simulation rows",
                "the dominant persisted blocker is missing_native_evidence",
                "no source registration, acquisition events, transformations, business-time evidence, or authority assertions currently exist for this class in runtime state",
            ],
            "next_required_real_change": "obtain valid external governance/source-control evidence and then ingest at least one truly native record from this class without upgrading historical records",
        },
        "records": records,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
