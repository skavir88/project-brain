# Next Task

## Metadata
- Task ID: ST1-053
- Stage: Stage 1 — Product Implementation
- Status: Awaiting business source-owner input
- Owner: Designated business owner

## Objective
Obtain the responsible project-control/reporting owner or the authoritative system/location for the latest periodic project-status source.

## Rationale
- ST1-052 completed the single approved metadata-only recovery pass over 52,981 runtime-local index rows.
- It found no bounded, project-wide source whose directory/name sequence can safely establish a reporting period after `1402/12/05`.
- The user does not know the filing location, and a further metadata crawl would repeat the exhausted strategy.

## Required Business Input
- One of: (a) the project-control/reporting owner who can identify the authoritative latest report, or (b) the authoritative source system/folder/file location for the latest periodic progress, dashboard, schedule, or status report.

## Allowed Hosts
- None. This is a business-source gate.

## Allowed Operations
- After a supplied source is confirmed within the approved pilot root: one bounded, read-only metadata verification and a separate atomic extraction task.

## Forbidden Operations
- Broad SMB crawling, arbitrary selection based on filesystem timestamps, content access before a bounded source is identified, automatic certification, or changes to existing trusted knowledge.

## Inputs
- The business source-owner input above.

## Verification
```powershell
# After input: verify the supplied location is inside the approved pilot root
# and record only sanitized aggregate metadata.
```

## Evidence Requirements
- Sanitized proof of source boundary, supported file count/type summary, and the reason it is the designated reporting source; no raw locator or organizational content in Git.

## Rollback
- None; this task does not change runtime or source state.

## Definition of Done
- A bounded authoritative source is identified and one extraction task is created, or the business-source gap is precisely recorded without repeating metadata discovery.
