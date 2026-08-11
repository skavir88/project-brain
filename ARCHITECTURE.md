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

## Declared Real-Data Pilot Boundary
One explicitly selected, read-only organizational file-share folder may enter the verified trust path only after a bounded preflight. The pilot flow is `file discovery → ingestion → validation/canonicalization/duplicate control → provenance/quality → human review → explicit certification → Certified Knowledge → derived Qdrant index → Dify answer with provenance`. File content, filesystem ordering, and folder membership are never certification evidence by themselves. The exact source path, host access method, and file inventory remain unknown until ST1-013.

ST1-013 verified access through the control workstation only and established a partial metadata inventory. The folder is substantially larger than an initial safe ingestion batch and contains several unsupported/risky format categories. Real content remains outside the platform until an approved bounded subset and allowlist-based extraction policy are selected. No file-share mount is configured on Enterprise AI hosts.

ST1-014 discovered multiple bounded allowlisted status-reporting candidates using names and metadata only. Because a folder/subset selection can alter the executive meaning of “latest status,” no candidate is automatically selected and content remains unread until the architecture owner chooses a source alias.

## Selected Real-Content Boundary — 2026-08-08
DEC-015 selected the local operational alias `status_candidate_b` for the first controlled extraction. The bounded corpus contains 19 documents (18 PDF, 1 XLSX) and 23,606,611 aggregate metadata bytes. Extraction occurs only on the control workstation, read-only, with raw text and source references retained outside Git. It is not a remote deployment, data-store ingestion, or AI/RAG integration.

Eighteen documents were extractable; the selected XLSX raised `BadZipFile` under deterministic OOXML extraction. Real content remains outside PostgreSQL, Certified Knowledge, Qdrant, Dify, and external AI services. The remaining path is human review, explicit certification, and only then controlled projection/retrieval; the unsupported/invalid spreadsheet requires resolution before the subset can be treated as complete.

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

## Sahra Data Assurance Standard v0.1 Pilot Boundary

SDAS v0.1 is an accepted internal experimental, additive assurance-envelope
model around certified records. It is not a replacement for the verified
lifecycle, a statement of legal assurance, or an automatic upgrade of current
pilot data. Its implemented pilot chain
is `Source → Acquisition → identity/timestamp/integrity → extraction and
validation → Human Review → certification/audit → Certified Knowledge →
supersession/revocation state → consumption provenance`.

The proposal separates certified, current, authoritative, and
reliance-eligible data. It preserves the currentness boundary: no historical
or package-specific pilot observation establishes current project status, and
`current_status=insufficient_certified_evidence` remains mandatory. The 49
existing Certified Knowledge records are test evidence only. The back
assessment created 49 `SDAS-1` / `assessed_partial` envelopes without marking
any record current, authoritative, or reliance-eligible. Assurance and
consumption event tables are append-only; their schema is additive and does
not modify the certification lifecycle. SDAS v0.2 still requires a separate
architecture/governance decision. Full proposal and evidence:
`docs/SDAS_V0_1_PROPOSAL.md` and
`evidence/sanitized/2026-08-10-st1-055-sdas-v0-1-pilot.json`.

## Sahra Data Assurance Standard v0.2 Private Pilot

SDAS v0.2 extends the private pilot with append-only source and actor
registries, acquisition and transformation evidence, versioned policy
decisions, Certified Knowledge registration evidence, and post-registration
event evidence. It distinguishes `native`, `corroborated_historical`,
`reconstructed`, `declared_unverified`, and `missing` evidence without
upgrading historical pilot records.

`policy_automatic` is only a preliminary policy decision. It never replaces
explicit Human Review or the existing controlled certification lifecycle.
The only end-to-end native test record was certified after a separately
recorded human `APPROVE`. Supersession, revocation, correction, expiration,
and authority change are modeled as append-only events but remain inactive.
Neither SDAS certification nor registration establishes currentness,
authority, legal assurance, or reliance eligibility.

## ST1-071 Assurance Passport Verification Layer - 2026-08-11

The governance/authority activation path remains externally blocked as
`WAITING_FOR_EXTERNAL_EVIDENCE`. That dependency is not treated as a failed
technical task and does not block unrelated SDAS implementation.

An additive assurance-passport layer now sits above the existing append-only
evidence tables. On `rddb`, the read-only projection
`ingestion.sdas_assurance_passport_projection` reconciles certification,
policy, authority, business-time, acquisition, transformation, assurance,
post-registration, and consumption evidence for one Certified Knowledge item.
On `rdapp`, the loopback-only ingestion service privately exposes
`GET /v1/sdas/passport` as a machine-readable verifier over that projection.
It also exposes `GET /v1/sdas/passports/summary` and
`GET /v1/sdas/passports/exceptions` as deterministic portfolio-level
operator/auditor read models.

This layer does not certify records, activate governance, create currentness,
grant reliance eligibility, or mutate truth. It only explains the recorded
state of a certified datum and deterministically classifies it as
`VERIFIED`, `VERIFIED_WITH_LIMITATIONS`, `HUMAN_REQUIRED`,
`NOT_RELIANCE_ELIGIBLE`, `REVOKED_OR_SUPERSEDED`, or `QUARANTINED`.

ST1-073 adds a sibling pre-certification operating layer. On `rddb`, the
read-only projections `ingestion.sdas_record_policy_routing_projection`,
`ingestion.sdas_record_policy_routing_summary`, and
`ingestion.sdas_record_policy_routing_exception_queue` reconcile immutable
record, policy-decision, assurance-decision, source, and active-delegation
evidence. On `rdapp`, the same loopback-only ingestion service privately
exposes `GET /v1/sdas/routing/summary` and
`GET /v1/sdas/routing/exceptions` for the original ST1-066 operating model:
`policy_automatic`, `human_required`, or `reject_or_quarantine` before
certification.

This routing layer likewise does not bypass governance: if no exact-scope
active delegation matches a record's source/report class, the routing state
remains `human_required` with
`governance_dependency_state=WAITING_FOR_EXTERNAL_EVIDENCE`.

ST1-074 adds a per-record explainability read model on `rddb`:
`ingestion.sdas_record_policy_routing_detail`. On `rdapp`, the loopback-only
ingestion service privately exposes `GET /v1/sdas/routing/detail` for a single
record fingerprint. This route explains the normalized routing outcome, the
dominant reason codes, the key policy/assurance/source signals, and any exact
matched active-delegation evidence needed for operator triage. It remains
read-only and does not certify, activate governance, or mutate routing truth.
