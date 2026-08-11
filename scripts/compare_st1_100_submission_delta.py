#!/usr/bin/env python3
"""Compare baseline vs submitted selected-class evidence for reentry relevance.

This comparator is deterministic, local-only, and non-mutating. It reports
only the exact bundle/native artifact deltas that can truthfully affect
selected-class reentry and first-real readiness.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REHEARSAL_SCRIPT = ROOT / "scripts" / "run_st1_099_first_real_attempt_rehearsal.py"
HANDOFF_SCRIPT = ROOT / "scripts" / "compile_st1_094_external_evidence_to_dossier_handoff.py"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_json(script: Path, args: list[str]) -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    items: dict[str, Any] = {}
    if isinstance(value, dict):
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else key
            items.update(flatten(value[key], path))
    elif isinstance(value, list):
        items[prefix] = value
    else:
        items[prefix] = value
    return items


def normalize_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    evidence = bundle["evidence_items"]
    return {
        "candidate_class_id": bundle["candidate_class_id"],
        "project_scope": bundle["project_scope"],
        "evidence_items": {
            "A1": {
                "signed_artifact_fingerprint": evidence["A1"]["signed_artifact_fingerprint"],
                "subject_role_class": evidence["A1"]["subject_role_class"],
                "payload": {
                    "governance_role_class": evidence["A1"]["payload"]["governance_role_class"],
                    "authority_basis": evidence["A1"]["payload"]["authority_basis"],
                    "scope": evidence["A1"]["payload"]["scope"],
                    "approval_method": evidence["A1"]["payload"]["approval_method"],
                },
            },
            "A2": {
                "signed_artifact_fingerprint": evidence["A2"]["signed_artifact_fingerprint"],
                "subject_role_class": evidence["A2"]["subject_role_class"],
                "payload": {
                    "accountable_role_class": evidence["A2"]["payload"]["accountable_role_class"],
                    "report_classes": evidence["A2"]["payload"]["report_classes"],
                    "permitted_fact_classes": evidence["A2"]["payload"]["permitted_fact_classes"],
                    "prohibited_fact_classes": evidence["A2"]["payload"]["prohibited_fact_classes"],
                    "scope": evidence["A2"]["payload"]["scope"],
                    "approval_method": evidence["A2"]["payload"]["approval_method"],
                },
            },
            "A3": {
                "signed_artifact_fingerprint": evidence["A3"]["signed_artifact_fingerprint"],
                "subject_role_class": evidence["A3"]["subject_role_class"],
                "payload": {
                    "source_report_class": evidence["A3"]["payload"]["source_report_class"],
                    "owning_role_class": evidence["A3"]["payload"]["owning_role_class"],
                    "source_location_class": evidence["A3"]["payload"]["source_location_class"],
                    "reporting_period_rule": evidence["A3"]["payload"]["reporting_period_rule"],
                    "document_identifier_convention": evidence["A3"]["payload"]["document_identifier_convention"],
                    "permitted_fact_classes": evidence["A3"]["payload"]["permitted_fact_classes"],
                    "prohibited_inference": evidence["A3"]["payload"]["prohibited_inference"],
                    "scope": evidence["A3"]["payload"]["scope"],
                    "approval_method": evidence["A3"]["payload"]["approval_method"],
                },
            },
        },
        "source_registration": bundle["source_registration"],
    }


def normalize_native(native: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_class_id": native["candidate_class_id"],
        "project_scope": native["project_scope"],
        "source_registration": {
            "source_id": native["source_registration"]["source_id"],
            "report_class": native["source_registration"]["report_class"],
            "authority_state": native["source_registration"]["authority_state"],
            "evidence_reference": native["source_registration"]["evidence_reference"],
        },
        "acquisition": {
            "source_reference": native["acquisition"]["source_reference"],
            "acquisition_method": native["acquisition"]["acquisition_method"],
            "original_fingerprint": native["acquisition"]["original_fingerprint"],
            "media_type": native["acquisition"]["media_type"],
            "read_only": native["acquisition"]["read_only"],
        },
        "transformation": {
            "transformation_type": native["transformation"]["transformation_type"],
            "input_fingerprint": native["transformation"]["input_fingerprint"],
            "output_fingerprint": native["transformation"]["output_fingerprint"],
            "deterministic": native["transformation"]["deterministic"],
            "lineage_complete": native["transformation"]["lineage_complete"],
        },
        "business_time": {
            "resolved": native["business_time"]["resolved"],
            "resolution_source": native["business_time"]["resolution_source"],
            "report_period_value": native["business_time"]["report_period_value"],
            "disallowed_substitutes_used": native["business_time"]["disallowed_substitutes_used"],
        },
        "policy_context": native["policy_context"],
        "independent_verification": native["independent_verification"],
    }


def build_surface(bundle_path: Path, native_path: Path, expected_fingerprint: str, operator_inputs: Path, receipt: Path, batch: Path) -> dict[str, Any]:
    bundle = load_json(bundle_path)
    native = load_json(native_path)
    handoff = run_json(HANDOFF_SCRIPT, ["--bundle", str(bundle_path), "--native-record", str(native_path)])
    rehearsal = run_json(
        REHEARSAL_SCRIPT,
        [
            "--expected-fingerprint", expected_fingerprint,
            "--bundle", str(bundle_path),
            "--native-record", str(native_path),
            "--operator-inputs", str(operator_inputs),
            "--receipt", str(receipt),
            "--batch", str(batch),
        ],
    )
    return {
        "bundle": normalize_bundle(bundle),
        "native": normalize_native(native),
        "handoff": {
            "handoff_status": handoff.get("handoff_status"),
            "blocking_reasons": handoff.get("blocking_reasons", {}),
            "verified_external_evidence_summary": handoff.get("verified_external_evidence_summary"),
            "native_evidence_chain": handoff.get("native_evidence_chain") or handoff.get("dossier_ready_inputs", {}).get("native_evidence_chain"),
            "receipt_contract_expectations": handoff.get("dossier_ready_inputs", {}).get("receipt_contract_expectations"),
        },
        "rehearsal": {
            "rehearsal_result": rehearsal["rehearsal_result"],
            "readiness_status": rehearsal["readiness_status"],
            "next_action": rehearsal["next_action"],
            "blocking_reasons": rehearsal["blocking_reasons"],
            "resume_requirements": rehearsal["resume_requirements"],
        },
    }


def compare_flattened(baseline: dict[str, Any], submission: dict[str, Any]) -> list[dict[str, Any]]:
    baseline_flat = flatten(baseline)
    submission_flat = flatten(submission)
    changed_paths = sorted(set(baseline_flat) | set(submission_flat))
    changes: list[dict[str, Any]] = []
    for path in changed_paths:
        baseline_value = baseline_flat.get(path)
        submission_value = submission_flat.get(path)
        if baseline_value != submission_value:
            changes.append(
                {
                    "field_path": path,
                    "baseline_value": baseline_value,
                    "submission_value": submission_value,
                }
            )
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-fingerprint", required=True, help="Expected parked external-gate fingerprint")
    parser.add_argument("--baseline-bundle", type=Path, required=True, help="Baseline ST1-078 bundle JSON")
    parser.add_argument("--baseline-native-record", type=Path, required=True, help="Baseline ST1-083/ST1-094 native-record JSON")
    parser.add_argument("--submission-bundle", type=Path, required=True, help="Submitted ST1-078 bundle JSON")
    parser.add_argument("--submission-native-record", type=Path, required=True, help="Submitted native-record JSON")
    parser.add_argument("--operator-inputs", type=Path, required=True, help="Path to ST1-088 operator-input JSON")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to ST1-089 receipt JSON")
    parser.add_argument("--batch", type=Path, required=True, help="Path to ST1-090 batch JSON")
    args = parser.parse_args()

    baseline_surface = build_surface(
        args.baseline_bundle,
        args.baseline_native_record,
        args.expected_fingerprint,
        args.operator_inputs,
        args.receipt,
        args.batch,
    )
    submission_surface = build_surface(
        args.submission_bundle,
        args.submission_native_record,
        args.expected_fingerprint,
        args.operator_inputs,
        args.receipt,
        args.batch,
    )

    changed_fields = compare_flattened(baseline_surface, submission_surface)
    output = {
        "schema_version": "st1-100-selected-class-submission-delta-v1",
        "candidate_class_id": baseline_surface["bundle"]["candidate_class_id"],
        "project_scope": baseline_surface["bundle"]["project_scope"],
        "delta_result": "CHANGED_BASELINE_RELEVANT_INPUTS" if changed_fields else "UNCHANGED_BASELINE_RELEVANT_INPUTS",
        "baseline_rehearsal_result": baseline_surface["rehearsal"]["rehearsal_result"],
        "submission_rehearsal_result": submission_surface["rehearsal"]["rehearsal_result"],
        "baseline_next_action": baseline_surface["rehearsal"]["next_action"],
        "submission_next_action": submission_surface["rehearsal"]["next_action"],
        "reentry_relevant_changed_fields": changed_fields,
        "reopen_recommended": bool(changed_fields),
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
