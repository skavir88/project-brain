# Next Task

## Metadata
- Task ID: ST1-036
- Stage: Stage 1 — Product Implementation
- Status: Awaiting Content-Access Approval
- Owner: Designated business reviewer

## Objective
Obtain explicit read-only content-access approval for the bounded `metadata-695d19f1b3ce5979` corpus, so it can be assessed for internally dated evidence later than the verified reporting week `1402/06/25–1402/06/31`.

## Rationale
ST1-035 selected a single bounded discovery candidate through the approved local metadata index. Metadata can define scope only: it cannot establish authority, reporting date, factual correctness, certification, or current project status. Opening the new organizational corpus requires an explicit business content-access gate.

## Candidate Boundary
- Source alias: `metadata-695d19f1b3ce5979`
- Documents: 58
- Allowlisted formats: 55 PDF, three XLSX
- Aggregate metadata size: 41,524,545 bytes
- Metadata range: 2023-09-26 through 2024-12-07 UTC (discovery metadata only)
- Source locator: runtime-local only; not versioned or displayed.

## Required Decision
Choose exactly one:

1. `APPROVE_CONTENT_ACCESS` — authorize read-only local extraction for this exact corpus and only `.pdf`/`.xlsx` files.
2. `REJECT_CONTENT_ACCESS` — retain the corpus unopened and stop currentness discovery at this boundary.

## Scope if Approved
- Read-only deterministic local extraction and bounded local OCR only where required.
- Preserve PDF page and XLSX workbook/sheet/cell provenance where practical.
- Build only substantive, source-attributed Human Review candidates; do not auto-certify or send content to an external model.

## Out of Scope
- Any source outside the fixed 58-document boundary; SMB writes; broad traversal; source modification; automatic certification; PostgreSQL/Qdrant/Dify persistence of unreviewed real content; filesystem-date currentness claims.

## Evidence Requirements
- Exact decision and selected boundary aggregate only.
- On approval, sanitized extraction counts/provenance coverage only; no raw content, locator, filename, or secret.

## Rollback
Read-only extraction makes no source change. Local raw extraction artifacts remain outside Git and can be retained solely under runtime-local controls.

## Definition of Done
- One explicit content-access decision is recorded.
- No document content is opened before `APPROVE_CONTENT_ACCESS`.
- Project Brain and sanitized evidence are updated and one next atomic task is prepared.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if a new source-selection decision is required
