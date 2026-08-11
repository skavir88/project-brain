#!/usr/bin/env python3
"""Compile a candidate-submission checklist for future selected-class arrivals.

This compiler is deterministic, local-only, and non-mutating. It combines the
selected-class missing-input pack with the business-facing change-impact
summary so an operator sees only the exact files, fields, and runtime
artifacts still needed before the first real attempt.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MISSING_INPUT_SCRIPT = ROOT / "scripts" / "compile_st1_097_missing_input_pack.py"
CHANGE_IMPACT_SCRIPT = ROOT / "scripts" / "summarize_st1_101_submission_change_impact.py"


def run_json(script: Path, args: list[str]) -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def external_items(requirements: list[dict[str, Any]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for req in requirements:
        field_path = req["field_path"]
        if field_path.startswith("transformation."):
            artifact = "native_record_submission"
        else:
            artifact = "external_evidence_bundle"
        items.append(
            {
                "artifact": artifact,
                "field_path": field_path,
                "requirement": req["requirement"],
            }
        )
    return items


def runtime_items(requirements: list[dict[str, Any]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for req in requirements:
        items.append(
            {
                "artifact": "runtime_only_input",
                "field_path": req["field_path"],
                "required_kind": req["required_kind"],
            }
        )
    return items


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

    missing_input = run_json(
        MISSING_INPUT_SCRIPT,
        [
            "--bundle", str(args.submission_bundle),
            "--native-record", str(args.submission_native_record),
            "--operator-inputs", str(args.operator_inputs),
            "--receipt", str(args.receipt),
            "--batch", str(args.batch),
        ],
    )
    change_impact = run_json(
        CHANGE_IMPACT_SCRIPT,
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

    missing = missing_input["missing_input_pack"]["exact_missing_inputs"]
    checklist = {
        "external_evidence_bundle_items": external_items(missing["external_evidence_requirements"]),
        "runtime_only_items": runtime_items(missing["runtime_only_requirements"]),
    }

    output = {
        "schema_version": "st1-102-candidate-submission-checklist-v1",
        "candidate_class_id": missing_input["candidate_class_id"],
        "project_scope": missing_input["project_scope"],
        "checklist_result": (
            "READY_CHECKLIST"
            if not checklist["external_evidence_bundle_items"] and not checklist["runtime_only_items"]
            else "CHECKLIST_ITEMS_REMAIN"
        ),
        "change_impact_result": change_impact["change_impact_result"],
        "readiness_transition": change_impact["readiness_transition"],
        "next_action_transition": change_impact["next_action_transition"],
        "exact_checklist_items": checklist,
        "checklist_counts": {
            "external_evidence_bundle_items": len(checklist["external_evidence_bundle_items"]),
            "runtime_only_items": len(checklist["runtime_only_items"]),
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
