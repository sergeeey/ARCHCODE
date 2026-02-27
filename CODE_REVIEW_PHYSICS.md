# Code Review: Physics Engines

**Reviewer**: Claude Code
**Date**: 2026-02-02
**Scope**: Core physics modules for loop extrusion simulation

---

## Executive Summary

| Component                | Status      | Critical Issues                           |
| ------------------------ | ----------- | ----------------------------------------- |
| `MultiCohesinEngine.ts`  | ✅ Good     | Minor: no leaky non-convergent            |
| `LoopExtrusionEngine.ts` | ⚠️ OK       | No stochastic blocking                    |
| `physics.ts`             | ❌ ORPHANED | Uses `Math.random()`, not used by engines |
| `genome.ts`              | ⚠️ OK       | INV-1 violation, wrong default velocity   |
| `contactMatrix.ts`       | ✅ Good     | Solid implementation                      |

**Overall**: Physics is scientifically correct for publication, but has code quality issues.

---

## 1. MultiCohesinEngine.ts (MAIN ENGINE)

### ✅ Correct Implementations

**1.1 Convergent CTCF Rule (lines 182-230)**

```typescript
// Left leg: ищем R (< ) слева
const leftBarriers = this.ctcfSites.filter(
  (site) => site.orientation === "R" && site.position <= cohesin.leftLeg,
);
// Right leg: ищем F (> ) справа
const rightBarriers = this.ctcfSites.filter(
  (site) => site.orientation === "F" && site.position >= cohesin.rightLeg,
);
```

**Verdict**: ✅ Correct — R blocks left leg, F blocks right leg = convergent trap

**1.2 Stochastic Blocking (lines 201-203)**

```typescript
const blockingEfficiency = CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY;
if (this.rng.random() < blockingEfficiency) {
```

**Verdict**: ✅ Correct — uses SeededRandom, respects efficiency parameter

**1.3 Unloading Dynamics (lines 96-100, 141-143)**

```typescript
private shouldUnload(): boolean {
    return this.rng.random() < COHESIN_PARAMS.UNLOADING_PROBABILITY;
}
```

**Verdict**: ✅ Correct — stochastic unloading with configurable probability

**1.4 Respawn with Bookmarking (lines 148-180)**

```typescript
if (this.rng.random() < COHESIN_PARAMS.BOOKMARKING_EFFICIENCY) {
    this.cohesins.push(createCohesinComplex(pos, this.velocity));
```

**Verdict**: ✅ Correct — maintains steady-state cohesin pool

### ⚠️ Issues Found

**1.5 No Leaky Non-Convergent Blocking**

```typescript
// Current: only checks convergent (R...F)
if (leftBarrier && rightBarrier) {
  // Only convergent pairs trigger blocking
}
```

**Problem**: Non-convergent configurations (F...R, F...F, R...R) should have 15% leaky blocking per `CTCF_PARAMS.NON_CONVERGENT_BLOCKING_EFFICIENCY`.

**Current behavior**: Non-convergent = no blocking at all
**Expected behavior**: 15% chance to block even without convergent pair

**Impact**: LOW — convergent dominates in real biology (>90% of loops)

**Fix**:

```typescript
// Add after convergent check:
} else if (leftBarrier || rightBarrier) {
    // Leaky barrier for non-convergent
    if (this.rng.random() < CTCF_PARAMS.NON_CONVERGENT_BLOCKING_EFFICIENCY) {
        // Single-sided stall (not full loop)
    }
}
```

**1.6 Boundary Margin Check**

```typescript
if (cohesin.leftLeg < -this.velocity || cohesin.rightLeg > this.genomeLength + this.velocity) {
```

**Issue**: Allows negative positions temporarily. Should be `< 0` for strict invariant.
**Impact**: LOW — cleaned up next step

---

## 2. LoopExtrusionEngine.ts (SINGLE COHESIN)

### ⚠️ Key Differences from MultiCohesinEngine

| Feature             | MultiCohesinEngine | LoopExtrusionEngine |
| ------------------- | ------------------ | ------------------- |
| Stochastic blocking | ✅ Yes (85%)       | ❌ No (100%)        |
| Unloading           | ✅ Yes             | ❌ No               |
| Respawn             | ✅ Bookmarking     | ✅ Random only      |
| SeededRandom        | ✅ Yes             | ✅ Yes              |

**Problem**: LoopExtrusionEngine uses **deterministic** blocking (100% if convergent found), not stochastic.

**Line 119-134**:

```typescript
if (leftBlocked && rightBlocked && leftBarrier && rightBarrier) {
    cohesin.active = false;
    cohesin.loopFormed = true;
    // No efficiency check!
```

**Impact**: MEDIUM — single-cohesin mode produces different physics than multi-cohesin

**Recommendation**: Add stochastic blocking to match MultiCohesinEngine, or document as "deterministic approximation mode".

---

## 3. physics.ts (ORPHANED CODE)

### ❌ Critical: Not Used by Active Engines

This module has correct physics logic but is **never called** by `LoopExtrusionEngine` or `MultiCohesinEngine`.

**Evidence**:

- No imports of `checkCTCFBlocking`, `stepPhysics`, etc. in engine files
- Engines implement their own barrier checking inline

### ❌ Critical: Uses Math.random()

**Lines 49, 56, 87, 94, 107**:

```typescript
shouldStop: Math.random() < CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY,
```

**Problem**: `Math.random()` breaks reproducibility with fixed seed.

**Fix**: Pass `SeededRandom` instance or use deterministic logic.

### ⚠️ Convergent Definition Inconsistency

**Line 26-28** (isConvergent function):

```typescript
function isConvergent(leftSite: CTCFSite, rightSite: CTCFSite): boolean {
  return leftSite.orientation === "F" && rightSite.orientation === "R";
}
```

This checks `F...R` (forward left, reverse right).

**But engines check** `R...F` (reverse left, forward right).

**Analysis**: Both are valid depending on perspective:

- `physics.ts`: "left site" = site on left genomic position
- `engines`: "left leg" = cohesin leg moving leftward

**The engines are correct** — the left LEG is blocked by REVERSE CTCF (pointing left, <).

**Recommendation**: Delete `physics.ts` or refactor to use engine's blocking logic.

---

## 4. genome.ts (Domain Models)

### ⚠️ INV-1 Violation at Initialization

**Lines 47-58**:

```typescript
export function createCohesinComplex(loadPosition: number, velocity: number = 1.0): CohesinComplex {
    return {
        leftLeg: loadPosition,      // Same position
        rightLeg: loadPosition,     // Same position
```

**Problem**: At t=0, `leftLeg == rightLeg`, violating the invariant that cohesin has two distinct binding sites.

**Impact**: LOW — fixed after first step, but `getCohesinLoopSize()` returns 0 at t=0.

**Fix**:

```typescript
leftLeg: loadPosition,
rightLeg: loadPosition + 1,  // Minimal offset
```

### ❌ Wrong Default Velocity

**Line 125**:

```typescript
export const DEFAULT_CONFIG: SimulationConfig = {
    ...
    velocity: 1.0,  // Should be 1000!
```

**Problem**: 1.0 bp/step is far too slow (1000× slower than intended).

**Impact**: HIGH if DEFAULT_CONFIG is used directly (appears to not be, engines override).

**Fix**: Change to `velocity: 1000,`

---

## 5. contactMatrix.ts (Analysis)

### ✅ Solid Implementation

**5.1 Distance Decay (lines 43-51)**

```typescript
const decayFactor = 1.0 / (distance + 1);
const baseline = backgroundLevel * decayFactor;
```

**Verdict**: ✅ Correct power-law decay approximation

**5.2 Loop Enhancement (lines 53-67)**

```typescript
const enhancement = (loop.strength ?? 1.0) * 10.0;
matrix[leftBin][rightBin] += enhancement;
matrix[rightBin][leftBin] += enhancement; // Symmetric
```

**Verdict**: ✅ Correct — symmetric matrix, strength-weighted

**5.3 P(s) Power-Law Fit (lines 131-177)**

```typescript
const alpha = numerator / denominator; // Slope in log-log space
```

**Verdict**: ✅ Correct linear regression in log-space

### Minor: Magic Number

**Line 63**: `* 10.0` — undocumented enhancement factor.

**Recommendation**: Move to `biophysics.ts` as `LOOP_ENHANCEMENT_FACTOR`.

---

## 6. Invariants Check

| Invariant                   | LoopExtrusionEngine | MultiCohesinEngine | Status   |
| --------------------------- | ------------------- | ------------------ | -------- |
| INV-1: `leftLeg < rightLeg` | ❌ Violated at t=0  | ❌ Violated at t=0 | Fix init |
| INV-2: Bounds check         | ✅                  | ⚠️ Allows margin   | OK       |
| INV-3: Loop anchors = CTCF  | ✅                  | ✅                 | OK       |
| INV-4: Convergent = R...F   | ✅                  | ✅                 | OK       |
| INV-5: Deterministic seed   | ✅                  | ✅                 | OK       |
| INV-6: loops ≥ unique       | N/A                 | ✅                 | OK       |
| INV-7: Matrix symmetric     | ✅                  | ✅                 | OK       |
| INV-8: Diagonal = 1.0       | ✅                  | ✅                 | OK       |

---

## 7. Recommended Fixes

### P0: Critical (Before Publication)

| #   | File            | Issue                | Fix                     |
| --- | --------------- | -------------------- | ----------------------- |
| 1   | `genome.ts:125` | `velocity: 1.0`      | Change to `1000`        |
| 2   | `physics.ts`    | Uses `Math.random()` | Delete file or refactor |

### P1: Important (Scientific Accuracy)

| #   | File                     | Issue                   | Fix                                     |
| --- | ------------------------ | ----------------------- | --------------------------------------- |
| 3   | `genome.ts:52-53`        | INV-1 violation         | Init with `rightLeg = loadPosition + 1` |
| 4   | `LoopExtrusionEngine.ts` | No stochastic blocking  | Add efficiency check or document        |
| 5   | `MultiCohesinEngine.ts`  | No leaky non-convergent | Add 15% blocking for single barriers    |

### P2: Code Quality

| #   | File                  | Issue               | Fix                 |
| --- | --------------------- | ------------------- | ------------------- |
| 6   | `contactMatrix.ts:63` | Magic number `10.0` | Move to constants   |
| 7   | `physics.ts`          | Orphaned code       | Delete or integrate |

---

## 8. Test Coverage Gaps

| Scenario                     | Covered? | File                  |
| ---------------------------- | -------- | --------------------- |
| Convergent R...F             | ✅       | gold-standard.test.ts |
| Divergent F...R              | ✅       | gold-standard.test.ts |
| Extreme velocity skip        | ❌       | Need test             |
| INV-1 at t=0                 | ❌       | Need test             |
| Stochastic blocking variance | ❌       | Need test             |
| Non-convergent leaky         | ❌       | Need test             |

---

## 9. Conclusion

The physics implementation is **scientifically correct for the core loop extrusion model**:

- Convergent CTCF rule implemented correctly
- Stochastic dynamics in MultiCohesinEngine
- Contact matrix generation is sound

**Main concerns**:

1. `physics.ts` is orphaned and uses `Math.random()`
2. `LoopExtrusionEngine` lacks stochastic blocking
3. Minor invariant violations at initialization

**Recommendation**: Fix P0 issues, delete orphaned `physics.ts`, document single vs multi-cohesin mode differences.

---

**Review completed by Claude Code**
