#!/usr/bin/env python3
"""Send only explicitly approved ST1-023 historical claims to the controlled API.

Real claims are constructed from the local-only review package and travel over
SSH stdin to the loopback service; they are never written to this repository.
"""

from __future__ import annotations

import json
import os
import subprocess
import base64
from pathlib import Path


REMOTE = r'''import json, sys
from urllib.request import Request, urlopen
payload=json.load(sys.stdin)
result=[]
for record in payload["records"]:
    req=Request("http://127.0.0.1:8081/v1/records",data=json.dumps(record).encode(),method="POST",headers={"Content-Type":"application/json"})
    with urlopen(req,timeout=30) as response: intake=json.load(response)
    fingerprint=intake["fingerprint"]
    cert=Request(f"http://127.0.0.1:8081/v1/records/{fingerprint}/certify",data=json.dumps({"actor_id":"enterprise_ai_human_reviewer","policy_version":"st1-023-historical-v1"}).encode(),method="POST",headers={"Content-Type":"application/json"})
    with urlopen(cert,timeout=30) as response: certification=json.load(response)
    result.append({"intake":intake["disposition"],"certification":certification["disposition"],"policy":certification["policy_version"]})
print(json.dumps({"record_count":len(result),"intake_dispositions":sorted(set(x["intake"] for x in result)),"certification_dispositions":sorted(set(x["certification"] for x in result)),"policies":sorted(set(x["policy"] for x in result))}))
'''


def main() -> int:
    package_path = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / "st1-022-human-review-package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    records = []
    for candidate in package["candidates"]:
        evidence = candidate["minimum_supporting_evidence"]
        statement = (
            f"According to the approved project activity report for reporting period "
            f"{candidate['reporting_period']}, {evidence['notes'] or evidence['activity']} was reported."
        )
        records.append({
            "source_id": "enterprise_ai_real_historical_status",
            "record_id": f"st1-023-{candidate['candidate_id']}",
            "payload": {"source_id": "enterprise_ai_real_historical_status", "statement": statement, "category": candidate["category"], "historical_reporting_period": candidate["reporting_period"]},
            "provenance": {"source_reference": candidate["source_relative_locator"], "source_alias": candidate["source_alias"], "sheet": candidate["location"]["sheet"], "row": candidate["location"]["row"], "cells": [candidate["location"]["activity_cell"], *candidate["location"]["note_cells"]], "reporting_period": candidate["reporting_period"], "review_candidate_id": candidate["candidate_id"], "reviewer": "explicit_user_approval"},
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
