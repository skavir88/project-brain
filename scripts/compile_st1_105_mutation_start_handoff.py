#!/usr/bin/env python3
"""Compile a first-real mutation-start handoff.

This compiler is deterministic, local-only, and non-mutating. It reduces the
selected-class pre-mutation execution envelope to only the exact mutation-start
payload and before-step-one confirmations needed immediately before step 1.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ENVELOPE_SCRIPT = ROOT / "scripts" / "compile_st1_104_pre_mutation_execution_envelope.py"


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

    envelope = run_json(
        ENVELOPE_SCRIPT,
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

    section = envelope["pre_mutation_execution_envelope"]
    ready = envelope["execution_envelope_status"] == "READY_PRE_MUTATION_EXECUTION_ENVELOPE"
    output = {
        "schema_version": "st1-105-mutation-start-handoff-v1",
        "candidate_class_id": envelope["candidate_class_id"],
        "project_scope": envelope["project_scope"],
        "handoff_status": "READY_MUTATION_START_HANDOFF" if ready else "BLOCKED_MUTATION_START_HANDOFF",
        "mutation_start_handoff": {
            "mutation_start_payload": {
                "ordered_runtime_step_count": section.get("ordered_runtime_step_count"),
                "required_operator_inputs": section.get("required_operator_inputs"),
                "next_action_transition": section.get("next_action_transition"),
            },
            "before_step_one_confirmations": {
                "arrival_packet_ready": section.get("arrival_packet_status") == "READY_CHECKLIST",
                "execution_dossier_ready": section.get("dossier_status") == "READY_FIRST_REAL_EXECUTION_DOSSIER",
                "launch_package_ready": section.get("launch_package_status") == "READY_FINAL_OPERATOR_LAUNCH_PACKAGE",
                "hard_stop_report_ready": section.get("hard_stop_report_ready") is True,
                "hard_stop_count": section.get("hard_stop_count"),
            },
            "remaining_checklist_items": section.get("remaining_checklist_items"),
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
