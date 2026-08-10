# Next Task

## Metadata
- Task ID: ST1-067
- Stage: Stage 1 — Product Implementation
- Status: Awaiting explicit governance delegation decision
- Owner: Accountable Enterprise AI governance authority

## Objective
Obtain a complete, scoped governance decision that can create one real,
reusable delegated-authority record for the LOW-risk Project Controls progress
workbook class. This task does not certify any real organizational record.

## Rationale
ST1-061 locator recovery and native acquisition are already verified. ST1-066
confirmed that zero real delegations and zero real authority assertions exist,
so no real record can truthfully route to `policy_automatic`.

## Preconditions
- The governance authority completes every required field in
  `docs/ST1_067_GOVERNANCE_DELEGATION_DECISION_TEMPLATE.md`.
- The decision identifies a non-secret, stable actor identifier and its exact
  source-system, project, document-class, fact-class, and time scope.

## Scope
- Validate and persist only the explicit scoped delegation using the existing
  append-only delegated-authority model.
- Re-evaluate only exact LOW-risk policy matches after the delegation is
  active; retain missing/conflicting/high-risk cases as exceptions.

## Out of Scope
- Automatic certification; claim approval; currentness/authority inference;
  reliance eligibility; source expansion; credential changes; external AI;
  destructive operations; and any changes to ST1-061.

## Files to Inspect
- `docs/ST1_067_GOVERNANCE_DELEGATION_DECISION_TEMPLATE.md`
- `docs/SDAS_DELEGATED_AUTHORITY.md`
- `docs/SDAS_V0_3_CONTRACT.md`
- `CURRENT_STATE.md`
- `DECISIONS.md`

## Files Allowed to Change
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md` (only for the explicit approved decision)
- `NEXT_TASK.md`
- Sanitized evidence and an additive migration only if the supplied decision
  validates against the existing model.

## Execution Steps
1. Receive the complete, explicit governance decision; do not infer omitted fields.
2. Validate exact scope, effective period, fact classes, business-time rule,
   and revocation semantics against the v0.3 contract.
3. If valid, append the real delegation and an event; do not alter historical
   synthetic records or ST1-061.
4. Run an exact-match policy simulation, then persist only a policy decision
   permitted by the contract. Stop before any certification.
5. Sanitize evidence and update Project Brain.

## Acceptance Criteria
- A real delegation exists only after the accountable authority explicitly
  supplies all required scope and time fields.
- Missing, expired, revoked, conflicting, or out-of-scope evidence does not
  route to `policy_automatic`.
- No real record is certified, projected, indexed, or made current or
  reliance-eligible.

## Verification Commands
```powershell
git diff --check
Get-Content docs/ST1_067_GOVERNANCE_DELEGATION_DECISION_TEMPLATE.md -Raw
```

## Evidence Required
- Sanitized decision outcome, scope-validation result, and append-only event
  identifiers only. No raw organizational content, locator, or secret.

## Rollback
- Before a real decision, no runtime mutation occurs. If a valid delegation is
  later revoked, append a revocation event; never delete or overwrite it.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md` only when a valid decision is accepted
- `NEXT_TASK.md`
