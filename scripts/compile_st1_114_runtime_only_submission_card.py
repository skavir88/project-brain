#!/usr/bin/env python3
"""Compile a runtime-only submission card for the first real selected-class attempt.

This compiler is deterministic, local-only, and non-mutating. It reduces the
selected-class pre-certification hard-stop gate package plus existing missing-
input surfaces to only the exact real operator-supplied values still required
to execute the first `policy_automatic` attempt.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARD_STOP_GATE_SCRIPT = ROOT / "scripts" / "compile_st1_113_pre_certification_hard_stop_gate.py"
MISSING_INPUT_PACK_SCRIPT = ROOT / "scripts" / "compile_st1_097_missing_input_pack.py"
READINESS_SUMMARY_SCRIPT = ROOT / "scripts" / "compile_st1_096_real_run_readiness_summary.py"

EXACT_RUNTIME_VALUES = [
    "verified accountable_actor_id",
    "verified evidence_fingerprint values",
    "real record_id",
    "real observed_at",
    "real low-risk fact payload",
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
    hard_stop_gate = run_json(HARD_STOP_GATE_SCRIPT, common_step_args)
    missing_input_pack = run_json(
        MISSING_INPUT_PACK_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )
    readiness_summary = run_json(
        READINESS_SUMMARY_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )

    ready_gate = hard_stop_gate.get("gate_package_status") == "READY_PRE_CERTIFICATION_HARD_STOP_GATE"
    launch_package = hard_stop_gate.get("pre_certification_hard_stop_gate", {}).get("launch_package_summary", {})
    missing_pack = missing_input_pack.get("missing_input_pack", {})
    ready = ready_gate and missing_input_pack.get("readiness_status") == "ready_to_run"

    output = {
        "schema_version": "st1-114-runtime-only-submission-card-v1",
        "candidate_class_id": hard_stop_gate.get("candidate_class_id"),
        "project_scope": hard_stop_gate.get("project_scope"),
        "submission_card_status": "READY_RUNTIME_ONLY_SUBMISSION_CARD" if ready else "BLOCKED_RUNTIME_ONLY_SUBMISSION_CARD",
        "runtime_only_submission_card": {
            "required_runtime_values": EXACT_RUNTIME_VALUES if ready_gate else [],
            "remaining_runtime_only_fields": launch_package.get("remaining_runtime_only_fields", []),
            "required_confirmations": hard_stop_gate.get("pre_certification_hard_stop_gate", {}).get("required_confirmations", {}),
            "remaining_checklist_items": hard_stop_gate.get("pre_certification_hard_stop_gate", {}).get("remaining_checklist_items", {}),
            "current_readiness_status": readiness_summary.get("readiness_status"),
            "missing_input_state": missing_pack.get("missing_input_state"),
        },
        "blocking_reasons": {
            "gate_package_status": hard_stop_gate.get("gate_package_status"),
            "readiness_status": readiness_summary.get("readiness_status"),
            "missing_input_counts": missing_pack.get("counts", {}),
            "remaining_checklist_items": hard_stop_gate.get("pre_certification_hard_stop_gate", {}).get("remaining_checklist_items", {}),
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
