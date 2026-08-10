CREATE TABLE ingestion.sdas_assurance_decisions (
 decision_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, record_fingerprint char(64) NOT NULL REFERENCES ingestion.credibility_records(record_fingerprint),
 authority_inheritance_state text NOT NULL CHECK (authority_inheritance_state IN ('eligible','not_eligible','conflict','missing')),
 business_time_state text NOT NULL CHECK (business_time_state IN ('valid','missing','conflict','not_applicable')),
 risk_tier text NOT NULL CHECK (risk_tier IN ('low','medium','high')),
 currentness_state text NOT NULL CHECK (currentness_state IN ('not_assessed','historical','current_eligible','stale','conflict')),
 reliance_state text NOT NULL CHECK (reliance_state='not_eligible'), outcome text NOT NULL CHECK (outcome IN ('policy_automatic','human_required','reject_or_quarantine')),
 reason_codes jsonb NOT NULL, policy_version text NOT NULL, decided_at timestamptz NOT NULL DEFAULT now(), actor_id text NOT NULL, evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'), event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);
CREATE TRIGGER sdas_assurance_decision_no_mutation BEFORE UPDATE OR DELETE ON ingestion.sdas_assurance_decisions FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
GRANT SELECT,INSERT ON ingestion.sdas_assurance_decisions TO enterprise_ai_ingestion_runtime;
GRANT USAGE,SELECT ON SEQUENCE ingestion.sdas_assurance_decisions_decision_id_seq TO enterprise_ai_ingestion_runtime;
