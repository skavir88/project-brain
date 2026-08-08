# Decisions

## DEC-001 — Enterprise AI Is the Sole Project Identity
Status: Accepted

The Project Brain documents Enterprise AI, titled Enterprise Data Platform & Data Credibility Assurance. Previous test-project identity and claims are removed.

## DEC-002 — Stage 0 Is Evidence-First
Status: Accepted

No infrastructure condition is `verified` without reproducible command output. Missing access remains `unknown` or `blocked`.

## DEC-003 — Local, Read-Only Baseline Collection
Status: Accepted

Baseline evidence is collected on each Ubuntu host by a local script. The collector performs no installation, configuration, restart, deletion, inspection of secrets, or Docker inspection.

## DEC-004 — Raw Evidence Is Not Versioned by Default
Status: Accepted

Collector output is written outside Git by default. Only reviewed and sanitized evidence may be incorporated later under an explicitly scoped task.

## DEC-005 — External Dify Backends
Status: Accepted

PostgreSQL, Redis, and Qdrant are intended as external Dify backends. Duplicating them within an application stack requires a documented architecture decision.

## DEC-006 — SSH Trust and Authentication Bootstrap
Status: Accepted

Each declared host uses a dedicated local Enterprise AI SSH key and a stable alias. Host-key verification remains enabled and initial host keys are recorded locally only after review. Passwords are never sent through command arguments, stored in the repository, or placed in project documentation. Non-interactive operations are blocked until the authorized operator installs the project public key on each host.

## DEC-007 — Scoped Autonomous Implementation Authority
Status: Accepted

The Autonomous Implementation Agent may execute the active atomic task on declared hosts when its scope, rollback, and verification are explicit. It must run preflight, make backups before important changes, sanitize evidence, and update Project Brain. High-risk destructive, SSH, network, reboot, credential, broad-sudo, or public-exposure operations remain approval-gated.

## DEC-008 — Accept n8n Placement on rdapp for the MVP
Status: Accepted

n8n observed on `rdapp` is accepted as part of the current Enterprise AI MVP application/runtime placement. `rdapp` may host Dify runtime components, Nginx, n8n, and supporting application-runtime components. `rdautomation` is reserved for future automation/workflow scale-out or isolation. This does not require n8n to remain on `rdapp` permanently; a future migration requires evidence of a concrete need and a separately approved architecture change. No n8n migration, restart, reconfiguration, or runtime change is authorized by this decision.

## DEC-009 — Initial MVP Data Credibility Gate
Status: Accepted

For local synthetic records only, structural validity and duplicate absence are necessary but not sufficient for credibility eligibility. A record may be a `certification_candidate` only after structural validation, duplicate control, and the deterministic quality gate pass; this state is eligible for later certification and is never final `certified` status.

The minimum gate requires a usable `provenance.source_reference`. Its absence routes an otherwise processable record to `human_review_required` with `provenance_insufficient`. If `observed_at` is present, it must be an ISO-8601 timestamp with timezone and must not be in the future; failure is `rejected` with `temporal_validity_failed`. If `payload.source_id` is present, it must match canonical `source_id`; failure is `rejected` with `consistency_check_failed`.

This decision authorizes no persistence, final certification, LLM judgment, quality scoring, external integration, real organizational data, or remote deployment. The resulting disposition and reason codes are transient local responses only.
