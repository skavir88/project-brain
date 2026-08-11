#!/usr/bin/env python3
"""Compile a first-real activation-request packet for the selected-class attempt.

This compiler is deterministic, local-only, and non-mutating. It collapses the
selected-class trigger card, missing-input pack, and execution worksheet into
the smallest truthful request needed to move the first-real path toward
`execute_now`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRIGGER_CARD_SCRIPT = ROOT / "scripts" / "compile_st1_116_execution_trigger_card.py"
MISSING_INPUT_SCRIPT = ROOT / "scripts" / "compile_st1_097_missing_input_pack.py"
WORKSHEET_SCRIPT = ROOT / "scripts" / "compile_st1_115_first_real_execution_worksheet.py"


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
    trigger = run_json(TRIGGER_CARD_SCRIPT, common_step_args)
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
    worksheet = run_json(WORKSHEET_SCRIPT, common_step_args)

    trigger_card = trigger.get("execution_trigger_card", {})
    next_action = trigger_card.get("next_action")
    missing_pack = missing_input_pack.get("missing_input_pack", {})
    worksheet_payload = worksheet.get("first_real_execution_worksheet", {})

    if next_action == "wait_for_external_evidence":
        request_kind = "external_evidence_request"
        requested_items = trigger_card.get("external_evidence_items", [])
    elif next_action == "wait_for_runtime_only_values":
        request_kind = "runtime_only_request"
        requested_items = trigger_card.get("runtime_only_items", [])
    else:
        request_kind = "execute_now_packet"
        requested_items = [
            {"value": item}
            for item in worksheet_payload.get("runtime_values", [])
        ]

    ready = trigger.get("trigger_card_status") == "READY_EXECUTION_TRIGGER_CARD"
    output = {
        "schema_version": "st1-117-activation-request-packet-v1",
        "candidate_class_id": trigger.get("candidate_class_id"),
        "project_scope": trigger.get("project_scope"),
        "packet_status": "READY_ACTIVATION_REQUEST_PACKET" if ready else "BLOCKED_ACTIVATION_REQUEST_PACKET",
        "activation_request_packet": {
            "next_action": next_action,
            "request_kind": request_kind,
            "requested_items": requested_items,
            "hard_stop_boundary": trigger_card.get("hard_stop_boundary", {}),
            "runtime_value_map": worksheet_payload.get("runtime_value_map", []),
            "remaining_checklist_items": {
                "external_evidence_bundle_items": missing_pack.get("exact_missing_inputs", {}).get("external_evidence_requirements", []),
                "runtime_only_items": missing_pack.get("exact_missing_inputs", {}).get("runtime_only_requirements", []),
            },
        },
        "blocking_reasons": {
            "trigger_card_status": trigger.get("trigger_card_status"),
            "next_action": next_action,
            "requested_item_count": len(requested_items),
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
