# Next Task

## Metadata
- Task ID: ST1-001
- Stage: Stage 1 — Product Implementation
- Status: Blocked — Stage transition approval required
- Owner: Product/architecture owner

## Goal
Create a local, non-production ingestion-service implementation workspace with a health-only endpoint and Docker Compose validation, establishing the first executable Enterprise AI product artifact without using organizational data.

## Transition Gate
Stage 0 is complete. Execution of this task requires explicit approval to enter Stage 1 because `AI_CONTEXT.md` and `PROJECT.md` keep Stage 1 out of scope until transition approval.

## Scope After Approval
- Create only local implementation artifacts in this repository or an explicitly approved implementation workspace.
- Use a health-only ingestion-service skeleton and Docker Compose validation.
- Do not connect to organizational data, deploy to declared hosts, expose public endpoints, or claim production readiness.

## Forbidden Operations
- No remote deployment, database provisioning, real-data ingestion, secret creation, public exposure, destructive operation, or Stage 1 scope expansion beyond the approved health-only skeleton.

## Inputs
- `PROJECT.md`
- `ARCHITECTURE.md`
- `MASTER_PLAN.md`
- `DESIGN_SYSTEM.md`
- `evidence/sanitized/2026-08-08-stage0-transition-readiness.json`

## Verification After Approval
```bash
git diff --check
# Run the implementation workspace health and Docker Compose validation commands defined by ST1-001.
```

## Evidence Requirements
- Explicit Stage 1 transition approval.
- Local health endpoint verification and Docker Compose validation output, sanitized before recording.

## Rollback
Remove only the newly created local implementation skeleton if review fails; do not affect Stage 0 infrastructure.

## Definition of Done
- Stage transition approval is recorded.
- Health-only service skeleton and Compose validation succeed locally.
- Project Brain is updated with the actual implementation evidence and one next atomic task.
