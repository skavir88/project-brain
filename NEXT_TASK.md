# Next Task

## Metadata
- Task ID: ST1-030
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Human Review
- Owner: Designated business reviewer

## Objective
Obtain one explicit Human Review disposition for each of the ten local-only, provenance-backed observations extracted from `indexed_currentness_candidate_1` for internal period signal `1402/06`.

## Rationale
The bounded corpus contains substantive planned-versus-actual row-level observations that may extend the verified timeline beyond the source issue date `1402/02/27`. Their document authority, exact column semantics, factual correctness, event-effective dates, and currentness remain unverified; they cannot be certified automatically.

## Preconditions
- The local Human Review package exists outside Git at the control-workstation runtime location.
- Each card presents the minimum necessary content, source alias, local locator, sheet/row provenance, uncertainty, and proposed disposition.
- Review decisions must be explicit and use only `APPROVE`, `REJECT`, `NEEDS_MORE_EVIDENCE`, or `CONFLICT`.

## Scope
- Present exactly the ten ST1-030 review cards to the designated reviewer locally.
- Record the reviewer’s exact dispositions in local review state and sanitized aggregate evidence.
- If and only if items are explicitly approved, prepare one subsequent controlled-certification task preserving source attribution, `1402/06` period semantics, modality, provenance, reviewer/actor, policy, and non-currentness boundary.

## Out of Scope
- Automatic certification; treating plans as completed outcomes; treating `1402/06` as current/latest status; content access outside the selected stable corpus; source modification; external-model use; platform persistence of unapproved claims; retrieval-policy changes.

## Files to Inspect
- `AI_CONTEXT.md`
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-09-st1-029-indexed-currentness-extraction.json`

## Files Allowed to Change
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if approved certification semantics require a new recorded decision
- `evidence/sanitized/`, aggregate-only

## Execution Steps
1. Read the local-only ST1-030 review package; do not place excerpts or locators in Git.
2. Display each card to the designated reviewer with the required provenance and uncertainty.
3. Record the reviewer’s exact disposition; do not infer a decision.
4. Exclude rejected/unapproved claims from certification and platform persistence.
5. Create exactly one atomic follow-up task matching the actual decision outcome.

## Acceptance Criteria
- All ten decisions are explicit and attributable to the designated reviewer.
- No unapproved claim is certified, projected, indexed, or supplied to Dify.
- Any later certification task preserves source-attributed, historical/non-current semantics.
- Sanitized evidence contains only counts and policy/result metadata, never raw source content or locators.

## Verification Commands
```bash
python -m json.tool evidence/sanitized/2026-08-09-st1-029-indexed-currentness-extraction.json > /dev/null
git diff --check
```

## Evidence Required
- Local-only review package and decision state.
- Sanitized aggregate decision summary after review.

## Rollback
Human Review is an append-only decision event. No source, infrastructure, platform, or certification state is changed before an explicit approval and a separately verified controlled-certification task.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only when required
