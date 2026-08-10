# Master Plan

## Stage 0 — Project Discovery, Baseline and Automation Foundation
Status: Complete

Objectives:
- Record the actual infrastructure baseline, host roles, services, versions, ports, dependencies, and unknowns.
- Establish Project Brain governance, configuration/secrets policy, repeatable verification tools, and atomic-task automation workflow.
- Define and verify Stage 0 completion criteria.

Quality gates:
- Every infrastructure claim is classified and evidence-backed when marked `verified`.
- No secrets or unreviewed raw evidence are versioned.
- Verification is command-based, repeatable, readable, and returns meaningful exit codes.
- `NEXT_TASK.md` contains only one atomic, testable task.

### Completion Review — 2026-08-08
Outcome: `ready_for_stage_transition_approval`

The transition gate was explicitly approved on 2026-08-08.

Verified evidence covers the infrastructure baseline, SSH automation, service placement categories, critical listeners, Dify runtime reachability, PostgreSQL/Redis active-connection evidence, verification tooling, Project Brain governance, and the accepted n8n placement. Two `rdapp` containers, Qdrant reported version, Redis unauthenticated readiness, and sampled Qdrant active-use evidence remain known limitations; none blocks starting non-production product implementation. Stage 1 remains outside scope until the transition gate is explicitly approved.

## Stage 1 — Product Implementation
Status: In progress — local runtime and ST1-001 implementation baseline verified.

Objective: deliver the smallest safe, demonstrable vertical slice of the approved product direction without real organizational data or production deployment.

ST1-001 through ST1-005 verified the local synthetic intake, validation, canonicalization, duplicate gate, and deterministic credibility dispositions. ST1-006 added isolated durable PostgreSQL persistence, ST1-007 added controlled certification plus an append-only audit trail, ST1-008 added an idempotent Certified Knowledge projection restricted to certified records, ST1-009 added deterministic retrieval with source/certification provenance, and ST1-010/ST1-011 verified the first private Dify/Qdrant grounded-answer vertical slice. DEC-014 authorizes one bounded real business pilot; ST1-013 must first verify only the selected read-only file-share folder and its metadata constraints.

ST1-013 verified read-only pilot-folder access and a partial metadata inventory. The next gate is intentionally narrow: select a bounded initial document subset and explicit supported-format/extraction allowlist before any real file content is read or ingested.

ST1-045 completed controlled certification of seven explicitly approved historical management-report observations. It preserved the source-scope conflict and excluded all nonapproved items. ST1-046 then selected and read only one bounded, later internally dated management-report family under standing authorization. It produced seven runtime-local, provenance-backed Human Review candidates. The next gate is explicit Human Review; no candidate is certification-eligible until its exact disposition is supplied.

ST1-047 completed controlled certification and Certified Knowledge projection for all seven explicitly approved observations from the coherent bi-weekly reporting period `1402/11/21–1402/12/05`. The timeline advances only to that historical reporting period; present-day status remains insufficient. Index/RAG completion is blocked by the unchanged embedding invocation timing out with no Qdrant write. The next atomic task is bounded existing-provider runtime recovery; it may not change credentials, provider, model, vector schema, or threshold without separate approval.

ST1-048 completed the permitted existing-runtime diagnosis. It observed an embedding-related authentication failure alongside the controlled timeout but did not inspect or change the credential. The remaining work is approval-gated credential recovery or, separately, an approved provider/model decision; no further blind retry is planned.

ST1-049 performed the approved read-only diagnosis before any credential mutation. The existing embedding credential is recognized by Dify: one controlled synthetic embedding invocation succeeded at vector dimension 3072, while a separate generation credential/model also succeeded. Credential refresh is not required; the next task is controlled idempotent ST1-047 indexing and period-bound RAG verification without changing configuration.

ST1-050 verified the first end-to-end retrieval path for the approved bi-weekly management observations: the collection holds exactly seven new ST1-047 points without removing the 42 prior points, and a narrow source/period/metric-bound query returns provenance-backed historical framing at threshold `0.70`. Broad management retrieval correctly remains conservative. The next task returns to metadata-only currentness discovery for coherent status sources newer than `1402/12/05`.

ST1-051 exhausted the completed local metadata index for post-`1402/12` candidate families with coherent status semantics. It found no name/directory signals sufficient for safe automatic content selection. The next gate requests the normal business filing location for the latest periodic progress, dashboard, schedule, or status source; no broad crawl or speculative corpus selection is authorized.

ST1-052 completed the one approved business-locator recovery pass using only the same local metadata index. It found no deterministic project-wide source that can extend the verified period beyond `1402/12/05`; apparently later package-specific folders cannot establish report date, authority, or CEO-status semantics from metadata. The critical path is now a source-system owner or authoritative reporting location, not another discovery crawl.

ST1-053 acknowledges that source gap and leaves it blocked pending business input. In parallel it creates the decision-gated SDAS v0.1 proposal: an additive assurance model for Source through downstream consumption provenance, with explicit gaps for the current 49-item pilot. It makes no currentness, authority, certification, or runtime change. The next gate is architecture/governance approval before any additive assurance implementation.

ST1-055 implemented the approved SDAS v0.1 internal pilot with additive immutable assurance/consumption evidence tables. It back-assessed all 49 Certified Knowledge items only from persisted evidence, yielding `SDAS-1` / `assessed_partial` for all and zero reliance-eligible records. The next SDAS change is a decision gate; no v0.2 supersession/revocation, authority/currentness, reliance eligibility, or external rollout is implied.

ST1-056 through ST1-058 implemented and verified the approved private SDAS v0.2 provenance/policy pilot. One native synthetic record traversed source acquisition, deterministic transformation, policy automatic preparation, explicit human approval, controlled certification, registration, Certified Knowledge projection, isolated indexing, and provenance-backed retrieval. The 49 historical Certified Knowledge items remain `human_required` in the v0.2 simulation; no historical evidence was upgraded. Policy automatic approval does not certify a record, and currentness/authority/reliance remain out of scope.

ST1-014 confirmed that multiple bounded status-reporting subsets satisfy the technical size target. A business selection is required before content reading, because filesystem metadata does not establish which status period is authoritative.

DEC-015 selected `status_candidate_b`; bounded read-only extraction then completed for 18 of 19 documents without platform persistence or AI use. One selected XLSX failed deterministic OOXML extraction (`BadZipFile`), so the real-data corpus is partial and requires a human resolution/review gate before any real record can advance toward certification.

ST1-015 prepared the three successful real candidates for human decision without persisting real data. The XLSX remains unresolved because the approved SMB source was not reachable in the current session; `BadZipFile` is insufficient to infer corruption. The next critical-path gate is human review of the prepared candidates.

ST1-016 recorded `NEEDS_MORE_EVIDENCE` for all three first-pass candidates and confirmed that existing extracted text from the 18 approved PDFs is inadequate for the CEO project-status use case. The practical next step is bounded local OCR only after the exact selected-subset relative locator is recovered; broad share rediscovery is explicitly excluded.

ST1-017 recovered the exact selected subset through operator-provided bounded roots, validated the 19-entry signature, and completed local Persian OCR on all 18 PDFs. OCR did not yield report dates, physical progress, schedule, delay, risk, action, management decision, or status evidence; only two undated financial observations remain. This selected subset cannot answer the CEO project-status question. Selecting any new source requires a new explicit bounded business decision.

ST1-018 performed business-question-driven metadata discovery. Three materially different bounded series require user selection before content access: two planning-oriented series and one explicit project-status spreadsheet series. No new source content was read.

ST1-019 records the user’s selection of `status_oriented_candidate_1` as a bounded, read-only source only. Local deterministic extraction and review preparation may proceed strictly within its 18-file signature; the selection itself establishes neither source authority nor latest-status semantics.

ST1-020 recorded a complete Human Review with zero approvals. ST1-021 then performed a single bounded enrichment pass over the four unresolved sources. It found a visible Change Log row/status snapshot but no populated update date or authority/currentness evidence. The selected corpus is insufficient; the next critical path requires a specifically selected dated, authoritative project-status source rather than further reprocessing.

ST1-022 selected and extracted an internally dated daily-status workbook series. The source provides a time-contextualized historical activity snapshot and reviewable row provenance, but its authority and currentness beyond the greatest extracted reporting period remain unverified. ST1-023 is the mandatory Human Review gate; no real claim may advance without an explicit reviewer decision.

ST1-036/ST1-037 exhausted two later metadata-selected boundaries without a trustworthy current-status result. ST1-038 recorded `NEEDS_MORE_EVIDENCE` for all 15 associated candidates; none may enter the certification path.

ST1-039 is complete with a source gap. The bounded local metadata index and targeted document-control inspection did not identify the underlying authoritative periodic progress source required for the CEO-status question. The next critical path is a single business locator for the normal project-team filing location of the latest periodic progress, dashboard, schedule, or status report; it is not another broad discovery cycle.

The ST1-040 self-discovery override supersedes that human-locator gate. It ranked the completed runtime-local index and qualified one small family with source-attributed engineering/procurement evidence later than the existing certified timeline. The family does not establish a complete authoritative CEO-status snapshot; three Human Review candidates are the next gate, with no automatic certification or currentness change.

ST1-041 certified those three explicitly approved observations with strict source-attributed semantics. They extend the evidence timeline only in their narrow contexts; retrieval remains conservative at the unchanged threshold and current status remains insufficient. The critical path is targeted linkage/supersession discovery from those observations toward an authoritative overall status snapshot.

ST1-043 executed one user-directed metadata-only locator search after no business filing locator was available. A bounded management-report candidate has the strongest name/hierarchy signals, but its content, authority, reporting period, and currentness remain unknown. The next gate is a single business confirmation before any separate bounded content-access task; existing ST1-042 Human Review candidates remain untouched.

ST1-044 completed bounded local extraction after that confirmation. The source contains a historical management-level snapshot with plan/actual, discipline/site, constraint, and financial-context signals, but its newest internal date signals precede the already certified `1402/06/25-1402/06/31` period. A title/scope/date conflict remains explicit. Ten provenance-backed candidates await Human Review; no trust, currentness, or certification policy changed.

## Later Stages
Future work may implement ingestion, validation, normalization, quality scoring, HITL, lineage, certified knowledge, RAG/AI services, automation, and observability. Scope, design, and readiness criteria for later stages must be approved explicitly; they are not established by this document.
