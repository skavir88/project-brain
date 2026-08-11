#!/usr/bin/env python3
"""Compile a concise selected-class real-run readiness summary.

This compiler is deterministic, local-only, and non-mutating. It classifies
the first real selected-class attempt as one of:

- ready_to_run
- waiting_for_external_evidence
- waiting_for_runtime_only_fields
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_SCRIPT = ROOT / "scripts" / "compile_st1_094_external_evidence_to_dossier_handoff.py"
LAUNCH_SCRIPT = ROOT / "scripts" / "compile_st1_095_final_operator_launch_package.py"


def run_json(script: Path, args: list[str]) -> dict[str, object]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def classify_status(handoff: dict[str, object], launch: dict[str, object]) -> tuple[str, list[str]]:
    handoff_status = handoff.get("handoff_status")
    launch_status = launch.get("launch_package_status")
    launch_blockers = launch.get("blocking_reasons", {})
    dossier_blockers = launch_blockers.get("dossier_blocking_reasons", {}) if isinstance(launch_blockers, dict) else {}

    if handoff_status != "READY_DOSSIER_HANDOFF":
        reasons = []
        if isinstance(handoff.get("blocking_reasons"), dict):
            reasons.extend(handoff["blocking_reasons"].get("native_record_errors", []))
            reasons.extend(handoff["blocking_reasons"].get("bundle_errors", []))
        return "waiting_for_external_evidence", reasons

    if launch_status == "READY_FINAL_OPERATOR_LAUNCH_PACKAGE":
        return "ready_to_run", []

    reasons: list[str] = []
    if isinstance(dossier_blockers, dict):
        reasons.extend(dossier_blockers.get("pre_mutation_reason_codes", []))
        reasons.extend(dossier_blockers.get("receipt_reason_codes", []))
    return "waiting_for_runtime_only_fields", reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to ST1-078 bundle JSON")
    parser.add_argument("--native-record", type=Path, required=True, help="Path to ST1-083 native-record JSON")
    parser.add_argument("--operator-inputs", type=Path, required=True, help="Path to ST1-088 operator-input JSON")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to ST1-089 receipt JSON")
    parser.add_argument("--batch", type=Path, required=True, help="Path to ST1-090 batch JSON")
    args = parser.parse_args()

    handoff = run_json(HANDOFF_SCRIPT, ["--bundle", str(args.bundle), "--native-record", str(args.native_record)])
    launch = run_json(
        LAUNCH_SCRIPT,
        [
            "--bundle",
            str(args.bundle),
            "--native-record",
            str(args.native_record),
            "--operator-inputs",
            str(args.operator_inputs),
            "--receipt",
            str(args.receipt),
            "--batch",
            str(args.batch),
        ],
    )

    readiness_status, reasons = classify_status(handoff, launch)
    remaining_runtime_only_fields = []
    if handoff.get("handoff_status") == "READY_DOSSIER_HANDOFF":
        remaining_runtime_only_fields = handoff.get("dossier_ready_inputs", {}).get("remaining_runtime_only_fields", [])

    output = {
        "schema_version": "st1-096-real-run-readiness-summary-v1",
        "candidate_class_id": handoff.get("candidate_class_id"),
        "project_scope": handoff.get("project_scope"),
        "readiness_status": readiness_status,
        "blocking_reasons": reasons,
        "remaining_runtime_only_fields": remaining_runtime_only_fields,
        "launch_package_status": launch.get("launch_package_status"),
        "handoff_status": handoff.get("handoff_status"),
        "hard_stop_count": launch.get("launch_package", {}).get("hard_stop_count"),
        "hard_stop_report_ready": launch.get("launch_package", {}).get("hard_stop_report_ready"),
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_file_acquired": False,
            "real_record_ingested": False,
            "real_policy_decision_executed": False,
            "real_certification_performed": False,
            "trust_boundary_changed": False
        }
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
