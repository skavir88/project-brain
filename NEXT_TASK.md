# Next Task

## Metadata
- Task ID: ST1-058
- Stage: Stage 1 — Product Implementation
- Status: Awaiting explicit human certification approval
- Owner: Designated human reviewer

## Objective
Obtain one explicit Human Review decision for the native synthetic SDAS test
record that policy automatically prepared as `certification_candidate`.

## Rationale
- SDAS v0.2 native acquisition, transformation, policy decision, and audit path is verified.
- Automatic certification is prohibited. `policy_automatic` is not human approval.

## Allowed Operations
- On explicit `APPROVE`: invoke only the existing controlled certification lifecycle with an explicit human actor, then project/index/consume the synthetic record and verify provenance.

## Forbidden Operations
- Automatic certification, certification of real organizational data, reliance eligibility, currentness/authority upgrade, policy weakening, or public exposure.

## Evidence Requirements
- Exact reviewer disposition, controlled lifecycle result, append-only audit/registration/consumption linkage, and sanitized verification output.

## Rollback
- No destructive rollback; immutable audit evidence remains. Stop before certification if no approval is supplied.

## Definition of Done
- The explicitly approved synthetic record is certified through the existing controlled path, or the decision is recorded as non-approval with no certification.
