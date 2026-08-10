CREATE TABLE ingestion.sdas_registration_events (
  registration_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  knowledge_id char(64) NOT NULL REFERENCES ingestion.certified_knowledge_items(knowledge_id),
  record_fingerprint char(64) NOT NULL REFERENCES ingestion.credibility_records(record_fingerprint),
  certification_event_id bigint NOT NULL REFERENCES ingestion.certification_audit_events(event_id),
  policy_version text NOT NULL, registered_at timestamptz NOT NULL DEFAULT now(),
  registration_hash char(64) NOT NULL UNIQUE CHECK (registration_hash ~ '^[0-9a-f]{64}$'),
  UNIQUE(knowledge_id)
);
CREATE TRIGGER sdas_registration_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_registration_events FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
GRANT SELECT,INSERT ON ingestion.sdas_registration_events TO enterprise_ai_ingestion_runtime;
GRANT USAGE,SELECT ON SEQUENCE ingestion.sdas_registration_events_registration_event_id_seq TO enterprise_ai_ingestion_runtime;
