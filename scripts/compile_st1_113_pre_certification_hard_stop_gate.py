#!/usr/bin/env python3
"""Compile the final pre-certification hard-stop gate package.

This compiler is deterministic, local-only, and non-mutating. It assembles the
six selected-class runtime-write step cards together with the preserved
stop-before-certification semantics into the smallest truthful operator handoff
immediately before the first real `policy_automatic` attempt.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STEP_1_SCRIPT = ROOT / "scripts" / "compile_st1_107_source_registration_step_card.py"
STEP_2_SCRIPT = ROOT / "scripts" / "compile_st1_108_source_control_verification_step_card.py"
STEP_3_SCRIPT = ROOT / "scripts" / "compile_st1_109_acquisition_step_card.py"
STEP_4_SCRIPT = ROOT / "scripts" / "compile_st1_110_transformation_step_card.py"
STEP_5_SCRIPT = ROOT / "scripts" / "compile_st1_111_record_intake_step_card.py"
STEP_6_SCRIPT = ROOT / "scripts" / "compile_st1_112_policy_decision_step_card.py"
HARD_STOP_REPORT_SCRIPT = ROOT / "scripts" / "compile_st1_092_first_real_hard_stop_report.py"
LAUNCH_PACKAGE_SCRIPT = ROOT / "scripts" / "compile_st1_095_final_operator_launch_package.py"


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
    source_registration = run_json(STEP_1_SCRIPT, common_step_args)
    source_control = run_json(STEP_2_SCRIPT, common_step_args)
    acquisition = run_json(STEP_3_SCRIPT, common_step_args)
    transformation = run_json(STEP_4_SCRIPT, common_step_args)
    record_intake = run_json(STEP_5_SCRIPT, common_step_args)
    policy_decision = run_json(STEP_6_SCRIPT, common_step_args)

    hard_stop_report = run_json(
        HARD_STOP_REPORT_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
        ],
    )
    launch_package = run_json(
        LAUNCH_PACKAGE_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )

    ready = (
        source_registration.get("step_card_status") == "READY_SOURCE_REGISTRATION_STEP_CARD"
        and source_control.get("step_card_status") == "READY_SOURCE_CONTROL_VERIFICATION_STEP_CARD"
        and acquisition.get("step_card_status") == "READY_ACQUISITION_STEP_CARD"
        and transformation.get("step_card_status") == "READY_TRANSFORMATION_STEP_CARD"
        and record_intake.get("step_card_status") == "READY_RECORD_INTAKE_STEP_CARD"
        and policy_decision.get("step_card_status") == "READY_POLICY_DECISION_STEP_CARD"
        and hard_stop_report.get("report_status") == "READY_HARD_STOP_REPORT"
        and launch_package.get("launch_package_status") == "READY_FINAL_OPERATOR_LAUNCH_PACKAGE"
    )

    step_cards = [
        {
            "sequence": 1,
            "status": source_registration["step_card_status"],
            "write_target": source_registration["source_registration_step_card"]["write_target"],
            "minimal_payload": source_registration["source_registration_step_card"]["minimal_payload"],
        },
        {
            "sequence": 2,
            "status": source_control["step_card_status"],
            "write_target": source_control["source_control_verification_step_card"]["write_target"],
            "minimal_payload": source_control["source_control_verification_step_card"]["minimal_payload"],
        },
        {
            "sequence": 3,
            "status": acquisition["step_card_status"],
            "write_target": acquisition["acquisition_step_card"]["write_target"],
            "minimal_payload": acquisition["acquisition_step_card"]["minimal_payload"],
        },
        {
            "sequence": 4,
            "status": transformation["step_card_status"],
            "write_target": transformation["transformation_step_card"]["write_target"],
            "minimal_payload": transformation["transformation_step_card"]["minimal_payload"],
        },
        {
            "sequence": 5,
            "status": record_intake["step_card_status"],
            "write_target": record_intake["record_intake_step_card"]["write_target"],
            "minimal_payload": record_intake["record_intake_step_card"]["minimal_payload"],
        },
        {
            "sequence": 6,
            "status": policy_decision["step_card_status"],
            "write_target": policy_decision["policy_decision_step_card"]["write_target"],
            "minimal_payload": policy_decision["policy_decision_step_card"]["minimal_payload"],
        },
    ]

    shared_required_confirmations = policy_decision["policy_decision_step_card"]["required_confirmations"]
    remaining_checklist_items = policy_decision["policy_decision_step_card"]["remaining_checklist_items"]
    blocking_reasons = {
        "step_card_statuses": {f"step_{card['sequence']}": card["status"] for card in step_cards},
        "launch_package_status": launch_package.get("launch_package_status"),
        "hard_stop_report_status": hard_stop_report.get("report_status"),
        "remaining_checklist_items": remaining_checklist_items,
    }

    gate_package: dict[str, Any] = {
        "schema_version": "st1-113-pre-certification-hard-stop-gate-v1",
        "candidate_class_id": policy_decision["candidate_class_id"],
        "project_scope": policy_decision["project_scope"],
        "gate_package_status": "READY_PRE_CERTIFICATION_HARD_STOP_GATE" if ready else "BLOCKED_PRE_CERTIFICATION_HARD_STOP_GATE",
        "pre_certification_hard_stop_gate": {
            "step_cards": step_cards,
            "required_confirmations": shared_required_confirmations,
            "remaining_checklist_items": remaining_checklist_items,
            "launch_package_summary": launch_package.get("launch_package", {}),
            "hard_stop_boundary": {
                "report_status": hard_stop_report.get("report_status"),
                "human_approval_required_before_certification": hard_stop_report.get("hard_stop_report", {}).get("human_approval_required_before_certification"),
                "certification_boundary": hard_stop_report.get("hard_stop_report", {}).get("certification_boundary"),
                "policy": hard_stop_report.get("hard_stop_report", {}).get("policy"),
                "record_data_class": hard_stop_report.get("hard_stop_report", {}).get("record_data_class"),
                "source_class": hard_stop_report.get("hard_stop_report", {}).get("source_class"),
                "reporting_business_time": hard_stop_report.get("hard_stop_report", {}).get("reporting_business_time"),
                "native_evidence": hard_stop_report.get("hard_stop_report", {}).get("native_evidence"),
                "authority_basis": hard_stop_report.get("hard_stop_report", {}).get("authority_basis"),
                "risk_tier": hard_stop_report.get("hard_stop_report", {}).get("risk_tier"),
                "deterministic_decision_reasons": hard_stop_report.get("hard_stop_report", {}).get("deterministic_decision_reasons"),
                "exact_facts_eligible_for_policy_automatic": hard_stop_report.get("hard_stop_report", {}).get("exact_facts_eligible_for_policy_automatic"),
                "exact_facts_excluded_from_policy": hard_stop_report.get("hard_stop_report", {}).get("exact_facts_excluded_from_policy"),
            },
        },
        "blocking_reasons": blocking_reasons,
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
    print(json.dumps(gate_package, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
