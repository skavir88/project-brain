#!/usr/bin/env python3
"""Compile a first-real execution trigger card for the selected-class attempt.

This compiler is deterministic, local-only, and non-mutating. It collapses the
selected-class execution worksheet and readiness surfaces into one truthful
next-action outcome:

- execute_now
- wait_for_external_evidence
- wait_for_runtime_only_values
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSHEET_SCRIPT = ROOT / "scripts" / "compile_st1_115_first_real_execution_worksheet.py"
READINESS_SCRIPT = ROOT / "scripts" / "compile_st1_096_real_run_readiness_summary.py"
MISSING_INPUT_SCRIPT = ROOT / "scripts" / "compile_st1_097_missing_input_pack.py"


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

    common_step_args = [
        "--expected-fingerprint", args.expected_fingerprint,
        "--baseline-bundle", str(args.baseline_bundle),
        "--baseline-native-record", str(args.baseline_native_record),
        "--submission-bundle", str(args.submission_bundle),
        "--submission-native-record", str(args.submission_native_record),
        "--operator-inputs", str(args.operator_inputs),
        "--receipt", str(args.receipt),
        "--batch", str(args.batch),
    ]
    worksheet = run_json(WORKSHEET_SCRIPT, common_step_args)
    readiness = run_json(
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

    readiness_status = readiness.get("readiness_status")
    if readiness_status == "ready_to_run":
        next_action = "execute_now"
    elif readiness_status == "waiting_for_runtime_only_fields":
        next_action = "wait_for_runtime_only_values"
    else:
        next_action = "wait_for_external_evidence"

    worksheet_payload = worksheet.get("first_real_execution_worksheet", {})
    missing_pack = missing_input_pack.get("missing_input_pack", {})
    ready = (
        worksheet.get("worksheet_status") == "READY_FIRST_REAL_EXECUTION_WORKSHEET"
        and readiness_status == "ready_to_run"
    )

    output = {
        "schema_version": "st1-116-execution-trigger-card-v1",
        "candidate_class_id": worksheet.get("candidate_class_id"),
        "project_scope": worksheet.get("project_scope"),
        "trigger_card_status": "READY_EXECUTION_TRIGGER_CARD" if ready else "BLOCKED_EXECUTION_TRIGGER_CARD",
        "execution_trigger_card": {
            "next_action": next_action,
            "readiness_status": readiness_status,
            "runtime_values": worksheet_payload.get("runtime_values", []),
            "runtime_only_items": missing_pack.get("exact_missing_inputs", {}).get("runtime_only_requirements", []),
            "external_evidence_items": missing_pack.get("exact_missing_inputs", {}).get("external_evidence_requirements", []),
            "hard_stop_boundary": worksheet_payload.get("hard_stop_boundary", {}),
        },
        "blocking_reasons": {
            "worksheet_status": worksheet.get("worksheet_status"),
            "readiness_status": readiness_status,
            "missing_input_counts": missing_pack.get("counts", {}),
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
