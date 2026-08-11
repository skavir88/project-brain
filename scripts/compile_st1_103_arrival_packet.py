#!/usr/bin/env python3
"""Compile an operator-ready arrival packet for future selected-class submissions.

This compiler is deterministic, local-only, and non-mutating. It combines the
selected-class submission delta, change-impact summary, and candidate-submission
checklist into one exact operator-ready payload for the first-real local stack.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DELTA_SCRIPT = ROOT / "scripts" / "compare_st1_100_submission_delta.py"
SUMMARY_SCRIPT = ROOT / "scripts" / "summarize_st1_101_submission_change_impact.py"
CHECKLIST_SCRIPT = ROOT / "scripts" / "compile_st1_102_candidate_submission_checklist.py"


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

    common = [
        "--expected-fingerprint", args.expected_fingerprint,
        "--baseline-bundle", str(args.baseline_bundle),
        "--baseline-native-record", str(args.baseline_native_record),
        "--submission-bundle", str(args.submission_bundle),
        "--submission-native-record", str(args.submission_native_record),
        "--operator-inputs", str(args.operator_inputs),
        "--receipt", str(args.receipt),
        "--batch", str(args.batch),
    ]
    delta = run_json(DELTA_SCRIPT, common)
    summary = run_json(SUMMARY_SCRIPT, common)
    checklist = run_json(CHECKLIST_SCRIPT, common)

    output = {
        "schema_version": "st1-103-selected-class-arrival-packet-v1",
        "candidate_class_id": delta["candidate_class_id"],
        "project_scope": delta["project_scope"],
        "arrival_packet_status": checklist["checklist_result"],
        "operator_ready_payload": {
            "change_impact_result": summary["change_impact_result"],
            "readiness_transition": summary["readiness_transition"],
            "next_action_transition": summary["next_action_transition"],
            "exact_changed_facts": summary["exact_changed_facts"],
            "remaining_checklist_items": checklist["exact_checklist_items"],
        },
        "delta_result": delta["delta_result"],
        "reopen_recommended": delta["reopen_recommended"],
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
