INSERT INTO ingestion.sdas_policy_versions (
  policy_id, policy_version, effective_from, enabled, allowed_source_types,
  allowed_data_classes, required_evidence, risk_class, decision_reason_codes,
  actor_authority_requirements, policy_hash
) VALUES (
  'sdas-low-risk-native', 'simulation-v1', now(), true,
  '["historical_certified"]'::jsonb, '["historical_certified"]'::jsonb,
  '["missing_native_evidence"]'::jsonb, 'medium', '["human_review_required"]'::jsonb,
  '["human_reviewer"]'::jsonb,
  'a8c0e0c24e7a50176d7b24f1c0bc70c537978691258414da366e81c9f12a7c54'
) ON CONFLICT (policy_id, policy_version) DO NOTHING;

ALTER TABLE ingestion.sdas_policy_decisions
  ADD CONSTRAINT sdas_policy_decision_policy_version_fk
  FOREIGN KEY (policy_id, policy_version)
  REFERENCES ingestion.sdas_policy_versions(policy_id, policy_version);

CREATE FUNCTION ingestion.enforce_sdas_policy_enabled() RETURNS trigger LANGUAGE plpgsql AS $$
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
  RETURN NEW;
END;
$$;

CREATE TRIGGER sdas_policy_decision_policy_state
BEFORE INSERT ON ingestion.sdas_policy_decisions
FOR EACH ROW EXECUTE FUNCTION ingestion.enforce_sdas_policy_enabled();
