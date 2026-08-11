-- ST1-070: controlled organizational attestations are evidence artifacts, not delegation.
-- A verified attestation can support a future readiness check only; it never
-- activates a delegation or certifies a record by itself.

CREATE TABLE ingestion.sdas_controlled_attestations (
  attestation_id text PRIMARY KEY,
  attestation_kind text NOT NULL CHECK (attestation_kind IN (
    'governance_authority', 'project_controls_accountability', 'controlled_report_definition'
  )),
  attestation_version text NOT NULL,
  project_scope text NOT NULL,
  subject_role_class text NOT NULL,
  attestation_payload jsonb NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  signer_actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
  signed_artifact_reference text NOT NULL,
  signed_artifact_fingerprint char(64) NOT NULL CHECK (signed_artifact_fingerprint ~ '^[0-9a-f]{64}$'),
  acquisition_provenance text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$'),
  CHECK (effective_to IS NULL OR effective_to > effective_from)
);

CREATE TABLE ingestion.sdas_controlled_attestation_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  attestation_id text NOT NULL REFERENCES ingestion.sdas_controlled_attestations(attestation_id),
  transition_state text NOT NULL CHECK (transition_state IN (
    'SUBMITTED', 'IDENTITY_VERIFIED', 'VERIFIED', 'REVOKED', 'SUPERSEDED', 'REJECTED'
  )),
  verifier_actor_id text REFERENCES ingestion.sdas_actor_registry(actor_id),
  successor_attestation_id text REFERENCES ingestion.sdas_controlled_attestations(attestation_id),
  reason_code text NOT NULL,
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  event_at timestamptz NOT NULL DEFAULT now(),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE OR REPLACE FUNCTION ingestion.validate_sdas_controlled_attestation_transition()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  previous_state text;
  a ingestion.sdas_controlled_attestations%ROWTYPE;
  signer_quality text;
  required_ok boolean;
BEGIN
  SELECT * INTO a FROM ingestion.sdas_controlled_attestations WHERE attestation_id=NEW.attestation_id;
  SELECT transition_state INTO previous_state
    FROM ingestion.sdas_controlled_attestation_events
   WHERE attestation_id=NEW.attestation_id ORDER BY event_id DESC LIMIT 1;

  IF NEW.transition_state='SUBMITTED' THEN
    IF previous_state IS NOT NULL OR NEW.verifier_actor_id IS NOT NULL OR NEW.successor_attestation_id IS NOT NULL THEN
      RAISE EXCEPTION 'attestation submission must be the first non-verified event';
    END IF;
  ELSIF NEW.transition_state='IDENTITY_VERIFIED' THEN
    IF previous_state<>'SUBMITTED' OR NEW.verifier_actor_id IS NULL THEN
      RAISE EXCEPTION 'identity verification requires submitted attestation and verifier';
    END IF;
    SELECT evidence_quality INTO signer_quality FROM ingestion.sdas_actor_registry WHERE actor_id=a.signer_actor_id;
    IF signer_quality NOT IN ('native','corroborated_historical') THEN
      RAISE EXCEPTION 'signer identity is not independently evidenced';
    END IF;
  ELSIF NEW.transition_state='VERIFIED' THEN
    IF previous_state<>'IDENTITY_VERIFIED' OR NEW.verifier_actor_id IS NULL THEN
      RAISE EXCEPTION 'verification requires independently verified signer identity';
    END IF;
    required_ok := CASE a.attestation_kind
      WHEN 'governance_authority' THEN
        a.attestation_payload ?& ARRAY['governance_role_class','authority_basis','scope','expiry_or_revocation_rule','approval_method']
      WHEN 'project_controls_accountability' THEN
        a.attestation_payload ?& ARRAY['accountable_role_class','report_classes','permitted_fact_classes','prohibited_fact_classes','scope','approval_method']
      WHEN 'controlled_report_definition' THEN
        a.attestation_payload ?& ARRAY['source_report_class','owning_role_class','source_location_class','reporting_period_rule','document_identifier_convention','permitted_fact_classes','prohibited_inference','scope','approval_method']
    END;
    IF NOT required_ok THEN
      RAISE EXCEPTION 'attestation payload lacks mandatory controlled-evidence fields';
    END IF;
  ELSIF NEW.transition_state IN ('REVOKED','REJECTED') THEN
    IF previous_state NOT IN ('SUBMITTED','IDENTITY_VERIFIED','VERIFIED') OR NEW.verifier_actor_id IS NULL OR NEW.successor_attestation_id IS NOT NULL THEN
      RAISE EXCEPTION 'revocation or rejection requires a non-terminal attestation and verifier';
    END IF;
  ELSIF NEW.transition_state='SUPERSEDED' THEN
    IF previous_state<>'VERIFIED' OR NEW.verifier_actor_id IS NULL OR NEW.successor_attestation_id IS NULL OR NEW.successor_attestation_id=NEW.attestation_id THEN
      RAISE EXCEPTION 'supersession requires verified predecessor, verifier, and distinct successor';
    END IF;
  ELSE
    RAISE EXCEPTION 'controlled attestation is terminal';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER sdas_controlled_attestation_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_controlled_attestations
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_controlled_attestation_event_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_controlled_attestation_events
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_controlled_attestation_transition_guard
BEFORE INSERT ON ingestion.sdas_controlled_attestation_events
FOR EACH ROW EXECUTE FUNCTION ingestion.validate_sdas_controlled_attestation_transition();

CREATE VIEW ingestion.sdas_verified_controlled_attestations AS
SELECT a.attestation_id, a.attestation_kind, a.attestation_version,
       a.project_scope, a.subject_role_class, a.attestation_payload,
       a.effective_from, a.effective_to, a.signed_artifact_reference,
       a.signed_artifact_fingerprint
  FROM ingestion.sdas_controlled_attestations a
 WHERE (SELECT e.transition_state FROM ingestion.sdas_controlled_attestation_events e
         WHERE e.attestation_id=a.attestation_id ORDER BY e.event_id DESC LIMIT 1)='VERIFIED'
   AND a.effective_from<=now() AND (a.effective_to IS NULL OR a.effective_to>now());

GRANT SELECT, INSERT ON ingestion.sdas_controlled_attestations,
  ingestion.sdas_controlled_attestation_events TO enterprise_ai_ingestion_runtime;
GRANT USAGE, SELECT ON SEQUENCE ingestion.sdas_controlled_attestation_events_event_id_seq
  TO enterprise_ai_ingestion_runtime;
GRANT SELECT ON ingestion.sdas_verified_controlled_attestations TO enterprise_ai_ingestion_runtime;
