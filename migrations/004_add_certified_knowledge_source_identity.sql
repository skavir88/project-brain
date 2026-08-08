ALTER TABLE ingestion.certified_knowledge_items
  ADD COLUMN IF NOT EXISTS source_record_id text;

UPDATE ingestion.certified_knowledge_items AS knowledge
SET source_record_id = source.record_id
FROM ingestion.credibility_records AS source
WHERE source.record_fingerprint = knowledge.source_fingerprint
  AND knowledge.source_record_id IS NULL;

ALTER TABLE ingestion.certified_knowledge_items
  ALTER COLUMN source_record_id SET NOT NULL;
