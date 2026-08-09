# Changelog

## 2026-08-08

### Added
- Controlled synthetic certification lifecycle and append-only audit persistence.
- Deterministic, durable Certified Knowledge projection for persisted synthetic certified records only.
- Loopback-only deterministic Certified Knowledge retrieval with source and certification provenance.
- Private synthetic Certified Knowledge → Qdrant → Dify grounded-answer vertical slice with structured provenance and no-evidence behavior.
- DEC-014 and the bounded read-only real business-pilot preflight task.
- Sanitized ST1-013 real file-share metadata-only preflight evidence.
- Sanitized ST1-014 metadata-only real-content subset discovery evidence.
- Sanitized partial real-content extraction evidence for the selected `status_candidate_b` subset.
- Sanitized ST1-015 real human-review preparation evidence.
- Sanitized ST1-016 human-review outcomes and bounded evidence-improvement evidence.
- Sanitized ST1-017 bounded locator recovery, local OCR, XLSX diagnosis, and Human Review summary.
- Sanitized ST1-018 status-oriented metadata discovery evidence.
- Sanitized ST1-019 explicit source-selection and bounded extraction/review summaries.
- Sanitized ST1-020 Human Review decision summary and ST1-021 bounded evidence-enrichment summary.
- Sanitized ST1-022 dated status-source selection and local extraction/review summaries.
- Local-only deterministic PDF/DOCX/XLSX extraction and Human Review packaging utilities for the selected corpus.
- Local-only deterministic extraction and review-package utilities for bounded real content.
- Sanitized ET0-004 runtime connectivity evidence from Dify components on `rdapp` to the declared data backend endpoints.
- Local-only Stage 1 ingestion-service health skeleton and sanitized verification evidence.

### Changed
- Replaced the reachability task with a narrower active-connection-evidence task; no architecture conclusion was made from reachability alone.
- Recorded direct runtime evidence for PostgreSQL/Redis connections and retained Qdrant usage as unknown after no active connection was observed.
- Recorded safe backend health/version evidence and documented unauthenticated Redis and Qdrant-version limitations.
- Recorded observed critical listeners and scheduled a Stage 0 completion review.
- Recorded the Stage 0 Completion Review outcome as further safe evidence work required before the architecture transition gate.
- Recorded sanitized local-Redis active-connection evidence without inferring configuration or non-use.
- Recorded one Dify SSRF proxy classification, two non-critical unclassified containers, and the Stage 0 architecture decision gate.
- Accepted current n8n placement on `rdapp`, closed Stage 0, and prepared the Stage 1 transition approval gate.
- Recorded explicit Stage 1 transition approval; recorded local Docker Compose runtime availability as the remaining ST1-001 blocker without installing software or changing infrastructure.
- Recorded the approved but unsuccessful WSL prerequisite attempt from a non-administrative control-workstation session; no component installation or reboot occurred.
- Verified Docker Desktop/WSL2 local runtime availability and successful ST1-001 Docker Compose configuration validation.
- Added and verified the local synthetic-record intake and structural-validation slice; Compose testing was loopback-only and left the service stopped.
- Added and verified deterministic identifier canonicalization and SHA-256 content fingerprints for accepted synthetic records.
- Added and verified a process-local synthetic duplicate gate that returns a conflict for repeated fingerprints and clears on service restart.
- Recorded DEC-009 and added the verified deterministic MVP Data Credibility Gate with transient candidate, review, and rejection dispositions; no final certification or persistence was introduced.
- Added isolated PostgreSQL-backed durable persistence for synthetic ingestion credibility results and restart-safe duplicate control.
- Verified controlled certification concurrency, invalid-state handling, restart persistence, and least-privilege runtime access.
- Recorded DEC-011 and DEC-012, and verified the Certified Knowledge projection boundary, idempotency, traceability, and restart persistence.
- Added and verified bounded deterministic Certified Knowledge retrieval without raw-record exposure, embeddings, or AI/RAG invocation.
- Recorded DEC-013, added explicit source-record identity to Certified Knowledge, and verified the isolated Qdrant derived index and Dify grounded-answer path.
- Authorized one bounded real business pilot while retaining explicit certification and human-review boundaries.
- Recorded partial read-only pilot-folder inventory, format-risk categories, and the bounded-subset gate before real content access.
- Recorded three non-sensitive status-reporting candidate summaries and stopped before content access pending business selection.
- Recorded DEC-015 and partial read-only extraction: 18 of 19 selected documents succeeded; one XLSX requires format-resolution and human review.
- Recorded the XLSX diagnosis as incomplete due to unavailable current SMB access, rather than inferring corruption from `BadZipFile`; prepared three local redacted candidates for explicit human decisions.
- Recorded three explicit `NEEDS_MORE_EVIDENCE` decisions with zero certification, and corrected the local-only subset-locator design for future extraction runs.
- Validated the operator-provided `status_candidate_b` subset, completed local Persian OCR, and recorded that this corpus cannot support the CEO project-status question.
- Replaced generic bounded-subfolder selection with business-question-driven source discovery and retained human selection where metadata candidates have different business meanings.
- Recorded the explicit selection of `status_oriented_candidate_1`; completed local-only extraction within its fixed boundary and retained all real content, provenance locators, and review excerpts outside Git.
- Recorded zero approvals from ST1-020; excluded 11 rejected educational/external candidates and bounded the final enrichment pass to the four unresolved project-related candidates.
- Selected a recurring internally dated daily-status source, deduplicated copied-forward snapshots, and prepared only time-contextualized row-level candidates for Human Review.
- Recorded DEC-018 and certified 12 explicitly approved real observations as historical, source-attributed claims only; projected only those claims to Certified Knowledge and the isolated Qdrant index.
- Recorded the real-data RAG threshold result: the current `0.70` minimum score preserves `insufficient_certified_evidence` and no historical grounded answer is yet verified.
- Verified a provenance-backed real historical answer with the unchanged `0.70` policy when the query explicitly bound the approved reporting period; current/latest status remains unsupported.
- Added sanitized ST1-024 metadata-only currentness discovery; no new source was selected or opened because the sole later-metadata candidate is planning-labelled and lacks verified reporting-date/authority semantics.
- Recorded DEC-019 and completed bounded, read-only ST1-025 extraction of the approved currentness corpus; prepared seven local-only, provenance-backed Human Review candidates without certification or platform persistence.
- Recorded DEC-020 and certified seven explicitly approved Action Plan observations as source-attributed historical statements; verified projection, isolated Qdrant indexing, provenance-backed RAG, unchanged retrieval threshold, and historical/modality framing.
- Recorded the bounded ST1-027 metadata-only discovery timeout after excluding exhausted corpora; no content was opened and no absence-of-source conclusion was made.

## 2026-08-06

### Added
- Sanitized, machine-readable Stage 0 service inventory for all declared hosts.

### Changed
- Recorded observed service placement and the n8n/`rdautomation` divergence without changing architecture responsibilities.
- Recorded scoped autonomous implementation authority while retaining high-risk approval gates.

## 2026-08-05

### Added
- Non-secret SSH connection metadata for the five declared hosts.
- Local dedicated SSH key, managed aliases, host-key registration, and the SSH bootstrap decision.
- Sanitized Stage 0 baseline summary from all five declared hosts.

### Changed
- Replaced the collector task with the prerequisite public-key authentication task after verified `auth_failed` results on all five hosts.
- Replaced the SSH bootstrap task with a read-only service-inventory task after public-key login and collector execution were verified on all five hosts.

## 2026-08-03

### Changed
- Rebased Project Brain documentation from test content to Enterprise AI Stage 0.
- Replaced unsupported infrastructure claims with declared topology, evidence states, and explicit unknowns.
- Replaced the broad legacy task with the next atomic local baseline-evidence task.
- Aligned supporting prompts and repository guide with the 10-file Project Brain model.

### Added
- Declared host inventory manifest, read-only local baseline collector, and raw-evidence Git exclusion.
- Evidence-first status model and Stage 0 governance decisions.
- Added DEC-021 and a resumable, local-only metadata discovery index for the approved pilot root; recorded aggregate index completion and errors without versioning raw inventory.
- Selected a bounded metadata-ranked currentness candidate, revalidated its availability, and completed local read-only extraction of its stable 32-entry subset. Prepared ten local-only Human Review candidates with a later internal `1402/06` period signal; no certification or platform persistence occurred.
- Recorded ten exact ST1-030 `NEEDS_MORE_EVIDENCE` decisions with zero certification eligibility; added bounded ST1-031 same-workbook schema enrichment and revised local-only review material with verified plan/actual field semantics.
- Recorded DEC-022 and all ten explicit ST1-032 `APPROVE` decisions; atomically certified and projected only the approved weekly Action-Plan observations with source-attributed reporting-week semantics.
- Recorded the downstream embedding-provider runtime blocker during controlled Qdrant/Dify verification. No retrieval threshold or policy was weakened and no credential detail was versioned.
