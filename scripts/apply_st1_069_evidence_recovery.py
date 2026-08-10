#!/usr/bin/env python3
"""Record ST1-069 bounded evidence-recovery observations without authority."""
from __future__ import annotations
import base64, subprocess

REMOTE = r'''
import hashlib,json,os,psycopg
from datetime import datetime,timezone
def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
rows=[
 ('governance_authority_evidence','MISSING','authorized_runtime_and_metadata_review','no controlled organizational governance-role evidence was found','CEO / Executive Governance Authority','maroon_pilot_project','st1-069-runtime-metadata-review','not_found_in_already_authorized_state','local_runtime_metadata_and_authorized_artifact_review','not_assessed'),
 ('role_identity_evidence','MISSING','authorized_runtime_and_metadata_review','no controlled organizational Project Controls/PMO role evidence was found','Project Controls / PMO accountable role','maroon_pilot_project','st1-069-runtime-metadata-review','not_found_in_already_authorized_state','local_runtime_metadata_and_authorized_artifact_review','not_assessed'),
 ('source_control_evidence','PARTIAL','previously_authorized_bounded_extraction','a bounded reporting-oriented corpus was previously extracted, but ownership/control by Project Controls was not established','controlled recurring Project Controls progress/status report or workbook','maroon_pilot_project','runtime-4adcf886b2db','deterministic_local_artifact_term_and_structure_review','prior_authorized_read_only_local_extraction','low'),
 ('reporting_time_evidence','PARTIAL','previously_authorized_bounded_extraction','reporting-period indicators were observed in the bounded extraction, but no approved controlled-report convention was established','controlled recurring Project Controls progress/status report or workbook','maroon_pilot_project','runtime-4adcf886b2db','deterministic_local_artifact_term_and_structure_review','prior_authorized_read_only_local_extraction','low')]
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'],port=os.environ.get('INGESTION_DB_PORT','5432'),dbname=os.environ['INGESTION_DB_NAME'],user=os.environ['INGESTION_DB_USER'],password=os.environ['INGESTION_DB_PASSWORD']) as c:
 with c.cursor() as q:
  for category,status,typ,fact,subject,project,ref,method,acq,confidence in rows:
   payload={'category':category,'status':status,'subject':subject,'project':project,'reference':ref,'fact':fact}
   q.execute("INSERT INTO ingestion.sdas_governance_evidence_observations(evidence_category,status,evidence_type,asserted_fact,subject_class,scope,evidence_reference,evidence_fingerprint,verification_method,acquisition_provenance,confidence,event_hash) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s) ON CONFLICT(event_hash) DO NOTHING",(category,status,typ,fact,subject,json.dumps({'project_scope':project}),ref,h(payload),method,acq,confidence,h({'event':payload})))
  q.execute("SELECT evidence_category,status,count(*) FROM ingestion.sdas_governance_evidence_observations WHERE evidence_reference IN ('st1-069-runtime-metadata-review','runtime-4adcf886b2db') GROUP BY evidence_category,status ORDER BY evidence_category,status")
  print(json.dumps({'observations':[{'category':a,'status':b,'count':n} for a,b,n in q.fetchall()],'authority_created':False},separators=(',',':')))
'''
def main():
 p=base64.b64encode(REMOTE.encode()).decode(); cmd="docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('"+p+"'))\""
 r=subprocess.run(['ssh','-o','BatchMode=yes','enterprise-ai-rdapp',cmd],text=True,capture_output=True)
 if r.returncode: raise SystemExit(r.stderr.strip() or 'ST1-069 evidence recovery failed')
 print(r.stdout.strip())
if __name__=='__main__': main()
