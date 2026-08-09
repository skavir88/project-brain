# Next Task

## Metadata
- Task ID: ST1-033
- Stage: Stage 1 — Product Implementation
- Status: Blocked
- Owner: Enterprise AI Project Operator

## Objective
Restore the already configured embedding capability sufficiently to complete the pending, unchanged-policy Qdrant index and grounded RAG verification for the ten certified ST1-032 Weekly Action-Plan observations.

## Rationale
Certification, audit persistence, projection, provenance, and least privilege are verified. The only remaining ST1-032 gate is downstream vectorization: the configured embedding runtime returned an error twice. A successful controlled retry must not weaken the approved retrieval policy or alter certification semantics.

## Preconditions
- DEC-022 and `st1-032-source-attributed-v1` exist.
- Exactly ten approved records, audit events, and Certified Knowledge projections are verified.
- The Dify API and plugin runtime are running on declared `rdapp`.
- No credential, provider, network, or Dify configuration change is made without any separately required approval.

## Scope
- Read-only health/diagnostic checks of the existing configured embedding capability.
- One controlled re-index and one period-bound grounded RAG retry using the existing `enterprise_ai_certified_knowledge_v1` collection and unchanged `0.70` threshold, only after embedding health is evidenced.
- Sanitized status/evidence and Project Brain updates.

## Out of Scope
- Credential, provider, Dify, network, firewall, DNS, or model configuration changes; threshold reduction; source discovery/extraction; certification changes; public exposure; deletion of Qdrant points or collections.

## Allowed Hosts
- `enterprise-ai-rdapp`
- `enterprise-ai-rdvector` only through the existing Dify/Qdrant integration path.

## Allowed Operations
- SSH `BatchMode=yes` preflight and read-only logs/status checks.
- Existing controlled bridge invocation after health preflight.
- Repository documentation and aggregate-only sanitized evidence updates.

## Forbidden Operations
- Secret inspection or disclosure; provider credential changes; Qdrant collection deletion; threshold/prompt-policy weakening; new real-content extraction; destructive database operations.

## Inputs
- `implementation/dify-rag-bridge/run_certified_rag.py`
- `evidence/sanitized/2026-08-09-st1-032-weekly-action-plan-certification.json`
- Existing configured Dify embedding and generation capability.

## Execution Steps
1. Verify declared-host preflight and Dify/plugin runtime availability without recording sensitive configuration.
2. Run a minimal existing embedding health invocation; record only exit status/category.
3. If it succeeds, run the existing certified-knowledge index bridge and a period-bound grounded RAG query without changing threshold or policy.
4. Verify provenance fields and historical/source-attributed framing; record only aggregate non-secret results.
5. If the health invocation fails, retain the exact blocked state and do not mutate configuration.

## Verification Commands
```bash
ssh -o BatchMode=yes enterprise-ai-rdapp "docker ps --format '{{.Names}}'"
ssh -o BatchMode=yes enterprise-ai-rdapp "cat /opt/enterprise-ai/dify-rag-bridge/run_certified_rag.py | docker exec -i dify-api python3 - index"
python -m json.tool evidence/sanitized/2026-08-09-st1-032-weekly-action-plan-certification.json > /dev/null
git diff --check
```

## Evidence Requirements
- Sanitized embedding health outcome.
- On success: indexed item count, unchanged threshold, grounded-answer/provenance count and historical framing result.
- On failure: non-secret error category, exit code, and confirmation that no policy/configuration changed.

## Rollback
This task does not alter configuration. A failed health or bridge invocation requires no rollback. Do not delete or recreate an existing Qdrant collection.

## Definition of Done
- Existing embedding health is reproducibly blocked after three controlled attempts without configuration change.
- If healthy, the ten ST1-032 projections are indexed and a provenance-backed source-attributed RAG answer is verified at the unchanged threshold.
- If blocked, the exact non-secret limitation and safe next gate are recorded; no certification, source, or policy boundary is weakened.
- Project Brain, sanitized evidence, JSON validation, secret scan, legacy scan, and `git diff --check` are updated.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if a new decision is required
