#!/usr/bin/env python3
"""Compile a first-real execution worksheet for the selected-class attempt.

This compiler is deterministic, local-only, and non-mutating. It maps the
exact five real runtime values from the selected-class readiness surfaces onto
the existing six-step runtime sequence and preserved stop-before-certification
boundary without adding new trust semantics.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCRIPT = ROOT / "scripts" / "compile_st1_085_first_real_attempt_manifest.py"
READINESS_SCRIPT = ROOT / "scripts" / "compile_st1_096_real_run_readiness_summary.py"
MISSING_INPUT_SCRIPT = ROOT / "scripts" / "compile_st1_097_missing_input_pack.py"
HARD_STOP_REPORT_SCRIPT = ROOT / "scripts" / "compile_st1_092_first_real_hard_stop_report.py"


EXACT_RUNTIME_VALUES = [
    "verified accountable_actor_id",
    "verified evidence_fingerprint values",
    "real record_id",
    "real observed_at",
    "real low-risk fact payload",
]

RUNTIME_VALUE_MAP = [
    {
        "runtime_value": "verified accountable_actor_id",
        "used_in_steps": [2, 3],
        "target_fields": [
            "step_2.payload_shape.accountable_actor_id",
            "step_3.payload_shape.actor_id",
        ],
    },
    {
        "runtime_value": "verified evidence_fingerprint values",
        "used_in_steps": [2],
        "target_fields": [
            "step_2.payload_shape.evidence_fingerprint",
            "step_2.payload_shape.evidence_reference",
        ],
    },
    {
        "runtime_value": "real record_id",
        "used_in_steps": [5],
        "target_fields": [
            "step_5.payload_shape.record_id",
        ],
    },
    {
        "runtime_value": "real observed_at",
        "used_in_steps": [5],
        "target_fields": [
            "step_5.payload_shape.observed_at",
        ],
    },
    {
        "runtime_value": "real low-risk fact payload",
        "used_in_steps": [5],
        "target_fields": [
            "step_5.payload_shape.payload.fact_payload",
        ],
    },
]


def run_json(script: Path, args: list[str]) -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-fingerprint", required=True, help="Expected parked external-gate fingerprint")
    parser.add_argument("--baseline-bundle", type=Path, required=True, help="Baseline ST1-078 bundle JSON")
    parser.add_argument("--baseline-native-record", type=Path, required=True, help="Baseline native-record JSON")
    parser.add_argument("--submission-bundle", type=Path, required=True, help="Submitted ST1-078 bundle JSON")
    parser.add_argument("--submission-native-record", type=Path, required=True, help="Submitted native-record JSON")
    parser.add_argument("--operator-inputs", type=Path, required=True, help="Path to ST1-088 operator-input JSON")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to ST1-089 receipt JSON")
    parser.add_argument("--batch", type=Path, required=True, help="Path to ST1-090 batch JSON")
    args = parser.parse_args()

    manifest = run_json(
        MANIFEST_SCRIPT,
        ["--bundle", str(args.submission_bundle), "--native-record", str(args.submission_native_record)],
    )
    readiness_summary = run_json(
        READINESS_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )
    missing_input_pack = run_json(
        MISSING_INPUT_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )
    hard_stop_report = run_json(
        HARD_STOP_REPORT_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
        ],
    )

    readiness_status = readiness_summary.get("readiness_status")
    missing_pack = missing_input_pack.get("missing_input_pack", {})
    ready = (
        manifest.get("compiler_result") == "READY_EXECUTION_MANIFEST"
        and readiness_status == "ready_to_run"
        and hard_stop_report.get("report_status") == "READY_HARD_STOP_REPORT"
    )

    worksheet_steps: list[dict[str, Any]] = []
    if manifest.get("compiler_result") == "READY_EXECUTION_MANIFEST":
        for row in manifest.get("execution_manifest", []):
            seq = row.get("sequence")
            worksheet_steps.append(
                {
                    "sequence": seq,
                    "target": row.get("target"),
                    "purpose": row.get("purpose"),
                    "runtime_values_used": [
                        item["runtime_value"]
                        for item in RUNTIME_VALUE_MAP
                        if seq in item["used_in_steps"]
                    ],
                    "preserved_payload_shape": row.get("payload_shape"),
                }
            )

    output = {
        "schema_version": "st1-115-first-real-execution-worksheet-v1",
        "candidate_class_id": manifest.get("candidate_class_id"),
        "project_scope": manifest.get("project_scope"),
        "worksheet_status": "READY_FIRST_REAL_EXECUTION_WORKSHEET" if ready else "BLOCKED_FIRST_REAL_EXECUTION_WORKSHEET",
        "first_real_execution_worksheet": {
            "runtime_values": EXACT_RUNTIME_VALUES if ready else [],
            "runtime_value_map": RUNTIME_VALUE_MAP if manifest.get("compiler_result") == "READY_EXECUTION_MANIFEST" else [],
            "execution_steps": worksheet_steps,
            "required_confirmations": {
                "manifest_ready": manifest.get("compiler_result") == "READY_EXECUTION_MANIFEST",
                "readiness_status": readiness_status,
                "hard_stop_report_ready": hard_stop_report.get("report_status") == "READY_HARD_STOP_REPORT",
                "hard_stop_count": readiness_summary.get("hard_stop_count"),
            },
            "remaining_checklist_items": {
                "external_evidence_bundle_items": missing_pack.get("exact_missing_inputs", {}).get("external_evidence_requirements", []),
                "runtime_only_items": missing_pack.get("exact_missing_inputs", {}).get("runtime_only_requirements", []),
            },
            "hard_stop_boundary": hard_stop_report.get("hard_stop_report", {}),
        },
        "blocking_reasons": {
            "manifest_status": manifest.get("compiler_result"),
            "readiness_status": readiness_status,
            "hard_stop_report_status": hard_stop_report.get("report_status"),
            "remaining_checklist_items": {
                "external_evidence_bundle_items": missing_pack.get("exact_missing_inputs", {}).get("external_evidence_requirements", []),
                "runtime_only_items": missing_pack.get("exact_missing_inputs", {}).get("runtime_only_requirements", []),
            },
        },
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_source_control_verified": False,
            "real_file_acquired": False,
            "real_transformation_recorded": False,
            "real_record_ingested": False,
            "real_policy_decision_executed": False,
            "real_certification_performed": False,
            "trust_boundary_changed": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
