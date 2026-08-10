# Sahra Data Assurance Standard v0.1 — Proposal

Status: Accepted for internal experimental pilot validation — implementation is limited to ST1-055 and remains decision-gated for SDAS v0.2.

## Purpose and Boundary

SDAS v0.1 is a machine-verifiable evidence model for a data record that has
been certified in Enterprise AI. It records the assurance evidence available
for a claim; it does not create insurance, pricing, underwriting, legal
guarantees, legal liability, source authority, or present-day truth.

The existing 49 Certified Knowledge items are pilot evidence only. They were
back-assessed under the approved pilot policy; this is not an automatic claim
of full SDAS compliance, authority, currentness, or reliance eligibility. No
item was re-certified, revoked, or superseded.

## Assurance Dimensions and Mandatory Evidence

Each dimension is `present`, `partial`, `missing`, or `not_applicable`; an
unknown value is never silently upgraded to `present`.

| Dimension | Mandatory machine-verifiable fields |
|---|---|
| Source | `source_id`, `source_class`, `source_reference`, `source_scope` |
| Acquisition | `acquisition_event_id`, `acquired_at_utc`, `acquisition_method`, `collector_identity`, `read_only_assertion` |
| Source identity | `source_identity_type`, `source_identity_value`, `source_locator_reference`, `source_owner_reference` |
| Timestamp | `observed_at`, `reporting_period_start`, `reporting_period_end`, `document_issue_date`, `timestamp_semantics`, `timezone_or_calendar` |
| Fingerprint / integrity | `source_fingerprint_algorithm`, `source_fingerprint`, `acquired_artifact_fingerprint`, `integrity_verified_at_utc` |
| Extraction / transformation | `transformation_run_id`, `extractor_name`, `extractor_version`, `input_fingerprint`, `output_fingerprint`, `transformation_timestamp_utc` |
| Validation | `validation_run_id`, `validation_rule_set_id`, `validation_rule_set_version`, `validation_outcome`, `validation_evidence_reference` |
| Human reviewer / actor | `review_event_id`, `reviewer_identifier`, `reviewer_role_reference`, `reviewed_at_utc` |
| Review decision | `review_decision`, `decision_rationale_reference`, `review_candidate_id` |
| Certification | `certification_event_id`, `certification_actor_identifier`, `certification_policy_version`, `certification_timestamp_utc`, `certification_transition` |
| Audit | `audit_event_id`, `audit_event_hash`, `previous_event_hash`, `recorded_at_utc` |
| Certified Knowledge registration | `knowledge_id`, `source_record_id`, `knowledge_registration_timestamp_utc`, `projection_version`, `projection_fingerprint` |
| Supersession / revocation | `assurance_state`, `supersedes_knowledge_id`, `superseded_by_knowledge_id`, `revocation_event_id`, `state_changed_at_utc`, `state_reason_code` |
| Consumption / RAG provenance | `consumption_event_id`, `consumed_at_utc`, `consumer_identity`, `knowledge_ids`, `retrieval_policy_version`, `retrieval_threshold`, `provenance_set_fingerprint`, `outcome_class` |

`source_locator_reference` may point to protected runtime-local evidence. Raw
UNC paths, filenames, document content, secrets, or reviewer-private notes
must not be stored in Git merely to satisfy an SDAS field.

## Proposed Lifecycle and State Model

The existing `credibility_records.lifecycle_state` remains unchanged. SDAS
adds a separate assurance-envelope state, not a replacement lifecycle:

```text
unassessed
  -> assessed_partial
  -> evidence_complete
  -> certified_assured
  -> superseded | revoked
```

- `unassessed`: no SDAS evaluation has been recorded.
- `assessed_partial`: an assessment exists and one or more mandatory fields
  are missing or partial.
- `evidence_complete`: all mandatory evidence for the selected assurance
  level is present and integrity-verifiable; this alone does not certify data.
- `certified_assured`: a certified record has a complete SDAS envelope for
  its declared level.
- `superseded`: a later identified record supersedes it; the original audit
  chain remains immutable.
- `revoked`: a governed revocation event marks reliance ineligible without
  deleting the record or prior audit events.

Allowed transitions must be append-only, actor-attributed, timestamped, and
optimistic-concurrency-safe. Neither `superseded` nor `revoked` is authorized
in the current implementation.

## Proposed Assurance Levels

| Level | Meaning | Minimum requirement |
|---|---|---|
| `SDAS-0` | Unassessed | no envelope or incomplete identity |
| `SDAS-1` | Traceable certification | certified lifecycle, human decision, certification policy/timestamp, audit event, Certified Knowledge registration, and source/provenance reference |
| `SDAS-2` | Evidence-complete traceability | `SDAS-1` plus acquisition, source/artifact integrity, extraction/transformation, validation, and timestamp semantics evidenced end-to-end |
| `SDAS-3` | Reliance-eligible for a declared use | `SDAS-2` plus source authority assessment, freshness/currentness assessment for the declared use, supersession/revocation state, and durable consumption evidence |

No assurance level asserts legal reliance, financial coverage, or correctness
beyond its declared evidence. `SDAS-3` is only a proposed technical
eligibility term and requires a future governance decision.

## Semantics That Must Remain Separate

SDAS must distinguish certified, current, authoritative, and reliance-eligible
data as separate predicates; none is implied by another.

| Term | Meaning | Does not imply |
|---|---|---|
| Certified data | An approved record completed the controlled certification transition. | current, authoritative, complete, or reliance-eligible |
| Current data | Evidence is sufficiently recent for a declared use under an approved freshness rule. | certified or authoritative |
| Authoritative data | A designated owner/source class is evidenced for the stated scope. | current, certified, or error-free |
| Reliance-eligible data | All approved technical/governance requirements for a declared use are met. | insurance, legal guarantee, or unlimited reliance |

For the Maroon pilot, `current_status=insufficient_certified_evidence`
remains mandatory. Historical reporting-period observations cannot be promoted
to current or authoritative merely by SDAS assessment.

## Maroon Pilot Gap Assessment

The following is a portfolio-level assessment of the 49 currently indexed
Certified Knowledge items, based on verified implementation evidence. It is
not a per-record compliance finding.

| Dimension | Observed pilot coverage | Gap / SDAS result |
|---|---|---|
| Certified lifecycle, reviewer, policy, timestamp | verified for certified pilot records | supports `SDAS-1` component only |
| Append-only certification audit | verified audit-event linkage | audit hash-chain is absent |
| Certified Knowledge registration | deterministic/idempotent projection and source/audit provenance verified | registration timestamp/version/fingerprint are not a full SDAS envelope |
| Source/provenance | source identifiers, runtime-local references, reporting-period and location provenance vary by batch | no normalized source-identity/owner evidence for every record |
| Acquisition | bounded read-only access and local discovery/extraction were documented for selected corpora | no durable normalized acquisition event for every Certified Knowledge item |
| Timestamp semantics | reporting-period/source-attribution distinctions are preserved for reviewed batches | no universal normalized timestamp model or freshness policy |
| Integrity | record fingerprints and selected local fingerprints exist | no end-to-end source-artifact integrity chain for all 49 items |
| Transformation | deterministic extractors and some local provenance exist | no universal versioned transformation run/fingerprint chain |
| Validation | credibility gates and batch-specific checks exist | no versioned SDAS validation evidence bundle per record |
| Supersession/revocation | explicitly not implemented | missing; do not infer absence of supersession |
| Consumption/RAG | response provenance is returned; Qdrant and threshold invariants are verified | no durable append-only downstream consumption event |
| Authority/currentness | no overall authoritative recent project-status source is verified | missing; currentness remains insufficient |

Conclusion: the pilot shows a strong controlled-certification path and can be
used as SDAS test input, but no portfolio-wide `SDAS-1`, `SDAS-2`, or
`SDAS-3` conformance claim is justified today.

## Downstream Consumption Evidence Requirement

Every future retrieval/generation/automation/reporting use that claims SDAS
traceability must append an append-only consumption event after the operation,
containing:

- immutable `consumption_event_id` and UTC timestamp;
- authenticated service or actor identifier and declared purpose/use class;
- consumed `knowledge_id` set and a deterministic `provenance_set_fingerprint`;
- retrieval collection/version, policy version, threshold, query-input
  fingerprint or approved redacted equivalent, and result/outcome class;
- answer/output fingerprint, not raw organizational answer text by default;
- linkage to the originating certification/audit/assurance-envelope version;
- an append-only event hash and prior-event hash, with no secret, raw query,
  or raw organizational content in versioned evidence.

Failed/no-evidence consumption attempts should be recorded only when an
approved operational policy requires them; they must never be converted into
evidence that a project condition is true.

## Recommended Additive Implementation Sequence

1. Approve or revise this model, its terminology, target assurance level, and
   governance owner; decide whether `reliance-eligible` is in scope at all.
2. Add an isolated, additive `assurance_envelopes` and append-only
   `assurance_events` schema with no mutation of existing certification state.
3. Implement a read-only backfill assessor for the 49 pilot records that
   records only observed evidence and marks gaps explicitly.
4. Add source-acquisition, identity, timestamp, integrity, transformation,
   and validation adapters for new records; do not fabricate legacy evidence.
5. Add governed supersession/revocation proposals with explicit policy,
   actor, reason, immutable event history, and rollback-safe migration review.
6. Add an append-only consumption-evidence service to the private RAG path,
   then verify that retrieval provenance and consumption events reconcile.
7. Define approved authority and freshness policies before any `SDAS-3` or
   current-status claim is permitted.

## Decision Gate

ST1-054 accepted the limited v0.1 pilot. ST1-055 implemented an additive,
append-only assurance envelope and consumption evidence path, then
back-assessed all 49 Certified Knowledge items. The resulting distribution is
49 `SDAS-1` / `assessed_partial`; none is `SDAS-2`, `SDAS-3`, authoritative,
current, or reliance-eligible. See
`evidence/sanitized/2026-08-10-st1-055-sdas-v0-1-pilot.json`.

SDAS v0.2 still requires an architecture/governance decision before
supersession/revocation transitions, reliance eligibility, external rollout,
or any change to the existing certification/currentness semantics.

## SDAS v0.2 Recommendations

1. Select only one governed next scope: supersession/revocation, or an
   authority/freshness assessment model. Do not combine them with reliance
   eligibility in one migration.
2. Define a retention and privacy policy for consumption-event hashes and
   consumer identifiers before broadening RAG/automation logging.
3. Add source acquisition and transformation evidence adapters for new
   records first; never manufacture this chain for historical records.
4. Require an independently approved authority and freshness policy before
   considering any `SDAS-3` or reliance-eligibility predicate.
