# Next Task

## Metadata
- Task ID: ST1-015
- Stage: Stage 1 — Product Implementation
- Status: Blocked — human review and format-resolution decision required
- Owner: Enterprise AI Project Operator

## Objective
Resolve the failed selected XLSX extraction and obtain a human-review decision for the local, redacted real-status evidence package before any real record can enter the certification lifecycle.

## Rationale
ST1-014 completed bounded, read-only extraction for 18 of 19 selected documents but one XLSX failed as `BadZipFile`. The three deterministic review items are unreviewed and folder/file metadata does not establish their authority, accuracy, or currentness.

## Preconditions
- DEC-015 and `evidence/sanitized/2026-08-08-st1-014-real-content-extraction.json` are available.
- A designated business reviewer can access the local runtime review package and the original selected documents through approved read-only source access.

## Scope
- Determine whether the single failed XLSX is a valid OOXML workbook, a renamed/legacy/unsupported format, or an inaccessible/corrupt source; record only a sanitized outcome.
- Review each local review item against its original source and decide whether it is unsupported, needs clarification, or may be submitted as a certification candidate through the existing controlled process.

## Out of Scope
- Broadening the subset, reading other source files, modifying source files, automatic certification, real-content persistence to PostgreSQL, Qdrant/Dify/AI use, public exposure, credentials, remote-host changes, and destructive operations.

## Files to Inspect
- `DECISIONS.md`
- `CURRENT_STATE.md`
- `evidence/sanitized/2026-08-08-st1-014-real-content-extraction.json`
- Local operator runtime review package and the bounded source document only.

## Files Allowed to Change
- `evidence/sanitized/<dated-st1-015-review-resolution>.json`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md` only if review changes product or architecture policy.

## Execution Steps
1. Perform a read-only format diagnosis of the failed selected XLSX without recording its name, path, or content in Git.
2. Have the designated reviewer assess each local review item against its original source and record only a sanitized decision and provenance-reference count.
3. Do not submit any record to certification unless the reviewer explicitly approves it and the existing policy requirements are met.

## Acceptance Criteria
- The XLSX failure has a sanitized, reproducible disposition.
- Every candidate item has a human-review outcome.
- No real content, secret, raw filename/path, or uncertified claim enters Git, PostgreSQL, Qdrant, Dify, or an external AI service.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-08-st1-014-real-content-extraction.json > /dev/null
git diff --check
```

## Evidence Required
- Sanitized XLSX-format result and aggregate human-review outcomes.

## Rollback
Read-only review task; discard local runtime review artifacts if policy requires. No source or platform state is changed.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required
