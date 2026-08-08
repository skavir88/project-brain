CREATE ROLE enterprise_ai_ingestion_owner NOLOGIN;
CREATE ROLE enterprise_ai_ingestion_runtime LOGIN;
CREATE DATABASE enterprise_ai_ingestion_mvp OWNER enterprise_ai_ingestion_owner;
\connect enterprise_ai_ingestion_mvp
REVOKE ALL ON DATABASE enterprise_ai_ingestion_mvp FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA ingestion AUTHORIZATION enterprise_ai_ingestion_owner;
CREATE TABLE ingestion.credibility_records (
  record_fingerprint char(64) PRIMARY KEY CHECK (record_fingerprint ~ '^[0-9a-f]{64}$'),
  canonical_record jsonb NOT NULL,
  provenance jsonb,
  source_id text NOT NULL,
  record_id text NOT NULL,
  observed_at timestamptz,
  ingested_at timestamptz NOT NULL DEFAULT now(),
  disposition text NOT NULL CHECK (disposition IN ('certification_candidate','human_review_required','rejected')),
  reason_code text,
  quality_gate_outcome text NOT NULL CHECK (quality_gate_outcome IN ('passed','review_required','failed')),
  lifecycle_state text NOT NULL CHECK (lifecycle_state IN ('certification_candidate','human_review_required','rejected','certified'))
);
CREATE INDEX credibility_records_disposition_idx ON ingestion.credibility_records (disposition);
GRANT CONNECT ON DATABASE enterprise_ai_ingestion_mvp TO enterprise_ai_ingestion_runtime;
GRANT USAGE ON SCHEMA ingestion TO enterprise_ai_ingestion_runtime;
GRANT SELECT, INSERT ON ingestion.credibility_records TO enterprise_ai_ingestion_runtime;
