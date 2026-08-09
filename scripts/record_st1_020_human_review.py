#!/usr/bin/env python3
"""Persist exact ST1-020 reviewer decisions locally and write aggregate-only evidence."""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


DECISIONS = {
    "review-6068e90ef3dcc7f5": "NEEDS_MORE_EVIDENCE",
    "review-931128fcc74b906b": "NEEDS_MORE_EVIDENCE",
    "review-9fcb42cda10a3ad4": "REJECT",
    "review-5ef2d203b9c04eac": "REJECT",
    "review-bfa0e7f6094be4d7": "REJECT",
    "review-605825873271b341": "REJECT",
    "review-86ea13b70074986c": "REJECT",
    "review-ec49c6e6018e3545": "NEEDS_MORE_EVIDENCE",
    "review-57365ab6285271d3": "NEEDS_MORE_EVIDENCE",
    "review-ae4e245266ab7c8c": "REJECT",
    "review-7ac5762361a2da21": "REJECT",
    "review-e009489fdc4854ee": "REJECT",
    "review-58f0b6567aca214e": "REJECT",
    "review-fc512d62c357bdad": "REJECT",
    "review-acc28176e7c3c368": "REJECT",
}
ALLOWED = {"APPROVE", "REJECT", "NEEDS_MORE_EVIDENCE", "CONFLICT"}


def main() -> int:
    runtime = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
    package = json.loads((runtime / "st1-019-human-review-package.json").read_text(encoding="utf-8"))
    candidate_ids = {item["candidate_id"] for item in package["candidates"]}
    if candidate_ids != set(DECISIONS) or not set(DECISIONS.values()) <= ALLOWED:
        raise RuntimeError("decision set is not a complete exact match for the review package")
    audit = {
        "schema_version": "st1-020-review-audit-v1",
        "recorded_utc": datetime.now(UTC).isoformat(),
        "reviewer": "explicit_user_decision",
        "selection_alias": package["selection_alias"],
        "decisions": DECISIONS,
        "certification_executed": False,
    }
    (runtime / "st1-020-human-review-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = Counter(DECISIONS.values())
    evidence = {
        "schema_version": "st1-020-sanitized-human-review-summary-v1",
        "selection_alias": package["selection_alias"],
        "review_candidate_count": len(candidate_ids),
        "reviewer": "explicit_user_decision",
        "decision_counts": {key: counts.get(key, 0) for key in sorted(ALLOWED)},
        "certification_executed": False,
        "unresolved_candidate_count": counts["NEEDS_MORE_EVIDENCE"] + counts["CONFLICT"],
        "rejected_external_or_educational_candidate_count": 11,
        "raw_content_or_locator_versioned": False,
    }
    target = Path("evidence/sanitized/2026-08-09-st1-020-human-review-summary.json")
    target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
