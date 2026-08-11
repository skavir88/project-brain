#!/usr/bin/env python3
"""Create a deterministic non-mutating dry-run plan for the first real attempt.

This planner consumes:
1. an ST1-078 bundle, and
2. an ST1-083 native-record metadata artifact,

then uses the ST1-083 preflight verifier to decide whether the first real
selected-class runtime attempt is blocked or ready. It never mutates runtime.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / "scripts" / "verify_st1_083_first_native_record_preflight.py"


def run_preflight(bundle: Path, native_record: Path | None) -> dict[str, object]:
    command = [sys.executable, str(VERIFY_SCRIPT), "--bundle", str(bundle)]
    if native_record is not None:
        command.extend(["--native-record", str(native_record)])
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def planned_writes(native_record_summary: dict[str, object]) -> list[dict[str, object]]:
    source_id = native_record_summary.get("source_id")
    media_type = native_record_summary.get("media_type")
    resolution_source = native_record_summary.get("resolution_source")
    return [
        {
            "sequence": 1,
            "phase": "source_registration",
            "target": "ingestion.sdas_source_registry",
            "write_kind": "append_or_idempotent_insert",
            "purpose": "register the exact selected-class source/system identity and scope",
            "minimum_inputs": [
                "source_id",
                "source_type",
                "non_sensitive_location_class",
                "owning_role_class",
                "project_scope",
                "report_class",
                "authority_state",
                "evidence_reference",
            ],
            "derived_summary": {"source_id": source_id},
        },
        {
            "sequence": 2,
            "phase": "source_registration",
            "target": "ingestion.sdas_source_control_verifications",
            "write_kind": "append_insert",
            "purpose": "persist the exact source-control verification that ties the source to the accountable role and workbook reporting-period rule",
            "minimum_inputs": [
                "source_id",
                "accountable_actor_id",
                "project_scope",
                "document_data_class",
                "business_time_rule",
                "evidence_reference",
                "evidence_fingerprint",
            ],
            "derived_summary": {"resolution_source": resolution_source},
        },
        {
            "sequence": 3,
            "phase": "acquisition",
            "target": "ingestion.sdas_acquisition_events",
            "write_kind": "append_or_idempotent_insert",
            "purpose": "record read-only native acquisition, original SHA-256, size, media type, and source reference",
            "minimum_inputs": [
                "source_id",
                "acquired_at",
                "actor_id",
                "acquisition_method",
                "source_reference",
                "original_fingerprint",
                "size_bytes",
                "media_type",
                "evidence_hash",
            ],
            "derived_summary": {"media_type": media_type},
        },
        {
            "sequence": 4,
            "phase": "transformation",
            "target": "ingestion.sdas_transformations",
            "write_kind": "append_or_idempotent_insert",
            "purpose": "record deterministic transformation continuity from original fingerprint to canonical output fingerprint",
            "minimum_inputs": [
                "acquisition_event_id",
                "transformation_type",
                "tool_name",
                "tool_version",
                "transformed_at",
                "input_fingerprint",
                "output_fingerprint",
                "deterministic",
                "evidence_hash",
            ],
        },
        {
            "sequence": 5,
            "phase": "record_intake",
            "target": "POST /v1/records -> ingestion.credibility_records",
            "write_kind": "service_insert",
            "purpose": "create the first real selected-class credibility record through the existing intake contract",
            "minimum_inputs": [
                "source_id",
                "record_id",
                "payload.source_id",
                "payload.data_class",
                "provenance.source_reference",
                "provenance.acquisition_event_id",
                "provenance.evidence_quality",
                "observed_at",
            ],
            "expected_service_gate": "certification_candidate",
        },
        {
            "sequence": 6,
            "phase": "policy_evaluation",
            "target": "ingestion.sdas_policy_decisions",
            "write_kind": "append_or_idempotent_insert",
            "purpose": "persist the first policy decision for the real native record",
            "minimum_inputs": [
                "record_fingerprint",
                "policy_id",
                "policy_version",
                "approval_mode",
                "decision_actor",
                "decision_reasons",
                "evidence_quality",
                "decision_hash",
            ],
            "expected_outcome_if_all_controls_hold": "policy_automatic",
        },
    ]


def hard_stops(preflight: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "gate": "before_mutation",
            "condition": "bundle_readiness must remain PENDING_INDEPENDENT_VERIFICATION and native_record_readiness must be READY_FOR_FIRST_REAL_RUNTIME_ATTEMPT",
            "current_status": {
                "bundle_readiness": preflight["bundle_readiness"]["status"],
                "native_record_readiness": preflight["native_record_readiness"]["status"],
            },
        },
        {
            "gate": "before_policy_automatic_claim",
            "condition": "runtime write sequence must be executed successfully and the resulting decision must still be checked against exact-scope active delegation, business time, risk, and validation controls",
            "current_status": "not_executed_in_dry_run",
        },
        {
            "gate": "before_certification",
            "condition": "first real policy_automatic record must stop before certification unless explicit user approval is later provided",
            "current_status": "hard_stop_preserved",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the ST1-078 bundle JSON file")
    parser.add_argument("--native-record", type=Path, help="Path to the native-record metadata JSON file")
    args = parser.parse_args()

    preflight = run_preflight(args.bundle, args.native_record)
    ready = bool(preflight.get("ready_for_real_runtime_attempt"))
    output: dict[str, object] = {
        "schema_version": "st1-084-first-real-runtime-dry-run-v1",
        "candidate_class_id": preflight["candidate_class_id"],
        "project_scope": preflight["project_scope"],
        "dry_run_only": True,
        "runtime_mutation_performed": False,
        "preflight": preflight,
        "planned_write_sequence": planned_writes(preflight.get("native_record_summary", {})) if ready else [],
        "hard_stops": hard_stops(preflight),
        "planner_result": "READY_DRY_RUN_PLAN" if ready else "BLOCKED_DRY_RUN_PLAN",
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
