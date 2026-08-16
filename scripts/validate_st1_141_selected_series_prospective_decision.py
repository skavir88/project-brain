#!/usr/bin/env python3
"""Validate the bounded ST1-141 Governance Owner decision locally.

This validator is local-only and non-destructive. It does not activate
delegation, register a source, acquire data, or certify anything.

It classifies one decision into:

- WAITING_FOR_GOVERNANCE_OWNER_DECISION
- READY_FOR_TRANSLATION
- WAITING_FOR_EXACT_CORRECTIONS
- REJECTED_SCOPE_OR_POLICY_MISMATCH
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compile_st1_140_selected_series_prospective_decision import (
    MIN_EFFECTIVE_FROM,
    PERMITTED_FACTS,
    PROJECT_SCOPE,
    PROHIBITED_FACTS,
    PROHIBITED_INFERENCE,
    REPORTING_PERIOD_RULE,
    REPORT_CLASS,
    TARGET_SOURCE_ID,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def has_required_marker(value: object) -> bool:
    if isinstance(value, str):
        return "REQUIRED_INPUT" in value
    if isinstance(value, list):
        return any(has_required_marker(item) for item in value)
    if isinstance(value, dict):
        return any(has_required_marker(item) for item in value.values())
    return False


def validate_common(decision: dict) -> list[str]:
    errors: list[str] = []
    required = {
        "decision_version",
        "project_scope",
        "target_source_id",
        "representative_filename",
        "governance_bootstrap_effective_from",
        "selected_series_identifier",
        "selected_series_identifier_kind",
        "report_class",
        "governance_owner_decision_state",
        "approval_mode",
        "decision_reference",
        "decision_acquisition_provenance",
        "proposed_values",
        "corrected_values",
    }
    missing = sorted(required - set(decision))
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))
        return errors

    if decision["decision_version"] != "st1-140/v1":
        errors.append("decision_version must be st1-140/v1")
    if decision["project_scope"] != PROJECT_SCOPE:
        errors.append(f"project_scope must be {PROJECT_SCOPE}")
    if decision["target_source_id"] != TARGET_SOURCE_ID:
        errors.append(f"target_source_id must be {TARGET_SOURCE_ID}")
    if decision["report_class"] != REPORT_CLASS:
        errors.append(f"report_class must be {REPORT_CLASS}")
    if decision["selected_series_identifier"] != TARGET_SOURCE_ID:
        errors.append("selected_series_identifier must preserve the approved pilot series identifier")
    if decision["selected_series_identifier_kind"] != "pilot_non_sensitive_series_identifier":
        errors.append("selected_series_identifier_kind must remain pilot_non_sensitive_series_identifier")
    effective_from = decision["governance_bootstrap_effective_from"]
    if not isinstance(effective_from, str) or effective_from < MIN_EFFECTIVE_FROM:
        errors.append(f"governance_bootstrap_effective_from must be {MIN_EFFECTIVE_FROM} or later")

    proposed = decision.get("proposed_values")
    if not isinstance(proposed, dict):
        errors.append("proposed_values must be an object")
    else:
        if proposed.get("permitted_fact_classes") != PERMITTED_FACTS:
            errors.append("proposed_values.permitted_fact_classes must preserve the approved LOW-risk set")
        if proposed.get("prohibited_fact_classes") != PROHIBITED_FACTS:
            errors.append("proposed_values.prohibited_fact_classes must preserve the approved HIGH-risk set")
        if proposed.get("prohibited_inference") != PROHIBITED_INFERENCE:
            errors.append("proposed_values.prohibited_inference must preserve the approved boundary set")
        if proposed.get("reporting_period_rule") != REPORTING_PERIOD_RULE:
            errors.append("proposed_values.reporting_period_rule must preserve the approved reporting-time rule")
    return errors


def validate_ready(decision: dict, branch: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(decision.get("decision_reference"), str) or not decision["decision_reference"].strip():
        errors.append("decision_reference must be a non-empty string")
    if has_required_marker(decision["decision_reference"]):
        errors.append("decision_reference must not contain REQUIRED_INPUT markers")
    if not isinstance(decision.get("decision_acquisition_provenance"), str) or not decision["decision_acquisition_provenance"].strip():
        errors.append("decision_acquisition_provenance must be a non-empty string")
    if has_required_marker(decision["decision_acquisition_provenance"]):
        errors.append("decision_acquisition_provenance must not contain REQUIRED_INPUT markers")

    values = decision["proposed_values"] if branch == "proposed" else decision["corrected_values"]
    if branch == "corrected":
        if has_required_marker(values):
            errors.append("corrected_values must not contain REQUIRED_INPUT markers when approval_mode=approve_with_explicit_corrections")
        if values.get("permitted_fact_classes") != PERMITTED_FACTS:
            errors.append("corrected_values.permitted_fact_classes must preserve the approved LOW-risk set")
        if values.get("prohibited_fact_classes") != PROHIBITED_FACTS:
            errors.append("corrected_values.prohibited_fact_classes must preserve the approved HIGH-risk set")
        if values.get("prohibited_inference") != PROHIBITED_INFERENCE:
            errors.append("corrected_values.prohibited_inference must preserve the approved boundary set")
        if values.get("reporting_period_rule") != REPORTING_PERIOD_RULE:
            errors.append("corrected_values.reporting_period_rule must preserve the approved reporting-time rule")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", type=Path, required=True, help="Path to the ST1-141 decision JSON file")
    args = parser.parse_args()

    decision = load_json(args.decision)
    common_errors = validate_common(decision)

    state = decision.get("governance_owner_decision_state")
    mode = decision.get("approval_mode")
    readiness = "REJECTED_SCOPE_OR_POLICY_MISMATCH"
    branch = None
    branch_errors: list[str] = []

    if not common_errors:
        if state == "PENDING_GOVERNANCE_OWNER_DECISION":
            readiness = "WAITING_FOR_GOVERNANCE_OWNER_DECISION"
            if mode != "REQUIRED_INPUT":
                branch_errors.append("approval_mode must remain REQUIRED_INPUT while decision is pending")
            if not has_required_marker(decision.get("decision_reference")):
                branch_errors.append("pending decision_reference should still contain REQUIRED_INPUT")
            if not has_required_marker(decision.get("decision_acquisition_provenance")):
                branch_errors.append("pending decision_acquisition_provenance should still contain REQUIRED_INPUT")
        elif state == "APPROVED" and mode == "approve_as_proposed":
            readiness = "READY_FOR_TRANSLATION"
            branch = "proposed"
            branch_errors = validate_ready(decision, branch)
        elif state == "APPROVED" and mode == "approve_with_explicit_corrections":
            readiness = "READY_FOR_TRANSLATION"
            branch = "corrected"
            branch_errors = validate_ready(decision, branch)
        elif state == "APPROVED" and mode == "REQUIRED_INPUT":
            readiness = "WAITING_FOR_EXACT_CORRECTIONS"
            branch_errors.append("approved decision cannot keep approval_mode=REQUIRED_INPUT")
        else:
            branch_errors.append("unsupported combination of governance_owner_decision_state and approval_mode")

    final_errors = common_errors + branch_errors
    if final_errors:
        if readiness == "READY_FOR_TRANSLATION":
            readiness = "REJECTED_SCOPE_OR_POLICY_MISMATCH"
        elif readiness == "WAITING_FOR_GOVERNANCE_OWNER_DECISION" and state != "PENDING_GOVERNANCE_OWNER_DECISION":
            readiness = "REJECTED_SCOPE_OR_POLICY_MISMATCH"

    output = {
        "task_id": "ST1-141",
        "decision_path": str(args.decision),
        "selected_target": {
            "target_source_id": TARGET_SOURCE_ID,
            "project_scope": PROJECT_SCOPE,
            "report_class": REPORT_CLASS,
            "governance_bootstrap_effective_from": MIN_EFFECTIVE_FROM,
        },
        "decision_status": {
            "governance_owner_decision_state": state,
            "approval_mode": mode,
            "branch": branch,
            "readiness": readiness,
            "errors": final_errors,
        },
        "boundary": {
            "historical_authority_backfilled": False,
            "real_delegation_activation": False,
            "real_source_registration": False,
            "real_certification": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
