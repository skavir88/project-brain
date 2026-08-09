#!/usr/bin/env python3
"""Build a local-only human-review package from a local selection manifest.

The manifest and generated package remain in the workstation runtime directory.
This generic builder intentionally contains no organizational source text,
filenames, or cell selections.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def value_at(document: dict, location: str) -> str:
    for segment in document["segments"]:
        if segment["location"] == location:
            return segment["text"]
    raise RuntimeError(f"required local provenance location is absent: {location}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    extraction = json.loads(args.extraction.read_text(encoding="utf-8"))
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    if extraction.get("selection_alias") != selection.get("selection_alias"):
        raise RuntimeError("selection does not match the extracted bounded corpus")
    candidates = []
    for spec in selection["candidates"]:
        document = extraction["documents"][int(spec["document_ordinal"]) - 1]
        date = value_at(document, spec["date_location"])
        note = value_at(document, spec["note_location"])
        package = value_at(document, spec["package_location"])
        canonical = "|".join((document["sha256"], spec["note_location"], spec["category"]))
        identifier = "review-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
        candidates.append({
            "candidate_id": identifier,
            "proposed_claim": f"According to the action-plan workbook dated {date}, the note for {package} states: {note}",
            "document_date": date,
            "date_type": spec["date_type"],
            "category": spec["category"],
            "affected_work_package": package,
            "source_workbook_alias": spec["source_workbook_alias"],
            "source_relative_locator": document["source_relative_locator"],
            "provenance": {
                "sheet_and_cells": [spec["date_location"], spec["package_location"], spec["note_location"]],
                "source_sha256": document["sha256"],
            },
            "minimum_supporting_evidence": note,
            "duplicate_or_copy_forward": spec.get("duplicate_or_copy_forward", "not_observed_in_selected_candidates"),
            "comparison_to_prior_certified_period": "document date is later than 1401/10/10–1401/10/16; note/event effective date is not independently established",
            "uncertainty": "Document date is not proof of authority, currentness today, or the event effective date; Human Review must assess relevance and status semantics.",
            "required_dispositions": ["APPROVE", "REJECT", "NEEDS_MORE_EVIDENCE", "CONFLICT"],
            "proposed_reviewer_disposition": "NEEDS_MORE_EVIDENCE",
            "lifecycle_state": "human_review_required",
        })
    if not (1 <= len(candidates) <= 15) or len({c["candidate_id"] for c in candidates}) != len(candidates):
        raise RuntimeError("review candidate count or identifiers are invalid")
    payload = {
        "schema_version": "st1-025-currentness-review-v1",
        "selection_alias": selection["selection_alias"],
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"selection_alias": selection["selection_alias"], "candidate_count": len(candidates), "categories": sorted({c["category"] for c in candidates}), "output_written_outside_git": True}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
