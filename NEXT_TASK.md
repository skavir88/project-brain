# Next Task

## Metadata
- Task ID: ST1-017
- Stage: Stage 1 — Product Implementation
- Status: Blocked — exact approved subset locator required
- Owner: Enterprise AI Project Operator

## Objective
Recover the exact relative locator of the already approved `status_candidate_b` subset from an existing approved operational artifact or the authorized operator, then run local read-only OCR only over its 18 PDFs.

## Rationale
ST1-016 proved that currently retained text extraction is insufficient for the CEO project-status question. The prior local runtime artifact kept per-document relative references but not the subset relative path from the approved SMB root; broad recursive rediscovery of the 255+ GB share is excluded.

## Preconditions
- The approved SMB share root is read-only accessible.
- The operator provides, or an existing local operational artifact contains, the exact subset-relative path under that root.
- The subset still matches the approved signature: 19 documents, 18 PDF, 1 XLSX, 23,606,611 aggregate bytes.

## Scope
- Validate the supplied/recovered locator against the approved aggregate signature.
- Run local, read-only, page-level Persian OCR on only the 18 PDF documents after signature validation.
- Build a local-only substantive review package and sanitized aggregate evidence.

## Out of Scope
- Whole-share recursive discovery, sibling folders, content outside the validated subset, source modification, external AI/model use, automatic certification, real-content persistence, XLSX repair, Qdrant/Dify use, remote-host changes, credentials, public exposure, and destructive operations.

## Files to Inspect
- `CURRENT_STATE.md`
- `DECISIONS.md`
- `evidence/sanitized/2026-08-09-st1-016-human-review-and-evidence-improvement.json`
- `evidence/sanitized/2026-08-09-st1-017-locator-recovery.json`
- Local runtime artifacts only.

## Files Allowed to Change
- `scripts/<bounded-ocr-utility>.py`
- `evidence/sanitized/<dated-st1-017-ocr-summary>.json`
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`

## Execution Steps
1. Obtain an exact approved subset-relative locator from the operator's local Explorer/PowerShell lookup; do not repeat whole-share discovery.
2. Validate count, extension distribution, and aggregate size before opening a source document.
3. OCR only the validated 18 PDFs locally using Persian-capable Tesseract.
4. Create only substantive, provenance-backed, human-review-required candidates; do not certify.

## Acceptance Criteria
- The exact subset locator is validated by the approved signature before OCR.
- OCR does not read outside the bounded PDFs or send content externally.
- Candidate evidence includes page provenance and content-supported dates where available.
- No real data reaches PostgreSQL, Qdrant, Dify, or external AI.

## Verification Commands
```bash
python -m py_compile scripts/extract_real_pilot_subset.py scripts/build_substantive_real_pilot_review_package.py
git diff --check
```

## Evidence Required
- Sanitized locator-validation and OCR aggregate results; raw OCR content remains outside Git.

## Rollback
Local read-only task; delete only generated local runtime artifacts if required by policy. No source or platform state changes.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
