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

## DEC-015 — Initial Real-Content Subset
Status: Accepted

The initial real-content pilot subset is the user-selected source alias `status_candidate_b`. Its fixed boundary is 19 documents: 18 PDF and 1 XLSX, with an aggregate metadata size of 23,606,611 bytes. Only that bounded subset may be read, and only by read-only extractors for the approved PDF/XLSX formats. The source path and document names remain local operational data and are never recorded in versioned evidence.

The selection is a scope boundary, not evidence that the folder is authoritative, current, credible, or certified. Extracted facts remain unreviewed and uncertified. No real content may enter PostgreSQL, Certified Knowledge, Qdrant, Dify, or any external AI service until the existing human-review and explicit-certification path is completed.

## DEC-016 — ST1-019 Status-Oriented Corpus Selection
Status: Accepted

The user explicitly selected `status_oriented_candidate_1` for one read-only, local extraction pass. Its fixed discovery boundary is 18 entries: seven PDF, four DOCX, and seven XLSX, totaling 20,923,849 metadata bytes. The runtime-local locator is the only permissible source locator; no broad SMB rediscovery is authorized.

This selection is neither an authority determination nor evidence of correctness, recency, completeness, credibility, or “latest-status” semantics. Filesystem metadata dates are not project-status facts. Extracted organizational material remains local, unreviewed, and uncertified; it must not enter PostgreSQL, Certified Knowledge, Qdrant, Dify, or an external model before the approved human-review and certification path.

## DEC-017 — ST1-022 Internally Dated Status-Source Selection
Status: Accepted

`status_oriented_candidate_3` is selected for one bounded, read-only local extraction pass because its workbook content contains a recurring daily-status structure, internal reporting dates, a project identifier, and activity/issue rows with cell provenance. Its fixed discovery signature is ten XLSX workbooks totaling 1,163,077 metadata bytes; raw locators remain only in local runtime state.

The selection is evidence of source relevance signals only. It does not establish approval authority, organization-wide completeness, recency beyond the extracted internal reporting period, factual correctness, or executive “latest-status” semantics. All extracted real information remains unreviewed and uncertified; no platform persistence, AI/RAG use, or automatic certification is authorized.
