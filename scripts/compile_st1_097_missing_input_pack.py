#!/usr/bin/env python3
"""Compile a concise missing-input pack for the selected-class first real attempt.

This compiler is deterministic, local-only, and non-mutating. It consumes the
existing ST1-094/ST1-095/ST1-096 selected-class artifacts and emits only the
exact external-evidence or runtime-only inputs still missing when the first
real attempt is not yet ready to run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_SCRIPT = ROOT / "scripts" / "compile_st1_094_external_evidence_to_dossier_handoff.py"
LAUNCH_SCRIPT = ROOT / "scripts" / "compile_st1_095_final_operator_launch_package.py"
READINESS_SCRIPT = ROOT / "scripts" / "compile_st1_096_real_run_readiness_summary.py"

RUNTIME_PLACEHOLDER = "RUNTIME_REQUIRED_INPUT"
RUNTIME_ALLOWED_SET_PLACEHOLDER = "RUNTIME_REQUIRED_INPUT_FROM_ALLOWED_SET"
RUNTIME_VERIFIED_EVIDENCE_PLACEHOLDER = "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_EVIDENCE"


def run_json(script: Path, args: list[str]) -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def collect_runtime_placeholders(value: Any, path: str = "") -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            next_path = f"{path}.{key}" if path else key
            items.extend(collect_runtime_placeholders(nested, next_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            next_path = f"{path}[{index}]"
            items.extend(collect_runtime_placeholders(nested, next_path))
    elif isinstance(value, str):
        if value == RUNTIME_PLACEHOLDER:
            items.append({"field_path": path, "required_kind": "runtime_value"})
        elif value == RUNTIME_ALLOWED_SET_PLACEHOLDER:
            items.append({"field_path": path, "required_kind": "approved_fact_class"})
        elif value == RUNTIME_VERIFIED_EVIDENCE_PLACEHOLDER:
            items.append({"field_path": path, "required_kind": "verified_evidence_identity"})
    return items


def normalize_error(error: str) -> dict[str, str]:
    field_path = error.split(" must be ", 1)[0] if " must be " in error else error
    return {
        "field_path": field_path,
        "requirement": error,
    }


def build_external_missing_pack(handoff: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    blockers = handoff.get("blocking_reasons", {})
    native_errors = blockers.get("native_record_errors", []) if isinstance(blockers, dict) else []
    bundle_errors = blockers.get("bundle_errors", []) if isinstance(blockers, dict) else []
    external_requirements = [normalize_error(item) for item in [*bundle_errors, *native_errors]]

    return {
        "missing_input_state": "waiting_for_external_evidence",
        "blocking_reasons": readiness.get("blocking_reasons", []),
        "exact_missing_inputs": {
            "external_evidence_requirements": external_requirements,
            "runtime_only_requirements": [],
        },
        "counts": {
            "external_evidence_requirements": len(external_requirements),
            "runtime_only_requirements": 0,
        },
    }


def build_runtime_missing_pack(handoff: dict[str, Any], readiness: dict[str, Any], operator_inputs_path: Path) -> dict[str, Any]:
    derived_template = (
        handoff.get("dossier_ready_inputs", {}).get("derived_operator_inputs_template", {})
        if isinstance(handoff.get("dossier_ready_inputs"), dict)
        else {}
    )
    current_inputs = json.loads(operator_inputs_path.read_text(encoding="utf-8"))
    unresolved_paths = collect_runtime_placeholders(current_inputs)
    template_runtime_fields = collect_runtime_placeholders(derived_template)
    unresolved_field_paths = {item["field_path"] for item in unresolved_paths}

    exact_runtime_requirements = [
        item for item in template_runtime_fields
        if item["field_path"] in unresolved_field_paths
    ]

    additional_runtime_only = []
    remaining_runtime_only_fields = readiness.get("remaining_runtime_only_fields", [])
    if isinstance(remaining_runtime_only_fields, list):
        for item in remaining_runtime_only_fields:
            if item in {
                "runtime receipt after actual execution",
                "batch routing input only if exception-queue simulation is needed for the same run",
            }:
                additional_runtime_only.append({"field_path": item, "required_kind": "later_runtime_artifact"})

    return {
        "missing_input_state": "waiting_for_runtime_only_fields",
        "blocking_reasons": readiness.get("blocking_reasons", []),
        "exact_missing_inputs": {
            "external_evidence_requirements": [],
            "runtime_only_requirements": exact_runtime_requirements + additional_runtime_only,
        },
        "counts": {
            "external_evidence_requirements": 0,
            "runtime_only_requirements": len(exact_runtime_requirements) + len(additional_runtime_only),
        },
    }


def build_ready_pack(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "missing_input_state": "ready_to_run",
        "blocking_reasons": readiness.get("blocking_reasons", []),
        "exact_missing_inputs": {
            "external_evidence_requirements": [],
            "runtime_only_requirements": [],
        },
        "counts": {
            "external_evidence_requirements": 0,
            "runtime_only_requirements": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to ST1-078 bundle JSON")
    parser.add_argument("--native-record", type=Path, required=True, help="Path to ST1-083 native-record JSON")
    parser.add_argument("--operator-inputs", type=Path, required=True, help="Path to ST1-088 operator-input JSON")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to ST1-089 receipt JSON")
    parser.add_argument("--batch", type=Path, required=True, help="Path to ST1-090 batch JSON")
    args = parser.parse_args()

    command_args = [
        "--bundle", str(args.bundle),
        "--native-record", str(args.native_record),
        "--operator-inputs", str(args.operator_inputs),
        "--receipt", str(args.receipt),
        "--batch", str(args.batch),
    ]
    handoff = run_json(HANDOFF_SCRIPT, ["--bundle", str(args.bundle), "--native-record", str(args.native_record)])
    launch = run_json(LAUNCH_SCRIPT, command_args)
    readiness = run_json(READINESS_SCRIPT, command_args)

    readiness_status = readiness.get("readiness_status")
    if readiness_status == "waiting_for_external_evidence":
        pack = build_external_missing_pack(handoff, readiness)
    elif readiness_status == "waiting_for_runtime_only_fields":
        pack = build_runtime_missing_pack(handoff, readiness, args.operator_inputs)
    else:
        pack = build_ready_pack(readiness)

    output = {
        "schema_version": "st1-097-selected-class-missing-input-pack-v1",
        "candidate_class_id": readiness.get("candidate_class_id"),
        "project_scope": readiness.get("project_scope"),
        "readiness_status": readiness_status,
        "missing_input_pack": pack,
        "references": {
            "handoff_status": handoff.get("handoff_status"),
            "launch_package_status": launch.get("launch_package_status"),
            "readiness_summary_status": readiness_status,
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
