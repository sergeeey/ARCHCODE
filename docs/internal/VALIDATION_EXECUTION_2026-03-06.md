# VALIDATION_EXECUTION_2026-03-06

## Task

Task 3: Weak CTCF Paradox (isolated weak-site ablation with stability check across seeds)

## Implemented

- Updated script:
  - `scripts/test_weak_ctcf.ts`
- Changes:
  - Added `--locusPreset` (`hbb` | `weak_probe`).
  - Added `weak_probe` preset with a central weak convergent pair to ensure weak-barrier encounters.
  - Added explicit Go/No-Go gate in output (`goNoGo`, `noGoReason`).
  - Updated no-event verdict to `NO_GO_NO_WEAK_EVENTS` (instead of silent inconclusive wording).
  - Default output filename now date-based (`task3_weak_ctcf_isolated_YYYY-MM-DD.json`) when `--out` is not provided.
- New artifacts:
  - `results/task3_weak_ctcf_isolated_2026-03-06_seed0.json`
  - `results/task3_weak_ctcf_isolated_2026-03-06_seed10000.json`
  - `results/task3_ctcf_summary_2026-03-06.json`

## Verified

- Smoke checks:
  - `npx tsx scripts/test_weak_ctcf.ts --locusPreset=weak_probe --runs=10 --steps=3000 --seedOffset=0 --out results/task3_weak_ctcf_isolated_smoke.json`
    - Result: `SUPPORTED_IN_MODEL` (weak events present).
  - `npx tsx scripts/test_weak_ctcf.ts --locusPreset=hbb --runs=10 --steps=3000 --seedOffset=0 --out results/task3_weak_ctcf_isolated_smoke_hbb.json`
    - Result: `NO_GO_NO_WEAK_EVENTS`.

- Full runs (protocol evidence):
  - `npx tsx scripts/test_weak_ctcf.ts --locusPreset=weak_probe --runs=200 --steps=36000 --seedOffset=0 --out results/task3_weak_ctcf_isolated_2026-03-06_seed0.json`
  - `npx tsx scripts/test_weak_ctcf.ts --locusPreset=weak_probe --runs=200 --steps=36000 --seedOffset=10000 --out results/task3_weak_ctcf_isolated_2026-03-06_seed10000.json`
  - Observed:
    - Seed0: `weakEncounter=237`, `weakReadthroughRate=0.1561`, `delta=0.0`, verdict `SUPPORTED_IN_MODEL`
    - Seed10000: `weakEncounter=224`, `weakReadthroughRate=0.1071`, `delta=0.0`, verdict `SUPPORTED_IN_MODEL`
    - Both runs: `hasWeakEvents=true`

- Summary generation:
  - PowerShell aggregation created:
    - `results/task3_ctcf_summary_2026-03-06.json`
  - Observed summary verdict: `SUPPORTED_IN_MODEL`

- Regression safety checks:
  - `npm test -- src/__tests__/regression/gold-standard.test.ts`
    - Result: PASS (12/12)
    - Key metrics: HBB `r=0.888`, Sox2 `r=0.662`, Pcdh `r=0.668`
  - `npm run test:coverage`
    - Result: PASS (gate `50/55/50/50`)
    - Coverage: Statements `64.81`, Branches `55.00`, Functions `67.90`, Lines `64.68`

## UNVERIFIED

- External biological validation for weak-site readthrough effect remains missing.
- The isolated result is model-internal and should not be presented as clinical causality.

## Risks

- `weak_probe` is a synthetic probe preset to guarantee event observability; it is not an external experimental locus.
- In this model version, barrier blocking is controlled by global efficiency parameters; site strength mostly affects loop strength, not blocking probability directly.

## Verdict

`READY` for Task 3 protocol status update at model-validation level (`SUPPORTED_IN_MODEL`), with explicit external-validation disclaimer.

