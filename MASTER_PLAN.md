# Master Plan

## Stage 0 — Project Discovery, Baseline and Automation Foundation
Status: Complete

Objectives:
- Record the actual infrastructure baseline, host roles, services, versions, ports, dependencies, and unknowns.
- Establish Project Brain governance, configuration/secrets policy, repeatable verification tools, and atomic-task automation workflow.
- Define and verify Stage 0 completion criteria.

Quality gates:
- Every infrastructure claim is classified and evidence-backed when marked `verified`.
- No secrets or unreviewed raw evidence are versioned.
- Verification is command-based, repeatable, readable, and returns meaningful exit codes.
- `NEXT_TASK.md` contains only one atomic, testable task.

### Completion Review — 2026-08-08
Outcome: `ready_for_stage_transition_approval`

The transition gate was explicitly approved on 2026-08-08.

Verified evidence covers the infrastructure baseline, SSH automation, service placement categories, critical listeners, Dify runtime reachability, PostgreSQL/Redis active-connection evidence, verification tooling, Project Brain governance, and the accepted n8n placement. Two `rdapp` containers, Qdrant reported version, Redis unauthenticated readiness, and sampled Qdrant active-use evidence remain known limitations; none blocks starting non-production product implementation. Stage 1 remains outside scope until the transition gate is explicitly approved.

## Stage 1 — Product Implementation
Status: In progress — local runtime and ST1-001 implementation baseline verified.

Objective: deliver the smallest safe, demonstrable vertical slice of the approved product direction without real organizational data or production deployment.

ST1-001 through ST1-005 verified the local synthetic intake, validation, canonicalization, duplicate gate, and deterministic credibility dispositions. ST1-006 added isolated durable PostgreSQL persistence, ST1-007 added controlled certification plus an append-only audit trail, ST1-008 added an idempotent Certified Knowledge projection restricted to certified records, ST1-009 added deterministic retrieval with source/certification provenance, and ST1-010/ST1-011 verified the first private Dify/Qdrant grounded-answer vertical slice. DEC-014 authorizes one bounded real business pilot; ST1-013 must first verify only the selected read-only file-share folder and its metadata constraints.

ST1-013 verified read-only pilot-folder access and a partial metadata inventory. The next gate is intentionally narrow: select a bounded initial document subset and explicit supported-format/extraction allowlist before any real file content is read or ingested.

ST1-014 confirmed that multiple bounded status-reporting subsets satisfy the technical size target. A business selection is required before content reading, because filesystem metadata does not establish which status period is authoritative.

DEC-015 selected `status_candidate_b`; bounded read-only extraction then completed for 18 of 19 documents without platform persistence or AI use. One selected XLSX failed deterministic OOXML extraction (`BadZipFile`), so the real-data corpus is partial and requires a human resolution/review gate before any real record can advance toward certification.

ST1-015 prepared the three successful real candidates for human decision without persisting real data. The XLSX remains unresolved because the approved SMB source was not reachable in the current session; `BadZipFile` is insufficient to infer corruption. The next critical-path gate is human review of the prepared candidates.

ST1-016 recorded `NEEDS_MORE_EVIDENCE` for all three first-pass candidates and confirmed that existing extracted text from the 18 approved PDFs is inadequate for the CEO project-status use case. The practical next step is bounded local OCR only after the exact selected-subset relative locator is recovered; broad share rediscovery is explicitly excluded.

ST1-017 recovered the exact selected subset through operator-provided bounded roots, validated the 19-entry signature, and completed local Persian OCR on all 18 PDFs. OCR did not yield report dates, physical progress, schedule, delay, risk, action, management decision, or status evidence; only two undated financial observations remain. This selected subset cannot answer the CEO project-status question. Selecting any new source requires a new explicit bounded business decision.

ST1-018 performed business-question-driven metadata discovery. Three materially different bounded series require user selection before content access: two planning-oriented series and one explicit project-status spreadsheet series. No new source content was read.

ST1-019 records the user’s selection of `status_oriented_candidate_1` as a bounded, read-only source only. Local deterministic extraction and review preparation may proceed strictly within its 18-file signature; the selection itself establishes neither source authority nor latest-status semantics.

ST1-020 recorded a complete Human Review with zero approvals. ST1-021 then performed a single bounded enrichment pass over the four unresolved sources. It found a visible Change Log row/status snapshot but no populated update date or authority/currentness evidence. The selected corpus is insufficient; the next critical path requires a specifically selected dated, authoritative project-status source rather than further reprocessing.

## Later Stages
Future work may implement ingestion, validation, normalization, quality scoring, HITL, lineage, certified knowledge, RAG/AI services, automation, and observability. Scope, design, and readiness criteria for later stages must be approved explicitly; they are not established by this document.
