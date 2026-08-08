# Next Task

## Metadata
- Task ID: ST1-007
- Stage: Stage 1 — Product Implementation
- Status: Blocked — certification lifecycle policy decision required
- Owner: Product/architecture owner

## Objective
Approve the minimum controlled transition from persisted `certification_candidate` to final `certified` data/knowledge.

## Rationale
ST1-006 now persists candidate/review/rejection states durably. Final certification semantics, authorization, evidence requirements, and human-review behavior are not yet approved and must not be inferred.

## Decision Required
- Define who or what may transition a candidate to `certified`.
- Define minimum evidence and audit fields required for that transition.
- Confirm whether the first MVP transition is manual/HITL only.

## Out of Scope
- Automatic certification, public UI, external AI/RAG integration, real data, destructive changes, and credential changes.

## Evidence Required
- Explicit lifecycle decision recorded in `DECISIONS.md`.

## Definition of Done
- One approved, atomic implementation task for the controlled certification transition is created.
