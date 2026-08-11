CREATE OR REPLACE VIEW ingestion.sdas_assurance_passport_index_projection AS
SELECT
  k.knowledge_id,
  k.source_fingerprint,
  k.source_record_id,
  k.certification_event_id,
  lower(
    substr(k.knowledge_id, 1, 8) || '-' ||
    substr(k.knowledge_id, 9, 4) || '-' ||
    substr(k.knowledge_id, 13, 4) || '-' ||
    substr(k.knowledge_id, 17, 4) || '-' ||
    substr(k.knowledge_id, 21, 12)
  ) AS qdrant_point_id,
  'enterprise_ai_certified_knowledge_v1'::text AS qdrant_collection_name,
  COALESCE(p.base_verification_result, 'HUMAN_REQUIRED') AS passport_base_verification_result,
  COALESCE(p.currentness_state, 'not_assessed') AS currentness_state,
  COALESCE(p.reliance_state, 'not_eligible') AS reliance_state,
  p.latest_post_registration_event_type,
  k.certification_timestamp,
  k.certification_policy_version,
  COALESCE(p.limitation_codes, '[]'::jsonb) AS limitation_codes
FROM ingestion.certified_knowledge_items AS k
LEFT JOIN ingestion.sdas_assurance_passport_projection AS p
  ON p.knowledge_id = k.knowledge_id
WHERE k.lifecycle_state = 'certified';

GRANT SELECT ON ingestion.sdas_assurance_passport_index_projection TO enterprise_ai_ingestion_runtime;
