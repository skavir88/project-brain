# Next Task

## Metadata
- Task ID: ST1-056
- Stage: Stage 1 — Product Implementation
- Status: Awaiting architecture/governance decision
- Owner: Designated business and architecture owner

## Objective
Decide the bounded SDAS v0.2 scope before adding supersession/revocation,
reliance eligibility, external rollout, or any legal/insurance semantics.

## Rationale
- ST1-055 implemented and verified the approved additive v0.1 pilot: 49 SDAS-1 / `assessed_partial` envelopes, append-only assessment and consumption evidence, and no SDAS-3/reliance-eligible record.
- The authoritative-source/currentness track remains independently blocked pending a business locator or reporting owner; `current_status=insufficient_certified_evidence` remains unchanged.

## Inputs
- Explicit decision on whether SDAS v0.2 should address only one bounded topic: (a) governed supersession/revocation, (b) authority/freshness assessment, (c) reliance-eligibility definition, or (d) external organizational rollout.

## Allowed Hosts
- None.

## Allowed Operations
- Documentation review and a single separately approved, additive implementation task after the decision.

## Forbidden Operations
- Automatic reliance eligibility, certification/currentness/retrieval-policy changes, destructive migration, public exposure, insurance/underwriting/coverage/pricing/legal-policy implementation, or raw organizational-content logging.

## Evidence Requirements
- Explicit decision record, bounded scope, lifecycle/policy ownership, privacy/retention requirements, and rollback strategy.

## Rollback
- None; this decision-gate task changes no runtime state.

## Definition of Done
- One bounded SDAS v0.2 implementation task or a documented decision to retain v0.1 pilot-only status.
