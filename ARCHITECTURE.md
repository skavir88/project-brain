# Architecture

## Evidence Status
The topology below is **declared** project context. Host reachability, Docker/Compose availability, observed service placement, selected listeners, and selected runtime connectivity are separately verified in the dated evidence sections below. Declared responsibilities and configuration targets remain distinct from observed evidence.

## Declared Infrastructure Topology
| Host | IP | Declared responsibility |
|---|---:|---|
| `rddb` | `172.20.190.61` | PostgreSQL and durable data services |
| `rdapp` | `172.20.190.62` | Dify, Nginx, and application services |
| `rdvector` | `172.20.190.63` | Qdrant and vector services |
| `rdautomation` | `172.20.190.64` | Reserved for future automation/workflow scale-out or isolation |
| `rdmonitor` | `172.20.190.65` | Monitoring, logging, and observability |

The declared virtualization platform is VMware and declared server OS is Ubuntu Linux. Docker CLI and Docker Compose command availability are `verified` on all five declared hosts by the 2026-08-05 baseline collection; VMware, service deployment, service versions, and configuration remain unverified.

## Logical Flow
`Data Sources → Ingestion → Structural Validation → Normalization and Deduplication → Quality Gates → Certified Data / Certified Knowledge → AI Services, Automation, Reporting, Audit, and Monitoring`.

Human review/HITL is a branch from Quality Gates for sensitive cases.

## Technical Boundaries
- PostgreSQL, Redis, and Qdrant are intended to be external backends for Dify. They must not be duplicated inside the application stack without a recorded architecture decision.
- Services must be independently deployable and communicate backend-to-backend.
- No claim of production readiness, HA, backup, monitoring, or security hardening is permitted without recorded evidence.
- The need for accessible regional image/package mirrors is `planned` and requires a later decision backed by operational evidence.

## Verified Synthetic MVP Runtime — 2026-08-08
The loopback-only ingestion service on `rdapp` persists synthetic Stage 1 records to the isolated `enterprise_ai_ingestion_mvp.ingestion` schema on `rddb` through a restricted runtime role. Its verified lifecycle is `ingestion record → credibility disposition → explicit certification → append-only certification audit → deterministic Certified Knowledge projection`. Only `certified` records are eligible for the projection; each projection retains source fingerprint, certification-event reference, actor, timestamp, policy version, and provenance. This is not a public service, production deployment, Qdrant integration, or AI/RAG integration.

The same loopback-only service now has verified deterministic retrieval over Certified Knowledge only. It returns the knowledge identifier/text plus source fingerprint and certification provenance, with a bounded query and stable ordering. It does not expose canonical raw ingestion records or invoke an embedding model, Qdrant, Dify, or an AI model.

## Verified Certified AI/RAG Vertical Slice — 2026-08-08
The existing Dify API runtime on `rdapp` privately consumes the controlled Certified Knowledge retrieval service across an internal Docker network. It uses its already configured generation and embedding capabilities to derive vectors for the isolated `enterprise_ai_certified_knowledge_v1` collection on the existing Qdrant service at `rdvector`. The index is derived only from Certified Knowledge; PostgreSQL remains the authority for certification and provenance.

The answer path embeds the query, searches only that isolated collection, applies a minimum evidence score, invokes Dify generation only when eligible knowledge is retrieved, and returns source/certification provenance with the answer. No eligible result yields `insufficient_certified_evidence` without generation. The path is private and synthetic-only; it creates no public endpoint and does not make Qdrant, Dify, or PostgreSQL public.

## Observed Service Placement — 2026-08-06
The sanitized service inventory verifies running PostgreSQL and Redis containers on `rddb`; Qdrant on `rdvector`; and Dify `1.16.0` API/web components, Nginx, Redis, n8n, a Dify SSRF proxy, and two unclassified containers on `rdapp`. `rdautomation` and `rdmonitor` had no running containers at collection time.

The observed n8n placement on `rdapp` is accepted for the current Enterprise AI MVP architecture. `rdapp` may host Dify runtime components, Nginx, n8n, and supporting application-runtime components. `rdautomation` remains reserved for future scale-out or isolation; no migration is authorized or required now.

## Dify Runtime Reachability — 2026-08-08
Three running Dify API/worker components on `rdapp` resolved the declared `rddb` and `rdvector` names and completed TCP handshakes to PostgreSQL, Redis, Qdrant HTTP, and Qdrant gRPC endpoints. The local entrypoint returned HTTP `307` to a status-only request.

This verifies network reachability from Dify runtime containers only. It does not prove Dify configuration targets, authentication, data access, or that the external services are the actively used backends.

## Active Backend Connection Evidence — 2026-08-08
Sampled Dify API/worker runtime processes had active TCP connections to the declared PostgreSQL and Redis endpoints on `rddb`. No active Qdrant connection was observed in the same sample. This is direct runtime evidence for the `rddb` endpoints, while Qdrant usage remains unknown; it is not an architecture decision or a conclusion about configured backend targets.

No active sampled Dify connection to the Redis container on `rdapp` was observed. This does not prove local Redis is unused, but it does not add competing active-connection evidence to the observed `rddb` Redis usage.

## Declared Backend Health — 2026-08-08
PostgreSQL readiness on `rddb` is verified with reported version `16.14`. Redis on `rddb` required authentication for the safe unauthenticated PING probe; it reported version `7.4.9`. Qdrant on `rdvector` returned HTTP `200` to a local status-only health request; its reported version remains unknown. These findings do not expose credentials or establish data-level readiness.

## Critical Listener Evidence — 2026-08-08
Sanitized `ss -lnt` evidence confirmed local listeners for declared PostgreSQL, Redis, Qdrant HTTP/gRPC, and the `rdapp` HTTP entrypoint. Bind addresses and raw listener output were not retained; this does not establish firewall exposure, TLS, or external reachability.
