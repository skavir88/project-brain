CREATE TABLE ingestion.sdas_authority_assertions (
  authority_assertion_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  subject_type text NOT NULL CHECK (subject_type IN ('source','document_class','record')),
  subject_id text NOT NULL,
  authority_basis text NOT NULL CHECK (authority_basis IN ('authoritative_by_registered_system','authoritative_by_accountable_owner','authoritative_by_approved_document_class','corroborated_authority','declared_not_verified','conflicting_authority','authority_not_verified')),
  authority_scope jsonb NOT NULL,
  accountable_actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  effective_from timestamptz, effective_to timestamptz,
  asserted_at timestamptz NOT NULL DEFAULT now(), verification_method text NOT NULL,
  policy_version text NOT NULL, assertion_state text NOT NULL CHECK (assertion_state IN ('asserted','revoked','superseded')),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);
CREATE TABLE ingestion.sdas_business_time_evidence (
  business_time_evidence_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  record_fingerprint char(64) NOT NULL REFERENCES ingestion.credibility_records(record_fingerprint),
  time_kind text NOT NULL CHECK (time_kind IN ('report_period','issue_date','effective_date','event_date','approval_date','acquisition_timestamp','filesystem_timestamp')),
  start_at timestamptz, end_at timestamptz, value_text text,
  evidence_reference text NOT NULL, evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  captured_at timestamptz NOT NULL DEFAULT now(), actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
  verification_method text NOT NULL, evidence_quality text NOT NULL CHECK (evidence_quality IN ('native','corroborated_historical','reconstructed','declared_unverified','missing')),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);
CREATE TRIGGER sdas_authority_assertion_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_authority_assertions FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_business_time_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_business_time_evidence FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
GRANT SELECT,INSERT ON ingestion.sdas_authority_assertions,ingestion.sdas_business_time_evidence TO enterprise_ai_ingestion_runtime;
GRANT USAGE,SELECT ON SEQUENCE ingestion.sdas_authority_assertions_authority_assertion_id_seq,ingestion.sdas_business_time_evidence_business_time_evidence_id_seq TO enterprise_ai_ingestion_runtime;
