#!/usr/bin/env python3
"""Record the seven exact ST1-046 approvals in local append-only state."""
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path


DECISIONS = {
    "review-21425de2da8b6731": "APPROVE",
    "review-5bc218514a8559ea": "APPROVE",
    "review-6b3b32ae24ffbd32": "APPROVE",
    "review-3194b3fa5b6a9ce7": "APPROVE",
    "review-30279a777f7e6877": "APPROVE",
    "review-64bffb6cef1da61f": "APPROVE",
    "review-305764f860fc7ff6": "APPROVE",
}


def main() -> int:
    runtime = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
    package = json.loads((runtime / "st1-046-mrp-human-review.json").read_text(encoding="utf-8"))
    if {item["review_id"] for item in package["review_cards"]} != set(DECISIONS):
        raise SystemExit("ST1-047 review package mismatch")
    audit = {
        "schema_version": "st1-047-human-review-audit-v1",
        "recorded_utc": datetime.now(UTC).isoformat(),
        "reviewer": "explicit_user_decision",
        "decisions": DECISIONS,
        "certification_policy": "st1-047-biweekly-management-report-v1",
        "certification_requested": True,
    }
    (runtime / "st1-047-human-review-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"review_candidate_count": 7, "approved": 7, "audit_outside_git": True}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
