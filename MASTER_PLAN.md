# Master Plan

## Stage 0 — Project Discovery, Baseline and Automation Foundation
Status: Active

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
Outcome: `decision_required`

Verified evidence covers the infrastructure baseline, SSH automation, service placement categories, critical listeners, Dify runtime reachability, PostgreSQL/Redis active-connection evidence, verification tooling, and Project Brain governance. Local `rdapp` Redis usage remains unknown after the safe probe, while active external `rddb` Redis usage is observed. Stage 0 cannot transition until the observed n8n placement on `rdapp` versus the declared `rdautomation` responsibility is resolved by an architecture decision. Two `rdapp` containers are recorded as a non-critical known limitation because safe discovery metadata cannot classify them reliably.

## Later Stages
Future work may implement ingestion, validation, normalization, quality scoring, HITL, lineage, certified knowledge, RAG/AI services, automation, and observability. Scope, design, and readiness criteria for later stages must be approved explicitly; they are not established by this document.
