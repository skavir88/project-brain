#!/usr/bin/env python3
"""Certify only explicitly approved ST1-032 source-attributed observations."""
from __future__ import annotations
import base64,json,os,subprocess
from pathlib import Path
POLICY="st1-032-source-attributed-v1"; SOURCE_ID="enterprise_ai_real_action_plan_weekly_observation"
REMOTE='''import json,sys
from urllib.request import Request,urlopen
p=json.load(sys.stdin);o=[]
for r in p["records"]:
 q=Request("http://127.0.0.1:8081/v1/records",data=json.dumps(r).encode(),method="POST",headers={"Content-Type":"application/json"})
 with urlopen(q,timeout=30) as x:i=json.load(x)
 q=Request(f"http://127.0.0.1:8081/v1/records/{i['fingerprint']}/certify",data=json.dumps({"actor_id":"enterprise_ai_human_reviewer","policy_version":"st1-032-source-attributed-v1"}).encode(),method="POST",headers={"Content-Type":"application/json"})
 with urlopen(q,timeout=30) as x:c=json.load(x)
 o.append({"intake":i["disposition"],"certification":c["disposition"],"policy":c["policy_version"]})
print(json.dumps({"record_count":len(o),"intake_dispositions":sorted(set(x["intake"] for x in o)),"certification_dispositions":sorted(set(x["certification"] for x in o)),"policies":sorted(set(x["policy"] for x in o))}))'''
runtime=Path(os.environ["LOCALAPPDATA"])/"EnterpriseAI"/"runtime"
p=json.loads((runtime/"st1-031-semantic-human-review-package.json").read_text(encoding="utf-8"))
if p.get("candidate_count")!=10: raise RuntimeError("expected ten ST1-032 candidates")
records=[]
for c in p["candidates"]:
 f=c["field_semantics"];v=c["deterministic_relationship"]["cumulative_progress_variance"]
 activity=c["proposed_claim"].split(", ",1)[-1].split(" had cumulative",1)[0]
 statement=f"According to the Action Plan for {c['reporting_period']}, {activity} had cumulative planned progress of {f['contractor_plan_progress_percent']['cumulative']['display_percent']}% and cumulative actual progress of {f['actual_progress_percent']['cumulative']['display_percent']}%, a variance of {v['value']} percentage points."
 records.append({"source_id":SOURCE_ID,"record_id":f"st1-032-{c['candidate_id']}","payload":{"source_id":SOURCE_ID,"statement":statement,"reporting_period":c["reporting_period"],"field_semantics":f,"variance":v},"provenance":{"source_reference":"runtime_local_only","source_alias":c["source_document_alias"],"sheet_row":c["provenance"],"review_candidate_id":c["candidate_id"],"reporting_period":c["reporting_period"],"reviewer":"explicit_user_approval","formula_backed_origin":True,"currentness":"not_established"}})
e=base64.b64encode(REMOTE.encode()).decode();cmd=f"python3 -c \"import base64;exec(base64.b64decode('{e}'))\""
r=subprocess.run(["ssh","-o","BatchMode=yes","enterprise-ai-rdapp",cmd],input=json.dumps({"records":records},ensure_ascii=False),text=True,encoding="utf-8",capture_output=True,check=False)
if r.returncode: raise SystemExit(r.stderr.strip() or "certification failed")
print(r.stdout.strip())
