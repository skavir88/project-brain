#!/usr/bin/env python3
"""Summarize selected-class submission delta into a business-facing impact view.

This summarizer is deterministic, local-only, and non-mutating. It preserves
the exact changed facts from ST1-100 while presenting only the minimal
business-facing change impact needed for future selected-class submissions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import compare_st1_100_submission_delta as delta_module

ROOT = Path(__file__).resolve().parents[1]


def summarize_changed_facts(changed_fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for item in changed_fields:
        path = item["field_path"]
        if path in {
            "native.transformation.lineage_complete",
            "handoff.handoff_status",
            "rehearsal.rehearsal_result",
            "rehearsal.readiness_status",
            "rehearsal.next_action",
            "handoff.verified_external_evidence_summary.native_record_readiness",
        }:
            summary.append(
                {
                    "field_path": path,
                    "baseline_value": item["baseline_value"],
                    "submission_value": item["submission_value"],
                }
            )
    return summary


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

    baseline_surface = delta_module.build_surface(
        args.baseline_bundle,
        args.baseline_native_record,
        args.expected_fingerprint,
        args.operator_inputs,
        args.receipt,
        args.batch,
    )
    submission_surface = delta_module.build_surface(
        args.submission_bundle,
        args.submission_native_record,
        args.expected_fingerprint,
        args.operator_inputs,
        args.receipt,
        args.batch,
    )
    changed_fields = delta_module.compare_flattened(baseline_surface, submission_surface)
    delta = {
        "candidate_class_id": baseline_surface["bundle"]["candidate_class_id"],
        "project_scope": baseline_surface["bundle"]["project_scope"],
        "delta_result": "CHANGED_BASELINE_RELEVANT_INPUTS" if changed_fields else "UNCHANGED_BASELINE_RELEVANT_INPUTS",
        "baseline_rehearsal_result": baseline_surface["rehearsal"]["rehearsal_result"],
        "submission_rehearsal_result": submission_surface["rehearsal"]["rehearsal_result"],
        "baseline_next_action": baseline_surface["rehearsal"]["next_action"],
        "submission_next_action": submission_surface["rehearsal"]["next_action"],
        "reentry_relevant_changed_fields": changed_fields,
        "reopen_recommended": bool(changed_fields),
    }
    output = {
        "schema_version": "st1-101-selected-class-change-impact-summary-v1",
        "candidate_class_id": delta["candidate_class_id"],
        "project_scope": delta["project_scope"],
        "change_impact_result": (
            "REENTRY_RELEVANT_CHANGE_DETECTED"
            if delta["delta_result"] == "CHANGED_BASELINE_RELEVANT_INPUTS"
            else "NO_REENTRY_RELEVANT_CHANGE"
        ),
        "readiness_transition": {
            "baseline": delta["baseline_rehearsal_result"],
            "submission": delta["submission_rehearsal_result"],
        },
        "next_action_transition": {
            "baseline": delta["baseline_next_action"],
            "submission": delta["submission_next_action"],
        },
        "exact_changed_facts": summarize_changed_facts(changed_fields),
        "changed_fact_count": len(changed_fields),
        "reopen_recommended": delta["reopen_recommended"],
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
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
