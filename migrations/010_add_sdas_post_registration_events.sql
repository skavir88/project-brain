CREATE TABLE ingestion.sdas_post_registration_events (
  post_registration_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  knowledge_id char(64) NOT NULL REFERENCES ingestion.certified_knowledge_items(knowledge_id),
  event_type text NOT NULL CHECK (event_type IN ('supersession','revocation','correction','expiration','authority_change')),
  event_at timestamptz NOT NULL DEFAULT now(),
  actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  reason_code text NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE TRIGGER sdas_post_registration_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_post_registration_events
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();

GRANT SELECT, INSERT ON ingestion.sdas_post_registration_events TO enterprise_ai_ingestion_runtime;
GRANT USAGE, SELECT ON SEQUENCE ingestion.sdas_post_registration_events_post_registration_event_id_seq TO enterprise_ai_ingestion_runtime;
