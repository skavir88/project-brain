# Next Task

## Metadata
- Task ID: ST1-044
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Business Confirmation
- Owner: Designated business reviewer

## Objective
Confirm whether the bounded metadata location represented by `st1-043-e3aca7f9868040d6` is the project team's Management Reports / project-status source to inspect in a separate read-only task, or select one of the other presented tokens.

## Rationale
The location has the strongest directory/name signals for an overall project-status source, but metadata cannot prove source authority, reporting period, or currentness. The preceding locator instruction explicitly prohibited content opening.

## Preconditions
- The runtime-local metadata index and raw locator mapping remain available.
- No source content has been opened by ST1-043.

## Scope
- Obtain one business confirmation of the intended bounded location only.
- Preserve the existing ST1-042 candidates and their IDs without re-rendering, altering, certifying, or replacing them.

## Out of Scope
- Content access, extraction, SMB crawling, certification, Qdrant/Dify persistence, or automatic source-authority/currentness conclusions.

## Evidence Required
- The selected runtime-local token and a sanitized selection rationale; no raw locator, filename, excerpt, or secret enters Git.

## Rollback
- No state-changing operation is permitted; a declined selection leaves all sources unopened.

## Definition of Done
- One bounded source token is explicitly confirmed for a new read-only extraction task, or all candidates are declined.
- Project Brain is updated and exactly one next atomic task is created.
