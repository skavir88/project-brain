#!/usr/bin/env python3
"""Compile the truthful first-real policy_automatic target summary.

This script is local-only. It reconciles the selected recurring workbook class
with already approved runtime-local evidence and explicitly excludes ST1-061 as
the success target.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"


def load_runtime(name: str) -> dict:
    return json.loads((RUNTIME / name).read_text(encoding="utf-8"))


def load_repo(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    mrp_review = load_runtime("st1-046-mrp-human-review.json")
    mrp_structure = load_runtime("st1-046-mrp-structure.json")
    st1_075 = load_repo("evidence/sanitized/2026-08-11-st1-075-real-candidate-gap.json")
    st1_076 = load_repo("evidence/sanitized/2026-08-11-st1-076-candidate-bundle.json")
    st1_121 = load_repo("evidence/sanitized/2026-08-11-st1-121-limited-pilot-bootstrap.json")

    target_source_alias = mrp_review["source_alias"]
    target_document = None
    for doc in mrp_structure["documents"]:
        if doc.get("source_alias") == target_source_alias:
            target_document = doc
            break
    if target_document is None:
        raise SystemExit("selected MRP review source alias not found in runtime structure")

    output = {
        "task_id": "ST1-122",
        "date": "2026-08-11",
        "objective_alignment": {
            "st1_061_must_remain_human_required": True,
            "st1_061_not_success_target": True,
            "selected_class_retained": st1_075["selected_candidate_class"],
        },
        "first_real_policy_automatic_target": {
            "candidate_class": st1_075["selected_candidate_class"],
            "series_source_id": "maroon_project_controls_progress_workbook_series",
            "representative_real_candidate": {
                "selection_family_alias": "st1-046-c6b4746986c7bfd3",
                "source_alias": target_source_alias,
                "filename": target_document["filename"],
                "extension": target_document["extension"],
                "indexed_size_bytes": target_document["indexed_size_bytes"],
                "metadata_fingerprint": target_document["metadata_fingerprint"],
                "reporting_period_from_content": mrp_review["reporting_period"],
                "provenance_mode": "sheet_cell",
            },
        },
        "why_this_is_the_success_target": [
            "already-authorized recurring workbook class from the Maroon pilot",
            "deterministic spreadsheet structure with workbook/sheet/cell provenance",
            "explicit reporting period available from document content",
            "LOW-risk reported plan/actual/progress observations can be isolated",
            "does not require certifying payment, claims, delay entitlement, current executive status, or reliance",
        ],
        "why_st1_061_is_not_the_success_target": [
            "ST1-061 already truthfully reached a native human_required hard stop",
            "its persisted missing dimensions are authority_not_verified and business_timestamp_missing",
            "the attached objective explicitly requires ST1-061 to remain human_required unless independently resolved",
        ],
        "eligible_fact_classes": st1_076["fixed_permitted_fact_classes"],
        "excluded_fact_classes": st1_076["fixed_prohibited_fact_classes"],
        "business_time_rule": {
            "approved_rule": st1_076["fixed_business_time_rule"],
            "candidate_document_content_reports_period": True,
            "candidate_document_period_value": mrp_review["reporting_period"],
            "filesystem_or_acquisition_time_substitution_allowed": False,
        },
        "minimum_real_governance_objects": {
            "registered_source_identity": {
                "status": "MISSING_REAL_RUNTIME_OBJECT",
                "target_source_id": "maroon_project_controls_progress_workbook_series",
                "source_type": "project_controls_progress_workbook_series",
            },
            "document_data_class": {
                "status": "SELECTED",
                "value": "project_controls_progress_workbook",
            },
            "allowed_fact_classes": {
                "status": "DEFINED",
                "value": st1_076["fixed_permitted_fact_classes"],
            },
            "prohibited_fact_classes": {
                "status": "DEFINED",
                "value": st1_076["fixed_prohibited_fact_classes"],
            },
            "business_time_resolution_rule": {
                "status": "DEFINED_NOT_CONTROLLED",
                "value": st1_076["fixed_business_time_rule"],
            },
            "native_acquisition_requirements": {
                "status": "DEFINED",
                "read_only": True,
                "sha256_required": True,
                "deterministic_transformation_required": True,
            },
            "integrity_provenance_requirements": {
                "status": "DEFINED",
                "sheet_cell_provenance": True,
                "lineage_complete_required": True,
            },
            "risk_tier": {
                "status": "DEFINED",
                "value": "LOW",
            },
            "policy_id_version": {
                "status": "DEFINED",
                "policy_id": "project-controls-progress-low-risk",
                "policy_version": "v1",
            },
            "authority_requirement": {
                "status": "UNRESOLVED",
                "value": "exact_scope_active_governance_and_source_control_required",
            },
        },
        "exact_governance_gap": {
            "A1_governance_authority_confirmation": "MISSING",
            "A2_project_controls_accountability_confirmation": "MISSING",
            "A3_controlled_report_definition_confirmation": "PARTIAL",
            "real_source_registration_inputs": "MISSING",
            "active_real_delegation": "MISSING",
        },
        "smallest_reusable_business_ask": {
            "kind": "class_scoped_governance_and_report_definition_bundle",
            "must_answer": [
                "چه role سازمانی مجاز به approve کردن pilot governance این کلاس گزارش است؟",
                "چه role سازمانی مسئول رسمی recurring Project Controls progress workbook/report class برای پروژه Maroon است؟",
                "برای این report/workbook class، reporting period رسمی دقیقاً در کدام header/field تعریف می‌شود و convention انتشار/کنترل آن چیست؟",
                "شناسه پایدار non-sensitive برای source/reporting system یا location class این series چیست؟",
            ],
        },
        "next_runtime_path_after_real_evidence": [
            "register real source/system",
            "verify source control",
            "native read-only acquisition",
            "capture original fingerprint",
            "capture deterministic transformation lineage",
            "resolve business time from approved workbook rule",
            "evaluate authority",
            "evaluate risk",
            "write policy decision",
            "hard stop before certification",
        ],
        "boundaries": {
            "new_source_boundary": False,
            "st1_061_modified": False,
            "real_delegation_activated": False,
            "real_certification_changed": False,
            "automatic_certification": False,
            "ck_qdrant_dify_touched": False,
        },
        "references": {
            "st1_075": "evidence/sanitized/2026-08-11-st1-075-real-candidate-gap.json",
            "st1_076": "evidence/sanitized/2026-08-11-st1-076-candidate-bundle.json",
            "st1_121": "evidence/sanitized/2026-08-11-st1-121-limited-pilot-bootstrap.json",
            "runtime_mrp_review": "st1-046-mrp-human-review.json",
            "runtime_mrp_structure": "st1-046-mrp-structure.json",
        },
    }

    out_path = ROOT / "evidence" / "sanitized" / "2026-08-11-st1-122-first-real-policy-target.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
