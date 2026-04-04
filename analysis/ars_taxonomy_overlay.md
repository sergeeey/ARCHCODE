# EXP-005: ARS (Architecture Risk Score) Overlay by Taxonomy Class

**Date:** 2026-03-09
**Branch:** feature/v4-prioritization-framework
**Question:** Do architecture-driven variants (Class B) tend to live in more structurally fragile loci?

---

## 1. Data Sources

| Source | File | Content |
|--------|------|---------|
| Fragility atlas HBB | `analysis/fragility_atlas_hbb.csv` | 159 bins, severe-level Delta_SSIM scan |
| Fragility atlas BRCA1 | `analysis/fragility_atlas_brca1.csv` | 200 positions, severe-level Delta_SSIM scan |
| Fragility zones HBB | `analysis/fragility_zones_hbb.json` | 0 severe zones (all SSIM > 0.9988) |
| Fragility summary BRCA1 | `analysis/fragility_atlas_brca1_summary.json` | 6 severe zones (min SSIM = 0.9236) |
| Taxonomy table | `analysis/taxonomy_assignment_table.csv` | 22 case assignments across 9 loci |
| Per-locus verdict | `analysis/per_locus_verdict.csv` | 9 loci with Q2b counts and verdicts |
| Cross-locus atlas | `results/cross_locus_atlas_comparison.json` | 13 loci, delta_LSSIM values |

---

## 2. Per-Locus Fragility vs. Taxonomy Class

### 2a. Loci with fragility atlas data (N=2)

| Locus | Severe Fragility Zones | Min SSIM (severe) | Max Delta_SSIM | Taxonomy Class | N_Q2b | Verdict |
|-------|----------------------|-------------------|----------------|---------------|-------|---------|
| HBB | 0 | 0.9505 (bin 27) | 0.0495 | B_architecture (confirmed) | 25 | PRIMARY |
| BRCA1 | 6 | 0.9236 (pos 43126000) | 0.0764 | B_architecture_tentative | 26 | EXPLORATORY |

**Key observation:** BRCA1 has more baseline fragility (6 severe zones, deeper SSIM drop) yet its Class B assignment is _tentative_ with only 3.8% precision. HBB has _zero_ severe fragility zones yet carries the strongest Class B evidence (100% Q2b precision, p=2.51e-31).

This is the **opposite** of what one would predict if baseline fragility drove Class B enrichment.

### 2b. All loci using cross-locus delta_LSSIM as fragility proxy

The cross-locus atlas provides `delta_LSSIM` (mean pathogenic - mean benign LSSIM) as a structural sensitivity metric across all 13 loci. A larger negative delta_LSSIM indicates greater structural discrimination between pathogenic and benign variants.

| Locus | delta_LSSIM | Structural Pathogenic N | Taxonomy Class | N_Q2b | Tissue Match |
|-------|-------------|------------------------|---------------|-------|-------------|
| hbb_95kb_subTAD | +0.0049 | 962 | B_architecture | 25 | 1.0 |
| tert_300kb | -0.0188 | 27 | D_coverage_gap (mostly Q2a) | 1 | 0.5 |
| bcl11a_300kb | -0.0137 | 0 | (not in taxonomy table) | 0 | N/A |
| pten_300kb | -0.0097 | 9 | (not in taxonomy table) | 0 | N/A |
| mlh1_300kb | -0.0091 | 72 | D_coverage_gap | 0 | 0.5 |
| tp53_300kb | -0.0090 | 0 | B_architecture_tentative | 2 | 0.5 |
| cftr_317kb | -0.0068 | 35 | D_coverage_gap | 0 | 0.0 |
| gjb2_300kb | -0.0062 | 0 | E_tissue_mismatch | 0 | 0.0 |
| brca1_400kb | -0.0056 | 52 | B_architecture_tentative | 26 | 0.5 |
| gata1_300kb | -0.0036 | 0 | (not in taxonomy table) | 0 | N/A |
| scn5a_400kb | -0.0035 | 0 | E_tissue_mismatch | 0 | 0.0 |
| ldlr_300kb | -0.0025 | 10 | E_tissue_mismatch_partial | 0 | 0.0 |
| hba1_300kb | -0.0023 | 0 | (not in taxonomy table) | 0 | N/A |

**Note on HBB anomaly:** HBB's delta_LSSIM is _positive_ (+0.0049), which is a modeling artifact of the 95kb subTAD window and the unique enhancer-promoter topology of the beta-globin LCR. This value is not comparable to the 300kb windows used for other loci.

---

## 3. Statistical Analysis

### 3a. Rank correlation: delta_LSSIM vs. N_Q2b

Restricting to the 9 loci present in the taxonomy table (excluding HBB due to incomparable window size):

| Locus | |delta_LSSIM| rank | N_Q2b rank |
|-------|---------------------|------------|
| TERT | 1 (0.0188) | 3 (1) |
| TP53 | 2 (0.0090) | 4 (2) |
| MLH1 | 3 (0.0091) | 5.5 (0) |
| CFTR | 4 (0.0068) | 5.5 (0) |
| GJB2 | 5 (0.0062) | 5.5 (0) |
| BRCA1 | 6 (0.0056) | 2 (26) |
| SCN5A | 7 (0.0035) | 5.5 (0) |
| LDLR | 8 (0.0025) | 5.5 (0) |

**Spearman rho cannot be meaningfully computed:** 5 of 8 loci have N_Q2b = 0, creating massive tied ranks. The remaining 3 loci with Q2b > 0 (TERT=1, TP53=2, BRCA1=26) do not show a monotonic relationship with delta_LSSIM. BRCA1 has the most Q2b variants but ranks 6th in structural sensitivity.

### 3b. Fragility atlas comparison (HBB vs BRCA1)

| Metric | HBB | BRCA1 |
|--------|-----|-------|
| Severe fragility zones | 0 | 6 |
| Max Delta_SSIM (severe) | 0.0495 | 0.0764 |
| Mean Delta_SSIM (severe, enhancer-proximal) | ~0.015 | 0.0302 |
| Enhancer proximity enrichment ratio | N/A | 4.2x |
| N_Q2b | 25 | 26 |
| Q2b precision | 1.000 | 0.038 |
| Taxonomy confidence | HIGH | LOW |

**Result:** BRCA1 is structurally more fragile at baseline, but its Class B assignment is far weaker. This suggests **baseline fragility does NOT predict Class B enrichment**. In fact, the pattern is inverted: HBB has low baseline fragility but high Class B confidence.

---

## 4. Interpretation

### Does baseline fragility predict Class B enrichment?

**No.** The available data shows an inverse or null relationship:

1. **HBB (low fragility, high Class B):** Zero severe fragility zones, yet the strongest Class B evidence. Architecture-driven pathogenicity arises from variant-specific disruption of the LCR-promoter loop, not from pre-existing structural weakness.

2. **BRCA1 (high fragility, weak Class B):** Six severe fragility zones and deeper SSIM drops at baseline, yet Q2b precision is only 3.8% and most Q2b variants are common polymorphisms. The fragile baseline may actually _increase noise_, making it harder to distinguish architecture-driven pathogenicity.

3. **Tissue match dominates:** The strongest predictor of Class B enrichment is tissue match (HBB = 1.0 in K562 erythroid model), not baseline fragility. All loci with tissue_match = 0.0 have zero Q2b variants regardless of their structural properties.

### Possible mechanistic explanations

- **Fragile loci may tolerate perturbation:** If a locus is already structurally flexible, additional variant-induced disruption may have less marginal effect on gene regulation (diminishing returns).
- **Rigid architectures may be more informative:** A stable loop architecture (like HBB-LCR) creates a clear binary signal — loop intact vs. disrupted — making architecture-driven effects detectable.
- **Confounding by tissue match:** With only 2 fragility atlases and strong tissue match confounding, we cannot disentangle fragility from tissue specificity.

---

## 5. Limitations

1. **Fragility atlas data exists for only 2 of 9 loci** (HBB and BRCA1). The remaining 7 loci have no fragility scan, making any cross-locus generalization premature.
2. **Window size incompatibility:** HBB uses a 95kb subTAD window while all other loci use 300-400kb windows, making delta_LSSIM values not directly comparable.
3. **Tissue match confounds the analysis:** HBB (tissue_match=1.0) vs BRCA1 (tissue_match=0.5) — the stronger signal at HBB may reflect tissue matching, not fragility.
4. **N=2 comparison:** Any correlation between fragility and Class B from two data points has no statistical power. Even the direction of the effect (inverse) could be coincidental.
5. **Fragility and ARS are computed from the same polymer model.** They are not independent measurements — both derive from OpenMM simulations with the same cohesin parameters. Any correlation could be tautological.

---

## 6. Conclusion

**The data does not support a positive correlation between baseline structural fragility and Class B (architecture-driven) enrichment.** If anything, the two available loci suggest an inverse relationship: the structurally rigid HBB locus shows strong Class B evidence while the fragile BRCA1 locus shows weak Class B evidence. However, with N=2 loci and strong tissue-match confounding, this observation is **insufficient to draw a causal conclusion**.

**Recommendation:** To properly test this hypothesis, fragility atlases would need to be generated for all 9 loci (or at minimum the 4 with Q2b variants: HBB, TERT, BRCA1, TP53), ideally in tissue-matched cell types. Until then, the ARS-taxonomy bridge remains a plausible but unvalidated hypothesis.

**Status: INCONCLUSIVE (insufficient data)**
