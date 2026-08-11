#!/usr/bin/env python3
"""Verify the first real-attempt post-mutation receipt and certification hard stop.

This verifier is local-only and non-mutating. It evaluates whether a future
runtime receipt truthfully proves that the first selected-class record reached
`policy_automatic` under the exact approved scope and then stopped before
certification.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from validate_st1_078_real_evidence_bundle import CANDIDATE_CLASS_ID, PERMITTED_FACTS, PROJECT_SCOPE


ROOT = Path(__file__).resolve().parents[1]
PRE_MUTATION_GATE_SCRIPT = ROOT / "scripts" / "verify_st1_088_pre_mutation_gate.py"
HEX_64 = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_TARGETS = [
    "ingestion.sdas_source_registry",
    "ingestion.sdas_source_control_verifications",
    "ingestion.sdas_acquisition_events",
    "ingestion.sdas_transformations",
    "POST /v1/records -> ingestion.credibility_records",
    "ingestion.sdas_policy_decisions",
]


def run_pre_mutation_gate(bundle: Path, native_record: Path | None, operator_inputs: Path | None) -> dict[str, object]:
    command = [sys.executable, str(PRE_MUTATION_GATE_SCRIPT), "--bundle", str(bundle)]
    if native_record is not None:
        command.extend(["--native-record", str(native_record)])
    if operator_inputs is not None:
        command.extend(["--operator-inputs", str(operator_inputs)])
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and HEX_64.fullmatch(value) is not None


def load_json(path: Path | None, missing_label: str) -> tuple[dict[str, object], list[str]]:
    if path is None:
        return {}, [f"{missing_label} not supplied"]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return {}, [f"{missing_label} file not found: {path}"]
    except json.JSONDecodeError as exc:
        return {}, [f"{missing_label} invalid JSON: {exc.msg}"]


def require_nonempty_str(errors: list[str], obj: dict[str, object], key: str, context: str) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}.{key} must be a non-empty string")
        return None
    return value.strip()


def require_bool(errors: list[str], obj: dict[str, object], key: str, expected: bool, context: str) -> None:
    if obj.get(key) is not expected:
        errors.append(f"{context}.{key} must be {str(expected).lower()}")


def validate_receipt(path: Path | None) -> tuple[str, list[str], dict[str, object]]:
    receipt, load_errors = load_json(path, "receipt")
    if load_errors:
        return "BLOCKED_RECEIPT_MISSING", load_errors, {}

    errors: list[str] = []
    required_sections = {
        "candidate_class_id",
        "project_scope",
        "receipt_version",
        "record_id",
        "source_id",
        "report_period_value",
        "fact_class",
        "executed_steps",
        "policy_decision",
        "certification_boundary",
    }
    missing = sorted(required_sections - set(receipt))
    if missing:
        errors.append(f"receipt missing required sections: {', '.join(missing)}")

    if receipt.get("candidate_class_id") != CANDIDATE_CLASS_ID:
        errors.append("receipt.candidate_class_id mismatch")
    if receipt.get("project_scope") != PROJECT_SCOPE:
        errors.append("receipt.project_scope mismatch")
    if receipt.get("receipt_version") != "st1-089/v1":
        errors.append("receipt.receipt_version must be st1-089/v1")

    require_nonempty_str(errors, receipt, "record_id", "receipt")
    require_nonempty_str(errors, receipt, "source_id", "receipt")
    report_period_value = require_nonempty_str(errors, receipt, "report_period_value", "receipt")
    fact_class = require_nonempty_str(errors, receipt, "fact_class", "receipt")
    if fact_class is not None and fact_class not in PERMITTED_FACTS:
        errors.append("receipt.fact_class must remain inside the approved low-risk fact classes")

    executed_steps = receipt.get("executed_steps")
    if not isinstance(executed_steps, list):
        errors.append("receipt.executed_steps must be a list")
        executed_steps = []
    if len(executed_steps) != len(EXPECTED_TARGETS):
        errors.append("receipt.executed_steps must contain exactly six runtime write receipts")
    for index, expected_target in enumerate(EXPECTED_TARGETS, start=1):
        if index - 1 >= len(executed_steps):
            break
        step = executed_steps[index - 1]
        context = f"receipt.executed_steps[{index - 1}]"
        if not isinstance(step, dict):
            errors.append(f"{context} must be an object")
            continue
        if step.get("sequence") != index:
            errors.append(f"{context}.sequence must be {index}")
        if step.get("target") != expected_target:
            errors.append(f"{context}.target must be {expected_target}")
        require_bool(errors, step, "persisted", True, context)
        require_nonempty_str(errors, step, "receipt_reference", context)

    policy_decision = receipt.get("policy_decision")
    if not isinstance(policy_decision, dict):
        errors.append("receipt.policy_decision must be an object")
        policy_decision = {}
    if policy_decision.get("policy_id") != "project-controls-progress-low-risk":
        errors.append("receipt.policy_decision.policy_id must be project-controls-progress-low-risk")
    require_nonempty_str(errors, policy_decision, "policy_version", "receipt.policy_decision")
    if policy_decision.get("approval_mode") != "policy_automatic":
        errors.append("receipt.policy_decision.approval_mode must be policy_automatic")
    if policy_decision.get("decision_actor") != "sahra_policy_engine":
        errors.append("receipt.policy_decision.decision_actor must be sahra_policy_engine")
    if policy_decision.get("risk_tier") != "LOW":
        errors.append("receipt.policy_decision.risk_tier must be LOW")
    decision_reasons = policy_decision.get("decision_reasons")
    if not isinstance(decision_reasons, list) or not decision_reasons:
        errors.append("receipt.policy_decision.decision_reasons must be a non-empty list")
    decision_hash = policy_decision.get("decision_hash")
    if not is_sha256(decision_hash):
        errors.append("receipt.policy_decision.decision_hash must be a lowercase sha256 hex string")

    certification_boundary = receipt.get("certification_boundary")
    if not isinstance(certification_boundary, dict):
        errors.append("receipt.certification_boundary must be an object")
        certification_boundary = {}
    require_bool(errors, certification_boundary, "certification_executed", False, "receipt.certification_boundary")
    require_bool(errors, certification_boundary, "human_approval_executed", False, "receipt.certification_boundary")
    require_bool(errors, certification_boundary, "currentness_asserted", False, "receipt.certification_boundary")
    require_bool(errors, certification_boundary, "reliance_asserted", False, "receipt.certification_boundary")
    require_nonempty_str(errors, certification_boundary, "hard_stop_state", "receipt.certification_boundary")
    if certification_boundary.get("hard_stop_state") != "STOPPED_BEFORE_CERTIFICATION":
        errors.append("receipt.certification_boundary.hard_stop_state must be STOPPED_BEFORE_CERTIFICATION")

    if errors:
        if any("approval_mode" in item or "decision_hash" in item or "decision_reasons" in item for item in errors):
            return "BLOCKED_POLICY_RECEIPT_INVALID", errors, receipt
        if any("certification_boundary" in item for item in errors):
            return "BLOCKED_CERTIFICATION_HARD_STOP_BREACHED", errors, receipt
        return "BLOCKED_RECEIPT_INVALID", errors, receipt

    return "READY_POLICY_AUTOMATIC_HARD_STOP", [], receipt


def summarize_reason_codes(pre_gate_result: str, receipt_status: str, receipt_errors: list[str]) -> list[str]:
    reason_codes: list[str] = []
    if pre_gate_result != "GO_FOR_FIRST_RUNTIME_MUTATION":
        reason_codes.append("pre_mutation_gate_not_ready")
    if receipt_status == "BLOCKED_RECEIPT_MISSING":
        reason_codes.append("receipt_missing")
    elif receipt_status == "BLOCKED_RECEIPT_INVALID":
        reason_codes.append("receipt_invalid")
    elif receipt_status == "BLOCKED_POLICY_RECEIPT_INVALID":
        reason_codes.append("policy_receipt_invalid")
    elif receipt_status == "BLOCKED_CERTIFICATION_HARD_STOP_BREACHED":
        reason_codes.append("certification_hard_stop_breached")
    if any("fact_class" in item for item in receipt_errors):
        reason_codes.append("fact_class_out_of_scope")
    if any("report_period_value" in item for item in receipt_errors):
        reason_codes.append("business_time_missing_or_invalid")
    return sorted(set(reason_codes))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the ST1-078 bundle JSON file")
    parser.add_argument("--native-record", type=Path, help="Path to the ST1-083 native-record JSON file")
    parser.add_argument("--operator-inputs", type=Path, help="Path to the ST1-088 operator-input JSON file")
    parser.add_argument("--receipt", type=Path, help="Path to the ST1-089 runtime-receipt JSON file")
    args = parser.parse_args()

    pre_gate = run_pre_mutation_gate(args.bundle, args.native_record, args.operator_inputs)
    receipt_status, receipt_errors, receipt = validate_receipt(args.receipt)

    ready = pre_gate.get("gate_result") == "GO_FOR_FIRST_RUNTIME_MUTATION" and receipt_status == "READY_POLICY_AUTOMATIC_HARD_STOP"
    reason_codes = summarize_reason_codes(str(pre_gate.get("gate_result")), receipt_status, receipt_errors)

    output = {
        "schema_version": "st1-089-policy-automatic-receipt-v1",
        "candidate_class_id": CANDIDATE_CLASS_ID,
        "project_scope": PROJECT_SCOPE,
        "receipt_result": "REACHED_POLICY_AUTOMATIC_HARD_STOP" if ready else "NO_GO_POLICY_AUTOMATIC_RECEIPT",
        "pre_mutation_gate_result": pre_gate.get("gate_result"),
        "receipt_status": receipt_status,
        "reason_codes": reason_codes,
        "receipt_summary": {
            "record_id": receipt.get("record_id") if receipt else None,
            "source_id": receipt.get("source_id") if receipt else None,
            "report_period_value": receipt.get("report_period_value") if receipt else None,
            "fact_class": receipt.get("fact_class") if receipt else None,
            "policy_id": receipt.get("policy_decision", {}).get("policy_id") if receipt else None,
            "approval_mode": receipt.get("policy_decision", {}).get("approval_mode") if receipt else None,
            "certification_executed": receipt.get("certification_boundary", {}).get("certification_executed") if receipt else None,
            "errors": receipt_errors,
        },
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_file_acquired": False,
            "real_record_ingested": False,
            "real_policy_decision_executed": False,
            "real_certification_performed": False
        }
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
