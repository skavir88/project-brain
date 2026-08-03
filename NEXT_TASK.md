# Next Task

## Metadata
- Task ID: ET0-002
- Stage: Stage 0 — Project Discovery, Baseline and Automation Foundation
- Status: Ready
- Owner: Authorized infrastructure operator

## Objective
Collect one read-only baseline JSON file from each declared host (`rddb`, `rdapp`, `rdvector`, `rdautomation`, `rdmonitor`) using the approved local collector, without making infrastructure changes.

## Rationale
All infrastructure status remains `unknown` until reproducible host-local evidence is available.

## Preconditions
- An authorized operator has local shell access to each declared Ubuntu host.
- `scripts/collect-host-baseline.sh` is transferred or made available without modification.
- `/var/tmp/enterprise-ai-baseline` is writable on each host, or a safe non-repository output directory is selected.

## Scope
- Run the collector locally once per declared host.
- Review outputs for secrets or sensitive operational content before sharing sanitized copies for review.
- Record a blocker if a host cannot be accessed or collection returns a nonzero code.

## Out of Scope
- Installing packages, changing Docker/Compose, restarting services, using SSH automation, or committing raw evidence.
- Declaring service availability, security, backup, HA, or production readiness.

## Files to Inspect
- `AI_CONTEXT.md`
- `CURRENT_STATE.md`
- `ARCHITECTURE.md`
- `inventory/hosts.yaml`
- `scripts/collect-host-baseline.sh`
- `evidence/README.md`

## Files Allowed to Change
- None in this repository during collection. A subsequent review task will define any permitted documentation updates.

## Execution Steps
1. On each matching host, run the collector with its declared host identifier.
2. Record the command exit code and the generated file path locally.
3. Review and sanitize outputs; do not commit raw files.
4. Provide sanitized outputs and recorded blockers for the next review task.

## Acceptance Criteria
- Exactly one output exists for each accessible declared host, with matching `host_id` and a UTC timestamp.
- Each output is valid JSON and includes all six named result records.
- Nonzero command or collector exit codes are retained as failures/unknowns, not treated as success.
- No raw output is committed to this repository.

## Verification Commands
```bash
bash scripts/collect-host-baseline.sh --host-id rddb
bash scripts/collect-host-baseline.sh --host-id rdapp
bash scripts/collect-host-baseline.sh --host-id rdvector
bash scripts/collect-host-baseline.sh --host-id rdautomation
bash scripts/collect-host-baseline.sh --host-id rdmonitor
```

## Evidence Required
- Five reviewed, sanitized JSON outputs or explicit per-host access/collection blockers.
- The local exit code for each collector execution.

## Rollback
No infrastructure changes are made. Remove only locally generated evidence files if the authorized operator decides they must not be retained.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if evidence requires an architecture decision
