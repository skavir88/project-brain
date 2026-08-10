CREATE TABLE ingestion.sdas_policy_status_events (
  policy_status_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  policy_id text NOT NULL,
  policy_version text NOT NULL,
  status text NOT NULL CHECK (status IN ('enabled','disabled')),
  effective_at timestamptz NOT NULL DEFAULT now(),
  actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
  reason_code text NOT NULL,
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$'),
  FOREIGN KEY (policy_id,policy_version)
    REFERENCES ingestion.sdas_policy_versions(policy_id,policy_version)
);

CREATE TRIGGER sdas_policy_status_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_policy_status_events
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();

CREATE OR REPLACE FUNCTION ingestion.enforce_sdas_policy_enabled() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE status_at_decision text;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM ingestion.sdas_policy_versions p
    WHERE p.policy_id = NEW.policy_id
      AND p.policy_version = NEW.policy_version
      AND p.enabled
      AND p.effective_from <= NEW.decision_timestamp
      AND (p.effective_to IS NULL OR p.effective_to >= NEW.decision_timestamp)
  ) THEN
    RAISE EXCEPTION 'SDAS policy version is disabled, expired, or unavailable';
  END IF;
  SELECT s.status INTO status_at_decision
  FROM ingestion.sdas_policy_status_events s
  WHERE s.policy_id=NEW.policy_id AND s.policy_version=NEW.policy_version
    AND s.effective_at <= NEW.decision_timestamp
  ORDER BY s.effective_at DESC, s.policy_status_event_id DESC LIMIT 1;
  IF status_at_decision='disabled' THEN
    RAISE EXCEPTION 'SDAS policy version is disabled by append-only status event';
  END IF;
  RETURN NEW;
END;
$$;

GRANT SELECT, INSERT ON ingestion.sdas_policy_status_events TO enterprise_ai_ingestion_runtime;
GRANT USAGE, SELECT ON SEQUENCE ingestion.sdas_policy_status_events_policy_status_event_id_seq TO enterprise_ai_ingestion_runtime;
