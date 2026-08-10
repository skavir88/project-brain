#!/usr/bin/env python3
"""Certify only the three explicitly approved ST1-041 source observations.

The runtime-local review package may contain real organizational content. It
is read locally and passed only over SSH stdin to the existing loopback API;
it is never logged or written into this repository.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
from pathlib import Path

POLICY = "st1-041-source-attributed-v1"
SOURCE_ID = "enterprise_ai_real_source_attributed_observation"
EXPECTED_IDS = {"review-ce24321a1153180b", "review-6afc7046e3178ed5", "review-8a906726a2d843ed"}
REMOTE = r'''import json,sys
from urllib.request import Request,urlopen
from urllib.error import HTTPError
payload=json.load(sys.stdin); result=[]
for record in payload["records"]:
 req=Request("http://127.0.0.1:8081/v1/records",data=json.dumps(record).encode(),method="POST",headers={"Content-Type":"application/json"})
 try:
  with urlopen(req,timeout=30) as response: intake=json.load(response); intake_status=response.status
 except HTTPError as error:
  if error.code != 409: raise
  intake=json.load(error); intake_status=error.code
 if not intake.get("fingerprint"): raise RuntimeError("intake did not return a candidate fingerprint")
 cert=Request(f"http://127.0.0.1:8081/v1/records/{intake['fingerprint']}/certify",data=json.dumps({"actor_id":"enterprise_ai_human_reviewer","policy_version":"st1-041-source-attributed-v1"}).encode(),method="POST",headers={"Content-Type":"application/json"})
 with urlopen(cert,timeout=30) as response: certification=json.load(response)
 result.append({"intake_status":intake_status,"certification":certification["disposition"],"policy":certification["policy_version"]})
print(json.dumps({"record_count":len(result),"intake_statuses":sorted(set(x["intake_status"] for x in result)),"certification_dispositions":sorted(set(x["certification"] for x in result)),"policies":sorted(set(x["policy"] for x in result))}))'''

def main() -> int:
    package_path = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / "st1-040-human-review-package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    candidates = package.get("candidates", [])
    if {candidate.get("candidate_id") for candidate in candidates} != EXPECTED_IDS:
        raise RuntimeError("ST1-041 review package does not match the approved candidate set")
    records = []
    for candidate in candidates:
        dates = candidate["date_semantics"]
        records.append({
            "source_id": SOURCE_ID, "record_id": f"st1-041-{candidate['candidate_id']}",
            "payload": {"source_id": SOURCE_ID, "statement": f"According to the explicitly approved source-attributed observation, {candidate['proposed_claim']}", "observation_type": candidate["claim_type"], "date_semantics": dates, "historical_source_attributed": True, "currentness": "not_established"},
            "provenance": {"source_reference": "runtime_local_only", "source_alias": candidate["source_alias"], "location": candidate["provenance"], "date_semantics": dates, "review_candidate_id": candidate["candidate_id"], "reviewer": "explicit_user_approval", "uncertainty": candidate["uncertainty"], "relationship_to_certified_history": candidate["relationship_to_certified_history"], "currentness": "not_established"},
        })
    encoded = base64.b64encode(REMOTE.encode("utf-8")).decode("ascii")
    command = f"python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], input=json.dumps({"records": records}, ensure_ascii=False), text=True, encoding="utf-8", capture_output=True, check=False)
    if run.returncode:
        raise RuntimeError(run.stderr.strip() or "controlled certification failed")
    print(run.stdout.strip())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
