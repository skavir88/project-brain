# Next Task

## Metadata
- Task ID: ST1-022
- Stage: Stage 1 — Product Implementation
- Status: Blocked — explicit bounded source selection required
- Owner: Architecture owner / designated business reviewer

## Objective
Select exactly one additional bounded source that can establish current, authoritative evidence for the CEO project-status question, without reopening rejected educational sources or broadly rediscovering the file share.

## Rationale
ST1-021 extracted the maximum bounded value from `status_oriented_candidate_1`: the visible Change Log has useful status counts and impact flags, but its update date is blank and authority/currentness are unverified. The financial and site-support pages similarly lack the reporting context needed for an executive answer.

## Preconditions
- `evidence/sanitized/2026-08-09-st1-020-human-review-summary.json` and `evidence/sanitized/2026-08-09-st1-021-targeted-evidence-enrichment.json` validate.
- The new source is within the already approved pilot root and is available through the existing read-only SMB session.
- The user supplies or explicitly selects one bounded candidate/locator; no broad recursive SMB crawl is authorized.

## Scope
- Record one explicit bounded source-selection decision for a dated, authoritative project-status report or a populated current Change Log.
- Validate metadata signature and read-only accessibility only.
- Preserve raw locators only in local runtime state.

## Out of Scope
- Content reading before selection, broad SMB traversal, reopening any rejected educational/external source, automatic authority inference, certification, platform persistence, Qdrant/Dify/external model use, source modification, remote-host changes, credentials, public exposure, and destructive operations.

## Files to Inspect
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-09-st1-020-human-review-summary.json`
- `evidence/sanitized/2026-08-09-st1-021-targeted-evidence-enrichment.json`

## Files Allowed to Change
- `DECISIONS.md`, only if a new source-selection decision is required
- `evidence/sanitized/<dated-st1-022-source-selection>.json`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`

## Execution Steps
1. Confirm the selected source has a document-level reporting/effective date and a plausible authority relationship before opening content.
2. Record its bounded metadata signature and preserve its raw locator locally only.
3. Create one read-only extraction task limited to that source; do not read content in this task.

## Acceptance Criteria
- Exactly one explicit source is selected or a source-access blocker is recorded.
- The source is bounded, read-only, and targeted to the missing executive-status dimensions.
- No source is assumed authoritative merely from its name or filesystem timestamp.
- No rejected educational/external source is reopened.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-09-st1-020-human-review-summary.json > /dev/null
python -m json.tool evidence/sanitized/2026-08-09-st1-021-targeted-evidence-enrichment.json > /dev/null
git diff --check
```

## Evidence Required
- Sanitized source-selection metadata and local-only raw locator state.

## Rollback
Decision-only and metadata-only task; no source or platform state changes occur.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required
