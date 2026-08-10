#!/usr/bin/env python3
"""Back-assess every existing Certified Knowledge item through the additive SDAS API.

The remote worker reads only knowledge identifiers and emits aggregate results.
It never exports Certified Knowledge text, source locators, or DB credentials.
"""
from __future__ import annotations

import base64
import subprocess


REMOTE = r'''import json, os, psycopg
from urllib.request import Request, urlopen
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'],port=os.environ.get('INGESTION_DB_PORT','5432'),dbname=os.environ['INGESTION_DB_NAME'],user=os.environ['INGESTION_DB_USER'],password=os.environ['INGESTION_DB_PASSWORD']) as c:
 with c.cursor() as q:
  q.execute("SELECT knowledge_id FROM ingestion.certified_knowledge_items WHERE lifecycle_state='certified' ORDER BY knowledge_id")
  ids=[row[0] for row in q.fetchall()]
result=[]
for knowledge_id in ids:
 request=Request('http://127.0.0.1:8080/v1/sdas/assess',data=json.dumps({'knowledge_id':knowledge_id,'actor_id':'enterprise_ai_sdas_pilot_assessor','assessment_policy_version':'sdas-v0.1-pilot-assessment-v1'}).encode(),method='POST',headers={'Content-Type':'application/json'})
 with urlopen(request,timeout=20) as response:
  payload=json.load(response)
  if response.status != 201: raise RuntimeError('unexpected assessment status')
  result.append(payload)
levels={}
for row in result: levels[row['assurance_level']]=levels.get(row['assurance_level'],0)+1
print(json.dumps({'certified_knowledge_input_count':len(ids),'assessments_created':len(result),'level_distribution':levels,'states':sorted(set(row['assurance_state'] for row in result))}))'''


def main() -> int:
    encoded = base64.b64encode(REMOTE.encode()).decode()
    command = f"docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], text=True, capture_output=True)
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "SDAS back-assessment failed")
    print(run.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
