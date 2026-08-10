# ST1-067 Governance Delegation Decision Template

This template is a decision request, not an authority assertion. Completing
it authorizes neither certification nor a currentness claim.

## Decision Required

An accountable Enterprise AI governance owner must explicitly provide every
field below for the proposed reusable LOW-risk route:

- Organization and accountable governance authority (stable, non-secret identifier).
- Delegated operating role: Project Controls / PMO, or a named equivalent.
- Registered source-system identity and Maroon pilot project scope.
- Allowed document class: recurring Project Controls progress workbook.
- Permitted fact classes: source-attributed reporting period, Plan, Actual,
  progress, activity, milestone, and Project Controls issue observations.
- Prohibited fact classes: payment, delay entitlement, claims, financial
  liability, safety-critical facts, current executive status, and reliance/insurance facts.
- Required business-time evidence rule (for example, a named report-period
  field, document-control field, signature, or accountable attestation).
- Required document-control or integrity evidence.
- Effective-from date, optional expiry date, revocation authority, and policy
  version (`project-controls-progress-low-risk/v1`).

## Required Explicit Statement

The accountable governance authority must state that the named role is delegated
only for the stated source system, project, document class, fact classes, and
effective period. Missing, conflicting, revoked, expired, or out-of-scope
evidence must remain `human_required` or `reject_or_quarantine`.

## Non-Effects

This delegation does not certify a record, establish source authority beyond
its exact scope, establish that a report is current, make a claim
reliance-eligible, or permit automatic certification. Any real record routed
to `policy_automatic` still requires the controlled certification lifecycle
before entering Certified Knowledge.
