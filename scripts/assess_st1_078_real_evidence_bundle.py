#!/usr/bin/env python3
"""Assess ST1-078 bundle readiness without activating or verifying authority.

This assessor sits above the structural validator. It classifies each required
section into:

- MISSING
- PARTIAL
- REJECTED

It never returns VERIFIED because signer identity, source ownership/control,
and controlled evidence verification are intentionally outside the local-only
assessment boundary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_st1_078_real_evidence_bundle import (
    CANDIDATE_CLASS_ID,
    EXPECTED_EVIDENCE_ITEMS,
    PROJECT_SCOPE,
    collect_validation_errors,
    load_bundle,
)


REQUIRED_INPUT = "REQUIRED_INPUT"


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


def section_errors(errors: list[str], prefix: str) -> list[str]:
    return [item for item in errors if item.startswith(prefix)]


def classify_section(payload: object, errors: list[str], prefix: str) -> tuple[str, list[str]]:
    if payload is None:
        return "MISSING", [f"{prefix} not supplied"]
    if has_required_input(payload):
        return "MISSING", [f"{prefix} still contains REQUIRED_INPUT placeholder(s)"]
    scoped_errors = section_errors(errors, prefix)
    if scoped_errors:
        return "REJECTED", scoped_errors
    return "PARTIAL", [f"{prefix} is structurally complete but still pending independent verification"]


def classify_top_level(bundle: dict, errors: list[str]) -> tuple[str, list[str]]:
    blockers: list[str] = []
    if bundle.get("candidate_class_id") != CANDIDATE_CLASS_ID:
        blockers.append("candidate_class_id mismatch")
    if bundle.get("project_scope") != PROJECT_SCOPE:
        blockers.append("project_scope mismatch")
    for flag in (
        "activation_request",
        "automatic_certification_requested",
        "currentness_override_requested",
        "reliance_override_requested",
    ):
        if bundle.get(flag) is not False:
            blockers.append(f"{flag} must remain false")
    if blockers:
        return "REJECTED", blockers
    return "PARTIAL", ["top-level bundle scope and control flags are structurally acceptable"]


def readiness_from_statuses(statuses: dict[str, str]) -> str:
    values = list(statuses.values())
    if any(value == "REJECTED" for value in values):
        return "WAITING_FOR_SCOPE_OR_POLICY_CORRECTION"
    if any(value == "MISSING" for value in values):
        return "WAITING_FOR_EXTERNAL_EVIDENCE"
    return "PENDING_INDEPENDENT_VERIFICATION"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the intake bundle JSON file")
    args = parser.parse_args()

    bundle = load_bundle(args.bundle)
    errors = collect_validation_errors(bundle)

    evidence_items = bundle.get("evidence_items") if isinstance(bundle.get("evidence_items"), dict) else {}
    statuses: dict[str, str] = {}
    details: dict[str, list[str]] = {}

    top_status, top_details = classify_top_level(bundle, errors)
    statuses["bundle"] = top_status
    details["bundle"] = top_details

    for evidence_id in sorted(EXPECTED_EVIDENCE_ITEMS):
        status, section_detail = classify_section(evidence_items.get(evidence_id), errors, f"evidence_items.{evidence_id}")
        statuses[evidence_id] = status
        details[evidence_id] = section_detail

    source_status, source_details = classify_section(bundle.get("source_registration"), errors, "source_registration")
    statuses["source_registration"] = source_status
    details["source_registration"] = source_details

    output = {
        "candidate_class_id": CANDIDATE_CLASS_ID,
        "project_scope": PROJECT_SCOPE,
        "structural_validation_passed": len(errors) == 0,
        "activation_readiness": readiness_from_statuses(statuses),
        "section_statuses": statuses,
        "section_details": details,
        "verified_sections": [],
        "boundary": {
            "real_delegation_activation": False,
            "real_certification": False,
            "real_source_registration": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
