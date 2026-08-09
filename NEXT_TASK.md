# Next Task

## Metadata
- Task ID: ST1-026
- Stage: Stage 1 — Product Implementation
- Status: Ready — Human Review required
- Owner: Designated business reviewer

## Objective
Obtain one explicit Human Review disposition for each of the seven ST1-025 newer-document candidates before any new real claim can enter certification.

## Rationale
ST1-025 found internal workbook issue-date evidence later than the historical certified period and prepared seven substantive candidates. The document date alone does not prove event-effective date, authority, currentness, or factual correctness.

## Preconditions
- `%LOCALAPPDATA%\EnterpriseAI\runtime\st1-025-human-review-package.json` exists with exactly seven candidates.
- DEC-019 and ST1-025 sanitized evidence validate.
- Candidate excerpts and locators remain local-only.

## Scope
- Display each candidate with its ID, claim, internal document date/type, category, affected work package, workbook/sheet/cell provenance, minimal evidence, uncertainty, and duplicate/copy-forward status.
- Record exactly one explicit disposition per candidate: `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT`.
- Produce only a sanitized aggregate decision summary.

## Out of Scope
- Automatic approval, certification, source modification, corpus expansion, platform persistence, Qdrant/Dify use, external-model use, credentials, or public exposure.

## Files to Inspect
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-09-st1-025-currentness-corpus-extraction.json`
- Local-only ST1-025 Human Review package.

## Files Allowed to Change
- `evidence/sanitized/<dated-st1-026-human-review-summary>.json`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required

## Execution Steps
1. Validate the package schema, candidate uniqueness, and complete provenance without publishing raw content.
2. Present all seven review cards and obtain one explicit permitted disposition per card.
3. Persist the attributable decisions locally and verify the complete decision set.
4. Create exactly one next task based on actual outcomes; only approved candidates may become eligible for controlled certification.

## Acceptance Criteria
- Exactly seven explicit, attributable decisions are recorded; none is inferred.
- No candidate is certified or persisted to platform services.
- Sanitized evidence contains aggregate outcomes only and no source content or raw locator.
- One atomic next task follows actual review outcomes.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-09-st1-025-currentness-corpus-extraction.json > /dev/null
git diff --check
```

## Evidence Required
- Local-only review package and decision audit.
- Sanitized aggregate decision summary.

## Rollback
Decision-only; remove only a mistaken local runtime decision artifact. No source or platform state changes occur.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required
