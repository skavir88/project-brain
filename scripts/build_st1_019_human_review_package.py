#!/usr/bin/env python3
"""Create a local-only, deterministic Human Review package from ST1-019 extraction.

The output holds organizational excerpts and is intentionally kept outside Git.
Repository evidence is an aggregate-only companion produced by this program.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def normalize(text: str) -> str:
    text = text.translate(str.maketrans("كيى٠١٢٣٤٥٦٧٨٩", "کیی0123456789"))
    return re.sub(r"\s+", " ", text).strip()


def redact(text: str) -> str:
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[redacted-email]", text)
    text = re.sub(r"(?<!\d)(?:\+?98|0)?9\d{9}(?!\d)", "[redacted-phone]", text)
    return text


DATE = re.compile(r"\b(?:13|14|20)\d{2}[/-]\d{1,2}[/-]\d{1,2}\b")
NUMBER = re.compile(r"(?<!\d)\d{1,3}(?:[,،]\d{3})*(?:\.\d+)?\s*(?:%|درصد|ریال|تومان)?")
TOPICS = {
    "physical_progress": ("پیشرفت فیزیکی", "physical progress", "درصد پیشرفت"),
    "financial_progress": ("پیشرفت مالی", "صورت وضعیت", "کارکرد", "پرداخت", "دریافت", "مبلغ", "invoice", "cost"),
    "schedule": ("برنامه زمانبندی", "زمانبندی", "schedule", "baseline", "شروع", "پایان", "milestone"),
    "delay_risk_issue": ("تاخیر", "تأخیر", "ریسک", "مشکل", "مانع", "delay", "risk", "issue"),
    "action_decision": ("اقدام", "تصمیم", "مصوبه", "پیگیری", "action", "decision", "approved"),
    "status_statement": ("وضعیت پروژه", "گزارش وضعیت", "project status", "status report", "progress report"),
}


def classify(text: str) -> list[str]:
    folded = normalize(text).casefold()
    return [key for key, words in TOPICS.items() if any(word.casefold() in folded for word in words)]


def substantive(text: str, topics: list[str]) -> bool:
    normalized = normalize(text)
    if len(normalized) < 40 or not topics:
        return False
    # A heading/title or bare figure is insufficient: require a status theme plus
    # a fact-like date, number/unit, or a full contextual sentence.
    has_fact = bool(DATE.search(normalized) or NUMBER.search(normalized))
    # Generic status words require clear report semantics; they must not turn a
    # title, heading, or incidental project reference into a review candidate.
    if topics == ["status_statement"]:
        return has_fact and len(normalized.split()) >= 10
    return has_fact and len(normalized.split()) >= 8


def claim_text(text: str, topic: str) -> str:
    # This is an extractive, not generative, claim: the reviewer sees the exact
    # local source statement rather than an untraceable interpretation.
    return f"Potential {topic} claim extracted verbatim for review: {redact(normalize(text)[:520])}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local-only ST1-019 Human Review package.")
    parser.add_argument("--input", type=Path, default=runtime("st1-019-status-extraction.json"))
    parser.add_argument("--output", type=Path, default=runtime("st1-019-human-review-package.json"))
    parser.add_argument("--sanitized-output", type=Path, default=Path("evidence/sanitized/2026-08-09-st1-019-extraction-review.json"))
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    candidates = []
    seen = set()
    for document in data["documents"]:
        for segment in document["segments"]:
            text = normalize(segment["text"])
            topics = classify(text)
            if not substantive(text, topics):
                continue
            key = hashlib.sha256((document["sha256"] + "|" + normalize(text).casefold()).encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            topic = next((x for x in topics if x != "status_statement"), topics[0])
            dates, values = DATE.findall(text), NUMBER.findall(text)
            candidate_id = "review-" + hashlib.sha256((key + segment["location"]).encode()).hexdigest()[:16]
            candidates.append({
                "candidate_id": candidate_id,
                "proposed_claim": claim_text(text, topic),
                "category": topic,
                "effective_or_reporting_date": dates[0] if dates else "not_deterministically_extracted",
                "value_or_unit": values[0] if values else "not_deterministically_extracted",
                "source_alias": "status_oriented_candidate_1",
                "source_relative_locator": document["source_relative_locator"],
                "location": segment["location"],
                "minimum_supporting_evidence": redact(text[:1200]),
                "uncertainty": "Extracted deterministically from a bounded source; authority, scope, reporting semantics, and factual correctness require human review.",
                "conflicting_evidence": [],
                "reason_human_review_required": "Real organizational information cannot be certified automatically; extracted context may be incomplete.",
                "proposed_disposition": "human_review_required",
                "fingerprint": key,
            })
    # Prefer candidates with dates, numbers, and richer contextual excerpts.
    candidates.sort(key=lambda x: (x["effective_or_reporting_date"] != "not_deterministically_extracted", x["value_or_unit"] != "not_deterministically_extracted", len(x["minimum_supporting_evidence"])), reverse=True)
    selected = candidates[:15]
    topic_counts = Counter(x["category"] for x in selected)
    by_topic_date: dict[tuple[str, str], list[dict]] = {}
    for candidate in selected:
        if candidate["effective_or_reporting_date"] != "not_deterministically_extracted":
            by_topic_date.setdefault((candidate["category"], candidate["effective_or_reporting_date"]), []).append(candidate)
    for group in by_topic_date.values():
        values = {x["value_or_unit"] for x in group}
        if len(group) > 1 and len(values) > 1:
            ids = [x["candidate_id"] for x in group]
            for candidate in group:
                candidate["conflicting_evidence"] = [x for x in ids if x != candidate["candidate_id"]]
                candidate["proposed_disposition"] = "human_review_required_conflict_check"
    package = {"schema_version": "st1-019-review-v1", "generated_utc": datetime.now(UTC).isoformat(), "selection_alias": "status_oriented_candidate_1", "candidate_count": len(selected), "candidates": selected, "review_instructions": "For each item choose exactly APPROVE, REJECT, NEEDS_MORE_EVIDENCE, or CONFLICT. No item is certified until explicitly approved."}
    args.output.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    sanitized = {
        "schema_version": "st1-019-sanitized-review-summary-v1",
        "selection_alias": "status_oriented_candidate_1",
        "source_signature": data["selection_signature"],
        "extraction_aggregate": data["aggregate"],
        "review_candidate_count": len(selected),
        "review_category_distribution": dict(topic_counts),
        "date_supported_candidate_count": sum(x["effective_or_reporting_date"] != "not_deterministically_extracted" for x in selected),
        "value_supported_candidate_count": sum(x["value_or_unit"] != "not_deterministically_extracted" for x in selected),
        "candidate_conflict_check_count": sum(bool(x["conflicting_evidence"]) for x in selected),
        "local_package_only": True,
        "certification_executed": False,
        "external_ai_or_platform_persistence": False,
    }
    args.sanitized_output.parent.mkdir(parents=True, exist_ok=True)
    args.sanitized_output.write_text(json.dumps(sanitized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(sanitized, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
