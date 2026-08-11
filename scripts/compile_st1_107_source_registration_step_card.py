#!/usr/bin/env python3
"""Compile a source-registration step card for the first write target.

This compiler is deterministic, local-only, and non-mutating. It reduces the
selected-class first-step launch card plus known handoff data to only the
minimal field-level payload and confirmations for `sdas_source_registry`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAUNCH_CARD_SCRIPT = ROOT / "scripts" / "compile_st1_106_first_step_launch_card.py"
HANDOFF_SCRIPT = ROOT / "scripts" / "compile_st1_094_external_evidence_to_dossier_handoff.py"


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

    launch_card = run_json(
        LAUNCH_CARD_SCRIPT,
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
    handoff = run_json(
        HANDOFF_SCRIPT,
        ["--bundle", str(args.submission_bundle), "--native-record", str(args.submission_native_record)],
    )

    launch = launch_card["first_step_launch_card"]
    confirmations = launch["required_confirmations"]
    ready = launch_card["launch_card_status"] == "READY_FIRST_STEP_LAUNCH_CARD"

    payload = {}
    if handoff.get("handoff_status") == "READY_DOSSIER_HANDOFF":
        summary = handoff["verified_external_evidence_summary"]
        payload = {
            "source_id": summary["source_id"],
            "report_class": summary["report_class"],
            "project_scope": launch_card["project_scope"],
            "report_period_value": summary["report_period_value"],
            "resolution_source": summary["resolution_source"],
        }

    output = {
        "schema_version": "st1-107-source-registration-step-card-v1",
        "candidate_class_id": launch_card["candidate_class_id"],
        "project_scope": launch_card["project_scope"],
        "step_card_status": "READY_SOURCE_REGISTRATION_STEP_CARD" if ready else "BLOCKED_SOURCE_REGISTRATION_STEP_CARD",
        "source_registration_step_card": {
            "write_target": "sdas_source_registry",
            "minimal_payload": payload,
            "required_confirmations": confirmations,
            "remaining_checklist_items": launch.get("remaining_checklist_items"),
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
