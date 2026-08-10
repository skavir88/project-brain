CREATE TABLE ingestion.sdas_governance_evidence_observations (
  observation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  evidence_category text NOT NULL CHECK (evidence_category IN ('governance_authority_evidence','role_identity_evidence','source_control_evidence','reporting_time_evidence')),
  status text NOT NULL CHECK (status IN ('VERIFIED','PARTIAL','MISSING')),
  evidence_type text NOT NULL,
  asserted_fact text NOT NULL,
  subject_class text NOT NULL,
  scope jsonb NOT NULL,
  effective_from timestamptz, effective_to timestamptz,
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  verification_method text NOT NULL,
  acquisition_provenance text NOT NULL,
  confidence text NOT NULL CHECK (confidence IN ('high','medium','low','not_assessed')),
  observed_at timestamptz NOT NULL DEFAULT now(),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);
CREATE TRIGGER sdas_governance_evidence_observation_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_governance_evidence_observations
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
GRANT SELECT,INSERT ON ingestion.sdas_governance_evidence_observations TO enterprise_ai_ingestion_runtime;
GRANT USAGE,SELECT ON SEQUENCE ingestion.sdas_governance_evidence_observations_observation_id_seq TO enterprise_ai_ingestion_runtime;
