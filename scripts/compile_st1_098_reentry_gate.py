#!/usr/bin/env python3
"""Compile a deterministic reentry gate for the first real selected-class attempt.

This compiler is local-only and non-mutating. It combines:
- the parked external-gate fingerprint;
- the ST1-097 missing-input pack; and
- the selected-class readiness summary

to decide whether the first real path should stay parked, reopen for external
evidence reassessment, wait only on runtime inputs, or is ready for the first
runtime mutation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FINGERPRINT_SCRIPT = ROOT / "scripts" / "fingerprint_st1_078_external_gate.py"
MISSING_INPUT_PACK_SCRIPT = ROOT / "scripts" / "compile_st1_097_missing_input_pack.py"


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

    fingerprint = run_json(FINGERPRINT_SCRIPT, [])
    missing_input_pack = run_json(
        MISSING_INPUT_PACK_SCRIPT,
        [
            "--bundle", str(args.bundle),
            "--native-record", str(args.native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )

    current_fingerprint = fingerprint["dependency_fingerprint"]
    readiness_status = missing_input_pack["readiness_status"]
    fingerprint_changed = current_fingerprint != args.expected_fingerprint

    if readiness_status == "waiting_for_external_evidence":
        gate_result = (
            "REOPEN_FOR_EXTERNAL_EVIDENCE_REASSESSMENT"
            if fingerprint_changed
            else "PARKED_UNCHANGED_EXTERNAL_DEPENDENCY"
        )
    elif readiness_status == "waiting_for_runtime_only_fields":
        gate_result = "WAITING_FOR_RUNTIME_ONLY_FIELDS"
    else:
        gate_result = "READY_FOR_FIRST_RUNTIME_MUTATION"

    output = {
        "schema_version": "st1-098-first-real-reentry-gate-v1",
        "candidate_class_id": missing_input_pack.get("candidate_class_id"),
        "project_scope": missing_input_pack.get("project_scope"),
        "expected_dependency_fingerprint": args.expected_fingerprint,
        "current_dependency_fingerprint": current_fingerprint,
        "dependency_fingerprint_changed": fingerprint_changed,
        "readiness_status": readiness_status,
        "reentry_gate_result": gate_result,
        "resume_requirements": missing_input_pack.get("missing_input_pack", {}).get("exact_missing_inputs", {}),
        "blocking_reasons": missing_input_pack.get("missing_input_pack", {}).get("blocking_reasons", []),
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
