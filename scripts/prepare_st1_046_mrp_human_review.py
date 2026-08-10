#!/usr/bin/env python3
"""Build a local-only ST1-046 Human Review package from bounded workbook cells.

The package retains organizational content and source locators only under the
operator's local runtime directory.  This script does not write to a platform
service or to the repository evidence directory.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path


SOURCE_ALIAS = "source-a08f4a79cf2116b1"
REPORTING_PERIOD = "1402/11/21–1402/12/05"


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def cell_map(sheet: dict) -> dict[str, dict]:
    return {cell["cell"]: cell for cell in sheet["cells"]}


def review_id(kind: str, cells: list[str]) -> str:
    basis = f"st1-046|{SOURCE_ALIAS}|{kind}|{'|'.join(cells)}"
    return "review-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def main() -> int:
    source = runtime("st1-046-twrp-cells.json")
    output = runtime("st1-046-mrp-human-review.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    sheets = {sheet["sheet_index"]: sheet for sheet in data["sheets"]}
    summary = cell_map(sheets[1])
    cover = cell_map(sheets[4])
    events = cell_map(sheets[5])
    issues = cell_map(sheets[6])
    activities = cell_map(sheets[7])
    procurement = cell_map(sheets[9])
    construction = cell_map(sheets[10])

    def value(mapping: dict[str, dict], ref: str):
        item = mapping.get(ref)
        if not item or item["value"] in (None, ""):
            raise ValueError(f"required source cell unavailable: {ref}")
        return item["value"]

    def card(kind: str, claim: str, cells: list[tuple[int, str]], evidence: list[str], **extra):
        refs = [ref for _, ref in cells]
        return {
            "review_id": review_id(kind, refs),
            "proposed_claim": claim,
            "reporting_period": REPORTING_PERIOD,
            "source_alias": SOURCE_ALIAS,
            "provenance": [
                {
                    "sheet_index": index,
                    "sheet_name": sheets[index]["sheet_name"],
                    "cell": ref,
                    "literal_vs_formula": next(
                        c["literal_vs_formula"]
                        for c in sheets[index]["cells"]
                        if c["cell"] == ref
                    ),
                }
                for index, ref in cells
            ],
            "minimum_supporting_evidence": evidence,
            "source_attributed_only": True,
            "not_current_status": True,
            "not_authority_proof": True,
            "proposed_disposition": "NEEDS_HUMAN_REVIEW",
            **extra,
        }

    # Values are included only in the local-only review package.  The
    # repository evidence records only aggregate, non-content-bearing facts.
    cards = [
        card(
            "overall_mdl_progress",
            "The report's MDL Progress total lists an actual and a plan value for its reporting period.",
            [(1, "J3"), (1, "K3"), (4, "R8")],
            [f"MDL actual={value(summary, 'J3')}", f"MDL plan={value(summary, 'K3')}", value(cover, "R8")],
            claim_type="observation",
            uncertainty="The workbook contains more than one progress methodology; this card does not equate the metric with overall completion or delay.",
        ),
        card(
            "primavera_total_progress",
            "The report's Primavera Progress total lists an actual and a plan value for its reporting period.",
            [(1, "F3"), (1, "G3"), (4, "R8")],
            [f"Primavera actual={value(summary, 'F3')}", f"Primavera plan={value(summary, 'G3')}", value(cover, "R8")],
            claim_type="observation",
            uncertainty="Metric ownership, calculation basis, and relationship to the MDL figure require reviewer confirmation; negative/positive variance alone is not a delay finding.",
        ),
        card(
            "m5_engineering_progress",
            "The report lists actual and plan values for the Marun 5 engineering summary line.",
            [(1, "J7"), (1, "K7"), (1, "A7"), (1, "C7"), (4, "R8")],
            [value(summary, "A7"), value(summary, "C7"), f"actual={value(summary, 'J7')}", f"plan={value(summary, 'K7')}"],
            claim_type="observation",
            uncertainty="This is a discipline/site reporting metric, not an independently validated project-wide status conclusion.",
        ),
        card(
            "period_activity_cluster",
            "The report records a cluster of procurement and construction activities across named project sites during the reporting period.",
            [(5, "C13"), (5, "C17"), (5, "C32"), (5, "C38"), (7, "C10"), (7, "C17"), (7, "C25")],
            [value(events, "C13"), value(events, "C17"), value(events, "C32"), value(events, "C38"), value(activities, "C10"), value(activities, "C17"), value(activities, "C25")],
            claim_type="observation",
            uncertainty="Listed activities demonstrate that activities were reported, not their completion, quality, timeliness, or current state.",
        ),
        card(
            "engineering_constraints",
            "The report identifies engineering/document-control and design-input constraints as issues for the reporting period.",
            [(6, "C14"), (6, "C17"), (6, "C21"), (6, "C23"), (6, "C24")],
            [value(issues, "C14"), value(issues, "C17"), value(issues, "C21"), value(issues, "C23"), value(issues, "C24")],
            claim_type="issue",
            uncertainty="The report does not, by itself, establish the root cause, scope, later resolution, or current persistence of these constraints.",
        ),
        card(
            "procurement_package_constraint",
            "The report lists incomplete finalization of the project's procurement-package list as a procurement concern.",
            [(9, "C11"), (4, "R8")],
            [value(procurement, "C11"), value(cover, "R8")],
            claim_type="issue",
            uncertainty="The scope, materiality, ownership, and subsequent resolution are not established by this row alone.",
        ),
        card(
            "construction_payment_stoppage",
            "The report states that related execution activities at three named sites were stopped because contractor claims had not been paid.",
            [(10, "C10"), (10, "C11"), (10, "C12"), (10, "C13"), (10, "C15"), (10, "C16"), (4, "R8")],
            [value(construction, "C10"), value(construction, "C11"), value(construction, "C12"), value(construction, "C13"), value(construction, "C15"), value(construction, "C16")],
            claim_type="issue",
            uncertainty="This is a source-attributed statement for the reporting period; it does not establish that the stoppage continued afterward or its exact operational/financial impact.",
        ),
    ]
    package = {
        "schema_version": "st1-046-mrp-human-review-v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "source_alias": SOURCE_ALIAS,
        "reporting_period": REPORTING_PERIOD,
        "candidate_count": len(cards),
        "review_cards": cards,
        "boundaries": {
            "read_only_source": True,
            "raw_content_outside_git": True,
            "platform_persistence": False,
            "external_model_use": False,
            "automatic_certification": False,
        },
    }
    output.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"candidate_count": len(cards), "output_outside_git": True, "review_ids": [x["review_id"] for x in cards]}, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
