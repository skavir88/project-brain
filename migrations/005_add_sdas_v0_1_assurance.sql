-- Additive SDAS v0.1 pilot schema. It does not alter certification, audit,
-- Certified Knowledge, retrieval, or currentness semantics.
CREATE TABLE ingestion.sdas_assurance_envelopes (
  knowledge_id char(64) PRIMARY KEY REFERENCES ingestion.certified_knowledge_items(knowledge_id),
  source_fingerprint char(64) NOT NULL REFERENCES ingestion.credibility_records(record_fingerprint),
  assessment_policy_version text NOT NULL,
  assurance_level text NOT NULL CHECK (assurance_level IN ('SDAS-0','SDAS-1','SDAS-2','SDAS-3')),
  assurance_state text NOT NULL CHECK (assurance_state IN ('assessed_partial','evidence_complete','certified_assured','superseded','revoked')),
  dimensions jsonb NOT NULL,
  gaps jsonb NOT NULL,
  assessed_by text NOT NULL,
  assessed_at timestamptz NOT NULL DEFAULT now(),
  envelope_fingerprint char(64) NOT NULL UNIQUE CHECK (envelope_fingerprint ~ '^[0-9a-f]{64}$')
);

CREATE TABLE ingestion.sdas_assurance_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  knowledge_id char(64) NOT NULL REFERENCES ingestion.sdas_assurance_envelopes(knowledge_id),
  previous_state text,
  new_state text NOT NULL CHECK (new_state IN ('assessed_partial','evidence_complete','certified_assured','superseded','revoked')),
  actor_identifier text NOT NULL,
  policy_version text NOT NULL,
  reason_code text NOT NULL,
  event_payload jsonb NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  previous_event_hash char(64),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE TABLE ingestion.sdas_consumption_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  knowledge_id char(64) NOT NULL REFERENCES ingestion.certified_knowledge_items(knowledge_id),
  consumer_identifier text NOT NULL,
  purpose_class text NOT NULL,
  outcome_class text NOT NULL CHECK (outcome_class IN ('grounded_answer','insufficient_certified_evidence','retrieval_only')),
  retrieval_policy_version text NOT NULL,
  retrieval_threshold numeric(4,3) NOT NULL CHECK (retrieval_threshold >= 0 AND retrieval_threshold <= 1),
  provenance_set_fingerprint char(64) NOT NULL CHECK (provenance_set_fingerprint ~ '^[0-9a-f]{64}$'),
  output_fingerprint char(64) NOT NULL CHECK (output_fingerprint ~ '^[0-9a-f]{64}$'),
  idempotency_key char(64) NOT NULL CHECK (idempotency_key ~ '^[0-9a-f]{64}$'),
  recorded_at timestamptz NOT NULL DEFAULT now(),
  previous_event_hash char(64),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$'),
  UNIQUE (knowledge_id, idempotency_key)
);

CREATE INDEX sdas_assurance_envelopes_level_idx ON ingestion.sdas_assurance_envelopes (assurance_level);
CREATE INDEX sdas_consumption_events_knowledge_idx ON ingestion.sdas_consumption_events (knowledge_id, recorded_at);

CREATE FUNCTION ingestion.reject_sdas_event_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'SDAS evidence is append-only';
END;
$$;

CREATE TRIGGER sdas_assurance_envelopes_no_update_delete
BEFORE UPDATE OR DELETE ON ingestion.sdas_assurance_envelopes
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_event_mutation();
CREATE TRIGGER sdas_assurance_events_no_update_delete
BEFORE UPDATE OR DELETE ON ingestion.sdas_assurance_events
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_event_mutation();
CREATE TRIGGER sdas_consumption_events_no_update_delete
BEFORE UPDATE OR DELETE ON ingestion.sdas_consumption_events
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_event_mutation();

GRANT SELECT, INSERT ON ingestion.sdas_assurance_envelopes TO enterprise_ai_ingestion_runtime;
GRANT SELECT, INSERT ON ingestion.sdas_assurance_events TO enterprise_ai_ingestion_runtime;
GRANT SELECT, INSERT ON ingestion.sdas_consumption_events TO enterprise_ai_ingestion_runtime;
GRANT USAGE, SELECT ON SEQUENCE ingestion.sdas_assurance_events_event_id_seq TO enterprise_ai_ingestion_runtime;
GRANT USAGE, SELECT ON SEQUENCE ingestion.sdas_consumption_events_event_id_seq TO enterprise_ai_ingestion_runtime;
