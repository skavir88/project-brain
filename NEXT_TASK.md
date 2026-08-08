# Next Task

## Metadata
- Task ID: ST1-006
- Stage: Stage 1 — Product Implementation
- Status: Blocked — durable persistence target and credential-creation approval required
- Owner: Product/architecture owner

## Objective
Approve the smallest durable PostgreSQL persistence target and scoped runtime credential required to extend the verified local synthetic credibility gate into a persistent MVP vertical slice.

## Rationale
The local flow now reaches `Ingestion → Structural Validation → Normalization → Deduplication → Credibility Gate → certification_candidate`. The next critical-path component is durable persistence for canonical records, fingerprints, dispositions, and later certification workflow. Selecting a database target and creating a runtime credential are material persistent/credential changes and cannot be inferred safely.

## Decision Required
- Confirm whether the declared PostgreSQL service on `rddb` is the approved MVP persistence target for this ingestion service.
- Approve creation of a new, isolated non-production database/schema and least-privilege runtime role for the MVP; do not reuse or disclose an existing credential.
- Approve a runtime secret reference outside Git (for example, `/etc/enterprise-ai/secrets/ingestion-db.env`) with restricted permissions.
- Confirm that a new migration may create tables/indexes only and must not alter or delete existing data.

## Scope After Approval
- Use only `enterprise-ai-rddb` and `enterprise-ai-rdapp` aliases from `inventory/hosts.yaml`.
- Perform documented remote preflight, inspect only safe PostgreSQL service identity/health metadata, and create timestamped backups before configuration or migration changes.
- Create only the approved new database/schema/role, a local Git-safe migration artifact, and a root-owned runtime secret file outside Git.
- Deploy the local ingestion service to `rdapp` only after the migration and connection verification succeed; no public exposure.

## Out of Scope
- Existing database/schema/table alteration or deletion, data deletion, credential reuse or disclosure, public exposure, firewall/network changes, Dify/n8n/Qdrant changes, final certification, real organizational data, destructive migration, or production claim.

## Files to Inspect
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `CURRENT_STATE.md`
- `inventory/hosts.yaml`
- `implementation/ingestion-service/`
- `evidence/sanitized/2026-08-08-st1-005-data-credibility-gate.json`

## Files Allowed to Change After Approval
- `implementation/ingestion-service/`
- `deploy/`
- `migrations/`
- `CURRENT_STATE.md`
- `MASTER_PLAN.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `evidence/sanitized/`

## Verification Commands After Approval
```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rddb '<read-only-preflight>'
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdapp '<read-only-preflight>'
git diff --check
```

## Evidence Required
- Explicit target/credential/migration approval.
- Sanitized remote preflight, database creation/migration, restricted-secret-file metadata, and application-to-PostgreSQL connection results.

## Rollback
No persistent change is authorized before approval. After approval, use only an approved rollback migration for newly created isolated objects; never delete or alter pre-existing objects without a separate destructive-operation approval.

## Definition of Done
- The required target and credential approval is recorded in `DECISIONS.md`.
- The next atomic implementation task contains exact non-destructive database and deployment scope.
- No remote persistent or credential change occurs before explicit approval.
