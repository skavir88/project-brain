-- Additive independent predicates. Defaults are intentionally conservative;
-- they do not infer authority, currentness, or reliance from certification.
ALTER TABLE ingestion.sdas_assurance_envelopes
  ADD COLUMN authority_state text NOT NULL DEFAULT 'not_assessed'
    CHECK (authority_state IN ('not_assessed','not_authoritative','authoritative')),
  ADD COLUMN currentness_state text NOT NULL DEFAULT 'not_assessed'
    CHECK (currentness_state IN ('not_assessed','insufficient_certified_evidence','assessed_current')),
  ADD COLUMN reliance_eligibility_state text NOT NULL DEFAULT 'not_eligible'
    CHECK (reliance_eligibility_state IN ('not_eligible','assessment_pending','eligible'));
