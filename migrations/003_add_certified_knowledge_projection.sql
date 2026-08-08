CREATE TABLE ingestion.certified_knowledge_items (
  knowledge_id char(64) PRIMARY KEY,
  source_fingerprint char(64) UNIQUE NOT NULL REFERENCES ingestion.credibility_records(record_fingerprint),
  source_record_id text NOT NULL,
  certification_event_id bigint NOT NULL REFERENCES ingestion.certification_audit_events(event_id),
  knowledge_text text NOT NULL,
  provenance jsonb,
  certifying_actor text NOT NULL,
  certification_timestamp timestamptz NOT NULL,
  certification_policy_version text NOT NULL,
  lifecycle_state text NOT NULL CHECK (lifecycle_state = 'certified'),
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT ON ingestion.certified_knowledge_items TO enterprise_ai_ingestion_runtime;
