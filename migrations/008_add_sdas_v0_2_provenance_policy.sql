CREATE TABLE ingestion.sdas_actor_registry (
  actor_id text PRIMARY KEY, organizational_role text NOT NULL, approval_scope jsonb NOT NULL,
  identity_evidence_reference text NOT NULL, effective_from timestamptz NOT NULL, expires_at timestamptz,
  evidence_quality text NOT NULL CHECK (evidence_quality IN ('native','corroborated_historical','reconstructed','declared_unverified','missing')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ingestion.sdas_source_registry (
  source_id text PRIMARY KEY, source_type text NOT NULL, system_location_identity text NOT NULL,
  owner_actor_id text REFERENCES ingestion.sdas_actor_registry(actor_id), business_purpose text NOT NULL,
  authority_status text NOT NULL CHECK (authority_status IN ('not_assessed','declared_unverified','verified_limited','authoritative')),
  authority_scope jsonb NOT NULL, effective_from timestamptz, effective_to timestamptz,
  evidence_quality text NOT NULL CHECK (evidence_quality IN ('native','corroborated_historical','reconstructed','declared_unverified','missing')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ingestion.sdas_acquisition_events (
  acquisition_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, source_id text NOT NULL REFERENCES ingestion.sdas_source_registry(source_id),
  acquired_at timestamptz NOT NULL, actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id), acquisition_method text NOT NULL,
  source_reference text NOT NULL, original_fingerprint char(64) NOT NULL CHECK (original_fingerprint ~ '^[0-9a-f]{64}$'),
  size_bytes bigint, media_type text, evidence_quality text NOT NULL CHECK (evidence_quality IN ('native','corroborated_historical','reconstructed','declared_unverified','missing')),
  evidence_hash char(64) NOT NULL UNIQUE CHECK (evidence_hash ~ '^[0-9a-f]{64}$'), created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ingestion.sdas_transformations (
  transformation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, acquisition_event_id bigint NOT NULL REFERENCES ingestion.sdas_acquisition_events(acquisition_event_id),
  transformation_type text NOT NULL, tool_name text NOT NULL, tool_version text NOT NULL, transformed_at timestamptz NOT NULL,
  input_fingerprint char(64) NOT NULL CHECK (input_fingerprint ~ '^[0-9a-f]{64}$'), output_fingerprint char(64) NOT NULL CHECK (output_fingerprint ~ '^[0-9a-f]{64}$'),
  deterministic boolean NOT NULL, extraction_coordinates jsonb NOT NULL, evidence_quality text NOT NULL CHECK (evidence_quality IN ('native','corroborated_historical','reconstructed','declared_unverified','missing')),
  evidence_hash char(64) NOT NULL UNIQUE CHECK (evidence_hash ~ '^[0-9a-f]{64}$')
);
CREATE TABLE ingestion.sdas_policy_versions (
  policy_id text NOT NULL, policy_version text NOT NULL, effective_from timestamptz NOT NULL, effective_to timestamptz,
  enabled boolean NOT NULL, allowed_source_types jsonb NOT NULL, allowed_data_classes jsonb NOT NULL, required_evidence jsonb NOT NULL,
  risk_class text NOT NULL, decision_reason_codes jsonb NOT NULL, actor_authority_requirements jsonb NOT NULL,
  policy_hash char(64) NOT NULL UNIQUE CHECK (policy_hash ~ '^[0-9a-f]{64}$'), created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(policy_id,policy_version)
);
CREATE TABLE ingestion.sdas_policy_decisions (
  decision_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, record_fingerprint char(64) REFERENCES ingestion.credibility_records(record_fingerprint),
  policy_id text NOT NULL, policy_version text NOT NULL, approval_mode text NOT NULL CHECK (approval_mode IN ('policy_automatic','human_required','reject_or_quarantine')),
  decision_actor text NOT NULL CHECK (decision_actor='sahra_policy_engine'), decision_timestamp timestamptz NOT NULL DEFAULT now(),
  decision_reasons jsonb NOT NULL, evidence_quality text NOT NULL CHECK (evidence_quality IN ('native','corroborated_historical','reconstructed','declared_unverified','missing')),
  decision_hash char(64) NOT NULL UNIQUE CHECK (decision_hash ~ '^[0-9a-f]{64}$'),
  UNIQUE(record_fingerprint,policy_id,policy_version)
);
CREATE FUNCTION ingestion.reject_sdas_v02_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'SDAS v0.2 evidence is append-only'; END; $$;
CREATE TRIGGER sdas_actor_registry_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_actor_registry FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_source_registry_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_source_registry FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_acquisition_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_acquisition_events FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_transformation_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_transformations FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_policy_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_policy_versions FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_policy_decision_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_policy_decisions FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
GRANT SELECT,INSERT ON ingestion.sdas_actor_registry,ingestion.sdas_source_registry,ingestion.sdas_acquisition_events,ingestion.sdas_transformations,ingestion.sdas_policy_versions,ingestion.sdas_policy_decisions TO enterprise_ai_ingestion_runtime;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA ingestion TO enterprise_ai_ingestion_runtime;
