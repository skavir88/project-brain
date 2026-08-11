#!/usr/bin/env python3
"""Compile a transformation step card for the fourth write target.

This compiler is deterministic, local-only, and non-mutating. It reduces the
selected-class acquisition surface plus existing execution manifest data to
only the minimal field-level payload and confirmations for
`sdas_transformations`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACQUISITION_STEP_SCRIPT = ROOT / "scripts" / "compile_st1_109_acquisition_step_card.py"
MANIFEST_SCRIPT = ROOT / "scripts" / "compile_st1_085_first_real_attempt_manifest.py"


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

    acquisition_step = run_json(
        ACQUISITION_STEP_SCRIPT,
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
    manifest = run_json(
        MANIFEST_SCRIPT,
        ["--bundle", str(args.submission_bundle), "--native-record", str(args.submission_native_record)],
    )

    acquisition = acquisition_step["acquisition_step_card"]
    acquisition_confirmations = acquisition["required_confirmations"]
    acquisition_ready = acquisition_step["step_card_status"] == "READY_ACQUISITION_STEP_CARD"
    manifest_ready = manifest.get("compiler_result") == "READY_EXECUTION_MANIFEST"
    ready = acquisition_ready and manifest_ready

    payload: dict[str, Any] = {}
    if manifest_ready:
        for row in manifest.get("execution_manifest", []):
            if row.get("target") == "ingestion.sdas_transformations":
                payload = row.get("payload_shape", {})
                break

    output = {
        "schema_version": "st1-110-transformation-step-card-v1",
        "candidate_class_id": acquisition_step["candidate_class_id"],
        "project_scope": acquisition_step["project_scope"],
        "step_card_status": "READY_TRANSFORMATION_STEP_CARD" if ready else "BLOCKED_TRANSFORMATION_STEP_CARD",
        "transformation_step_card": {
            "write_target": "sdas_transformations",
            "minimal_payload": payload if ready else {},
            "required_confirmations": {
                "acquisition_step_card_ready": acquisition_ready,
                **acquisition_confirmations,
            },
            "remaining_checklist_items": acquisition.get("remaining_checklist_items"),
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
