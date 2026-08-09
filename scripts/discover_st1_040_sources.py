#!/usr/bin/env python3
"""Rank metadata-only status-source families in the local pilot discovery index.

The input SQLite index is local operational state outside Git and may contain
raw SMB-relative locators. This script never opens source documents. Its JSON
output is intentionally written outside Git; only an aggregate sanitized
summary may be versioned after review.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path


ALLOWED = {".pdf", ".docx", ".xlsx"}

# Signals are deliberately lexical: they establish discovery relevance only,
# never document authority, reporting date, truth, or currentness.
SIGNALS = {
    "explicit_status": (9, [
        "گزارش پیشرفت", "گزارش وضعیت", "گزارش هفتگی", "گزارش ماهانه",
        "گزارش عملکرد", "گزارش مدیریتی", "داشبورد", "پیشرفت فیزیکی",
        "progress report", "project status", "status report", "weekly report",
        "monthly report", "weekly progress", "monthly progress", "dashboard",
        "management report", "executive report",
    ]),
    "schedule_or_control": (6, [
        "کنترل پروژه", "برنامه زمان بندی", "برنامه زمان‌بندی", "برنامه پیشرفت",
        "time schedule", "updated schedule", "baseline", "lookahead", "primavera", "p6",
        "project control", "recovery plan", "catch-up plan",
    ]),
    "status_dimension": (4, [
        "اکشن پلن", "برنامه اقدام", "تاخیرات", "تأخیرات", "صورتجلسه", "جلسه پیشرفت",
        "action plan", "progress meeting", "meeting minutes", "procurement status",
        "engineering status", "construction status", "risk register", "issue register",
    ]),
}
NEGATIVE_CONTEXT = ["claim", "legal", "tender", "bid", "لایحه", "دعاوی", "حقوقی", "مناقصه"]
DATE_PATTERN = re.compile(r"(?:13\d{2}|14\d{2}|20\d{2})[-_/. ]?\d{1,2}(?:[-_/. ]?\d{1,2})?")


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ي", "ی").replace("ك", "ک")
    return " ".join(value.casefold().split())


def signal_matches(value: str) -> dict[str, list[str]]:
    probe = normalized(value)
    result: dict[str, list[str]] = {}
    for category, (_, terms) in SIGNALS.items():
        hits = [term for term in terms if normalized(term) in probe]
        if hits:
            result[category] = hits
    return result


def family_key(parent: str) -> str:
    # Direct-parent grouping avoids treating every ancestor as an independent
    # family and makes recurring, colocated report series comparable.
    return parent.replace("\\", "/") or "."


def score_family(item: dict) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    for category, (weight, _) in SIGNALS.items():
        if item["signals"][category]:
            score += weight * min(3, len(item["signals"][category]))
            reasons.append(category)
    if item["date_pattern_count"]:
        score += min(6, item["date_pattern_count"])
        reasons.append("apparent_date_or_version_sequence")
    if item["document_count"] >= 3:
        score += min(5, item["document_count"] // 3)
        reasons.append("multi_document_family")
    if item["allowed_count"]:
        score += min(4, item["allowed_count"])
        reasons.append("locally_probeable_formats")
    if item["negative_context"]:
        score -= 18
        reasons.append("negative_context_penalty")
    return score, reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=runtime("pilot_metadata_index.sqlite"))
    parser.add_argument("--output", type=Path, default=runtime("st1-040-source-family-ranking.json"))
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    if not args.database.is_file():
        raise SystemExit("local metadata index is unavailable")
    conn = sqlite3.connect(args.database)
    try:
        rows = conn.execute("""
            SELECT relative_locator, parent_relative_locator, filename, extension,
                   size_bytes, created_utc, modified_utc
            FROM files WHERE enumeration_status='enumerated'
        """).fetchall()
        directory_counts = dict(conn.execute("SELECT status,count(*) FROM directories GROUP BY status"))
    finally:
        conn.close()

    families: dict[str, dict] = defaultdict(lambda: {
        "files": [], "document_count": 0, "allowed_count": 0, "aggregate_size_bytes": 0,
        "extension_distribution": Counter(), "signals": {key: set() for key in SIGNALS},
        "date_pattern_count": 0, "negative_context": False, "modified_dates": [],
    })
    for relative, parent, filename, extension, size, created, modified in rows:
        key = family_key(parent)
        item = families[key]
        item["files"].append({
            "relative_locator": relative, "filename": filename, "extension": extension,
            "size_bytes": size, "created_utc": created, "modified_utc": modified,
        })
        item["document_count"] += 1
        item["aggregate_size_bytes"] += int(size or 0)
        item["extension_distribution"][extension or ""] += 1
        if extension in ALLOWED:
            item["allowed_count"] += 1
        haystack = f"{parent}/{filename}"
        for category, hits in signal_matches(haystack).items():
            item["signals"][category].update(hits)
        item["date_pattern_count"] += len(DATE_PATTERN.findall(haystack))
        item["negative_context"] |= any(normalized(term) in normalized(parent) for term in NEGATIVE_CONTEXT)
        if modified:
            item["modified_dates"].append(modified)

    ranked = []
    for locator, item in families.items():
        if not any(item["signals"].values()):
            continue
        score, reasons = score_family(item)
        ranked.append({
            "relative_locator": locator,
            "score": score,
            "ranking_reasons": reasons,
            "document_count": item["document_count"],
            "locally_probeable_document_count": item["allowed_count"],
            "extension_distribution": dict(sorted(item["extension_distribution"].items())),
            "aggregate_size_bytes": item["aggregate_size_bytes"],
            "metadata_date_range": [min(item["modified_dates"]), max(item["modified_dates"])] if item["modified_dates"] else None,
            "metadata_signals": {key: sorted(value) for key, value in item["signals"].items() if value},
            "negative_context": item["negative_context"],
            "files": item["files"],
        })
    ranked.sort(key=lambda item: (-item["score"], -item["locally_probeable_document_count"], item["aggregate_size_bytes"], item["relative_locator"].casefold()))
    output = {
        "schema_version": "st1-040-source-family-ranking-v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "metadata_only": True,
        "index_rows_queried": len(rows),
        "directory_status_counts": directory_counts,
        "source_family_count": len(ranked),
        "top_families": ranked[:args.limit],
        "boundaries": {"content_opened": False, "new_smb_traversal": False, "external_model_use": False, "raw_output_outside_git": True},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    # Print aggregate-only output so command logs remain safe.
    print(json.dumps({
        "metadata_only": True, "index_rows_queried": len(rows), "source_family_count": len(ranked),
        "top_family_count": len(output["top_families"]), "directory_status_counts": directory_counts,
        "output_outside_git": True,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
