"""Create local-only substantive review candidates from approved PDF extraction.

This utility is deterministic: it does not invoke an AI model, certify records,
or write to a platform service.  Raw excerpts and relative source references are
written only to a caller-supplied runtime path outside the repository.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any


PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\b\+?\d[\d\s-]{8,}\b")
NATIONAL_ID = re.compile(r"\b\d{10}\b")
DATE = re.compile(r"\b(?:13\d{2}|14\d{2}|20\d{2})[/-]\d{1,2}[/-]\d{1,2}\b|\b\d{1,2}[/-]\d{1,2}[/-](?:13\d{2}|14\d{2}|20\d{2})\b")

CATEGORIES: list[tuple[str, re.Pattern[str], bool]] = [
    (
        "financial_progress",
        re.compile(r"مجموع\s*کارکرد|جمع\s*کل\s*کارکرد|مبلغ|(?<!\S)ریال(?!\S)|(?<!\S)تومان(?!\S)|دریافت|پرداخت|financial", re.I),
        True,
    ),
    ("physical_progress", re.compile(r"پیشرفت|physical\s+progress", re.I), True),
    ("schedule_or_milestone", re.compile(r"زمانبندی|برنامه|شروع|پایان|تمدید|مدت|schedule|baseline|milestone", re.I), True),
    ("delay", re.compile(r"تأخیر|تاخیر|delay", re.I), False),
    ("risk_or_issue", re.compile(r"ریسک|مشکل|مانع|risk|issue", re.I), False),
    ("action_or_decision", re.compile(r"اقدام|تصمیم|پیگیری|action|decision", re.I), False),
]


def repair_utf8_mojibake(text: str) -> str:
    if not any(marker in text for marker in ("Ø", "Ù", "â€")):
        return text
    try:
        return text.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def redact(text: str) -> str:
    text = EMAIL.sub("[REDACTED_EMAIL]", text)
    text = PHONE.sub("[REDACTED_PHONE]", text)
    return NATIONAL_ID.sub("[REDACTED_IDENTIFIER]", text)


def normalized(text: str) -> str:
    return " ".join(text.translate(PERSIAN_DIGITS).casefold().split())


def claim_id(reference: str, fingerprint: str, page: int, line: int, category: str, excerpt: str) -> str:
    material = "|".join((reference, fingerprint, str(page), str(line), category, normalized(excerpt)))
    return "substantive-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def text_lines(page: str) -> list[str]:
    return [repair_utf8_mojibake(line).strip() for line in page.splitlines() if repair_utf8_mojibake(line).strip()]


def date_evidence(text: str) -> str | None:
    found = DATE.search(text.translate(PERSIAN_DIGITS))
    return found.group(0) if found else None


def build_candidates(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Counter[str], int]:
    candidates: list[dict[str, Any]] = []
    category_counts: Counter[str] = Counter()
    source_pages_with_text = 0
    seen: set[tuple[str, str, str]] = set()

    for record in records:
        if record.get("document_type") != ".pdf":
            continue
        for page_number, page in enumerate(record.get("text", "").split("\f"), start=1):
            lines = text_lines(page)
            if not lines:
                continue
            source_pages_with_text += 1
            for index, line in enumerate(lines):
                translated = line.translate(PERSIAN_DIGITS)
                has_number_or_date = bool(re.search(r"\d", translated) or DATE.search(translated))
                for category, pattern, needs_number in CATEGORIES:
                    if not pattern.search(line):
                        continue
                    if needs_number and not has_number_or_date:
                        continue
                    if not needs_number and len(normalized(line)) < 18:
                        continue
                    context = " ".join(lines[max(0, index - 1):min(len(lines), index + 2)])[:1100]
                    excerpt = redact(context)
                    if category == "financial_progress":
                        semantic_material = ",".join(
                            sorted(set(re.findall(r"\d+(?:,\d{3})*", excerpt.translate(PERSIAN_DIGITS))))
                        )
                    else:
                        semantic_material = normalized(excerpt)
                    dedupe_key = (record["content_fingerprint"], category, semantic_material)
                    if dedupe_key in seen:
                        continue
                    seen.add(dedupe_key)
                    reported = date_evidence(context)
                    candidate = {
                        "candidate_id": claim_id(
                            record["source_relative_reference"], record["content_fingerprint"], page_number,
                            index + 1, category, excerpt,
                        ),
                        "proposed_claim": excerpt,
                        "claim_category": category,
                        "reporting_or_effective_date": reported or "not_deterministically_extracted",
                        "source_alias": record["source_alias"],
                        "source_relative_reference": record["source_relative_reference"],
                        "source_timestamp_utc": record["source_timestamp_utc"],
                        "source_timestamp_authority": "not_authoritative",
                        "content_fingerprint": record["content_fingerprint"],
                        "extraction_method": record["extraction"]["method"],
                        "source_location": f"pdf_page:{page_number}; lines:{max(1,index)}-{min(len(lines),index + 2)}",
                        "minimum_supporting_evidence": excerpt,
                        "uncertainty_or_conflict": [
                            "deterministic_text_extraction_only",
                            "cross_document_conflict_resolution_not_performed",
                            "real_claim_requires_explicit_human_review",
                        ],
                        "reason_for_review": "real_substantive_evidence_requires_explicit_human_review_before_certification",
                        "proposed_disposition": "NEEDS_MORE_EVIDENCE",
                        "review_status": "human_review_required_unreviewed_not_certified",
                    }
                    candidates.append(candidate)
                    category_counts[category] += 1
    candidates.sort(key=lambda item: (item["source_relative_reference"], item["source_location"], item["claim_category"]))
    return candidates[:15], category_counts, source_pages_with_text


def main() -> int:
    input_value = os.environ.get("EAI_EXTRACTION_RUNTIME_INPUT")
    output_value = os.environ.get("EAI_SUBSTANTIVE_REVIEW_RUNTIME_OUTPUT")
    if not input_value or not output_value:
        raise SystemExit("EAI_EXTRACTION_RUNTIME_INPUT and EAI_SUBSTANTIVE_REVIEW_RUNTIME_OUTPUT are required")
    payload = json.loads(Path(input_value).read_text(encoding="utf-8"))
    candidates, categories, text_pages = build_candidates(payload.get("records", []))
    result: dict[str, Any] = {
        "schema_version": "st1-016-substantive-review-v1",
        "source_alias": "status_candidate_b",
        "scope": {"approved_pdf_document_count": 18, "source_access": "read_only"},
        "candidates": candidates,
        "policy": {
            "llm_used": False,
            "certification_performed": False,
            "real_content_destination": "local_operator_runtime_only",
        },
    }
    output = Path(output_value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "source_alias": "status_candidate_b",
        "approved_pdf_document_count": 18,
        "text_bearing_page_count": text_pages,
        "substantive_candidate_count": len(candidates),
        "candidate_category_counts": dict(sorted(categories.items())),
        "llm_used": False,
        "certification_performed": False,
        "raw_review_package_outside_git": True,
    }
    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
