# Next Task

## Metadata
- Task ID: ST1-047
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Human Review
- Owner: Designated business reviewer

## Objective
Obtain one explicit disposition for each of the seven existing ST1-046 management-report candidates without changing their IDs, source-attributed reporting-period semantics, or cell-level provenance.

## Required Decisions
- `review-21425de2da8b6731`
- `review-5bc218514a8559ea`
- `review-6b3b32ae24ffbd32`
- `review-3194b3fa5b6a9ce7`
- `review-30279a777f7e6877`
- `review-64bffb6cef1da61f`
- `review-305764f860fc7ff6`

Allowed disposition for each ID: `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT`.

## Scope
- Render and record only the existing runtime-local ST1-046 cards.
- Preserve the internally stated reporting period, source attribution, plan/actual metric distinction, formula/literal status, and all uncertainty.

## Out of Scope
- New discovery or extraction; source modification; automatic certification; resolving authority, currentness, metric semantics, issue resolution, or source conflicts by inference; persistence to PostgreSQL, Certified Knowledge, Qdrant, or Dify.

## Evidence Requirements
- Maintain local append-only decision state and sanitized aggregate evidence only.
- Do not version raw source content, filename, locator, excerpt, or credentials.

## Rollback
- No platform state change is permitted. Any candidate without explicit `APPROVE` remains outside all trusted stores.

## Definition of Done
- Every listed ID has one exact explicit disposition.
- Only explicitly approved candidates may enter a separate controlled-certification task.
- Project Brain and sanitized evidence are updated and exactly one next atomic task is created.
