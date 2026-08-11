# Next Task

## Metadata
- Task ID: ST1-078
- Stage: Stage 1 — Product Implementation
- Status: Waiting for external evidence
- Owner: Governance authority, Project Controls / PMO, and controlled report owner

## Objective
Validate and register only the real controlled organizational evidence supplied
for the selected recurring Project Controls progress workbook class:
A1 governance authority, A2 Project Controls accountability, A3 controlled
report definition, and the exact source-registration inputs for that class.

## Rationale
ST1-075 selected the exact real candidate class, ST1-076 froze its scope, and
ST1-077 converted the evidence ask into a class-specific Persian business pack.
The next step is no longer discovery or design; it is validating real supplied
evidence for this exact class.

## Preconditions
- One or more signed business artifacts or stronger Tier-A controlled records
  answering `docs/ST1_077_PROJECT_CONTROLS_PROGRESS_EVIDENCE_REQUEST_FA.md`
  are supplied through an approved business channel.
- Each signer can be independently identified through controlled evidence.

## Scope
- Inspect only supplied controlled evidence for the selected workbook class.
- Validate provenance, signer identity, scope match, reporting-time rule, and
  source-registration inputs.
- Append only sanitized references/fingerprints and update readiness.

## Out of Scope
- New SMB discovery
- New source boundary
- Real delegation activation
- Real certification
- Any change to ST1-061

## Files to Inspect
- `docs/ST1_075_REAL_POLICY_AUTOMATIC_CANDIDATE.md`
- `docs/ST1_076_PROJECT_CONTROLS_PROGRESS_WORKBOOK_BUNDLE.md`
- `docs/ST1_077_PROJECT_CONTROLS_PROGRESS_EVIDENCE_REQUEST_FA.md`
- `docs/ST1_078_REAL_EVIDENCE_INTAKE_SPEC.md`
- `docs/ST1_078_REAL_EVIDENCE_SUBMISSION_TEMPLATE.md`
- `docs/examples/ST1_078_real_evidence_bundle.template.json`
- `scripts/assess_st1_078_real_evidence_bundle.py`
- `scripts/validate_st1_078_real_evidence_bundle.py`
- Supplied business artifacts only

## Files Allowed to Change
- Sanitized evidence
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md`, only if a new decision is required
- `NEXT_TASK.md`

## Execution Steps
1. Verify each supplied artifact against the selected workbook-class scope.
2. Confirm signer identity independently.
3. Determine whether A1, A2, A3, and source-registration inputs are
   `VERIFIED`, `PARTIAL`, `REJECTED`, or still `MISSING`.
4. Update activation/native-ingestion readiness without activating anything.
5. Record sanitized evidence and update Project Brain.

## Acceptance Criteria
- No artifact passes on self-assertion alone.
- The selected workbook class either has verified real organizational inputs
  or an exact remaining gap, with no inference.
- No real delegation is activated and no real certification occurs.

## Verification Commands
```powershell
python scripts/validate_st1_078_real_evidence_bundle.py --bundle <path-to-supplied-bundle.json>
python scripts/assess_st1_078_real_evidence_bundle.py --bundle <path-to-supplied-bundle.json>
git diff --check
```

## Evidence Required
- Sanitized fingerprint/reference, asserted role/source/time fact, scope,
  effective period, verification method, provenance, and status.

## Rollback
- Append `REJECTED`, `REVOKED`, `SUPERSEDED`, or a new corrective event; never
  overwrite or delete evidence.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md`, only if a new decision is required
- `NEXT_TASK.md`
