#!/usr/bin/env python3
"""Compile the first-real hard-stop report required by ST1-066 section D.

This compiler is deterministic, local-only, and non-mutating. It emits the
exact non-secret pre-certification report fields immediately after a truthful
`policy_automatic` result and before any certification step.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from validate_st1_078_real_evidence_bundle import (
    CANDIDATE_CLASS_ID,
    PERMITTED_FACTS,
    PROHIBITED_FACTS,
    PROJECT_SCOPE,
)


ROOT = Path(__file__).resolve().parents[1]
PRE_GATE_SCRIPT = ROOT / "scripts" / "verify_st1_088_pre_mutation_gate.py"
RECEIPT_SCRIPT = ROOT / "scripts" / "verify_st1_089_policy_automatic_receipt.py"


def run_json(script: Path, args: list[str]) -> dict[str, object]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def load_json(path: Path | None, label: str) -> tuple[dict[str, object], list[str]]:
    if path is None:
        return {}, [f"{label} not supplied"]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return {}, [f"{label} file not found: {path}"]
    except json.JSONDecodeError as exc:
        return {}, [f"{label} invalid JSON: {exc.msg}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to ST1-078 bundle JSON")
    parser.add_argument("--native-record", type=Path, required=True, help="Path to ST1-083 native-record JSON")
    parser.add_argument("--operator-inputs", type=Path, required=True, help="Path to ST1-088 operator-inputs JSON")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to ST1-089 receipt JSON")
    args = parser.parse_args()

    pre_gate = run_json(
        PRE_GATE_SCRIPT,
        ["--bundle", str(args.bundle), "--native-record", str(args.native_record), "--operator-inputs", str(args.operator_inputs)],
    )
    receipt_gate = run_json(
        RECEIPT_SCRIPT,
        [
            "--bundle",
            str(args.bundle),
            "--native-record",
            str(args.native_record),
            "--operator-inputs",
            str(args.operator_inputs),
            "--receipt",
            str(args.receipt),
        ],
    )
    bundle, bundle_errors = load_json(args.bundle, "bundle")
    native_record, native_errors = load_json(args.native_record, "native_record")
    operator_inputs, operator_errors = load_json(args.operator_inputs, "operator_inputs")
    receipt, receipt_errors = load_json(args.receipt, "receipt")

    loading_errors = bundle_errors + native_errors + operator_errors + receipt_errors
    blocked = loading_errors or pre_gate.get("gate_result") != "GO_FOR_FIRST_RUNTIME_MUTATION" or receipt_gate.get("receipt_result") != "REACHED_POLICY_AUTOMATIC_HARD_STOP"

    if blocked:
        output = {
            "schema_version": "st1-092-first-real-hard-stop-report-v1",
            "candidate_class_id": CANDIDATE_CLASS_ID,
            "project_scope": PROJECT_SCOPE,
            "report_status": "BLOCKED_HARD_STOP_REPORT",
            "blocking_reasons": {
                "loading_errors": loading_errors,
                "pre_mutation_gate_result": pre_gate.get("gate_result"),
                "pre_mutation_reason_codes": pre_gate.get("reason_codes", []),
                "receipt_result": receipt_gate.get("receipt_result"),
                "receipt_reason_codes": receipt_gate.get("reason_codes", []),
            },
            "boundaries": {
                "real_delegation_activated": False,
                "real_source_registered": False,
                "real_file_acquired": False,
                "real_record_ingested": False,
                "real_policy_decision_executed": False,
                "real_certification_performed": False,
            },
        }
        print(json.dumps(output, sort_keys=True, separators=(",", ":")))
        return 0

    source_registration = native_record["source_registration"]
    acquisition = native_record["acquisition"]
    transformation = native_record["transformation"]
    business_time = native_record["business_time"]
    policy_context = native_record["policy_context"]
    fact_payload = operator_inputs["fact_payload"]
    a1_payload = bundle["evidence_items"]["A1"]["payload"]
    a2_payload = bundle["evidence_items"]["A2"]["payload"]
    a3_payload = bundle["evidence_items"]["A3"]["payload"]
    receipt_summary = receipt_gate.get("receipt_summary", {})
    receipt_policy = receipt["policy_decision"]

    output = {
        "schema_version": "st1-092-first-real-hard-stop-report-v1",
        "candidate_class_id": CANDIDATE_CLASS_ID,
        "project_scope": PROJECT_SCOPE,
        "report_status": "READY_HARD_STOP_REPORT",
        "hard_stop_report": {
            "record_data_class": {
                "candidate_class_id": CANDIDATE_CLASS_ID,
                "fact_class": fact_payload["fact_class"],
                "record_id": operator_inputs["record_id"],
            },
            "source_class": {
                "source_id": source_registration["source_id"],
                "source_type": source_registration["source_type"],
                "report_class": source_registration["report_class"],
                "non_sensitive_location_class": source_registration["non_sensitive_location_class"],
            },
            "reporting_business_time": {
                "report_period_value": business_time["report_period_value"],
                "resolution_source": business_time["resolution_source"],
                "observed_at": operator_inputs["observed_at"],
            },
            "native_evidence": {
                "evidence_quality": "native",
                "read_only_acquisition": acquisition["read_only"],
                "original_fingerprint": acquisition["original_fingerprint"],
                "transformation_output_fingerprint": transformation["output_fingerprint"],
                "source_reference": acquisition["source_reference"],
                "acquisition_method": acquisition["acquisition_method"],
            },
            "authority_basis": {
                "governance_role_class": a1_payload["governance_role_class"],
                "authority_basis": a1_payload["authority_basis"],
                "accountable_role_class": a2_payload["accountable_role_class"],
                "controlled_report_owner_role": a3_payload["owning_role_class"],
            },
            "risk_tier": policy_context["risk_tier"],
            "policy": {
                "policy_id": receipt_policy["policy_id"],
                "policy_version": receipt_policy["policy_version"],
                "approval_mode": receipt_policy["approval_mode"],
            },
            "deterministic_decision_reasons": receipt_policy["decision_reasons"],
            "exact_facts_eligible_for_policy_automatic": sorted(PERMITTED_FACTS),
            "exact_facts_excluded_from_policy": sorted(PROHIBITED_FACTS),
            "human_approval_required_before_certification": True,
            "certification_boundary": {
                "certification_executed": receipt_summary.get("certification_executed"),
                "currentness_implied": False,
                "reliance_eligibility_implied": False,
            },
        },
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_file_acquired": False,
            "real_record_ingested": False,
            "real_policy_decision_executed": False,
            "real_certification_performed": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
