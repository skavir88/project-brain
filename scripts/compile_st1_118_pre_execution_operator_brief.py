#!/usr/bin/env python3
"""Compile a final pre-execution operator brief for the selected-class attempt.

This compiler is deterministic, local-only, and non-mutating. It combines the
truthful next action, the smallest activation request, the six-step execution
mapping, and the preserved stop-before-certification boundary into one concise
handoff for a future first-real selected-class attempt.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACTIVATION_PACKET_SCRIPT = ROOT / "scripts" / "compile_st1_117_activation_request_packet.py"
WORKSHEET_SCRIPT = ROOT / "scripts" / "compile_st1_115_first_real_execution_worksheet.py"
HARD_STOP_REPORT_SCRIPT = ROOT / "scripts" / "compile_st1_092_first_real_hard_stop_report.py"


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

    common_args = [
        "--expected-fingerprint", args.expected_fingerprint,
        "--baseline-bundle", str(args.baseline_bundle),
        "--baseline-native-record", str(args.baseline_native_record),
        "--submission-bundle", str(args.submission_bundle),
        "--submission-native-record", str(args.submission_native_record),
        "--operator-inputs", str(args.operator_inputs),
        "--receipt", str(args.receipt),
        "--batch", str(args.batch),
    ]

    activation_packet = run_json(ACTIVATION_PACKET_SCRIPT, common_args)
    worksheet = run_json(WORKSHEET_SCRIPT, common_args)
    hard_stop_report = run_json(
        HARD_STOP_REPORT_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
        ],
    )

    packet_payload = activation_packet.get("activation_request_packet", {})
    worksheet_payload = worksheet.get("first_real_execution_worksheet", {})
    hard_stop_payload = hard_stop_report.get("hard_stop_report", {})

    ready = (
        activation_packet.get("packet_status") == "READY_ACTIVATION_REQUEST_PACKET"
        and worksheet.get("worksheet_status") == "READY_FIRST_REAL_EXECUTION_WORKSHEET"
        and hard_stop_report.get("report_status") == "READY_HARD_STOP_REPORT"
    )

    next_action = packet_payload.get("next_action")
    if next_action == "execute_now":
        concise_summary = "All local-only prerequisites are satisfied; execute the six-step runtime path and preserve the pre-certification hard stop."
    elif next_action == "wait_for_runtime_only_values":
        concise_summary = "External evidence is already sufficient; collect only the exact remaining runtime-only values before step 1."
    else:
        concise_summary = "Do not retry internal tooling; wait only for new independently verified external evidence for the parked selected class."

    output = {
        "schema_version": "st1-118-pre-execution-operator-brief-v1",
        "candidate_class_id": activation_packet.get("candidate_class_id"),
        "project_scope": activation_packet.get("project_scope"),
        "brief_status": "READY_PRE_EXECUTION_OPERATOR_BRIEF" if ready else "BLOCKED_PRE_EXECUTION_OPERATOR_BRIEF",
        "pre_execution_operator_brief": {
            "truthful_next_action": next_action,
            "smallest_activation_request": {
                "request_kind": packet_payload.get("request_kind"),
                "requested_items": packet_payload.get("requested_items", []),
            },
            "six_step_execution_mapping": worksheet_payload.get("execution_steps", []),
            "runtime_value_map": worksheet_payload.get("runtime_value_map", []),
            "runtime_values": worksheet_payload.get("runtime_values", []),
            "hard_stop_boundary": packet_payload.get("hard_stop_boundary", {}),
            "hard_stop_report": hard_stop_payload if ready else {},
            "concise_handoff_summary": concise_summary,
            "remaining_checklist_items": packet_payload.get("remaining_checklist_items", {}),
        },
        "blocking_reasons": {
            "packet_status": activation_packet.get("packet_status"),
            "worksheet_status": worksheet.get("worksheet_status"),
            "hard_stop_report_status": hard_stop_report.get("report_status"),
            "next_action": next_action,
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
