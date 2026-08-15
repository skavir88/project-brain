# Next Task

## Metadata
- Task ID: ST1-138
- Stage: Stage 1 — Product Implementation
- Status: BLOCKED_BY_EXTERNAL_EVIDENCE
- Owner: Codex / Enterprise AI Project Operator

## Objective
Receive the minimum remaining real selected-series governance/source-control
evidence required to re-run the exact ST1-136 gate chain for the already
matched representative workbook.

Required real inputs only:

1. exact-scope confirmation that the related Project Controls / PMO reporting
   ownership/control signals already observed in the Maroon pilot also apply to
   `maroon_project_controls_progress_workbook_series`
2. exact-scope controlled report-definition confirmation for the selected
   recurring workbook series
3. `stable_source_registration_evidence_reference`

Then:

4. merge/compile those real inputs onto the preserved A1 + pilot-series-id
   bundle;
5. reuse the existing partial real native-record artifact;
6. re-run ST1-125, ST1-131, and ST1-132;
7. if all gates become ready, compile the independent controlled-review
   handoff only;
8. stop before any delegation activation, source registration mutation,
   native acquisition mutation, policy mutation, or certification.

## Rationale
As of Tuesday, August 11, 2026:

- the pilot non-sensitive series identifier is no longer missing;
- the representative workbook is deterministically re-matched;
- a truthful partial real native-record artifact already exists;
- business-time evidence from the workbook header is already preserved;
- already-authorized adjacent PMO/project-controls evidence exists for a
  related Maroon reporting artifact;
- the remaining blocker is now narrower and exact-scope external confirmation:
  apply-or-do-not-apply confirmation for that reporting ownership/control
  evidence on the selected recurring workbook series, plus one stable
  source-registration evidence reference.

## Preconditions
- The target remains `maroon_project_controls_progress_workbook_series`.
- The representative workbook remains `070-TWRP-24 1402-12-05.xlsx`.
- The observed reporting-period example remains `1402/11/21–1402/12/05`.
- The existing A1 limited pilot-governance evidence must remain preserved with
  its explicit non-implication limits.
- The existing partial real native-record artifact must remain preserved:
  `evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json`
- No new source boundary, broad discovery, or inferred historical authority is
  allowed.

## Scope
- Accept only the exact missing real inputs for the selected series.
- Use the existing ST1-136 intake/gate machinery:
  - `scripts/compile_st1_136_remaining_inputs_from_individual_attestations.py`
  - `scripts/apply_st1_136_remaining_selected_series_inputs.py`
  - `scripts/verify_st1_136_remaining_inputs_supplement.py`
  - `scripts/run_st1_136_post_a1_submission_gate.py`
  - `scripts/run_st1_125_series_bundle_gate.py`
  - `scripts/verify_st1_131_selected_series_native_record.py`
  - `scripts/run_st1_132_selected_series_dual_input_gate.py`
- Reuse the already prepared evidence:
  - `evidence/sanitized/2026-08-11-st1-135-a1-pilot-governance-attestation.json`
  - `evidence/sanitized/2026-08-11-st1-136-selected-series-bundle.a1-plus-pilot-series-id.json`
  - `evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json`

## Out of Scope
- Inventing or inferring A2/A3 authority from workbook content alone
- Treating the pilot series identifier as an official organizational ID
- Any new SMB discovery or new source boundary
- Any runtime mutation before the gates truthfully allow controlled review
- Any certification or Certified Knowledge mutation

## Files to Inspect
- `evidence/sanitized/2026-08-11-st1-136-real-selected-series-reconciliation.json`
- `evidence/sanitized/2026-08-11-st1-136-real-selected-series-gate-results.json`
- `evidence/sanitized/2026-08-11-st1-136-selected-series-bundle.a1-plus-pilot-series-id.json`
- `evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json`
- `docs/ST1_136_SELECTED_SERIES_COMPLETION_PACK_FA.md`

## Files Allowed to Change
- sanitized evidence
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `MASTER_PLAN.md`
- `NEXT_TASK.md`

## Execution Steps
1. Receive one exact-scope confirmation from the accountable Project Controls /
   PMO side, or its controlled evidence equivalent, that the selected recurring
   workbook series is governed by the same reporting ownership/control process
   evidenced in the related authorized Maroon reporting artifact.
2. Receive one exact-scope controlled report-definition confirmation for the
   same selected recurring workbook series that establishes the still-unresolved
   ownership/control applicability beyond the workbook-header observation.
3. Receive one real stable source-registration evidence reference for that same
   selected series.
4. Compile or merge those exact inputs onto the preserved A1 + pilot-series-id
   bundle.
5. Re-run the deterministic selected-series bundle gate.
6. Re-run the deterministic selected-series native-record gate against the
   preserved partial real native-record artifact.
7. Re-run the deterministic dual-input gate.
8. If the pair becomes ready, compile the independent controlled-review
   handoff only.

## Acceptance Criteria
- Only the narrowed exact-scope external confirmations plus the stable
  source-registration reference are added.
- No historical/source authority is fabricated.
- The selected-series scope remains exact.
- The native-record artifact is reused rather than rediscovered.
- The gates return a truthful outcome with exact blocker reasons if still not
  ready.
- If controlled review becomes ready, the exact handoff is produced and no
  runtime mutation beyond that occurs.

## Verification Commands
```powershell
python scripts/run_st1_125_series_bundle_gate.py --bundle <updated-real-selected-series-bundle.json>
python scripts/verify_st1_131_selected_series_native_record.py --native-record evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json
python scripts/run_st1_132_selected_series_dual_input_gate.py --bundle <updated-real-selected-series-bundle.json> --native-record evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json
git diff --check
```

## Evidence Required
- Sanitized evidence showing:
  - exact A2/A3/source-registration inputs received;
  - exact bundle readiness after merge;
  - exact native-record readiness after re-check;
  - exact dual-input convergence result;
  - unchanged non-activation / non-certification boundaries.

## Rollback
- If the new external evidence is incomplete or rejected, keep the current
  partial artifacts unchanged and record the exact missing/invalid fields.
- No destructive rollback is authorized or required.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `MASTER_PLAN.md`
- `NEXT_TASK.md`
