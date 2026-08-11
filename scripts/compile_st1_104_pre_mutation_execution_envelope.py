#!/usr/bin/env python3
"""Compile a first-real pre-mutation execution envelope.

This compiler is deterministic, local-only, and non-mutating. It packages the
selected-class arrival packet together with the existing hard-stop-aware
execution stack into one exact pre-mutation execution object for a future real
selected-class attempt.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARRIVAL_PACKET_SCRIPT = ROOT / "scripts" / "compile_st1_103_arrival_packet.py"
DOSSIER_SCRIPT = ROOT / "scripts" / "compile_st1_093_first_real_execution_dossier.py"
LAUNCH_SCRIPT = ROOT / "scripts" / "compile_st1_095_final_operator_launch_package.py"


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

    common_execution = [
        "--bundle", str(args.submission_bundle),
        "--native-record", str(args.submission_native_record),
        "--operator-inputs", str(args.operator_inputs),
        "--receipt", str(args.receipt),
        "--batch", str(args.batch),
    ]
    arrival_packet = run_json(
        ARRIVAL_PACKET_SCRIPT,
        [
            "--expected-fingerprint", args.expected_fingerprint,
            "--baseline-bundle", str(args.baseline_bundle),
            "--baseline-native-record", str(args.baseline_native_record),
            "--submission-bundle", str(args.submission_bundle),
            "--submission-native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )
    dossier = run_json(DOSSIER_SCRIPT, common_execution)
    launch = run_json(LAUNCH_SCRIPT, common_execution)

    ready = (
        arrival_packet.get("arrival_packet_status") == "READY_CHECKLIST"
        and dossier.get("dossier_status") == "READY_FIRST_REAL_EXECUTION_DOSSIER"
        and launch.get("launch_package_status") == "READY_FINAL_OPERATOR_LAUNCH_PACKAGE"
    )

    output = {
        "schema_version": "st1-104-pre-mutation-execution-envelope-v1",
        "candidate_class_id": arrival_packet.get("candidate_class_id"),
        "project_scope": arrival_packet.get("project_scope"),
        "execution_envelope_status": "READY_PRE_MUTATION_EXECUTION_ENVELOPE" if ready else "BLOCKED_PRE_MUTATION_EXECUTION_ENVELOPE",
        "pre_mutation_execution_envelope": {
            "arrival_packet_status": arrival_packet.get("arrival_packet_status"),
            "dossier_status": dossier.get("dossier_status"),
            "launch_package_status": launch.get("launch_package_status"),
            "readiness_transition": arrival_packet.get("operator_ready_payload", {}).get("readiness_transition"),
            "next_action_transition": arrival_packet.get("operator_ready_payload", {}).get("next_action_transition"),
            "ordered_runtime_step_count": launch.get("launch_package", {}).get("ordered_runtime_step_count"),
            "required_operator_inputs": launch.get("launch_package", {}).get("required_operator_inputs"),
            "hard_stop_count": launch.get("launch_package", {}).get("hard_stop_count"),
            "hard_stop_report_ready": launch.get("launch_package", {}).get("hard_stop_report_ready"),
            "remaining_checklist_items": arrival_packet.get("operator_ready_payload", {}).get("remaining_checklist_items"),
        },
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_file_acquired": False,
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
