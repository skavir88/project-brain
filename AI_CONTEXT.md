# Enterprise AI — AI Context

## Mandatory First Read
Read this file first in every work session. The Project Brain has 10 authoritative Markdown files in the repository root.

## Mandatory Reading Order
1. `AI_CONTEXT.md`
2. `CURRENT_STATE.md`
3. `NEXT_TASK.md`
4. `MASTER_PLAN.md`
5. `ARCHITECTURE.md`
6. `PROJECT.md`
7. `DECISIONS.md`
8. `DESIGN_SYSTEM.md`
9. `SESSION_LOG.md`
10. `CHANGELOG.md`

## Operating Contract
- Execute only the single atomic task in `NEXT_TASK.md`.
- Separate `planned`, `configured`, `deployed`, `verified`, and `unknown`. Only reproducible evidence may support `verified`.
- Inspect affected files before changing them; use the smallest safe scope; run the listed verification commands.
- Record architecture changes in `DECISIONS.md`, state changes in `CURRENT_STATE.md`, changes in `CHANGELOG.md`, and each changing session in `SESSION_LOG.md`.
- Leave one testable atomic next task when work is complete.

## Safety and Evidence
- Do not install, remove, restart, reconfigure, or otherwise change infrastructure without explicit user approval.
- Do not store or disclose secrets, tokens, passwords, private keys, real organizational data, environment variables, or unreviewed raw evidence.
- Treat missing infrastructure access as a documented limitation, never as verification.
- Resolve a material conflict through a recorded decision; do not silently choose a narrative.

## Stage Boundary
Stage 0 is discovery, baseline, documentation, policy, and automation foundation only. Production deployment, HA/DR, real-data integration, complete product development, and Stage 1 work are out of scope unless explicitly tasked.
