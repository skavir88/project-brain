# Next Task

## Metadata
- Task ID: ST1-141
- Stage: Stage 1 — Product Implementation
- Status: WAITING_FOR_GOVERNANCE_OWNER_DECISION
- Owner: Codex / Enterprise AI Project Operator

## Objective
Receive exactly one bounded prospective governance-owner decision for future
reports of `maroon_project_controls_progress_workbook_series`, using the
single proposal prepared in:

`docs/ST1_139_PROSPECTIVE_SELECTED_SERIES_GOVERNANCE_PROPOSAL_FA.md`

and, if helpful for exact corrections, the machine-readable shape at:

`docs/examples/ST1_140_selected_series_prospective_decision.template.json`

or the already prefilled decision stub at:

`docs/examples/ST1_141_selected_series_prospective_decision.proposed.real.json`

The decision should either:

1. approve the package as proposed; or
2. approve it with explicit corrections.

The package is prospective only and covers:

- proposed accountable role class for future selected-series reports;
- proposed controlled report-definition rule for future selected-series reports;
- continued pilot use of
  `maroon_project_controls_progress_workbook_series` as
  `pilot_non_sensitive_series_identifier`;
- source-registration rule for the same selected series;
- explicit effective boundary `2026-08-15`;
- allowed LOW-risk facts and prohibited HIGH-risk facts.

If the decision arrives with sufficient exact values:

3. translate it into the existing A2/A3/source-registration artifacts using the
   current ST1-140 / ST1-136 / ST1-124 machinery;
4. re-run ST1-125, ST1-131, and ST1-132 truthfully;
5. prepare the first post-bootstrap native-record intake using:
   `docs/examples/ST1_140_first_post_bootstrap_native_record.template.json`
6. stop before activation, runtime mutation, or certification.

## Rationale
As of Saturday, August 15, 2026:

- the historical representative workbook remains preserved and unchanged;
- the pilot owner has now made a real prospective governance decision for the
  selected series;
- the existing governance/attestation machinery is sufficient for the
  prospective path and does not require another framework;
- one approved prospective decision can now be translated directly into the
  existing selected-series gates;
- both allowed response modes for that decision are now technically verified;
- the preserved historical native record is now proven **not** to be the first
  post-bootstrap record for the future path;
- the next smallest truthful business gate is no longer historical A2/A3
  proof. It is one bounded future-facing decision package for selected-series
  governance from `2026-08-15` onward, followed by one first post-bootstrap
  native record.

## Preconditions
- The target remains `maroon_project_controls_progress_workbook_series`.
- The representative workbook remains `070-TWRP-24 1402-12-05.xlsx`.
- The observed reporting-period example remains `1402/11/21–1402/12/05`.
- The historical representative workbook and its native evidence must remain
  unchanged.
- The ST1-139 prospective governance-owner decision must remain prospective
  only with boundary `2026-08-15`.
- The existing partial real native-record artifact must remain preserved:
  `evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json`
- No historical authority/accountability may be backfilled from the new
  governance decision.

## Scope
- Accept only one bounded prospective governance-owner decision for future
  selected-series reports.
- Reuse the already prepared machinery and artifacts:
  - `docs/ST1_139_PROSPECTIVE_SELECTED_SERIES_GOVERNANCE_PROPOSAL_FA.md`
  - `docs/examples/ST1_140_selected_series_prospective_decision.template.json`
  - `docs/examples/ST1_141_selected_series_prospective_decision.proposed.real.json`
  - `docs/ST1_141_GOVERNANCE_OWNER_DECISION_RESPONSE_FA.md`
  - `evidence/sanitized/2026-08-15-st1-139-a1-pilot-governance-owner-selected-series.json`
  - `evidence/sanitized/2026-08-15-st1-139-selected-series-bundle.prospective-owner.partial.json`
  - `scripts/compile_st1_140_selected_series_prospective_decision.py`
  - `scripts/compile_st1_136_remaining_inputs_from_individual_attestations.py`
  - `scripts/run_st1_125_series_bundle_gate.py`
  - `scripts/verify_st1_131_selected_series_native_record.py`
  - `scripts/run_st1_132_selected_series_dual_input_gate.py`
  - `docs/examples/ST1_140_first_post_bootstrap_native_record.template.json`

## Out of Scope
- Proving historical A2/A3 from the 1402 workbook
- Backfilling historical PMO / Project Controls / source authority
- Treating the pilot series identifier as an official historical
  document-control identifier
- Any activation, source registration mutation, native acquisition mutation,
  or certification
- Any new SMB discovery or new source boundary

## Files to Inspect
- `evidence/sanitized/2026-08-15-st1-139-a1-pilot-governance-owner-selected-series.json`
- `evidence/sanitized/2026-08-15-st1-139-selected-series-bundle.prospective-owner.partial.json`
- `evidence/sanitized/2026-08-15-st1-139-prospective-governance-bootstrap.json`
- `evidence/sanitized/2026-08-15-st1-139-prospective-bundle-gate.json`
- `evidence/sanitized/2026-08-15-st1-140-prospective-decision-bridge.json`
- `evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json`
- `docs/ST1_139_PROSPECTIVE_SELECTED_SERIES_GOVERNANCE_PROPOSAL_FA.md`
- `docs/examples/ST1_140_selected_series_prospective_decision.template.json`
- `docs/examples/ST1_141_selected_series_prospective_decision.proposed.real.json`
- `docs/examples/ST1_140_first_post_bootstrap_native_record.template.json`
- `docs/ST1_140_FIRST_POST_BOOTSTRAP_NATIVE_RECORD_CONTRACT.md`
- `docs/ST1_141_GOVERNANCE_OWNER_DECISION_RESPONSE_FA.md`

## Files Allowed to Change
- sanitized evidence
- `docs/ST1_139_PROSPECTIVE_SELECTED_SERIES_GOVERNANCE_PROPOSAL_FA.md`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `MASTER_PLAN.md`
- `NEXT_TASK.md`

## Execution Steps
1. Receive one explicit decision on the bounded ST1-139 proposal:
   approve as proposed, or approve with exact corrections.
2. If approved/corrected, compile the exact A2/A3/source-registration artifacts
   for the prospective selected-series path only.
3. Re-run the deterministic selected-series bundle gate.
4. Prepare one first post-bootstrap native record using the class-level ST1-140
   native-record contract.
5. Re-run the truthful class-level and selected-series gates as applicable.
6. If the future-facing pair becomes ready, compile the independent controlled-
   review handoff only and stop before any activation or runtime mutation.

## Acceptance Criteria
- Only one bounded prospective governance-owner decision is requested.
- No historical/source authority is fabricated or backfilled.
- The selected-series scope remains exact.
- The historical native-record artifact remains preserved but is not misused as
  the first post-bootstrap record.
- The gates return a truthful outcome with exact blocker reasons if still not
  ready.
- If controlled review becomes ready, the exact handoff is produced and no
  runtime mutation beyond that occurs.

## Verification Commands
```powershell
python scripts/run_st1_125_series_bundle_gate.py --bundle <updated-prospective-selected-series-bundle.json>
python scripts/verify_st1_131_selected_series_native_record.py --native-record evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json
python scripts/run_st1_132_selected_series_dual_input_gate.py --bundle <updated-prospective-selected-series-bundle.json> --native-record evidence/sanitized/2026-08-11-st1-136-selected-series-native-record.partial.real.json
git diff --check
```

## Evidence Required
- Sanitized evidence showing:
  - the exact governance-owner decision received;
  - the exact future-facing A2/A3/source-registration inputs approved or
    corrected;
  - exact bundle readiness after merge;
  - exact first post-bootstrap native-record readiness after re-check;
  - exact dual-input convergence result;
  - unchanged non-activation / non-certification boundaries.

## Rollback
- If the prospective decision is incomplete or rejected, keep the current
  ST1-139 partial artifacts unchanged and record the exact missing/invalid
  fields.
- No destructive rollback is authorized or required.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `MASTER_PLAN.md`
- `NEXT_TASK.md`
