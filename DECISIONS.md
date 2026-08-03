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
