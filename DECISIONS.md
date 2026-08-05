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
