#!/usr/bin/env python3
"""Compile the ST1-127 independent-verification handoff for a series bundle.

This script sits immediately after the deterministic ST1-125 series gate.
It does not verify identity, activate authority, register a source, acquire
data, or certify anything. It only converts the gate outcome into the exact
controlled checks still required before any future real selected-series
runtime mutation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


TARGET_SOURCE_ID = "maroon_project_controls_progress_workbook_series"
TARGET_SERIES_ALIAS = "source-a08f4a79cf2116b1"
TARGET_REPORTING_PERIOD = "1402/11/21–1402/12/05"


def run_gate(bundle: Path) -> dict:
    result = subprocess.run(
        [sys.executable, "scripts/run_st1_125_series_bundle_gate.py", "--bundle", str(bundle)],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or result.stderr).strip()
    if not output:
        raise SystemExit("ST1-127 gate handoff failed: no output from ST1-125 gate")
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ST1-127 gate handoff failed: invalid gate JSON: {exc}") from exc


def build_checks(gate: dict) -> list[dict[str, object]]:
    readiness = gate.get("gate_summary", {}).get("activation_readiness")
    selected_match = gate.get("gate_summary", {}).get("selected_series_match")

    checks: list[dict[str, object]] = [
        {
            "check_id": "IV-001",
            "title": "Governance approver identity verification",
            "required_when": "always",
            "evidence_target": "A1 signer identity + organizational role + authority basis + effective period",
            "expected_outcome": "controlled signer identity independently verified for Maroon pilot governance scope",
        },
        {
            "check_id": "IV-002",
            "title": "Project Controls / PMO accountable role verification",
            "required_when": "always",
            "evidence_target": "A2 signer identity + accountable role + project scope match + recurring report-class responsibility",
            "expected_outcome": "accountable role independently verified for the exact recurring workbook class and Maroon scope",
        },
        {
            "check_id": "IV-003",
            "title": "Controlled report-definition verification",
            "required_when": "always",
            "evidence_target": "A3 owning role + source/location class + reporting-period field/header rule + document/version convention + release/approval convention",
            "expected_outcome": "exact workbook/report class definition independently verified",
        },
        {
            "check_id": "IV-004",
            "title": "Business-time rule verification",
            "required_when": "always",
            "evidence_target": "approved reporting-period header/field for the recurring workbook class",
            "expected_outcome": "business time resolvable only from approved header/field and not from filesystem/acquisition/row-level dates",
        },
        {
            "check_id": "IV-005",
            "title": "Source ownership/control verification",
            "required_when": "always",
            "evidence_target": "stable source-series identifier + source-registration evidence reference + owning role alignment",
            "expected_outcome": "the exact registered recurring workbook series is independently tied to the accountable role and approved scope",
        },
        {
            "check_id": "IV-006",
            "title": "Selected-series exact-scope confirmation",
            "required_when": "always",
            "evidence_target": "target_source_id + representative alias + representative filename + observed example reporting period",
            "expected_outcome": "bundle remains exactly matched to the selected success-target series and excludes ST1-061",
        },
    ]

    if readiness == "PENDING_INDEPENDENT_VERIFICATION" and selected_match:
        for item in checks:
            item["status"] = "REQUIRED_FOR_REAL_REVIEW"
    elif readiness == "WAITING_FOR_EXTERNAL_EVIDENCE":
        for item in checks:
            item["status"] = "NOT_READY_EXTERNAL_EVIDENCE_INCOMPLETE"
    else:
        for item in checks:
            item["status"] = "NOT_READY_SCOPE_OR_POLICY_CORRECTION_REQUIRED"
    return checks


def build_missing_inputs(gate: dict) -> list[str]:
    series_result = gate.get("series_alignment_verification", {}).get("result", {})
    if isinstance(series_result, dict):
        remaining = series_result.get("required_external_inputs_remaining")
        if isinstance(remaining, list):
            return remaining
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the selected-series bundle JSON file")
    args = parser.parse_args()

    gate = run_gate(args.bundle)
    readiness = gate.get("gate_summary", {}).get("activation_readiness")
    selected_match = gate.get("gate_summary", {}).get("selected_series_match")

    output = {
        "task_id": "ST1-127",
        "bundle_path": str(args.bundle),
        "selected_target": {
            "target_source_id": TARGET_SOURCE_ID,
            "representative_source_alias": TARGET_SERIES_ALIAS,
            "observed_reporting_period_example": TARGET_REPORTING_PERIOD,
        },
        "gate_summary": gate.get("gate_summary", {}),
        "independent_verification_readiness": {
            "can_begin_real_controlled_review": readiness == "PENDING_INDEPENDENT_VERIFICATION" and selected_match,
            "activation_readiness": readiness,
            "selected_series_match": selected_match,
            "missing_external_inputs": build_missing_inputs(gate),
        },
        "required_controlled_checks": build_checks(gate),
        "boundary": {
            "real_delegation_activation": False,
            "real_source_registration": False,
            "real_native_acquisition": False,
            "real_certification": False,
            "st1_061_is_success_target": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
