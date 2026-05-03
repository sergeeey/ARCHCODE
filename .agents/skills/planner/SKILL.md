---
name: planner
description: Use this skill to plan project work, decompose tasks, define risks, and produce execution checklists.
---

# Skill: planner

Use when:

- task affects 3+ files
- requirements are ambiguous
- change can impact contracts, data, or security

Workflow:

1. Build dependency map (files/modules/docs/contracts).
2. Read relevant context.
3. Enumerate risks.
4. Produce execution plan with rollback and verification.
5. Stop for explicit approval.

Output contract:

- `Context analyzed`
- `Risks`
- `Plan`
- `Rollback`
- `Verification`
- `Approval gate`

Hard rules:

- no implementation edits before approval
- no unverifiable promises
