CREATE VIEW ingestion.sdas_assurance_passport_portfolio_summary AS
WITH passport_rows AS (
  SELECT
    knowledge_id,
    CASE
      WHEN base_verification_result IN ('VERIFIED', 'VERIFIED_WITH_LIMITATIONS')
        AND COALESCE(authority_inheritance_state, 'missing') = 'eligible'
        AND COALESCE(business_time_state, 'missing') = 'valid'
        AND COALESCE(currentness_state, 'not_assessed') = 'current_eligible'
        AND COALESCE(reliance_state, 'not_eligible') = 'eligible'
        THEN 'VERIFIED'
      WHEN base_verification_result IN ('VERIFIED', 'VERIFIED_WITH_LIMITATIONS')
        AND COALESCE(reliance_state, 'not_eligible') <> 'eligible'
        THEN 'NOT_RELIANCE_ELIGIBLE'
      ELSE base_verification_result
    END AS verification_result,
    limitation_codes
  FROM ingestion.sdas_assurance_passport_projection
),
passport_counts AS (
  SELECT verification_result, count(*) AS passport_count
  FROM passport_rows
  GROUP BY verification_result
),
limitation_counts AS (
  SELECT
    verification_result,
    limitation_code,
    count(*) AS limitation_count
  FROM passport_rows
  LEFT JOIN LATERAL jsonb_array_elements_text(COALESCE(limitation_codes, '[]'::jsonb)) limitation(limitation_code) ON true
  GROUP BY verification_result, limitation_code
)
SELECT
  pc.verification_result,
  pc.passport_count,
  COALESCE(
    jsonb_object_agg(lc.limitation_code, lc.limitation_count ORDER BY lc.limitation_code)
      FILTER (WHERE limitation_code IS NOT NULL),
    '{}'::jsonb
  ) AS limitation_code_counts
FROM passport_counts pc
LEFT JOIN limitation_counts lc
  ON lc.verification_result = pc.verification_result
GROUP BY pc.verification_result, pc.passport_count;

CREATE VIEW ingestion.sdas_assurance_passport_exception_queue AS
WITH normalized AS (
  SELECT
    knowledge_id,
    source_id,
    source_record_id,
    certification_timestamp,
    base_verification_result,
    CASE
      WHEN base_verification_result IN ('VERIFIED', 'VERIFIED_WITH_LIMITATIONS')
        AND COALESCE(authority_inheritance_state, 'missing') = 'eligible'
        AND COALESCE(business_time_state, 'missing') = 'valid'
        AND COALESCE(currentness_state, 'not_assessed') = 'current_eligible'
        AND COALESCE(reliance_state, 'not_eligible') = 'eligible'
        THEN 'VERIFIED'
      WHEN base_verification_result IN ('VERIFIED', 'VERIFIED_WITH_LIMITATIONS')
        AND COALESCE(reliance_state, 'not_eligible') <> 'eligible'
        THEN 'NOT_RELIANCE_ELIGIBLE'
      ELSE base_verification_result
    END AS verification_result,
    limitation_codes,
    passport_authority_state,
    passport_business_time_state,
    currentness_state,
    reliance_state,
    risk_tier,
    latest_post_registration_event_type
  FROM ingestion.sdas_assurance_passport_projection
)
SELECT
  knowledge_id,
  source_id,
  source_record_id,
  certification_timestamp,
  verification_result,
  limitation_codes,
  passport_authority_state,
  passport_business_time_state,
  currentness_state,
  reliance_state,
  risk_tier,
  latest_post_registration_event_type
FROM normalized
WHERE verification_result <> 'VERIFIED'
ORDER BY
  CASE verification_result
    WHEN 'QUARANTINED' THEN 1
    WHEN 'REVOKED_OR_SUPERSEDED' THEN 2
    WHEN 'HUMAN_REQUIRED' THEN 3
    WHEN 'NOT_RELIANCE_ELIGIBLE' THEN 4
    WHEN 'VERIFIED_WITH_LIMITATIONS' THEN 5
    ELSE 6
  END,
  certification_timestamp DESC,
  knowledge_id;

GRANT SELECT ON ingestion.sdas_assurance_passport_portfolio_summary TO enterprise_ai_ingestion_runtime;
GRANT SELECT ON ingestion.sdas_assurance_passport_exception_queue TO enterprise_ai_ingestion_runtime;
