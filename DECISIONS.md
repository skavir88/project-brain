# Decisions

## DEC-001 — Enterprise AI Is the Sole Project Identity
Status: Accepted

The Project Brain documents Enterprise AI, titled Enterprise Data Platform & Data Credibility Assurance. Previous test-project identity and claims are removed.

## DEC-002 — Stage 0 Is Evidence-First
Status: Accepted

No infrastructure condition is `verified` without reproducible command output. Missing access remains `unknown` or `blocked`.

## DEC-003 — Local, Read-Only Baseline Collection
Status: Accepted

Baseline evidence is collected on each Ubuntu host by a local script. The collector performs no installation, configuration, restart, deletion, inspection of secrets, or Docker inspection.

## DEC-004 — Raw Evidence Is Not Versioned by Default
Status: Accepted

Collector output is written outside Git by default. Only reviewed and sanitized evidence may be incorporated later under an explicitly scoped task.

## DEC-005 — External Dify Backends
Status: Accepted

PostgreSQL, Redis, and Qdrant are intended as external Dify backends. Duplicating them within an application stack requires a documented architecture decision.

## DEC-006 — SSH Trust and Authentication Bootstrap
Status: Accepted

Each declared host uses a dedicated local Enterprise AI SSH key and a stable alias. Host-key verification remains enabled and initial host keys are recorded locally only after review. Passwords are never sent through command arguments, stored in the repository, or placed in project documentation. Non-interactive operations are blocked until the authorized operator installs the project public key on each host.

## DEC-007 — Scoped Autonomous Implementation Authority
Status: Accepted

The Autonomous Implementation Agent may execute the active atomic task on declared hosts when its scope, rollback, and verification are explicit. It must run preflight, make backups before important changes, sanitize evidence, and update Project Brain. High-risk destructive, SSH, network, reboot, credential, broad-sudo, or public-exposure operations remain approval-gated.

## DEC-008 — Accept n8n Placement on rdapp for the MVP
Status: Accepted

n8n observed on `rdapp` is accepted as part of the current Enterprise AI MVP application/runtime placement. `rdapp` may host Dify runtime components, Nginx, n8n, and supporting application-runtime components. `rdautomation` is reserved for future automation/workflow scale-out or isolation. This does not require n8n to remain on `rdapp` permanently; a future migration requires evidence of a concrete need and a separately approved architecture change. No n8n migration, restart, reconfiguration, or runtime change is authorized by this decision.

## DEC-009 — Initial MVP Data Credibility Gate
Status: Accepted

For local synthetic records only, structural validity and duplicate absence are necessary but not sufficient for credibility eligibility. A record may be a `certification_candidate` only after structural validation, duplicate control, and the deterministic quality gate pass; this state is eligible for later certification and is never final `certified` status.

The minimum gate requires a usable `provenance.source_reference`. Its absence routes an otherwise processable record to `human_review_required` with `provenance_insufficient`. If `observed_at` is present, it must be an ISO-8601 timestamp with timezone and must not be in the future; failure is `rejected` with `temporal_validity_failed`. If `payload.source_id` is present, it must match canonical `source_id`; failure is `rejected` with `consistency_check_failed`.

This decision authorizes no persistence, final certification, LLM judgment, quality scoring, external integration, real organizational data, or remote deployment. The resulting disposition and reason codes are transient local responses only.

## DEC-010 — Isolated PostgreSQL Persistence for the MVP
Status: Accepted

The existing PostgreSQL service on `rddb` is the approved isolated persistence target for the ingestion/data-credibility MVP. The logical database is `enterprise_ai_ingestion_mvp`, its application schema is `ingestion`, and its runtime role is `enterprise_ai_ingestion_runtime`. Runtime secrets are stored only outside Git at the approved `/etc/enterprise-ai/secrets/ingestion-db.env` reference. This decision does not authorize final certification, unrelated database changes, or reuse of Dify objects.

## DEC-011 — Controlled Synthetic Certification Lifecycle
Status: Accepted

Final certification is an explicit, actor-driven operation for synthetic MVP records only. It atomically permits only `certification_candidate` to `certified`, persists the timestamp, actor identifier, and policy version, and appends one durable audit event. Repeated certification of an already certified record returns `already_certified`; other lifecycle states are not eligible. No automatic certification, revocation, or change to the Stage 1 credibility-gate semantics is authorized.

## DEC-012 — Certified Knowledge Projection Boundary
Status: Accepted

Certified Knowledge is a deterministic, durable projection of persisted `certified` records only. Each projection preserves the source fingerprint, certification audit-event reference, actor, timestamp, policy version, and provenance needed for traceability. The projection is idempotent by source fingerprint and excludes candidates, human-review records, rejected records, and raw-record representation. Embeddings, Qdrant, Dify, and AI/RAG consumption remain separate tasks.

## DEC-013 — First Certified AI/RAG Vertical Slice
Status: Accepted

The existing Dify deployment on `rdapp` is the sole AI/RAG runtime for the first synthetic vertical slice. It uses existing valid `openai_api_compatible` generation and embedding capabilities without exposing provider credentials. The existing Qdrant service on `rdvector` owns the additive, isolated `enterprise_ai_certified_knowledge_v1` derived index; PostgreSQL remains authoritative for eligibility, certification, audit, and provenance.

Dify consumes only the private Controlled Certified Knowledge retrieval path. The derived index is populated only from that path and carries knowledge identity, source identity/fingerprint, certification metadata, and provenance. A Qdrant vector never establishes certification. The answer wrapper returns structured provenance and deterministically returns `insufficient_certified_evidence` when no result reaches the minimum score (`0.70`). No public endpoint, real data, provider credential, new Dify instance, or unrelated Qdrant collection is authorized by this decision.

## DEC-014 — First Real Business Pilot
Status: Accepted

The first real Enterprise AI pilot is limited to one explicitly approved, read-only organizational file-share folder representing one bounded project dataset. Folder membership never establishes credibility or certification. Files must pass the existing ingestion, quality, human-review, certification, Certified Knowledge, retrieval, Qdrant, and Dify boundaries before contributing to an executive answer.

The pilot answers the CEO question, “What is the latest status of this project?”, only with certified evidence and structured provenance. “Latest” derives from controlled source/provenance and certification metadata, never filesystem ordering alone. Conflicts remain visible or route through the existing review policy. No automatic certification, whole-share crawl, write access, public exposure, production UI, or organizational-wide RBAC is authorized. Real file content may be accessed only after the exact bounded path and read-only access are verified by ST1-013.
