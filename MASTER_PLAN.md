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

## Later Stages
Future work may implement ingestion, validation, normalization, quality scoring, HITL, lineage, certified knowledge, RAG/AI services, automation, and observability. Scope, design, and readiness criteria for later stages must be approved explicitly; they are not established by this document.
