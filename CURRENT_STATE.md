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
- ST1-007 certification lifecycle is verified for synthetic data: only one of concurrent certification requests succeeds (`200`/`409`), repeated certification is `already_certified`, review/rejected records are ineligible, malformed actor requests return `400`, the timestamp/actor/policy `st1-007-v1` and a single append-only audit event persist, restart survival is verified, and the runtime role has no DELETE privilege. Evidence: `evidence/sanitized/2026-08-08-st1-007-certification-lifecycle.json`.
- ST1-008 Certified Knowledge projection is verified for synthetic data. The additive projection is deterministic and durable: three certified records yielded three projection rows; candidate, review, and rejected records yielded zero; projection provenance matches its certified source/audit event; an immediate repeat inserted zero rows; and the count remained three after application restart. Evidence: `evidence/sanitized/2026-08-08-st1-008-certified-knowledge-projection.json`.
- ST1-009 deterministic Certified Knowledge retrieval is verified for synthetic data through the loopback-only ingestion service. It returns three Certified Knowledge items in stable order with only knowledge and certification/source provenance fields; a no-match query returns `200`/zero results, an overlong query returns `400 invalid_query`, repeated calls match, and the behavior survives restart. Raw ingestion records and non-certified lifecycle states are not returned. Evidence: `evidence/sanitized/2026-08-08-st1-009-certified-knowledge-retrieval.json`.
- ST1-010/ST1-011 first Certified AI/RAG vertical slice is verified for synthetic data. Existing Dify on `rdapp` used configured `openai_api_compatible/gpt-4o` generation and `text-embedding-3-large` embeddings; the derived isolated Qdrant collection on `rdvector` contains exactly the three controlled Certified Knowledge items. The mixed-state dataset retains four candidates, three review records, and three rejected records, while no non-certified item enters Certified Knowledge or Qdrant. A grounded answer returned structured provenance; an unrelated query returned `insufficient_certified_evidence` without LLM generation. Evidence: `evidence/sanitized/2026-08-08-st1-010-certified-ai-rag-vertical-slice.json`.
- The ingestion service under `implementation/ingestion-service/` is deployed loopback-only on `rdapp` for synthetic Stage 1 testing and persists only to the isolated MVP PostgreSQL database/schema on `rddb` using a restricted runtime role. It has no public endpoint, real organizational data, Qdrant, Dify, or AI/RAG integration.
- The local service health contract is `verified` on 2026-08-08: `GET /health` returned HTTP `200` and the expected non-sensitive service/status fields. Evidence is `evidence/sanitized/2026-08-08-st1-001-local-ingestion-skeleton.json`.
- Docker Desktop with the WSL2 backend is `verified` as operational for local development on 2026-08-08: Docker Client/Server and Compose commands exited `0` in the `desktop-linux` context. The selected context uses a local Windows named pipe, not an insecure Docker TCP endpoint. The exact Compose configuration validation for the local ingestion skeleton also exited `0`; evidence is `evidence/sanitized/2026-08-08-st1-001-docker-compose-validation.json`.
- The first local `Ingestion → Structural Validation` slice is `verified` in `evidence/sanitized/2026-08-08-st1-002-synthetic-intake-validation.json`: `POST /v1/records` returned `202` for a valid synthetic record and `422` with machine-readable errors for an invalid record. The Compose service built, ran only through loopback, and was stopped after testing. No record persistence or external backend behavior exists.
- Deterministic identifier canonicalization and content fingerprinting are `verified` in `evidence/sanitized/2026-08-08-st1-003-canonicalization-fingerprint.json`: equivalent synthetic records produced the same SHA-256 fingerprint, while invalid records continued to return `422` without a fingerprint. No deduplication state or persistence exists.
- A process-local synthetic duplicate gate is `verified` in `evidence/sanitized/2026-08-08-st1-004-process-local-duplicate-gate.json`: the first valid fingerprint returned `202`, an equivalent repeat returned `409`, invalid input remained `422`, and a controlled service restart cleared duplicate state. This is a demonstration only; it is not durable deduplication, lineage, audit, quality scoring, or certification.
- The approved initial MVP Data Credibility Gate is `verified` in `evidence/sanitized/2026-08-08-st1-005-data-credibility-gate.json`. A valid unique synthetic record with usable provenance returned `certification_candidate`; insufficient provenance returned `human_review_required`; future supplied temporal metadata returned deterministic `rejected`; structural failure and duplicates retained `422`/`409` with machine-readable rejection codes. `certification_candidate` is not final certification and no result is persisted.
- ST1-006 durable PostgreSQL persistence is verified on `rddb` for synthetic data only. The isolated database `enterprise_ai_ingestion_mvp`, schema `ingestion`, and least-privilege runtime role exist; the runtime secret is outside Git at `/etc/enterprise-ai/secrets/ingestion-db.env` on `rddb` and `rdapp` with mode `600`. Candidate, review, and rejection dispositions persist; duplicate detection survives application restart. Evidence: `evidence/sanitized/2026-08-08-st1-006-durable-persistence.json`.

## Next Operational Target
The synthetic Certified AI/RAG vertical slice is complete. DEC-014 approves one bounded real-data pilot only after ST1-013 verifies the exact read-only folder path, access, inventory metadata, and privacy constraints. Public exposure and production readiness remain unapproved.

## ST1-013 Real File-Share Pilot Preflight
- SMB port reachability and read-only enumeration of the approved pilot folder are `verified` through the existing local Windows SMB session. No credential was persisted, no file content was read, and no write was attempted.
- The metadata-only inventory is `partial`: at least 53,441 files, 14,145 directories, and 255,633,940,993 bytes were observed. 422 directories produced transient metadata errors (`ObjectNotFound=149`, `ReadError=273`); all counts are lower bounds and do not establish a complete inventory.
- The dataset includes office documents and also archives, CAD files, executables, a mailstore, project-planning formats, videos, temporary/system artifacts, and shortcuts. No file content or filename/path is retained in evidence. Filesystem timestamps are not authoritative “latest” evidence. Evidence: `evidence/sanitized/2026-08-08-st1-013-real-file-share-pilot-preflight.json`.
- ST1-014 metadata-only discovery found 55 bounded allowlisted candidate subsets but no safe automatic selection. Three non-sensitive status-reporting candidates are summarized in `evidence/sanitized/2026-08-08-st1-014-subset-discovery.json`; selecting one can change the business meaning of “latest status,” so content access remains blocked pending user selection.

## ST1-014 Selected Real-Content Extraction
- DEC-015 selected `status_candidate_b` as the bounded real-content source: 19 documents (18 PDF, 1 XLSX), aggregate metadata size 23,606,611 bytes. This is a scope boundary only, not an authority or certification claim.
- Read-only local extraction completed for 18 documents. One XLSX failed deterministic OOXML extraction with `BadZipFile`; therefore extraction is `partial` and the failed source remains unresolved. No source file was modified.
- The successful extraction produced 12 unique content fingerprints across 18 records, six duplicate-fingerprint groups, and three deterministic, redacted status-review items from one document. Each item has required provenance fields, a canonical comparison fingerprint, duplicate-source count, and `human_review_required` disposition. A possible phone-number category was detected once. Raw text, source references, and the local review package remain outside Git.
- No LLM, Dify, Qdrant, PostgreSQL persistence, Certified Knowledge projection, or certification processed real organizational content. Evidence: `evidence/sanitized/2026-08-08-st1-014-real-content-extraction.json`.

## ST1-015 XLSX Diagnosis and Human-Review Preparation
- The prior XLSX result is `BadZipFile`, but this is not classified as corruption, format mismatch, or encryption: the approved SMB source was unavailable or not enumerable in the current Windows session (zero active SMB connections), so signature and actual format remain `unknown`.
- The three existing real review candidates are complete as a local, redacted human-review package. All include a stable identifier, proposed claim, local source reference/location, source timestamp metadata, fingerprint, supporting redacted excerpt, review reason, uncertainty, and the permitted dispositions `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT`.
- Every candidate remains `human_review_required` and `unreviewed_not_certified`. The pilot corpus is incomplete pending XLSX diagnosis; no claim is made that the missing document is or is not material. Evidence: `evidence/sanitized/2026-08-08-st1-015-review-preparation.json`.
- A resumed ST1-015 source check verified that the approved SMB share root is reachable. Resolving the exact selected subset with metadata-only criteria timed out after an ancestor-aware traversal of 604 seconds, so the XLSX signature and actual format remain `unknown`; no source content outside the bounded subset was read and no format inference was made.

## ST1-016 Human Review and Bounded Evidence Improvement
- The designated human reviewer explicitly decided `NEEDS_MORE_EVIDENCE` for all three first-pass real candidates. Three local-only attributed review events were recorded; zero candidates are approved for certification and no certification was executed.
- A deterministic, page-level pass over the already extracted text of the approved 18 PDFs found 102 PDF pages but only nine text-bearing pages. After removing title signals, semantic duplicates, and false-positive material text, only two substantive financial observations remained. Neither has a content-supported reporting/effective date, and no physical-progress, schedule/milestone, delay/risk/issue/action, or management-decision evidence was found.
- This proves the existing text extraction is insufficient for the CEO project-status question; it does not prove the 18 source PDFs themselves are empty, because scanned pages need local OCR. The current local extraction output did not retain the selected-subset relative locator, so the source documents cannot be safely re-opened without a prohibited broad rediscovery crawl. The extractor is now corrected to retain that locator and selection signature in local runtime output only on future runs.
- The unresolved XLSX remains an explicit coverage limitation. No real content was persisted to PostgreSQL, Certified Knowledge, Qdrant, Dify, or an external model. Evidence: `evidence/sanitized/2026-08-09-st1-016-human-review-and-evidence-improvement.json`.

## ST1-017 Targeted Locator Recovery
- Two bounded metadata-only anchor searches ran only under the newly supplied approved pilot root: exact filename and Unicode-normalized filename. Both returned zero matches, so no subset locator was recovered and no document content was opened.
- A subsequent path audit verified that the executed root is a valid UNC path with exactly two leading backslashes and that `Test-Path` succeeds. The earlier zero-match result is therefore valid; any single-backslash rendering was display-only.
- Operator-provided candidate roots then enabled a bounded descendant metadata comparison. Exactly one subset matched the approved signature; raw relative locators for all 19 entries were retained only in local runtime state.
- The selected XLSX has a non-OOXML signature and was observed as a temporary-lock or unstable entry. It was not parsed and is not usable as business content. The 18 PDFs were processed only locally: 84 pages, 82 text-bearing pages, and 75 Persian-Tesseract OCR pages with zero extraction failures.
- OCR added no substantive project-status claim. The resulting local Human Review package retains only two non-date-qualified financial observations; it has no content-supported report date, physical progress, schedule, delay, risk, action, management decision, or status statement. The selected subset therefore cannot support the CEO project-status question. No real content was certified or sent to a platform service. Evidence: `evidence/sanitized/2026-08-09-st1-017-bounded-ocr-and-review.json`.
- Per the approved constraint, no further broad recursive discovery is being attempted. The operator must provide the containing folder path found through local Explorer/PowerShell search before the validated 18 PDFs can be re-opened for local Persian OCR. Evidence: `evidence/sanitized/2026-08-09-st1-017-locator-recovery.json`.
