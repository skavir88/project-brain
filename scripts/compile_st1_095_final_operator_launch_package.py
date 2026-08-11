#!/usr/bin/env python3
"""Compile the final non-secret operator launch package for the first real attempt.

This compiler is deterministic, local-only, and non-mutating. It combines the
selected-class execution dossier with the external-evidence handoff surface
into one immediate-use operator package for the first truthful native run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOSSIER_SCRIPT = ROOT / "scripts" / "compile_st1_093_first_real_execution_dossier.py"
HANDOFF_SCRIPT = ROOT / "scripts" / "compile_st1_094_external_evidence_to_dossier_handoff.py"


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

    dossier = run_json(
        DOSSIER_SCRIPT,
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
    handoff = run_json(
        HANDOFF_SCRIPT,
        ["--bundle", str(args.bundle), "--native-record", str(args.native_record)],
    )

    ready = (
        dossier.get("dossier_status") == "READY_FIRST_REAL_EXECUTION_DOSSIER"
        and handoff.get("handoff_status") == "READY_DOSSIER_HANDOFF"
    )

    output = {
        "schema_version": "st1-095-final-operator-launch-package-v1",
        "candidate_class_id": dossier.get("candidate_class_id"),
        "project_scope": dossier.get("project_scope"),
        "launch_package_status": "READY_FINAL_OPERATOR_LAUNCH_PACKAGE" if ready else "BLOCKED_FINAL_OPERATOR_LAUNCH_PACKAGE",
        "runtime_mutation_performed": False,
        "launch_package": {
            "execution_dossier_reference": "st1-093-first-real-execution-dossier-v1",
            "handoff_reference": "st1-094-external-evidence-to-dossier-handoff-v1",
            "ordered_runtime_step_count": dossier.get("dossier_summary", {}).get("ordered_runtime_step_count"),
            "required_operator_inputs": dossier.get("dossier_summary", {}).get("required_operator_inputs"),
            "remaining_runtime_only_fields": handoff.get("dossier_ready_inputs", {}).get("remaining_runtime_only_fields"),
            "hard_stop_count": dossier.get("dossier_summary", {}).get("hard_stop_count"),
            "hard_stop_report_ready": dossier.get("dossier_summary", {}).get("hard_stop_report_ready"),
            "policy_automatic_items_excluded_from_exception_review": dossier.get("dossier_summary", {}).get("policy_automatic_items_excluded_from_exception_review"),
        },
        "blocking_reasons": {
            "dossier_status": dossier.get("dossier_status"),
            "dossier_blocking_reasons": dossier.get("dossier_summary", {}).get("blocking_reasons"),
            "handoff_status": handoff.get("handoff_status"),
            "handoff_blocking_reasons": handoff.get("blocking_reasons"),
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
