# G4-3 Hypothesis — KILLED

**Date:** 2026-04-26  
**Status:** ❌ HYPOTHESIS REJECTED  
**Reason:** Failed pre-registered kill criteria (AUC < 0.65)

---

## Hypothesis

**H-G4-3:** Λ-index (G4-load / helicase-capacity) predicts G4-clearance vulnerability

**Prediction:** High Λ → high dependency on helicase genes (WRN, BLM, BRIP1, DHX36, PIF1, RTEL1)

**Data:** DepMap 26Q1 (n=1,190 cell lines)
- Expression: WRN, BLM, BRIP1, DHX36, PIF1, RTEL1, RAD51, BRCA1, BRCA2, PALB2, MYC, EGFR
- CRISPR: Gene effect scores (helicase dependency)

---

## Pre-Registered Kill Criteria

**KILL if:**
1. AUC(Λ → helicase dependency) ≤ 0.65
2. Spearman ρ not significant (p > 0.05) AND effect size < 0.2

---

## Results (Real Data)

### Mock Validation (n=500 synthetic)
- **AUC:** 0.827 ✓
- **Verdict:** PASS (misleading)

### Real Data Validation (n=1,190 DepMap)

| Metric | Value | Threshold | Verdict |
|--------|-------|-----------|---------|
| **AUC** | **0.467** | > 0.65 | ❌ **KILL** |
| Spearman ρ | 0.046 | p<0.05 | ❌ Not significant |
| Q4 vs Q1 dependency | -0.337 vs -0.350 | Q4 < Q1 | ❌ **Opposite direction** |

### Per-Gene Results

| Gene | Spearman ρ | p-value | Significance |
|------|------------|---------|--------------|
| **WRN** | **-0.102** | 0.0004 | *** (weak signal) |
| BLM | -0.010 | 0.72 | — |
| BRIP1 | +0.093 | 0.001 | ** (wrong sign) |
| DHX36 | -0.052 | 0.07 | — |
| PIF1 | +0.035 | 0.23 | — |
| RTEL1 | +0.091 | 0.002 | ** (wrong sign) |

**Only WRN showed weak negative correlation** (expected direction, but too weak)

---

## Kill Decision

**Criteria 1:** AUC = 0.467 < 0.65 → **KILL TRIGGERED** ✓  
**Criteria 2:** ρ = 0.046 (p=0.11) → **Not significant** ✓

**Verdict:** **HYPOTHESIS KILLED** per pre-registered protocol

---

## Why Failed?

### Primary Reasons

1. **G4-load proxy inadequate:**
   - Formula: `G4_load = MYC*10 + EGFR*5 + 100`
   - Assumption: MYC/EGFR expression ≈ G4 burden
   - Reality: Too simplistic, no direct G4 measurement

2. **Helicase capacity formula simplistic:**
   - Formula: `capacity = SUM(WRN, BLM, BRIP1, DHX36, PIF1, RTEL1, RAD51, BRCA1, BRCA2, PALB2)`
   - Assumption: Equal weights, additive
   - Reality: WRN-specific signal suggests non-uniform importance

3. **Λ-index = ratio of two weak proxies:**
   - Double uncertainty propagation
   - Mock data masked this (no confounders)

### Secondary Factors

4. **Confounding variables:**
   - Cancer type, proliferation rate, other DDR pathways
   - Not controlled in analysis

5. **CRISPR dependency ≠ drug sensitivity:**
   - Genetic dependency may differ from pharmacological vulnerability
   - Should have used drug response (but CX-5461 not in DepMap)

---

## Mock vs Real Data

**Why mock succeeded (AUC=0.827) but real failed (AUC=0.467)?**

| Factor | Mock Data | Real Data |
|--------|-----------|-----------|
| G4-load | Synthetic (β=2.0 true effect) | Proxy (MYC/EGFR, weak) |
| Confounders | None | Cancer type, proliferation, etc. |
| Noise | Controlled (30% variance) | Real biological variance |
| Sample size | n=500 | n=1,190 (more power to detect weakness) |

**Lesson:** Mock validation insufficient without reality-check on real data subset.

---

## What Worked

✅ **Process:**
- Pre-registered kill criteria
- Honest falsification
- No p-hacking when faced with failure

✅ **Pipeline:**
- Built in 2.5 hours
- Modular, reusable scripts
- Clear documentation

✅ **Scientific integrity:**
- Followed kill criteria despite sunk cost (4 hours work)
- Documented negative result

---

## What Failed

❌ **Proxy metrics:**
- G4-load calculation too simplistic
- Helicase capacity additive assumption wrong

❌ **Mock validation:**
- Misleading positive result
- Should have tested on 50-100 real samples first

❌ **Hypothesis complexity:**
- Λ = ratio of two proxies = compounded uncertainty
- Simpler hypotheses preferable

---

## Lessons Learned

### For Next Hypothesis

1. **Prefer direct measurements over calculated proxies**
   - If no G4-seq data → don't calculate G4-load
   - If no drug response → don't predict drug sensitivity

2. **Mock validation + small real data subset**
   - Don't trust mock alone (AUC=0.827 → 0.467 collapse)
   - Test on 50-100 real samples before full analysis

3. **Simpler hypotheses = stronger tests**
   - Single gene (WRN) showed signal
   - Complex index (Λ) failed
   - Next: test direct relationships, not derived metrics

4. **Pre-registration protects integrity**
   - Kill criteria worked as designed
   - Prevented p-hacking temptation
   - Negative result = valid scientific outcome

---

## Alternative Interpretations

**Could hypothesis be salvaged?**

**Option A:** Focus on WRN only (weak signal ρ=-0.102)
- **Problem:** Still below significance threshold
- **Risk:** Post-hoc cherry-picking

**Option B:** Better G4-load calculation (G4Hunter scores)
- **Problem:** Violates pre-registration
- **Risk:** P-hacking until success

**Option C:** Different endpoint (mutation burden, not CRISPR)
- **Problem:** Changes hypothesis
- **Risk:** Moving goalposts

**Decision:** None acceptable. Hypothesis KILLED.

---

## Publication Potential

**Negative Result Publishable:**
- Pre-registered protocol ✓
- Adequate sample size (n=1,190) ✓
- Clear falsification ✓
- Methodologically sound ✓

**Target journals:**
- PLOS ONE (negative results welcome)
- F1000Research (post-publication review)
- bioRxiv preprint

**Title:** "Λ-Index Does Not Predict G4-Helicase Dependency in Cancer Cell Lines: A Pre-Registered Negative Result"

---

## Next Steps

**NOT doing:**
❌ Refining G4-load formula to "save" hypothesis
❌ Searching for subset where it works
❌ Adding covariates until p<0.05

**Doing:**
✅ Document (this file)
✅ Extract lessons (above)
✅ Choose next hypothesis with:
   - Direct measurements (no complex proxies)
   - Available data (DepMap expression/CRISPR)
   - Quick falsifiability (1-2 days max)

---

## Time Investment

| Activity | Time | Outcome |
|----------|------|---------|
| Pipeline build | 2.5 hours | ✓ Reusable code |
| Mock validation | 0.5 hours | ✗ Misleading (AUC=0.827) |
| Real data analysis | 1.5 hours | ✓ Honest result (AUC=0.467) |
| Documentation | 0.5 hours | ✓ This file |
| **Total** | **5 hours** | **Process success, outcome failure** |

**ROI:** 5 hours → validated pipeline + negative result + lessons learned = **success**

Outcome failure ≠ process failure. This is how science works.

---

## Final Verdict

**G4-3 Hypothesis:** ❌ **KILLED**

**Reason:** Failed pre-registered kill criteria (AUC=0.467 < 0.65)

**Integrity:** ✅ **PRESERVED** (followed protocol, no p-hacking)

**Lesson:** Proxy metrics unreliable, direct measurements essential

**Status:** Ready for next hypothesis

---

**Documented:** 2026-04-26, 10:15  
**Signed off:** Hypothesis testing protocol followed, kill criteria satisfied
