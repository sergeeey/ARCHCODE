# Preliminary Results — Month 1, Week 1

**Date:** 2026-04-25  
**Status:** ⚠️ EARLY DATA — n=5 samples only  
**Analysis:** First test of H0 hypothesis

---

## Data Collected

| Tissue | Doubling Time (h) | Mutation Rate (mut/Mb) | Source |
|--------|------------------|------------------------|--------|
| LAML | 15 | 14.83 | TCGA (1 sample) |
| GBM | 18 | 1.87 | TCGA (1 sample) |
| COAD | 24 | 34.90 | TCGA (1 sample) |
| LUAD | 48 | 6.87 | TCGA (1 sample) |
| BRCA | 100 | 1.27 | TCGA (1 sample) |

**Doubling times:** Sender 2016 (Cell) — manual curation

---

## H0 Test Results

**Hypothesis:** Longer doubling time → MORE mutations  
**Predicted:** Spearman r > 0.4, p < 0.01

**Actual:**
- **Spearman r = -0.500** (NEGATIVE correlation)
- **p = 0.391** (not significant)

**Interpretation:** ✗ **WRONG DIRECTION**

The data shows the **opposite** of what was predicted:
- Shorter doubling time (faster proliferation) → FEWER mutations
- Longer doubling time (slower proliferation) → MORE mutations

---

## Visual Analysis

![Scatter plot](h0_preliminary.png)

**Key observations:**
1. **COAD outlier** — 34.9 mut/Mb (much higher than other tissues)
2. **BRCA low** — 1.27 mut/Mb (slowest proliferation, lowest mutations)
3. **LAML moderate** — 14.83 mut/Mb (fastest proliferation, moderate mutations)

---

## Critical Issues

### 1. Sample Size
- **n = 5** (target: n > 1000)
- 1 sample per tissue → **no variance estimate**
- Cannot test within-tissue correlation (confounding control)

### 2. COAD Outlier
- 34.9 mut/Mb is 3-6× higher than typical COAD
- Possible MSI-high (microsatellite instability)
- Need clinical data to check MSI status

### 3. Direction Paradox
**Original hypothesis:**
- Fast division → more time in Q state (low ATP) → more mutations

**Alternative interpretation:**
- Fast division → MORE divisions → MORE **repair cycles** → FEWER accumulated errors?
- Slow division → fewer repair opportunities → errors persist?

**OR:**
- The Bilinsky framework applies to **radiation damage**, not **replication errors**
- Different mechanisms for exogenous vs endogenous mutagenesis

---

## Next Steps

### Immediate (Week 2)

1. **Download more samples** (20-30 per tissue type)
   - Get variance estimates
   - Identify outliers systematically
   - Test within-tissue correlation

2. **Filter MSI-high samples**
   - Download clinical data from TCGA
   - Exclude MSI-high (known confounder)

3. **Re-test H0 with n > 100**
   - Spearman correlation
   - Bootstrap 95% CI
   - Bonferroni correction

### If r < 0 persists (wrong direction)

**Option A: Kill H0, investigate H0-inverted**
- Test: "Fast proliferation → BETTER repair → fewer mutations"
- Mechanism: More frequent S-phase checkpoints, DNA damage response

**Option B: Kill entire project**
- r < 0.3 after n > 100 → NULL result
- Publish negative result in PLOS Computational Biology
- Title: "No Evidence for Bilinsky-Inspired ATP-Mutagenesis Link in TCGA Data"

**Option C: Pivot hypothesis**
- Original: proliferation rate → mutation rate
- New: ATP levels → mutation rate (skip doubling time proxy)
- Test H3 directly (ATP proxy from RNA-seq)

---

## Statistical Power

Current:
- n = 5, r = -0.5, p = 0.391 (underpowered)

Required for r = 0.4, p < 0.01:
- n ≈ 50 (power = 0.8)
- n ≈ 100 (power = 0.95)

---

## Checkpoint Decision

**Month 2 Kill Criterion:** r < 0.1  
**Current:** r = -0.5 (worse than null)

**Recommendation:**
- Download n = 100-200 samples (Week 2)
- Re-test H0
- If r < 0 persists → **pivot to H3** (ATP proxy) or **kill project**

---

## Lessons from ARCHCODE

**Category confounding risk:**
- Tissue type may drive signal more than proliferation rate
- Need within-tissue test (same tissue, different proliferation)
- Baseline comparison: tissue type alone (no proliferation info)

**Matched controls:**
- Currently: unmatched (different tissues)
- Need: matched (same tissue, different samples)

**Pre-registration saved us:**
- We predicted r > 0.4
- Data shows r < 0
- Cannot p-hack our way out — hypothesis clearly wrong

---

## Status

⚠️ **WARNING: Preliminary data suggests hypothesis may be inverted or NULL**

**Next milestone:** Week 2 — download n=100+, re-test

**If hypothesis fails:** Month 3 checkpoint will KILL project or pivot to H3

---

**Generated:** 2026-04-25  
**Analyst:** Claude Sonnet 4.5 + Sergey Boyko  
**Code:** `stress_biology/` branch `feature/stress-biology-atp-mutagenesis`
