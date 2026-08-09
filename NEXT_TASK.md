# Next Task

## Metadata
- Task ID: ST1-038
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Human Review
- Owner: Designated business reviewer

## Objective
Obtain one explicit disposition for each of the 15 existing local-only ST1-037 currentness-review candidates.

## Scope
- Render and record only the existing candidate IDs from the local `st1-037-human-review-package.json`.
- Preserve source-attributed date, provenance, field semantics, uncertainty, and non-currentness boundaries for any approval.

## Out of Scope
- Regeneration/extraction; automatic certification; platform persistence; source discovery; changing review IDs; interpreting planned dates as achieved events or actual values as present-day completion.

## Required Decisions
For every displayed ID, choose exactly one: `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT`.

## Evidence Requirements
- Local append-only decision state and aggregate sanitized count only.
- No raw source content, locator, filename, or secret enters versioned artifacts.

## Definition of Done
- All 15 decisions are explicit and recorded.
- Only approved claims may be prepared for a separate controlled-certification task.
- Project Brain and sanitized evidence are updated with one atomic next task.
