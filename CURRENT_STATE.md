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

## Declared, Not Verified
- Five VMware-hosted Ubuntu servers and their declared roles/IPs are listed in `ARCHITECTURE.md` and `inventory/hosts.yaml`.
- Docker Compose is the intended deployment method.
- PostgreSQL, Redis, Qdrant, Dify `1.16.0`, n8n, Nginx, and a monitoring/logging stack are planned components.
- Dify is intended to use PostgreSQL, Redis, and Qdrant as external backends.

## Unknowns and Constraints
- No SSH or local-server evidence is available in this repository.
- Service installation, runtime status, versions, ports, dependencies, security posture, backup, HA, and observability are `unknown`.
- Raw host evidence must be collected locally, reviewed, and sanitized before any repository use.

## Next Operational Target
Run the approved read-only collector on each declared host and safely provide sanitized outputs for review.
