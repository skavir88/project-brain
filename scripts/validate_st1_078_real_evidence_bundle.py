#!/usr/bin/env python3
"""Validate the local ST1-078 real-evidence intake bundle.

This validator is deliberately local-only and non-destructive. It checks only
bundle structure, exact candidate scope, required fields, and fact/time
boundaries. It never activates authority and never connects to remote systems.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROJECT_SCOPE = "maroon_pilot"
CANDIDATE_CLASS_ID = "project_controls_progress_workbook"
EXPECTED_EVIDENCE_ITEMS = {
    "A1": "governance_authority",
    "A2": "project_controls_accountability",
    "A3": "controlled_report_definition",
}
EXPECTED_REPORTING_SOURCES = {
    "workbook_labelled_reporting_week_header",
    "designated_reporting_period_field",
}
DISALLOWED_REPORTING_SUBSTITUTES = {
    "row_level_planned_date",
    "row_level_target_date",
    "filesystem_timestamp",
    "acquisition_timestamp",
}
PERMITTED_FACTS = {
    "report_period",
    "reported_plan",
    "reported_actual",
    "reported_progress",
    "reported_activity",
    "reported_milestone",
    "reported_project_control_issue",
}
PROHIBITED_FACTS = {
    "contractual_delay_determination",
    "entitlement",
    "claim",
    "payment_authorization_or_status",
    "financial_liability",
    "legal_conclusion",
    "safety_or_compliance_certification",
    "final_completion",
    "current_executive_status_outside_report_period",
    "reliance_eligibility",
    "insurance_or_guarantee_status",
}
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def fail(errors: list[str]) -> int:
    for item in errors:
        print(f"FAIL: {item}", file=sys.stderr)
    return 2


def require_keys(errors: list[str], obj: dict, required: set[str], context: str) -> None:
    missing = sorted(required - set(obj))
    if missing:
        errors.append(f"{context} missing required fields: {', '.join(missing)}")


def require_nonempty_str(errors: list[str], obj: dict, key: str, context: str) -> None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}.{key} must be a non-empty string")


def validate_bool_false(errors: list[str], obj: dict, key: str) -> None:
    if obj.get(key) is not False:
        errors.append(f"{key} must remain false")


def validate_exact_set(errors: list[str], observed: list[str] | object, expected: set[str], context: str) -> None:
    if not isinstance(observed, list) or set(observed) != expected:
        errors.append(f"{context} must match the approved exact set")


def load_bundle(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"FAIL: bundle not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON: {exc.msg}", file=sys.stderr)
        raise SystemExit(2)


def collect_validation_errors(bundle: dict) -> list[str]:
    errors: list[str] = []

    require_keys(
        errors,
        bundle,
        {
            "bundle_version",
            "candidate_class_id",
            "project_scope",
            "activation_request",
            "automatic_certification_requested",
            "currentness_override_requested",
            "reliance_override_requested",
            "evidence_items",
            "source_registration",
        },
        "bundle",
    )

    if bundle.get("bundle_version") != "st1-078/v1":
        errors.append("bundle_version must be st1-078/v1")
    if bundle.get("candidate_class_id") != CANDIDATE_CLASS_ID:
        errors.append("candidate_class_id does not match the selected ST1-075/ST1-076 class")
    if bundle.get("project_scope") != PROJECT_SCOPE:
        errors.append("project_scope must be maroon_pilot")

    for key in (
        "activation_request",
        "automatic_certification_requested",
        "currentness_override_requested",
        "reliance_override_requested",
    ):
        validate_bool_false(errors, bundle, key)

    evidence_items = bundle.get("evidence_items")
    if not isinstance(evidence_items, dict):
        errors.append("evidence_items must be an object")
        evidence_items = {}

    if set(evidence_items) != set(EXPECTED_EVIDENCE_ITEMS):
        errors.append("evidence_items must contain exactly A1, A2, and A3")

    for evidence_id, expected_kind in EXPECTED_EVIDENCE_ITEMS.items():
        item = evidence_items.get(evidence_id)
        context = f"evidence_items.{evidence_id}"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        require_keys(
            errors,
            item,
            {
                "tier",
                "status",
                "attestation_kind",
                "subject_role_class",
                "asserted_scope",
                "effective_from",
                "signed_artifact_reference",
                "signed_artifact_fingerprint",
                "acquisition_provenance",
                "payload",
            },
            context,
        )
        if item.get("attestation_kind") != expected_kind:
            errors.append(f"{context}.attestation_kind must be {expected_kind}")
        if item.get("asserted_scope") != PROJECT_SCOPE:
            errors.append(f"{context}.asserted_scope must be {PROJECT_SCOPE}")
        require_nonempty_str(errors, item, "subject_role_class", context)
        require_nonempty_str(errors, item, "effective_from", context)
        require_nonempty_str(errors, item, "signed_artifact_reference", context)
        require_nonempty_str(errors, item, "acquisition_provenance", context)
        fingerprint = item.get("signed_artifact_fingerprint")
        if not isinstance(fingerprint, str) or not HEX_64.fullmatch(fingerprint):
            errors.append(f"{context}.signed_artifact_fingerprint must be a lowercase sha256 hex string")

        payload = item.get("payload")
        if not isinstance(payload, dict):
            errors.append(f"{context}.payload must be an object")
            continue

        if evidence_id == "A1":
            require_keys(
                errors,
                payload,
                {"governance_role_class", "authority_basis", "scope", "expiry_or_revocation_rule", "approval_method"},
                f"{context}.payload",
            )
            if payload.get("scope") != PROJECT_SCOPE:
                errors.append(f"{context}.payload.scope must be {PROJECT_SCOPE}")
        elif evidence_id == "A2":
            require_keys(
                errors,
                payload,
                {"accountable_role_class", "report_classes", "permitted_fact_classes", "prohibited_fact_classes", "scope", "approval_method"},
                f"{context}.payload",
            )
            if payload.get("scope") != PROJECT_SCOPE:
                errors.append(f"{context}.payload.scope must be {PROJECT_SCOPE}")
            validate_exact_set(errors, payload.get("permitted_fact_classes"), PERMITTED_FACTS, f"{context}.payload.permitted_fact_classes")
            validate_exact_set(errors, payload.get("prohibited_fact_classes"), PROHIBITED_FACTS, f"{context}.payload.prohibited_fact_classes")
            if payload.get("report_classes") != [CANDIDATE_CLASS_ID]:
                errors.append(f"{context}.payload.report_classes must contain only {CANDIDATE_CLASS_ID}")
        elif evidence_id == "A3":
            require_keys(
                errors,
                payload,
                {
                    "source_report_class",
                    "owning_role_class",
                    "source_location_class",
                    "reporting_period_rule",
                    "document_identifier_convention",
                    "permitted_fact_classes",
                    "prohibited_inference",
                    "scope",
                    "approval_method",
                },
                f"{context}.payload",
            )
            if payload.get("scope") != PROJECT_SCOPE:
                errors.append(f"{context}.payload.scope must be {PROJECT_SCOPE}")
            if payload.get("source_report_class") != CANDIDATE_CLASS_ID:
                errors.append(f"{context}.payload.source_report_class must be {CANDIDATE_CLASS_ID}")
            validate_exact_set(errors, payload.get("permitted_fact_classes"), PERMITTED_FACTS, f"{context}.payload.permitted_fact_classes")
            reporting_rule = payload.get("reporting_period_rule")
            if not isinstance(reporting_rule, dict):
                errors.append(f"{context}.payload.reporting_period_rule must be an object")
            else:
                validate_exact_set(errors, reporting_rule.get("accepted_sources"), EXPECTED_REPORTING_SOURCES, f"{context}.payload.reporting_period_rule.accepted_sources")
                validate_exact_set(errors, reporting_rule.get("disallowed_substitutes"), DISALLOWED_REPORTING_SUBSTITUTES, f"{context}.payload.reporting_period_rule.disallowed_substitutes")

    source_registration = bundle.get("source_registration")
    if not isinstance(source_registration, dict):
        errors.append("source_registration must be an object")
        source_registration = {}
    require_keys(
        errors,
        source_registration,
        {
            "source_id",
            "source_type",
            "non_sensitive_location_class",
            "owning_role_class",
            "project_scope",
            "report_class",
            "authority_state",
            "evidence_reference",
        },
        "source_registration",
    )
    for key in (
        "source_id",
        "source_type",
        "non_sensitive_location_class",
        "owning_role_class",
        "authority_state",
        "evidence_reference",
    ):
        require_nonempty_str(errors, source_registration, key, "source_registration")
    if source_registration.get("project_scope") != PROJECT_SCOPE:
        errors.append("source_registration.project_scope must be maroon_pilot")
    if source_registration.get("report_class") != CANDIDATE_CLASS_ID:
        errors.append("source_registration.report_class must be project_controls_progress_workbook")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the intake bundle JSON file")
    args = parser.parse_args()

    bundle = load_bundle(args.bundle)
    errors = collect_validation_errors(bundle)

    if errors:
        return fail(errors)

    print(
        json.dumps(
            {
                "validation_result": "STRUCTURALLY_COMPLETE_PENDING_INDEPENDENT_VERIFICATION",
                "candidate_class_id": CANDIDATE_CLASS_ID,
                "project_scope": PROJECT_SCOPE,
                "evidence_items": sorted(EXPECTED_EVIDENCE_ITEMS),
                "source_registration_ready": True,
                "activation_permitted": False,
                "automatic_certification_permitted": False,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
