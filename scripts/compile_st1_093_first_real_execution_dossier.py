#!/usr/bin/env python3
"""Compile a deterministic non-secret first-real execution dossier.

This dossier is the operator-facing aggregation layer for the first real
selected-class attempt. It packages the existing execution sequence, gates,
receipt contract, hard-stop report contract, and exception-handling surface
into one concise non-mutating artifact set.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KIT_SCRIPT = ROOT / "scripts" / "compile_st1_087_first_real_attempt_kit.py"
PRE_GATE_SCRIPT = ROOT / "scripts" / "verify_st1_088_pre_mutation_gate.py"
RECEIPT_SCRIPT = ROOT / "scripts" / "verify_st1_089_policy_automatic_receipt.py"
REPORT_SCRIPT = ROOT / "scripts" / "compile_st1_092_first_real_hard_stop_report.py"
EXCEPTION_SCRIPT = ROOT / "scripts" / "generate_st1_091_selected_class_exception_queue.py"


def run_json(script: Path, args: list[str]) -> dict[str, object]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to ST1-078 bundle JSON")
    parser.add_argument("--native-record", type=Path, required=True, help="Path to ST1-083 native-record JSON")
    parser.add_argument("--operator-inputs", type=Path, required=True, help="Path to ST1-088 operator-input JSON")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to ST1-089 receipt JSON")
    parser.add_argument("--batch", type=Path, required=True, help="Path to ST1-090 batch JSON")
    args = parser.parse_args()

    kit = run_json(KIT_SCRIPT, ["--bundle", str(args.bundle), "--native-record", str(args.native_record)])
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
    hard_stop_report = run_json(
        REPORT_SCRIPT,
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
    exception_queue = run_json(EXCEPTION_SCRIPT, ["--batch", str(args.batch)])

    ready = (
        kit.get("kit_status") == "READY_OPERATOR_KIT"
        and pre_gate.get("gate_result") == "GO_FOR_FIRST_RUNTIME_MUTATION"
        and receipt_gate.get("receipt_result") == "REACHED_POLICY_AUTOMATIC_HARD_STOP"
        and hard_stop_report.get("report_status") == "READY_HARD_STOP_REPORT"
    )

    output = {
        "schema_version": "st1-093-first-real-execution-dossier-v1",
        "candidate_class_id": kit.get("candidate_class_id"),
        "project_scope": kit.get("project_scope"),
        "dossier_status": "READY_FIRST_REAL_EXECUTION_DOSSIER" if ready else "BLOCKED_FIRST_REAL_EXECUTION_DOSSIER",
        "runtime_mutation_performed": False,
        "sections": {
            "operator_kit": kit,
            "pre_mutation_gate": pre_gate,
            "post_mutation_receipt": receipt_gate,
            "hard_stop_report": hard_stop_report,
            "exception_queue": exception_queue,
        },
        "dossier_summary": {
            "ordered_runtime_step_count": kit.get("kit_summary", {}).get("ordered_runtime_step_count"),
            "required_operator_inputs": kit.get("kit_summary", {}).get("required_operator_inputs"),
            "hard_stop_count": len(kit.get("kit_summary", {}).get("hard_stops", [])),
            "hard_stop_report_ready": hard_stop_report.get("report_status") == "READY_HARD_STOP_REPORT",
            "policy_automatic_items_excluded_from_exception_review": exception_queue.get("exception_summary", {}).get("policy_automatic_items_excluded_from_review_output"),
            "blocking_reasons": {
                "kit_status": kit.get("kit_status"),
                "pre_mutation_gate_result": pre_gate.get("gate_result"),
                "pre_mutation_reason_codes": pre_gate.get("reason_codes", []),
                "receipt_result": receipt_gate.get("receipt_result"),
                "receipt_reason_codes": receipt_gate.get("reason_codes", []),
                "hard_stop_report_status": hard_stop_report.get("report_status"),
            },
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
