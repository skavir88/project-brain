#!/usr/bin/env python3
"""Record exact ST1-045 decisions in local-only append-only review state."""
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

DECISIONS = {
    "review-f333b9bfde1a559b": "APPROVE", "review-ea1a83cdce84b6d5": "APPROVE",
    "review-ff2dc45413bdb78d": "APPROVE", "review-dfe620ebf93dda74": "APPROVE",
    "review-d6445b78e21a7c66": "NEEDS_MORE_EVIDENCE", "review-9a6ce38cd3bcbd0d": "APPROVE",
    "review-4fb77b9195158d9c": "APPROVE", "review-9bdc8f847c8430f7": "APPROVE",
    "review-2f07dc7770fdf3b7": "NEEDS_MORE_EVIDENCE", "review-6879ff40db50ba67": "CONFLICT",
}

runtime = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
package = json.loads((runtime / "st1-044-human-review-package.json").read_text(encoding="utf-8"))
if {item["review_id"] for item in package["candidates"]} != set(DECISIONS):
    raise SystemExit("ST1-045 review package mismatch")
counts = {value: list(DECISIONS.values()).count(value) for value in sorted(set(DECISIONS.values()))}
audit = {"schema_version":"st1-045-human-review-audit-v1","recorded_utc":datetime.now(UTC).isoformat(),"reviewer":"explicit_user_decision","decisions":DECISIONS,"certification_policy":"st1-045-management-report-historical-v1","certification_requested":True}
(runtime / "st1-045-human-review-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"review_candidate_count":len(DECISIONS),"decision_counts":counts,"audit_outside_git":True},separators=(",",":")))
