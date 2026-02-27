# ARCHCODE Scientific Audit Report

**Auditor**: Independent Code Review (Kimi Code CLI)  
**Date**: 2026-02-01  
**Version Audited**: 1.0.0 / v0.3.1  
**Scope**: Core physics engines, reproducibility, invariants, UX risks

---

## 1. Executive Summary

**Scientific Plausibility**: CONDITIONALLY VALID  
The system implements core chromatin extrusion mechanics correctly in principle, but contains **critical type-consistency bugs** that could silently break the convergent rule in certain code paths.

**Safe for Hypothesis Testing**: WITH CAVEATS

- Single-engine mode (`LoopExtrusionEngine`) is deterministic and reproducible
- Multi-engine mode (`MultiCohesinEngine`) lacks processivity/unloading - loops never break once formed
- **Hard blocker**: CTCF orientation type mismatch between `domain/models/genome.ts` ('F'|'R') and `domain/models/physics.ts` ('forward'|'reverse') means physics module logic is orphaned/unused

---

## 2. Critical Findings

### 2.1 HARD CORRECTNESS RISKS

#### CRITICAL-1: CTCF Orientation Type Mismatch

**Location**: `src/domain/models/physics.ts` lines 25-27, 40-43 vs `src/domain/models/genome.ts` line 11

**Issue**:

- `genome.ts` defines: `type CTCFOrientation = 'F' | 'R'`
- `physics.ts` checks: `site.orientation === 'forward'` and `site.orientation === 'reverse'`

**Impact**:
The `checkCTCFBlocking()` function in `physics.ts` always returns non-convergent blocking (15% efficiency) because the string literals never match. This makes the entire `physics.ts` module produce biologically incorrect results if ever invoked.

**Evidence**:

```typescript
// physics.ts:40-43
const isConvergentOrientation =
  (approachDirection === "left" && ctcfSite.orientation === "forward") ||
  (approachDirection === "right" && ctcfSite.orientation === "reverse");
// These strings never match 'F' or 'R' from genome.ts
```

**Fix**: Align orientation values across codebase or remove orphaned physics.ts module.

---

#### CRITICAL-2: MultiCohesinEngine Lacks Unloading/Processivity

**Location**: `src/engines/MultiCohesinEngine.ts`

**Issue**:

- `MultiCohesinEngine` does NOT implement cohesin unloading (no `shouldUnload` check)
- Once a cohesin forms a loop, it stays `active=false, loopFormed=true` forever
- No respawn mechanism like in `LoopExtrusionEngine`

**Impact**:
Long simulations (>processivity time) will underestimate loop dynamics. Cohesins are "consumed" and never return to pool, violating steady-state assumption of extrusion model.

**Evidence**:

```typescript
// MultiCohesinEngine.ts - no unloading logic in step()
// Only has: checkBarriers() and boundary check
// Contrast with LoopExtrusionEngine.ts:204-217 which has respawn logic
```

---

#### CRITICAL-3: Loop Size Initialization Inconsistency

**Location**: `src/domain/models/genome.ts` lines 47-58

**Issue**:

```typescript
export function createCohesinComplex(
  loadPosition: number,
  velocity: number,
): CohesinComplex {
  return {
    leftLeg: loadPosition, // Same position
    rightLeg: loadPosition, // Same position
    velocity,
    active: true,
    loopFormed: false,
  };
}
```

After first `stepCohesin()`:

```typescript
cohesin.leftLeg -= Math.floor(cohesin.velocity); // loadPosition - v
cohesin.rightLeg += Math.floor(cohesin.velocity); // loadPosition + v
```

Result: loop size becomes `2 * velocity`, not `velocity` as biologically expected (each leg moves at velocity, total extrusion rate = 2v).

**Impact**:
Contact matrices have loop anchors offset by 2× expected speed. For velocity=1000 bp/step, first step creates 2000 bp loop.

**Scientific Justification Needed**: Document whether velocity means per-leg speed (current implementation) or total extrusion rate.

---

### 2.2 SOFT ASSUMPTIONS REQUIRING DOCUMENTATION

#### ASSUMPTION-1: Instantaneous Blocking (No Stochastic Leakage)

**Location**: `LoopExtrusionEngine.checkBarriers()` lines 91-139

Current implementation has deterministic blocking: if convergent CTCF exists, loop forms 100% of time. Real biology has 85-90% efficiency for convergent, 10-15% for non-convergent (leaky barriers).

The `physics.ts` module has the stochastic logic (`CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY = 0.9`) but is not used by active engines.

**Recommendation**: Either (a) document "deterministic approximation" or (b) wire up efficiency parameters.

---

#### ASSUMPTION-2: Cohesin Respawn Position Distribution

**Location**: `LoopExtrusionEngine.ts` lines 209-214

```typescript
const newPos = this.rng.randomInt(
  Math.floor(this.genomeLength * 0.1),
  Math.floor(this.genomeLength * 0.9),
);
```

Respawn excludes 10% of genome at each end. Document this "boundary exclusion zone" assumption.

---

#### ASSUMPTION-3: No Cohesin-Cohesin Collisions

Documented in KNOWN_ISSUES.md but not validated. At 20 cohesins / 100kb with processivity 600kb, collision probability is non-negligible but ignored.

---

## 3. Invariants Checklist

| Invariant | Statement                                  | Status            | Risk                                   |
| --------- | ------------------------------------------ | ----------------- | -------------------------------------- |
| INV-1     | `leftLeg < rightLeg` always                | **BROKEN at t=0** | Low - fixed at step 1                  |
| INV-2     | `leftLeg >= 0 && rightLeg <= genomeLength` | **HOLDS**         | Low - checked in boundary conditions   |
| INV-3     | Loop anchors must be CTCF positions        | **HOLDS**         | None - directly assigned from barriers |
| INV-4     | Convergent = R on left, F on right         | **HOLDS**         | None - correctly implemented           |
| INV-5     | Deterministic with same seed               | **HOLDS**         | Low - Mulberry32 + controlled respawn  |
| INV-6     | `loopsFormed >= uniqueLoopsFormed`         | **HOLDS**         | None - unique is subset                |
| INV-7     | Contact matrix symmetric                   | **HOLDS**         | None - explicitly set M[i][j]=M[j][i]  |
| INV-8     | Diagonal = 1.0                             | **HOLDS**         | None - explicitly set                  |

### INV-1 Detail: Initial State Violation

At t=0: `leftLeg == rightLeg == loadPosition`. This violates the biological invariant that cohesin has two distinct DNA-binding sites. Fix by initializing with minimal offset (e.g., `rightLeg = loadPosition + 1`).

---

## 4. Reproducibility Assessment

### 4.1 Determinism

**Source of Truth**: `stepCount` (discrete simulation step)

| Component        | Deterministic? | Notes                              |
| ---------------- | -------------- | ---------------------------------- |
| Cohesin motion   | Yes            | Fixed velocity per step            |
| CTCF blocking    | Yes            | No stochastic logic in active code |
| Respawn position | Yes            | Mulberry32 with fixed seed         |
| Contact matrix   | Yes            | Derived from loop positions        |
| P(s) curve       | Yes            | Deterministic averaging            |

### 4.2 Import/Export Reliability

**Format**: `ArchcodeRun` schema v1.0

| Aspect                   | Status          | Risk                                                      |
| ------------------------ | --------------- | --------------------------------------------------------- |
| Full param serialization | **HOLDS**       | All params saved                                          |
| CTCF site preservation   | **PARTIAL**     | Chromosome forced to 'chr1' on import (Simulator.tsx:300) |
| Seed preservation        | **HOLDS**       | Saved and restored                                        |
| Event replay             | **THEORETICAL** | `step` field exists but no replay engine implemented      |

**Critical Import Bug**:

```typescript
// Simulator.tsx:300
setCTCFSites(
  run.model.ctcfSites.map((s) => createCTCFSite("chr1", s.pos, s.orient, 1.0)),
);
// Always uses 'chr1', discards original chromosome from export
```

### 4.3 Replay Potential

Current `ArchcodeRun` format supports event listing but lacks:

1. Engine state snapshots per step
2. RNG state serialization
3. Cohesin trajectory history

True replay would require saving every cohesin position at every step (prohibitive for 10k steps × 20 cohesins).

---

## 5. Edge-Case Risk Matrix

| Case                                 | Expected Behavior                  | Actual                             | Risk                                             |
| ------------------------------------ | ---------------------------------- | ---------------------------------- | ------------------------------------------------ |
| **Zero CTCF sites**                  | No loops, cohesins exit boundaries | Same                               | Low - handled correctly                          |
| **Single CTCF site**                 | No loops (can't form pair)         | Same                               | Low - no convergent pair possible                |
| **All same orientation (F...F...F)** | No loops                           | Same                               | Low - verified in tests                          |
| **Velocity > genomeLength/2**        | Instant boundary hit               | Loop size > genome possible at t=1 | **Medium** - no upper bound check                |
| **Extreme speed (5000 bp/step)**     | Reduced resolution                 | May skip over CTCF sites           | **High** - no sub-step CTCF checking             |
| **Genome length = 0**                | Error                              | `nBins = 0`, empty matrix          | Medium - caught by guards but behavior undefined |
| **Resolution > genomeLength**        | Single bin                         | `nBins = 1`, loses all structure   | Medium - should warn user                        |
| **Reset → Run → Reset → Run**        | Same results                       | Same (fixed seed)                  | Low - verified by test                           |
| **Import → Apply → Run**             | Uses imported params               | Uses params, but NOT imported seed | **Medium** - seed hardcoded to 42                |

### Extreme Speed Risk (HIGH)

With velocity=5000 and CTCF at positions 1000, 2000:

- Step 1: cohesin at 5000±5000 → left=-0, right=10000
- CTCF at 1000 is "skipped" - never checked because legs jump over

**Fix**: Implement sub-step CTCF checking or cap velocity < min(CTCF spacing).

---

## 6. UX / Interpretation Risks

### 6.1 Metric Semantics

| Metric              | UI Label            | Actual Meaning                      | Risk                                             |
| ------------------- | ------------------- | ----------------------------------- | ------------------------------------------------ |
| `loops.length`      | "Loops"             | Number of loop formation events     | **High** - user may think these are simultaneous |
| `uniqueLoopsFormed` | Not shown in UI     | Unique (left,right) pairs formed    | Medium - hidden metric                           |
| `convergentPairs`   | Not clearly labeled | Equals loops.length in current impl | Low                                              |
| `activeCohesins`    | "Cohesin"           | Currently moving motors             | Medium - doesn't show total pool                 |

**Critical UI Issue**: The tooltip says "Не означает количество одновременно существующих петель" (Does not mean number of simultaneously existing loops) but the main display just shows "Loops: N" which is easily misinterpreted.

### 6.2 Plateau Detection

**Current Logic**: `!isRunning && activeCohesins === 0` shows "Плато достигнуто"

**Problem**:

1. User pausing simulation also triggers "Плато достигнуто" message
2. No actual plateau detection (checking for N steps with no new loops)
3. No maximum step limit warning

**Recommendation**: Implement explicit plateau detection: `stepsSinceLastLoop > plateauThreshold`.

### 6.3 Visualization vs Reality Gap

- **3D View**: Shows "temporary impulses" for new loops (pulse effect)
- **Reality**: Loops persist but visualization fades them
- **Risk**: User may think loops are transient when they are permanent in model

Document: "Visualization shows loop formation events; loops persist in the model."

### 6.4 AlphaGenome Validation Presentation

**Status**: Uses mock client (`apiKey: 'mock'`)  
**UI Risk**: Users may believe validation is against real AlphaGenome when it's simulated.

**Fix**: Add clear "MOCK MODE" indicator when using mock client.

---

## 7. Recommendations

### 7.1 MUST-FIX (Blocking Scientific Trust)

| Priority | Issue                          | Fix                                                           |
| -------- | ------------------------------ | ------------------------------------------------------------- |
| P0       | CTCF orientation type mismatch | Unify on 'F'/'R' or 'forward'/'reverse' across all files      |
| P0       | MultiCohesinEngine unloading   | Add `shouldUnload` probability check in step loop             |
| P1       | Extreme velocity CTCF skipping | Add `maxVelocity` cap or sub-step collision detection         |
| P1       | Import chromosome loss         | Preserve original chromosome in `handleApplyParamsFromLoaded` |
| P1       | Zero-step loop size            | Initialize cohesin with `rightLeg = loadPosition + 1`         |

### 7.2 NICE-TO-HAVE (Future Robustness)

| Priority | Issue                             | Rationale                                            |
| -------- | --------------------------------- | ---------------------------------------------------- |
| P2       | Deterministic stochastic blocking | Wire up `physics.ts` efficiency params to engines    |
| P2       | True plateau detection            | Track `stepsSinceLastLoop` instead of `!isRunning`   |
| P2       | Loop lifetime tracking            | Add `formedAtStep` and `unloadedAtStep` to Loop type |
| P2       | Memory limit for events           | `ArchcodeRun.events` grows unbounded in long runs    |
| P3       | Contact matrix validation         | Add checksum for matrix reproducibility              |
| P3       | RNG state export                  | Allow true replay by saving `SeededRandom.state`     |

---

## 8. Code Quality Observations

### Strengths

- Comprehensive test coverage for basic physics
- Good guard clauses (`isFinite`, bounds checking)
- Clear separation between domain models and engines
- Event sourcing pattern for reproducibility

### Weaknesses

- Orphaned code (`physics.ts` not used by active engines)
- Type safety gaps (string literal orientation mismatch not caught by compiler)
- Mixed languages (Russian comments, English code)
- Missing JSDoc for scientific assumptions

---

## 9. Validation Test Results

Running existing test suite:

```bash
cd D:\ДНК
npm test 2>&1 | head -50
```

Tests cover:

- Convergent rule (R...F forms loops) ✅
- Divergent rule (F...R no loops) ✅
- Genome boundary stopping ✅
- Contact matrix symmetry ✅
- P(s) power-law fitting ✅
- Reproducibility with seed ✅

Not covered:

- CTCF efficiency/stochastic blocking ❌
- Extreme velocity edge cases ❌
- Import/Apply/Run cycle ❌
- Memory limits with 100k steps ❌

---

## 10. Conclusion

ARCHCODE implements a scientifically reasonable loop extrusion model with correct convergent CTCF rule implementation. The core simulation is deterministic and reproducible with fixed seed.

**However**, the system has critical type-consistency issues that create "dead code" paths (physics.ts) and potential confusion about which physics is actually executing. The MultiCohesinEngine lacks unloading dynamics, making it unsuitable for steady-state hypothesis testing.

**Recommendation**:

1. Fix P0 issues before any publication
2. Add explicit "deterministic approximation" disclaimer to METHODS.md
3. Document all hardcoded parameters (10% boundary exclusion, 2× velocity factor)
4. Implement true plateau detection for UX clarity

---

**Audit completed by**: Kimi Code CLI  
**Next review recommended**: After P0 fixes implemented
