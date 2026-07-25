# AI Context

## Mandatory First Read
This file must be read first at the start of every AI or Codex work session for Arandi Platform.

## Mandatory Reading Order
1. `AI_CONTEXT.md`
2. `PROJECT.md`
3. `CURRENT_STATE.md`
4. `NEXT_TASK.md`
5. `DECISIONS.md`
6. `MASTER_PLAN.md`
7. `ARCHITECTURE.md`
8. `DESIGN_SYSTEM.md`
9. `CHANGELOG.md`

## AI Operating Rules
- Use real Arandi Platform project data only.
- Never use sample-project assumptions.
- Never invent architecture, services, modules, or roadmap items.
- Never skip current state review.
- Never start coding or documentation work without understanding `NEXT_TASK.md`.
- Keep documentation concise, operational, and enterprise-grade.
- Update state files after completing work.
- Record meaningful documentation or project-state changes in `CHANGELOG.md`.

## Codex Behavior
Every Codex task must include:
- project name
- current phase
- relevant files
- exact task objective
- constraints
- expected output
- test or validation method
- commit message suggestion

Codex output must be reviewed before acceptance. No Codex change is accepted only because it was generated.

## Forbidden Behavior
- Introducing unapproved dependencies.
- Adding undocumented services or integrations.
- Changing architecture without recording a decision in `DECISIONS.md`.
- Modifying roadmap without updating `MASTER_PLAN.md`.
- Completing work without updating `CURRENT_STATE.md` and `NEXT_TASK.md`.
- Leaving sample-project content in any Project Brain file.

## End-of-Session Updates
At the end of every work session, update:
- `CURRENT_STATE.md`
- `NEXT_TASK.md`
- `CHANGELOG.md` when documentation or project state changes
- `SESSION_LOG.md` if introduced later
