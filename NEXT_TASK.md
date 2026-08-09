# Next Task

## Metadata
- Task ID: ST1-028
- Stage: Stage 1 — Product Implementation
- Status: Blocked — bounded locator or indexed metadata result required
- Owner: Designated business reviewer / operator

## Objective
Provide one bounded source-relative folder locator, or one indexed metadata result, for a plausible project-status/reporting source that may contain an internal document date later than `1402/02/27`.

## Rationale
The approved pilot root is reachable, but a metadata-only traversal that excluded all exhausted corpora exceeded the 120-second bounded limit without producing a safe candidate result. Repeating it would be an unbounded performance loop.

## Preconditions
- The source must remain under the approved pilot root.
- The source must be a bounded PDF, DOCX, and/or XLSX folder set.
- No source content, filename, path, or credential is to be entered into versioned evidence.

## Scope
- The operator may use local Windows Explorer or an indexed metadata search to identify one containing folder with project-status, progress, monthly/weekly report, management report, project controls, or schedule/reporting signals.
- Supply only the selected folder locator directly in the conversation; it will be retained only in local runtime state.
- The agent will validate its metadata signature before any content access.

## Out of Scope
- Repeating an unrestricted recursive traversal, opening content before a bounded candidate is validated, modifying source data, certification, platform persistence, external-model use, or public exposure.

## Files to Inspect
- `CURRENT_STATE.md`
- `evidence/sanitized/2026-08-09-st1-027-newer-source-discovery.json`

## Files Allowed to Change
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if a bounded source is explicitly selected

## Execution Steps
1. Receive one bounded locator or indexed metadata candidate from the operator.
2. Validate its containment, allowlisted extension distribution, count, size, and metadata without opening content.
3. Create exactly one bounded read-only extraction task only when the signature is safe and the candidate may extend the timeline.

## Acceptance Criteria
- The source is bounded and within the approved pilot root.
- No content is opened before metadata validation.
- The operator input and raw locator remain outside Git and sanitized evidence.
- Exactly one atomic next task follows validation.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-09-st1-027-newer-source-discovery.json > /dev/null
git diff --check
```

## Evidence Required
- Sanitized bounded-discovery timeout record.
- Runtime-local candidate locator and sanitized aggregate metadata signature.

## Rollback
Read-only locator validation; no source, platform, or infrastructure state is changed.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required
