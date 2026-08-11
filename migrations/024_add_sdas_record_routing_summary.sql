CREATE VIEW ingestion.sdas_record_policy_routing_projection AS
WITH latest_policy_decision AS (
  SELECT DISTINCT ON (record_fingerprint)
    record_fingerprint,
    policy_id,
    policy_version,
    approval_mode,
    decision_timestamp,
    decision_reasons
  FROM ingestion.sdas_policy_decisions
  ORDER BY record_fingerprint, decision_timestamp DESC, decision_id DESC
),
latest_assurance_decision AS (
  SELECT DISTINCT ON (record_fingerprint)
    record_fingerprint,
    authority_inheritance_state,
    business_time_state,
    risk_tier,
    currentness_state,
    reliance_state,
    outcome,
    reason_codes,
    policy_version,
    decided_at
  FROM ingestion.sdas_assurance_decisions
  ORDER BY record_fingerprint, decided_at DESC, decision_id DESC
),
matching_active_delegations AS (
  SELECT
    src.source_id,
    count(*) AS matched_active_delegation_count
  FROM ingestion.sdas_source_registry AS src
  JOIN ingestion.sdas_active_delegation_bootstrap AS adb
    ON adb.project_scope = COALESCE(src.authority_scope ->> 'project_scope', '')
   AND adb.document_data_classes ? src.source_type
  GROUP BY src.source_id
)
SELECT
  r.record_fingerprint,
  r.source_id,
  r.record_id,
  r.lifecycle_state,
  r.disposition,
  r.quality_gate_outcome,
  r.observed_at,
  r.ingested_at,
  lpd.policy_id,
  lpd.policy_version,
  lpd.approval_mode AS policy_approval_mode,
  lpd.decision_timestamp AS policy_decision_timestamp,
  COALESCE(lpd.decision_reasons, '[]'::jsonb) AS policy_reason_codes,
  lad.policy_version AS assurance_policy_version,
  lad.outcome AS assurance_outcome,
  lad.decided_at AS assurance_decision_timestamp,
  COALESCE(lad.reason_codes, '[]'::jsonb) AS assurance_reason_codes,
  lad.authority_inheritance_state,
  lad.business_time_state,
  lad.risk_tier,
  lad.currentness_state,
  lad.reliance_state,
  COALESCE(mad.matched_active_delegation_count, 0) AS matched_active_delegation_count,
  CASE
    WHEN COALESCE(mad.matched_active_delegation_count, 0) = 0
      THEN 'WAITING_FOR_EXTERNAL_EVIDENCE'
    ELSE 'MATCHED_ACTIVE_DELEGATION'
  END AS governance_dependency_state,
  CASE
    WHEN COALESCE(lad.outcome, lpd.approval_mode, 'human_required') = 'reject_or_quarantine'
      THEN 'reject_or_quarantine'
    WHEN COALESCE(lad.outcome, lpd.approval_mode, 'human_required') = 'policy_automatic'
      AND COALESCE(mad.matched_active_delegation_count, 0) > 0
      AND COALESCE(lad.authority_inheritance_state, 'missing') = 'eligible'
      AND COALESCE(lad.business_time_state, 'missing') = 'valid'
      AND COALESCE(lad.risk_tier, 'high') = 'low'
      THEN 'policy_automatic'
    ELSE 'human_required'
  END AS effective_routing_outcome,
  CASE
    WHEN COALESCE(lad.outcome, lpd.approval_mode, 'human_required') = 'policy_automatic'
      AND COALESCE(mad.matched_active_delegation_count, 0) = 0
      THEN COALESCE(lad.reason_codes, lpd.decision_reasons, '[]'::jsonb) || '["governance_waiting_for_external_evidence"]'::jsonb
    WHEN lpd.record_fingerprint IS NULL AND lad.record_fingerprint IS NULL
      THEN '["policy_decision_missing"]'::jsonb
    ELSE COALESCE(lad.reason_codes, lpd.decision_reasons, '[]'::jsonb)
  END AS effective_reason_codes
FROM ingestion.credibility_records AS r
LEFT JOIN latest_policy_decision AS lpd
  ON lpd.record_fingerprint = r.record_fingerprint
LEFT JOIN latest_assurance_decision AS lad
  ON lad.record_fingerprint = r.record_fingerprint
LEFT JOIN matching_active_delegations AS mad
  ON mad.source_id = r.source_id;

CREATE VIEW ingestion.sdas_record_policy_routing_summary AS
WITH routing_rows AS (
  SELECT
    effective_routing_outcome,
    effective_reason_codes
  FROM ingestion.sdas_record_policy_routing_projection
),
routing_counts AS (
  SELECT effective_routing_outcome, count(*) AS record_count
  FROM routing_rows
  GROUP BY effective_routing_outcome
),
reason_counts AS (
  SELECT
    effective_routing_outcome,
    reason_code,
    count(*) AS reason_count
  FROM routing_rows
  LEFT JOIN LATERAL jsonb_array_elements_text(COALESCE(effective_reason_codes, '[]'::jsonb)) AS reason(reason_code) ON true
  GROUP BY effective_routing_outcome, reason_code
)
SELECT
  rc.effective_routing_outcome,
  rc.record_count,
  COALESCE(
    jsonb_object_agg(rsn.reason_code, rsn.reason_count ORDER BY rsn.reason_code)
      FILTER (WHERE rsn.reason_code IS NOT NULL),
    '{}'::jsonb
  ) AS reason_code_counts
FROM routing_counts AS rc
LEFT JOIN reason_counts AS rsn
  ON rsn.effective_routing_outcome = rc.effective_routing_outcome
GROUP BY rc.effective_routing_outcome, rc.record_count;

CREATE VIEW ingestion.sdas_record_policy_routing_exception_queue AS
SELECT
  record_fingerprint,
  source_id,
  record_id,
  lifecycle_state,
  quality_gate_outcome,
  policy_id,
  policy_version,
  policy_approval_mode,
  assurance_policy_version,
  assurance_outcome,
  authority_inheritance_state,
  business_time_state,
  currentness_state,
  reliance_state,
  governance_dependency_state,
  effective_routing_outcome,
  effective_reason_codes,
  observed_at,
  ingested_at
FROM ingestion.sdas_record_policy_routing_projection
WHERE effective_routing_outcome <> 'policy_automatic'
ORDER BY
  CASE effective_routing_outcome
    WHEN 'reject_or_quarantine' THEN 1
    WHEN 'human_required' THEN 2
    ELSE 3
  END,
  ingested_at DESC NULLS LAST,
  record_fingerprint;

GRANT SELECT ON ingestion.sdas_record_policy_routing_projection TO enterprise_ai_ingestion_runtime;
GRANT SELECT ON ingestion.sdas_record_policy_routing_summary TO enterprise_ai_ingestion_runtime;
GRANT SELECT ON ingestion.sdas_record_policy_routing_exception_queue TO enterprise_ai_ingestion_runtime;
