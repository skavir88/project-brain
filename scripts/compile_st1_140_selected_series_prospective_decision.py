#!/usr/bin/env python3
"""Compile one bounded ST1-140 governance-owner decision into ST1-136 inputs.

This is local-only and non-destructive. It reuses the existing selected-series
machinery by translating one approved prospective governance-owner decision into:

- A2 attestation artifact
- A3 attestation artifact
- ST1-136 supplement
- merged selected-series bundle

It never activates delegation, registers a source, acquires data, or certifies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


TARGET_SOURCE_ID = "maroon_project_controls_progress_workbook_series"
PROJECT_SCOPE = "maroon_pilot"
REPORT_CLASS = "project_controls_progress_workbook"
MIN_EFFECTIVE_FROM = "2026-08-15"
PERMITTED_FACTS = [
    "report_period",
    "reported_plan",
    "reported_actual",
    "reported_progress",
    "reported_activity",
    "reported_milestone",
    "reported_project_control_issue",
]
PROHIBITED_FACTS = [
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
]
PROHIBITED_INFERENCE = [
    "current_executive_status_outside_report_period",
    "reliance_eligibility",
    "insurance_or_guarantee_status",
]
REPORTING_PERIOD_RULE = {
    "accepted_sources": [
        "workbook_labelled_reporting_week_header",
        "designated_reporting_period_field",
    ],
    "disallowed_substitutes": [
        "row_level_planned_date",
        "row_level_target_date",
        "filesystem_timestamp",
        "acquisition_timestamp",
    ],
}


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 2


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"FAIL: file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: invalid JSON in {path}: {exc.msg}")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_value(decision: dict) -> dict:
    mode = decision.get("approval_mode")
    if decision.get("governance_owner_decision_state") != "APPROVED":
        raise SystemExit("FAIL: governance_owner_decision_state must be APPROVED")
    if mode == "approve_as_proposed":
        return decision["proposed_values"]
    if mode == "approve_with_explicit_corrections":
        corrected = decision.get("corrected_values")
        if not isinstance(corrected, dict):
            raise SystemExit("FAIL: corrected_values must be an object")
        text_markers = [
            corrected.get("accountable_role_class"),
            corrected.get("source_location_class"),
            corrected.get("document_identifier_convention"),
            corrected.get("approval_method"),
        ]
        if any(not isinstance(v, str) or "REQUIRED_INPUT" in v or not v.strip() for v in text_markers):
            raise SystemExit("FAIL: corrected_values must contain exact non-placeholder text fields")
        for key in ("permitted_fact_classes", "prohibited_fact_classes", "prohibited_inference"):
            value = corrected.get(key)
            if not isinstance(value, list) or any(isinstance(item, str) and "REQUIRED_INPUT" in item for item in value):
                raise SystemExit(f"FAIL: corrected_values.{key} must contain exact non-placeholder values")
        rule = corrected.get("reporting_period_rule")
        if not isinstance(rule, dict):
            raise SystemExit("FAIL: corrected_values.reporting_period_rule must be an object")
        if any(
            isinstance(item, str) and "REQUIRED_INPUT" in item
            for item in rule.get("accepted_sources", []) + rule.get("disallowed_substitutes", [])
        ):
            raise SystemExit("FAIL: corrected reporting_period_rule must not contain placeholders")
        return corrected
    raise SystemExit("FAIL: approval_mode must be approve_as_proposed or approve_with_explicit_corrections")


def validate_decision(decision: dict) -> None:
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
        raise SystemExit("FAIL: decision missing required fields: " + ", ".join(missing))
    if decision["decision_version"] != "st1-140/v1":
        raise SystemExit("FAIL: decision_version must be st1-140/v1")
    if decision["project_scope"] != PROJECT_SCOPE:
        raise SystemExit(f"FAIL: project_scope must be {PROJECT_SCOPE}")
    if decision["target_source_id"] != TARGET_SOURCE_ID:
        raise SystemExit(f"FAIL: target_source_id must be {TARGET_SOURCE_ID}")
    if decision["report_class"] != REPORT_CLASS:
        raise SystemExit(f"FAIL: report_class must be {REPORT_CLASS}")
    if decision["selected_series_identifier"] != TARGET_SOURCE_ID:
        raise SystemExit("FAIL: selected_series_identifier must preserve the approved pilot series identifier")
    if decision["selected_series_identifier_kind"] != "pilot_non_sensitive_series_identifier":
        raise SystemExit("FAIL: selected_series_identifier_kind must remain pilot_non_sensitive_series_identifier")
    effective_from = decision["governance_bootstrap_effective_from"]
    if not isinstance(effective_from, str) or effective_from < MIN_EFFECTIVE_FROM:
        raise SystemExit(f"FAIL: governance_bootstrap_effective_from must be {MIN_EFFECTIVE_FROM} or later")
    if not isinstance(decision["decision_reference"], str) or not decision["decision_reference"].strip():
        raise SystemExit("FAIL: decision_reference must be a non-empty string")
    if not isinstance(decision["decision_acquisition_provenance"], str) or not decision["decision_acquisition_provenance"].strip():
        raise SystemExit("FAIL: decision_acquisition_provenance must be a non-empty string")


def build_a2(selected: dict, decision_reference: str, decision_fingerprint: str, acquisition_provenance: str, effective_from: str) -> dict:
    role_class = selected["accountable_role_class"]
    return {
        "attestation_version": "st1-136-a2/v1",
        "project_scope": PROJECT_SCOPE,
        "target_source_id": TARGET_SOURCE_ID,
        "evidence_item": {
            "tier": "B",
            "status": "SUPPLIED_UNVALIDATED",
            "attestation_kind": "project_controls_accountability",
            "subject_role_class": role_class,
            "asserted_scope": PROJECT_SCOPE,
            "effective_from": effective_from,
            "signed_artifact_reference": decision_reference,
            "signed_artifact_fingerprint": decision_fingerprint,
            "acquisition_provenance": acquisition_provenance,
            "payload": {
                "accountable_role_class": role_class,
                "report_classes": [REPORT_CLASS],
                "permitted_fact_classes": selected["permitted_fact_classes"],
                "prohibited_fact_classes": selected["prohibited_fact_classes"],
                "scope": PROJECT_SCOPE,
                "approval_method": selected["approval_method"],
            },
        },
    }


def build_a3(selected: dict, decision_reference: str, decision_fingerprint: str, acquisition_provenance: str, effective_from: str) -> dict:
    role_class = selected["accountable_role_class"]
    return {
        "attestation_version": "st1-136-a3/v1",
        "project_scope": PROJECT_SCOPE,
        "target_source_id": TARGET_SOURCE_ID,
        "evidence_item": {
            "tier": "B",
            "status": "SUPPLIED_UNVALIDATED",
            "attestation_kind": "controlled_report_definition",
            "subject_role_class": role_class,
            "asserted_scope": PROJECT_SCOPE,
            "effective_from": effective_from,
            "signed_artifact_reference": decision_reference,
            "signed_artifact_fingerprint": decision_fingerprint,
            "acquisition_provenance": acquisition_provenance,
            "payload": {
                "source_report_class": REPORT_CLASS,
                "owning_role_class": role_class,
                "source_location_class": selected["source_location_class"],
                "reporting_period_rule": selected["reporting_period_rule"],
                "document_identifier_convention": selected["document_identifier_convention"],
                "permitted_fact_classes": selected["permitted_fact_classes"],
                "prohibited_inference": selected["prohibited_inference"],
                "scope": PROJECT_SCOPE,
                "approval_method": selected["approval_method"],
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", type=Path, required=True, help="Path to the ST1-140 approved decision JSON")
    parser.add_argument("--base-bundle", type=Path, required=True, help="Path to the ST1-139 partial selected-series bundle")
    parser.add_argument("--output-a2", type=Path, required=True, help="Output path for compiled A2 JSON")
    parser.add_argument("--output-a3", type=Path, required=True, help="Output path for compiled A3 JSON")
    parser.add_argument("--output-supplement", type=Path, required=True, help="Output path for compiled ST1-136 supplement JSON")
    parser.add_argument("--output-bundle", type=Path, required=True, help="Output path for merged selected-series bundle JSON")
    args = parser.parse_args()

    decision = load_json(args.decision)
    validate_decision(decision)
    selected = normalize_value(decision)

    if selected["permitted_fact_classes"] != PERMITTED_FACTS:
        return fail("permitted_fact_classes must preserve the approved LOW-risk set")
    if selected["prohibited_fact_classes"] != PROHIBITED_FACTS:
        return fail("prohibited_fact_classes must preserve the approved HIGH-risk set")
    if selected["prohibited_inference"] != PROHIBITED_INFERENCE:
        return fail("prohibited_inference must preserve the approved boundary set")
    if selected["reporting_period_rule"] != REPORTING_PERIOD_RULE:
        return fail("reporting_period_rule must preserve the approved reporting-time rule")

    decision_fingerprint = sha256_path(args.decision)
    decision_reference = decision["decision_reference"]
    acquisition_provenance = decision["decision_acquisition_provenance"]
    effective_from = decision["governance_bootstrap_effective_from"]

    a2 = build_a2(selected, decision_reference, decision_fingerprint, acquisition_provenance, effective_from)
    a3 = build_a3(selected, decision_reference, decision_fingerprint, acquisition_provenance, effective_from)

    args.output_a2.write_text(json.dumps(a2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_a3.write_text(json.dumps(a3, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    supplement = {
        "supplement_version": "st1-136/v1",
        "project_scope": PROJECT_SCOPE,
        "target_source_id": TARGET_SOURCE_ID,
        "series_scope": {
            "stable_source_series_identifier": decision["selected_series_identifier"],
            "stable_source_series_identifier_kind": decision["selected_series_identifier_kind"],
        },
        "evidence_items": {
            "A2": a2["evidence_item"],
            "A3": a3["evidence_item"],
        },
        "source_registration": {
            "non_sensitive_location_class": selected["source_location_class"],
            "owning_role_class": selected["accountable_role_class"],
            "evidence_reference": decision_reference,
        },
    }
    args.output_supplement.write_text(json.dumps(supplement, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    base = load_json(args.base_bundle)
    if base.get("source_registration", {}).get("source_id") != TARGET_SOURCE_ID:
        return fail("base bundle is not the expected selected-series partial bundle")
    base["evidence_items"]["A2"] = a2["evidence_item"]
    base["evidence_items"]["A3"] = a3["evidence_item"]
    base["source_registration"]["non_sensitive_location_class"] = selected["source_location_class"]
    base["source_registration"]["owning_role_class"] = selected["accountable_role_class"]
    base["source_registration"]["evidence_reference"] = decision_reference
    base["series_scope"]["stable_source_series_identifier"] = decision["selected_series_identifier"]
    base["series_scope"]["stable_source_series_identifier_kind"] = decision["selected_series_identifier_kind"]
    args.output_bundle.write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "task_id": "ST1-140",
                "compile_result": "OK",
                "decision_path": str(args.decision),
                "decision_fingerprint": decision_fingerprint,
                "approval_mode": decision["approval_mode"],
                "effective_from": effective_from,
                "selected_target_source_id": TARGET_SOURCE_ID,
                "outputs": {
                    "a2": str(args.output_a2),
                    "a3": str(args.output_a3),
                    "supplement": str(args.output_supplement),
                    "bundle": str(args.output_bundle),
                },
                "boundary": {
                    "prospective_only": True,
                    "historical_authority_backfilled": False,
                    "real_delegation_activation": False,
                    "real_source_registration": False,
                    "real_certification": False,
                },
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
