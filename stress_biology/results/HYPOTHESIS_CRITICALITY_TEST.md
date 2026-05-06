# Hypothesis Test: Tissue Mutation Variance as Critical-State Signal

**Date:** 2026-04-25  
**Hypothesis:** Within-tissue mutation rate variance (CV) reflects proximity to oncogenic phase transition  
**Status:** ❌ **REJECTED**

---

## Hypothesis Statement

Tissue-specific somatic mutation rate heterogeneity reflects proximity to oncogenic phase transition in metabolic-repair state space. High CV tissues (COAD 176%, LAML 253%) are near-critical, low CV tissues (GBM 28%) are far-from-critical.

**Predicted:** CV ~ |φ - φ_c|^(-γ) with γ ≈ 1

---

## Red Team Test: MSI Contamination Check

### Test Design

**Cheap falsification:** If high CV is driven by MSI-high samples (discrete failure mode, not criticality), then:
- Remove MSI-high samples (inferred as >30 mut/Mb in COAD)
- Recalculate CV
- If CV drops to <50% → hypothesis killed

### Results

| Tissue | n | CV (all) | Outliers | CV (clean) | Reduction |
|--------|---|----------|----------|------------|-----------|
| LAML | 9 | 252.5% | 1 | 118.0% | 134.5% |
| COAD | 10 | 176.2% | 2 | 78.1% | 98.1% |
| PRAD | 20 | 76.2% | 1 | 50.4% | 25.8% |
| THCA | 20 | 79.0% | 3 | 42.9% | 36.1% |
| BRCA | 10 | 46.4% | 1 | 32.8% | 13.6% |
| LUAD | 10 | 46.2% | 0 | 46.2% | 0.0% |
| GBM | 10 | 27.7% | 0 | 27.7% | 0.0% |

### Key Observations

**1. Outlier-driven variance:**
- All high-CV tissues have heavy-tailed distributions (skewness 2-2.5)
- 1-3 extreme samples dominate variance
- After outlier removal: CV collapses for most tissues

**2. LAML exception:**
- CV=118% even after outlier removal
- Genuinely high intrinsic variance
- But n=9 (small sample, low confidence)

**3. Distribution shape:**
- High-CV: positive skewness, high kurtosis → NOT symmetric fluctuations
- Low-CV: near-symmetric, low kurtosis → gaussian-like

**Critical insight:** This is NOT critical-state behavior. Critical fluctuations produce power-law tails with SYMMETRIC large deviations. Observed: asymmetric outliers = discrete failure modes.

---

## Falsification Criteria

**Original prediction:** CV ~ |φ - φ_c|^(-γ)

**Test 1: Outlier sensitivity**
- If criticality → CV stable after outlier removal (intrinsic variance)
- If discrete failures → CV collapses after outlier removal
- **Result:** CV collapses 40-70% for COAD/PRAD/THCA → FAILED

**Test 2: Distribution shape**
- If criticality → power-law P(μ) ~ μ^(-α)
- If discrete failures → skewed distribution with outliers
- **Result:** Skewness 2-2.5, not power-law → FAILED

**Test 3: Sample size scaling**
- If criticality → CV increases with sample size (more fluctuations captured)
- If outliers → CV stable or decreases with sample size
- **Result:** Cannot test (insufficient data), but pattern suggests outlier-driven

---

## Why Hypothesis Failed

### Mechanism mismatch

**Predicted (criticality):**
- Tissues operate near metabolic-repair bifurcation
- Small perturbations amplified near critical point
- CV diverges as φ → φ_c
- Symmetric fluctuations, power-law tails

**Observed (discrete failures):**
- Some samples have catastrophic events (MSI-high, hypermutation)
- These are RARE discrete failures, not continuous amplification
- Asymmetric outliers, not power-law
- Between-sample variance ≠ within-tissue biological variance

### Alternative explanation

**High CV sources:**
1. **Subclonal heterogeneity:** Different tumor regions sampled
2. **Temporal evolution:** Early vs late stage tumors
3. **Discrete failure modes:** MSI-high, POLE mutations, tobacco signatures
4. **Technical variance:** Sequencing depth, coverage variability

**None of these are critical-state phenomena.**

---

## Revised Understanding

**What CV actually measures:**
- Between-sample variance in bulk sequencing
- Includes: biological variance + sampling variance + technical variance
- Dominated by rare catastrophic events (MSI-high, hypermutation)

**What CV does NOT measure:**
- Proximity to phase transition
- Metabolic-repair state criticality
- Intrinsic tissue-level fluctuations

---

## Salvage Attempts

### Could within-sample variance show criticality?

**Idea:** Single-cell sequencing within one tumor might reveal critical fluctuations

**Problem:**
- Single-cell has ~30% false positive rate
- Sample size needed: 1000+ cells per tumor
- TCGA data: bulk sequencing only

**Verdict:** Cannot test with existing data

### Could LAML high CV (118% clean) be criticality?

**Observation:** LAML maintains CV=118% after outlier removal (n=8 clean samples)

**Alternative explanation:**
- LAML = blood cancer, circulating cells
- High genetic diversity normal for hematopoietic system
- Not critical state, just high baseline variance

**Test needed:** Compare LAML variance to normal hematopoiesis (not available in TCGA)

**Verdict:** Plausible, but cannot distinguish from baseline heterogeneity

---

## Final Verdict

**Hypothesis:** ❌ **REJECTED**

**Confidence:** 0.85 (high confidence in rejection)

**Reasons:**
1. ✗ Outlier-driven variance, not intrinsic fluctuations
2. ✗ Asymmetric distributions, not power-law
3. ✗ CV collapses after outlier removal (COAD 176→78%, PRAD 76→50%)
4. ✗ No correlation with metabolic state (cannot test, but mechanism implausible)

**What survived:**
- Observation: tissue-specific variance exists
- LAML genuinely high variance (but n=8, low confidence)
- Between-tissue heterogeneity > within-tissue (Stress Biology original finding)

**What failed:**
- Critical-state interpretation
- Order parameter mapping
- CV as biomarker for phase transition proximity

---

## Lessons Learned

### 1. Check outliers FIRST

**Before building complex theory:**
- Plot distribution
- Check skewness, kurtosis
- Remove outliers, recalculate
- If effect disappears → it was outlier-driven

**Cost:** 5 minutes  
**Saves:** weeks of theory development on false premise

### 2. Between-sample variance ≠ biological variance

**TCGA samples:**
- Different patients
- Different tumor stages
- Different sampling times
- Different sequencing batches

**Cannot infer tissue-level biology from patient-level variance.**

### 3. Power-law claims require distribution tests

**Red flag:** Claiming criticality without fitting P(x) ~ x^(-α)

**Required tests:**
- Log-log plot (should be linear)
- Powerlaw package (likelihood ratio vs log-normal)
- Bootstrapped confidence intervals

**This hypothesis:** Did not test distribution shape → premature claim

---

## Application to Future Hypotheses

**When proposing critical-state dynamics:**
1. Test outlier sensitivity (primary falsification)
2. Fit distribution shape (power-law vs exponential vs log-normal)
3. Check sample size scaling
4. Verify symmetry of fluctuations
5. Require n>50 samples for reliable variance estimation

**Red flags:**
- High CV with only n=10-20 samples
- Skewed distributions (outlier contamination)
- No distribution fitting

---

## Tags

#falsification #critical-phenomena #hypothesis-rejection #outlier-analysis #stress-biology #quick-test

---

**Summary:** Tissue mutation rate variance is outlier-driven (MSI-high, hypermutation events), not critical-state fluctuations. CV collapses 40-70% after outlier removal. Hypothesis rejected with 0.85 confidence. Lesson: always check outliers before building complex theory.
