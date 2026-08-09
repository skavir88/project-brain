# Next Task

## Metadata
- Task ID: ST1-040
- Stage: Stage 1 — Product Implementation
- Status: Blocked on one business locator input
- Owner: Designated business owner / project-controls representative

## Objective
Obtain the folder or file location normally used by the project team for its latest periodic progress report, dashboard, current schedule report/export, or current project-status report.

## Rationale
ST1-039 exhausted the bounded local metadata index sufficiently for the current strategy. It did not identify a source that can be deterministically treated as authoritative for the CEO-status question. The existing certified timeline remains historical and does not establish current status.

## Preconditions
- The location must remain inside the already approved pilot root.
- It must identify a business-maintained status/progress source, not merely a document-control, tender, legal/claim, training, or generic planning folder.

## Scope
- Record one operator-supplied folder or file locator in runtime-local state only.
- Verify read-only access and bounded metadata signature.
- If the supplied source is clearly within the standing read-only authorization, extract only that bounded source locally and prepare substantive Human Review candidates with provenance.

## Out of Scope
- Broad recursive crawling; reprocessing exhausted corpora; opening unselected content; automatic certification; platform persistence; external-model processing of uncertified organizational content; using filesystem dates as status facts.

## Inputs
- One business locator: the normal filing location for the project's latest weekly/monthly progress report, dashboard, schedule, or status report.

## Verification
```powershell
# Read-only: verify the supplied locator is within the approved pilot root and enumerate its bounded metadata signature.
```

## Evidence Requirements
- Sanitized aggregate signature, access result, extraction/review outcome, and source-gap coverage only.
- Raw locator, filename, organizational content, credential, and raw evidence remain outside Git.

## Rollback
No source change occurs. Remove only runtime-local transient selection state if it is incorrect.

## Definition of Done
- The business locator is recorded only in runtime-local state and its bounded boundary is verified.
- Any extraction stays read-only and within that boundary.
- Substantive review candidates, or a precise insufficiency result, are recorded without automatic certification.
- Project Brain, sanitized evidence, and one next atomic task are updated.
