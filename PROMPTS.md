# Prompts Library

This file stores only prompts that have proven useful during project development.

New prompts should be added only after successful usage.

---

# Project Initialization Prompt

Purpose:

Initialize AI understanding of the project architecture.


Prompt:

Read the following files before making any changes:

- .ai/PROJECT.md
- .ai/ARCHITECTURE.md
- .ai/CURRENT_STATE.md
- .ai/NEXT_TASK.md
- .ai/DESIGN_SYSTEM.md
- .ai/DECISIONS.md

Understand the project rules and implement only the active task.

Do not change architecture unless explicitly approved.

---

# Code Review Prompt

Purpose:

Review implemented code.


Prompt:

Review the current implementation according to:

- Architecture rules
- TypeScript best practices
- Component structure
- Maintainability
- Performance
- Security

Do not modify code unless requested.

---

# Feature Development Prompt

Purpose:

Implement a defined feature.


Prompt:

Before coding:

1. Read project documentation.
2. Understand current architecture.
3. Identify affected files.
4. Explain implementation plan.

After implementation:

1. Test the result.
2. Report changed files.
3. Suggest documentation updates.

---

# Bug Fix Prompt

Purpose:

Debug an issue.


Prompt:

Analyze the problem systematically.

Steps:

1. Reproduce the issue.
2. Identify root cause.
3. Apply the smallest correct fix.
4. Test the result.
5. Document the change.