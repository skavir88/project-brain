# ST1-078 Real Evidence Intake Spec

This spec defines the minimum machine-checkable intake bundle for the selected
real candidate class from ST1-075/ST1-076:

- Project scope: `maroon_pilot`
- Candidate class: `project_controls_progress_workbook`
- Risk tier: `LOW`

This intake bundle does **not** activate a real delegation, create authority,
certify a record, assert currentness, or enable reliance.

## Purpose

When the organization later supplies real controlled evidence for A1, A2, A3,
and the exact source-registration inputs, ST1-078 should be able to validate
that bundle deterministically before any runtime registration or native
acquisition attempt.

The validator is local-only and non-destructive. It verifies bundle structure,
exact candidate-class scope, required fields, fact-class boundaries, and the
reporting-time rule.

## Required bundle sections

### 1. Top-level bundle metadata

- `bundle_version`
- `candidate_class_id`
- `project_scope`
- `activation_request`
- `automatic_certification_requested`
- `currentness_override_requested`
- `reliance_override_requested`
- `evidence_items`
- `source_registration`

The four boolean request flags must all remain `false`.

### 2. Evidence items

The bundle must contain exactly these three evidence items:

- `A1`
- `A2`
- `A3`

Each one must include:

- `tier`
- `status`
- `attestation_kind`
- `subject_role_class`
- `asserted_scope`
- `effective_from`
- `signed_artifact_reference`
- `signed_artifact_fingerprint`
- `acquisition_provenance`
- `payload`

Expected attestation kinds:

- `A1 -> governance_authority`
- `A2 -> project_controls_accountability`
- `A3 -> controlled_report_definition`

### 3. A1 payload

The A1 payload must include:

- `governance_role_class`
- `authority_basis`
- `scope`
- `expiry_or_revocation_rule`
- `approval_method`

### 4. A2 payload

The A2 payload must include:

- `accountable_role_class`
- `report_classes`
- `permitted_fact_classes`
- `prohibited_fact_classes`
- `scope`
- `approval_method`

### 5. A3 payload

The A3 payload must include:

- `source_report_class`
- `owning_role_class`
- `source_location_class`
- `reporting_period_rule`
- `document_identifier_convention`
- `permitted_fact_classes`
- `prohibited_inference`
- `scope`
- `approval_method`

The reporting-period rule must allow only:

- `workbook_labelled_reporting_week_header`
- `designated_reporting_period_field`

And must explicitly disallow:

- `row_level_planned_date`
- `row_level_target_date`
- `filesystem_timestamp`
- `acquisition_timestamp`

### 6. Source registration block

The source-registration block must include:

- `source_id`
- `source_type`
- `non_sensitive_location_class`
- `owning_role_class`
- `project_scope`
- `report_class`
- `authority_state`
- `evidence_reference`

The validator only confirms structural readiness. It does not prove the source
owner or signer identity.

## Deterministic result classes

The local validator distinguishes only:

- `STRUCTURALLY_COMPLETE_PENDING_INDEPENDENT_VERIFICATION`
- `STRUCTURALLY_INCOMPLETE`

Even a structurally complete bundle still requires:

- signer identity verification,
- controlled artifact review,
- scope match verification,
- source ownership/control verification,
- reporting-time evidence verification,
- activation-readiness calculation,
- and the existing hard stop before any first real `policy_automatic`
  certification step.

## Verification commands

```powershell
python scripts/validate_st1_078_real_evidence_bundle.py --bundle docs/examples/ST1_078_real_evidence_bundle.synthetic.valid.json
python scripts/validate_st1_078_real_evidence_bundle.py --bundle docs/examples/ST1_078_real_evidence_bundle.synthetic.invalid.json
python scripts/assess_st1_078_real_evidence_bundle.py --bundle docs/examples/ST1_078_real_evidence_bundle.synthetic.valid.json
python scripts/assess_st1_078_real_evidence_bundle.py --bundle docs/examples/ST1_078_real_evidence_bundle.template.json
```

Expected outcomes:

- the valid synthetic bundle passes;
- the invalid synthetic bundle fails with explicit reason(s).
- the valid synthetic bundle assesses to
  `PENDING_INDEPENDENT_VERIFICATION`;
- the template bundle assesses to `WAITING_FOR_EXTERNAL_EVIDENCE`.

## Readiness assessment

`scripts/assess_st1_078_real_evidence_bundle.py` sits above the structural
validator. It does not verify identity or activate authority. Instead, it
classifies:

- `bundle`
- `A1`
- `A2`
- `A3`
- `source_registration`

into:

- `MISSING`
- `PARTIAL`
- `REJECTED`

and returns an overall readiness state:

- `WAITING_FOR_EXTERNAL_EVIDENCE`
- `WAITING_FOR_SCOPE_OR_POLICY_CORRECTION`
- `PENDING_INDEPENDENT_VERIFICATION`

The assessor never returns `VERIFIED`. That state requires independent
controlled evidence review outside the local-only boundary.

## Boundary

Real signed artifacts, source-system identifiers, and any non-sanitized
evidence should remain outside Git until manually reviewed and sanitized under
the established Project Brain policy.
