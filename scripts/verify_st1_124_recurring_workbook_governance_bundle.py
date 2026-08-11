#!/usr/bin/env python3
"""Verify the ST1-124 series-scoped governance intake bundle.

This wrapper keeps the existing ST1-078 bundle contract intact while adding
the exact recurring-workbook-series boundary selected by ST1-122/ST1-123.
It is local-only, non-destructive, and never activates authority,
certification, currentness, or reliance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from assess_st1_078_real_evidence_bundle import (
    REQUIRED_INPUT,
    classify_section,
    classify_top_level,
    readiness_from_statuses,
)
from validate_st1_078_real_evidence_bundle import (
    EXPECTED_EVIDENCE_ITEMS,
    collect_validation_errors,
    load_bundle,
)


TARGET_SOURCE_ID = "maroon_project_controls_progress_workbook_series"
REPRESENTATIVE_SOURCE_ALIAS = "source-a08f4a79cf2116b1"
REPRESENTATIVE_FILENAME = "070-TWRP-24 1402-12-05.xlsx"
REPRESENTATIVE_REPORTING_PERIOD = "1402/11/21–1402/12/05"


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


def classify_series_scope(series_scope: object) -> tuple[str, list[str]]:
    if series_scope is None:
        return "MISSING", ["series_scope not supplied"]
    if not isinstance(series_scope, dict):
        return "REJECTED", ["series_scope must be an object"]

    required_fields = {
        "target_source_id",
        "representative_source_alias",
        "representative_filename",
        "observed_reporting_period_example",
        "stable_source_series_identifier",
        "stable_source_series_identifier_kind",
    }
    missing = sorted(required_fields - set(series_scope))
    if missing:
        return "REJECTED", [f"series_scope missing required fields: {', '.join(missing)}"]

    exact_errors: list[str] = []
    if series_scope.get("target_source_id") != TARGET_SOURCE_ID:
        exact_errors.append(f"series_scope.target_source_id must be {TARGET_SOURCE_ID}")
    if series_scope.get("representative_source_alias") != REPRESENTATIVE_SOURCE_ALIAS:
        exact_errors.append(
            f"series_scope.representative_source_alias must be {REPRESENTATIVE_SOURCE_ALIAS}"
        )
    if series_scope.get("representative_filename") != REPRESENTATIVE_FILENAME:
        exact_errors.append(
            f"series_scope.representative_filename must be {REPRESENTATIVE_FILENAME}"
        )
    if series_scope.get("observed_reporting_period_example") != REPRESENTATIVE_REPORTING_PERIOD:
        exact_errors.append(
            "series_scope.observed_reporting_period_example must preserve the "
            "approved document-content example period"
        )
    if exact_errors:
        return "REJECTED", exact_errors

    if has_required_input(
        [
            series_scope.get("stable_source_series_identifier"),
            series_scope.get("stable_source_series_identifier_kind"),
        ]
    ):
        return "MISSING", ["series_scope still contains REQUIRED_INPUT placeholder(s)"]

    return (
        "PARTIAL",
        ["series_scope is structurally complete but still pending independent verification"],
    )


def build_remaining_inputs(statuses: dict[str, str]) -> list[str]:
    mapping = {
        "A1": "A1_governance_authority_confirmation",
        "A2": "A2_project_controls_accountability_confirmation",
        "A3": "A3_controlled_report_definition_confirmation",
        "source_registration": "stable_source_registration_evidence_reference",
        "series_scope": "stable_non_sensitive_source_series_identifier",
    }
    remaining: list[str] = []
    for key, label in mapping.items():
        if statuses.get(key) == "MISSING":
            remaining.append(label)
    return remaining


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the series-scoped bundle JSON file")
    args = parser.parse_args()

    bundle = load_bundle(args.bundle)
    errors = collect_validation_errors(bundle)

    statuses: dict[str, str] = {}
    details: dict[str, list[str]] = {}

    top_status, top_details = classify_top_level(bundle, errors)
    statuses["bundle"] = top_status
    details["bundle"] = top_details

    evidence_items = bundle.get("evidence_items") if isinstance(bundle.get("evidence_items"), dict) else {}
    for evidence_id in sorted(EXPECTED_EVIDENCE_ITEMS):
        status, section_detail = classify_section(evidence_items.get(evidence_id), errors, f"evidence_items.{evidence_id}")
        statuses[evidence_id] = status
        details[evidence_id] = section_detail

    source_status, source_details = classify_section(
        bundle.get("source_registration"), errors, "source_registration"
    )
    statuses["source_registration"] = source_status
    details["source_registration"] = source_details

    series_status, series_details = classify_series_scope(bundle.get("series_scope"))
    statuses["series_scope"] = series_status
    details["series_scope"] = series_details

    output = {
        "task_id": "ST1-124",
        "selected_target": {
            "target_source_id": TARGET_SOURCE_ID,
            "representative_source_alias": REPRESENTATIVE_SOURCE_ALIAS,
            "representative_filename": REPRESENTATIVE_FILENAME,
            "observed_reporting_period_example": REPRESENTATIVE_REPORTING_PERIOD,
        },
        "structural_validation_passed": len(errors) == 0 and series_status != "REJECTED",
        "activation_readiness": readiness_from_statuses(statuses),
        "section_statuses": statuses,
        "section_details": details,
        "required_external_inputs_remaining": build_remaining_inputs(statuses),
        "boundary": {
            "real_delegation_activation": False,
            "real_certification": False,
            "real_source_registration": False,
            "st1_061_is_success_target": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
