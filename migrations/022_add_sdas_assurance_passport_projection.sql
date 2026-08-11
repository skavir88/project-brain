CREATE OR REPLACE VIEW ingestion.sdas_assurance_passport_projection AS
WITH latest_policy_decision AS (
  SELECT DISTINCT ON (record_fingerprint)
    record_fingerprint,
    policy_id,
    policy_version,
    approval_mode,
    decision_reasons,
    evidence_quality
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
latest_post_registration AS (
  SELECT DISTINCT ON (knowledge_id)
    knowledge_id,
    event_type,
    event_at,
    reason_code
  FROM ingestion.sdas_post_registration_events
  ORDER BY knowledge_id, event_at DESC, post_registration_event_id DESC
),
record_authority_rollup AS (
  SELECT
    subject_id AS record_fingerprint,
    count(*) FILTER (
      WHERE assertion_state = 'asserted'
        AND authority_basis = 'conflicting_authority'
        AND (effective_from IS NULL OR effective_from <= now())
        AND (effective_to IS NULL OR effective_to > now())
    ) AS conflicting_count,
    count(*) FILTER (
      WHERE assertion_state = 'asserted'
        AND authority_basis IN (
          'authoritative_by_registered_system',
          'authoritative_by_accountable_owner',
          'authoritative_by_approved_document_class',
          'corroborated_authority'
        )
        AND (effective_from IS NULL OR effective_from <= now())
        AND (effective_to IS NULL OR effective_to > now())
    ) AS verified_count,
    count(*) FILTER (WHERE assertion_state IN ('revoked', 'superseded')) AS revoked_or_superseded_count
  FROM ingestion.sdas_authority_assertions
  WHERE subject_type = 'record'
  GROUP BY subject_id
),
source_authority_rollup AS (
  SELECT
    subject_id AS source_id,
    count(*) FILTER (
      WHERE assertion_state = 'asserted'
        AND authority_basis = 'conflicting_authority'
        AND (effective_from IS NULL OR effective_from <= now())
        AND (effective_to IS NULL OR effective_to > now())
    ) AS conflicting_count,
    count(*) FILTER (
      WHERE assertion_state = 'asserted'
        AND authority_basis IN (
          'authoritative_by_registered_system',
          'authoritative_by_accountable_owner',
          'authoritative_by_approved_document_class',
          'corroborated_authority'
        )
        AND (effective_from IS NULL OR effective_from <= now())
        AND (effective_to IS NULL OR effective_to > now())
    ) AS verified_count,
    count(*) FILTER (WHERE assertion_state IN ('revoked', 'superseded')) AS revoked_or_superseded_count
  FROM ingestion.sdas_authority_assertions
  WHERE subject_type = 'source'
  GROUP BY subject_id
),
business_time_rollup AS (
  SELECT
    record_fingerprint,
    count(*) FILTER (
      WHERE time_kind IN ('report_period', 'issue_date', 'effective_date', 'event_date', 'approval_date')
    ) AS substantive_time_count,
    count(*) FILTER (
      WHERE time_kind IN ('filesystem_timestamp', 'acquisition_timestamp')
    ) AS non_business_time_count,
    count(DISTINCT COALESCE(start_at::text, '') || '|' || COALESCE(end_at::text, '') || '|' || COALESCE(value_text, '')) FILTER (
      WHERE time_kind IN ('report_period', 'issue_date', 'effective_date', 'event_date', 'approval_date')
    ) AS distinct_time_values,
    jsonb_agg(
      jsonb_strip_nulls(
        jsonb_build_object(
          'time_kind', time_kind,
          'start_at', start_at,
          'end_at', end_at,
          'value_text', value_text,
          'verification_method', verification_method,
          'evidence_quality', evidence_quality
        )
      )
      ORDER BY business_time_evidence_id
    ) AS time_evidence
  FROM ingestion.sdas_business_time_evidence
  GROUP BY record_fingerprint
),
transformation_rollup AS (
  SELECT
    output_fingerprint AS record_fingerprint,
    count(*) AS transformation_count,
    bool_and(deterministic) AS all_deterministic
  FROM ingestion.sdas_transformations
  GROUP BY output_fingerprint
),
assurance_chain_validity AS (
  SELECT
    knowledge_id,
    COALESCE(bool_and(previous_event_hash IS NOT DISTINCT FROM expected_previous), true) AS chain_valid
  FROM (
    SELECT
      knowledge_id,
      previous_event_hash,
      lag(event_hash) OVER (PARTITION BY knowledge_id ORDER BY event_id) AS expected_previous
    FROM ingestion.sdas_assurance_events
  ) ordered
  GROUP BY knowledge_id
),
consumption_chain_validity AS (
  SELECT
    knowledge_id,
    COALESCE(bool_and(previous_event_hash IS NOT DISTINCT FROM expected_previous), true) AS chain_valid
  FROM (
    SELECT
      knowledge_id,
      previous_event_hash,
      lag(event_hash) OVER (PARTITION BY knowledge_id ORDER BY event_id) AS expected_previous
    FROM ingestion.sdas_consumption_events
  ) ordered
  GROUP BY knowledge_id
),
consumption_rollup AS (
  SELECT
    knowledge_id,
    count(*) AS consumption_count,
    max(recorded_at) AS last_consumed_at
  FROM ingestion.sdas_consumption_events
  GROUP BY knowledge_id
)
SELECT
  k.knowledge_id,
  k.source_fingerprint,
  k.source_record_id,
  r.source_id,
  r.record_id,
  r.observed_at,
  r.ingested_at,
  a.acquired_at,
  k.certification_event_id,
  k.certifying_actor,
  k.certification_timestamp,
  k.certification_policy_version,
  env.assurance_level,
  env.assurance_state,
  lad.policy_version AS assurance_policy_version,
  lad.authority_inheritance_state,
  lad.business_time_state,
  lad.risk_tier,
  lad.currentness_state,
  lad.reliance_state,
  lad.outcome AS assurance_outcome,
  lpd.policy_id,
  lpd.policy_version AS policy_version,
  lpd.approval_mode AS policy_approval_mode,
  src.authority_status AS source_registry_authority_status,
  COALESCE(tr.transformation_count, 0) AS transformation_count,
  COALESCE(tr.all_deterministic, false) AS all_transformations_deterministic,
  COALESCE(bt.time_evidence, '[]'::jsonb) AS business_time_evidence,
  COALESCE(bt.substantive_time_count, 0) AS substantive_business_time_count,
  COALESCE(bt.distinct_time_values, 0) AS distinct_business_time_values,
  COALESCE(c.consumption_count, 0) AS consumption_count,
  c.last_consumed_at,
  post.event_type AS latest_post_registration_event_type,
  post.event_at AS latest_post_registration_event_at,
  CASE
    WHEN COALESCE(ra.revoked_or_superseded_count, 0) > 0 OR COALESCE(sa.revoked_or_superseded_count, 0) > 0
      THEN 'revoked_or_superseded'
    WHEN COALESCE(ra.conflicting_count, 0) > 0 OR COALESCE(sa.conflicting_count, 0) > 0
      THEN 'conflict'
    WHEN COALESCE(ra.verified_count, 0) > 0 OR COALESCE(sa.verified_count, 0) > 0 OR src.authority_status IN ('verified_limited', 'authoritative')
      THEN 'verified'
    ELSE 'missing'
  END AS passport_authority_state,
  CASE
    WHEN COALESCE(bt.distinct_time_values, 0) > 1 THEN 'conflict'
    WHEN COALESCE(bt.substantive_time_count, 0) > 0 THEN 'valid'
    ELSE 'missing'
  END AS passport_business_time_state,
  CASE
    WHEN k.source_fingerprint <> r.record_fingerprint OR env.source_fingerprint IS DISTINCT FROM k.source_fingerprint THEN false
    ELSE true
  END AS provenance_link_valid,
  COALESCE(acv.chain_valid, true) AS assurance_event_chain_valid,
  COALESCE(ccv.chain_valid, true) AS consumption_event_chain_valid,
  CASE
    WHEN post.event_type IN ('revocation', 'supersession') OR COALESCE(ra.revoked_or_superseded_count, 0) > 0 OR COALESCE(sa.revoked_or_superseded_count, 0) > 0
      THEN 'REVOKED_OR_SUPERSEDED'
    WHEN k.source_fingerprint <> r.record_fingerprint
      OR env.source_fingerprint IS DISTINCT FROM k.source_fingerprint
      OR NOT COALESCE(acv.chain_valid, true)
      OR NOT COALESCE(ccv.chain_valid, true)
      THEN 'INTEGRITY_FAILURE'
    WHEN COALESCE(ra.conflicting_count, 0) > 0 OR COALESCE(sa.conflicting_count, 0) > 0
      OR COALESCE(bt.distinct_time_values, 0) > 1
      OR COALESCE(lad.risk_tier, 'low') = 'high'
      OR COALESCE(lad.outcome, lpd.approval_mode, 'human_required') = 'reject_or_quarantine'
      THEN 'QUARANTINED'
    WHEN COALESCE(lad.outcome, lpd.approval_mode, 'human_required') = 'human_required'
      OR (
        COALESCE(ra.verified_count, 0) = 0
        AND COALESCE(sa.verified_count, 0) = 0
        AND src.authority_status NOT IN ('verified_limited', 'authoritative')
      )
      OR COALESCE(bt.substantive_time_count, 0) = 0
      THEN 'HUMAN_REQUIRED'
    WHEN COALESCE(lad.currentness_state, 'not_assessed') IN ('historical', 'stale', 'conflict', 'not_assessed')
      OR COALESCE(env.assurance_state, 'assessed_partial') <> 'certified_assured'
      THEN 'VERIFIED_WITH_LIMITATIONS'
    ELSE 'VERIFIED'
  END AS base_verification_result,
  to_jsonb(ARRAY_REMOVE(ARRAY[
    CASE WHEN COALESCE(lad.outcome, lpd.approval_mode, 'human_required') = 'human_required'
      AND COALESCE((lpd.decision_reasons ? 'authority_not_verified'), false)
      THEN 'governance_waiting_for_external_evidence' END,
    CASE WHEN COALESCE(ra.verified_count, 0) = 0 AND COALESCE(sa.verified_count, 0) = 0 AND src.authority_status NOT IN ('verified_limited', 'authoritative')
      THEN 'authority_missing' END,
    CASE WHEN COALESCE(bt.substantive_time_count, 0) = 0 THEN 'business_time_missing' END,
    CASE WHEN COALESCE(bt.distinct_time_values, 0) > 1 THEN 'business_time_conflict' END,
    CASE WHEN COALESCE(lad.currentness_state, 'not_assessed') IN ('historical', 'stale', 'conflict', 'not_assessed')
      THEN 'currentness_limited' END,
    CASE WHEN COALESCE(lad.reliance_state, 'not_eligible') = 'not_eligible' THEN 'reliance_not_eligible' END,
    CASE WHEN COALESCE(env.assurance_state, 'assessed_partial') <> 'certified_assured' THEN 'assurance_partial' END,
    CASE WHEN post.event_type IN ('revocation', 'supersession') THEN 'post_registration_terminal_event' END,
    CASE WHEN COALESCE(ra.conflicting_count, 0) > 0 OR COALESCE(sa.conflicting_count, 0) > 0 THEN 'authority_conflict' END,
    CASE WHEN NOT COALESCE(acv.chain_valid, true) OR NOT COALESCE(ccv.chain_valid, true) THEN 'event_hash_chain_mismatch' END,
    CASE WHEN env.source_fingerprint IS DISTINCT FROM k.source_fingerprint OR k.source_fingerprint <> r.record_fingerprint THEN 'provenance_link_mismatch' END,
    CASE WHEN COALESCE(lad.risk_tier, 'low') = 'high' THEN 'high_risk_fact' END
  ], NULL)) AS limitation_codes,
  r.quality_gate_outcome,
  COALESCE(lpd.decision_reasons, '[]'::jsonb) AS policy_reason_codes,
  COALESCE(lad.reason_codes, '[]'::jsonb) AS assurance_reason_codes
FROM ingestion.certified_knowledge_items AS k
JOIN ingestion.credibility_records AS r
  ON r.record_fingerprint = k.source_fingerprint
LEFT JOIN ingestion.sdas_assurance_envelopes AS env
  ON env.knowledge_id = k.knowledge_id
LEFT JOIN latest_assurance_decision AS lad
  ON lad.record_fingerprint = k.source_fingerprint
LEFT JOIN latest_policy_decision AS lpd
  ON lpd.record_fingerprint = k.source_fingerprint
LEFT JOIN ingestion.sdas_source_registry AS src
  ON src.source_id = r.source_id
LEFT JOIN LATERAL (
  SELECT acquired_at
  FROM ingestion.sdas_acquisition_events
  WHERE source_id = r.source_id
  ORDER BY acquired_at DESC, acquisition_event_id DESC
  LIMIT 1
) AS a ON true
LEFT JOIN record_authority_rollup AS ra
  ON ra.record_fingerprint = k.source_fingerprint
LEFT JOIN source_authority_rollup AS sa
  ON sa.source_id = r.source_id
LEFT JOIN business_time_rollup AS bt
  ON bt.record_fingerprint = k.source_fingerprint
LEFT JOIN transformation_rollup AS tr
  ON tr.record_fingerprint = k.source_fingerprint
LEFT JOIN assurance_chain_validity AS acv
  ON acv.knowledge_id = k.knowledge_id
LEFT JOIN consumption_chain_validity AS ccv
  ON ccv.knowledge_id = k.knowledge_id
LEFT JOIN consumption_rollup AS c
  ON c.knowledge_id = k.knowledge_id
LEFT JOIN latest_post_registration AS post
  ON post.knowledge_id = k.knowledge_id;

GRANT SELECT ON ingestion.sdas_assurance_passport_projection TO enterprise_ai_ingestion_runtime;
