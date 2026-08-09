#!/usr/bin/env python3
"""Project certified ST1-026 observations without reading raw claims locally."""
from __future__ import annotations

import base64
import subprocess


SQL_RUNNER = '''import os,json,psycopg
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'],port=os.environ.get('INGESTION_DB_PORT','5432'),dbname=os.environ['INGESTION_DB_NAME'],user=os.environ['INGESTION_DB_USER'],password=os.environ['INGESTION_DB_PASSWORD']) as c:
 with c.cursor() as q:
  q.execute("""INSERT INTO ingestion.certified_knowledge_items (knowledge_id,source_fingerprint,source_record_id,certification_event_id,knowledge_text,provenance,certifying_actor,certification_timestamp,certification_policy_version,lifecycle_state) SELECT r.record_fingerprint,r.record_fingerprint,r.record_id,a.event_id,r.canonical_record->'payload'->>'statement',r.provenance,r.certification_actor,r.certification_timestamp,r.certification_policy_version,'certified' FROM ingestion.credibility_records r JOIN LATERAL (SELECT event_id FROM ingestion.certification_audit_events e WHERE e.record_fingerprint=r.record_fingerprint ORDER BY event_id DESC LIMIT 1) a ON true WHERE r.source_id='enterprise_ai_real_currentness_observation' AND r.lifecycle_state='certified' ON CONFLICT (source_fingerprint) DO NOTHING RETURNING knowledge_id""")
  inserted=len(q.fetchall())
  q.execute("SELECT count(*) FROM ingestion.certified_knowledge_items WHERE source_record_id LIKE 'st1-026-%'")
  total=q.fetchone()[0]
print(json.dumps({'inserted':inserted,'source_attributed_knowledge_count':total}))'''


def main() -> int:
    encoded = base64.b64encode(SQL_RUNNER.encode()).decode()
    command = f"docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], text=True, capture_output=True, check=False)
    if run.returncode:
        raise RuntimeError(run.stderr.strip() or "projection failed")
    print(run.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
