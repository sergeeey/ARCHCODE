# Skill: reviewer

Use when:

- user asks for review
- changes are ready for gate decision

Two-pass review:

1. Spec compliance

- does implementation match request
- are contracts preserved
- are edge cases addressed

2. Quality and risk

- regressions
- tests and evidence sufficiency
- security and secret hygiene

Verdict:

- `READY`
- `NEEDS_FIXES`
- `BLOCKED`

Output contract:

- findings first, ordered by severity
- exact file references
- missing tests/evidence
- final verdict
