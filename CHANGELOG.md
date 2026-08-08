# Changelog

## 2026-08-08

### Added
- Sanitized ET0-004 runtime connectivity evidence from Dify components on `rdapp` to the declared data backend endpoints.

### Changed
- Replaced the reachability task with a narrower active-connection-evidence task; no architecture conclusion was made from reachability alone.
- Recorded direct runtime evidence for PostgreSQL/Redis connections and retained Qdrant usage as unknown after no active connection was observed.
- Recorded safe backend health/version evidence and documented unauthenticated Redis and Qdrant-version limitations.
- Recorded observed critical listeners and scheduled a Stage 0 completion review.
- Recorded the Stage 0 Completion Review outcome as further safe evidence work required before the architecture transition gate.
- Recorded sanitized local-Redis active-connection evidence without inferring configuration or non-use.
- Recorded one Dify SSRF proxy classification, two non-critical unclassified containers, and the Stage 0 architecture decision gate.

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
