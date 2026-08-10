ALTER TABLE ingestion.sdas_delegation_bootstrap_proposals
  ADD COLUMN governance_role_class text NOT NULL DEFAULT 'CEO / Executive Governance Authority';

CREATE TABLE ingestion.sdas_role_identity_verifications (
  verification_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
  role_class text NOT NULL,
  project_scope text NOT NULL,
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  verification_method text NOT NULL,
  evidence_quality text NOT NULL CHECK (evidence_quality IN ('native','corroborated_historical')),
  effective_from timestamptz NOT NULL, effective_to timestamptz,
  asserted_at timestamptz NOT NULL DEFAULT now(),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE TABLE ingestion.sdas_source_control_verifications (
  verification_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  source_id text NOT NULL REFERENCES ingestion.sdas_source_registry(source_id),
  accountable_actor_id text NOT NULL REFERENCES ingestion.sdas_actor_registry(actor_id),
  project_scope text NOT NULL,
  document_data_class text NOT NULL,
  business_time_rule text NOT NULL CHECK (business_time_rule IN ('approved_report_header','registered_source_system_period_field','document_control_evidence','accountable_owner_attestation')),
  evidence_reference text NOT NULL,
  evidence_fingerprint char(64) NOT NULL CHECK (evidence_fingerprint ~ '^[0-9a-f]{64}$'),
  evidence_quality text NOT NULL CHECK (evidence_quality IN ('native','corroborated_historical')),
  effective_from timestamptz NOT NULL, effective_to timestamptz,
  asserted_at timestamptz NOT NULL DEFAULT now(),
  event_hash char(64) NOT NULL UNIQUE CHECK (event_hash ~ '^[0-9a-f]{64}$')
);

CREATE TRIGGER sdas_role_identity_verification_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_role_identity_verifications
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();
CREATE TRIGGER sdas_source_control_verification_no_mutation
BEFORE UPDATE OR DELETE ON ingestion.sdas_source_control_verifications
FOR EACH ROW EXECUTE FUNCTION ingestion.reject_sdas_v02_mutation();

CREATE OR REPLACE FUNCTION ingestion.validate_sdas_bootstrap_transition()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  previous_state text; terminal_seen boolean; source_status text; source_scope jsonb;
  project text; governance_role text; accountable_role text; prior_governance text; prior_accountable text;
BEGIN
  SELECT transition_state INTO previous_state FROM ingestion.sdas_delegation_bootstrap_events WHERE proposal_id=NEW.proposal_id ORDER BY event_id DESC LIMIT 1;
  SELECT EXISTS(SELECT 1 FROM ingestion.sdas_delegation_bootstrap_events WHERE proposal_id=NEW.proposal_id AND transition_state IN ('REVOKED','SUPERSEDED','EXPIRED','REJECTED')) INTO terminal_seen;
  SELECT project_scope,governance_role_class,intended_role_class INTO project,governance_role,accountable_role FROM ingestion.sdas_delegation_bootstrap_proposals WHERE proposal_id=NEW.proposal_id;
  IF terminal_seen THEN RAISE EXCEPTION 'SDAS bootstrap proposal is terminal'; END IF;
  IF NEW.transition_state='GOVERNANCE_APPROVED' THEN
    IF previous_state IS NOT NULL OR NOT EXISTS (SELECT 1 FROM ingestion.sdas_delegation_bootstrap_proposals p JOIN ingestion.sdas_governance_policy_approvals a ON a.approval_id=p.approval_id WHERE p.proposal_id=NEW.proposal_id AND a.governance_policy_status='approved_for_pilot') OR NEW.governance_actor_id IS NOT NULL OR NEW.accountable_actor_id IS NOT NULL OR NEW.source_id IS NOT NULL THEN RAISE EXCEPTION 'governance policy approval requires a proposed policy without operational authority'; END IF;
  ELSIF NEW.transition_state='IDENTITY_VERIFIED' THEN
    IF previous_state<>'GOVERNANCE_APPROVED' OR NEW.governance_actor_id IS NULL OR NEW.accountable_actor_id IS NULL THEN RAISE EXCEPTION 'identity verification requires governance approval and both role identities'; END IF;
    IF NOT EXISTS (SELECT 1 FROM ingestion.sdas_role_identity_verifications v WHERE v.actor_id=NEW.governance_actor_id AND v.role_class=governance_role AND v.project_scope=project AND v.effective_from<=now() AND (v.effective_to IS NULL OR v.effective_to>now()))
       OR NOT EXISTS (SELECT 1 FROM ingestion.sdas_role_identity_verifications v WHERE v.actor_id=NEW.accountable_actor_id AND v.role_class=accountable_role AND v.project_scope=project AND v.effective_from<=now() AND (v.effective_to IS NULL OR v.effective_to>now())) THEN RAISE EXCEPTION 'identity verification requires reusable role identity evidence'; END IF;
  ELSIF NEW.transition_state='SOURCE_VERIFIED' THEN
    IF previous_state<>'IDENTITY_VERIFIED' OR NEW.source_id IS NULL THEN RAISE EXCEPTION 'source verification requires verified identities and a source'; END IF;
    SELECT governance_actor_id,accountable_actor_id INTO prior_governance,prior_accountable FROM ingestion.sdas_delegation_bootstrap_events WHERE proposal_id=NEW.proposal_id AND transition_state='IDENTITY_VERIFIED' ORDER BY event_id DESC LIMIT 1;
    SELECT authority_status,authority_scope INTO source_status,source_scope FROM ingestion.sdas_source_registry WHERE source_id=NEW.source_id;
    IF source_status NOT IN ('verified_limited','authoritative') OR source_scope IS NULL OR source_scope->>'project_scope' IS DISTINCT FROM project OR NOT EXISTS (SELECT 1 FROM ingestion.sdas_source_control_verifications v WHERE v.source_id=NEW.source_id AND v.accountable_actor_id=prior_accountable AND v.project_scope=project AND v.effective_from<=now() AND (v.effective_to IS NULL OR v.effective_to>now())) THEN RAISE EXCEPTION 'source verification requires exact-scope source control and reporting-time evidence'; END IF;
  ELSIF NEW.transition_state='ACTIVE' THEN
    IF previous_state<>'SOURCE_VERIFIED' THEN RAISE EXCEPTION 'activation requires source verification'; END IF;
  ELSIF NEW.transition_state IN ('REVOKED','SUPERSEDED','EXPIRED','REJECTED') THEN
    IF previous_state IS NULL THEN RAISE EXCEPTION 'terminal state requires an existing bootstrap state'; END IF;
  ELSE RAISE EXCEPTION 'unsupported bootstrap transition'; END IF;
  RETURN NEW;
END; $$;

CREATE VIEW ingestion.sdas_governance_bootstrap_exception_queue AS
SELECT p.proposal_id,
  CASE WHEN last_event.transition_state='ACTIVE' THEN 'PASS'
       WHEN last_event.transition_state IN ('REVOKED','SUPERSEDED','EXPIRED','REJECTED') THEN 'QUARANTINE'
       ELSE 'HUMAN_REQUIRED' END AS queue_outcome,
  CASE WHEN last_event.transition_state='GOVERNANCE_APPROVED' THEN 'role_source_or_business_time_evidence_missing'
       WHEN last_event.transition_state='IDENTITY_VERIFIED' THEN 'source_control_or_business_time_evidence_missing'
       WHEN last_event.transition_state='SOURCE_VERIFIED' THEN 'activation_pending'
       WHEN last_event.transition_state='ACTIVE' THEN 'all_activation_requirements_passed'
       ELSE 'terminal_or_unresolved_state' END AS reason_code
FROM ingestion.sdas_delegation_bootstrap_proposals p
CROSS JOIN LATERAL (SELECT transition_state FROM ingestion.sdas_delegation_bootstrap_events e WHERE e.proposal_id=p.proposal_id ORDER BY e.event_id DESC LIMIT 1) last_event;

GRANT SELECT,INSERT ON ingestion.sdas_role_identity_verifications,ingestion.sdas_source_control_verifications TO enterprise_ai_ingestion_runtime;
GRANT USAGE,SELECT ON SEQUENCE ingestion.sdas_role_identity_verifications_verification_id_seq,ingestion.sdas_source_control_verifications_verification_id_seq TO enterprise_ai_ingestion_runtime;
GRANT SELECT ON ingestion.sdas_governance_bootstrap_exception_queue TO enterprise_ai_ingestion_runtime;
