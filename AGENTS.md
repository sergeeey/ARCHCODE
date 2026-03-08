# AGENTS.md - Codex Operating Contract (Zero-Hallucination Mode)

Scope: this file is for Codex-driven work in this repository. It does not impose process on humans unless they choose to follow it.

## Authority and precedence

1. `CLAUDE.md` scientific integrity constraints are mandatory and override everything below.
2. This `AGENTS.md` defines execution protocol for Codex tasks in this repository.
3. If rules conflict, choose the stricter rule and state the conflict explicitly.

## Non-negotiable objective

Goal: zero hallucinations in code, docs, claims, and status reporting.

This means:
- No unverified claims.
- No "done" without evidence.
- No "verified" without command output or artifact path.
- No invented references, data, APIs, files, or benchmark numbers.

## Mandatory protocol

### Phase 1: Context and analysis

Before proposing changes:
1. Map dependencies for target files/modules (imports, callers, docs/contracts impacted).
2. Read relevant context files.
3. List breaking-change risks:
- API/schema/type contract changes
- data format changes
- security/secret exposure risks
- reproducibility and validation risks

### Phase 2: Execution plan

Provide a concrete plan with:
1. Step-by-step edits
2. Rollback strategy
3. Verification strategy (exact commands and expected artifacts)

### Phase 3: Approval gate

Stop and wait for explicit user approval (`APPROVE` or `PROCEED`) before implementation edits.

### Phase 4: Execution

Implement only approved plan scope. If scope changes, return to Phase 2.

## Implemented vs Verified (required in every completion)

### Implemented

List only what was changed:
- file paths
- behavioral impact
- contract changes

### Verified

List only what was proved:
- commands run
- pass/fail outcome
- produced artifact paths

If a test/command was not run, say so explicitly.

## Source-of-truth policy

For every factual claim, include one of:
- local artifact/file path
- reproducible command result
- approved external source link (if web research was requested)

If evidence is missing, label as `UNVERIFIED`.

## Security and secret hygiene

Always enforce:
- no real secrets in repo
- no secret values in logs/output
- no accidental `.env` leakage
- redact tokens/keys in examples

Before concluding work, run secret-hygiene checks when applicable.

## Change-safety rules

- Prefer minimal surface area changes.
- Do not modify unrelated files.
- Do not claim KPI improvements without evidence artifacts.
- Keep production path unified; if bypass path is used, state it explicitly.

## Review standard

Default review order:
1. Spec compliance (does the change solve the requested problem)
2. Code/document quality
3. Regression and security risk

Final verdict vocabulary:
- `READY`
- `NEEDS_FIXES`
- `BLOCKED`

