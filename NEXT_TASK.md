# Next Task

## Metadata
- Task ID: ST1-018
- Stage: Stage 1 — Product Implementation
- Status: Blocked — explicit bounded replacement-source decision required
- Owner: Architecture owner / business reviewer

## Objective
Select one new bounded, read-only source subset that is expected to contain authoritative project-status reporting, or explicitly conclude that no additional real-data source is authorized for the pilot.

## Rationale
ST1-017 fully processed the selected `status_candidate_b` subset with local Persian OCR. It yielded only two undated financial observations and cannot support the CEO question. Broadening or selecting another subset would change the business meaning of the pilot and requires an explicit decision.

## Preconditions
- `evidence/sanitized/2026-08-09-st1-017-bounded-ocr-and-review.json` is available.
- Any proposed replacement is described with non-sensitive aggregate metadata, exact read-only boundary, format allowlist, and business rationale.

## Scope
- Review the existing candidate summaries or provide one explicitly bounded replacement source.
- Record the decision and create one subsequent extraction task only after approval.

## Out of Scope
- Automatic corpus expansion, reading new content, certification, source modification, external AI/model use, real-content persistence, Qdrant/Dify use, remote-host changes, credentials, public exposure, and destructive operations.

## Files to Inspect
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-08-st1-014-subset-discovery.json`
- `evidence/sanitized/2026-08-09-st1-017-bounded-ocr-and-review.json`

## Files Allowed to Change
- `DECISIONS.md`
- `evidence/sanitized/<dated-st1-018-source-decision>.json`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`

## Execution Steps
1. Select exactly one bounded source with a documented business rationale for the CEO project-status question.
2. Record its explicit read-only boundary, format policy, and expected reporting value.
3. Create the next atomic content-access task; do not read the new source in this decision task.

## Acceptance Criteria
- The decision does not infer authority from filename or timestamp alone.
- The new boundary prevents a whole-share crawl and excludes unsupported formats.
- No real content is read, stored, certified, or sent to any AI service during this task.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-09-st1-017-bounded-ocr-and-review.json > /dev/null
git diff --check
```

## Evidence Required
- Sanitized replacement-source decision with no raw paths or filenames.

## Rollback
Decision-only task; no source or platform state changes.

## Completion Updates
- `DECISIONS.md`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
