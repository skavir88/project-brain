# Next Task

## Metadata
- Task ID: ST1-034
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Approval
- Owner: Project owner / credential custodian

## Objective
Authorize one bounded remediation path for the dedicated embedding capability so the verified ST1-032 Certified Knowledge can be indexed and retrieved without changing trusted certification data or retrieval policy.

## Rationale
ST1-033 proved that the failure occurs before Qdrant, while Dify/plugin dispatch, provider network reachability, Qdrant, and generation are healthy. The embedding model is registered and has a credential reference, but read-only evidence cannot distinguish an upstream embedding API fault from credential validity, quota, or model-availability conditions.

## Preconditions
- `evidence/sanitized/2026-08-09-st1-033-embedding-provider-diagnostic.json` is reviewed.
- Existing certification, audit, Certified Knowledge, Qdrant collection, and `0.70` threshold remain unchanged.
- No credential value has been exposed or copied.

## Required Approval
Choose exactly one bounded path:

1. **Provider recovery** — wait for/provider-side confirmation that the existing embedding endpoint/model is healthy, then re-run ST1-033 unchanged.
2. **Interactive credential validation/replacement** — authorize an operator to enter a replacement credential through the existing Dify secret-entry UI for the existing embedding model only. The secret must never enter chat, command arguments, Git, logs, or evidence.
3. **Model/provider change review** — request a separate architecture/data-compatibility decision identifying the proposed already-configured compatible embedding model, vector dimension, and required re-index plan.

## Scope
- Decision and, only after approval, the single selected remediation path.
- Preserve all existing trusted data and policy boundaries.

## Out of Scope
- Changing certification/audit/Certified Knowledge records; deleting Qdrant data; reducing retrieval threshold; exposing credentials; unrelated provider changes; new real-content extraction.

## Allowed Hosts
- `enterprise-ai-rdapp`
- `enterprise-ai-rdvector` only through the existing controlled index path after approved recovery.

## Verification
After the selected path succeeds:

```bash
ssh -o BatchMode=yes enterprise-ai-rdapp "cat /opt/enterprise-ai/dify-rag-bridge/run_certified_rag.py | docker exec -i dify-api python3 - index"
```

- Verify unchanged `0.70` threshold, idempotent ST1-032 indexing, end-to-end provenance, source-attributed reporting period, and non-currentness boundary.

## Evidence Requirements
- Sanitized selected-path outcome only.
- No secret, encrypted configuration, authorization header, raw source content, or locator.

## Rollback
- Provider recovery: no state change.
- Credential replacement: use the Dify UI to restore the prior secret reference if the operator has retained it; no secret is handled by the agent.
- Model/provider change: do not proceed without a separately approved compatibility and re-index rollback plan.

## Definition of Done
- A single approved path is executed safely.
- Or the approval requirement is explicitly retained with the diagnostic evidence and no trusted state change.
- Project Brain, sanitized evidence, JSON validation, secret scan, legacy scan, and `git diff --check` are updated.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if a model/provider architecture decision is approved
