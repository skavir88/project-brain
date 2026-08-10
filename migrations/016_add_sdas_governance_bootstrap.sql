-- ST1-067: policy governance is distinct from organizational authority.
-- All tables and events are append-only.  Only the view's ACTIVE proposals
-- may be considered by a future authority-inheritance evaluator.

CREATE TABLE ingestion.sdas_governance_policy_approvals (
  approval_id text PRIMARY KEY,
  policy_id text NOT NULL,
  policy_version text NOT NULL,
  governance_policy_status text NOT NULL CHECK (
    governance_policy_status IN ('approved_for_pilot')
  ),
  approver_identity_state text NOT NULL CHECK (
    approver_identity_state IN ('unverified', 'verified')
  ),
  approval_basis_reference text NOT NULL,
  policy_scope jsonb NOT NULL,
  approved_at timestamptz NOT NULL DEFAULT now(),
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE TABLE ingestion.sdas_governance_policy_approval_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  approval_id text NOT NULL REFERENCES ingestion.sdas_governance_policy_approvals(approval_id),
  event_type text NOT NULL CHECK (event_type IN ('approved_for_pilot', 'revoked', 'superseded')),
  event_at timestamptz NOT NULL DEFAULT now(),
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE TABLE ingestion.sdas_delegation_bootstrap_proposals (
  proposal_id text PRIMARY KEY,
  approval_id text NOT NULL REFERENCES ingestion.sdas_governance_policy_approvals(approval_id),
  intended_role_class text NOT NULL,
  project_scope text NOT NULL,
  source_system_identity_state text NOT NULL CHECK (source_system_identity_state IN ('required', 'verified')),
  document_data_classes jsonb NOT NULL,
  permitted_fact_classes jsonb NOT NULL,
  prohibited_fact_classes jsonb NOT NULL,
  business_time_rule jsonb NOT NULL,
  policy_version text NOT NULL,
  initial_state text NOT NULL CHECK (initial_state = 'PROPOSED'),
  created_at timestamptz NOT NULL DEFAULT now(),
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE TABLE ingestion.sdas_delegation_bootstrap_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proposal_id text NOT NULL REFERENCES ingestion.sdas_delegation_bootstrap_proposals(proposal_id),
  transition_state text NOT NULL CHECK (transition_state IN (
    'GOVERNANCE_APPROVED', 'IDENTITY_VERIFIED', 'SOURCE_VERIFIED', 'ACTIVE',
    'REVOKED', 'SUPERSEDED', 'EXPIRED', 'REJECTED'
  )),
  governance_actor_id text REFERENCES ingestion.sdas_actor_registry(actor_id),
  accountable_actor_id text REFERENCES ingestion.sdas_actor_registry(actor_id),
  source_id text REFERENCES ingestion.sdas_source_registry(source_id),
  event_at timestamptz NOT NULL DEFAULT now(),
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE OR REPLACE FUNCTION ingestion.validate_sdas_bootstrap_transition()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  previous_state text;
  terminal_seen boolean;
  source_status text;
  governance_quality text;
  accountable_quality text;
BEGIN
  SELECT transition_state INTO previous_state
    FROM ingestion.sdas_delegation_bootstrap_events
   WHERE proposal_id = NEW.proposal_id
   ORDER BY event_id DESC LIMIT 1;
  SELECT EXISTS(
    SELECT 1 FROM ingestion.sdas_delegation_bootstrap_events
     WHERE proposal_id = NEW.proposal_id
       AND transition_state IN ('REVOKED', 'SUPERSEDED', 'EXPIRED', 'REJECTED')
  ) INTO terminal_seen;

  IF terminal_seen THEN
    RAISE EXCEPTION 'SDAS bootstrap proposal is terminal';
  END IF;

  IF NEW.transition_state = 'GOVERNANCE_APPROVED' THEN
    IF previous_state IS NOT NULL OR NOT EXISTS (
      SELECT 1 FROM ingestion.sdas_delegation_bootstrap_proposals p
      JOIN ingestion.sdas_governance_policy_approvals a ON a.approval_id = p.approval_id
      WHERE p.proposal_id = NEW.proposal_id
        AND a.governance_policy_status = 'approved_for_pilot'
    ) THEN
      RAISE EXCEPTION 'governance approval requires a proposed pilot policy';
    END IF;
    IF NEW.governance_actor_id IS NOT NULL OR NEW.accountable_actor_id IS NOT NULL OR NEW.source_id IS NOT NULL THEN
      RAISE EXCEPTION 'governance policy approval must not assert operational identity or source authority';
    END IF;
  ELSIF NEW.transition_state = 'IDENTITY_VERIFIED' THEN
    IF previous_state <> 'GOVERNANCE_APPROVED' OR NEW.governance_actor_id IS NULL OR NEW.accountable_actor_id IS NULL THEN
      RAISE EXCEPTION 'identity verification requires governance approval and both role identities';
    END IF;
    SELECT evidence_quality INTO governance_quality FROM ingestion.sdas_actor_registry WHERE actor_id = NEW.governance_actor_id;
    SELECT evidence_quality INTO accountable_quality FROM ingestion.sdas_actor_registry WHERE actor_id = NEW.accountable_actor_id;
    IF governance_quality NOT IN ('native', 'corroborated_historical') OR accountable_quality NOT IN ('native', 'corroborated_historical') THEN
      RAISE EXCEPTION 'identity verification requires independently evidenced actors';
    END IF;
  ELSIF NEW.transition_state = 'SOURCE_VERIFIED' THEN
    IF previous_state <> 'IDENTITY_VERIFIED' OR NEW.source_id IS NULL THEN
      RAISE EXCEPTION 'source verification requires verified identities and a source';
    END IF;
    SELECT authority_status INTO source_status FROM ingestion.sdas_source_registry WHERE source_id = NEW.source_id;
    IF source_status NOT IN ('verified_limited', 'authoritative') THEN
      RAISE EXCEPTION 'source verification requires a verified source authority status';
    END IF;
  ELSIF NEW.transition_state = 'ACTIVE' THEN
    IF previous_state <> 'SOURCE_VERIFIED' THEN
      RAISE EXCEPTION 'activation requires source verification';
    END IF;
  ELSIF NEW.transition_state IN ('REVOKED', 'SUPERSEDED', 'EXPIRED', 'REJECTED') THEN
    IF previous_state IS NULL THEN
      RAISE EXCEPTION 'terminal state requires an existing bootstrap state';
    END IF;
  ELSE
    RAISE EXCEPTION 'unsupported bootstrap transition';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER sdas_governance_policy_approval_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_governance_policy_approvals
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_governance_policy_approval_event_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_governance_policy_approval_events
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_delegation_bootstrap_proposal_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_delegation_bootstrap_proposals
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_delegation_bootstrap_event_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_delegation_bootstrap_events
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_delegation_bootstrap_transition_guard
BEFORE INSERT ON ingestion.sdas_delegation_bootstrap_events
FOR EACH ROW EXECUTE FUNCTION ingestion.validate_sdas_bootstrap_transition();

CREATE VIEW ingestion.sdas_active_delegation_bootstrap AS
SELECT p.proposal_id, p.approval_id, p.intended_role_class, p.project_scope,
       p.document_data_classes, p.permitted_fact_classes, p.prohibited_fact_classes,
       p.business_time_rule, p.policy_version
 FROM ingestion.sdas_delegation_bootstrap_proposals p
 WHERE (SELECT e.transition_state FROM ingestion.sdas_delegation_bootstrap_events e
         WHERE e.proposal_id = p.proposal_id ORDER BY e.event_id DESC LIMIT 1) = 'ACTIVE'
   AND NOT EXISTS (
     SELECT 1 FROM ingestion.sdas_governance_policy_approval_events a
      WHERE a.approval_id = p.approval_id
        AND a.event_type IN ('revoked', 'superseded')
   );

GRANT SELECT, INSERT ON ingestion.sdas_governance_policy_approvals,
  ingestion.sdas_governance_policy_approval_events,
  ingestion.sdas_delegation_bootstrap_proposals,
  ingestion.sdas_delegation_bootstrap_events TO enterprise_ai_ingestion_runtime;
GRANT SELECT ON ingestion.sdas_active_delegation_bootstrap TO enterprise_ai_ingestion_runtime;
GRANT USAGE, SELECT ON SEQUENCE ingestion.sdas_governance_policy_approval_events_event_id_seq,
  ingestion.sdas_delegation_bootstrap_events_event_id_seq TO enterprise_ai_ingestion_runtime;
