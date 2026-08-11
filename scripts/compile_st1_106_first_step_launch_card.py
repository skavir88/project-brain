#!/usr/bin/env python3
"""Compile a deterministic first-step launch card.

This compiler is deterministic, local-only, and non-mutating. It reduces the
selected-class mutation-start handoff to only the exact initial write target,
required confirmations, and preserved hard stops needed at the moment a real
run starts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_SCRIPT = ROOT / "scripts" / "compile_st1_105_mutation_start_handoff.py"


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

    handoff = run_json(
        HANDOFF_SCRIPT,
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

    section = handoff["mutation_start_handoff"]
    confirmations = section["before_step_one_confirmations"]
    ready = handoff["handoff_status"] == "READY_MUTATION_START_HANDOFF"
    output = {
        "schema_version": "st1-106-first-step-launch-card-v1",
        "candidate_class_id": handoff["candidate_class_id"],
        "project_scope": handoff["project_scope"],
        "launch_card_status": "READY_FIRST_STEP_LAUNCH_CARD" if ready else "BLOCKED_FIRST_STEP_LAUNCH_CARD",
        "first_step_launch_card": {
            "initial_write_target": "sdas_source_registry",
            "required_confirmations": confirmations,
            "required_operator_inputs": section["mutation_start_payload"].get("required_operator_inputs", []),
            "next_action_transition": section["mutation_start_payload"].get("next_action_transition"),
            "preserved_hard_stops": {
                "hard_stop_count": confirmations.get("hard_stop_count"),
                "hard_stop_report_ready": confirmations.get("hard_stop_report_ready"),
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
