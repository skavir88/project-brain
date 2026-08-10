#!/usr/bin/env python3
"""Create one native synthetic SDAS v0.2 policy decision; never certify it."""
from __future__ import annotations
import base64, subprocess

REMOTE = '''import hashlib,json,os,psycopg
from datetime import datetime,timezone
from urllib.request import Request,urlopen
def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
now=datetime.now(timezone.utc); actor="sahra-native-synthetic-service"; source="sahra-native-synthetic-source-v1"; policy="sdas-low-risk-native"
with psycopg.connect(host=os.environ["INGESTION_DB_HOST"],port=os.environ.get("INGESTION_DB_PORT","5432"),dbname=os.environ["INGESTION_DB_NAME"],user=os.environ["INGESTION_DB_USER"],password=os.environ["INGESTION_DB_PASSWORD"]) as c:
 with c.cursor() as q:
  q.execute("INSERT INTO ingestion.sdas_actor_registry(actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality) VALUES (%s,'service','[\\\"synthetic_low_risk\\\"]'::jsonb,'runtime_service_identity',%s,'native') ON CONFLICT DO NOTHING",(actor,now))
  q.execute("INSERT INTO ingestion.sdas_source_registry(source_id,source_type,system_location_identity,owner_actor_id,business_purpose,authority_status,authority_scope,evidence_quality) VALUES (%s,'synthetic_test','private_runtime',%s,'SDAS native chain','declared_unverified','[\\\"synthetic_only\\\"]'::jsonb,'native') ON CONFLICT DO NOTHING",(source,actor))
  obj=h({"source":source,"object":"001"}); ah=h({"source":source,"object":obj})
  q.execute("INSERT INTO ingestion.sdas_acquisition_events(source_id,acquired_at,actor_id,acquisition_method,source_reference,original_fingerprint,size_bytes,media_type,evidence_quality,evidence_hash) VALUES (%s,%s,%s,'generated_synthetic','native://sdas/001',%s,128,'application/json','native',%s) ON CONFLICT (evidence_hash) DO NOTHING RETURNING acquisition_event_id",(source,now,actor,obj,ah)); row=q.fetchone()
  if row: acq=row[0]
  else: q.execute("SELECT acquisition_event_id FROM ingestion.sdas_acquisition_events WHERE evidence_hash=%s",(ah,)); acq=q.fetchone()[0]
  q.execute("INSERT INTO ingestion.sdas_transformations(acquisition_event_id,transformation_type,tool_name,tool_version,transformed_at,input_fingerprint,output_fingerprint,deterministic,extraction_coordinates,evidence_quality,evidence_hash) VALUES (%s,'canonicalization','enterprise-ai-ingestion','0.2',%s,%s,%s,true,'{}'::jsonb,'native',%s) ON CONFLICT DO NOTHING",(acq,now,obj,h({"out":obj}),h({"acq":acq})))
  q.execute("INSERT INTO ingestion.sdas_policy_versions(policy_id,policy_version,effective_from,enabled,allowed_source_types,allowed_data_classes,required_evidence,risk_class,decision_reason_codes,actor_authority_requirements,policy_hash) VALUES (%s,'v1',%s,true,'[\\\"synthetic_test\\\"]'::jsonb,'[\\\"synthetic_low_risk\\\"]'::jsonb,'[\\\"source\\\",\\\"acquisition\\\",\\\"integrity\\\",\\\"transformation\\\",\\\"validation\\\"]'::jsonb,'low','[\\\"all_native_evidence_present\\\"]'::jsonb,'[\\\"service_identity\\\"]'::jsonb,%s) ON CONFLICT DO NOTHING",(policy,now,h({"policy":policy,"v":"v1"})))
req=Request("http://127.0.0.1:8080/v1/records",data=json.dumps({"source_id":source,"record_id":"sdas-native-synthetic-001","payload":{"source_id":source,"data_class":"synthetic_low_risk"},"provenance":{"source_reference":"native://sdas/001","acquisition_event_id":acq,"evidence_quality":"native"},"observed_at":now.isoformat()}).encode(),method="POST",headers={"Content-Type":"application/json"})
with urlopen(req,timeout=20) as r: intake=json.load(r)
if intake.get("disposition")!="certification_candidate": raise RuntimeError("candidate failed")
fp=intake["fingerprint"]
with psycopg.connect(host=os.environ["INGESTION_DB_HOST"],port=os.environ.get("INGESTION_DB_PORT","5432"),dbname=os.environ["INGESTION_DB_NAME"],user=os.environ["INGESTION_DB_USER"],password=os.environ["INGESTION_DB_PASSWORD"]) as c:
 with c.cursor() as q:
  q.execute("INSERT INTO ingestion.sdas_policy_decisions(record_fingerprint,policy_id,policy_version,approval_mode,decision_actor,decision_reasons,evidence_quality,decision_hash) VALUES (%s,%s,'v1','policy_automatic','sahra_policy_engine','[\\\"all_required_native_evidence_present\\\"]'::jsonb,'native',%s) ON CONFLICT DO NOTHING",(fp,policy,h({"fp":fp,"d":"auto"})))
  q.execute("SELECT source_fingerprint FROM ingestion.certified_knowledge_items")
  for (old,) in q.fetchall(): q.execute("INSERT INTO ingestion.sdas_policy_decisions(record_fingerprint,policy_id,policy_version,approval_mode,decision_actor,decision_reasons,evidence_quality,decision_hash) VALUES (%s,%s,'simulation-v1','human_required','sahra_policy_engine','[\\\"missing_native_evidence\\\"]'::jsonb,'reconstructed',%s) ON CONFLICT DO NOTHING",(old,policy,h({"fp":old,"d":"human"})))
print(json.dumps({"native_record_disposition":"certification_candidate","policy_auto_approved_records":1,"simulation_human_review_required":49,"automatic_certification_performed":False}))'''

def main():
 e=base64.b64encode(REMOTE.encode()).decode(); cmd=f"docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('{e}'))\""
 r=subprocess.run(['ssh','-o','BatchMode=yes','enterprise-ai-rdapp',cmd],text=True,capture_output=True)
 if r.returncode: raise SystemExit(r.stderr.strip() or 'native policy failed')
 print(r.stdout.strip())
if __name__=='__main__': main()
