# Next Task

## Metadata
- Task ID: ST1-069
- Stage: Stage 1 — Product Implementation
- Status: Awaiting three reusable real-world evidence confirmations
- Owner: CEO / governance office and Project Controls / PMO

## Objective
Collect only the three reusable business evidence confirmations required to
activate the conditionally approved Maroon LOW-risk delegation. No claim
certification is in scope.

## Scope
- Verify role, source-control, and reporting-period evidence supplied by the
  business; append lifecycle events only after exact validation passes.
- Re-evaluate a record only when genuinely new evidence is supplied.

## Out of Scope
- Automatic certification, currentness/reliance promotion, new source
boundaries, per-record Human Review of unchanged evidence, credentials, and
destructive operations.

## Minimum Business Evidence Needed
1. **Governance role proof:** What approved internal record confirms that the
   CEO/Executive Governance Authority role can approve this pilot policy?
   Recommended evidence: a role mapping or signed governance attestation.
2. **Project Controls role proof:** What approved internal record confirms the
   Project Controls/PMO accountable role for these recurring reports?
   Recommended evidence: document-control responsibility or role mapping.
3. **Controlled report proof:** Which controlled recurring report/workbook
   class belongs to that role, and which header/field/document-control item
   explicitly states its reporting period? Provide its non-secret reference.

## Acceptance Criteria
- Each answer maps to reusable, exact-scope, effective-period evidence.
- Missing evidence leaves the exception queue `HUMAN_REQUIRED`.
- A real delegation cannot become `ACTIVE` without all three confirmations.
- No real record is certified, current, or reliance-eligible.

## Verification Commands
```powershell
python scripts/verify_st1_067_governance_bootstrap.py
git diff --check
```

## Evidence Required
- Sanitized validation result and event identifiers only; no confidential
document content, filename, locator, secret, or personal data.

## Rollback
- Append revocation/supersession/expiry/rejection events only; never overwrite
or delete evidence or lifecycle events.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md` when required
- `NEXT_TASK.md`
