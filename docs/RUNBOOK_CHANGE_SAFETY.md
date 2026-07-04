# RUNBOOK_CHANGE_SAFETY

Purpose: execute security/quality/architecture changes with minimal regression risk.

Status model:
- Implemented: what was changed.
- Verified: what was proven by commands/artifacts.
- Not Verified: explicit gaps.

Principles:
- Small batch only (one risk class per PR).
- No hidden mode switching (`real` vs `mock`).
- No merge without evidence.
- Fast rollback always available.

---

## 1. Change Classes and Order

Mandatory order:
1. P0: gold-standard stability and explicit runtime mode.
2. P1: browser/node boundary split.
3. P1: dependency security updates.
4. P2: CI gate hardening and secret hygiene expansion.

Do not start P1/P2 while P0 is red.

---

## 2. Pre-Change Baseline (Required)

Run and save outputs before any risky changes:

```bash
npm run lint
npm run build
npm test
npm run security:deps
npm run security:python
npm run security:secrets
```

Save summary to:
- `docs/internal/BASELINE_YYYY-MM-DD.md`

Include:
- command,
- PASS/FAIL,
- short evidence line,
- known failures list.

---

## 3. PR Safety Protocol

For each PR:
1. Scope exactly one risk class.
2. List assumptions and expected blast radius.
3. Add/adjust tests before broad refactors when possible.
4. Execute only relevant verification commands.
5. Fill `Implemented vs Verified` section in PR description.

Mandatory references:
- `docs/PR_GATE.md`
- `docs/CODEX_ZERO_HALLUCINATION_GATES.md`

---

## 4. P0 Runbook (Regression + Runtime Mode)

### 4.1 Gold-standard triage

Run:

```bash
npm test -- gold-standard.test.ts
```

Capture exact failing cases and values (for example Pearson thresholds per locus).

Decision rule:
- If data/source changed: repair data path or update fixtures with rationale.
- If scoring changed: add regression test proving intended behavior.
- If threshold is unrealistic: change threshold only with written scientific rationale.

### 4.2 Explicit mode policy

Runtime mode must be explicit:
- `MODE=real` or `MODE=mock`.

Rules:
- No implicit fallback `real -> mock` in gold-standard path.
- If `MODE=real` prerequisites are unavailable, fail fast with clear error.
- In CI, run gold-standard in mode that matches policy (recommended: `real` or dedicated validated fixture mode).

Verification minimum:

```bash
npm test -- gold-standard.test.ts
npm test
npm run build
```

---

## 5. P1 Runbook (Architecture Boundary)

Target:
- Keep browser bundle free from node-only runtime dependencies.

Method:
1. Introduce `AlphaGenomeNodeService` (node-only: grpc/fs/child_process/path/url).
2. Keep browser side as thin HTTP/typed client.
3. Migrate call sites incrementally (one consumer at a time).
4. Keep compatibility shim until migration completes.

Verification minimum:

```bash
npm run build
npm test
```

Expected:
- no new externalization warnings from browser-critical paths.

---

## 6. P1 Runbook (Dependency Security Updates)

Branching rule:
- Use dedicated branch, e.g. `chore/deps-security-2026Q1`.

Process:
1. Update one toolchain group at a time (`vite/vitest/esbuild`).
2. Re-lock and run full checks after each batch.
3. Stop at first regression; fix or revert that batch.

Verification minimum:

```bash
npm run build
npm test
npm run security:deps
```

Acceptance:
- No high/critical advisories.
- No new test failures.

---

## 7. P2 Runbook (CI Gates + Secrets)

Target required checks on PR:
- `npm run lint`
- `npm run build`
- `npm test`
- `npm run security:deps`
- `npm run security:python`
- `npm run security:secrets`

Recommended additions:
- dedicated gold-standard job,
- coverage threshold gate,
- gitleaks diff scan on PR,
- scheduled full-history secret scan.

---

## 8. Rollback Protocol

Always define rollback before merge.

Preferred rollback:
1. Revert PR commit(s) completely.
2. Re-run baseline checks.
3. Confirm restored status in incident note.

Do not do partial/manual production hotfix edits if full revert is possible.

---

## 9. Evidence and Reporting

For every completed step, store short report in `docs/internal` using this shape:

- Task
- Implemented
- Verified
- Not Verified
- Security hygiene
- Verdict

Template reference:
- `docs/templates/IMPLEMENTED_VERIFIED_TEMPLATE.md`

---

## 10. Merge Criteria (Hard)

Merge allowed only when all are true:
- PR gate checklist completed.
- Claimed fixes have command evidence.
- No unresolved high/critical security findings.
- Rollback path documented and tested at least once in branch lifecycle.

If any item is missing: `NO MERGE`.
