# Next Task

## Metadata
- Task ID: ST1-068
- Stage: Stage 1 — Product Implementation
- Status: Awaiting minimum business identity and activation decisions
- Owner: CEO / designated governance authority

## Objective
Obtain the minimum reusable business evidence required to activate the first
real, narrowly scoped Project Controls delegation. This task does not approve
or certify any organizational record.

## Rationale
ST1-067 approved the pilot policy model but deliberately recorded no verified
CEO role, Project Controls/PMO role, or authoritative source. The append-only
bootstrap lifecycle prevents inactive proposals from conferring authority.

## Preconditions
- Review `docs/SDAS_GOVERNANCE_BOOTSTRAP.md` and answer the four plain-language
  business questions below. An answer of `unknown` keeps the proposal inactive.

## Scope
- Validate only supplied role/source/reporting-time/activation evidence.
- Append lifecycle events only after every required identity and source check
  passes exactly.
- Re-evaluate ST1-061 only as a regression test; never reacquire it.

## Out of Scope
- Per-record certification, automatic certification, currentness/reliance
  promotion, new source boundaries, credentials, provider/model changes, and
  destructive operations.

## Minimum Business Decisions
1. **Governance role:** Which durable internal role is authorized to approve
   this pilot policy? Recommended: CEO or formally delegated governance office.
   Approval lets us verify a role identity; unknown keeps the policy pending.
2. **Accountable role:** Which Project Controls/PMO role owns recurring project
   progress/status reports? Recommended: the role named in your document-control
   process. Approval enables role verification, not record certification.
3. **Source and report convention:** Which registered system/report class is
   owned by that role, and where is its reporting period recorded? Recommended:
   one recurring controlled report/workbook and its approved header/period
   field. Unknown keeps real records in Human Review.
4. **Activation:** After the prior three items are evidenced, may this exact
   LOW-risk scope become active? Recommended: yes, with the ST1-067 exclusions
   unchanged. Rejection leaves it inactive; approval never enables automatic
   certification.

## Files to Inspect
- `docs/SDAS_GOVERNANCE_BOOTSTRAP.md`
- `docs/ST1_067_PROPOSED_CEO_GOVERNANCE_DELEGATION.md`
- `DECISIONS.md`
- `CURRENT_STATE.md`

## Files Allowed to Change
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md` when an explicit governance decision is accepted
- `NEXT_TASK.md`
- Sanitized evidence and append-only lifecycle events after all preconditions
  are verified

## Execution Steps
1. Receive the four business answers and their non-secret evidence references.
2. Verify role, source ownership, report class, business-time convention, and
   exact scope against the bootstrap requirements.
3. Append `IDENTITY_VERIFIED`, `SOURCE_VERIFIED`, and `ACTIVE` only when each
   prior condition is independently evidenced; otherwise preserve the pending
   state.
4. Run exact-scope policy simulation and stop before certification of the first
   real `policy_automatic` record.

## Acceptance Criteria
- Unverified identity/source evidence cannot activate authority.
- Every lifecycle transition is append-only and attributable.
- ST1-061 remains `human_required` absent independently new authority and
  business-time evidence.
- No real record is certified, current, reliance-eligible, or insured.

## Verification Commands
```powershell
python scripts/validate_st1_067_governance_proposal.py
python scripts/verify_st1_067_governance_bootstrap.py
python scripts/verify_st1_067_bootstrap_policy_gate.py
git diff --check
```

## Evidence Required
- Sanitized role/source/time/activation validation results and lifecycle event
  identifiers only; no organizational content, locator, or secret.

## Rollback
- Append revocation/supersession/expiry/rejection events only; never delete or
  overwrite a lifecycle event.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `DECISIONS.md` when required
- `NEXT_TASK.md`
