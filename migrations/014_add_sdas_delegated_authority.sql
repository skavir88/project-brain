CREATE TABLE ingestion.sdas_delegated_authority (
 delegation_id text PRIMARY KEY, delegating_actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
 delegated_role text NOT NULL, organization text NOT NULL, data_domain text NOT NULL,
 source_system_scope jsonb NOT NULL, document_data_classes jsonb NOT NULL, permitted_fact_classes jsonb NOT NULL,
 prohibited_fact_classes jsonb NOT NULL, effective_from timestamptz NOT NULL, effective_until timestamptz,
 delegation_basis_reference text NOT NULL, policy_version text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'), event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);
CREATE TABLE ingestion.sdas_delegated_authority_events (
 event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, delegation_id text NOT NULL REFERENCES ingestion.sdas_delegated_authority(delegation_id),
 event_type text NOT NULL CHECK (event_type IN ('created','revoked','superseded')), actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
 event_at timestamptz NOT NULL DEFAULT now(), reason_code text NOT NULL, evidence_reference text NOT NULL,
 evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'), event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);
CREATE TRIGGER sdas_delegation_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_delegated_authority FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_delegation_event_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_delegated_authority_events FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
GRANT SELECT,INSERT ON ingestion.sdas_delegated_authority,ingestion.sdas_delegated_authority_events TO enterprise_ai_ingestion_runtime;
GRANT USAGE,SELECT ON SEQUENCE ingestion.sdas_delegated_authority_events_event_id_seq TO enterprise_ai_ingestion_runtime;
