# Current State

## Current Stage
`Stage 1 — Product Implementation (active)`.

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
- `evidence/sanitized/2026-08-08-et0-010-rdapp-container-classification.json` classifies one of those containers as a running Dify SSRF proxy. Two `rdapp` containers remain `other_unclassified`; this is a known limitation because safe discovery metadata is insufficient for reliable classification.
- The observed n8n placement on `rdapp` is accepted for the current MVP architecture. `rdapp` may host Dify runtime components, Nginx, n8n, and supporting application-runtime components; `rdautomation` is reserved for future automation/workflow scale-out or isolation.
- Dify runtime connectivity from `rdapp` is `verified` in `evidence/sanitized/2026-08-08-et0-004-dify-runtime-connectivity.json`: three running Dify API/worker components resolved `rddb` and `rdvector`, and each completed TCP handshakes to `rddb:5432`, `rddb:6379`, `rdvector:6333`, and `rdvector:6334`.
- The local `rdapp` HTTP entrypoint is `verified` as responding with HTTP `307` through a status-only request. No response data was recorded.
- Runtime reachability does not prove Dify configuration targets, authentication success, data access, or actual backend usage.
- Active Dify runtime connections to `rddb:5432` and `rddb:6379` are `verified` in `evidence/sanitized/2026-08-08-et0-005-dify-active-backend-connections.json`; each was observed from two of three sampled Dify API/worker components.
- No active Dify runtime connection to `rdvector:6333` or `rdvector:6334` was observed during the sample. This remains `unknown` and is not evidence that Qdrant is unused.
- No active Dify runtime connection to the Redis container on `rdapp` was observed in `evidence/sanitized/2026-08-08-et0-009-local-redis-active-connection.json`. This remains `unknown`, but the observed `rddb` Redis connections are the only active Redis backend evidence currently recorded.
- Declared backend service health is recorded in `evidence/sanitized/2026-08-08-et0-006-declared-backend-health.json`: PostgreSQL readiness is `verified` with reported version `16.14`; Redis returned `auth_required` to an unauthenticated PING and reported version `7.4.9`; Qdrant returned HTTP `200` to a status-only local health request but its version remains `not_available` through safe commands.
- Declared critical local listeners are `verified` in `evidence/sanitized/2026-08-08-et0-007-critical-listener-inventory.json`: `rddb:5432`, `rddb:6379`, `rdvector:6333`, `rdvector:6334`, and `rdapp:80` were observed without recording bind addresses or raw listener data.
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

## Stage 0 Outcome
- Stage 0 is complete; the Stage 1 transition was explicitly approved on 2026-08-08.
- Known limitations are documented and do not authorize production claims: two unclassified `rdapp` containers, Qdrant reported version, unauthenticated Redis readiness, and unobserved sampled Qdrant activity.

## Stage 1 Implementation Evidence
- The local ingestion-service began as a health-only skeleton under `implementation/ingestion-service/`; its current verified synthetic behavior is documented below. It has no persistence, external backend, credential, or remote-host behavior.
- The local service health contract is `verified` on 2026-08-08: `GET /health` returned HTTP `200` and the expected non-sensitive service/status fields. Evidence is `evidence/sanitized/2026-08-08-st1-001-local-ingestion-skeleton.json`.
- Docker Desktop with the WSL2 backend is `verified` as operational for local development on 2026-08-08: Docker Client/Server and Compose commands exited `0` in the `desktop-linux` context. The selected context uses a local Windows named pipe, not an insecure Docker TCP endpoint. The exact Compose configuration validation for the local ingestion skeleton also exited `0`; evidence is `evidence/sanitized/2026-08-08-st1-001-docker-compose-validation.json`.
- The first local `Ingestion → Structural Validation` slice is `verified` in `evidence/sanitized/2026-08-08-st1-002-synthetic-intake-validation.json`: `POST /v1/records` returned `202` for a valid synthetic record and `422` with machine-readable errors for an invalid record. The Compose service built, ran only through loopback, and was stopped after testing. No record persistence or external backend behavior exists.
- Deterministic identifier canonicalization and content fingerprinting are `verified` in `evidence/sanitized/2026-08-08-st1-003-canonicalization-fingerprint.json`: equivalent synthetic records produced the same SHA-256 fingerprint, while invalid records continued to return `422` without a fingerprint. No deduplication state or persistence exists.
- A process-local synthetic duplicate gate is `verified` in `evidence/sanitized/2026-08-08-st1-004-process-local-duplicate-gate.json`: the first valid fingerprint returned `202`, an equivalent repeat returned `409`, invalid input remained `422`, and a controlled service restart cleared duplicate state. This is a demonstration only; it is not durable deduplication, lineage, audit, quality scoring, or certification.
- The approved initial MVP Data Credibility Gate is `verified` in `evidence/sanitized/2026-08-08-st1-005-data-credibility-gate.json`. A valid unique synthetic record with usable provenance returned `certification_candidate`; insufficient provenance returned `human_review_required`; future supplied temporal metadata returned deterministic `rejected`; structural failure and duplicates retained `422`/`409` with machine-readable rejection codes. `certification_candidate` is not final certification and no result is persisted.

## Next Operational Target
Await the persistence target and credential-creation approval required for a durable MVP vertical slice beyond the verified local synthetic credibility gate.
