# Architecture

## Evidence Status
The topology below is **declared** project context. It is not `verified`; no local evidence of reachability, operating system, Docker, services, versions, ports, or configuration has been collected yet.

## Declared Infrastructure Topology
| Host | IP | Declared responsibility |
|---|---:|---|
| `rddb` | `172.20.190.61` | PostgreSQL and durable data services |
| `rdapp` | `172.20.190.62` | Dify, Nginx, and application services |
| `rdvector` | `172.20.190.63` | Qdrant and vector services |
| `rdautomation` | `172.20.190.64` | n8n and workflow automation |
| `rdmonitor` | `172.20.190.65` | Monitoring, logging, and observability |

The declared virtualization platform is VMware; the declared server OS is Ubuntu Linux; the declared primary deployment method is Docker Compose. These are `planned` until evidence is captured.

## Logical Flow
`Data Sources → Ingestion → Structural Validation → Normalization and Deduplication → Quality Gates → Certified Data / Certified Knowledge → AI Services, Automation, Reporting, Audit, and Monitoring`.

Human review/HITL is a branch from Quality Gates for sensitive cases.

## Technical Boundaries
- PostgreSQL, Redis, and Qdrant are intended to be external backends for Dify. They must not be duplicated inside the application stack without a recorded architecture decision.
- Services must be independently deployable and communicate backend-to-backend.
- No claim of production readiness, HA, backup, monitoring, or security hardening is permitted without recorded evidence.
- The need for accessible regional image/package mirrors is `planned` and requires a later decision backed by operational evidence.
