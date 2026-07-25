# Decisions

## Decision 001 — Use Project Brain Repository
Decision: Maintain a dedicated documentation repository as the AI/project control layer.

Reason: Prevent context loss and guide AI-assisted development from a single operational source of truth.

## Decision 002 — Use 9-File Documentation Structure
Decision: Use the approved 9 Markdown files as the project documentation framework.

Reason: Standardize context for human operators and AI workflows while avoiding uncontrolled document growth.

## Decision 003 — Enter Phase 0.5 Before Coding
Decision: Complete Codex Workflow preparation before Phase 1 implementation.

Reason: Avoid uncontrolled coding, missing context, and architecture drift.

## Decision 004 — Use Real Project Data Only
Decision: Replace all sample-project content with Arandi Platform-specific information.

Reason: Prevent architecture contamination, documentation drift, and incorrect AI assumptions.

## Decision 005 — Commit and Changelog Discipline
Decision: Every meaningful documentation or project change must be committed and reflected in `CHANGELOG.md`.

Reason: Maintain traceability and make project state reviewable across human and AI sessions.
