#!/usr/bin/env python3
"""Verify first-real execution conformance against the approved ST1-118 brief.

This verifier is deterministic, local-only, and non-mutating. It proves
whether a future selected-class runtime receipt and observed six-step write
sequence conform exactly to the approved pre-execution operator brief while
preserving the stop-before-certification boundary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_SCRIPT = ROOT / "scripts" / "verify_st1_089_policy_automatic_receipt.py"


def run_json_command(args: list[str]) -> dict[str, Any]:
    import subprocess
    import sys

    result = subprocess.run([sys.executable, *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"{label} file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{label} invalid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"{label} must be a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-brief", type=Path, required=True, help="Path to the approved ST1-118 brief JSON")
    parser.add_argument("--submission-bundle", type=Path, required=True, help="Submitted ST1-078 bundle JSON used for receipt validation")
    parser.add_argument("--submission-native-record", type=Path, required=True, help="Submitted native-record JSON used for receipt validation")
    parser.add_argument("--operator-inputs", type=Path, required=True, help="Path to ST1-088 operator-input JSON used for receipt validation")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to ST1-089 receipt JSON")
    args = parser.parse_args()

    brief = load_json(args.approved_brief, "approved_brief")
    receipt = run_json_command(
        [
            str(RECEIPT_SCRIPT),
            "--bundle",
            str(args.submission_bundle),
            "--native-record",
            str(args.submission_native_record),
            "--operator-inputs",
            str(args.operator_inputs),
            "--receipt",
            str(args.receipt),
        ],
    )

    brief_payload = brief.get("pre_execution_operator_brief", {})
    hard_stop_boundary = brief_payload.get("hard_stop_boundary", {})
    expected_steps = brief_payload.get("six_step_execution_mapping", [])
    receipt_summary = receipt.get("receipt_summary", {})

    conformance_errors: list[str] = []

    if brief.get("brief_status") != "READY_PRE_EXECUTION_OPERATOR_BRIEF":
        conformance_errors.append("approved_brief_not_ready")
    if brief_payload.get("truthful_next_action") != "execute_now":
        conformance_errors.append("brief_next_action_not_execute_now")
    if receipt.get("receipt_result") != "REACHED_POLICY_AUTOMATIC_HARD_STOP":
        conformance_errors.append("receipt_not_at_policy_automatic_hard_stop")

    if receipt_summary.get("record_id") != hard_stop_boundary.get("record_data_class", {}).get("record_id"):
        conformance_errors.append("record_id_mismatch")
    if receipt_summary.get("source_id") != hard_stop_boundary.get("source_class", {}).get("source_id"):
        conformance_errors.append("source_id_mismatch")
    if receipt_summary.get("report_period_value") != hard_stop_boundary.get("reporting_business_time", {}).get("report_period_value"):
        conformance_errors.append("report_period_value_mismatch")
    if receipt_summary.get("fact_class") != hard_stop_boundary.get("record_data_class", {}).get("fact_class"):
        conformance_errors.append("fact_class_mismatch")
    if receipt_summary.get("policy_id") != hard_stop_boundary.get("policy", {}).get("policy_id"):
        conformance_errors.append("policy_id_mismatch")
    if receipt_summary.get("approval_mode") != hard_stop_boundary.get("policy", {}).get("approval_mode"):
        conformance_errors.append("approval_mode_mismatch")
    if receipt_summary.get("certification_executed") is not False:
        conformance_errors.append("certification_boundary_breached")

    receipt_file = load_json(args.receipt, "receipt")
    receipt_steps = receipt_file.get("executed_steps", []) if isinstance(receipt_file, dict) else []
    if len(expected_steps) != len(receipt_steps):
        conformance_errors.append("executed_step_count_mismatch")
    else:
        for expected, observed in zip(expected_steps, receipt_steps):
            if expected.get("sequence") != observed.get("sequence"):
                conformance_errors.append(f"step_{expected.get('sequence')}_sequence_mismatch")
            if expected.get("target") != observed.get("target"):
                conformance_errors.append(f"step_{expected.get('sequence')}_target_mismatch")
            if observed.get("persisted") is not True:
                conformance_errors.append(f"step_{expected.get('sequence')}_not_persisted")

    result = "EXECUTION_CONFORMS_TO_APPROVED_BRIEF" if not conformance_errors else "EXECUTION_DOES_NOT_CONFORM"
    reason_codes = sorted(set(conformance_errors + (receipt.get("reason_codes") or [])))

    output = {
        "schema_version": "st1-119-execution-conformance-v1",
        "candidate_class_id": brief.get("candidate_class_id"),
        "project_scope": brief.get("project_scope"),
        "conformance_result": result,
        "approved_brief_status": brief.get("brief_status"),
        "receipt_result": receipt.get("receipt_result"),
        "reason_codes": reason_codes,
        "conformance_summary": {
            "truthful_next_action": brief_payload.get("truthful_next_action"),
            "expected_execution_step_count": len(expected_steps),
            "observed_execution_step_count": len(receipt_steps),
            "requested_item_count": len(brief_payload.get("smallest_activation_request", {}).get("requested_items", [])),
            "runtime_value_count": len(brief_payload.get("runtime_values", [])),
            "human_approval_required_before_certification": hard_stop_boundary.get("human_approval_required_before_certification"),
            "certification_executed": receipt_summary.get("certification_executed"),
            "record_id": receipt_summary.get("record_id"),
            "source_id": receipt_summary.get("source_id"),
            "report_period_value": receipt_summary.get("report_period_value"),
            "fact_class": receipt_summary.get("fact_class"),
            "policy_id": receipt_summary.get("policy_id"),
            "approval_mode": receipt_summary.get("approval_mode"),
            "errors": conformance_errors,
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
