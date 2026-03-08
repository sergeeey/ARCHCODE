# Codex Zero-Hallucination Gates

This checklist is Codex-focused and complements `CLAUDE.md`.

## Required gates before declaring completion

1. Evidence gate
- Every factual claim must map to a file path, command output, or approved source.
- Unknown/assumed items must be labeled `UNVERIFIED`.

2. Verification gate
- No "verified" status without executed commands and observable results.
- Report results using `Implemented` vs `Verified`.

3. Security gate
- No real secrets in committed files.
- No secret leakage in examples, logs, or reports.

## Suggested local checks

Run from repo root:

```bash
rg -n "APPROVE|PROCEED|Implemented|Verified|UNVERIFIED" AGENTS.md docs .claude
rg -n "sk-|AKIA|AIza|xoxb-|ghp_|BEGIN PRIVATE KEY|password\\s*=|token\\s*=" -S .
```

For JS/TS changes:

```bash
npm run build
npm test
```

For Python/script changes:

```bash
python -m pytest
```

Note: run only commands relevant to changed scope.

