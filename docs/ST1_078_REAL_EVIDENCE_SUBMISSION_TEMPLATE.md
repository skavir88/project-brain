# ST1-078 Real Evidence Submission Template

Use this template only for the exact selected class:

- Project: `maroon_pilot`
- Candidate class: `project_controls_progress_workbook`

Template file:

- `docs/examples/ST1_078_real_evidence_bundle.template.json`

## How to use it

1. Copy the template JSON outside Git.
2. Replace each `REQUIRED_INPUT` value only with controlled evidence or a
   signed accountable attestation reference.
3. Do not invent signer identity, governance role, accountable role, source
   ownership, reporting-period rule, or document-control convention.
4. Keep these fields unchanged:
   - `candidate_class_id`
   - `project_scope`
   - `report_classes`
   - permitted fact classes
   - prohibited fact classes
   - accepted reporting-period sources
   - disallowed reporting-period substitutes
5. Keep all four request flags `false`:
   - `activation_request`
   - `automatic_certification_requested`
   - `currentness_override_requested`
   - `reliance_override_requested`

## Before validation

The template itself is not expected to pass the validator. It is only a
structured submission form.

Validation should run only after:

- all `REQUIRED_INPUT` placeholders are replaced;
- fingerprints are real lowercase SHA-256 hex values;
- the supplied evidence is sanitized for repository policy if it is copied into
  a tracked location.

## Validation command

```powershell
python scripts/validate_st1_078_real_evidence_bundle.py --bundle <path-to-filled-bundle.json>
python scripts/assess_st1_078_real_evidence_bundle.py --bundle <path-to-filled-bundle.json>
```

## Expected meaning of a pass

A validator pass means only:

- the evidence bundle is structurally complete for ST1-078 intake; and
- the bundle stays inside the approved candidate-class boundaries.

It does **not** mean:

- signer identity is verified;
- authority is active;
- source ownership/control is proven;
- reporting time is accepted as true;
- any real record may yet be certified;
- any real record is current or reliance-eligible.

## Expected meaning of the assessor

The assessor is more explicit than the validator:

- `MISSING` means the bundle still contains `REQUIRED_INPUT` placeholders or
  whole sections are absent;
- `REJECTED` means the supplied bundle crosses class/policy boundaries or
  violates required structure;
- `PARTIAL` means the supplied bundle is structurally acceptable but still
  awaits independent verification of signer identity, source ownership/control,
  and controlled-evidence truth.
