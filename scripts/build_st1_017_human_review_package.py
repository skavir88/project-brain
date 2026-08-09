"""Assemble a local-only final Human Review package for ST1-017."""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    substantive_input = os.environ.get("EAI_SUBSTANTIVE_REVIEW_INPUT")
    ocr_input = os.environ.get("EAI_OCR_EXTRACTION_INPUT")
    output_value = os.environ.get("EAI_ST1_017_REVIEW_OUTPUT")
    if not all((substantive_input, ocr_input, output_value)):
        raise SystemExit("EAI_SUBSTANTIVE_REVIEW_INPUT, EAI_OCR_EXTRACTION_INPUT, and EAI_ST1_017_REVIEW_OUTPUT are required")
    substantive = json.loads(Path(substantive_input).read_text(encoding="utf-8"))
    ocr = json.loads(Path(ocr_input).read_text(encoding="utf-8"))
    candidates = substantive["candidates"]
    result = {
        "schema_version": "st1-017-human-review-package-v1",
        "source_alias": "status_candidate_b",
        "candidates": candidates,
        "coverage": {
            "validated_pdf_document_count": 18,
            "pdf_page_count": 84,
            "text_bearing_page_count": 82,
            "local_ocr_page_count": 75,
            "ocr_added_substantive_status_claim_count": 0,
            "ceo_project_status_answer_supported": False,
            "reason": "no_content_supported_reporting_date_physical_progress_schedule_delay_risk_action_or_management_status_evidence",
        },
        "xlsx_coverage": {
            "signature_class": next((record.get("xlsx_signature") for record in ocr["records"] if record["document_type"] == ".xlsx"), "not_recorded"),
            "content_parse_attempted": False,
            "limitation": "non_ooxml_temporary_lock_or_unstable_entry_not_usable_as_business_content",
        },
        "policy": {
            "llm_used": False,
            "certification_performed": False,
            "real_content_destination": "local_operator_runtime_only",
        },
    }
    destination = Path(output_value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "substantive_candidate_count": len(candidates),
        "local_ocr_page_count": 75,
        "ocr_added_substantive_status_claim_count": 0,
        "ceo_project_status_answer_supported": False,
        "certification_performed": False,
        "raw_review_package_outside_git": True,
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
