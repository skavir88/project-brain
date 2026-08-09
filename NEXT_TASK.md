# Next Task

## Metadata
- Task ID: ST1-023
- Stage: Stage 1 — Product Implementation
- Status: Ready — Human Review required
- Owner: Designated business reviewer

## Objective
Obtain one explicit Human Review disposition for each of the 12 local-only, internally dated ST1-022 status candidates. Do not certify any candidate in this task.

## Rationale
The selected source provides a dated activity snapshot and row-level provenance, but it does not itself prove authority, currentness beyond the extracted period, completeness, or executive-status semantics. Human review is therefore required before any real claim can approach the certification boundary.

## Preconditions
- `%LOCALAPPDATA%\EnterpriseAI\runtime\st1-022-human-review-package.json` exists and contains exactly 12 candidates.
- `evidence/sanitized/2026-08-09-st1-022-dated-status-source-review.json` validates.
- Candidate excerpts and locators remain local-only.

## Scope
- Display every candidate locally with its reporting period, project/source reference, workbook/sheet/row/cell provenance, minimal supporting excerpt, uncertainty, and permitted disposition.
- Record only explicit `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT` decisions in local runtime audit state.
- Produce a sanitized aggregate decision summary.

## Out of Scope
- Certification, automatic approval, source modification, corpus expansion, broad SMB traversal, platform persistence, Qdrant/Dify/external-model use, remote-host changes, credentials, public exposure, and destructive operations.

## Files to Inspect
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-09-st1-022-dated-status-source-selection.json`
- `evidence/sanitized/2026-08-09-st1-022-dated-status-source-review.json`
- Local-only review package.

## Files Allowed to Change
- `evidence/sanitized/<dated-st1-023-human-review-summary>.json`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when genuinely required

## Execution Steps
1. Validate the package schema, uniqueness, and candidate count without publishing raw content.
2. Present all 12 cards in deterministic batches; request exactly one permitted disposition per card.
3. Persist only explicit decisions locally and verify the complete set.
4. If any candidate is approved, create one narrow, approval-gated certification-preparation task; otherwise create one evidence-gap task based on the actual outcomes.

## Acceptance Criteria
- Exactly 12 explicit, attributable decisions exist; none is inferred.
- No candidate is certified or persisted to platform services.
- Sanitized evidence has counts only and contains no real excerpts or raw locators.
- One atomic next task follows actual review outcomes.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-09-st1-022-dated-status-source-selection.json > /dev/null
python -m json.tool evidence/sanitized/2026-08-09-st1-022-dated-status-source-review.json > /dev/null
git diff --check
```

## Evidence Required
- Local-only review package and decision audit.
- Sanitized aggregate decision summary.

## Rollback
Decision-only; remove only a mistaken local runtime decision artifact. No source or platform state changes occur.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required
