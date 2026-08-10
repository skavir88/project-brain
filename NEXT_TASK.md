# Next Task

## Metadata
- Task ID: ST1-062
- Stage: Stage 1 — Product Implementation
- Status: Awaiting explicit Human Review and authority evidence
- Owner: Designated business reviewer

## Objective
Review the single ST1-061 real-record candidate and decide whether missing
authority and business/effective-time evidence can be supplied. Do not
certify unless the reviewer explicitly approves a separately prepared claim.

## Scope
- Review only the runtime-local ST1-061 provenance package and the source
  authority/business-date evidence supplied by the owner.

## Out of Scope
- Automatic certification, authority/currentness inference, external AI,
  source expansion, public exposure, and destructive operations.

## Acceptance Criteria
- The decision is explicit; missing evidence stays missing.
- No certification occurs without an explicit `APPROVE` for a concrete claim.

## Verification Commands
```powershell
git diff --check
```

## Evidence Required
- Sanitized review/authority outcome only; no raw organizational content.

## Rollback
- No runtime mutation is authorized.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
