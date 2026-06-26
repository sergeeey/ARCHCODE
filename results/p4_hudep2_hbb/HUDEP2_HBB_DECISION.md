# HUDEP-2 Real Hi-C HBB Retest — Decision

**Date:** 2026-06-05
**Gate verdict:** `HUDEP2_FAILS_SAME_BIN`
**Data source:** GSM4873116 WT-HUDEP2 capture Hi-C, KR-balanced, 5kb resolution, chr11:5200000-5250000
**Compute:** `results/p4_hudep2_hbb/run_hudep2_gate.py` → `HUDEP2_HBB_GATE_STATS.json`

> **[VERIFIED-INLINE]** computation on real HUDEP-2 capture Hi-C + ClinVar-derived atlas.
> NOT [VERIFIED-REAL] real-world pathogenicity validation.

---

## Summary — three independent failures

| Failure | Description |
|---|---|
| **F1 — Resolution** | All 1103 HBB variants fall in a single 5kb bin (bin 5: 5225000-5230000). No positional discrimination is possible at 5kb. |
| **F2 — Analytical model ≠ real tissue** | Pearson r = **0.16** (p=0.30, not significant) between analytical wt contact map and HUDEP-2. The model does not reproduce real HUDEP-2 chromatin structure. |
| **F3 — Zero within-category discrimination** | Hybrid LSSIM is **CONSTANT** within every category (same bin + same effectStrength = same LSSIM). Within-category AUC = **0.5000 exactly** for all testable categories. |

---

## 1. Resolution — the test cannot be run at 5kb

All 1103 HBB atlas variants (positions 5225454–~5249xxx) fall in **bin 5** of the
10-bin HUDEP-2 window (chr11:5200000-5250000, 5kb bins). Every variant has exactly
the same local Hi-C submatrix. No per-variant positional signal is possible.

The root cause is the extraction: the `.hic` file (GSM4873116, 2.47GB capture Hi-C)
was extracted at 5kb binning. Capture Hi-C data contains sub-kb information, but it
was binned too coarsely to be usable here. Re-extraction at **1kb or 500bp** would
provide ~1–2 bins within the HBB gene body and could support a positional test in
principle.

---

## 2. Analytical model vs real HUDEP-2 — not correlated

| Metric | Value |
|---|---:|
| Pearson r (off-diagonal contacts) | **0.16** (p = 0.30, ns) |
| Spearman r | 0.11 |
| SSIM(analytical, HUDEP-2) | 0.9686 |

The SSIM of 0.97 appears high but is misleading — it is driven by global
distributional similarity (both matrices have similar mean and variance after KR
normalization), not by the specific contact-pattern agreement. The Pearson r=0.16
on the contact-by-contact comparison is the diagnostic: the analytical model's
contact map **does not reproduce** real HUDEP-2 chromatin organization at 5kb scale.

This is a second independent failure: even if resolution were sufficient, the input
model does not resemble the real tissue. Using it to compute a "mutant reference"
relative to real Hi-C would compound both errors.

---

## 3. Hybrid LSSIM — mathematically constant, AUC = 0.50 exactly

| Category | Unique LSSIM values | Within-cat AUC | MW p | Cliff δ |
|---|---:|---:|---:|---:|
| intronic | **1 (CONSTANT)** | **0.5000** | 1.0 | 0.000 |
| synonymous | 1 (CONSTANT) | 0.5000 | 1.0 | 0.000 |
| other | 1 (CONSTANT) | 0.5000 | 1.0 | 0.000 |
| all other categories | 1 (CONSTANT) | n/a | n/a | n/a |

Because all variants share the same 5kb bin AND the same effectStrength per category,
the hybrid LSSIM is a single number per category. AUC = 0.50 is not a "near-chance"
result — it is **exactly 0.50 by construction**. This is the strongest possible null.

---

## 4. What WOULD be needed to run this test properly

| Requirement | Current status | Path forward |
|---|---|---|
| Resolution ≤ 1kb | 5kb (too coarse) | Re-extract GSM4873116 at 1kb via hic2cool |
| Analytical model reproduces real Hi-C | r = 0.16 (fails) | Re-calibrate to HUDEP-2 structure, or use real Hi-C directly |
| Regulatory variants (non-coding) | All HBB variants are coding | Need ClinVar non-coding + regulatory set, or synthetic VCF at regulatory positions |
| Erythroid CTCF | K562 used for HBB too in some configs | Use HUDEP-2-specific CTCF ChIP-seq |

None of these are solved in the current repo. This is not a failure of ARCHCODE
as a concept — it is a failure of the current input data layer for this test.

---

## 5. Gate decision

| Gate step | Status |
|---|---|
| Resolution | ❌ FAIL — single bin |
| Analytical ≈ real Hi-C | ❌ FAIL — r=0.16, p=0.30 |
| Per-variant discrimination | ❌ STRUCTURALLY IMPOSSIBLE at 5kb |
| K2 (LSSIM adds over category) | ❌ FIRES (0.9802 = 0.9802) |

**`HUDEP2_VERDICT = FAILS_SAME_BIN`**

The HUDEP-2 data does not rescue the residual-signal hypothesis.

---

## 6. What this means for the program

**Five experiments, five gates, five failures:**

| Experiment | Type | Gate result |
|---|---|---|
| HBB analytical | Category confound test | FAIL — d −2.67 → −0.34 stratified |
| HBB K1/K2 | Regulatory-distance confound | FAIL — K1 R²=0.907, K2 fires |
| BCL11A | Second positive locus | FAIL — not_observed_graphql |
| GATA1 | Matched-category test | FAIL — wrong-direction missense, K562 tissue |
| HUDEP-2 Hi-C | Real tissue retest | FAIL — single bin, r=0.16, AUC=0.50 exact |

**The residual-signal hypothesis is now falsified across all testable configurations
in this repository.** It is not falsified in principle — a properly designed
experiment (1kb Hi-C, regulatory variants, erythroid CTCF, correct tissue) could
still test it. But the data in this repo cannot.

---

## 7. What this does NOT mean

1. Does NOT prove ARCHCODE's engine is wrong — the physics is plausible.
2. Does NOT prove the 3D signal doesn't exist in real biology.
3. Does NOT close the hypothesis for regulatory/non-coding variants at 1kb+ resolution.

---

## 8. Conclusion — Paper 3 framing is now determined

The outcome is unambiguous. Paper 3 is a **negative falsification framework paper.**

> *Five systematic matched-control experiments across HBB, BCL11A, GATA1, and
> HUDEP-2 real Hi-C show that current LSSIM implementations do not add independent
> 3D structural signal beyond consequence category, regulatory-distance, and tissue
> baselines. These negative results define exactly what conditions a fair test
> requires: 1kb-resolution erythroid Hi-C, regulatory non-coding variants, and
> matched-category controls. The ARCHCODE falsification framework is the contribution.*

This framing requires **no positive signal**, is **defensible against any reviewer**,
and documents a systematic methodological contribution. Target venues: PLoS
Computational Biology, Bioinformatics, Genome Biology.

Paper 3 skeleton is now ready to write.
