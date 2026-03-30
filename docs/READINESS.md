# Readiness Assessment (ARCHCODE)

## Goal

Provide a repeatable scoring and evidence map for release readiness.

## Scoring rubric (0-10)

- 9–10: Production-ready Enterprise
- 7–8: Solid Startup / Growth
- 5–6: Works with risks
- 3–4: Tech debt dominates
- 1–2: Critical state

## Evidence checklist

- [ ] Score semantics documented
- [ ] Anti-inversion test present
- [ ] Golden set defined and stable
- [ ] Acceptance cases defined
- [ ] Failure modes mapped to detection
- [ ] Regression tests for bug fixes

## Current status (fill per release)

**Score:** \_\_/10

**Evidence links:**

- `D:\ДНК\docs\VALIDATION.md`
- `D:\ДНК\docs\INVARIANTS.md`
- `D:\ДНК\docs\FAILURE_MODES.md`
- `D:\ДНК\docs\PR_GATE.md`

## CI gates (2026-03-06 baseline)

- `security-gates.yml` enforces:
  - lint/build/unit tests
  - coverage gate at `60/55/60/60`
  - gold-standard regression tests (physics engine, no external API dependency)
  - dependency, python, and secret scans
- AlphaGenome mock system was removed (2026-03-30). Validation uses real API via `scripts/alphagenome_real_experiments.py`.
