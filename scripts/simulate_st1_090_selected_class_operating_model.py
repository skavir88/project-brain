#!/usr/bin/env python3
"""Simulate selected-class batch routing outcomes for the ST1-066 operating model.

This simulator is deterministic, local-only, and non-mutating. It is intended
to answer how future routine batches in the selected recurring LOW-risk class
would route into:

- policy_automatic
- human_required
- reject_or_quarantine

without upgrading reconstructed historical evidence to native and without
automatic certification.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from validate_st1_078_real_evidence_bundle import CANDIDATE_CLASS_ID, PERMITTED_FACTS, PROJECT_SCOPE


TARGET_POLICY_ID = "project-controls-progress-low-risk"
TARGET_POLICY_VERSION = "v1"


def load_batch(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise SystemExit("batch file must be a JSON object containing a records array")
    return payload["records"]


def evaluate_record(record: dict[str, object]) -> tuple[str, list[str]]:
    reasons: list[str] = []

    if record.get("candidate_class_id") != CANDIDATE_CLASS_ID:
        reasons.append("candidate_class_mismatch")
    if record.get("project_scope") != PROJECT_SCOPE:
        reasons.append("project_scope_mismatch")
    if record.get("exact_scope_match") is not True:
        reasons.append("exact_scope_mismatch")
    if record.get("fact_class") not in PERMITTED_FACTS:
        reasons.append("fact_class_out_of_scope")
    if record.get("risk_tier") != "LOW":
        reasons.append("risk_tier_not_low")
    if record.get("automatic_certification_requested") is True:
        reasons.append("automatic_certification_not_allowed")
    if record.get("integrity_ready") is not True:
        reasons.append("integrity_or_validation_failed")

    if reasons:
        return "reject_or_quarantine", sorted(set(reasons))

    evidence_quality = record.get("evidence_quality")
    if evidence_quality != "native":
        return "human_required", ["missing_native_evidence"]

    if record.get("native_evidence_ready") is not True:
        return "human_required", ["missing_native_evidence"]
    if record.get("governance_ready") is not True:
        return "human_required", ["authority_not_verified"]
    if record.get("business_time_ready") is not True:
        return "human_required", ["business_time_missing"]

    return "policy_automatic", ["all_required_policy_evidence_present"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True, help="Path to the ST1-090 batch JSON file")
    args = parser.parse_args()

    records = load_batch(args.batch)
    outcomes = Counter()
    reasons = Counter()
    evaluated: list[dict[str, object]] = []

    for item in records:
        if not isinstance(item, dict):
            raise SystemExit("each batch record must be a JSON object")
        outcome, reason_codes = evaluate_record(item)
        outcomes[outcome] += 1
        for reason in reason_codes:
            reasons[reason] += 1
        evaluated.append(
            {
                "record_id": item.get("record_id"),
                "source_id": item.get("source_id"),
                "fact_class": item.get("fact_class"),
                "evidence_quality": item.get("evidence_quality"),
                "routing_outcome": outcome,
                "reason_codes": reason_codes,
            }
        )

    policy_count = outcomes.get("policy_automatic", 0)
    human_count = outcomes.get("human_required", 0)
    reject_count = outcomes.get("reject_or_quarantine", 0)
    batch_size = len(evaluated)

    output = {
        "schema_version": "st1-090-selected-class-operating-model-v1",
        "candidate_class_id": CANDIDATE_CLASS_ID,
        "project_scope": PROJECT_SCOPE,
        "policy_context": {
            "policy_id": TARGET_POLICY_ID,
            "policy_version": TARGET_POLICY_VERSION,
            "risk_tier": "LOW",
        },
        "batch_summary": {
            "record_count": batch_size,
            "routing_counts": {
                "policy_automatic": policy_count,
                "human_required": human_count,
                "reject_or_quarantine": reject_count,
            },
            "dominant_reason_codes": dict(reasons),
            "estimated_human_review_reduction": policy_count,
        },
        "human_review_operating_model": {
            "description": "Only human_required exceptions should be presented for Human Review.",
            "future_batch_shape": {
                "N_new_records": batch_size,
                "X_policy_automatic": policy_count,
                "Y_human_review_required": human_count,
                "Z_quarantine": reject_count,
            },
            "review_rule": {
                "review_policy_automatic_individually": False,
                "review_human_required_individually": True,
                "review_quarantine_individually": True,
            },
        },
        "false_positive_safety_checks": {
            "historical_or_reconstructed_not_promoted_to_native": all(
                row["routing_outcome"] != "policy_automatic" for row in evaluated if row["evidence_quality"] != "native"
            ),
            "out_of_scope_fact_classes_not_promoted": all(
                row["routing_outcome"] != "policy_automatic" for row in evaluated if row["fact_class"] not in PERMITTED_FACTS
            ),
            "automatic_certification_not_enabled": True,
        },
        "mutates_real_state": False,
        "evaluated_records": evaluated,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
