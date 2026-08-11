# Next Task

## Metadata
- Task ID: ST1-071
- Stage: Stage 1 — Product Implementation
- Status: Awaiting signed organizational evidence
- Owner: Governance authority, Project Controls / PMO, and document-control owner

## Objective
Validate and register only the independently signed controlled organizational
evidence needed to resolve E1, E2, and E3; calculate readiness, but do not
activate a real delegation.

## Rationale
ST1-070 provides the append-only evidence workflow and plain-language forms.
The remaining gap is real, attributable organizational confirmation—not a
technical implementation gap.

## Preconditions
- One or more completed forms from `docs/ST1_070_BUSINESS_ATTESTATION_PACK.md`,
  or stronger Tier-A controlled records, are supplied through an approved
  business channel.
- Each signer can be independently identified through controlled organizational
  evidence; self-assertion alone is insufficient.

## Scope
- Inspect only supplied attestation artifacts or Tier-A records.
- Store sanitized references/fingerprints and append-only evidence events.
- Recalculate E1/E2/E3 and the `PASS`/`HUMAN_REQUIRED`/`QUARANTINE` queue.

## Out of Scope
- SMB discovery, source reacquisition, ST1-061 changes, activating a real
  delegation, certification, currentness/reliance changes, or automatic
  certification.

## Files to Inspect
- `docs/ST1_070_BUSINESS_ATTESTATION_PACK.md`
- `docs/SDAS_GOVERNANCE_BOOTSTRAP.md`
- `migrations/021_add_sdas_controlled_attestations.sql`
- Supplied business artifacts only

## Files Allowed to Change
- Sanitized evidence, Project Brain documents, and additive validation scripts
  if needed. No raw organizational artifact enters Git.

## Execution Steps
1. Verify artifact provenance, signer identity, scope, effective period, and
   required fields independently for each supplied A1/A2/A3 record.
2. Append `SUBMITTED`, `IDENTITY_VERIFIED`, and only then `VERIFIED` or a
   terminal event; preserve fingerprints and non-secret references.
3. Recalculate E1/E2/E3 and activation readiness without creating `ACTIVE`.
4. Run lifecycle, JSON, secret, legacy, and diff validation; record sanitized evidence.

## Acceptance Criteria
- Every supplied artifact is `VERIFIED`, `PARTIAL`, or rejected from real,
  traceable evidence—not inference.
- Self-assertion alone cannot pass.
- No real delegation is `ACTIVE` and no certification occurs.

## Verification Commands
```powershell
python scripts/verify_st1_070_attestation_workflow.py
git diff --check
```

## Evidence Required
- Sanitized fingerprint/reference, evidence type, asserted role/source/time
  fact, scope, effective period, verification method, provenance, and status.

## Rollback
- Append `REVOKED`, `SUPERSEDED`, `REJECTED`, or a new correction event; never
  overwrite or delete evidence.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md`, only if a new decision is required
- `NEXT_TASK.md`
