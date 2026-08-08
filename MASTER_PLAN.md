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

ST1-001 verified a local health-only ingestion-service skeleton, Docker Desktop with the WSL2 backend, and successful Docker Compose configuration validation. ST1-002 verified the first local synthetic `Ingestion → Structural Validation` slice without persistence or remote deployment. ST1-003 verified deterministic canonicalization and fingerprinting. ST1-004 verified a process-local duplicate gate that clears on restart. ST1-005 verified the approved deterministic credibility gate and transient candidate/review/rejection dispositions without final certification. The next critical-path step is durable persistence, which requires an explicit target and credential-creation approval.

## Later Stages
Future work may implement ingestion, validation, normalization, quality scoring, HITL, lineage, certified knowledge, RAG/AI services, automation, and observability. Scope, design, and readiness criteria for later stages must be approved explicitly; they are not established by this document.
