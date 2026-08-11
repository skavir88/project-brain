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

## SDAS assurance passport

`GET /v1/sdas/passport?knowledge_id=<hex64>&require_reliance_eligible=false`
returns a machine-readable assurance passport for one existing Certified
Knowledge item. The route reads only the additive append-only SDAS projection;
it does not certify, mutate, or create truth.

The response exposes the evidence chain state, verification result,
limitations, business-time evidence summary, post-registration state, and
chain-integrity flags. When `require_reliance_eligible=true`, an otherwise
verified passport deterministically downgrades to
`NOT_RELIANCE_ELIGIBLE` unless the stored reliance state is `eligible`.

`GET /v1/sdas/passports/summary` returns deterministic portfolio counts by
passport outcome plus aggregated limitation-code counts.

`GET /v1/sdas/passports/exceptions` returns only non-`VERIFIED` passports for
triage. An optional `verification_result` filter narrows the queue to one
deterministic class such as `HUMAN_REQUIRED` or `QUARANTINED`.

## SDAS record routing

`GET /v1/sdas/routing/summary` returns deterministic pre-certification routing
counts by `policy_automatic`, `human_required`, and
`reject_or_quarantine`.

`GET /v1/sdas/routing/exceptions` returns only non-`policy_automatic` records
for operator triage. An optional `outcome` filter narrows the queue to one
deterministic class such as `human_required` or `reject_or_quarantine`.

`GET /v1/sdas/routing/detail?record_fingerprint=<hex64>` returns one
deterministic routing explanation for operator triage. It exposes the
effective routing outcome, governance dependency state, dominant reason codes,
the relevant policy and assurance signals, source registration context, and
matched active-delegation evidence when present.

## Docker Compose

```powershell
docker compose -f compose.yaml config
```

The Compose file binds the service only to loopback. It is intended solely for local verification.
