#!/usr/bin/env python3
"""Run a single-command rehearsal for the selected-class first real attempt.

This runner is deterministic, local-only, and non-mutating. It executes the
existing reentry gate stack and returns one concise truthful status plus the
immediate next action required for the first real selected-class attempt.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REENTRY_SCRIPT = ROOT / "scripts" / "compile_st1_098_reentry_gate.py"

NEXT_ACTIONS = {
    "PARKED_UNCHANGED_EXTERNAL_DEPENDENCY": "wait_for_new_external_evidence",
    "REOPEN_FOR_EXTERNAL_EVIDENCE_REASSESSMENT": "reassess_new_external_evidence_bundle",
    "WAITING_FOR_RUNTIME_ONLY_FIELDS": "supply_remaining_runtime_only_inputs",
    "READY_FOR_FIRST_RUNTIME_MUTATION": "begin_first_runtime_mutation_under_existing_hard_stops",
}


def run_json(script: Path, args: list[str]) -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-fingerprint", required=True, help="Expected parked external-gate fingerprint")
    parser.add_argument("--bundle", type=Path, required=True, help="Path to ST1-078 bundle JSON")
    parser.add_argument("--native-record", type=Path, required=True, help="Path to ST1-083 native-record JSON")
    parser.add_argument("--operator-inputs", type=Path, required=True, help="Path to ST1-088 operator-input JSON")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to ST1-089 receipt JSON")
    parser.add_argument("--batch", type=Path, required=True, help="Path to ST1-090 batch JSON")
    args = parser.parse_args()

    reentry_gate = run_json(
        REENTRY_SCRIPT,
        [
            "--expected-fingerprint", args.expected_fingerprint,
            "--bundle", str(args.bundle),
            "--native-record", str(args.native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )

    gate_result = reentry_gate["reentry_gate_result"]
    output = {
        "schema_version": "st1-099-first-real-attempt-rehearsal-v1",
        "candidate_class_id": reentry_gate["candidate_class_id"],
        "project_scope": reentry_gate["project_scope"],
        "rehearsal_result": gate_result,
        "readiness_status": reentry_gate["readiness_status"],
        "next_action": NEXT_ACTIONS[gate_result],
        "blocking_reasons": reentry_gate.get("blocking_reasons", []),
        "resume_requirements": reentry_gate.get("resume_requirements", {}),
        "dependency_fingerprint_changed": reentry_gate["dependency_fingerprint_changed"],
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
