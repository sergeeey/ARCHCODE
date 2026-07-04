# ADR-035: Loop Extrusion Collision Detection — Known Limitation

**Date:** 2026-05-25
**Status:** ACCEPTED (deferred fix)
**Context:** External code audit (2026-05-25) identified bug #1 in `LoopExtrusionEngine.ts` / `MultiCohesinEngine.ts`
**Materiality:** ❌ NOT material for active AlphaGenome 7/7 loci claim (router code path, killed April 2026)

---

## Problem

`checkBarriers()` uses retroactive detection:

```typescript
const leftBarriers = this.ctcfSites.filter(
  (site) => site.orientation === "R" && site.position <= cohesin.leftLeg,
);
```

This finds **any** R-site left of current leftLeg, not just those reached in the current step. Effect: if the genome contains an R-site to the left of the cohesin's load position, the left leg appears "blocked" from step 1, before any extrusion has occurred.

## Impact

| Metric | Affected? | Severity |
|--------|-----------|----------|
| **Loop anchor positions** | ❌ NO — final anchors are physically correct | None |
| **Contact matrix structure** | ❌ NO — equilibrium contacts correct | None |
| **Loop duration statistics** | ✅ YES — systematically underestimated | High |
| **Loop formation step count** | ✅ YES — first-step bias | High |
| **AlphaGenome 7/7 claim** | ❌ NO — uses external API, not simulation | None |
| **Router (TDRA) claim** | ✅ YES — but already killed April 2026 (AUC=0.52) | N/A |

## Why This Slipped Through

1. Existing test (`LoopExtrusionEngine.test.ts:32-55`) loads cohesin **between** convergent barriers, so retroactive logic coincidentally produces correct anchors.
2. No adversarial test for "cohesin loaded outside convergent pair" scenarios.
3. Router claim was killed (April 2026) before the bug became material to any active result.

## Attempted Fix

Initial collision-detection rewrite (filter `site.position >= leftLeg && < leftLeg + velocity`) broke 4 regression tests because the proper fix requires **stalled-state semantics**:

- When left leg first reaches a barrier → mark `leftStalled = true`, snap `leftLeg` to barrier position
- `stepCohesin()` must not move stalled legs
- Loop forms when **both** legs are stalled on convergent barriers

This requires:
- New fields in `CohesinComplex`: `leftStalled`, `rightStalled`, `leftBarrier`, `rightBarrier`
- Refactor of `stepCohesin()` in `genome.ts`
- Update of all regression tests with new step counts
- Re-run of any simulation-derived figures in manuscript

Estimated effort: 4–6 hours.

## Decision

**DEFER fix** until one of:
1. Router claim is revived (currently killed, low probability)
2. Reviewer requests reproduction of simulation pipeline
3. Submission Methods description requires accurate loop duration statistics

**Current mitigation:**
- Code comment in `checkBarriers()` flags the limitation
- This ADR documents the bug, impact, and fix plan
- Methods section of manuscript only describes anchor positions (which are correct), not loop duration

## Manuscript Disclosure

The simulation Methods section (`manuscript/manuscript_v2_full.md` lines 54, 104) describes cohesin extrusion mechanics. The bug does **not** invalidate the description — convergent rule and anchor positions are correct. Loop duration is not claimed.

No correction needed in current manuscript version.

## Related Findings (external audit)

- Bug #1 (this ADR) — retroactive barrier detection
- Bug #2 — Python/TS PRNG drift (separate ADR-036)
- Bug #3 — contactMatrix OOM cap missing diagonal (separate ADR-037)
- Bugs #4–8 — naming, boundary, docs (deferred technical debt)

## References

- External audit report (user-provided, 2026-05-25)
- `src/engines/LoopExtrusionEngine.ts:141-160` — retroactive filter
- `src/engines/MultiCohesinEngine.ts:418-437` — duplicate retroactive filter
- `src/__tests__/LoopExtrusionEngine.test.ts:32-55` — test that misses the bug
- ARCHCODE H5 (TDRA router) kill commit: `f6016ed` (April 15, 2026)
