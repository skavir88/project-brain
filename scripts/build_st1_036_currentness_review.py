#!/usr/bin/env python3
"""Build a local-only, deterministic ST1-036 currentness-review package.

It never calls an AI service. Raw excerpts and source-relative locators are
written only under the local runtime directory; terminal output is aggregate.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import argparse
from collections import Counter
from pathlib import Path


PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
DATE = re.compile(r"(?<!\d)((?:1[34]|20)\d{2})\s*[/.-]\s*(\d{1,2})\s*[/.-]\s*(\d{1,2})(?!\d)")
PERSIAN_TEXTUAL_DATE = re.compile(
    r"(?<!\d)((?:1[34]|20)\d{2})\s+(فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s+(\d{1,2})(?!\d)"
)
CATEGORY_TERMS = {
    "progress": ("پیشرفت", "progress"),
    "plan_actual": ("برنامه", "واقعی", "actual", "plan"),
    "schedule": ("زمانبندی", "برنامه زمان", "schedule", "milestone"),
    "explicit_delay": ("تاخیر", "تأخیر", "delay"),
    "stoppage": ("توقف", "متوقف", "stoppage"),
    "material_procurement": ("مصالح", "خرید", "تامین", "تأمین", "material", "procurement"),
    "engineering": ("طراحی", "مهندسی", "نقشه", "engineering", "design"),
    "issue_risk": ("مشکل", "ریسک", "مانع", "issue", "risk", "constraint"),
    "action_decision": ("اقدام", "تصمیم", "مسئول", "action", "decision"),
    "financial": ("مالی", "هزینه", "پرداخت", "financial", "cost"),
}


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.translate(PERSIAN_DIGITS)).strip()


def categories(text: str) -> list[str]:
    folded = normalize(text).casefold()
    return [name for name, terms in CATEGORY_TERMS.items() if any(term.casefold() in folded for term in terms)]


def dates(text: str) -> list[str]:
    value = normalize(text)
    numeric = ["/".join(match.groups()) for match in DATE.finditer(value)]
    textual = [" ".join(match.groups()) for match in PERSIAN_TEXTUAL_DATE.finditer(value)]
    return numeric + textual


def excerpt(text: str, limit: int = 620) -> str:
    value = normalize(text)
    return value[:limit] + ("…" if len(value) > limit else "")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local-only deterministic currentness review package.")
    parser.add_argument("--input", type=Path, default=runtime("st1-036-extraction.json"))
    parser.add_argument("--output", type=Path, default=runtime("st1-036-human-review-package.json"))
    args = parser.parse_args()
    extraction = json.loads(args.input.read_text(encoding="utf-8"))
    candidates = []
    seen = set()
    document_date_count = 0
    for document in extraction["documents"]:
        all_text = "\n".join(segment.get("text", "") for segment in document["segments"])
        document_dates = dates(all_text)
        if document_dates:
            document_date_count += 1
        for segment in document["segments"]:
            text = segment.get("text", "")
            found_dates = dates(text) or document_dates[:1]
            found_categories = categories(text)
            # Require substantive category evidence plus an internal source date
            # somewhere in the document; titles and isolated numbers cannot qualify.
            if not found_dates or len(found_categories) < 2 or len(normalize(text)) < 80:
                continue
            key = hashlib.sha256((document["sha256"] + "\0" + normalize(text)).encode("utf-8")).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            candidate_id = "review-" + hashlib.sha256((key + segment["location"]).encode("utf-8")).hexdigest()[:16]
            claimed_date = max(found_dates)
            candidates.append({
                "candidate_id": candidate_id,
                "proposed_claim": "Source-attributed status evidence requires Human Review; assess only the literal dated observation in the supporting excerpt.",
                "document_date_candidates": found_dates,
                "latest_detected_internal_date": claimed_date,
                "date_semantics": "Document-content date candidate only; reporting/effective/event/planned-date role requires Human Review.",
                "categories": found_categories,
                "source_alias": "source-" + document["sha256"][:16],
                "provenance": {"source_relative_locator": document["source_relative_locator"], "location": segment["location"], "extraction_method": segment.get("method", "local_structural_parse")},
                "supporting_excerpt": excerpt(text),
                "uncertainty": "Source authority, currentness today, exact date role, supersession, and any relationship between negative variance and delay are unverified.",
                "proposed_disposition": "NEEDS_HUMAN_REVIEW",
            })
    candidates.sort(key=lambda item: (-len(item["categories"]), item["latest_detected_internal_date"], item["candidate_id"]), reverse=True)
    # Keep a small reviewer workload; related pages remain auditable through local provenance.
    candidates = candidates[:15]
    package = {
        "schema_version": "st1-036-local-currentness-review-v1",
        "selection_alias": extraction["selection_alias"],
        "selection_signature": extraction["selection_signature"],
        "document_date_detection": {"documents_with_internal_date_candidates": document_date_count},
        "candidates": candidates,
        "boundaries": {
            "automatic_certification": False,
            "external_model_use": False,
            "platform_persistence": False,
            "filesystem_metadata_promoted_to_fact": False,
        },
    }
    args.output.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "selection_alias": extraction["selection_alias"],
        "document_count": len(extraction["documents"]),
        "documents_with_internal_date_candidates": document_date_count,
        "human_review_candidate_count": len(candidates),
        "category_distribution": dict(sorted(Counter(category for item in candidates for category in item["categories"]).items())),
        "package_written_outside_git": True,
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
