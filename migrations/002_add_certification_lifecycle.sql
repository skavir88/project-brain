ALTER TABLE ingestion.credibility_records ADD COLUMN certification_timestamp timestamptz;
ALTER TABLE ingestion.credibility_records ADD COLUMN certification_actor text;
ALTER TABLE ingestion.credibility_records ADD COLUMN certification_policy_version text;
CREATE TABLE ingestion.certification_audit_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  record_fingerprint char(64) NOT NULL REFERENCES ingestion.credibility_records(record_fingerprint),
  previous_lifecycle_state text NOT NULL,
  new_lifecycle_state text NOT NULL CHECK (new_lifecycle_state = 'certified'),
  certification_timestamp timestamptz NOT NULL,
  actor_identifier text NOT NULL,
  policy_version text NOT NULL,
  UNIQUE (record_fingerprint, new_lifecycle_state)
);
GRANT INSERT, UPDATE, SELECT ON ingestion.credibility_records TO enterprise_ai_ingestion_runtime;
GRANT INSERT, SELECT ON ingestion.certification_audit_events TO enterprise_ai_ingestion_runtime;
GRANT USAGE, SELECT ON SEQUENCE ingestion.certification_audit_events_event_id_seq TO enterprise_ai_ingestion_runtime;
