#!/usr/bin/env python3
"""Record the exact ST1-041 reviewer decisions in local append-only state."""
from __future__ import annotations
import json
import os
from datetime import UTC, datetime
from pathlib import Path

DECISIONS = {
    "review-ce24321a1153180b": "APPROVE",
    "review-6afc7046e3178ed5": "APPROVE",
    "review-8a906726a2d843ed": "APPROVE",
}
runtime = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
package = json.loads((runtime / "st1-040-human-review-package.json").read_text(encoding="utf-8"))
if {item["candidate_id"] for item in package["candidates"]} != set(DECISIONS):
    raise SystemExit("review package mismatch")
audit = {"schema_version":"st1-041-human-review-audit-v1","recorded_utc":datetime.now(UTC).isoformat(),"reviewer":"explicit_user_decision","decisions":DECISIONS,"certification_policy":"st1-041-source-attributed-v1","certification_requested":True}
(runtime / "st1-041-human-review-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"review_candidate_count":3,"decision_counts":{"APPROVE":3,"REJECT":0,"NEEDS_MORE_EVIDENCE":0,"CONFLICT":0},"audit_outside_git":True}, separators=(",",":")))
