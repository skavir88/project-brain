# Next Task

## Metadata
- Task ID: ST1-008
- Stage: Stage 1 — Product Implementation
- Status: Ready
- Owner: Enterprise AI Project Operator

## Objective
Create and verify a deterministic durable Certified Knowledge projection from persisted `certified` records only, retaining source fingerprint and certification provenance.

## Scope
- Add only isolated PostgreSQL schema objects and local service code needed for projection.
- Exclude `certification_candidate`, `human_review_required`, `rejected`, and raw records.
- Use synthetic data, loopback deployment, additive migration, and no new credentials.

## Out of Scope
- Qdrant, embeddings, RAG, Dify, n8n, UI, external exposure, real data, destructive operations, and changes to certification semantics.

## Acceptance Criteria
- Only persisted `certified` records create knowledge projections.
- Projection retains source fingerprint, certification event provenance, lifecycle/version metadata, and deterministic text representation.
- Non-certified states are excluded by database constraint/query behavior.

## Verification Commands
```bash
git diff --check
```

## Rollback
Use only a rollback scoped to newly created ST1-008 isolated objects if required; do not affect existing objects.
