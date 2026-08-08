# Current State

## Current Stage
`Stage 0 — Project Discovery, Baseline and Automation Foundation` is active.

## Status Model
- `planned`: intended but not configured.
- `configured`: configuration exists, but runtime operation is unproven.
- `deployed`: installation or deployment is evidenced, but expected behavior is unproven.
- `verified`: reproducible evidence confirms the stated condition.
- `unknown`: no sufficient evidence is available.

## Confirmed Repository Baseline
- The 10 Project Brain documents exist in the repository root.
- The Enterprise AI documentation baseline and local collection kit were created in this session; repository-local verification is recorded in `SESSION_LOG.md`.

## SSH Bootstrap Status
- Local SSH configuration for all five declared aliases is `configured`; the dedicated private key remains only on the control workstation.
- TCP connectivity to port `22` is `verified` for all five declared IPs as of 2026-08-05.
- The observed SSH host-key fingerprints were registered in the control workstation's `known_hosts` with host-key verification enabled.
- Public-key authentication and non-interactive `root` login are `verified` for every declared alias: `BatchMode=yes` returned `root` with exit code `0` on 2026-08-05.
- The read-only collector is `verified` on every declared host. The reviewed summary is `evidence/sanitized/2026-08-05-stage0-host-baseline-summary.json`; raw JSON remains outside Git on the remote hosts.
- Docker CLI and Docker Compose command availability are `verified` on every declared host. The baseline observed running-container counts were `rddb=2`, `rdapp=12`, `rdvector=1`, `rdautomation=0`, and `rdmonitor=0`; service identity required the subsequent sanitized inventory.
- The sanitized service inventory is `verified` in `evidence/sanitized/2026-08-06-stage0-service-inventory.json`. It observed running PostgreSQL and Redis containers on `rddb`, Qdrant on `rdvector`, and Dify `1.16.0` API/web components, Nginx, Redis, n8n, and additional unclassified containers on `rdapp`.
- A placement divergence is observed: n8n is running on `rdapp`, while `rdautomation` has no running containers. This is evidence, not an approved architecture change.
- Dify runtime connectivity from `rdapp` is `verified` in `evidence/sanitized/2026-08-08-et0-004-dify-runtime-connectivity.json`: three running Dify API/worker components resolved `rddb` and `rdvector`, and each completed TCP handshakes to `rddb:5432`, `rddb:6379`, `rdvector:6333`, and `rdvector:6334`.
- The local `rdapp` HTTP entrypoint is `verified` as responding with HTTP `307` through a status-only request. No response data was recorded.
- Runtime reachability does not prove Dify configuration targets, authentication success, data access, or actual backend usage.
- Full service versions, port values, dependencies, configuration targets, security posture, backup, HA, and monitoring remain unverified.

## Declared, Not Verified
- Five VMware-hosted Ubuntu servers and their declared roles/IPs are listed in `ARCHITECTURE.md` and `inventory/hosts.yaml`.
- Docker Compose is the intended deployment method.
- PostgreSQL, Redis, Qdrant, Dify `1.16.0`, n8n, Nginx, and a monitoring/logging stack are planned components.
- Dify is intended to use PostgreSQL, Redis, and Qdrant as external backends.

## Unknowns and Constraints
- Specific service identities, versions, published ports, dependencies, security posture, backup, HA, and monitoring remain `unknown` because raw collector detail was intentionally excluded from the versioned summary.
- Service installation, runtime status, versions, ports, dependencies, security posture, backup, HA, and observability are `unknown`.
- Raw host evidence must be collected locally, reviewed, and sanitized before any repository use.

## Next Operational Target
Collect sanitized runtime-connection evidence for active Dify connections to declared backend IPs; do not infer backend usage from reachability alone.
