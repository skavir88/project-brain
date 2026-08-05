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
- Public-key authentication is `not verified`: `BatchMode=yes` returned `auth_failed` (exit code `255`) for every declared host because the project public key is not yet present in their `root` `authorized_keys`.
- No remote identity, collector execution, service status, version, port inventory, security posture, backup, HA, or monitoring claim is verified.

## Declared, Not Verified
- Five VMware-hosted Ubuntu servers and their declared roles/IPs are listed in `ARCHITECTURE.md` and `inventory/hosts.yaml`.
- Docker Compose is the intended deployment method.
- PostgreSQL, Redis, Qdrant, Dify `1.16.0`, n8n, Nginx, and a monitoring/logging stack are planned components.
- Dify is intended to use PostgreSQL, Redis, and Qdrant as external backends.

## Unknowns and Constraints
- A secure tool-mediated path to use password authentication for remote public-key installation is unavailable. The received password was not persisted, sent to a command, or recorded.
- An authorized operator must add the existing project public key to each declared host before non-interactive automation can proceed.
- Service installation, runtime status, versions, ports, dependencies, security posture, backup, HA, and observability are `unknown`.
- Raw host evidence must be collected locally, reviewed, and sanitized before any repository use.

## Next Operational Target
Enable project public-key authentication on each declared host, then verify non-interactive login before collecting baseline evidence.
