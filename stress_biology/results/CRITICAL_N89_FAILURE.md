# CRITICAL: Hypothesis FAILS at n=89

**Date:** 2026-04-25  
**Status:** 🔴 HYPOTHESIS REJECTED — Month 2 checkpoint FAILED  
**Verdict:** r < 0 (WRONG DIRECTION) at larger sample size

---

## Summary

**Progression of r values:**

| N | Spearman r | p-value | Status |
|---|-----------|---------|--------|
| 5 | -0.500 | 0.391 | WRONG (dismissed as small sample) |
| 49 | **+0.364** | 0.010 | CORRECT (celebration!) |
| 89 | **-0.173** | 0.106 | WRONG (disaster) |

**What happened:**
- Adding PRAD (n=20) + THCA (n=20) reversed the correlation
- Effect disappeared and flipped sign
- Hypothesis FAILS Month 2 checkpoint (r < 0.1)

---

## The Killer Data

**Tissue-by-tissue (sorted by doubling time):**

| Doubling Time | Mutation Rate | Tissue | Pattern |
|--------------|--------------|--------|---------|
| 15h | 1.92 mut/Mb | LAML | ✓ baseline |
| 18h | 1.36 mut/Mb | GBM | ✓ similar |
| **24h** | **16.57 mut/Mb** | **COAD** | ⚠️ OUTLIER |
| 48h | 6.18 mut/Mb | LUAD | ? intermediate |
| **72h** | **0.31 mut/Mb** | **THCA** | ✗ BREAKS PATTERN |
| 100h | 1.47 mut/Mb | BRCA | ✓ low |
| **120h** | **0.86 mut/Mb** | **PRAD** | ✗ BREAKS PATTERN |

**The problem:**
- **PRAD (120h):** Longest doubling time → 0.86 mut/Mb (VERY LOW)
- **THCA (72h):** Long doubling time → 0.31 mut/Mb (LOWEST!)
- **Expected:** longer time → MORE mutations
- **Reality:** longest times → FEWEST mutations

---

## Why n=49 Looked Good

**n=49 included:** COAD, BRCA, LUAD, GBM, LAML

**These 5 tissues happened to show:**
- COAD (24h): 16.57 (high outlier)
- LUAD (48h): 6.18 (medium)
- BRCA (100h): 1.47 (low)

**Spurious pattern:** faster proliferation → higher rates

**But this was ACCIDENTAL:**
- COAD is MSI-high enriched (not proliferation effect)
- Sampling bias: picked tissues that fit hypothesis

---

## Why n=89 Kills It

**Adding PRAD + THCA revealed:**
- PRAD (120h): Slowest proliferation → 0.86 mut/Mb
- THCA (72h): Slow proliferation → 0.31 mut/Mb

**These DON'T fit the hypothesis!**

**New correlation:** r = -0.17 (NEGATIVE!)
- Longer doubling time → FEWER mutations (opposite of prediction)

---

## Root Cause: COAD is an Outlier Tissue

**COAD alone drives the n=49 signal:**

Without COAD:
- 4 tissues (BRCA, LUAD, GBM, LAML): r ≈ 0.1 (weak)
- With COAD: r = 0.36 (inflated)

**COAD characteristics:**
- Mean: 16.57 mut/Mb (5-10× higher than other tissues)
- Std: 29.20 (huge variance)
- Outliers: 34.9, 94.6 mut/Mb (MSI-high)

**Conclusion:** COAD MSI-high contamination created false signal

---

## Checkpoint Status

**Month 2 Kill Criterion:** r < 0.1  
**Actual:** r = -0.17  
**Verdict:** ✗ **FAILED**

**Month 3 would require:** r > 0.3  
**Actual:** r = -0.17 (nowhere close)

---

## Possible Explanations

### 1. Hypothesis is Wrong

**Original:** Fast division → more Q state → more mutations  
**Reality:** No correlation (or inverse)

**Alternative interpretations:**
- Fast division → MORE repair opportunities → FEWER accumulated errors
- Tissue-specific repair mechanisms matter more than proliferation
- ATP hypothesis applies to radiation damage, not replication errors

### 2. COAD MSI-high Confounding

**If we exclude COAD:**
- 6 tissues, n=79
- Expected: r improves?
- Or: r stays negative?

**Test needed:** Remove COAD, recalculate

### 3. Tissue Heterogeneity Dominant

**Proliferation within tissue may matter, but:**
- Between-tissue comparison confounded by:
  - DNA repair capacity (tissue-specific)
  - Cell type (epithelial vs blood)
  - Microenvironment
  - Telomere dynamics

---

## Decision Tree

### Option A: Kill Project (Recommended)

**Verdict:** Hypothesis REJECTED at n=89

**Actions:**
1. Write negative result paper
2. Title: "No Evidence for Proliferation Rate-Mutation Rate Link in TCGA Pan-Cancer Analysis"
3. Journal: PLOS Computational Biology, F1000Research
4. Value: Prevents others from pursuing wrong hypothesis

**Timeline:** 1 month to manuscript

### Option B: Exclude COAD, Re-test

**Rationale:** COAD MSI-high may be a confounder

**Test:** n=79 (without COAD)  
**Result:** r = -0.052, p = 0.649 (NOT SIGNIFICANT)

**Verdict:** ✗ **HYPOTHESIS STILL DEAD**
- Correlation remains negative (though weak)
- COAD was NOT the only problem
- THCA (72h) → 0.31 mut/Mb, PRAD (120h) → 0.86 mut/Mb still break pattern
- Effect is genuinely NULL or reversed, not COAD artifact

### Option C: Pivot to H3 (ATP Proxy)

**Skip doubling time entirely, test:**
- ATP proxy (OXPHOS expression) vs mutation rate
- Direct mechanism test (not proliferation proxy)

**Risk:** If ATP proxy also fails → project dead

### Option D: Within-Tissue Test

**Different approach:**
- Same tissue, different proliferation rates
- Requires: single-cell markers (Ki67, MKI67)
- Downloads: RNA-seq for same samples

**Risk:** High effort, low probability of success

---

## Pre-Registration Saved Us

**Why this matters:**

Without pre-registration:
1. See n=49: r=0.36 → "Hypothesis confirmed!"
2. Publish in Bioessays
3. n=89 later shows r=-0.17 → Retraction

**With pre-registration:**
1. Predicted r>0.4 BEFORE data
2. n=49: r=0.36 (weak, but promising)
3. n=89: r=-0.17 (hypothesis KILLED)
4. Honest negative result (no retraction needed)

**Lesson:** Small samples mislead. n=49 was NOT enough.

---

## Comparison to ARCHCODE

**ARCHCODE:**
- Initial: AUC=0.69 (physics)
- Baseline: AUC=0.98 (category alone)
- Verdict: Physics adds nothing

**Stress Biology:**
- Initial (n=49): r=0.36 (doubling time)
- Expanded (n=89): r=-0.17 (doubling time)
- Verdict: Effect was spurious

**Both projects:** Rigorous testing killed initial promising results

---

## Recommendations

**Immediate (Week 2):**
1. Test without COAD (r=??? for n=79)
2. If still r<0 → kill project
3. Write negative result paper

**Month 3:**
- Publish negative result
- Value: scientific honesty, prevents wasted effort

**Don't pursue:**
- More sample collection (won't fix fundamental issue)
- p-hacking (pre-registration prevents this)
- Pivot to H3 without strong justification

---

## Status

🔴 **HYPOTHESIS REJECTED**

**Month 2 checkpoint:** FAILED (r=-0.17 < 0.1 requirement)

**Recommendation:** Kill project, publish negative result

---

**Generated:** 2026-04-25  
**Analyst:** Claude Sonnet 4.5 + Sergey Boyko  
**Data:** n=89 samples, 7 tissues (COAD, BRCA, LUAD, GBM, LAML, PRAD, THCA)
