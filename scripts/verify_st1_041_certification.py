#!/usr/bin/env python3
"""Verify aggregate ST1-041 certification, projection, and privilege invariants."""
from __future__ import annotations
import base64
import subprocess

SQL = '''import os,json,psycopg
with psycopg.connect(host=os.environ['INGESTION_DB_HOST'],port=os.environ.get('INGESTION_DB_PORT','5432'),dbname=os.environ['INGESTION_DB_NAME'],user=os.environ['INGESTION_DB_USER'],password=os.environ['INGESTION_DB_PASSWORD']) as c:
 with c.cursor() as q:
  q.execute("SELECT lifecycle_state,count(*) FROM ingestion.credibility_records WHERE record_id LIKE 'st1-041-%' GROUP BY lifecycle_state ORDER BY lifecycle_state"); states=q.fetchall()
  q.execute("SELECT count(*) FROM ingestion.certification_audit_events a JOIN ingestion.credibility_records r ON r.record_fingerprint=a.record_fingerprint WHERE r.record_id LIKE 'st1-041-%' AND a.policy_version='st1-041-source-attributed-v1'"); audits=q.fetchone()[0]
  q.execute("SELECT count(*) FROM ingestion.certified_knowledge_items WHERE source_record_id LIKE 'st1-041-%' AND certification_policy_version='st1-041-source-attributed-v1'"); knowledge=q.fetchone()[0]
  q.execute("SELECT rolsuper FROM pg_roles WHERE rolname=current_user"); superuser=q.fetchone()[0]
  q.execute("SELECT count(*) FROM information_schema.role_table_grants WHERE grantee=current_user AND privilege_type='DELETE' AND table_schema='ingestion' AND table_name IN ('credibility_records','certification_audit_events')"); deletes=q.fetchone()[0]
print(json.dumps({'lifecycle_states':states,'audit_events':audits,'certified_knowledge_items':knowledge,'runtime_role_superuser':superuser,'runtime_delete_grants':deletes}))'''
encoded=base64.b64encode(SQL.encode()).decode()
command=f"docker exec -i deploy-ingestion-service-1 python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
run=subprocess.run(["ssh","-o","BatchMode=yes","enterprise-ai-rdapp",command],text=True,capture_output=True)
if run.returncode: raise SystemExit(run.stderr.strip() or "verification failed")
print(run.stdout.strip())
