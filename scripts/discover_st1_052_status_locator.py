#!/usr/bin/env python3
"""Rank bounded, metadata-only project-status source locations from the local index.

This utility never contacts SMB or opens source documents.  It reads the
runtime-local metadata index and writes raw locators only to the runtime
directory.  Its stdout is an aggregate, non-sensitive execution summary.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path


ALLOWLIST = {".pdf", ".docx", ".xlsx"}
TERM_GROUPS = {
    "explicit_status_progress": (
        "گزارش پیشرفت", "گزارش وضعیت", "وضعیت پروژه", "گزارش مدیریت",
        "progress report", "project status", "status report", "management report",
    ),
    "periodic_reporting": (
        "گزارش هفتگی", "گزارش دو هفتگی", "گزارش ماهانه", "weekly report",
        "bi-weekly report", "biweekly report", "monthly report",
    ),
    "project_control_schedule": (
        "کنترل پروژه", "برنامه زمان بندی", "برنامه زمان‌بندی", "داشبورد",
        "project control", "project controls", "time schedule", "schedule",
        "dashboard", "primavera", "p6", "action plan",
    ),
}
NEGATIVE_TERMS = ("claim", "legal", "tender", "bid", "لایحه", "دعاوی", "حقوقی", "مناقصه")
PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
DATE = re.compile(r"(?<!\d)(14\d{2})[._/\-\s]+(\d{1,2})(?:[._/\-\s]+(\d{1,2}))?(?!\d)")
# MRP report numbers are two digits in this family.  Deliberately do not
# mistake the common project code "070" for a report sequence.
SERIES = re.compile(
    r"(?<!\d)(?:no\.?\s*|mrp[-_\s]*)([2-9]\d)(?!\d)|"
    r"(?<!\d)([2-9]\d)[-_\s]+(?:mrp|twrp)(?!\w)", re.I
)


def runtime_file(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").translate(PERSIAN_DIGITS)
    value = value.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")
    return " ".join(value.casefold().split())


def ancestry(parent: str) -> list[str]:
    parts = [p for p in parent.replace("\\", "/").split("/") if p]
    return ["/".join(parts[:i]) for i in range(1, len(parts) + 1)]


def generic_category(probe: str) -> str:
    if any(norm(term) in probe for term in TERM_GROUPS["explicit_status_progress"]):
        return "project-status-or-progress-reporting"
    if any(norm(term) in probe for term in TERM_GROUPS["periodic_reporting"]):
        return "periodic-reporting"
    if any(norm(term) in probe for term in TERM_GROUPS["project_control_schedule"]):
        return "project-control-or-schedule"
    return "reporting-family"


def main() -> None:
    database = runtime_file("pilot_metadata_index.sqlite")
    output = runtime_file("st1-052-business-locator-recovery.json")
    if not database.is_file():
        raise SystemExit("runtime-local metadata index unavailable")
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute(
            "SELECT relative_locator,parent_relative_locator,source_alias,filename,"
            "extension,size_bytes,created_utc,modified_utc FROM files "
            "WHERE enumeration_status='enumerated'"
        ).fetchall()
    finally:
        connection.close()

    # A candidate is the nearest parent family whose own path or a child name
    # bears a permitted business-status signal.  This avoids a fresh traversal.
    families: dict[str, dict] = defaultdict(lambda: {
        "files": [], "signals": defaultdict(set), "date_tokens": set(),
        "series": set(), "negative": False,
    })
    for relative, parent, source_alias, filename, extension, size, created, modified in rows:
        combined = f"{parent}/{filename}"
        probe = norm(combined)
        matching = []
        for group, terms in TERM_GROUPS.items():
            terms_found = [term for term in terms if norm(term) in probe]
            if terms_found:
                matching.append((group, terms_found))
        if not matching:
            continue
        # Use a signal-bearing ancestor if present; otherwise the immediate
        # parent remains the bounded location.
        family = parent
        for candidate_parent in reversed(ancestry(parent)):
            ancestor_probe = norm(candidate_parent)
            if (any(norm(term) in ancestor_probe for terms in TERM_GROUPS.values() for term in terms)
                    or SERIES.search(ancestor_probe)):
                family = candidate_parent
                break
        item = families[family]
        item["files"].append({
            "relative_locator": relative, "source_alias": source_alias,
            "filename": filename, "extension": extension.casefold(),
            "size_bytes": int(size or 0), "created_utc": created, "modified_utc": modified,
        })
        for group, terms_found in matching:
            item["signals"][group].update(terms_found)
        item["negative"] |= any(norm(term) in probe for term in NEGATIVE_TERMS)
        item["date_tokens"].update(
            f"{year}/{int(month):02d}" for year, month, _ in DATE.findall(norm(combined))
        )
        item["series"].update(int(number) for match in SERIES.findall(norm(combined)) for number in match if number)

    candidates = []
    for family, item in families.items():
        files_by_locator = {entry["relative_locator"]: entry for entry in item["files"]}
        # Include all indexed sibling files under the selected bounded family.
        prefix = family.rstrip("/") + "/"
        for relative, parent, source_alias, filename, extension, size, created, modified in rows:
            if parent == family or parent.startswith(prefix):
                files_by_locator.setdefault(relative, {
                    "relative_locator": relative, "source_alias": source_alias,
                    "filename": filename, "extension": extension.casefold(),
                    "size_bytes": int(size or 0), "created_utc": created, "modified_utc": modified,
                })
        files = list(files_by_locator.values())
        allowed = [entry for entry in files if entry["extension"] in ALLOWLIST]
        size = sum(entry["size_bytes"] for entry in files)
        if item["negative"] or not allowed or len(files) > 250 or size > 1_073_741_824:
            continue
        signals = {group: sorted(values) for group, values in item["signals"].items()}
        score = (30 * bool(signals.get("explicit_status_progress"))
                 + 18 * bool(signals.get("periodic_reporting"))
                 + 10 * bool(signals.get("project_control_schedule"))
                 + min(10, len(allowed) // 4)
                 + (15 if any(number > 25 for number in item["series"]) else 0))
        probes = norm(family)
        scope = "project-wide-or-unknown" if any(
            norm(term) in probes for terms in TERM_GROUPS.values() for term in terms
        ) else "package-or-discipline-unknown"
        metadata_dates = sorted(
            entry["modified_utc"] for entry in files if entry["modified_utc"]
        )
        candidates.append({
            "alias": "st1-052-" + hashlib.sha256(family.encode("utf-8")).hexdigest()[:16],
            "relative_locator": family,
            "score": score,
            "category": generic_category(probes),
            "scope_signal": scope,
            "signals": signals,
            "file_count": len(files),
            "probeable_file_count": len(allowed),
            "extension_distribution": dict(sorted(Counter(entry["extension"] for entry in files).items())),
            "aggregate_size_bytes": size,
            "filesystem_metadata_date_range_utc": ([metadata_dates[0], metadata_dates[-1]] if metadata_dates else []),
            "filename_or_directory_date_tokens": sorted(item["date_tokens"]),
            "series_numbers": sorted(item["series"]),
            "possible_biweekly_continuation": any(number > 25 for number in item["series"]),
            "files": files,
        })
    candidates.sort(key=lambda c: (-c["score"], -c["probeable_file_count"], c["aggregate_size_bytes"], c["relative_locator"].casefold()))
    output.parent.mkdir(parents=True, exist_ok=True)
    continuations = [candidate for candidate in candidates if candidate["possible_biweekly_continuation"]]
    output.write_text(json.dumps({
        "schema_version": "st1-052-business-locator-recovery-v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "metadata_only": True,
        "index_rows_queried": len(rows),
        "candidate_location_count": len(candidates),
        "candidates": candidates,
        "biweekly_continuation_candidates": continuations[:10],
        "boundaries": {
            "content_opened": False, "smb_contacted": False,
            "new_smb_traversal": False, "external_model_use": False,
            "raw_locators_runtime_local_only": True,
        },
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "metadata_only": True, "index_rows_queried": len(rows),
        "candidate_location_count": len(candidates), "reported_candidates": len(candidates),
        "biweekly_continuation_count": len(continuations),
        "output_outside_git": True,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
