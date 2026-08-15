#!/usr/bin/env python3
"""Verify the ST1-136 post-A1 remaining-input supplement.

This local-only verifier checks the exact selected-series supplement that is
meant to be merged onto the already-captured ST1-135 A1 partial bundle. It
never activates governance, registers a source, acquires a file, or certifies
anything.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from assess_st1_078_real_evidence_bundle import REQUIRED_INPUT, classify_section
from validate_st1_078_real_evidence_bundle import (
    CANDIDATE_CLASS_ID,
    EXPECTED_EVIDENCE_ITEMS,
    PROJECT_SCOPE,
    collect_validation_errors,
)


TARGET_SOURCE_ID = "maroon_project_controls_progress_workbook_series"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def flatten(value: object) -> list[object]:
    items: list[object] = []
    if isinstance(value, dict):
        for nested in value.values():
            items.extend(flatten(nested))
    elif isinstance(value, list):
        for nested in value:
            items.extend(flatten(nested))
    else:
        items.append(value)
    return items


def has_required_input(value: object) -> bool:
    return any(item == REQUIRED_INPUT for item in flatten(value))


def validate_series_scope(scope: object) -> tuple[str, list[str]]:
    if not isinstance(scope, dict):
        return "REJECTED", ["series_scope must be an object"]
    errors: list[str] = []
    if has_required_input(scope):
        return "MISSING", ["series_scope still contains REQUIRED_INPUT placeholder(s)"]
    if scope.get("stable_source_series_identifier") in ("", None):
        errors.append("series_scope.stable_source_series_identifier must be a non-empty string")
    if scope.get("stable_source_series_identifier_kind") in ("", None):
        errors.append("series_scope.stable_source_series_identifier_kind must be a non-empty string")
    if errors:
        return "REJECTED", errors
    return "PARTIAL", ["series_scope is structurally complete but still pending independent verification"]


def validate_source_registration(source: object) -> tuple[str, list[str]]:
    if not isinstance(source, dict):
        return "REJECTED", ["source_registration must be an object"]
    if has_required_input(source):
        return "MISSING", ["source_registration still contains REQUIRED_INPUT placeholder(s)"]
    errors: list[str] = []
    for key in ("non_sensitive_location_class", "owning_role_class", "evidence_reference"):
        value = source.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"source_registration.{key} must be a non-empty string")
    if errors:
        return "REJECTED", errors
    return "PARTIAL", ["source_registration is structurally complete but still pending independent verification"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supplement", type=Path, required=True, help="Path to the ST1-136 remaining-input supplement JSON")
    args = parser.parse_args()

    supplement = load_json(args.supplement)
    errors: list[str] = []

    if supplement.get("supplement_version") != "st1-136/v1":
        errors.append("supplement_version must be st1-136/v1")
    if supplement.get("project_scope") != PROJECT_SCOPE:
        errors.append("project_scope must be maroon_pilot")
    if supplement.get("target_source_id") != TARGET_SOURCE_ID:
        errors.append(f"target_source_id must be {TARGET_SOURCE_ID}")

    evidence = supplement.get("evidence_items")
    if not isinstance(evidence, dict):
        errors.append("evidence_items must be an object")
        evidence = {}
    if set(evidence) != {"A2", "A3"}:
        errors.append("evidence_items must contain exactly A2 and A3")

    synthetic_bundle = {
        "bundle_version": "st1-078/v1",
        "candidate_class_id": CANDIDATE_CLASS_ID,
        "project_scope": PROJECT_SCOPE,
        "activation_request": False,
        "automatic_certification_requested": False,
        "currentness_override_requested": False,
        "reliance_override_requested": False,
        "evidence_items": {
            "A1": {
                "tier": "B",
                "status": "SUPPLIED_UNVALIDATED",
                "attestation_kind": EXPECTED_EVIDENCE_ITEMS["A1"],
                "subject_role_class": "placeholder_a1_preserved_elsewhere",
                "asserted_scope": PROJECT_SCOPE,
                "effective_from": "2026-08-11T00:00:00Z",
                "signed_artifact_reference": "placeholder://a1",
                "signed_artifact_fingerprint": "1111111111111111111111111111111111111111111111111111111111111111",
                "acquisition_provenance": "placeholder",
                "payload": {
                    "governance_role_class": "placeholder",
                    "authority_basis": "placeholder",
                    "scope": PROJECT_SCOPE,
                    "expiry_or_revocation_rule": "placeholder",
                    "approval_method": "placeholder"
                }
            },
            "A2": evidence.get("A2"),
            "A3": evidence.get("A3"),
        },
        "source_registration": {
            "source_id": TARGET_SOURCE_ID,
            "source_type": "recurring_report_series",
            "non_sensitive_location_class": supplement.get("source_registration", {}).get("non_sensitive_location_class"),
            "owning_role_class": supplement.get("source_registration", {}).get("owning_role_class"),
            "project_scope": PROJECT_SCOPE,
            "report_class": CANDIDATE_CLASS_ID,
            "authority_state": "awaiting_validation",
            "evidence_reference": supplement.get("source_registration", {}).get("evidence_reference"),
        },
    }
    bundle_errors = collect_validation_errors(synthetic_bundle)

    statuses: dict[str, str] = {}
    details: dict[str, list[str]] = {}

    for evidence_id in ("A2", "A3"):
        status, detail = classify_section(evidence.get(evidence_id), bundle_errors, f"evidence_items.{evidence_id}")
        statuses[evidence_id] = status
        details[evidence_id] = detail

    sr_status, sr_detail = validate_source_registration(supplement.get("source_registration"))
    ss_status, ss_detail = validate_series_scope(supplement.get("series_scope"))
    statuses["source_registration"] = sr_status
    statuses["series_scope"] = ss_status
    details["source_registration"] = sr_detail
    details["series_scope"] = ss_detail

    if errors or any(status == "REJECTED" for status in statuses.values()):
        readiness = "WAITING_FOR_SCOPE_OR_POLICY_CORRECTION"
    elif any(status == "MISSING" for status in statuses.values()):
        readiness = "WAITING_FOR_EXTERNAL_EVIDENCE"
    else:
        readiness = "READY_TO_MERGE_ONTO_A1_PARTIAL_BUNDLE"

    output = {
        "task_id": "ST1-136",
        "supplement_path": str(args.supplement),
        "selected_target": {
            "target_source_id": TARGET_SOURCE_ID,
            "candidate_class_id": CANDIDATE_CLASS_ID,
        },
        "structural_validation_passed": len(errors) == 0 and len(bundle_errors) == 0,
        "readiness": readiness,
        "top_level_errors": errors,
        "section_statuses": statuses,
        "section_details": details,
        "boundary": {
            "real_delegation_activation": False,
            "real_source_registration": False,
            "real_native_acquisition": False,
            "real_policy_mutation": False,
            "real_certification": False,
            "st1_061_is_success_target": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
