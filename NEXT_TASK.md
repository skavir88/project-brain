# Next Task

## Metadata
- Task ID: ST1-005
- Stage: Stage 1 — Product Implementation
- Status: Blocked — minimum Quality Gate and Certified Data policy decision required
- Owner: Product/architecture owner

## Objective
Approve the smallest non-production policy that determines whether a synthetic record which passes structural validation and the process-local duplicate gate may be reported as a certification candidate, requires Human-In-The-Loop review, or is rejected.

## Rationale
The verified local slice now reaches `Ingestion → Structural Validation → Normalization → Deduplication`. The next required flow components, Quality Gates and Certified Data/Knowledge, have no approved acceptance rule, review behavior, or output semantics. Implementing those choices without an owner decision would invent material product requirements.

## Preconditions
- ST1-002, ST1-003, and ST1-004 evidence is available under `evidence/sanitized/`.
- The request is limited to synthetic, local, non-production behavior.

## Decision Required
- Select one disposition for a structurally valid, unique synthetic record: `certification_candidate`, `human_review_required`, or `rejected`.
- Specify any additional minimum quality checks beyond structural validity and duplicate absence, or explicitly confirm that no additional check applies to this MVP slice.
- Specify whether a candidate result may be represented only as a transient response or requires a durable audit/certification record. Durable storage is out of scope until separately approved.

## Scope After Decision
- Implement only the selected local, synthetic, non-production response semantics.
- Keep loopback-only Compose deployment and no persistence unless a separate storage decision is approved.

## Out of Scope
- Real organizational data, persistent certification/audit storage, external backends, remote deployment, public exposure, quality-score methodology not selected by the owner, destructive operations, and architecture expansion.

## Files to Inspect
- `PROJECT.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `CURRENT_STATE.md`
- `evidence/sanitized/2026-08-08-st1-002-synthetic-intake-validation.json`
- `evidence/sanitized/2026-08-08-st1-003-canonicalization-fingerprint.json`
- `evidence/sanitized/2026-08-08-st1-004-process-local-duplicate-gate.json`

## Files Allowed to Change
- `DECISIONS.md`
- `CURRENT_STATE.md`
- `MASTER_PLAN.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `implementation/ingestion-service/`
- `evidence/sanitized/`

## Verification Commands
```bash
git diff --check
```

## Evidence Required
- Explicit product-owner decision with the selected disposition and any quality criteria.
- If implementation follows, sanitized local response and Compose verification output.

## Rollback
No implementation change is authorized until the decision is recorded. Any later local response-only change must have an ignored timestamped backup and no persistent data.

## Definition of Done
- The policy decision is recorded in `DECISIONS.md`.
- The next atomic implementation task reflects only the approved policy.
- No unapproved quality, certification, HITL, persistence, or architecture behavior is introduced.
