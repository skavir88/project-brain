# Next Task

## Metadata
- Task ID: ST1-014
- Stage: Stage 1 — Product Implementation
- Status: Ready
- Owner: Enterprise AI Project Operator

## Objective
Approve the bounded initial real-content subset and format allowlist for the first pilot ingestion batch.

## Rationale
ST1-013 confirmed read-only access but found a large, heterogeneous, partial-inventory dataset. Reading real content without a narrower subset and format policy would exceed the pilot boundary.

## Preconditions
- ST1-013 sanitized evidence is available.
- The architecture owner selects one subfolder or other deterministic bounded subset and an allowlist of formats to inspect first.

## Scope
- Record one explicit subset boundary and supported-format/content-extraction policy.
- Define one atomic content-read task that remains read-only and does not auto-certify real records.

## Out of Scope
- Reading document contents, ingestion, persistence of real content, certification, Qdrant indexing, Dify use, write access, recursive expansion through links/mounts, credential changes, public exposure, and destructive operations.

## Files to Inspect
- `CURRENT_STATE.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-08-st1-013-real-file-share-pilot-preflight.json`

## Files Allowed to Change
- `DECISIONS.md`
- `evidence/sanitized/<dated-st1-014-subset-decision>.json`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`

## Execution Steps
1. Record the approved subset boundary without exposing raw business content.
2. Record the extraction allowlist and explicitly excluded/risky types.
3. Define the smallest read-only content-extraction task, including content-sanitization and human-review limits.

## Acceptance Criteria
- The subset and allowlist are explicit enough to prevent a whole-folder crawl.
- The resulting task contains no auto-certification path and no secret.

## Verification Commands
```bash
git diff --check
# No implementation command is authorized until the subset/allowlist decision is recorded.
```

## Evidence Required
- Recorded subset/allowlist decision and one atomic follow-up task.

## Rollback
Documentation-only decision task; no rollback applies.

## Completion Updates
- `DECISIONS.md`
- `ARCHITECTURE.md`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
