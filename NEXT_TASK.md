# Next Task

## Metadata
- Task ID: ET0-004
- Stage: Stage 0 — Project Discovery, Baseline and Automation Foundation
- Status: Ready
- Owner: Autonomous Implementation Agent

## Goal
Collect sanitized, read-only runtime-connection evidence showing whether running Dify API/worker components on `rdapp` have observed TCP connections to the declared `rddb` and `rdvector` backend IPs.

## Scope
- Allowed hosts: `rdapp` only, using `enterprise-ai-rdapp`.
- Allowed operations: SSH preflight, `docker ps`, read-only `docker exec`, and reading `/proc/net/tcp` or `/proc/net/tcp6` only.
- Create one sanitized evidence file containing component counts, command exit codes, and booleans for observed connections to declared backend identifiers.

## Forbidden Operations
- No Docker inspection, configuration or environment-value reads, writes, package changes, restarts, deploys, database queries, network changes, or operations on hosts outside scope.
- Do not persist container IDs, names, raw IP addresses, port values, environment values, labels, mounts, logs, credentials, or raw `/proc` output.

## Inputs
- `inventory/hosts.yaml`
- `evidence/sanitized/2026-08-06-stage0-service-inventory.json`
- `CURRENT_STATE.md`
- `ARCHITECTURE.md`

## Steps
1. Run the mandatory read-only preflight on `rdapp`.
2. Identify running Dify API/worker container IDs in memory only from `docker ps` output.
3. Read the selected containers’ TCP tables without storing raw output.
4. Record only whether a connection to the declared `rddb` or `rdvector` backend IP was observed; absence is `unknown`, not evidence of non-use.
5. Sanitize evidence, update Project Brain, run final checks, and create the next atomic task.

## Verification
```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdapp 'hostname; whoami; pwd; date -u; df -h; free -m; docker --version; docker compose version'
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdapp "docker ps --format '{{.ID}}\t{{.Image}}\t{{.Status}}'"
```

## Evidence Requirements
- Successful preflight and service-list exit codes.
- Sanitized booleans for observed active TCP connections to `rddb` and `rdvector`, per component category.
- Explicit `unknown` classification when no usable connection evidence exists.

## Rollback
No remote or service state changes are made. If review finds prohibited content, remove only the new sanitized evidence file and revert its documentation references.

## Definition of Done
- Only `rdapp` is contacted.
- No prohibited data is persisted.
- Every added claim is tied to exit-code evidence.
- `CURRENT_STATE.md`, `ARCHITECTURE.md`, `SESSION_LOG.md`, `CHANGELOG.md`, and `NEXT_TASK.md` are updated.
- `git diff --check`, secret scan, legacy scan, and JSON validation pass.
