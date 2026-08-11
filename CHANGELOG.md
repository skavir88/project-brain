# Changelog

## 2026-08-10

### Added
- Additive ST1-070 controlled-attestation lifecycle, verified-only view,
  synthetic guard verification, sanitized evidence, and Persian Business
  Attestation Pack.
- DEC-030 controlled-attestation evidence hierarchy and non-retroactive,
  no-auto-certification boundary.
- Additive append-only ST1-069 governance-evidence observation model and sanitized bounded recovery evidence.
- Additive ST1-068 reusable role-identity and source-control/reporting-time verification models, exact-scope lifecycle guard, and PASS/HUMAN_REQUIRED/QUARANTINE exception queue.
- Sanitized ST1-068 conditional-activation readiness evidence.
- Additive append-only ST1-067 governance-bootstrap policy, pending-delegation, lifecycle-event, and active-authority structures.
- Sanitized ST1-067 governance-bootstrap evidence, reusable resolution queue, and rolled-back synthetic lifecycle verification.
- Idempotent ST1-067 policy-bootstrap application that preserves the single pending lifecycle event on repeat execution.
- A fully populated but non-registerable ST1-067 CEO governance-delegation proposal with explicit required inputs and no runtime mutation.
- A local ST1-067 proposal validator for the machine-readable CEO decision object.
- Sanitized ST1-067 read-only registry evidence confirming that required governance identities and authoritative source identity must remain explicit inputs.
- ST1-067's scoped governance-delegation decision template and atomic approval gate.
- SDAS v0.3 contract, append-only assurance-decision schema, and sanitized framework evidence.
- SDAS authority/business-time append-only evidence models and sanitized ST1-062 resolution evidence.
- Sanitized ST1-061 bounded native real-data acquisition and policy-routing evidence.
- Sanitized ST1-060 append-only policy-status and disabled-decision rejection evidence.
- Additive SDAS policy-status-event table and database-enforced append-only disable/rollback behavior.
- Sanitized ST1-059 deterministic SDAS v0.2 policy-evaluator evidence.
- Sanitized ST1-058 private synthetic SDAS v0.2 native-chain, controlled-certification, registration, policy-state, and provenance-backed retrieval evidence.
- Additive immutable SDAS v0.2 registration and post-registration lifecycle-event tables, plus policy-version state enforcement.

### Changed
- Revalidated that ST1-061 locator recovery and its single native read-only acquisition are already complete; avoided a duplicate acquisition event and advanced the next task to the required governance decision.
- Added and deployed a private deterministic policy evaluator without database writes or automatic certification.
- Completed the approved human-controlled certification of one private native synthetic SDAS record; no organizational data, automatic certification, authority/currentness upgrade, or reliance eligibility was introduced.

## 2026-08-08

### Added
- Sanitized ST1-051 post-1402/12 metadata-only currentness-discovery evidence.
- Sanitized ST1-050 bi-weekly management RAG verification evidence.
- Sanitized ST1-049 existing embedding-credential read-only diagnostic evidence.
- Sanitized ST1-048 existing embedding-runtime diagnostic evidence.
- Sanitized ST1-047 bi-weekly management-report certification and embedding-blocker evidence.
- Sanitized ST1-045 controlled historical-management-report certification evidence and ST1-046 bounded newer-management-report review-preparation evidence.
- Controlled synthetic certification lifecycle and append-only audit persistence.
- Deterministic, durable Certified Knowledge projection for persisted synthetic certified records only.
- Loopback-only deterministic Certified Knowledge retrieval with source and certification provenance.
- Private synthetic Certified Knowledge → Qdrant → Dify grounded-answer vertical slice with structured provenance and no-evidence behavior.
- DEC-014 and the bounded read-only real business-pilot preflight task.
- Sanitized ST1-013 real file-share metadata-only preflight evidence.
- Sanitized ST1-014 metadata-only real-content subset discovery evidence.
- Sanitized partial real-content extraction evidence for the selected `status_candidate_b` subset.
- Sanitized ST1-015 real human-review preparation evidence.
- Sanitized ST1-016 human-review outcomes and bounded evidence-improvement evidence.
- Sanitized ST1-017 bounded locator recovery, local OCR, XLSX diagnosis, and Human Review summary.
- Sanitized ST1-018 status-oriented metadata discovery evidence.
- Sanitized ST1-019 explicit source-selection and bounded extraction/review summaries.
- Sanitized ST1-020 Human Review decision summary and ST1-021 bounded evidence-enrichment summary.
- Sanitized ST1-022 dated status-source selection and local extraction/review summaries.
- Local-only deterministic PDF/DOCX/XLSX extraction and Human Review packaging utilities for the selected corpus.
- Local-only deterministic extraction and review-package utilities for bounded real content.
- Sanitized ET0-004 runtime connectivity evidence from Dify components on `rdapp` to the declared data backend endpoints.
- Local-only Stage 1 ingestion-service health skeleton and sanitized verification evidence.

### Changed
- Replaced the reachability task with a narrower active-connection-evidence task; no architecture conclusion was made from reachability alone.
- Recorded direct runtime evidence for PostgreSQL/Redis connections and retained Qdrant usage as unknown after no active connection was observed.
- Recorded safe backend health/version evidence and documented unauthenticated Redis and Qdrant-version limitations.
- Recorded observed critical listeners and scheduled a Stage 0 completion review.
- Recorded the Stage 0 Completion Review outcome as further safe evidence work required before the architecture transition gate.
- Recorded sanitized local-Redis active-connection evidence without inferring configuration or non-use.
- Recorded one Dify SSRF proxy classification, two non-critical unclassified containers, and the Stage 0 architecture decision gate.
- Accepted current n8n placement on `rdapp`, closed Stage 0, and prepared the Stage 1 transition approval gate.
- Recorded explicit Stage 1 transition approval; recorded local Docker Compose runtime availability as the remaining ST1-001 blocker without installing software or changing infrastructure.
- Recorded the approved but unsuccessful WSL prerequisite attempt from a non-administrative control-workstation session; no component installation or reboot occurred.
- Verified Docker Desktop/WSL2 local runtime availability and successful ST1-001 Docker Compose configuration validation.
- Added and verified the local synthetic-record intake and structural-validation slice; Compose testing was loopback-only and left the service stopped.
- Added and verified deterministic identifier canonicalization and SHA-256 content fingerprints for accepted synthetic records.
- Added and verified a process-local synthetic duplicate gate that returns a conflict for repeated fingerprints and clears on service restart.
- Recorded DEC-009 and added the verified deterministic MVP Data Credibility Gate with transient candidate, review, and rejection dispositions; no final certification or persistence was introduced.
- Added isolated PostgreSQL-backed durable persistence for synthetic ingestion credibility results and restart-safe duplicate control.
- Verified controlled certification concurrency, invalid-state handling, restart persistence, and least-privilege runtime access.
- Recorded DEC-011 and DEC-012, and verified the Certified Knowledge projection boundary, idempotency, traceability, and restart persistence.
- Added and verified bounded deterministic Certified Knowledge retrieval without raw-record exposure, embeddings, or AI/RAG invocation.
- Recorded DEC-013, added explicit source-record identity to Certified Knowledge, and verified the isolated Qdrant derived index and Dify grounded-answer path.
- Authorized one bounded real business pilot while retaining explicit certification and human-review boundaries.
- Recorded partial read-only pilot-folder inventory, format-risk categories, and the bounded-subset gate before real content access.
- Recorded three non-sensitive status-reporting candidate summaries and stopped before content access pending business selection.
- Recorded DEC-015 and partial read-only extraction: 18 of 19 selected documents succeeded; one XLSX requires format-resolution and human review.
- Recorded the XLSX diagnosis as incomplete due to unavailable current SMB access, rather than inferring corruption from `BadZipFile`; prepared three local redacted candidates for explicit human decisions.
- Recorded three explicit `NEEDS_MORE_EVIDENCE` decisions with zero certification, and corrected the local-only subset-locator design for future extraction runs.
- Validated the operator-provided `status_candidate_b` subset, completed local Persian OCR, and recorded that this corpus cannot support the CEO project-status question.
- Replaced generic bounded-subfolder selection with business-question-driven source discovery and retained human selection where metadata candidates have different business meanings.
- Recorded the explicit selection of `status_oriented_candidate_1`; completed local-only extraction within its fixed boundary and retained all real content, provenance locators, and review excerpts outside Git.
- Recorded zero approvals from ST1-020; excluded 11 rejected educational/external candidates and bounded the final enrichment pass to the four unresolved project-related candidates.
- Selected a recurring internally dated daily-status source, deduplicated copied-forward snapshots, and prepared only time-contextualized row-level candidates for Human Review.
- Recorded DEC-018 and certified 12 explicitly approved real observations as historical, source-attributed claims only; projected only those claims to Certified Knowledge and the isolated Qdrant index.
- Recorded the real-data RAG threshold result: the current `0.70` minimum score preserves `insufficient_certified_evidence` and no historical grounded answer is yet verified.
- Verified a provenance-backed real historical answer with the unchanged `0.70` policy when the query explicitly bound the approved reporting period; current/latest status remains unsupported.
- Added sanitized ST1-024 metadata-only currentness discovery; no new source was selected or opened because the sole later-metadata candidate is planning-labelled and lacks verified reporting-date/authority semantics.
- Recorded DEC-019 and completed bounded, read-only ST1-025 extraction of the approved currentness corpus; prepared seven local-only, provenance-backed Human Review candidates without certification or platform persistence.
- Recorded DEC-020 and certified seven explicitly approved Action Plan observations as source-attributed historical statements; verified projection, isolated Qdrant indexing, provenance-backed RAG, unchanged retrieval threshold, and historical/modality framing.
- Recorded the bounded ST1-027 metadata-only discovery timeout after excluding exhausted corpora; no content was opened and no absence-of-source conclusion was made.

## 2026-08-11

### Added
- Additive SDAS assurance-passport projection on `rddb` via `migrations/022_add_sdas_assurance_passport_projection.sql`.
- Private assurance-passport route and classifier in the loopback ingestion service: `GET /v1/sdas/passport`.
- Additive SDAS portfolio summary and exception-queue views on `rddb` via `migrations/023_add_sdas_assurance_passport_summary.sql`.
- Private loopback summary and queue routes in the ingestion service: `GET /v1/sdas/passports/summary` and `GET /v1/sdas/passports/exceptions`.
- Additive SDAS pre-certification routing projection, summary, and exception queue on `rddb` via `migrations/024_add_sdas_record_routing_summary.sql`.
- Additive SDAS per-record routing-detail view on `rddb` via `migrations/025_add_sdas_record_routing_detail.sql`.
- Private loopback routing routes in the ingestion service: `GET /v1/sdas/routing/summary` and `GET /v1/sdas/routing/exceptions`.
- Private loopback per-record explainability route in the ingestion service: `GET /v1/sdas/routing/detail`.
- Candidate-class analysis for the first real ST1-066 path at `docs/ST1_075_REAL_POLICY_AUTOMATIC_CANDIDATE.md`.
- Candidate-specific governance/source bundle for the selected ST1-075 workbook class at `docs/ST1_076_PROJECT_CONTROLS_PROGRESS_WORKBOOK_BUNDLE.md`.
- Candidate-specific Persian business evidence-request pack for the selected workbook class at `docs/ST1_077_PROJECT_CONTROLS_PROGRESS_EVIDENCE_REQUEST_FA.md`.
- Sanitized ST1-071 evidence for governance parking, gap analysis, passport verification outcomes, and deployment checks.
- Sanitized ST1-072 evidence for deterministic portfolio counts, exception routing, and runtime route checks.
- Sanitized ST1-073 evidence for deterministic record-routing counts, governance-blocked routing, and runtime route checks.
- Sanitized ST1-074 evidence for deterministic per-record routing explainability and runtime detail-route checks.
- Sanitized ST1-075 evidence for real candidate-class selection and exact governance/control gap mapping.
- Candidate-specific ST1-076 bundle for the selected recurring Project Controls progress workbook class.
- Sanitized ST1-077 evidence for the class-specific business evidence-request pack.
- `docs/SDAS_ASSURANCE_PASSPORT.md` documenting the machine-readable passport contract and deterministic result semantics.

### Changed
- Explicitly parked the unresolved E1/E2/E3 governance dependency as `WAITING_FOR_EXTERNAL_EVIDENCE` instead of treating it as a failed technical task.
- Rebuilt and restarted only `ingestion-service` on `rdapp` after a timestamped backup of remote `app.py`; verified private health and malformed-request behavior.
- Rebuilt and restarted only `ingestion-service` on `rdapp` again after a second timestamped backup of remote `app.py`; verified private summary and exception routes.
- Rebuilt and restarted only `ingestion-service` on `rdapp` again after a third timestamped backup of remote `app.py`; verified private routing summary and exception routes.
- Rebuilt and restarted only `ingestion-service` on `rdapp` again after a fourth timestamped backup of remote `app.py`; verified the private routing-detail route.
- Continued SDAS implementation without changing real authority, certification, currentness, or reliance boundaries.

## 2026-08-06

### Added
- Sanitized, machine-readable Stage 0 service inventory for all declared hosts.

### Changed
- Recorded observed service placement and the n8n/`rdautomation` divergence without changing architecture responsibilities.
- Recorded scoped autonomous implementation authority while retaining high-risk approval gates.

## 2026-08-05

### Added
- Non-secret SSH connection metadata for the five declared hosts.
- Local dedicated SSH key, managed aliases, host-key registration, and the SSH bootstrap decision.
- Sanitized Stage 0 baseline summary from all five declared hosts.

### Changed
- Replaced the collector task with the prerequisite public-key authentication task after verified `auth_failed` results on all five hosts.
- Replaced the SSH bootstrap task with a read-only service-inventory task after public-key login and collector execution were verified on all five hosts.

## 2026-08-03

### Changed
- Rebased Project Brain documentation from test content to Enterprise AI Stage 0.
- Replaced unsupported infrastructure claims with declared topology, evidence states, and explicit unknowns.
- Replaced the broad legacy task with the next atomic local baseline-evidence task.
- Aligned supporting prompts and repository guide with the 10-file Project Brain model.

### Added
- Declared host inventory manifest, read-only local baseline collector, and raw-evidence Git exclusion.
- Evidence-first status model and Stage 0 governance decisions.
- Added DEC-021 and a resumable, local-only metadata discovery index for the approved pilot root; recorded aggregate index completion and errors without versioning raw inventory.
- Selected a bounded metadata-ranked currentness candidate, revalidated its availability, and completed local read-only extraction of its stable 32-entry subset. Prepared ten local-only Human Review candidates with a later internal `1402/06` period signal; no certification or platform persistence occurred.
- Recorded ten exact ST1-030 `NEEDS_MORE_EVIDENCE` decisions with zero certification eligibility; added bounded ST1-031 same-workbook schema enrichment and revised local-only review material with verified plan/actual field semantics.
- Recorded DEC-022 and all ten explicit ST1-032 `APPROVE` decisions; atomically certified and projected only the approved weekly Action-Plan observations with source-attributed reporting-week semantics.
- Recorded the downstream embedding-provider runtime blocker during controlled Qdrant/Dify verification. No retrieval threshold or policy was weakened and no credential detail was versioned.
- Added sanitized ST1-033 provider diagnostics: Dify/plugin, provider-network, Qdrant, and independent-generation checks are healthy; the remaining fault is limited to the embedding capability and has no safe automatic configuration repair.
- Recorded approved Option 1 existing-provider recovery: a controlled `dify-plugin-daemon` restart restored embedding without credential, model, provider, schema, threshold, or trusted-data changes. Verified 32 isolated Qdrant points and source-attributed ST1-032 RAG provenance at the unchanged threshold.
- Added sanitized ST1-035 local metadata-only selection of one bounded newer-source candidate. No SMB traversal or content access occurred; the selected source remains a discovery boundary pending content-access approval.
- Recorded standing-authorized ST1-036/ST1-037 bounded extraction: one insufficient partial boundary and one 34-document corpus with 15 local-only Human Review candidates; no real content entered platform services.
- Recorded all 15 ST1-038 Human Review decisions as `NEEDS_MORE_EVIDENCE`, with zero certification eligibility.
- Closed ST1-039 as `complete_with_source_gap`; recorded the bounded metadata-only source-gap search and a sanitized CEO-status evidence specification without weakening trust or retrieval policy.
- Recorded ST1-040 controlled self-discovery: ranked runtime-local metadata families, qualified one bounded family with local extraction/Persian OCR, and prepared three local-only Human Review candidates without certification or platform persistence.
- Recorded DEC-023 and ST1-041 controlled certification of three approved source-attributed observations; verified append-only audit, Certified Knowledge projection, 35-point isolated Qdrant index, least privilege, and unchanged no-evidence retrieval policy.
- Recorded ST1-042 targeted linkage discovery and two local-only Human Review candidates without automatic certification or platform persistence.
- Added sanitized ST1-043 metadata-only authoritative-source locator evidence. It identifies one bounded management-report candidate by runtime-local token and records no raw locator or content.
- Added sanitized ST1-044 bounded management-report extraction evidence. It records successful local-only extraction/OCR, the historical-date boundary, and the unreviewed source-scope/date conflict without versioning organizational content.

### Changed
- Recorded DEC-024 and controlled certification of seven approved ST1-044 historical observations; preserved two `NEEDS_MORE_EVIDENCE` records and one scope conflict outside trusted stores, and verified 42 isolated Qdrant points without weakening retrieval policy.
- Completed bounded ST1-046 newer management-report extraction from a runtime-local family and prepared seven local-only, provenance-backed Human Review candidates without automatic certification or platform persistence.
- Recorded DEC-025 and certified/projected seven explicitly approved reporting-period-bounded management observations; retained the currentness boundary and recorded the non-mutating existing-embedding timeout blocker before Qdrant indexing.
- Recorded the bounded ST1-048 diagnosis: embedding-related authentication failure was observed without credential inspection or change; Qdrant invariants remained intact and the next recovery path is approval-gated.
- Recorded ST1-049 non-mutating diagnostic success: the existing model-specific embedding credential produced one controlled 3072-dimensional embedding; no credential refresh or configuration change was required.
- Verified ST1-050 isolated index invariants and provenance-backed, period-bound historical RAG at threshold `0.70`; broad management retrieval remains conservatively insufficient.
- Recorded ST1-051 metadata-only exhaustion: no post-1402/12 family has deterministic management-status, periodic-report, or project-control signals, so no content source was opened.
- Completed ST1-052's one bounded metadata-only locator-recovery pass over the runtime-local index. It selected no source because no eligible project-wide continuation beyond the verified period could be established from metadata; added sanitized source-gap evidence and a source-owner gate.
- Added the decision-gated Sahra Data Assurance Standard v0.1 proposal and pilot gap assessment. It documents assurance evidence requirements and downstream consumption provenance without changing existing certification, currentness, authority, retrieval, or runtime semantics.
- Recorded DEC-026 and implemented the approved additive SDAS v0.1 internal pilot: immutable assurance/consumption evidence, 49 evidence-only back-assessments, append-only consumption verification, and negative tamper/transition/duplicate checks. No record became current, authoritative, or reliance-eligible.
- Added deterministic ST1-078 local evidence-intake spec and validator for the selected real workbook class at `docs/ST1_078_REAL_EVIDENCE_INTAKE_SPEC.md` and `scripts/validate_st1_078_real_evidence_bundle.py`.
- Added synthetic valid/invalid ST1-078 bundle fixtures under `docs/examples/`.
- Added sanitized ST1-078 evidence for the local intake-validator verification path.
- Added a machine-readable ST1-078 submission template with `REQUIRED_INPUT` placeholders and a short usage guide at `docs/ST1_078_REAL_EVIDENCE_SUBMISSION_TEMPLATE.md`.
- Added deterministic ST1-078 readiness assessment at `scripts/assess_st1_078_real_evidence_bundle.py` and sanitized verification evidence for valid/invalid/template bundle states.
- Added ST1-079 external-gate parking and dependency fingerprinting at `docs/ST1_079_EXTERNAL_GATE_PARKING.md` and `scripts/fingerprint_st1_078_external_gate.py`.
- Added ST1-079 assurance-passport capability matrix at `docs/ST1_079_ASSURANCE_PASSPORT_MATRIX.md`.
- Upgraded the repository-side Assurance Passport contract toward `SDAS Assurance Passport v0.1`, including a distinct `INTEGRITY_FAILURE` outcome and dimension-level explanation in the local service/read-model code and docs.
- Added local ST1-079 contract verification at `scripts/verify_st1_079_assurance_passport_v01.py` and sanitized evidence for the parked external gate plus v0.1 contract behavior.
- Added ST1-080 runtime apply/verify automation at `scripts/apply_st1_080_passport_v01.py` and `scripts/verify_st1_080_passport_runtime.py`.
- Deployed the upgraded `SDAS Assurance Passport v0.1` contract/views to the private ingestion stack and recorded sanitized runtime verification evidence.
- Added ST1-081 additive index-visibility projection at `migrations/026_add_sdas_assurance_passport_index_projection.sql`.
- Added ST1-081 private runtime apply/verify automation at `scripts/apply_st1_081_passport_index_visibility.py` and `scripts/verify_st1_081_passport_index_visibility.py`.
- Extended the private assurance surface with `GET /v1/sdas/passport/index` for certified-only Qdrant projection visibility without exposing vectors, credentials, or uncertified records.
- Recorded sanitized ST1-081 runtime verification evidence for indexed certified, certified-not-indexed synthetic, and uncertified/missing exclusion behavior.
- Added ST1-082 read-only selected-class forecast automation at `scripts/forecast_st1_082_policy_automatic.py`.
- Recorded sanitized ST1-082 evidence that exact-scope governance/source-control activation alone unlocks zero current records from the selected recurring workbook class because all 10 currently known rows still lack native evidence.
- Added ST1-083 first-native-record preflight verifier at `scripts/verify_st1_083_first_native_record_preflight.py`.
- Added ST1-083 synthetic native-record fixtures for ready, invalid business-time, and incomplete native-evidence cases under `docs/examples/`.
- Recorded sanitized ST1-083 evidence for four deterministic first-native-record preflight states without mutating any runtime trust or certification data.
- Added ST1-084 dry-run runtime planner at `scripts/plan_st1_084_first_real_runtime_attempt.py`.
- Recorded sanitized ST1-084 evidence for blocked and ready dry-run planning states, including the ordered six-step append-only write sequence and preserved hard stops.
- Added ST1-085 non-secret execution-manifest compiler at `scripts/compile_st1_085_first_real_attempt_manifest.py`.
- Recorded sanitized ST1-085 evidence for blocked and ready manifest compilation states, including the operator-executable six-step payload shapes and preserved hard stops.
- Added ST1-086 operator handoff generator at `scripts/generate_st1_086_operator_handoff.py`.
- Recorded sanitized ST1-086 evidence for blocked and ready operator-handoff states, including required operator-supplied values, ordered runtime actions, and preserved hard stops.
- Added ST1-087 operator-kit compiler at `scripts/compile_st1_087_first_real_attempt_kit.py`.
- Recorded sanitized ST1-087 evidence for blocked and ready operator-kit states, including preserved hard stops, ordered runtime-step counts, and required operator-input counts without runtime mutation.
- Added ST1-088 pre-mutation independent-verification gate at `scripts/verify_st1_088_pre_mutation_gate.py`.
- Added ST1-088 synthetic ready/invalid operator-input fixtures and recorded sanitized evidence for `NO_GO_FOR_RUNTIME_MUTATION` and `GO_FOR_FIRST_RUNTIME_MUTATION` outcomes with exact blocker reason codes.
- Added ST1-089 post-mutation receipt verifier at `scripts/verify_st1_089_policy_automatic_receipt.py`.
- Added ST1-089 synthetic ready/invalid runtime-receipt fixtures and recorded sanitized evidence for missing, invalid, and successful `policy_automatic` hard-stop verification outcomes.
- Added ST1-090 selected-class operating-model simulator at `scripts/simulate_st1_090_selected_class_operating_model.py`.
- Added ST1-090 current-like and mixed synthetic batch fixtures and recorded sanitized evidence for deterministic batch routing counts, dominant reason codes, Human Review reduction, and exception-focused review handling.
- Added ST1-091 selected-class exception queue generator at `scripts/generate_st1_091_selected_class_exception_queue.py`.
- Recorded sanitized ST1-091 evidence proving `policy_automatic` items are excluded from individual review output and only exact exceptions enter the review pack.
- Added ST1-092 first-real hard-stop report compiler at `scripts/compile_st1_092_first_real_hard_stop_report.py`.
- Recorded sanitized ST1-092 evidence for blocked and ready hard-stop report compilation states, including the required pre-certification report fields.
- Added ST1-093 first-real execution dossier compiler at `scripts/compile_st1_093_first_real_execution_dossier.py`.
- Recorded sanitized ST1-093 evidence for blocked and ready dossier compilation states, including preserved hard stops, ready hard-stop reporting, and exception-handling surfaces.
- Added ST1-094 external-evidence-to-dossier handoff compiler at `scripts/compile_st1_094_external_evidence_to_dossier_handoff.py`.
- Added ST1-094 invalid native-record fixture and recorded sanitized evidence for blocked and ready handoff compilation states.
- Added ST1-095 final operator launch-package compiler at `scripts/compile_st1_095_final_operator_launch_package.py`.
- Recorded sanitized ST1-095 evidence for blocked and ready launch-package compilation states, including preserved hard stops and the ready hard-stop reporting surface.
- Added ST1-096 real-run readiness-summary compiler at `scripts/compile_st1_096_real_run_readiness_summary.py`.
- Added ST1-096 runtime-only-missing operator-input fixture and recorded sanitized evidence for `waiting_for_external_evidence`, `waiting_for_runtime_only_fields`, and `ready_to_run` states.
- Added ST1-097 selected-class missing-input-pack compiler at `scripts/compile_st1_097_missing_input_pack.py`.
- Recorded sanitized ST1-097 evidence proving the exact non-ready missing inputs are narrowed to one external native-evidence requirement or five runtime-only requirements, with zero missing inputs in the ready case.
- Added ST1-098 selected-class reentry-gate compiler at `scripts/compile_st1_098_reentry_gate.py`.
- Recorded sanitized ST1-098 evidence proving unchanged parked dependency state stays parked, changed dependency fingerprint reopens external reassessment, runtime-only gaps remain local, and ready inputs surface `READY_FOR_FIRST_RUNTIME_MUTATION` without mutating trust state.
- Added ST1-099 single-command first-real-attempt rehearsal runner at `scripts/run_st1_099_first_real_attempt_rehearsal.py`.
- Recorded sanitized ST1-099 evidence proving one deterministic invocation now returns the truthful parked/reopen/runtime-only/ready status plus immediate next action without mutating trust state.
- Added ST1-100 selected-class submission-delta comparator at `scripts/compare_st1_100_submission_delta.py`.
- Recorded sanitized ST1-100 evidence proving unchanged bundle/native submissions keep the first-real path parked, while a changed native-evidence state surfaces exact reentry-relevant deltas and a truthful readiness transition without mutating trust state.
- Added ST1-101 business-facing selected-class change-impact summarizer at `scripts/summarize_st1_101_submission_change_impact.py`.
- Recorded sanitized ST1-101 evidence proving unchanged submissions remain no-impact while changed submissions surface a concise exact readiness/next-action transition without mutating trust state.
- Added ST1-102 selected-class candidate-submission checklist compiler at `scripts/compile_st1_102_candidate_submission_checklist.py`.
- Recorded sanitized ST1-102 evidence proving unchanged submissions still expose one exact remaining native-record requirement, while a changed ready submission yields a zero-item `READY_CHECKLIST` without mutating trust state.
- Added ST1-103 selected-class arrival-packet compiler at `scripts/compile_st1_103_arrival_packet.py`.
- Recorded sanitized ST1-103 evidence proving future selected-class submissions can now be packaged into one operator-ready payload with exact readiness impact and remaining checklist items, without mutating trust state.
- Added ST1-104 selected-class pre-mutation execution-envelope compiler at `scripts/compile_st1_104_pre_mutation_execution_envelope.py`.
- Recorded sanitized ST1-104 evidence proving future selected-class ready arrivals can now be handed into the first-runtime path as one exact pre-mutation execution object with six runtime steps, three hard stops, and preserved required operator inputs.
- Added ST1-105 selected-class mutation-start handoff compiler at `scripts/compile_st1_105_mutation_start_handoff.py`.
- Recorded sanitized ST1-105 evidence proving the first-real path can now be reduced to the exact mutation-start payload and before-step-one confirmations without mutating trust state.
- Added ST1-106 selected-class first-step launch-card compiler at `scripts/compile_st1_106_first_step_launch_card.py`.
- Recorded sanitized ST1-106 evidence proving the first-real path can now be reduced to the exact initial write target, required confirmations, and preserved hard stops without mutating trust state.
- Added ST1-107 selected-class source-registration step-card compiler at `scripts/compile_st1_107_source_registration_step_card.py`.
- Recorded sanitized ST1-107 evidence proving the first write target can now be reduced to the minimal field-level `sdas_source_registry` payload plus required confirmations without mutating trust state.
- Added ST1-108 selected-class source-control-verification step-card compiler at `scripts/compile_st1_108_source_control_verification_step_card.py`.
- Recorded sanitized ST1-108 evidence proving the second write target can now be reduced to the minimal field-level `sdas_source_control_verifications` payload plus required confirmations without mutating trust state.
- Added ST1-109 selected-class acquisition step-card compiler at `scripts/compile_st1_109_acquisition_step_card.py`.
- Recorded sanitized ST1-109 evidence proving the third write target can now be reduced to the minimal field-level `sdas_acquisition_events` payload plus required confirmations without mutating trust state.
- Added ST1-110 selected-class transformation step-card compiler at `scripts/compile_st1_110_transformation_step_card.py`.
- Recorded sanitized ST1-110 evidence proving the fourth write target can now be reduced to the minimal field-level `sdas_transformations` payload plus required confirmations without mutating trust state.
- Added ST1-111 selected-class record-intake step-card compiler at `scripts/compile_st1_111_record_intake_step_card.py`.
- Recorded sanitized ST1-111 evidence proving the fifth write target can now be reduced to the minimal field-level record-intake payload plus required confirmations without mutating trust state.
- Added ST1-112 selected-class policy-decision step-card compiler at `scripts/compile_st1_112_policy_decision_step_card.py`.
- Recorded sanitized ST1-112 evidence proving the sixth write target can now be reduced to the minimal field-level `sdas_policy_decisions` payload plus required confirmations without mutating trust state.
- Added ST1-113 selected-class pre-certification hard-stop gate compiler at `scripts/compile_st1_113_pre_certification_hard_stop_gate.py`.
- Recorded sanitized ST1-113 evidence proving the six exact runtime-write surfaces can now be assembled into one truthful stop-before-certification operator handoff without mutating trust state.
- Added ST1-114 selected-class runtime-only submission-card compiler at `scripts/compile_st1_114_runtime_only_submission_card.py`.
- Recorded sanitized ST1-114 evidence proving the last local-only execution-input surface can now be reduced to the exact five real operator-supplied values still required for the first selected-class attempt.
- Added ST1-115 selected-class first-real execution-worksheet compiler at `scripts/compile_st1_115_first_real_execution_worksheet.py`.
- Recorded sanitized ST1-115 evidence proving the exact five real runtime values can now be mapped deterministically onto the existing six-step runtime sequence and preserved hard-stop boundary without mutating trust state.
- Added ST1-116 selected-class execution-trigger-card compiler at `scripts/compile_st1_116_execution_trigger_card.py`.
- Recorded sanitized ST1-116 evidence proving the selected-class first-real path can now resolve to one truthful next action: `execute_now`, `wait_for_external_evidence`, or `wait_for_runtime_only_values`.
- Added ST1-117 selected-class activation-request-packet compiler at `scripts/compile_st1_117_activation_request_packet.py`.
- Recorded sanitized ST1-117 evidence proving the selected-class first-real path can now express the smallest truthful request needed to move toward `execute_now`.
- Added ST1-118 selected-class pre-execution-operator-brief compiler at `scripts/compile_st1_118_pre_execution_operator_brief.py`.
- Recorded sanitized ST1-118 evidence proving the selected-class first-real path can now be handed off as one concise brief that combines the smallest truthful request, the six-step execution map, and the preserved stop-before-certification boundary.
- Added ST1-119 selected-class execution-conformance verifier at `scripts/verify_st1_119_execution_conformance.py`.
- Added the approved ready brief fixture `docs/examples/ST1_118_pre_execution_operator_brief.synthetic.ready.json` so future runtime receipts can be compared against a pre-approved brief artifact.
- Recorded sanitized ST1-119 evidence proving the selected-class first-real path now has deterministic conforming vs non-conforming receipt verification against the approved brief, including certification-boundary breach detection.
- Recorded sanitized ST1-120 blocked-arrival audit evidence proving the current workspace/runtime state still lacks a real independently verified arrival bundle and a real native selected-class record artifact, while runtime counts for the selected class remain at zero for source registration, acquisition, transformation, and active delegation.
- Added `scripts/verify_st1_121_limited_pilot_bootstrap.py`.
- Recorded sanitized ST1-121 evidence proving the existing append-only governance bootstrap already expresses the newly approved limited pilot boundary without granting historical/source authority, and that the existing real ST1-061 artifact truthfully remains at a native `human_required` hard stop with no certification.
- Added `scripts/compile_st1_122_first_real_policy_target.py`.
- Recorded sanitized ST1-122 evidence re-aligning the first real `policy_automatic` success target away from ST1-061 and onto the already-selected recurring workbook class plus its representative real workbook candidate with document-content reporting period evidence.
- Added the Persian business request pack `docs/ST1_123_RECURRING_WORKBOOK_GOVERNANCE_REQUEST_FA.md` for the selected recurring workbook series.
- Recorded sanitized ST1-123 evidence narrowing the external ask to exactly A1, A2, A3, plus one stable non-sensitive source-series identifier.
- Added the exact selected-series intake template `docs/examples/ST1_124_recurring_workbook_governance_bundle.template.json`.
- Added `scripts/verify_st1_124_recurring_workbook_governance_bundle.py`.
- Recorded sanitized ST1-124 evidence proving the selected-series intake kit truthfully remains `WAITING_FOR_EXTERNAL_EVIDENCE` with exact missing inputs and unchanged trust boundaries.
- Added the positive selected-series synthetic filled fixture `docs/examples/ST1_124_recurring_workbook_governance_bundle.synthetic.ready.json`.
- Added `scripts/run_st1_125_series_bundle_gate.py`.
- Recorded sanitized ST1-125 evidence proving the exact selected-series gate now deterministically distinguishes `WAITING_FOR_EXTERNAL_EVIDENCE` from `PENDING_INDEPENDENT_VERIFICATION` without activating delegation, source registration, or certification.
- Added `scripts/compile_st1_127_independent_verification_handoff.py`.
- Recorded sanitized ST1-127 evidence proving the exact selected-series post-gate path now deterministically distinguishes “not ready for controlled review” from “ready for independent verification” and freezes the exact six controlled checks without activating delegation, source registration, acquisition, or certification.
- Added `scripts/audit_st1_066_readiness.py`.
- Recorded sanitized ST1-129 evidence proving exactly which ST1-066 sections are already proven, which are preparation-only, and that the success criterion still awaits one real selected-series bundle, controlled review, a native selected-series record, and a real `policy_automatic` hard stop.
- Added `scripts/verify_st1_131_selected_series_native_record.py`.
- Added the positive selected-series native-record fixture `docs/examples/ST1_131_selected_series_native_record.synthetic.ready.json`.
- Recorded sanitized ST1-131 evidence proving the native-record path is now exact-scope checked for the selected recurring workbook series rather than only the broader selected class.
- Added `scripts/run_st1_132_selected_series_dual_input_gate.py`.
- Recorded sanitized ST1-132 evidence proving the selected-series bundle + selected-series native-record pair now deterministically converge to `begin_independent_controlled_review` when both exact-scope synthetic inputs are present.
- Added the Persian real-input request pack `docs/ST1_134_SELECTED_SERIES_REAL_INPUT_REQUEST_FA.md`.
- Recorded sanitized ST1-134 evidence narrowing the remaining real-world ask to exactly two selected-series artifacts and preserving the non-activation / non-certification boundary.
