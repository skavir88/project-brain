#!/usr/bin/env python3
"""Certify only explicitly approved ST1-026 source-attributed observations.

The local-only review package supplies organizational content and raw locators.
This repository script transfers that material only over SSH stdin to the
loopback controlled API; it neither writes nor logs it locally.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
from pathlib import Path


POLICY = "st1-026-source-attributed-v1"
SOURCE_ID = "enterprise_ai_real_currentness_observation"
REMOTE = r'''import json, sys
from urllib.request import Request, urlopen
payload=json.load(sys.stdin)
result=[]
for record in payload["records"]:
    req=Request("http://127.0.0.1:8081/v1/records",data=json.dumps(record).encode(),method="POST",headers={"Content-Type":"application/json"})
    with urlopen(req,timeout=30) as response: intake=json.load(response)
    fingerprint=intake["fingerprint"]
    cert=Request(f"http://127.0.0.1:8081/v1/records/{fingerprint}/certify",data=json.dumps({"actor_id":"enterprise_ai_human_reviewer","policy_version":"st1-026-source-attributed-v1"}).encode(),method="POST",headers={"Content-Type":"application/json"})
    with urlopen(cert,timeout=30) as response: certification=json.load(response)
    result.append({"intake":intake["disposition"],"certification":certification["disposition"],"policy":certification["policy_version"]})
print(json.dumps({"record_count":len(result),"intake_dispositions":sorted(set(x["intake"] for x in result)),"certification_dispositions":sorted(set(x["certification"] for x in result)),"policies":sorted(set(x["policy"] for x in result))}))
'''


def main() -> int:
    package_path = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / "st1-025-human-review-package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    if package.get("candidate_count") != 7 or len(package.get("candidates", [])) != 7:
        raise RuntimeError("expected exactly seven reviewed ST1-026 candidates")
    records = []
    for candidate in package["candidates"]:
        statement = (
            f"According to the Action Plan issued on {candidate['document_date']}, "
            f"the following condition or plan was reported for {candidate['affected_work_package']}: "
            f"{candidate['minimum_supporting_evidence']}"
        )
        records.append({
            "source_id": SOURCE_ID,
            "record_id": f"st1-026-{candidate['candidate_id']}",
            "payload": {
                "source_id": SOURCE_ID,
                "statement": statement,
                "category": candidate["category"],
                "document_issue_date": candidate["document_date"],
                "event_effective_date": None,
                "future_plan_modality_preserved": True,
            },
            "provenance": {
                "source_reference": candidate["source_relative_locator"],
                "source_alias": candidate["source_workbook_alias"],
                "sheet_and_cells": candidate["provenance"]["sheet_and_cells"],
                "document_issue_date": candidate["document_date"],
                "date_type": candidate["date_type"],
                "event_effective_date": "not_independently_established",
                "review_candidate_id": candidate["candidate_id"],
                "reviewer": "explicit_user_approval",
                "duplicate_or_copy_forward": candidate["duplicate_or_copy_forward"],
            },
        })
    encoded = base64.b64encode(REMOTE.encode("utf-8")).decode("ascii")
    remote_command = f"python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", remote_command], input=json.dumps({"records": records}, ensure_ascii=False), text=True, encoding="utf-8", capture_output=True, check=False)
    if run.returncode != 0:
        raise RuntimeError(run.stderr.strip() or "remote controlled certification failed")
    print(run.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
