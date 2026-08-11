#!/usr/bin/env python3
"""Compile a non-secret execution manifest for the first real selected-class attempt.

This compiler is local-only and non-mutating. It consumes the ST1-078 bundle,
the ST1-083 native-record metadata artifact, and the ST1-084 dry-run planner.
If the plan is ready, it emits a non-secret operator-facing manifest showing
the exact ordered write sequence, minimum payloads, and hard stops.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_SCRIPT = ROOT / "scripts" / "plan_st1_084_first_real_runtime_attempt.py"


def run_planner(bundle: Path, native_record: Path | None) -> dict[str, object]:
    command = [sys.executable, str(PLAN_SCRIPT), "--bundle", str(bundle)]
    if native_record is not None:
        command.extend(["--native-record", str(native_record)])
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def manifest_steps(native_record: dict[str, object], plan_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    source_registration = native_record["source_registration"]
    acquisition = native_record["acquisition"]
    transformation = native_record["transformation"]
    business_time = native_record["business_time"]
    policy_context = native_record["policy_context"]

    intake_payload = {
        "source_id": source_registration["source_id"],
        "record_id": "RUNTIME_REQUIRED_INPUT",
        "payload": {
            "source_id": source_registration["source_id"],
            "data_class": "project_controls_progress_workbook_low_risk_fact",
            "report_period": business_time["report_period_value"],
            "fact_payload": "RUNTIME_REQUIRED_INPUT",
        },
        "provenance": {
            "source_reference": acquisition["source_reference"],
            "acquisition_event_id": "RUNTIME_OUTPUT_FROM_STEP_3",
            "evidence_quality": "native",
        },
        "observed_at": "RUNTIME_REQUIRED_INPUT",
    }

    policy_payload = {
        "policy_id": policy_context["policy_id"],
        "policy_version": policy_context["policy_version"],
        "approval_mode": "policy_automatic",
        "decision_actor": "sahra_policy_engine",
        "decision_reasons": ["all_required_policy_evidence_present"],
        "evidence_quality": "native",
        "decision_hash": "RUNTIME_DERIVED_FROM_PERSISTED_FACTS",
    }

    compiled: list[dict[str, object]] = []
    for row in plan_rows:
        sequence = int(row["sequence"])
        payload: dict[str, object]
        if sequence == 1:
            payload = {
                "source_id": source_registration["source_id"],
                "source_type": source_registration["source_type"],
                "non_sensitive_location_class": source_registration["non_sensitive_location_class"],
                "owning_role_class": source_registration["owning_role_class"],
                "project_scope": source_registration["project_scope"],
                "report_class": source_registration["report_class"],
                "authority_state": source_registration["authority_state"],
                "evidence_reference": source_registration["evidence_reference"],
            }
        elif sequence == 2:
            payload = {
                "source_id": source_registration["source_id"],
                "project_scope": source_registration["project_scope"],
                "document_data_class": source_registration["report_class"],
                "business_time_rule": business_time["resolution_source"],
                "evidence_reference": source_registration["evidence_reference"],
                "accountable_actor_id": "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_BUNDLE",
                "evidence_fingerprint": "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_BUNDLE",
            }
        elif sequence == 3:
            payload = {
                "source_id": source_registration["source_id"],
                "acquired_at": acquisition["acquired_at"],
                "source_reference": acquisition["source_reference"],
                "acquisition_method": acquisition["acquisition_method"],
                "original_fingerprint": acquisition["original_fingerprint"],
                "size_bytes": acquisition["size_bytes"],
                "media_type": acquisition["media_type"],
                "read_only": acquisition["read_only"],
                "actor_id": "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_BUNDLE",
                "evidence_hash": "RUNTIME_DERIVED_FROM_ACQUISITION_FACTS",
            }
        elif sequence == 4:
            payload = {
                "transformation_type": transformation["transformation_type"],
                "tool_name": transformation["tool_name"],
                "tool_version": transformation["tool_version"],
                "transformed_at": transformation["transformed_at"],
                "input_fingerprint": transformation["input_fingerprint"],
                "output_fingerprint": transformation["output_fingerprint"],
                "deterministic": transformation["deterministic"],
                "lineage_complete": transformation["lineage_complete"],
                "acquisition_event_id": "RUNTIME_OUTPUT_FROM_STEP_3",
                "evidence_hash": "RUNTIME_DERIVED_FROM_TRANSFORMATION_FACTS",
            }
        elif sequence == 5:
            payload = intake_payload
        elif sequence == 6:
            payload = policy_payload
        else:
            payload = {}
        compiled.append(
            {
                "sequence": sequence,
                "phase": row["phase"],
                "target": row["target"],
                "purpose": row["purpose"],
                "write_kind": row["write_kind"],
                "payload_shape": payload,
            }
        )
    return compiled


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the ST1-078 bundle JSON file")
    parser.add_argument("--native-record", type=Path, help="Path to the native-record metadata JSON file")
    args = parser.parse_args()

    plan = run_planner(args.bundle, args.native_record)
    ready = plan.get("planner_result") == "READY_DRY_RUN_PLAN"

    output: dict[str, object] = {
        "schema_version": "st1-085-first-real-attempt-manifest-v1",
        "candidate_class_id": plan["candidate_class_id"],
        "project_scope": plan["project_scope"],
        "compiler_result": "READY_EXECUTION_MANIFEST" if ready else "BLOCKED_EXECUTION_MANIFEST",
        "runtime_mutation_performed": False,
        "dry_run_plan": plan,
        "execution_manifest": [],
    }
    if ready:
        native_record = json.loads(args.native_record.read_text(encoding="utf-8")) if args.native_record else {}
        output["execution_manifest"] = compiled = manifest_steps(native_record, plan["planned_write_sequence"])
        output["manifest_summary"] = {
            "step_count": len(compiled),
            "contains_secret_values": False,
            "requires_runtime_operator_inputs": [
                "verified accountable_actor_id",
                "verified evidence_fingerprint values",
                "real record_id",
                "real observed_at",
                "real low-risk fact payload",
            ],
            "hard_stops": plan["hard_stops"],
        }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
