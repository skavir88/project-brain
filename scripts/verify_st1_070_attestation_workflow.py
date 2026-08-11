#!/usr/bin/env python3
"""Verify ST1-070 lifecycle guards using a rolled-back synthetic transaction."""
from __future__ import annotations

import base64
import subprocess

REMOTE = r'''
import hashlib,json,os,psycopg
from datetime import datetime,timezone
def h(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
now=datetime.now(timezone.utc); out={}
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'],port=os.environ.get('INGESTION_DB_PORT','5432'),dbname=os.environ['INGESTION_DB_NAME'],user=os.environ['INGESTION_DB_USER'],password=os.environ['INGESTION_DB_PASSWORD']) as c:
 with c.cursor() as q:
  out['real_attestations']=q.execute("SELECT count(*) FROM ingestion.sdas_controlled_attestations").fetchone()[0]
  out['real_active_delegations']=q.execute("SELECT count(*) FROM ingestion.sdas_active_delegation_bootstrap").fetchone()[0]
  out['runtime_update_or_delete_grants']=q.execute("SELECT has_table_privilege('enterprise_ai_ingestion_runtime','ingestion.sdas_controlled_attestations','UPDATE') OR has_table_privilege('enterprise_ai_ingestion_runtime','ingestion.sdas_controlled_attestations','DELETE') OR has_table_privilege('enterprise_ai_ingestion_runtime','ingestion.sdas_controlled_attestation_events','UPDATE') OR has_table_privilege('enterprise_ai_ingestion_runtime','ingestion.sdas_controlled_attestation_events','DELETE')").fetchone()[0]
  signer='st1-070-test-signer'; verifier='st1-070-test-verifier'
  q.execute("INSERT INTO ingestion.sdas_actor_registry (actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality) VALUES (%s,'synthetic signer','[]'::jsonb,'synthetic',%s,'native'),(%s,'synthetic verifier','[]'::jsonb,'synthetic',%s,'native')",(signer,now,verifier,now))
  def add(a,k,payload):
   q.execute("INSERT INTO ingestion.sdas_controlled_attestations (attestation_id,attestation_kind,attestation_version,project_scope,subject_role_class,attestation_payload,effective_from,signer_actor_id,signed_artifact_reference,signed_artifact_fingerprint,acquisition_provenance,event_hash) VALUES (%s,%s,'v1','synthetic_project','synthetic role',%s::jsonb,%s,%s,'synthetic',%s,'synthetic',%s)",(a,k,json.dumps(payload),now,signer,h({'artifact':a}),h({'create':a})))
   q.execute("INSERT INTO ingestion.sdas_controlled_attestation_events (attestation_id,transition_state,reason_code,evidence_reference,evidence_fingerprint,event_hash,event_at) VALUES (%s,'SUBMITTED','synthetic','synthetic',%s,%s,%s)",(a,h({'s':a}),h({'se':a}),now))
  p1={'governance_role_class':'synthetic governance','authority_basis':'controlled','scope':'synthetic_project','expiry_or_revocation_rule':'event','approval_method':'synthetic'}
  p2={'accountable_role_class':'synthetic PMO','report_classes':['synthetic_report'],'permitted_fact_classes':['reported_actual'],'prohibited_fact_classes':['claim'],'scope':'synthetic_project','approval_method':'synthetic'}
  p3={'source_report_class':'synthetic_report','owning_role_class':'synthetic PMO','source_location_class':'controlled','reporting_period_rule':'header','document_identifier_convention':'v','permitted_fact_classes':['reported_actual'],'prohibited_inference':['currentness'],'scope':'synthetic_project','approval_method':'synthetic'}
  # A self-declared signer cannot get beyond the independent-identity gate.
  declared='st1-070-test-declared-signer'
  q.execute("INSERT INTO ingestion.sdas_actor_registry (actor_id,organizational_role,approval_scope,identity_evidence_reference,effective_from,evidence_quality) VALUES (%s,'declared only','[]'::jsonb,'synthetic',%s,'declared_unverified')",(declared,now))
  q.execute("INSERT INTO ingestion.sdas_controlled_attestations (attestation_id,attestation_kind,attestation_version,project_scope,subject_role_class,attestation_payload,effective_from,signer_actor_id,signed_artifact_reference,signed_artifact_fingerprint,acquisition_provenance,event_hash) VALUES ('st1-070-self','governance_authority','v1','synthetic_project','synthetic role',%s::jsonb,%s,%s,'synthetic',%s,'synthetic',%s)",(json.dumps(p1),now,declared,h({'artifact':'self'}),h({'create':'self'})))
  q.execute("INSERT INTO ingestion.sdas_controlled_attestation_events (attestation_id,transition_state,reason_code,evidence_reference,evidence_fingerprint,event_hash,event_at) VALUES ('st1-070-self','SUBMITTED','synthetic','synthetic',%s,%s,%s)",(h({'s':'self'}),h({'se':'self'}),now))
  q.execute('SAVEPOINT self_assertion')
  try:
   q.execute("INSERT INTO ingestion.sdas_controlled_attestation_events (attestation_id,transition_state,verifier_actor_id,reason_code,evidence_reference,evidence_fingerprint,event_hash,event_at) VALUES ('st1-070-self','IDENTITY_VERIFIED',%s,'synthetic','synthetic',%s,%s,%s)",(verifier,h({'sid':1}),h({'side':1}),now)); out['self_assertion_rejected']=False
  except psycopg.Error: q.execute('ROLLBACK TO SAVEPOINT self_assertion'); out['self_assertion_rejected']=True
  add('st1-070-a1','governance_authority',p1); add('st1-070-a2','project_controls_accountability',p2); add('st1-070-a3','controlled_report_definition',p3)
  q.execute('SAVEPOINT premature')
  try:
   q.execute("INSERT INTO ingestion.sdas_controlled_attestation_events (attestation_id,transition_state,verifier_actor_id,reason_code,evidence_reference,evidence_fingerprint,event_hash,event_at) VALUES ('st1-070-a1','VERIFIED',%s,'synthetic','synthetic',%s,%s,%s)",(verifier,h({'bad':1}),h({'badE':1}),now)); out['premature_verification_rejected']=False
  except psycopg.Error: q.execute('ROLLBACK TO SAVEPOINT premature'); out['premature_verification_rejected']=True
  for i in ('st1-070-a1','st1-070-a2','st1-070-a3'):
   q.execute("INSERT INTO ingestion.sdas_controlled_attestation_events (attestation_id,transition_state,verifier_actor_id,reason_code,evidence_reference,evidence_fingerprint,event_hash,event_at) VALUES (%s,'IDENTITY_VERIFIED',%s,'synthetic','synthetic',%s,%s,%s)",(i,verifier,h({'id':i}),h({'ie':i}),now))
   q.execute("INSERT INTO ingestion.sdas_controlled_attestation_events (attestation_id,transition_state,verifier_actor_id,reason_code,evidence_reference,evidence_fingerprint,event_hash,event_at) VALUES (%s,'VERIFIED',%s,'synthetic','synthetic',%s,%s,%s)",(i,verifier,h({'v':i}),h({'ve':i}),now))
  out['three_attestations_verified']=q.execute("SELECT count(*) FROM ingestion.sdas_verified_controlled_attestations WHERE attestation_id LIKE 'st1-070-%'").fetchone()[0]==3
  q.execute("INSERT INTO ingestion.sdas_controlled_attestation_events (attestation_id,transition_state,verifier_actor_id,reason_code,evidence_reference,evidence_fingerprint,event_hash,event_at) VALUES ('st1-070-a2','REVOKED',%s,'synthetic','synthetic',%s,%s,%s)",(verifier,h({'r':2}),h({'re':2}),now))
  out['revocation_removes_verified']=q.execute("SELECT count(*) FROM ingestion.sdas_verified_controlled_attestations WHERE attestation_id='st1-070-a2'").fetchone()[0]==0
  q.execute("INSERT INTO ingestion.sdas_controlled_attestation_events (attestation_id,transition_state,verifier_actor_id,successor_attestation_id,reason_code,evidence_reference,evidence_fingerprint,event_hash,event_at) VALUES ('st1-070-a1','SUPERSEDED',%s,'st1-070-a3','synthetic','synthetic',%s,%s,%s)",(verifier,h({'sp':1}),h({'spe':1}),now))
  out['supersession_removes_verified']=q.execute("SELECT count(*) FROM ingestion.sdas_verified_controlled_attestations WHERE attestation_id='st1-070-a1'").fetchone()[0]==0
  q.execute('SAVEPOINT mutate')
  try:
   q.execute("UPDATE ingestion.sdas_controlled_attestations SET project_scope='x' WHERE attestation_id='st1-070-a3'"); out['append_only_update_rejected']=False
  except psycopg.Error: q.execute('ROLLBACK TO SAVEPOINT mutate'); out['append_only_update_rejected']=True
 c.rollback()
out.update(automatic_certification=False,synthetic_test_persisted=False)
print(json.dumps(out,sort_keys=True,separators=(',',':')))
'''

def main() -> None:
    payload = base64.b64encode(REMOTE.encode()).decode()
    command = "docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('" + payload + "'))\""
    result = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "ST1-070 workflow verification failed")
    print(result.stdout.strip())

if __name__ == '__main__':
    main()
