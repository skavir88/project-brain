# Next Task

## Metadata
- Task ID: ET0-005
- Stage: Stage 0 — Project Discovery, Baseline and Automation Foundation
- Status: Ready
- Owner: Autonomous Implementation Agent

## Goal
Determine whether active Dify API/worker runtime processes on `rdapp` have observed TCP connections to the declared `rddb` and `rdvector` backend IPs, without reading configuration or environment values.

## Scope
- Allowed hosts: `rdapp` only, using `enterprise-ai-rdapp`.
- Allowed operations: SSH preflight, read-only `docker ps`, read-only `docker exec`, and reading selected containers’ `/proc/net/tcp` and `/proc/net/tcp6` only.
- Create one sanitized evidence file with component categories, command exit codes, and booleans for observed active connections to the declared backend identifiers.

## Forbidden Operations
- No Docker inspection, environment/config reads, writes, restarts, deploys, database queries, network changes, package changes, or operations outside `rdapp`.
- Do not persist container IDs, names, raw IP addresses, port values, raw `/proc` output, labels, mounts, logs, credentials, or secrets.

## Inputs
- `inventory/hosts.yaml`
- `evidence/sanitized/2026-08-08-et0-004-dify-runtime-connectivity.json`
- `CURRENT_STATE.md`
- `ARCHITECTURE.md`

## Steps
1. Run the mandatory read-only preflight on `rdapp`.
2. Identify running Dify API/worker container IDs in memory only.
3. Read `/proc/net/tcp` and `/proc/net/tcp6` from those containers; parse it in memory against declared backend IPs and the required backend ports.
4. Record only `observed`, `not_observed`, or `not_available` per backend identifier. Treat `not_observed` as `unknown`, not evidence of non-use.
5. Sanitize evidence, update Project Brain, run final checks, and create the next atomic task.

## Verification
```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdapp 'hostname; whoami; pwd; date -u; df -h; free -m; docker --version; docker compose version'
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdapp "docker ps --format '{{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Status}}'"
```

## Evidence Requirements
- Successful preflight and service-list exit codes.
- Sanitized per-component booleans for observed connections to `rddb:5432`, `rddb:6379`, `rdvector:6333`, and `rdvector:6334`.
- Explicit `unknown` interpretation for any `not_observed` result.

## Rollback
No remote or service state changes are made. If review finds prohibited content, remove only the new sanitized evidence file and revert documentation references.

## Definition of Done
- Only `rdapp` is contacted.
- No prohibited data is persisted.
- Every added claim is tied to exit-code evidence.
- `CURRENT_STATE.md`, `ARCHITECTURE.md`, `SESSION_LOG.md`, `CHANGELOG.md`, and `NEXT_TASK.md` are updated.
- `git diff --check`, secret scan, legacy scan, and JSON validation pass.
