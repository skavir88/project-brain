# Architecture

## Architecture Baseline
Architecture version: `v1.1 frozen baseline`.

This file documents the current real architecture and technical boundaries of Arandi Platform. It must not describe speculative product features or unapproved integrations.

## Current AI Infrastructure
- Dify `v1.16.0` is installed on `rdapp`.
- PostgreSQL is available on `rddb`.
- Redis is available on `rddb`.
- Qdrant is available on `rdvector`.
- GapGPT connection is prepared for LLM service delivery.

Core AI infrastructure is installed and ready for workflow integration.

## Server Responsibilities
- `rddb`: Database and Redis services.
- `rdapp`: Application layer and Dify runtime.
- `rdvector`: Vector database layer using Qdrant.
- `rdautomation`: Reserved for automation/workflow services.
- `rdmonitor`: Reserved for monitoring/observability services.

## System Separation
The Project Brain repository, AI orchestration layer, Codex development workflow, and future UI/application codebase are separate concerns.

- Project Brain repository: controls documentation, AI context, project state, decisions, roadmap, and task flow.
- AI orchestration layer: uses Dify and the prepared GapGPT LLM connection.
- Codex development workflow: receives controlled tasks with mandatory context and validation requirements.
- Future UI/application codebase: will be defined after Phase 0.5 and during Phase 1.

The documentation repository controls AI context but is not the runtime application.

## Architecture Constraints
- No undocumented service additions.
- No speculative integrations.
- No architecture drift without decision logging.
- No implementation assumptions outside approved project state.
- No sample-project architecture may remain in documentation.

## Future Architecture Expansion
Future expansion is reserved for Phase 1 and later. It may include frontend foundation, UI architecture, component structure, and application implementation details only after the Codex Workflow is finalized and relevant decisions are recorded.
