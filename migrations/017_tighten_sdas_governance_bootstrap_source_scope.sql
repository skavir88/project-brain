-- ST1-067 safety tightening: a verified source must evidence the exact project
-- scope of its pending proposal before it can advance the lifecycle.

CREATE OR REPLACE FUNCTION ingestion.validate_sdas_bootstrap_transition()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  previous_state text;
  terminal_seen boolean;
  source_status text;
  source_scope jsonb;
  required_project_scope text;
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
    SELECT authority_status, authority_scope INTO source_status, source_scope
      FROM ingestion.sdas_source_registry WHERE source_id = NEW.source_id;
    SELECT project_scope INTO required_project_scope
      FROM ingestion.sdas_delegation_bootstrap_proposals WHERE proposal_id = NEW.proposal_id;
    IF source_status NOT IN ('verified_limited', 'authoritative')
       OR source_scope IS NULL
       OR source_scope ->> 'project_scope' <> required_project_scope THEN
      RAISE EXCEPTION 'source verification requires verified authority for the exact project scope';
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
