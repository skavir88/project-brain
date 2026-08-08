# Next Task

## Metadata
- Task ID: ET0-011
- Stage: Stage 0 — Project Discovery, Baseline and Automation Foundation
- Status: Blocked — architecture decision required
- Owner: Architecture owner

## Goal
Resolve the discrepancy between observed n8n on `rdapp` and the declared `rdautomation` responsibility, so Stage 0 can complete its architecture transition gate.

## Decision Required
Select exactly one outcome:

1. **Accept observed placement:** record n8n as an `rdapp` responsibility and revise the declared `rdautomation` role.
2. **Move n8n to `rdautomation`:** authorize a separate scoped migration/deployment task with explicit data, downtime, backup, rollback, and verification controls.
3. **Exclude observed n8n from Enterprise AI scope:** record it as an unrelated existing service and retain `rdautomation` as the planned Enterprise AI automation host.

## Scope
- Allowed hosts: none until an outcome is selected.
- Allowed operations after selection: Project Brain decision/state/architecture documentation only. Any n8n move requires a new separately approved task.

## Forbidden Operations
- No remote connection, service move, restart, deployment, Docker change, data access, configuration read, credential access, or network change.
- Do not infer the architecture outcome from observed placement.

## Inputs
- `ARCHITECTURE.md`
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `MASTER_PLAN.md`
- `evidence/sanitized/2026-08-06-stage0-service-inventory.json`
- `evidence/sanitized/2026-08-08-et0-008-stage0-completion-review.json`

## Verification
```bash
git diff --check
rg -n -i "(password\s*[:=]|api[_-]?key\s*[:=]|secret\s*[:=]|token\s*[:=]|private[_-]?key\s*[:=])" -g "!evidence/**" .
rg -n -i "[A]randi|Phase 0[.]5|[G]apGPT|[.]ai/" -g "*.md" -g "*.txt" .
```

## Evidence Requirements
- Explicit architecture-owner outcome.
- Updated decision, architecture, state, changelog, session log, and exactly one next task.

## Rollback
Revert only Project Brain documentation changes if the selected outcome is entered incorrectly. No infrastructure action is authorized by this task.

## Definition of Done
- One outcome is recorded without ambiguity.
- No unauthorized n8n infrastructure action is performed.
- Stage 0 Completion Review is updated with the resulting transition classification.
- Final repository safety checks pass.
