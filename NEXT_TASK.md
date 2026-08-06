# Next Task

## Metadata
- Task ID: ET0-003
- Stage: Stage 0 — Project Discovery, Baseline and Automation Foundation
- Status: Ready
- Owner: Enterprise AI Project Operator

## Objective
Create one reviewed, machine-readable service inventory for the five declared hosts using only read-only SSH commands and a documented sanitization profile.

## Rationale
The first baseline verifies host reachability, Docker/Compose availability, and aggregate counts, but it intentionally excludes the service identities, versions, and published-port metadata needed to assess declared roles.

## Preconditions
- Public-key, non-interactive SSH authentication remains verified for all aliases in `inventory/hosts.yaml`.
- `evidence/sanitized/2026-08-05-stage0-host-baseline-summary.json` is available.
- No raw evidence will be committed.

## Scope
- Collect read-only Docker container metadata required to identify service category, image version, status, and published-port count.
- Sanitize output by excluding commands, labels, environment variables, mounts, container IDs, private registry paths, full port bindings, and secrets.
- Create one versioned machine-readable sanitized inventory and update Project Brain with evidence-backed service classifications only.

## Out of Scope
- Docker inspection, configuration reads, package changes, service restarts, deployment changes, database access, network changes, and any action outside the five declared aliases.

## Files to Inspect
- `AI_CONTEXT.md`
- `CURRENT_STATE.md`
- `ARCHITECTURE.md`
- `inventory/hosts.yaml`
- `evidence/sanitized/2026-08-05-stage0-host-baseline-summary.json`

## Files Allowed to Change
- `evidence/sanitized/`
- `CURRENT_STATE.md`
- `ARCHITECTURE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if required

## Execution Steps
1. Run the defined read-only service-list command through each alias with `BatchMode=yes`.
2. Validate exit codes and sanitize each record before writing it to Git.
3. Record only evidence-backed service classifications and unresolved unknowns.
4. Run repository consistency and secret scans; create the next atomic task.

## Acceptance Criteria
- Every accessible declared host has a sanitized service-inventory record or an explicit failure classification.
- The inventory identifies only service category, public image/version indicator, runtime status, and published-port count.
- No raw output, container ID, label, environment variable, mount, private registry path, secret, or full port binding is versioned.
- All claims added to Project Brain are traceable to successful command output.

## Verification Commands
```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rddb "docker ps --format '{{.Image}}\t{{.Status}}\t{{.Ports}}'"
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdapp "docker ps --format '{{.Image}}\t{{.Status}}\t{{.Ports}}'"
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdvector "docker ps --format '{{.Image}}\t{{.Status}}\t{{.Ports}}'"
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdautomation "docker ps --format '{{.Image}}\t{{.Status}}\t{{.Ports}}'"
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdmonitor "docker ps --format '{{.Image}}\t{{.Status}}\t{{.Ports}}'"
```

## Evidence Required
- One sanitized inventory record per host or a precise per-host failure classification.
- Recorded SSH and command exit codes.

## Rollback
Delete only the newly created sanitized inventory file if review finds prohibited data. No infrastructure changes are made.

## Completion Updates
- `CURRENT_STATE.md`
- `ARCHITECTURE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if required
