#!/usr/bin/env python3
"""Certify only the seven explicitly approved ST1-046 report observations."""
from __future__ import annotations

import base64
import json
import os
import subprocess
from pathlib import Path


POLICY = "st1-047-biweekly-management-report-v1"
SOURCE_ID = "enterprise_ai_real_biweekly_management_observation"
PERIOD = "1402/11/21–1402/12/05"
APPROVED = {
    "review-21425de2da8b6731", "review-5bc218514a8559ea", "review-6b3b32ae24ffbd32",
    "review-3194b3fa5b6a9ce7", "review-30279a777f7e6877", "review-64bffb6cef1da61f",
    "review-305764f860fc7ff6",
}

REMOTE = r'''import json,sys
from urllib.request import Request,urlopen
from urllib.error import HTTPError
payload=json.load(sys.stdin); result=[]
for record in payload["records"]:
 req=Request("http://127.0.0.1:8081/v1/records",data=json.dumps(record).encode(),method="POST",headers={"Content-Type":"application/json"})
 try:
  with urlopen(req,timeout=30) as response: intake=json.load(response); intake_status=response.status
 except HTTPError as error:
  if error.code!=409: raise
  intake=json.load(error); intake_status=error.code
 if not intake.get("fingerprint"): raise RuntimeError("intake did not return a candidate fingerprint")
 cert=Request(f"http://127.0.0.1:8081/v1/records/{intake['fingerprint']}/certify",data=json.dumps({"actor_id":"enterprise_ai_human_reviewer","policy_version":"st1-047-biweekly-management-report-v1"}).encode(),method="POST",headers={"Content-Type":"application/json"})
 try:
  with urlopen(cert,timeout=30) as response: certification=json.load(response); certification_status=response.status
 except HTTPError as error:
  if error.code!=409: raise
  certification=json.load(error); certification_status=error.code
 disposition=certification.get("disposition") or certification.get("error")
 if disposition not in {"certified","already_certified"}: raise RuntimeError("certification did not reach an allowed terminal state")
 result.append({"intake_status":intake_status,"certification_status":certification_status,"certification":disposition})
print(json.dumps({"record_count":len(result),"intake_statuses":sorted(set(x["intake_status"] for x in result)),"certification_statuses":sorted(set(x["certification_status"] for x in result)),"certification_dispositions":sorted(set(x["certification"] for x in result))}))'''


def statement(card: dict) -> str:
    evidence = "; ".join(card["minimum_supporting_evidence"])
    return f"According to the approved bi-weekly report for reporting period {PERIOD}, {card['proposed_claim']} Supporting source evidence: {evidence}"


def main() -> int:
    runtime = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
    package = json.loads((runtime / "st1-046-mrp-human-review.json").read_text(encoding="utf-8"))
    audit = json.loads((runtime / "st1-047-human-review-audit.json").read_text(encoding="utf-8"))
    cards = {item["review_id"]: item for item in package["review_cards"]}
    if set(cards) != APPROVED or set(audit["decisions"]) != APPROVED or set(audit["decisions"].values()) != {"APPROVE"}:
        raise SystemExit("ST1-047 approval scope mismatch")
    records = []
    for review_id in sorted(APPROVED):
        card = cards[review_id]
        provenance = {
            "source_reference": "runtime_local_only",
            "source_alias": card["source_alias"],
            "reporting_period": PERIOD,
            "report_date": "not_independently_established",
            "event_effective_date": "not_independently_established",
            "forecast_future_date": "not_applicable",
            "cell_provenance": card["provenance"],
            "review_candidate_id": review_id,
            "reviewer": "explicit_user_approval",
            "uncertainty": card["uncertainty"],
            "source_attributed_only": True,
            "currentness": "not_established",
            "reporting_period_relation_to_prior_certified": "newer",
        }
        records.append({
            "source_id": SOURCE_ID,
            "record_id": f"st1-047-{review_id}",
            "payload": {
                "source_id": SOURCE_ID,
                "statement": statement(card),
                "observation_type": card["claim_type"],
                "reporting_period": PERIOD,
                "source_attributed_only": True,
                "currentness": "not_established",
            },
            "provenance": provenance,
        })
    encoded = base64.b64encode(REMOTE.encode("utf-8")).decode("ascii")
    command = f"python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
    run = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command],
        input=json.dumps({"records": records}, ensure_ascii=False), text=True, encoding="utf-8", capture_output=True,
    )
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "controlled certification failed")
    print(run.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
