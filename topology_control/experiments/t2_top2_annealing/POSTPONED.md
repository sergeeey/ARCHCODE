# T2 Experiment — POSTPONED

**Date:** 2026-04-26
**Status:** Postponed due to O(n²) performance bottleneck
**Runtime:** >90 minutes without completion (stuck at model 1/3)

## Bottleneck Analysis

**Problem:**
- 200 rings → 40,000 pairs × 500 steps × 3 models = ~60M linking calculations
- Each calculation: Gauss linking integral with ~2500 quadrature points
- Total: ~150 billion floating point operations
- Result: hours of CPU time for toy model

**Evidence:**
- Test with 50 rings also failed to complete in 60s
- Process stuck at "[1/3] Running RANDOM (baseline)..."

## Optimization Required

**Before re-running:**
1. **Sparse matrix caching** — linking number doesn't change for untouched ring pairs
2. **NumPy Gauss quadrature** — `np.polynomial.legendre` 10-50× faster than double loop
3. **Multiprocessing** — parallelize linking calculations across cores
4. **Reduced scale** — 20-30 rings sufficient for proof-of-concept

**Expected speedup:** 50-100× (hours → minutes)

## Postpone Reason

**Tracy Zero-Based Decision:**
> "Зная что T2 займёт 4+ часа без оптимизации, начал бы я это сейчас?" → **НЕТ**

**Opportunity cost:**
- T2 = toy model, даже SUCCESS не даёт clinical application
- G4-3 = clinical ready, TCGA data доступны NOW
- 4 hours on T2 = потеря Week 1 G4-3 validation window

## Return Conditions

Resume T2 ONLY if:
1. G4-3 hypothesis killed (AUC < 0.65) OR completed
2. Optimization implemented (multiprocessing + sparse cache)
3. Clinical link clarified (how does annealing → disease mechanism?)

## Hypothesis Status

**H-TOPO-2 (TopoII+SMC annealing):** Not falsified, **postponed** pending optimization.

---

**Next Priority:** G4-3 Λ-index validation (clinical patient stratification)
