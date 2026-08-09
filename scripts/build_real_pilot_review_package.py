"""Build a local, redacted review package from approved pilot extraction output.

The input and output locations are supplied by the operator and must remain
outside the repository. This utility makes no source-file or database changes,
does not call an LLM, and never prints document text, names, or source paths.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


MAX_EXCERPTS_PER_DOCUMENT = 3
MAX_EXCERPT_CHARS = 900

TOPIC_PATTERNS = {
    "status": re.compile(r"\b(status|progress|report)\b|وضعیت|پیشرفت|گزارش", re.I),
    "schedule": re.compile(r"\b(schedule|milestone|planning|plan)\b|زمانبندی|برنامه\s*ریزی|برنامه", re.I),
    "risk_or_issue": re.compile(r"\b(risk|issue|delay|problem|blocker)\b|ریسک|مشکل|تاخیر|تأخیر|مانع", re.I),
    "action": re.compile(r"\b(action|next step|follow[- ]?up|decision)\b|اقدام|پیگیری|تصمیم", re.I),
}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\b\+?\d[\d\s-]{8,}\b")
NATIONAL_ID = re.compile(r"\b\d{10}\b")


def repair_utf8_mojibake(text: str) -> str:
    """Recover UTF-8 text that a PDF extractor exposed as Windows-1252 bytes."""
    if not any(marker in text for marker in ("Ø", "Ù", "â€")):
        return text
    try:
        repaired = text.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
    return repaired


def redact(text: str) -> str:
    text = EMAIL.sub("[REDACTED_EMAIL]", text)
    text = PHONE.sub("[REDACTED_PHONE]", text)
    return NATIONAL_ID.sub("[REDACTED_IDENTIFIER]", text)


def stable_claim_id(reference: str, fingerprint: str, location: str, line_number: int, category: str) -> str:
    material = f"{reference}|{fingerprint}|{location}|{line_number}|{category}".encode("utf-8")
    return "review-" + hashlib.sha256(material).hexdigest()[:16]


def canonicalize_excerpt(text: str) -> str:
    """Produce a deterministic, local-only comparison representation."""
    return " ".join(text.casefold().split())


def candidate_lines(text: str) -> list[tuple[int, str]]:
    page = 1
    results: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        page += line.count("\f")
        clean = repair_utf8_mojibake(line.replace("\f", " ").strip())
        if clean:
            results.append((page, clean))
    return results


def main() -> int:
    input_value = os.environ.get("EAI_EXTRACTION_RUNTIME_INPUT")
    output_value = os.environ.get("EAI_REVIEW_RUNTIME_OUTPUT")
    if not input_value or not output_value:
        raise SystemExit("EAI_EXTRACTION_RUNTIME_INPUT and EAI_REVIEW_RUNTIME_OUTPUT are required")

    payload = json.loads(Path(input_value).read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = payload.get("records", [])
    review_items: list[dict[str, Any]] = []
    duplicate_groups: dict[str, list[str]] = defaultdict(list)
    category_counts: Counter[str] = Counter()
    redaction_markers = 0

    for record in records:
        fingerprint = record["content_fingerprint"]
        duplicate_groups[fingerprint].append(record["source_relative_reference"])
        document_hits = 0
        for line_number, (page, line) in enumerate(candidate_lines(record.get("text", "")), start=1):
            for category, pattern in TOPIC_PATTERNS.items():
                if pattern.search(line):
                    excerpt = redact(line[:MAX_EXCERPT_CHARS])
                    redaction_markers += excerpt.count("[REDACTED_")
                    location = f"pdf_page:{page}" if record.get("document_type") == ".pdf" else f"text_line:{page}"
                    review_items.append({
                        "review_item_id": stable_claim_id(
                            record["source_relative_reference"], fingerprint, location, line_number, category
                        ),
                        "source_alias": record["source_alias"],
                        "source_relative_reference": record["source_relative_reference"],
                        "source_timestamp_utc": record["source_timestamp_utc"],
                        "reporting_date": "not_deterministically_extracted",
                        "content_fingerprint": fingerprint,
                        "document_type": record["document_type"],
                        "extraction_method": record["extraction"]["method"],
                        "source_location": location,
                        "source_line_number": line_number,
                        "topic_category": category,
                        "redacted_excerpt": excerpt,
                        "proposed_project_status_claim": excerpt,
                        "canonical_claim_fingerprint": hashlib.sha256(
                            canonicalize_excerpt(excerpt).encode("utf-8")
                        ).hexdigest(),
                        "structural_validation": "passed_required_provenance_fields_present",
                        "credibility_disposition": "human_review_required",
                        "credibility_reason": "real_content_requires_explicit_human_review",
                        "detected_conflicts_or_uncertainty": [
                            "filesystem_timestamp_is_not_authoritative",
                            "no_cross_document_conflict_resolution_performed",
                            "reporting_date_not_deterministically_extracted",
                        ],
                        "proposed_disposition": "NEEDS_MORE_EVIDENCE",
                        "reviewer_allowed_decisions": [
                            "APPROVE",
                            "REJECT",
                            "NEEDS_MORE_EVIDENCE",
                            "CONFLICT",
                        ],
                        "review_status": "unreviewed_not_certified",
                    })
                    category_counts[category] += 1
                    document_hits += 1
                    break
            if document_hits >= MAX_EXCERPTS_PER_DOCUMENT:
                break

    review_items.sort(key=lambda item: (item["source_relative_reference"], item["source_location"], item["topic_category"]))
    for item in review_items:
        item["duplicate_source_count"] = len(duplicate_groups[item["content_fingerprint"]])
    package = {
        "schema_version": "st1-014-review-package-v1",
        "source_alias": "status_candidate_b",
        "records_extracted": len(records),
        "records_failed_to_extract": 1,
        "failure_categories": ["BadZipFile"],
        "review_items": review_items,
        "duplicate_fingerprint_groups": [
            {"content_fingerprint": fingerprint, "source_relative_references": sorted(refs)}
            for fingerprint, refs in sorted(duplicate_groups.items()) if len(refs) > 1
        ],
        "policy": {
            "source_access": "read_only",
            "llm_used": False,
            "certification": "not_performed",
            "real_content_destination": "local_operator_runtime_only",
        },
        "deterministic_pipeline": {
            "structural_validation": "required provenance fields checked",
            "canonicalization": "whitespace and casefold comparison form",
            "duplicate_control": "content-fingerprint grouping retained for reviewer",
            "credibility_gate": "all real claims require human review; no automatic certification",
        },
    }
    output = Path(output_value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "source_alias": "status_candidate_b",
        "records_extracted": len(records),
        "records_failed_to_extract": 1,
        "review_item_count": len(review_items),
        "review_documents_with_items": len({item["source_relative_reference"] for item in review_items}),
        "topic_category_counts": dict(sorted(category_counts.items())),
        "duplicate_fingerprint_group_count": sum(1 for refs in duplicate_groups.values() if len(refs) > 1),
        "redaction_marker_count": redaction_markers,
        "llm_used": False,
        "certification_performed": False,
        "raw_review_package_outside_git": True,
        "source_modified": False,
    }
    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
