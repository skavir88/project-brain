#!/usr/bin/env python3
"""Build local-only, dated, row-provenance review candidates from status workbooks."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def normalized_date(value: str) -> tuple[int, int, int] | None:
    value = value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    match = re.fullmatch(r"(1[34]\d{2})/(\d{1,2})/(\d{1,2})", value.strip())
    return tuple(map(int, match.groups())) if match else None


def cell_map(segments: list[dict]) -> dict[str, str]:
    result = {}
    for segment in segments:
        match = re.search(r"cell:([A-Z]+\d+)$", segment["location"])
        if match:
            result[match.group(1)] = segment["text"].strip()
    return result


def main() -> int:
    data = json.loads(runtime("st1-022-dated-status-extraction.json").read_text(encoding="utf-8"))
    snapshots = []
    for document in data["documents"]:
        by_sheet: dict[str, list[dict]] = defaultdict(list)
        for segment in document["segments"]:
            sheet = segment["location"].split(",cell:", 1)[0]
            by_sheet[sheet].append(segment)
        for sheet, segments in by_sheet.items():
            cells = cell_map(segments)
            dates = [(reference, normalized_date(value)) for reference, value in cells.items() if re.fullmatch(r"[A-Z]+5", reference)]
            dates = [(ref, date) for ref, date in dates if date]
            if len(dates) < 2 or not cells.get("A3", "").startswith("شماره پیمان"):
                continue
            start, end = min(date for _, date in dates), max(date for _, date in dates)
            # A dated daily-status form must also name an ongoing-activity column.
            if not any("فعالیت اجرایی" in value for value in cells.values()):
                continue
            row_fingerprint = hashlib.sha256("|".join(cells.get(f"{column}{row}", "") for row in range(6, 80) for column in "ABCDLM").encode()).hexdigest()
            snapshots.append({"document": document, "sheet": sheet, "cells": cells, "start": start, "end": end, "fingerprint": row_fingerprint})
    if not snapshots:
        raise RuntimeError("no internally dated daily-status snapshot was found")
    # Collapse copy-forward workbooks by their table content. Choose the latest
    # internal date, never a filename or filesystem date, then a stable hash tie-break.
    unique = {snapshot["fingerprint"]: snapshot for snapshot in snapshots}
    latest = max(unique.values(), key=lambda x: (x["end"], x["start"], x["fingerprint"]))
    date_text = f"{latest['start'][0]:04d}/{latest['start'][1]:02d}/{latest['start'][2]:02d}–{latest['end'][0]:04d}/{latest['end'][1]:02d}/{latest['end'][2]:02d}"
    patterns = [("stoppage", ("متوقف", "hold")), ("slow_progress", ("کند",)), ("material_shortage", ("کمبود",)), ("workforce_availability", ("عدم حضور",)), ("design_change", ("تغییر",))]
    candidates = []
    for row in range(6, 80):
        activity = latest["cells"].get(f"D{row}", "")
        notes = " | ".join(value for value in (latest["cells"].get(f"L{row}", ""), latest["cells"].get(f"M{row}", "")) if value)
        text = (activity + " | " + notes).strip(" |")
        if not text:
            continue
        category = next((name for name, terms in patterns if any(term.casefold() in text.casefold() for term in terms)), None)
        if not category:
            continue
        identifier = " | ".join(value for value in (latest["cells"].get(f"B{row}", ""), latest["cells"].get(f"C{row}", "")) if value)
        if not identifier:
            continue
        fingerprint = hashlib.sha256((latest["document"]["sha256"] + latest["sheet"] + str(row) + text).encode()).hexdigest()
        candidates.append({
            "candidate_id": "review-" + fingerprint[:16],
            "category": category,
            "proposed_claim": f"Dated daily-status form reports an activity issue for {identifier} during the stated reporting period; human validation required.",
            "reporting_period": date_text,
            "project_identifier_present": True,
            "source_alias": data["selection_alias"],
            "source_relative_locator": latest["document"]["source_relative_locator"],
            "location": {"sheet": latest["sheet"], "row": row, "activity_cell": f"D{row}", "note_cells": [f"L{row}", f"M{row}"]},
            "minimum_supporting_evidence": {"activity": activity, "notes": notes},
            "uncertainty": "This is a dated internal activity snapshot, but the status series itself does not prove organization-wide currentness or approval authority. It must not be interpreted as a current executive status without human review.",
            "conflicting_evidence": [],
            "proposed_disposition": "human_review_required",
            "fingerprint": fingerprint,
        })
    # Prefer stoppages and slow progress, retaining at most 12 substantive rows.
    priority = {"stoppage": 0, "slow_progress": 1, "design_change": 2, "material_shortage": 3, "workforce_availability": 4}
    candidates.sort(key=lambda x: (priority[x["category"]], x["location"]["row"]))
    candidates = candidates[:12]
    package = {"schema_version": "st1-022-dated-status-review-v1", "generated_utc": datetime.now(UTC).isoformat(), "selection_alias": data["selection_alias"], "selected_internal_reporting_period": date_text, "deduplicated_snapshot_count": len(unique), "raw_snapshot_count": len(snapshots), "candidate_count": len(candidates), "candidates": candidates, "review_instructions": "For each candidate choose exactly APPROVE, REJECT, NEEDS_MORE_EVIDENCE, or CONFLICT. No real claim is certified automatically."}
    runtime("st1-022-human-review-package.json").write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {"schema_version": "st1-022-sanitized-dated-status-review-summary-v1", "selection_alias": data["selection_alias"], "source_signature": data["selection_signature"], "internally_dated_daily_status_snapshot_count": len(snapshots), "deduplicated_snapshot_count": len(unique), "selected_internal_reporting_period": date_text, "review_candidate_count": len(candidates), "review_category_distribution": dict(Counter(x["category"] for x in candidates)), "project_identifier_present": True, "currentness_or_approval_authority_verified": False, "certification_executed": False, "raw_content_or_locators_versioned": False}
    destination = Path("evidence/sanitized/2026-08-09-st1-022-dated-status-source-review.json")
    destination.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
