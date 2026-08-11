#!/usr/bin/env python3
"""Compile a source-control verification step card for the second write target.

This compiler is deterministic, local-only, and non-mutating. It reduces the
selected-class source-registration step card plus known handoff data to only
the minimal field-level payload and confirmations for
`sdas_source_control_verifications`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_REGISTRATION_SCRIPT = ROOT / "scripts" / "compile_st1_107_source_registration_step_card.py"
HANDOFF_SCRIPT = ROOT / "scripts" / "compile_st1_094_external_evidence_to_dossier_handoff.py"

BUSINESS_TIME_RULE_MAP = {
    "workbook_labelled_reporting_week_header": "approved_report_header",
    "designated_reporting_period_field": "registered_source_system_period_field",
}


def run_json(script: Path, args: list[str]) -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def resolve_business_time_rule(resolution_source: str | None) -> str:
    if resolution_source in BUSINESS_TIME_RULE_MAP:
        return BUSINESS_TIME_RULE_MAP[resolution_source]
    return "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_EVIDENCE"


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

    source_registration = run_json(
        SOURCE_REGISTRATION_SCRIPT,
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

    source_step = source_registration["source_registration_step_card"]
    source_confirmations = source_step["required_confirmations"]
    source_ready = source_registration["step_card_status"] == "READY_SOURCE_REGISTRATION_STEP_CARD"
    handoff_ready = handoff.get("handoff_status") == "READY_DOSSIER_HANDOFF"
    ready = source_ready and handoff_ready

    payload: dict[str, Any] = {}
    if handoff_ready:
        summary = handoff["verified_external_evidence_summary"]
        payload = {
            "source_id": summary["source_id"],
            "project_scope": source_registration["project_scope"],
            "document_data_class": summary["report_class"],
            "business_time_rule": resolve_business_time_rule(summary["resolution_source"]),
            "accountable_actor_id": "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_BUNDLE",
            "evidence_reference": "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_BUNDLE",
            "evidence_fingerprint": "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_BUNDLE",
        }

    output = {
        "schema_version": "st1-108-source-control-verification-step-card-v1",
        "candidate_class_id": source_registration["candidate_class_id"],
        "project_scope": source_registration["project_scope"],
        "step_card_status": "READY_SOURCE_CONTROL_VERIFICATION_STEP_CARD" if ready else "BLOCKED_SOURCE_CONTROL_VERIFICATION_STEP_CARD",
        "source_control_verification_step_card": {
            "write_target": "sdas_source_control_verifications",
            "minimal_payload": payload,
            "required_confirmations": {
                "source_registration_step_card_ready": source_ready,
                **source_confirmations,
            },
            "remaining_checklist_items": source_step.get("remaining_checklist_items"),
        },
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_source_control_verified": False,
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
