# Skill: security-check

Use when:

- changes touch config, auth, network, data export, CI/CD, secrets, or logs
- preparing for merge/release

Checklist:

1. Secret hygiene

- no real keys/tokens/passwords in repo
- no secrets in command output or docs examples
- `.env` excluded and examples sanitized

2. Data and privacy hygiene

- no unintended PII exposure
- logs avoid sensitive payloads

3. Supply-chain and command safety

- avoid destructive commands
- verify dependency/tooling changes are intentional

4. Evidence

- provide command-based checks and paths to findings

Output contract:

- `Security findings`
- `Risk level`
- `Required fixes`
- `Verification evidence`
