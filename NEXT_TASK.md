# Next Task

## Metadata
- Task ID: ST1-041
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Human Review
- Owner: Designated business reviewer

## Objective
Obtain one explicit disposition for each of the three existing ST1-040 runtime-local candidates.

## Scope
- Render and record only the existing candidate IDs from the local `st1-040-human-review-package.json`.
- Preserve each candidate's source-attributed date semantics, provenance, uncertainty, and currentness boundary.

## Out of Scope
- New source discovery or extraction; changing candidate IDs; automatic certification; platform persistence; treating a dated document as current status; treating a procurement release, document submission, or action deadline as completion or issue resolution.

## Required Decisions
- `review-ce24321a1153180b`: `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT`.
- `review-6afc7046e3178ed5`: `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT`.
- `review-8a906726a2d843ed`: `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT`.

## Evidence Requirements
- Local append-only decision state and a sanitized aggregate result only.
- Raw source locators, filenames, organizational excerpts, and credentials remain outside Git.

## Definition of Done
- All three decisions are explicit and recorded exactly.
- Only approved candidates may be proposed for a separate controlled-certification task.
- No candidate changes `current_status` without a separate evidence-backed decision.
- Project Brain, sanitized evidence, and one next atomic task are updated.
