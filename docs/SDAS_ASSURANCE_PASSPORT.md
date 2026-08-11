# SDAS Assurance Passport

Status: Implemented in ST1-071 as an additive read model and private service
contract. It does not activate governance, certify data, or weaken currentness,
authority, or reliance boundaries.

Contract revision: ST1-079 upgrades the private contract to
`SDAS Assurance Passport v0.1`, with explicit dimension-level explanation and
an `INTEGRITY_FAILURE` outcome separated from generic quarantine.

## Purpose

The assurance passport is a machine-readable projection over append-only SDAS
evidence for one already certified datum. It answers, from persisted evidence
only:

- what certified datum is being referenced;
- where it originated and when it was acquired;
- what business/effective time evidence exists;
- which authority, policy, transformation, and certification evidence exists;
- whether the evidence chain is intact;
- whether the datum is revoked, superseded, quarantined, or still only usable
  with limitations.

It does not create mutable truth. It reflects the best deterministic state of
the recorded evidence chain at read time.

## Projection Boundary

The projection reads only additive, append-only evidence already present in the
isolated ingestion schema:

- `credibility_records`
- `certification_audit_events`
- `certified_knowledge_items`
- `sdas_policy_decisions`
- `sdas_assurance_decisions`
- `sdas_assurance_envelopes`
- `sdas_assurance_events`
- `sdas_business_time_evidence`
- `sdas_authority_assertions`
- `sdas_source_registry`
- `sdas_acquisition_events`
- `sdas_transformations`
- `sdas_consumption_events`
- `sdas_post_registration_events`

The projection does not read raw organizational content, external models,
filesystem metadata, or secrets.

## Verification Results

The projection emits one deterministic base result per certified datum:

- `VERIFIED`
- `VERIFIED_WITH_LIMITATIONS`
- `HUMAN_REQUIRED`
- `REVOKED_OR_SUPERSEDED`
- `QUARANTINED`
- `INTEGRITY_FAILURE`

The private service classifier may additionally return
`NOT_RELIANCE_ELIGIBLE` when a caller explicitly requires reliance eligibility
and the stored reliance state is not `eligible`.

These results do not collapse the underlying dimensions into one opaque score.
The passport also returns explicit dimension states and limitation codes.

The `INTEGRITY_FAILURE` result is reserved for deterministic evidence-chain
breaks such as provenance-link mismatches or assurance/consumption event-chain
hash discontinuity. It is not used for governance, business-time, or risk
limitations that are otherwise structurally intact.

## Deterministic Rules

- `REVOKED_OR_SUPERSEDED`:
  a post-registration revocation/supersession exists, or authority evidence has
  already been revoked/superseded.
- `QUARANTINED`:
  conflicting authority/business-time evidence exists, a high-risk fact was
  evaluated, and the chain is otherwise structurally intact.
- `INTEGRITY_FAILURE`:
  the recorded evidence chain is malformed or provenance links do not
  reconcile.
- `HUMAN_REQUIRED`:
  authority or business-time evidence is missing, or the persisted policy path
  already routed the datum to accountable review.
- `VERIFIED_WITH_LIMITATIONS`:
  the certified datum is traceable but still has explicit limitations such as
  historical/stale/not-assessed currentness, partial assurance completion, or
  no reliance eligibility.
- `VERIFIED`:
  the append-only chain is internally consistent and the required evidence for
  the selected private scope is complete without the above blockers.

## Governance Dependency

The E1/E2/E3 organizational authority dependency is not a failed technical
task. It is represented operationally as:

`WAITING_FOR_EXTERNAL_EVIDENCE`

That state blocks real authority inheritance and real `policy_automatic`
routing, but it does not block unrelated SDAS development such as the
assurance-passport layer.

## Private Service Contract

The loopback/private ingestion service now supports:

`GET /v1/sdas/passport?knowledge_id=<hex64>&require_reliance_eligible=false`

The route returns only sanitized machine-readable state. It does not mutate the
database, trigger certification, or create currentness/authority/reliance.

The payload is versioned and dimension-based. At minimum it exposes:

- `identity`
- `provenance`
- `integrity`
- `authority`
- `business_time`
- `validation`
- `policy`
- `human_review`
- `certification`
- `currentness`
- `reliance`
- `conflict`
- `revocation`
- `supersession`
- `consumption`

Each dimension carries:

- `status`
- `evidence_refs`
- `limitations`
- `policy_version`, where relevant
- `verified_at` or `evaluated_at`, where applicable

The same layer now also exposes two portfolio-level private read models:

- `GET /v1/sdas/passports/summary`
- `GET /v1/sdas/passports/exceptions`

`summary` returns deterministic counts by outcome plus aggregated limitation
codes. `exceptions` returns only non-`VERIFIED` passports so operators can
triage accountable review, quarantine, revocation/supersession, or
reliance-ineligible items without querying raw evidence tables manually.

ST1-081 adds one private read-only adjunct:

- `GET /v1/sdas/passport/index?knowledge_id=<hex64>`

This adjunct does not widen trust or retrieval scope. It is limited to already
certified items and exposes only non-secret isolated index-projection state:

- expected Qdrant collection name
- deterministic point identifier derived from `knowledge_id`
- collection existence/runtime status
- point presence/absence
- payload-identity contract checks against Certified Knowledge identity

It does not expose raw vectors, embedding credentials, provider secrets,
retrieval thresholds, or uncertified data. A missing or uncertified
`knowledge_id` returns `404`, not discovery metadata about non-certified
records.
