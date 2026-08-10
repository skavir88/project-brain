# Next Task

## Metadata
- Task ID: ST1-070
- Stage: Stage 1 — Product Implementation
- Status: Awaiting missing controlled organizational evidence
- Owner: Governance office and Project Controls / PMO

## Objective
Obtain the smallest set of real organizational records needed to resolve the
remaining reusable authority gap. No real delegation or claim certification is
in scope.

## Rationale
ST1-069 proved that previously authorized runtime state can provide only a
partial reporting-period signal. It cannot prove governance authority, PMO
responsibility, source ownership/control, or an approved reporting convention.

## Scope
- Inspect only the specific controlled records supplied by the business.
- Validate reusable role/source/reporting-time evidence and update readiness.

## Out of Scope
- Broad SMB discovery, new corpus selection, source reacquisition, automatic
certification, currentness/reliance changes, and per-record review of unchanged evidence.

## Minimum Business Records Needed
1. A controlled organization chart, delegation-of-authority record, governance
   charter, or signed role attestation identifying the role allowed to approve
   this pilot policy.
2. A controlled Project Execution Plan, Project Control Procedure, RACI,
   document-control procedure, or role description identifying the Project
   Controls/PMO role responsible for recurring project reports.
3. One controlled recurring progress/status report/workbook reference plus the
   document-control rule, header, field, or approved metadata that explicitly
   identifies its reporting period and ownership/control.

## Acceptance Criteria
- E1/E2/E3 each become `VERIFIED`, `PARTIAL`, or remain `MISSING` from real,
  traceable evidence; inference is not accepted.
- No real delegation reaches `ACTIVE` until every activation condition passes.
- Exception queue changes only from new evidence.

## Verification Commands
```powershell
python scripts/verify_st1_067_governance_bootstrap.py
git diff --check
```

## Evidence Required
- Sanitized status, fingerprint/reference, scope, and validation result only.
  Do not version organizational contents, personal data, locators, or secrets.

## Rollback
- Append a later supersession/revocation/rejection observation when needed;
  never overwrite or delete prior evidence.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md` if a new decision is required
- `NEXT_TASK.md`
