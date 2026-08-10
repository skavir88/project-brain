#!/usr/bin/env python3
"""Validate the non-registerable ST1-067 CEO delegation proposal locally.

The validator never connects to a database and never creates a delegation.
It validates only the fenced JSON object in the proposed decision document.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_TOP_LEVEL = {
    "status",
    "delegation_id",
    "delegating_actor_id",
    "organization",
    "delegated_role",
    "data_domain",
    "source_system_scope",
    "document_data_classes",
    "permitted_fact_classes",
    "prohibited_fact_classes",
    "business_time_rule",
    "inheritance_requirements",
    "risk_tier",
    "policy_version",
    "effective_from",
    "effective_until",
    "revocation_authority_actor_id",
    "delegation_basis_reference",
    "automatic_certification",
    "currentness_state",
    "reliance_state",
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


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_proposal(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if not match:
        fail("machine-readable JSON object not found")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        fail(f"machine-readable JSON is invalid: {exc.msg}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--proposal",
        type=Path,
        default=Path("docs/ST1_067_PROPOSED_CEO_GOVERNANCE_DELEGATION.md"),
    )
    args = parser.parse_args()
    proposal = load_proposal(args.proposal)

    missing = sorted(REQUIRED_TOP_LEVEL - set(proposal))
    if missing:
        fail("missing required fields: " + ", ".join(missing))
    if proposal["status"] != "proposed_for_ceo_review_not_registered":
        fail("proposal must remain non-registerable")
    if proposal["risk_tier"] != "LOW":
        fail("only LOW risk is permitted")
    if proposal["policy_version"] != "project-controls-progress-low-risk/v1":
        fail("unexpected policy version")
    if proposal["automatic_certification"] is not False:
        fail("automatic certification must remain false")
    if proposal["currentness_state"] != "not_assessed":
        fail("currentness must remain not_assessed")
    if proposal["reliance_state"] != "not_eligible":
        fail("reliance must remain not_eligible")
    if set(proposal["permitted_fact_classes"]) != PERMITTED_FACTS:
        fail("permitted facts differ from the approved LOW-risk set")
    if set(proposal["prohibited_fact_classes"]) != PROHIBITED_FACTS:
        fail("prohibited facts differ from the required exclusion set")
    if set(proposal["permitted_fact_classes"]) & set(proposal["prohibited_fact_classes"]):
        fail("permitted and prohibited facts overlap")

    business_time = proposal["business_time_rule"]
    expected_time = {
        "approved_report_header",
        "registered_source_system_period_field",
        "document_control_evidence",
        "accountable_owner_attestation",
    }
    if set(business_time.get("accepted_evidence", [])) != expected_time:
        fail("business-time evidence rule is incomplete")
    if set(business_time.get("disallowed_substitutes", [])) != {
        "filesystem_timestamp",
        "acquisition_timestamp",
    }:
        fail("filesystem/acquisition timestamps must be disallowed")

    inheritance = proposal["inheritance_requirements"]
    required_inheritance = {
        "active_delegation",
        "exact_source_system_match",
        "exact_project_match",
        "exact_document_class_match",
        "exact_fact_class_match",
        "valid_business_period",
        "native_integrity_evidence",
        "complete_provenance",
        "no_conflict",
        "no_revocation_or_supersession",
        "document_control_evidence",
    }
    if not all(inheritance.get(key) is True for key in required_inheritance):
        fail("one or more authority-inheritance controls is not required")
    if inheritance.get("exact_policy_version") != proposal["policy_version"]:
        fail("inheritance policy version does not match proposal policy version")

    print("PASS: ST1-067 proposal is non-registerable, LOW-risk, and policy-consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
