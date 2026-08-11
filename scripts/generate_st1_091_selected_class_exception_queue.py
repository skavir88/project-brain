#!/usr/bin/env python3
"""Generate an exception-only selected-class review pack from ST1-090 routing outcomes.

This generator is deterministic, local-only, and non-mutating. It excludes
`policy_automatic` items from individual review output and emits only:

- human_required
- reject_or_quarantine
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIMULATOR = ROOT / "scripts" / "simulate_st1_090_selected_class_operating_model.py"


def run_simulator(batch: Path) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SIMULATOR), "--batch", str(batch)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True, help="Path to the ST1-090 batch JSON file")
    args = parser.parse_args()

    simulation = run_simulator(args.batch)
    evaluated = simulation.get("evaluated_records", [])
    if not isinstance(evaluated, list):
        raise SystemExit("simulator output missing evaluated_records list")

    exceptions: list[dict[str, object]] = []
    for item in evaluated:
        if not isinstance(item, dict):
            continue
        outcome = item.get("routing_outcome")
        if outcome == "policy_automatic":
            continue
        exceptions.append(
            {
                "record_id": item.get("record_id"),
                "source_id": item.get("source_id"),
                "fact_class": item.get("fact_class"),
                "routing_outcome": outcome,
                "reason_codes": item.get("reason_codes", []),
                "review_lane": "quarantine" if outcome == "reject_or_quarantine" else "human_review",
            }
        )

    output = {
        "schema_version": "st1-091-selected-class-exception-queue-v1",
        "candidate_class_id": simulation.get("candidate_class_id"),
        "project_scope": simulation.get("project_scope"),
        "mutates_real_state": False,
        "batch_summary": simulation.get("batch_summary"),
        "exception_summary": {
            "exception_count": len(exceptions),
            "policy_automatic_items_excluded_from_review_output": True,
            "human_review_count": sum(1 for item in exceptions if item["routing_outcome"] == "human_required"),
            "quarantine_count": sum(1 for item in exceptions if item["routing_outcome"] == "reject_or_quarantine"),
        },
        "review_pack": exceptions,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
