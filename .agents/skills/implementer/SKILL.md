# Skill: implementer

Use when:

- user approved a concrete plan
- required edits are clear and bounded

Workflow:

1. Apply edits exactly within approved scope.
2. Keep changes minimal and reversible.
3. Avoid touching unrelated files.
4. Run planned verification commands.
5. Report `Implemented` and `Verified` separately.

Output contract:

- files changed
- behavioral changes
- verification commands and outcomes
- unresolved items

Hard rules:

- if scope drift appears, stop and return to planning
- do not mark verified without command evidence
