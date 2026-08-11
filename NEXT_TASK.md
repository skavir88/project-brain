# Next Task

## Metadata
- Task ID: ST1-135
- Stage: Stage 1 — Product Implementation
- Status: Waiting for Two Real Selected-Series Artifacts
- Owner: Codex / Enterprise AI Project Operator

## Objective
Use the ST1-134 request pack to obtain the exact two real selected-series
artifacts still required on the ST1-066 critical path:

1. one real sanitized filled governance/report-definition bundle for
   `maroon_project_controls_progress_workbook_series`
2. one real sanitized native-record artifact for the same selected series

Then:

3. validate the real bundle with the deterministic selected-series bundle gate;
4. validate the real native-record artifact with the deterministic
   selected-series native-record gate;
5. validate the pair with the deterministic selected-series dual-input gate;
6. if both are exact-scope and ready, compile the independent controlled-review
   handoff only;
7. stop before any delegation activation, source registration, native
   acquisition, policy mutation, or certification.

## Rationale
As of Tuesday, August 11, 2026, the repository-local path is already fully
prepared:

- bundle-side exact-scope gate exists;
- native-record-side exact-scope gate exists;
- dual-input convergence gate exists;
- the Persian ST1-134 request pack narrows the real-world ask to exactly the
  two remaining artifacts;
- ST1-061 remains excluded as the first real success target.

The blocker is now only the arrival of those two real artifacts and their
controlled review.

## Preconditions
- The selected target remains the recurring Project Controls progress workbook
  series, not ST1-061.
- Both incoming artifacts must remain inside the approved Maroon pilot scope.
- Both incoming artifacts must be sanitized or otherwise safe for
  repository-local validation.
- No delegation activation, source registration, acquisition, policy mutation,
  or certification may occur in this task.

## Scope
- Use:
  - `docs/ST1_134_SELECTED_SERIES_REAL_INPUT_REQUEST_FA.md`
- Validate the real selected-series governance bundle with:
  - `scripts/validate_st1_078_real_evidence_bundle.py`
  - `scripts/assess_st1_078_real_evidence_bundle.py`
  - `scripts/verify_st1_124_recurring_workbook_governance_bundle.py`
  - `scripts/run_st1_125_series_bundle_gate.py`
- Validate the real selected-series native-record artifact with:
  - `scripts/verify_st1_083_first_native_record_preflight.py`
  - `scripts/verify_st1_131_selected_series_native_record.py`
- Validate the pair together with:
  - `scripts/run_st1_132_selected_series_dual_input_gate.py`
- If the pair is ready, compile:
  - `scripts/compile_st1_127_independent_verification_handoff.py`

## Out of Scope
- Using ST1-061 as the first real `policy_automatic` success target
- Real delegation activation
- Real source registration
- Real native acquisition
- Real policy decision mutation
- Real certification mutation
- Any new source boundary
- Any destructive change

## Files to Inspect
- `docs/ST1_134_SELECTED_SERIES_REAL_INPUT_REQUEST_FA.md`
- `evidence/sanitized/2026-08-11-st1-134-selected-series-real-input-request-pack.json`
- `evidence/sanitized/2026-08-11-st1-132-selected-series-dual-input-gate.json`
- `scripts/run_st1_125_series_bundle_gate.py`
- `scripts/verify_st1_131_selected_series_native_record.py`
- `scripts/run_st1_132_selected_series_dual_input_gate.py`
- `scripts/compile_st1_127_independent_verification_handoff.py`

## Files Allowed to Change
- sanitized evidence
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `MASTER_PLAN.md`
- `NEXT_TASK.md`

## Execution Steps
1. Use the ST1-134 request pack as the exact handoff for the selected series.
2. Receive one real sanitized filled bundle JSON for the selected recurring
   workbook series.
3. Receive one real sanitized native-record JSON for the same selected series.
4. Run the deterministic selected-series bundle gate.
5. Run the deterministic selected-series native-record gate.
6. Run the deterministic selected-series dual-input gate.
7. If both are scope-correct and ready, compile the independent-review handoff.
8. Stop before any activation, registration, acquisition, policy mutation, or
   certification.

## Acceptance Criteria
- The target remains the recurring workbook series and not ST1-061.
- The real filled bundle is classified truthfully with exact reason(s).
- The real native-record artifact is classified truthfully with exact reason(s).
- The real pair is classified truthfully with exact reason(s).
- If both are ready, the exact independent controlled-review checklist is produced.
- No historical/source authority is fabricated.
- No delegation is activated.
- No source is registered.
- No native acquisition occurs.
- No policy mutation occurs.
- No certification occurs.
- No trust boundary is weakened.

## Verification Commands
```powershell
python scripts/run_st1_125_series_bundle_gate.py --bundle <real-sanitized-filled-bundle.json>
python scripts/verify_st1_131_selected_series_native_record.py --native-record <real-sanitized-native-record.json>
python scripts/run_st1_132_selected_series_dual_input_gate.py --bundle <real-sanitized-filled-bundle.json> --native-record <real-sanitized-native-record.json>
python scripts/compile_st1_127_independent_verification_handoff.py --bundle <real-sanitized-filled-bundle.json>
git diff --check
```

## Evidence Required
- Sanitized evidence showing:
  - exact selected-series match or mismatch for the bundle;
  - exact selected-series match or mismatch for the native record;
  - exact pair convergence result;
  - structural and readiness outcomes;
  - exact missing or rejected fields if any;
  - exact independent-review checklist if eligible;
  - unchanged delegation/source-registration/acquisition/policy/certification boundaries.

## Rollback
- If either artifact is incomplete or rejected, no rollback is required.
- If an additive evidence write begins and fails, roll back only the in-flight
  write and do not mutate prior governance, ST1-061, or certification state.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `MASTER_PLAN.md`
- `NEXT_TASK.md`
