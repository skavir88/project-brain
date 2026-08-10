# Enterprise AI Ingestion Service

This is a Stage 1 local-only synthetic ingestion, validation, duplicate-control, and initial credibility-gate slice. It does not persist records, connect to platform backends, or use credentials.

## Local health check

```powershell
python app.py
Invoke-WebRequest http://127.0.0.1:8080/health -UseBasicParsing
```

## Synthetic intake contract

`POST /v1/records` accepts only this minimal JSON structure:

```json
{
  "source_id": "synthetic-source",
  "record_id": "synthetic-record-001",
  "payload": {"example": true}
}
```

The service returns `202` for a first structurally valid request and `422` with machine-readable validation errors for invalid requests. For accepted requests it trims surrounding whitespace from `source_id` and `record_id`, then returns a SHA-256 fingerprint of a stable JSON representation of that canonical record.

For this local demonstration only, the process keeps accepted fingerprints in memory. A repeated equivalent fingerprint returns `409` with `duplicate=true`. This state is cleared whenever the service restarts and is never written to disk, a Docker volume, or an external backend.

## Initial credibility gate

A valid and unique record is not automatically credible or certified. The gate returns one transient disposition:

- `certification_candidate`: a usable `provenance.source_reference` is present and the deterministic temporal/consistency checks pass. This is only eligible for later certification; it is not final certification.
- `human_review_required`: provenance is absent or insufficient. The record remains processable and returns `202` with `provenance_insufficient`.
- `rejected`: a deterministic quality check fails. A supplied `observed_at` must be an ISO-8601 timestamp with timezone and not be in the future. If `payload.source_id` is supplied, it must match canonical `source_id`.

Every non-candidate response contains a machine-readable `reason_code`. The gate uses no LLM, scoring model, durable audit record, or external service.

## SDAS v0.1 pilot endpoints

The isolated deployed service also exposes two private, additive endpoints for
the internal SDAS pilot. They do not alter a record's certification lifecycle:

- `POST /v1/sdas/assess` creates one immutable evidence-only assurance envelope
  for an existing Certified Knowledge identifier under
  `sdas-v0.1-pilot-assessment-v1`.
- `POST /v1/sdas/consumption` appends sanitized downstream-use evidence for
  existing Certified Knowledge identifiers. It accepts hashes and provenance
  linkage, not raw prompts, answers, source content, credentials, or a
  reliance decision.

Both routes are available only through the loopback/private deployment path.
Their tables are additive and append-only. `SDAS-1` expresses a traceable
certification chain only; it does not mean current, authoritative, correct,
or reliance-eligible.

## Docker Compose

```powershell
docker compose -f compose.yaml config
```

The Compose file binds the service only to loopback. It is intended solely for local verification.
