# AUDIT_RESPONSE.md

**Original Audit**: ARCHCODE Scientific Audit Report (2026-02-01)  
**Response Date**: 2026-02-01  
**Status**: P0 Fixes Implemented  
**Structure**: ISO 42010-style Architecture Viewpoints + Evidence

---

## Executive Summary

This document provides a formal response to the independent scientific audit of ARCHCODE v1.0. All P0 (blocking) findings have been addressed. The model is now scientifically correct with respect to CTCF orientation handling, cohesin unloading dynamics, and data preservation. The response is organized by **Stakeholder Concerns** and **Architecture Viewpoints** for traceability and funding/peer-review use.

---

## Stakeholder Concerns

- **Scientific correctness**: Model behavior must match literature (convergent rule, cohesin dynamics).
- **Reproducibility**: Fixed seed must yield identical outcomes; no loss of run/import data.
- **Publication readiness**: Claims must be evidence-backed; limitations explicitly stated.

---

## Viewpoints and Findings

### 1. Physics View (Loop Extrusion Model)

This view covers the loop extrusion engine, CTCF barriers, and cohesin dynamics.

#### 1.1 ✅ CRITICAL-1: CTCF Orientation Type Mismatch — FIXED

**Problem**: `physics.ts` used `'forward'|'reverse'` while `genome.ts` used `'F'|'R'`, causing the convergent rule to fail in the physics module.

**Solution**:
- Updated `src/domain/models/physics.ts` to use `'F'` and `'R'` literals
- Imported `CTCFOrientation` type from `./genome` for type safety
- Functions affected: `isConvergent()`, `checkCTCFBlocking()`

**Verification**:
```typescript
// After (FIXED):
const isConvergentOrientation =
    (approachDirection === 'left' && ctcfSite.orientation === 'F') ||
    (approachDirection === 'right' && ctcfSite.orientation === 'R');
```

**Evidence**:
- Implementation: `src/domain/models/physics.ts` (orientation checks, imports from genome)
- Regression: `src/__tests__/regression/gold-standard.test.ts` (convergent/divergent scenarios)
- Commit: `fix(domain): unify CTCF orientation type to 'F'|'R'`

**Impact**: The physics module now correctly identifies convergent CTCF pairs (R...F) with 85% efficiency as specified in `CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY`.

---

#### 1.2 ✅ CRITICAL-2: MultiCohesinEngine Missing Unloading — FIXED

**Problem**: MultiCohesinEngine did not implement cohesin unloading, violating the steady-state assumption of loop extrusion.

**Solution**:
1. Added `shouldUnload()` using `COHESIN_PARAMS.UNLOADING_PROBABILITY` (0.0005/step)
2. Implemented `handleRespawn()` with bookmarking efficiency (50%)
3. Added stochastic blocking using `CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY` (85%)
4. Added `seed` and RNG reset in `reset()` for reproducibility

**Evidence**:
- Implementation: `src/engines/MultiCohesinEngine.ts` (unloading, respawn, blocking)
- Constants: `src/domain/constants/biophysics.ts` (COHESIN_PARAMS, CTCF_PARAMS)
- Reproducibility: `src/utils/random.ts` (SeededRandom); tests with fixed seed in `src/__tests__/regression/`
- Commit: `fix(engines): add cohesin unloading and stochastic blocking to MultiCohesinEngine`

**Biological justification**: Unloading probability calibrated to ~20 min mean residence time (Gerlich et al., 2006); convergent efficiency 85% from Rao et al. (2014).

---

### 2. Data View (Contact Matrix, Events, Formats)

This view covers data produced by the model and how it is preserved (BED, ArchcodeRun, contact matrix).

#### 2.1 ✅ CRITICAL-3: Chromosome Loss on Import — FIXED

**Problem**: `handleApplyParamsFromLoaded()` used hardcoded `'chr1'`, discarding chromosome from imported runs.

**Solution**:
- Extended `ArchcodeRun` to include `chromosome` in `model`
- `buildRunInitial()` captures chromosome from first CTCF site
- `handleApplyParamsFromLoaded()` uses saved chromosome with fallback

**Evidence**:
- Schema: `src/domain/models/experiment.ts` (model.chromosome, ctcfSites[].chrom)
- Build: `src/utils/export-run.ts` (buildRunInitial)
- Apply: `src/pages/Simulator.tsx` (handleApplyParamsFromLoaded, chromosome from run.model)
- Commit: `fix(ui): preserve chromosome on run import`

---

### 3. Validation View (Tests, Ground Truth, Pearson r)

This view covers regression tests, gold-standard loci, and the source of ground truth (mock vs experimental Hi-C).

**Current state**:
- Regression tests: HBB, Sox2, Pcdh loci; target Pearson r ≥ 0.7
- Ground truth: **mock/synthetic** contact maps (not real AlphaGenome API)
- Publication target: validation against **experimental Hi-C** (e.g. Rao et al. 2014)

**Evidence**:
- Gold-standard tests: `src/__tests__/regression/gold-standard.test.ts`
- Validation client (mock): `src/validation/alphagenome.ts`
- Config: `config/default.json` (targetPearsonNote: vs experimental Hi-C)
- Run: `npm run test:regression` / `npm run validate:hbb`

---

## Correspondence Rules

- **Physics → Data**: Loop extrusion engine produces `Loop[]`; these are converted to contact matrices via `src/engines/contactMatrix.ts` (loopsToContactMatrix, computePSCurve). Experiment run format (ArchcodeRun) records events and stable pairs from the same engine state.
- **Data → Validation**: Contact matrices and P(s) curves are compared against gold-standard expectations (mock or, for publication, experimental Hi-C). Regression tests assert Pearson r and loop counts; evidence is in test files and CI logs.

---

## Scientific Impact Assessment

| Aspect | Before Audit | After Fixes | Status |
|--------|--------------|-------------|--------|
| Convergent CTCF rule | Partially broken | Fully functional | ✅ Fixed |
| Cohesin turnover | None (accumulation) | Stochastic unloading + respawn | ✅ Fixed |
| Steady-state dynamics | Violated | Maintained | ✅ Fixed |
| Data reproducibility | Chromosome loss | Full preservation | ✅ Fixed |
| Determinism | Seed ignored in reset | RNG reset on restart | ✅ Fixed |

---

## Parameter Classification

| Parameter | Type | Source | Uncertainty |
|-----------|------|--------|-------------|
| EXTRUSION_SPEED_BP_PER_S | Literature-based | Ganji et al. (2018) | ±50% (0.5–2 kb/s) |
| UNLOADING_PROBABILITY | Calculated | 1/meanResidenceSteps | Assumes exponential kinetics |
| CONVERGENT_BLOCKING_EFFICIENCY | Ensemble fit | Rao et al. (2014) | Single-molecule may differ |
| BOOKMARKING_EFFICIENCY | Assumed default | No direct measurement | HIGH uncertainty |

Steps are **dimensionless** discrete events; biological time mapping is a tunable parameter (see `docs/COGNITIVE_CORE.md`).

---

## Known Limitations (Scientific)

- **Time and step mapping**: "20 minutes" residence time is approximate and depends on BIOLOGICAL_TIME_SCALE.
- **Model parameters**: All efficiency values are model parameters fit to ensemble data, not physical constants.
- **AlphaGenome validation**: Currently **mock data**; publication should report correlation against experimental Hi-C. See KNOWN_ISSUES.md and docs/ALPHAGENOME.md.

---

## Remaining Risks (5C)

See subsection **5C** in KNOWN_ISSUES.md for Criteria / Condition / Cause / Consequence / Corrective action on remaining risks (e.g. unloading calibration, experimental Hi-C).

---

## Deferred Items (P1/P2)

- P1: Edge cases (extreme velocity, loop init size, Pause vs Plateau UX)
- P2: Real AlphaGenome API, WebGPU, supercoiling

---

## Re-audit Checklist

- [ ] `physics.ts` uses same orientation as `genome.ts` ('F'/'R')
- [ ] MultiCohesinEngine uses COHESIN_PARAMS.UNLOADING_PROBABILITY
- [ ] handleApplyParamsFromLoaded uses run.model.chromosome (not hardcoded 'chr1')
- [ ] RNG state resets on engine.reset()
- [ ] Stochastic blocking uses CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY

---

## References

1. Audit Report: `AUDIT_REPORT.md` (2026-02-01)
2. Known Issues: `KNOWN_ISSUES.md`
3. Cognitive Core: `docs/COGNITIVE_CORE.md`
4. Methods: `METHODS.md`
5. Sanborn et al. (2015). Chromatin extrusion. *PNAS*.
6. Rao et al. (2014). 3D map of the human genome. *Cell*.
7. Gerlich et al. (2006). Cohesin dynamics. *Cell*.
