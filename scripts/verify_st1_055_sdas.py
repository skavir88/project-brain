#!/usr/bin/env python3
"""Verify additive SDAS pilot invariants without exposing pilot content."""
from __future__ import annotations

import base64
import subprocess


SQL = r'''import json,os,psycopg
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'],port=os.environ.get('INGESTION_DB_PORT','5432'),dbname=os.environ['INGESTION_DB_NAME'],user=os.environ['INGESTION_DB_USER'],password=os.environ['INGESTION_DB_PASSWORD']) as c:
 with c.cursor() as q:
  q.execute("SELECT count(*) FROM ingestion.certified_knowledge_items WHERE lifecycle_state='certified'"); certified=q.fetchone()[0]
  q.execute("SELECT assurance_level,count(*) FROM ingestion.sdas_assurance_envelopes GROUP BY assurance_level ORDER BY assurance_level"); levels=q.fetchall()
  q.execute("SELECT assurance_state,count(*) FROM ingestion.sdas_assurance_envelopes GROUP BY assurance_state ORDER BY assurance_state"); states=q.fetchall()
  q.execute("SELECT count(*) FROM ingestion.sdas_assurance_events"); assessment_events=q.fetchone()[0]
  q.execute("SELECT count(*) FROM ingestion.sdas_assurance_envelopes e LEFT JOIN ingestion.sdas_assurance_events a ON a.knowledge_id=e.knowledge_id WHERE a.event_id IS NULL"); unlinked=q.fetchone()[0]
  q.execute("SELECT count(*) FROM ingestion.sdas_consumption_events"); consumption=q.fetchone()[0]
  q.execute("SELECT consumer_identifier,outcome_class,count(*) FROM ingestion.sdas_consumption_events GROUP BY consumer_identifier,outcome_class ORDER BY consumer_identifier,outcome_class"); consumption_distribution=q.fetchall()
  q.execute("SELECT key,value,count(*) FROM ingestion.sdas_assurance_envelopes CROSS JOIN LATERAL jsonb_each_text(dimensions) GROUP BY key,value ORDER BY key,value"); dimension_matrix=q.fetchall()
  q.execute("WITH ordered AS (SELECT knowledge_id,event_hash,previous_event_hash,lag(event_hash) OVER (PARTITION BY knowledge_id ORDER BY event_id) AS expected_previous FROM ingestion.sdas_consumption_events) SELECT COALESCE(bool_and(previous_event_hash IS NOT DISTINCT FROM expected_previous),true) FROM ordered"); consumption_chain_valid=q.fetchone()[0]
  q.execute("WITH ordered AS (SELECT knowledge_id,event_hash,previous_event_hash,lag(event_hash) OVER (PARTITION BY knowledge_id ORDER BY event_id) AS expected_previous FROM ingestion.sdas_assurance_events) SELECT COALESCE(bool_and(previous_event_hash IS NOT DISTINCT FROM expected_previous),true) FROM ordered"); assessment_chain_valid=q.fetchone()[0]
  q.execute("SELECT count(*) FROM information_schema.role_table_grants WHERE grantee=current_user AND table_schema='ingestion' AND table_name IN ('sdas_assurance_envelopes','sdas_assurance_events','sdas_consumption_events') AND privilege_type IN ('UPDATE','DELETE')"); mutation_grants=q.fetchone()[0]
  q.execute("SELECT count(*) FROM ingestion.sdas_assurance_envelopes WHERE assurance_level='SDAS-3'"); reliance=q.fetchone()[0]
  q.execute("SELECT authority_state,currentness_state,reliance_eligibility_state,count(*) FROM ingestion.sdas_assurance_envelopes GROUP BY authority_state,currentness_state,reliance_eligibility_state ORDER BY authority_state,currentness_state,reliance_eligibility_state"); independent_state_distribution=q.fetchall()
print(json.dumps({'certified_knowledge_count':certified,'level_distribution':levels,'state_distribution':states,'assessment_events':assessment_events,'unlinked_envelopes':unlinked,'consumption_events':consumption,'consumption_distribution':consumption_distribution,'dimension_matrix':dimension_matrix,'assessment_chain_valid':assessment_chain_valid,'consumption_chain_valid':consumption_chain_valid,'runtime_update_delete_grants':mutation_grants,'sdas3_records':reliance,'independent_state_distribution':independent_state_distribution}))'''


def main() -> int:
    encoded = base64.b64encode(SQL.encode()).decode()
    command = f"docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
    run = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rdapp", command], text=True, capture_output=True)
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "SDAS verification failed")
    print(run.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
