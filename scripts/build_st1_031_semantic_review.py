#!/usr/bin/env python3
"""Build a local-only ST1-031 review package from workbook-backed field labels."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

FIELD_COLUMNS = {
    "activity": "D", "unit": "H", "boq": "I", "plan_last": "J", "plan_this": "K", "plan_cumulative": "L",
    "duration": "M", "plan_start": "N", "plan_finish": "O", "actual_volume_this": "BH", "actual_volume_cumulative": "BI",
    "contractor_plan_last": "BJ", "contractor_plan_this": "BK", "contractor_plan_cumulative": "BL",
    "actual_progress_last": "BM", "actual_progress_this": "BN", "actual_progress_cumulative": "BO",
    "actual_weighted_value": "BP", "plan_weight_factor": "BR", "plan_weighted_value": "BS",
    "volume_until_previous_week": "BT", "volume_this_week": "BU", "volume_until_this_week": "BV",
}


def value(row: dict, column: str):
    cell = row.get(column)
    return None if cell is None else cell.get("value")


def number(raw: object) -> float | None:
    try:
        return float(str(raw))
    except (TypeError, ValueError):
        return None


def pct(raw: object) -> dict | None:
    parsed = number(raw)
    return None if parsed is None else {"stored_fraction": parsed, "display_percent": parsed * 100}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reporting-period", required=True)
    args = parser.parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    prior = json.loads(args.package.read_text(encoding="utf-8"))
    rows = schema["target_rows_data"]
    candidates = []
    for original in prior["candidates"]:
        row_number = original["provenance"].rsplit("row:", 1)[1]
        row = rows[row_number]
        mapping = {name: value(row, column) for name, column in FIELD_COLUMNS.items()}
        plan_cumulative, actual_cumulative = pct(mapping["contractor_plan_cumulative"]), pct(mapping["actual_progress_cumulative"])
        plan_this, actual_this = pct(mapping["contractor_plan_this"]), pct(mapping["actual_progress_this"])
        variance = None
        if plan_cumulative and actual_cumulative:
            variance = {
                "formula": "actual_progress_cumulative - contractor_plan_progress_cumulative",
                "unit": "percentage_points",
                "value": actual_cumulative["display_percent"] - plan_cumulative["display_percent"],
            }
        period_variance = None
        if plan_this and actual_this:
            period_variance = {
                "formula": "actual_progress_this_period - contractor_plan_progress_this_period",
                "unit": "percentage_points",
                "value": actual_this["display_percent"] - plan_this["display_percent"],
            }
        activity = mapping["activity"]
        candidates.append({
            "candidate_id": original["candidate_id"],
            "claim_type": "source-attributed observation of planned-versus-actual progress; not a completed-action assertion",
            "proposed_claim": f"According to the Action Plan reporting week {args.reporting_period}, {activity} has cumulative contractor-planned progress and cumulative actual progress recorded in the workbook.",
            "reporting_period": args.reporting_period,
            "source_document_alias": original["source_document_alias"],
            "provenance": original["provenance"],
            "field_semantics": {
                "activities_plan_volume": {"BOQ": mapping["boq"], "last_period": mapping["plan_last"], "this_period": mapping["plan_this"], "cumulative": mapping["plan_cumulative"], "unit": mapping["unit"]},
                "date_plan": {"duration": mapping["duration"], "start": mapping["plan_start"], "finish": mapping["plan_finish"]},
                "activities_actual_volume": {"this_period": mapping["actual_volume_this"], "cumulative": mapping["actual_volume_cumulative"], "unit": mapping["unit"]},
                "contractor_plan_progress_percent": {"last_period": pct(mapping["contractor_plan_last"]), "this_period": plan_this, "cumulative": plan_cumulative},
                "actual_progress_percent": {"last_period": pct(mapping["actual_progress_last"]), "this_period": actual_this, "cumulative": actual_cumulative},
                "weekly_volume": {"until_previous_week": mapping["volume_until_previous_week"], "this_week": mapping["volume_this_week"], "until_this_week": mapping["volume_until_this_week"], "unit": mapping["unit"]},
            },
            "deterministic_relationship": {"cumulative_progress_variance": variance, "this_period_progress_variance": period_variance},
            "minimum_supporting_evidence": {
                "header_hierarchy": "Activities Plan Volume (BOQ/Last Period/This Period/Cumulative); Activities Actual Volume (This Period/Cumulative); Contractor Plan Progress% (Last/This/Cumulative); Actual Progress (Last/This/Cumulative).",
                "formula_evidence": "Cumulative progress cells and weekly-volume cells contain workbook formulas or cached formula results; exact formulas are retained in local schema evidence.",
            },
            "uncertainty": "The workbook establishes field labels and arithmetic relationships, but does not itself establish source authority, present-day currentness, or that actual progress equals completed scope.",
            "conflict_copy_forward_supersession": "No conflict, copy-forward, or supersession relationship is established for this row by the inspected workbook structure.",
            "proposed_disposition": "NEEDS_MORE_EVIDENCE",
        })
    output = {"schema_version": "st1-031-semantic-review-v1", "reporting_period": args.reporting_period, "candidate_count": len(candidates), "candidates": candidates}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output_outside_git": True, "candidate_count": len(candidates), "same_candidate_ids": [item["candidate_id"] for item in candidates]}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
