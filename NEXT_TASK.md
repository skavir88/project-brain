# Next Task

## Metadata
- Task ID: ST1-059
- Stage: Stage 1 — Product Implementation
- Status: Awaiting explicit governance/business input
- Owner: Architecture and business-data owner

## Objective
Decide the smallest authorized evidence source and governance basis required
to establish source authority/currentness for a CEO-status snapshot, or to
activate any SDAS post-registration lifecycle action.

## Rationale
- The private SDAS v0.2 provenance/policy pilot is complete but does not
  establish authority, currentness, or reliance eligibility.

## Preconditions
- Identify an authoritative reporting owner or a specific bounded source,
  or submit an evidence-backed lifecycle event request with actor authority.

## Scope
- Read-only assessment of the supplied source or event request; produce an
  atomic task only after evidence and required approvals are explicit.

## Out of Scope
- Broad discovery, automatic certification, authority/currentness upgrade,
  reliance eligibility, policy weakening, credential changes, public
  exposure, destructive operations, and lifecycle-event activation without
  evidence and explicit approval.

## Files to Inspect
- `AI_CONTEXT.md`
- `CURRENT_STATE.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `docs/SDAS_V0_1_PROPOSAL.md`

## Files Allowed to Change
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md` (only if a decision is made)
- `NEXT_TASK.md`
- sanitized evidence only

## Execution Steps
1. Validate scope and evidence for the supplied source/event request.
2. Assess authority, reporting/effective date, provenance, and currentness
   separately; preserve missing evidence as missing.
3. Stop for explicit approval before certification, lifecycle activation, or
   trust-boundary change.

## Acceptance Criteria
- No speculative locator or broad discovery is used.
- Any future action has an explicit actor, evidence reference, integrity
  input, timestamp semantics, failure behavior, and approval gate.
- `current_status=insufficient_certified_evidence` remains unchanged unless
  separately approved evidence proves otherwise.

## Verification Commands
```powershell
git diff --check
Get-Content -Raw evidence/sanitized/<new-evidence>.json | ConvertFrom-Json | Out-Null
```

## Evidence Required
- Sanitized authority/currentness assessment or blocked lifecycle request;
  no raw organizational content or secret.

## Rollback
- Read-only task; no runtime rollback is required.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md`, only when required
- `NEXT_TASK.md`
