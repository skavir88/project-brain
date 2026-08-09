# Next Task

## Metadata
- Task ID: ST1-020
- Stage: Stage 1 — Product Implementation
- Status: Ready — Human Review required
- Owner: Designated business reviewer

## Objective
Obtain an explicit disposition for each of the 15 local-only, substantive ST1-019 review candidates; certify no candidate unless the reviewer explicitly approves it.

## Rationale
The selected bounded corpus produced provenance-backed potential status evidence, but source authority, context, conflicts, and factual correctness cannot be established by deterministic extraction. Human review is the mandatory credibility gate before any real organizational claim can enter the certification path.

## Preconditions
- Local-only package `%LOCALAPPDATA%\EnterpriseAI\runtime\st1-019-human-review-package.json` exists.
- `evidence/sanitized/2026-08-09-st1-019-extraction-review.json` validates.
- Review occurs locally; candidate excerpts and source locators are not copied into Git, evidence, logs, or external services.

## Scope
- Present each local review card with claim, source alias/reference, precise page/paragraph/table/cell location, minimum local supporting excerpt, date/value when extracted, uncertainty, and conflict references.
- Record the reviewer’s exact `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT` decision in local runtime audit state.
- Create a sanitized aggregate decision summary without raw content, filenames, locators, credentials, or source excerpts.

## Out of Scope
- Automatic certification, source modification, corpus expansion, SMB rediscovery, platform persistence, PostgreSQL/Qdrant/Dify use, external AI/model use, remote-host changes, public exposure, credentials, or destructive operations.

## Files to Inspect
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-09-st1-019-source-selection.json`
- `evidence/sanitized/2026-08-09-st1-019-extraction-review.json`
- Local-only runtime review package.

## Files Allowed to Change
- `evidence/sanitized/<dated-st1-020-human-review-summary>.json`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if a new architectural decision is genuinely required.

## Execution Steps
1. Validate the sanitized summary and local-only package schema without publishing real content.
2. Display each review card locally and request exactly one permitted disposition from the designated reviewer.
3. Persist each explicit decision only in local runtime audit state; do not infer a decision.
4. If any item is explicitly approved, create one narrow next task for controlled certification of only that item; otherwise create one evidence-gap or conflict-resolution task based on the actual decisions.
5. Update Project Brain and sanitized aggregate evidence.

## Acceptance Criteria
- All 15 decisions are explicit and attributable; no decision is inferred.
- No unapproved real candidate is certified or persisted to platform services.
- Sanitized evidence contains decisions/counts only, never raw organizational content or source locators.
- A single atomic next task is created from the actual review outcome.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-09-st1-019-source-selection.json > /dev/null
python -m json.tool evidence/sanitized/2026-08-09-st1-019-extraction-review.json > /dev/null
git diff --check
```

## Evidence Required
- Local-only review package and audit state.
- Sanitized decision-count summary with no real content.

## Rollback
Decision-only activity: remove only the local runtime decision artifact if a data-entry mistake is identified; no source or platform state changes occur.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required
