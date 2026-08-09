# Next Task

## Metadata
- Task ID: ST1-032
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Human Review
- Owner: Designated business reviewer

## Objective
Obtain explicit decisions for the revised, same-ID ST1-030 candidates after ST1-031 established their worksheet-backed plan/actual semantics for reporting week `1402/06/25–1402/06/31`.

## Rationale
The prior review correctly found that numerical values without schema semantics were insufficient. ST1-031 now provides field labels, units where populated, formula relationships, row-level plan dates, and deterministic variance. Source authority, currentness, and completion semantics remain unverified and require Human Review.

## Preconditions
- The local-only revised package contains exactly the ten pre-existing candidate IDs.
- Every card retains source alias, row provenance, labelled field mapping, reporting week, uncertainty, and a non-completion boundary.
- The reviewer must use exactly `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT` for every ID.

## Scope
- Render and record decisions for the existing ten IDs only.
- Preserve source-attributed `1402/06/25–1402/06/31` reporting-week semantics if any item is approved.
- Prepare one subsequent controlled-certification task only for explicitly approved IDs.

## Out of Scope
- Automatic certification; new source discovery; further extraction; changing ST1-023/ST1-026 records; treating actual progress as completion; treating this historical reporting week as current status; platform persistence of unapproved claims.

## Files to Inspect
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-09-st1-031-workbook-schema-enrichment.json`

## Files Allowed to Change
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if a new approval/certification semantic decision is needed
- `evidence/sanitized/`, aggregate-only

## Execution Steps
1. Render the existing revised package; do not regenerate IDs or extract new source content.
2. Record each explicit reviewer decision exactly.
3. Keep rejected/unresolved items outside certification and platform persistence.
4. Create exactly one atomic follow-up task based on the complete decision set.

## Acceptance Criteria
- Ten explicit reviewer decisions are recorded.
- No certification precedes explicit approval.
- Any approved item preserves reporting week, source attribution, field semantics, provenance, and non-currentness boundary.
- Sanitized evidence contains no raw source content, locator, or formula output.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-09-st1-031-workbook-schema-enrichment.json > /dev/null
git diff --check
```

## Evidence Required
- Local-only revised review package and decision state.
- Sanitized aggregate decision summary after review.

## Rollback
Human Review is append-only. No source, infrastructure, certification, or platform state is changed before an explicit approval and separately verified certification task.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required
