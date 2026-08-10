#!/usr/bin/env python3
"""Rank likely authoritative project-status source locations from local metadata.

This uses only the existing runtime-local SQLite inventory. It never opens a
source document, traverses SMB, or writes a raw locator into the repository.
The detailed output belongs in local runtime state; stdout is aggregate-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path


ALLOWED = {".pdf", ".docx", ".xlsx"}
MAX_BOUNDED_FILES = 100
MAX_BOUNDED_SIZE_BYTES = 1_073_741_824
SIGNALS: dict[str, tuple[int, tuple[str, ...]]] = {
    "explicit_status_progress": (20, (
        "گزارش پیشرفت پروژه", "گزارش پیشرفت", "گزارش وضعیت", "وضعیت پروژه",
        "progress report", "project status", "status report",
    )),
    "periodic_report": (14, (
        "گزارش هفتگی", "گزارش ماهانه", "weekly report", "monthly report",
        "weekly progress", "monthly progress",
    )),
    "project_control_schedule": (9, (
        "کنترل پروژه", "برنامه زمانبندی", "برنامه زمان‌بندی", "گزارش برنامه زمانبندی",
        "project control", "time schedule", "schedule", "primavera", "p6",
    )),
    "dashboard_or_action": (6, ("داشبورد", "dashboard", "action plan", "برنامه اقدام")),
}
NEGATIVE = ("claim", "legal", "tender", "bid", "لایحه", "دعاوی", "حقوقی", "مناقصه")


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = value.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")
    return " ".join(value.casefold().split())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=runtime("pilot_metadata_index.sqlite"))
    parser.add_argument("--output", type=Path, default=runtime("st1-043-authoritative-source-locator.json"))
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    if not args.database.is_file():
        raise SystemExit("runtime-local metadata index is unavailable")

    conn = sqlite3.connect(args.database)
    try:
        rows = conn.execute(
            """SELECT parent_relative_locator, filename, extension, size_bytes, modified_utc
               FROM files WHERE enumeration_status = 'enumerated'"""
        ).fetchall()
    finally:
        conn.close()

    families: dict[str, dict] = defaultdict(lambda: {
        "files": [], "signals": defaultdict(set), "modified": [], "negative": False,
    })
    for parent, filename, extension, size, modified in rows:
        item = families[parent]
        item["files"].append((filename, extension, int(size or 0)))
        probe = norm(f"{parent}/{filename}")
        for category, (_, terms) in SIGNALS.items():
            for term in terms:
                if norm(term) in probe:
                    item["signals"][category].add(term)
        item["negative"] |= any(norm(term) in probe for term in NEGATIVE)
        if modified:
            item["modified"].append(modified)

    ranked = []
    excluded_unbounded = 0
    for parent, item in families.items():
        if not item["signals"] or item["negative"]:
            continue
        files = item["files"]
        distribution = Counter(ext for _, ext, _ in files)
        allowed = sum(count for ext, count in distribution.items() if ext in ALLOWED)
        aggregate_size = sum(size for _, _, size in files)
        if len(files) > MAX_BOUNDED_FILES or aggregate_size > MAX_BOUNDED_SIZE_BYTES:
            excluded_unbounded += 1
            continue
        score = sum(SIGNALS[key][0] * min(3, len(hits)) for key, hits in item["signals"].items())
        # A coherent report family is a discovery signal only. Size and metadata
        # recency are tie-break/discovery signals, never source authority.
        score += min(6, len(files) // 3) + min(4, allowed)
        ranked.append({
            "locator_token": "st1-043-" + hashlib.sha256(parent.encode("utf-8")).hexdigest()[:16],
            "relative_locator": parent,
            "score": score,
            "source_type_signals": {key: sorted(hits) for key, hits in item["signals"].items()},
            "file_count": len(files),
            "allowed_type_summary": dict(sorted((ext, count) for ext, count in distribution.items() if ext in ALLOWED)),
            "aggregate_size_bytes": aggregate_size,
            "metadata_date_range": [min(item["modified"]), max(item["modified"])] if item["modified"] else None,
        })
    ranked.sort(key=lambda x: (-x["score"], -x["file_count"], x["aggregate_size_bytes"], x["relative_locator"].casefold()))
    payload = {
        "schema_version": "st1-043-authoritative-source-locator-v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "metadata_only": True,
        "index_rows_queried": len(rows),
        "strong_location_count": len(ranked),
        "unbounded_location_count_excluded": excluded_unbounded,
        "locations": ranked[:args.limit],
        "boundaries": {
            "content_opened": False,
            "new_smb_traversal": False,
            "external_model_use": False,
            "raw_locators_runtime_local_only": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "metadata_only": True,
        "index_rows_queried": len(rows),
        "strong_location_count": len(ranked),
        "unbounded_location_count_excluded": excluded_unbounded,
        "reported_location_count": len(payload["locations"]),
        "output_outside_git": True,
    }, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    raise SystemExit(main())
