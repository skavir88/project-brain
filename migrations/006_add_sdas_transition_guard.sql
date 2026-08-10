-- Additive guard for the SDAS assurance-event lifecycle. Existing rows are
-- initial assessed_partial events and remain untouched.
CREATE FUNCTION ingestion.validate_sdas_assurance_transition() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  latest_state text;
BEGIN
  SELECT new_state INTO latest_state
  FROM ingestion.sdas_assurance_events
  WHERE knowledge_id = NEW.knowledge_id
  ORDER BY event_id DESC
  LIMIT 1;

  IF latest_state IS NULL THEN
    IF NEW.previous_state IS NOT NULL OR NEW.new_state <> 'assessed_partial' THEN
      RAISE EXCEPTION 'invalid initial SDAS assurance transition';
    END IF;
    RETURN NEW;
  END IF;

  IF NEW.previous_state IS DISTINCT FROM latest_state THEN
    RAISE EXCEPTION 'SDAS previous state does not match append-only history';
  END IF;
  IF NOT (
    (latest_state = 'assessed_partial' AND NEW.new_state IN ('evidence_complete','superseded','revoked')) OR
    (latest_state = 'evidence_complete' AND NEW.new_state IN ('certified_assured','superseded','revoked')) OR
    (latest_state = 'certified_assured' AND NEW.new_state IN ('superseded','revoked'))
  ) THEN
    RAISE EXCEPTION 'invalid SDAS assurance transition';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER sdas_assurance_events_transition_guard
BEFORE INSERT ON ingestion.sdas_assurance_events
FOR EACH ROW EXECUTE FUNCTION ingestion.validate_sdas_assurance_transition();
