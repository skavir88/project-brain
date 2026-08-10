#!/usr/bin/env python3
"""Exercise SDAS malformed, duplicate, immutable, and invalid-transition guards."""
from __future__ import annotations

import base64
import subprocess


REMOTE = r'''import json, os, psycopg
from urllib.request import Request,urlopen
from urllib.error import HTTPError
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'],port=os.environ.get('INGESTION_DB_PORT','5432'),dbname=os.environ['INGESTION_DB_NAME'],user=os.environ['INGESTION_DB_USER'],password=os.environ['INGESTION_DB_PASSWORD']) as c:
 with c.cursor() as q:
  q.execute("SELECT knowledge_id FROM ingestion.sdas_assurance_envelopes ORDER BY knowledge_id LIMIT 1")
  knowledge_id=q.fetchone()[0]
def post(path,payload):
 request=Request('http://127.0.0.1:8080'+path,data=json.dumps(payload).encode(),method='POST',headers={'Content-Type':'application/json'})
 try:
  with urlopen(request,timeout=20) as r: return r.status,json.load(r)
 except HTTPError as e: return e.code,json.load(e)
invalid_status,_=post('/v1/sdas/consumption',{'knowledge_ids':['not-a-fingerprint']})
payload={'knowledge_ids':[knowledge_id],'consumer_id':'sdas-pilot-verifier','purpose_class':'assurance_verification','outcome_class':'retrieval_only','retrieval_policy_version':'sdas-v0.1-test-v1','retrieval_threshold':0.7,'provenance_set_fingerprint':'a'*64,'output_fingerprint':'b'*64,'idempotency_key':'c'*64}
first_status,first=post('/v1/sdas/consumption',payload)
duplicate_status,duplicate=post('/v1/sdas/consumption',payload)
mutation_denied=False
invalid_transition_denied=False
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'],port=os.environ.get('INGESTION_DB_PORT','5432'),dbname=os.environ['INGESTION_DB_NAME'],user=os.environ['INGESTION_DB_USER'],password=os.environ['INGESTION_DB_PASSWORD']) as c:
 try:
  with c.cursor() as q: q.execute("UPDATE ingestion.sdas_assurance_envelopes SET assurance_level='SDAS-3' WHERE knowledge_id=%s",(knowledge_id,))
 except Exception:
  mutation_denied=True; c.rollback()
 try:
  with c.cursor() as q: q.execute("INSERT INTO ingestion.sdas_assurance_events(knowledge_id,previous_state,new_state,actor_identifier,policy_version,reason_code,event_payload,event_hash) VALUES (%s,'assessed_partial','certified_assured','sdas-pilot-verifier','sdas-v0.1-test-v1','invalid_transition','{}',repeat('d',64))",(knowledge_id,))
 except Exception:
  invalid_transition_denied=True; c.rollback()
# Repeated verifier runs are idempotent: the first call may already be the
# existing same-key consumption event, but a duplicate must always conflict.
if not (invalid_status==400 and first_status in (201,409) and duplicate_status==409 and duplicate.get('disposition')=='duplicate_consumption' and mutation_denied and invalid_transition_denied): raise RuntimeError('SDAS negative invariant failed')
print(json.dumps({'malformed_request_status':invalid_status,'first_consumption_status':first_status,'duplicate_consumption_status':duplicate_status,'direct_mutation_denied':mutation_denied,'invalid_transition_denied':invalid_transition_denied}))'''


def main() -> int:
    encoded = base64.b64encode(REMOTE.encode()).decode()
    command = f"docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], text=True, capture_output=True)
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "SDAS negative verification failed")
    print(run.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
