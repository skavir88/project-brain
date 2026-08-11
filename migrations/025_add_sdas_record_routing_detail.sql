CREATE VIEW ingestion.sdas_record_policy_routing_detail AS
WITH source_context AS (
  SELECT
    source_id,
    source_type,
    system_location_identity,
    owner_actor_id,
    business_purpose,
    authority_status,
    authority_scope,
    effective_from,
    effective_to,
    evidence_quality
  FROM ingestion.sdas_source_registry
),
matching_active_delegations AS (
  SELECT
    src.source_id,
    jsonb_agg(
      jsonb_build_object(
        'proposal_id', adb.proposal_id,
        'approval_id', adb.approval_id,
        'project_scope', adb.project_scope,
        'intended_role_class', adb.intended_role_class,
        'document_data_classes', adb.document_data_classes,
        'permitted_fact_classes', adb.permitted_fact_classes,
        'prohibited_fact_classes', adb.prohibited_fact_classes,
        'business_time_rule', adb.business_time_rule,
        'policy_version', adb.policy_version
      )
      ORDER BY adb.proposal_id
    ) AS matched_active_delegations
  FROM source_context AS src
  JOIN ingestion.sdas_active_delegation_bootstrap AS adb
    ON adb.project_scope = COALESCE(src.authority_scope ->> 'project_scope', '')
   AND adb.document_data_classes ? src.source_type
  GROUP BY src.source_id
)
SELECT
  rp.record_fingerprint,
  rp.source_id,
  rp.record_id,
  rp.lifecycle_state,
  rp.disposition,
  rp.quality_gate_outcome,
  rp.observed_at,
  rp.ingested_at,
  rp.policy_id,
  rp.policy_version,
  rp.policy_approval_mode,
  rp.policy_decision_timestamp,
  rp.policy_reason_codes,
  rp.assurance_policy_version,
  rp.assurance_outcome,
  rp.assurance_decision_timestamp,
  rp.assurance_reason_codes,
  rp.authority_inheritance_state,
  rp.business_time_state,
  rp.risk_tier,
  rp.currentness_state,
  rp.reliance_state,
  rp.matched_active_delegation_count,
  rp.governance_dependency_state,
  rp.effective_routing_outcome,
  rp.effective_reason_codes,
  sc.source_type,
  sc.system_location_identity,
  sc.owner_actor_id,
  sc.business_purpose,
  sc.authority_status AS source_registry_authority_status,
  sc.authority_scope AS source_registry_authority_scope,
  sc.effective_from AS source_registry_effective_from,
  sc.effective_to AS source_registry_effective_to,
  sc.evidence_quality AS source_registry_evidence_quality,
  COALESCE(mad.matched_active_delegations, '[]'::jsonb) AS matched_active_delegations,
  jsonb_strip_nulls(
    jsonb_build_object(
      'policy_decision_present', rp.policy_id IS NOT NULL,
      'assurance_decision_present', rp.assurance_outcome IS NOT NULL,
      'matched_active_delegation_present', rp.matched_active_delegation_count > 0,
      'governance_waiting', rp.governance_dependency_state = 'WAITING_FOR_EXTERNAL_EVIDENCE',
      'source_authority_verified', sc.authority_status IN ('verified_limited', 'authoritative'),
      'authority_inheritance_eligible', rp.authority_inheritance_state = 'eligible',
      'business_time_valid', rp.business_time_state = 'valid',
      'risk_low', rp.risk_tier = 'low',
      'currentness_current_eligible', rp.currentness_state = 'current_eligible',
      'reliance_eligible', rp.reliance_state = 'eligible'
    )
  ) AS triage_signals
FROM ingestion.sdas_record_policy_routing_projection AS rp
LEFT JOIN source_context AS sc
  ON sc.source_id = rp.source_id
LEFT JOIN matching_active_delegations AS mad
  ON mad.source_id = rp.source_id;

GRANT SELECT ON ingestion.sdas_record_policy_routing_detail TO enterprise_ai_ingestion_runtime;
