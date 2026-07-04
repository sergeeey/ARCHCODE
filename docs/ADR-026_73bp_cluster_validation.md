# ADR-026: 73bp HBB Promoter Cluster Validation

**Date:** 2026-05-08  
**Status:** WEAK (category leakage)  
**Context:** Independent validation of pearl enrichment hypothesis  

---

## Hypothesis

HBB pearl variants are enriched in promoter zone **chr11:5227099-5227172** (74bp, GRCh38).

**Pre-registration:** Zone coordinates fixed before analysis (not cherry-picked).

---

## Methodology

### 10-Step Validation Protocol

1. **Data:** HBB_Unified_Atlas.csv (N=1,103 variants, 20 pearls)
2. **Fixed zone:** chr11:5227099-5227172 (74bp)
3. **Enrichment calculation:** 15/20 pearls (75%) in zone vs 22/1,103 total variants (2.0%)
4. **Fisher exact test:** One-sided test for enrichment (alternative='greater')
5. **Permutation test:** 10,000 random samples, null distribution of expected overlap
6. **Negative control 1:** 100 random 74bp windows (test specificity)
7. **Negative control 2:** 100 shuffled Pearl labels (test positional signal)
8. **Category leakage check:** Promoter category distribution in zone vs outside
9. **Seed sensitivity:** Test 5 random seeds (1, 7, 21, 42, 100) for stability
10. **Verdict:** PASS / WEAK / FAIL based on combined criteria

---

## Results

### Observed Enrichment

| Metric | Value |
|--------|-------|
| **Variants in zone** | 22/1,103 (2.0%) |
| **Pearls in zone** | 15/20 (75.0%) |
| **Enrichment ratio** | 37.5× |

### Statistical Tests

**Fisher Exact Test:**
- Odds ratio: **461.14**
- p-value: **< 0.000001** ✓

**Permutation Test (10,000 samples):**
- Observed: 15 pearls
- Expected: 0.40 ± 0.63 (mean ± std)
- p-value: **< 0.000001** ✓

**Seed Sensitivity:**
- Seeds tested: 1, 7, 21, 42, 100
- p-value range: 0.000000
- Stability: **STABLE** ✓

### Negative Controls

**Random Windows (100 samples):**
- False positive rate (p<0.05): 7.37%
- Median p-value: 1.0000
- **CLEAN** ✓

**Shuffled Labels (100 shuffles):**
- False positive rate (p<0.05): 0.00%
- Median p-value: 1.0000
- **CLEAN** ✓

### Category Leakage Analysis

**Critical Finding:** HIGH leakage risk

| Metric | Value |
|--------|-------|
| **Dominant pearl category** | Promoter (75.0% of pearls) |
| **Zone category** | Promoter (68.2% of variants in zone) |
| **Outside category** | Promoter (0.0% of variants outside zone) |
| **Leakage verdict** | **HIGH RISK** ⚠️ |

**Interpretation:** Pearls are predominantly promoter variants (15/20), and the zone is predominantly promoter region (15/22 variants). This creates circular logic: enrichment is driven by **category assignment**, not by independent structural signal.

---

## Verdict

**Status:** WEAK  
**Confidence:** LOW  
**Reason:** Significant p-value (< 0.000001), but HIGH category leakage risk (pearl category overrepresented in zone)

### What This Means

1. **Statistically real:** Enrichment is not a random artifact (p < 0.000001, stable across seeds, clean negative controls)

2. **Biologically circular:** The signal is **driven by category labels** (promoter), not by 3D structural features:
   - Pearls = 75% promoter category
   - Zone = 68.2% promoter category
   - Outside zone = 0.0% promoter category
   - **Conclusion:** Enrichment reflects categorical overlap, not independent 3D signal

3. **Cannot claim as independent validation:** The 73bp zone is in the promoter region, and pearls are predominantly promoter variants. This is expected by definition, not a discovery.

---

## Honest Limitations

### What We Cannot Claim

❌ "73bp cluster is an independent validation of ARCHCODE structural predictions"  
❌ "Promoter zone shows unique 3D disruption signal"  
❌ "Enrichment proves mechanism-specific targeting"  

**Why:** Enrichment is confounded by category assignment. Promoter variants cluster in promoter regions by definition.

### What We Can Claim (with caveats)

✓ "Promoter pearls (15/20) cluster in promoter zone chr11:5227099-5227172 (p < 0.000001)"  
✓ "Enrichment is statistically robust (stable across seeds, clean negative controls)"  
⚠️ "However, this reflects categorical overlap, not independent 3D structural signal"

---

## Next Steps

### Option A: Category-Matched Control (Recommended)

Test enrichment **within promoter category only**:
- Null hypothesis: Random promoter variants
- Test: Do promoter pearls (N=15) cluster in 73bp zone more than random promoter variants?
- If YES → evidence of zone-specific mechanism
- If NO → enrichment is purely categorical

### Option B: Cross-Category Test

Test if non-promoter pearls (N=5) show similar enrichment in their respective genomic regions.
- If YES → general 3D disruption signal across categories
- If NO → promoter pearls are unique (but still confounded by category)

### Option C: Ablation Test

Remove promoter category entirely, test enrichment on remaining pearls (N=5).
- Expected: No enrichment (too few samples)
- Purpose: Quantify how much signal is driven by promoter category

---

## Files

- **Validation script:** `scripts/validate_73bp_cluster.py` (526 lines)
- **Results JSON:** `results/validate_73bp_cluster.json`
- **Data source:** `results/HBB_Unified_Atlas.csv` (1,103 variants, 20 pearls)

---

## Conclusion

The 73bp promoter cluster hypothesis shows **statistically significant enrichment** (p < 0.000001, OR = 461.14), but suffers from **HIGH category leakage**. Pearls are 75% promoter category, and the zone is in the promoter region — enrichment reflects categorical overlap, not independent 3D structural signal.

**Verdict:** WEAK — cannot use as independent validation without category-matched controls.

**Honest answer to "Can we claim this in the manuscript?"**  
→ **No.** Not without Option A (category-matched test) to rule out circularity.

**Null result honestly documented:** The hypothesis as stated ("promoter pearls enrich in promoter zone") is **true but trivial** — driven by category assignment, not 3D mechanism.

---

**Integrity note:** This analysis follows ADR-001 Falsification-First Protocol. Circular logic detected and disclosed. No hype, no breakthrough claims. Science survives honesty.
