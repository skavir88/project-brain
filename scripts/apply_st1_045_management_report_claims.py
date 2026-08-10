#!/usr/bin/env python3
"""Certify only the seven explicitly approved ST1-045 historical observations."""
from __future__ import annotations
import base64,json,os,subprocess
from pathlib import Path

POLICY="st1-045-management-report-historical-v1"
SOURCE_ID="enterprise_ai_real_management_historical_observation"
APPROVED={"review-f333b9bfde1a559b","review-ea1a83cdce84b6d5","review-ff2dc45413bdb78d","review-dfe620ebf93dda74","review-9a6ce38cd3bcbd0d","review-4fb77b9195158d9c","review-9bdc8f847c8430f7"}
DENIED={"review-d6445b78e21a7c66","review-2f07dc7770fdf3b7","review-6879ff40db50ba67"}
REMOTE=r'''import json,sys
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
 cert=Request(f"http://127.0.0.1:8081/v1/records/{intake['fingerprint']}/certify",data=json.dumps({"actor_id":"enterprise_ai_human_reviewer","policy_version":"st1-045-management-report-historical-v1"}).encode(),method="POST",headers={"Content-Type":"application/json"})
 try:
  with urlopen(cert,timeout=30) as response: certification=json.load(response); certification_status=response.status
 except HTTPError as error:
  if error.code!=409: raise
  certification=json.load(error); certification_status=error.code
 disposition=certification.get("disposition") or certification.get("error")
 if disposition not in {"certified","already_certified"}: raise RuntimeError("certification did not reach an allowed terminal state")
 result.append({"intake_status":intake_status,"certification_status":certification_status,"certification":disposition})
print(json.dumps({"record_count":len(result),"intake_statuses":sorted(set(x["intake_status"] for x in result)),"certification_statuses":sorted(set(x["certification_status"] for x in result)),"certification_dispositions":sorted(set(x["certification"] for x in result))}))'''

runtime=Path(os.environ["LOCALAPPDATA"])/"EnterpriseAI"/"runtime"
package=json.loads((runtime/"st1-044-human-review-package.json").read_text(encoding="utf-8"))
audit=json.loads((runtime/"st1-045-human-review-audit.json").read_text(encoding="utf-8"))
candidates={item["review_id"]:item for item in package["candidates"]}
if set(candidates)!=APPROVED|DENIED or {key for key,value in audit["decisions"].items() if value=="APPROVE"}!=APPROVED:
 raise SystemExit("ST1-045 approval scope mismatch")
records=[]
for review_id in sorted(APPROVED):
 c=candidates[review_id]
 records.append({"source_id":SOURCE_ID,"record_id":f"st1-045-{review_id}","payload":{"source_id":SOURCE_ID,"statement":c["claim"],"observation_type":c["classification"],"date_semantics":c["date_semantics"],"values":c["values"],"historical_source_attributed":True,"currentness":"not_established"},"provenance":{"source_reference":"runtime_local_only","source_alias":c["source_alias"],"page_provenance":c["provenance"],"date_semantics":c["date_semantics"],"review_candidate_id":review_id,"reviewer":"explicit_user_approval","uncertainty":c["uncertainty"],"relationship_to_certified_history":c["relationship_to_certified_knowledge"],"currentness":"not_established"}})
encoded=base64.b64encode(REMOTE.encode("utf-8")).decode("ascii")
command=f"python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
run=subprocess.run(["ssh","-o","BatchMode=yes","enterprise-ai-rdapp",command],input=json.dumps({"records":records},ensure_ascii=False),text=True,encoding="utf-8",capture_output=True)
if run.returncode: raise SystemExit(run.stderr.strip() or "controlled certification failed")
print(run.stdout.strip())
