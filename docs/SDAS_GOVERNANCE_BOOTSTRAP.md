# SDAS Governance Bootstrap

## Purpose

ST1-067 separates approval of the SDAS pilot policy model from verification of
real organizational identities and operational data authority. A policy can be
`approved_for_pilot` while every real record remains `human_required`.

## Append-Only Lifecycle

```text
PROPOSED
  -> GOVERNANCE_APPROVED
  -> IDENTITY_VERIFIED
  -> SOURCE_VERIFIED
  -> ACTIVE

Terminal: REVOKED | SUPERSEDED | EXPIRED | REJECTED
```

Only the `ingestion.sdas_active_delegation_bootstrap` view represents usable
authority. The database guard rejects an `ACTIVE` transition unless the exact
preceding state is `SOURCE_VERIFIED`; it also rejects any transition after a
terminal event. Policy revocation/supersession excludes an otherwise active
proposal from the usable-authority view.

`GOVERNANCE_APPROVED` for this pilot is policy-model approval only. It carries
no governance actor, accountable actor, or source ID, and therefore cannot
confer operational authority.

## Identity Verification Requirements

| Identity | Minimum reusable evidence | Must establish | Does not establish |
|---|---|---|---|
| Governance approver | Approved role mapping, internal directory identity, or signed governance attestation | A durable governance role identity and its policy-approval scope | Operational approval of individual records |
| Project Controls / PMO accountable role | Approved role mapping, document-control responsibility, or signed role attestation | The accountable operating role for this report class/project | CEO identity or source authority |
| Source/system owner | Source-system ownership record plus accountable role evidence | Ownership/control of the registered recurring reporting source | Authority of every file in a folder |

Role-based identity is sufficient; no named person is required. Native or
corroborated identity evidence is required for the `IDENTITY_VERIFIED`
transition. No identity is inferred from a title, filesystem path, or local
account.

## Source Verification Requirements

A recurring Project Controls source may reach `SOURCE_VERIFIED` only when a
registered source record has a verified authority status and its authority
scope explicitly matches the proposed project scope. The minimum evidence is:

- stable registered source/system identity;
- source-system ownership evidence tied to the accountable role;
- recurring report/status document-class definition;
- accepted document-control/approval convention;
- business/report-period convention from approved header, registered field,
  document-control evidence, or accountable-owner attestation.

Filesystem location and acquisition timestamp are never source-authority or
business-time evidence.

## Automation Safety

Until a proposal is `ACTIVE`, all matching real records remain
`human_required` (or `reject_or_quarantine` when integrity or validation
fails). `ACTIVE` supports only exact LOW-risk policy matching; it does not
certify, establish currentness, enable reliance, or allow insurance/guarantee
semantics.

ST1-061 remains an unchanged regression case: no authority assertion and no
business-time evidence exists, so it remains `human_required`.

## Deterministic Governance-Resolution Queue

| Requirement | Status | Evidence required | Responsible role | Blocking effect | Reuse scope |
|---|---|---|---|---|---|
| Governance approver identity | `required` | Durable CEO/governance-role mapping or signed governance attestation | CEO / governance office | Blocks `IDENTITY_VERIFIED` | All pilot delegations |
| Accountable Project Controls role | `required` | Role mapping or document-control responsibility evidence | PMO / Project Controls governance owner | Blocks `IDENTITY_VERIFIED` | Maroon recurring Project Controls reports |
| Source/system ownership | `required` | Registered source identity plus ownership evidence | Source-system owner / Project Controls | Blocks `SOURCE_VERIFIED` | Same registered source/system |
| Recurring report-class definition | `required` | Approved class/structure and permitted LOW-risk fields | Project Controls / PMO | Blocks exact policy matching | Matching recurring reports |
| Business-time convention | `required` | Approved header/period field/document-control rule or role attestation | Project Controls / PMO | Blocks policy automation | Matching recurring reports |
| Activation decision | `required` | Append-only activation event after all prior requirements validate | Governance authority | Blocks `ACTIVE` | Exact policy/source/project scope |

The queue is reusable: it shifts review from each routine LOW-risk fact to a
small governance decision set about roles, sources, and policy boundaries.

## ST1-068 Conditional Activation Evidence

The governance structure is approved conditionally for the Maroon pilot, LOW
risk only. To make the model deterministic and reusable, activation now
requires two append-only evidence types in addition to native record lineage:

- **Role identity verification:** ties a durable governance role or Project
  Controls/PMO role to an actor-registry entry, project scope, effective period,
  and non-secret evidence reference. It does not require a person's name.
- **Source-control verification:** ties one registered source to the verified
  accountable role, exact project scope, one approved recurring report class,
  and one allowed reporting-time convention.

The database guard rejects `IDENTITY_VERIFIED` without both reusable role
verifications, and rejects `SOURCE_VERIFIED` unless the source has verified
authority, matching project scope, matching report class, and reusable
reporting-time/control evidence. The exception queue returns only `PASS`,
`HUMAN_REQUIRED`, or `QUARANTINE`; it is not a per-record governance-review
list.

## ST1-070 Controlled Attestation Evidence Hierarchy

Tier A is an existing controlled organizational artifact: approved organization
chart, delegation, governance charter, Project Execution Plan, Project Controls
procedure, RACI, document-control procedure, or controlled report definition.
Tier B is a narrowly scoped, signed accountable attestation only when Tier A is
unavailable. Tier B does not infer missing Tier A evidence and it never grants
retroactive authority outside its explicit effective period.

Three independent attestation kinds are supported: governance authority,
Project Controls/PMO accountability, and controlled recurring-report
definition. A signed artifact is stored as a fingerprint/reference with
acquisition provenance, scope, version, effective period, signer and an
append-only lifecycle:

```text
SUBMITTED -> IDENTITY_VERIFIED -> VERIFIED
                                 -> REVOKED | SUPERSEDED
SUBMITTED | IDENTITY_VERIFIED -> REJECTED
```

The signer must already have independently evidenced identity before an
attestation can become `VERIFIED`. A self-asserted or declared-only identity
cannot pass that gate. Corrections use a new attestation plus `SUPERSEDED`;
there is no update/delete path. A verified attestation is reusable only for
its exact project, role, report class, effective period, and permitted facts.
It is evidence for a later activation-readiness calculation, not a real active
delegation, automatic certification, currentness, reliance, or insurance.

For the existing E3 `PARTIAL` signal, the minimum Tier-B artifact is the
Controlled Report Definition Attestation. It must identify the recurring report
class, owning role, non-sensitive source-location class, deterministic
reporting-period header/field/convention, document identifier/version rule,
release convention where applicable, allowed LOW-risk facts, prohibited
inferences, scope, effective period, and approval method. The report-period
rule remains business-time evidence; filesystem and acquisition times cannot
substitute for it.
