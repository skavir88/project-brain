# ST1-076 Candidate-Specific Governance and Source Bundle

This bundle converts the selected ST1-075 candidate class into one exact,
reusable scope for future real SDAS v0.3 activation work. It does not create
or activate any real delegation.

## Fixed scope

- Project scope: Maroon pilot
- Candidate class: recurring Project Controls progress workbook
- Current representative runtime source family:
  `enterprise_ai_real_action_plan_weekly_observation`
- Risk tier: `LOW`
- Automatic certification: `false`
- Currentness / reliance / insurance enablement: `not allowed`

## Fixed permitted fact classes

- reporting period
- reported Plan
- reported Actual
- reported progress metric
- reported activity status
- reported milestone status
- reported Project Controls issue/constraint observation

## Fixed prohibited fact classes

- contractual delay determination
- entitlement / claims
- payment authorization or payment status
- financial liability
- legal conclusion
- safety/compliance certification
- final completion
- current executive status outside the stated reporting period
- reliance eligibility
- insurance / guarantee semantics

## Fixed business-time rule

Business/reporting time for this class must come only from:

- the workbook-labelled reporting-week header; or
- a designated reporting-period field in the workbook/report class.

These are not valid substitutes:

- row-level planned dates
- row-level target dates
- filesystem timestamps
- acquisition timestamps

## Required real inputs before native automatic routing

### A1 — Governance authority confirmation

Need a real controlled record or signed attestation proving which
organizational governance role may approve this pilot scope.

Still required:

- signer identity
- signer role
- authority basis
- effective period

### A2 — Project Controls / PMO accountability confirmation

Need a real controlled record or signed attestation proving which
organizational role owns recurring Project Controls reporting for this class.

Still required:

- accountable role identity
- project scope match
- recurring report-class responsibility

### A3 — Controlled report definition confirmation

Need a real controlled record or signed attestation proving all of the
following for this exact workbook class:

- source/report class name
- owning organizational role
- non-sensitive source/location class
- deterministic reporting-period field/header convention
- document/version convention
- release/approval convention if applicable

## Required source-registration inputs

The runtime still needs one real registered source/system for this class.
Required inputs:

- stable source/system identity
- source type for this workbook class
- non-sensitive system/location identity
- owning accountable role
- exact project scope

## Required native-ingestion controls after evidence exists

Only after the governance/source bundle is truly evidenced:

1. register the real source/system;
2. acquire one real workbook read-only;
3. capture original SHA-256 and acquisition metadata;
4. capture deterministic transformation lineage;
5. resolve business time only from the approved workbook rule;
6. evaluate exact-scope policy routing.

## Hard-stop rule

Even if one real record reaches `policy_automatic`, it still does **not** mean:

- human approved
- certified
- current
- reliance eligible
- insured

Certification remains a separate hard stop requiring explicit approval.

## Plain-language business request

When real-world evidence is requested, the minimum business ask should be:

1. Who in the organization is allowed to approve this pilot governance scope?
2. Which Project Controls / PMO role is officially responsible for this
   recurring progress workbook/report class?
3. For this workbook/report class, where is the official reporting period
   defined and what is the approved release/control convention?

Do not ask the business to fill technical SDAS fields directly; ask for the
real controlled document or signed confirmation that answers those three
questions.
