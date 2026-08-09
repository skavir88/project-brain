"""Metadata-only discovery of a bounded, status-oriented pilot corpus.

Raw relative locators remain in a local runtime output. Console output is a
sanitized aggregate suitable for recording in Project Brain evidence.
"""

from __future__ import annotations

import json
import os
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ALLOWED = {".pdf", ".docx", ".xlsx"}
MIN_DOCS = 10
MAX_DOCS = 50
MAX_BYTES = 1024 * 1024 * 1024

HIGHEST = {
    "گزارشپیشرفتپروژه": (100, "project_progress_report"),
    "گزارشپیشرفت": (90, "progress_report"),
    "گزارشماهانه": (85, "monthly_report"),
    "گزارشهفتگی": (80, "weekly_report"),
    "گزارشوضعیت": (85, "status_report"),
    "وضعیتپروژه": (80, "project_status"),
    "گزارشمدیریتی": (75, "management_report"),
    "کنترلپروژه": (70, "project_controls"),
    "projectstatus": (85, "project_status"),
    "progressreport": (90, "progress_report"),
    "monthlyreport": (85, "monthly_report"),
    "weeklyreport": (80, "weekly_report"),
    "managementreport": (75, "management_report"),
    "projectcontrols": (70, "project_controls"),
}
SECONDARY = {
    "برنام هریزی": (45, "planning"),
    "برنامهر یزی": (45, "planning"),
    "برنامهریزی": (45, "planning"),
    "زمانبندی": (50, "schedule"),
    "schedule": (50, "schedule"),
    "updatedschedule": (55, "updated_schedule"),
    "progressmeasurement": (55, "progress_measurement"),
    "پیشرفتفیزیکی": (55, "physical_progress"),
    "گزارشکارگاهی": (45, "site_report"),
    "صورتجلسهپیشرفت": (50, "progress_minutes"),
    "صورتجلسهکارگاهی": (45, "site_minutes"),
}


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).replace("ي", "ی").replace("ك", "ک")
    value = "".join(char for char in value if unicodedata.category(char) != "Cf")
    return "".join(value.casefold().split())


def name_signals(value: str) -> tuple[int, list[str]]:
    probe = normalized(value)
    score = 0
    labels: list[str] = []
    for term, (weight, label) in HIGHEST.items():
        if term.replace(" ", "") in probe:
            score += weight
            labels.append(label)
    for term, (weight, label) in SECONDARY.items():
        if term.replace(" ", "") in probe:
            score += weight
            labels.append(label)
    return score, sorted(set(labels))


def iso(value: float) -> str:
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def main() -> int:
    root_value = os.environ.get("EAI_PILOT_ROOT")
    output_value = os.environ.get("EAI_STATUS_DISCOVERY_RUNTIME_OUTPUT")
    if not root_value or not output_value:
        raise SystemExit("EAI_PILOT_ROOT and EAI_STATUS_DISCOVERY_RUNTIME_OUTPUT are required")
    root = Path(root_value)
    excluded_locators = set(json.loads(os.environ.get("EAI_EXCLUDED_RELATIVE_LOCATORS", "[]")))
    candidate_meta: dict[Path, dict] = {}
    files: list[tuple[Path, os.stat_result, int, list[str]]] = []
    errors = 0
    for directory, _, names in os.walk(root):
        parent = Path(directory)
        directory_score, directory_labels = name_signals(parent.name)
        if directory_score:
            candidate_meta[parent] = {"directory_score": directory_score, "labels": directory_labels}
        for name in names:
            path = parent / name
            extension = path.suffix.lower()
            if extension not in ALLOWED or name.startswith("~$"):
                continue
            try:
                stat = path.stat()
            except OSError:
                errors += 1
                continue
            file_score, file_labels = name_signals(path.stem)
            if file_score:
                current = candidate_meta.setdefault(parent, {"directory_score": 0, "labels": []})
                current["directory_score"] = max(current["directory_score"], file_score)
                current["labels"] = sorted(set(current["labels"] + file_labels))
            files.append((path, stat, file_score, file_labels))

    ranked: list[dict] = []
    for directory, meta in candidate_meta.items():
        if directory.relative_to(root).as_posix() in excluded_locators:
            continue
        rows = [(path, stat, score, labels) for path, stat, score, labels in files if path == directory or directory in path.parents]
        count = len(rows)
        size = sum(stat.st_size for _, stat, _, _ in rows)
        if not (MIN_DOCS <= count <= MAX_DOCS and size <= MAX_BYTES):
            continue
        extensions = Counter(path.suffix.lower() for path, _, _, _ in rows)
        dates = [iso(stat.st_mtime) for _, stat, _, _ in rows]
        filename_score = sum(score for _, _, score, _ in rows)
        score = meta["directory_score"] * 3 + min(filename_score, 300)
        # A coherent series of metadata dates and matching filenames boosts relevance,
        # while timestamps remain only a tie-breaker, not evidence of authority.
        unique_months = len({date[:7] for date in dates})
        score += min(unique_months, 12) * 2
        ranked.append({
            "directory": directory,
            "rows": rows,
            "score": score,
            "labels": meta["labels"],
            "document_count": count,
            "extension_distribution": dict(sorted(extensions.items())),
            "aggregate_size_bytes": size,
            "oldest_last_write_utc": min(dates),
            "newest_last_write_utc": max(dates),
        })
    ranked.sort(key=lambda item: (-item["score"], item["aggregate_size_bytes"], str(item["directory"]).casefold()))
    top = ranked[:3]
    selected = None
    # Different apparent series purposes can change the business meaning of
    # "latest status". Metadata ranking must not select across that boundary.
    top_purposes = {tuple(candidate["labels"]) for candidate in top}
    if top and len(top_purposes) == 1 and (len(top) == 1 or top[0]["score"] >= top[1]["score"] + 25):
        selected = top[0]
    runtime = {
        "schema_version": "st1-018-status-discovery-v1",
        "pilot_root_reference": "approved_pilot_root",
        "selection": None,
        "top_candidates": [],
    }
    for index, candidate in enumerate(top, start=1):
        item = {key: candidate[key] for key in ("score", "labels", "document_count", "extension_distribution", "aggregate_size_bytes", "oldest_last_write_utc", "newest_last_write_utc")}
        item["alias"] = f"status_oriented_candidate_{index}"
        item["relative_locator"] = candidate["directory"].relative_to(root).as_posix()
        item["files"] = [
            {
                "relative_locator": path.relative_to(candidate["directory"]).as_posix(),
                "extension": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "last_write_utc": iso(stat.st_mtime),
            }
            for path, stat, _, _ in sorted(candidate["rows"], key=lambda row: row[0].relative_to(candidate["directory"]).as_posix().casefold())
        ]
        runtime["top_candidates"].append(item)
        if selected is candidate:
            runtime["selection"] = item
    destination = Path(output_value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(runtime, ensure_ascii=False, indent=2), encoding="utf-8")
    sanitized = {
        "metadata_discovery_error_count": errors,
        "status_oriented_technical_candidate_count": len(ranked),
        "selection": "deterministic" if selected else "human_selection_required",
        "top_candidates": [
            {
                "alias": f"status_oriented_candidate_{index}",
                "apparent_document_series_purpose": candidate["labels"],
                "document_count": candidate["document_count"],
                "extension_distribution": candidate["extension_distribution"],
                "aggregate_size_bytes": candidate["aggregate_size_bytes"],
                "oldest_last_write_utc": candidate["oldest_last_write_utc"],
                "newest_last_write_utc": candidate["newest_last_write_utc"],
                "why_relevant": "metadata_name_signals_and_bounded_series_only",
            }
            for index, candidate in enumerate(top, start=1)
        ],
        "raw_locators_outside_git": True,
        "content_opened": False,
        "source_modified": False,
    }
    print(json.dumps(sanitized, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
