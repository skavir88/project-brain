# Next Task

## Metadata
- Task ID: ST1-049
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Explicit Credential-Recovery Approval
- Owner: System credential administrator

## Objective
Restore the existing configured embedding credential for the current provider/model without changing provider, model, vector dimensionality, Qdrant collection schema, retrieval threshold, or prior Certified Knowledge.

## Evidence for Gate
- The controlled embedding invocation timed out before Qdrant upsert.
- A controlled `dify-plugin-daemon` restart and one retry did not recover indexing.
- Sanitized diagnostics observed an embedding-related authentication failure but did not inspect credentials or prove root cause.
- The collection remains green at 42 points and dimension 3072; no partial ST1-047 vector write exists.

## Scope After Approval
- Replace or refresh only the existing embedding credential using the approved secure runtime mechanism.
- Do not print, commit, export, or include credential material in logs/evidence.
- Run one controlled embedding invocation, idempotent ST1-047 indexing, Qdrant before/after checks, and a period-bound grounded RAG verification at threshold `0.70`.

## Out of Scope
- Provider/model changes, credential disclosure, vector/schema/threshold changes, deletion, broad retries, modification of ST1-045, or source discovery/extraction.

## Required Approval
Explicit authorization to replace/refresh the existing embedding credential in the secure Dify runtime store. If credential recovery is unavailable or fails, a separate provider/model change decision is required.

## Rollback
- Preserve a secure pre-change credential reference/backup only when the runtime supports it without disclosure. Restore that reference if the controlled validation fails.

## Definition of Done
- Existing credential recovery is verified by a successful controlled embedding invocation, or the exact safe limitation is recorded without provider/model changes.
- Project Brain, sanitized evidence, and exactly one next atomic task are updated.
