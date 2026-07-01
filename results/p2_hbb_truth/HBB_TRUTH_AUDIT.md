# HBB Truth Audit — Etap 2 (Falsification-First)

**Date:** 2026-06-05
**Status:** COMPLETE
**Inputs (read-only):** `results/HBB_Unified_Atlas_95kb.csv` (1103 variants, ClinVar-derived, real)
**Compute:** `results/p2_hbb_truth/compute_hbb_severity.py` → `HBB_SEVERITY_STATS.json`
**Cross-checks:** `results/within_category_analysis.json`, `results/position_only_control_experiment.json`, `results/mutual_information_analysis.json`

> Evidence marker: **[VERIFIED-INLINE]** — fresh computation on the project's own
> canonical ClinVar-derived atlas (real data, not synthetic). It validates a
> **DESCRIPTIVE** claim about the atlas. It is **NOT** [VERIFIED-REAL] evidence of
> real-world pathogenicity prediction. See "What this does NOT mean".

---

## 0. The question (EstimandOps L0)

- **Question type:** descriptive (NOT causal, NOT predictive).
- **Estimand:** the distribution of `ARCHCODE_LSSIM` by ClinVar label and by
  consequence category within the HBB locus, and whether label-discrimination
  survives conditioning on category.
- **Natural-language statement:** *We describe LSSIM by consequence category for HBB
  ClinVar variants, comparing pathogenic vs benign, to test whether the headline
  pathogenic/benign LSSIM separation persists within consequence categories.*

## 1. The mechanism that makes the naive claim circular

`scripts/generate-unified-atlas.ts` (verified by reading lines 291–352): LSSIM is a
**deterministic function of the consequence category** via a hardcoded lookup:

```
CATEGORICAL_EFFECTS = { nonsense:0.1, frameshift:0.15, splice_*:0.2,
                        missense:0.4, promoter:0.3, intronic:0.8, synonymous:0.9, ... }
```

`effectStrength = CATEGORICAL_EFFECTS[category]` → scales the occupancy reduction →
drives the contact-map perturbation → drives LSSIM. Therefore **"low LSSIM ⇔
severe category" is true by construction**, not an empirical discovery. Any
"pathogenic vs benign LSSIM" gap is mostly a re-statement of "the two groups have
different category mixes."

## 2. Per-category severity table (the honest descriptive result)

All numbers from `HBB_SEVERITY_STATS.json`. n = total variants in category; CI = bootstrap 95% of mean LSSIM (5000 resamples, seed 20260605).

| Category | n | n_path | n_benign | mean LSSIM | median | IQR | both-class testable? |
|---|---:|---:|---:|---:|---:|---|:--:|
| nonsense | 40 | 40 | 0 | 0.7984 | — | — | no (no benign) |
| frameshift | 99 | 99 | 0 | 0.8176 | — | — | no (no benign) |
| missense | 125 | 125 | 0 | 0.9267 | — | — | no (no benign) |
| splice_* | (see JSON) | path-only | 0 | — | — | — | no (no benign) |
| **intronic** | **667** | **9** | **658** | 0.9928 | — | — | **YES** |
| **synonymous** | **86** | **3** | **83** | — | — | — | **YES** |
| **other** | **19** | **12** | **7** | — | — | — | **YES (underpowered)** |
| 3′UTR | 14 | 13 | 1 | 0.9918 | — | — | no (1 benign) |
| 5′UTR | 4 | 3 | 1 | 0.9758 | — | — | no (1 benign) |

**Key structural fact:** the severe categories (nonsense, frameshift, missense,
splice) contain **0 benign** HBB variants; the benign group is **87.7% intronic**.
The pathogenic and benign groups are **almost disjoint in category space** — so a
matched-category comparison is barely possible in HBB at all.

## 3. The matched test (the only real test) — NULL

Within categories that have ≥3 of each class:

| Category | n | within-cat AUC | Mann–Whitney p | Cliff's δ | verdict |
|---|---:|---:|---:|---:|---|
| intronic | 667 | **0.524** | **0.804** | −0.048 | **null — no discrimination** |
| synonymous | 86 | **0.570** | **0.673** | −0.141 | **null — no discrimination** |
| other | 19 | 0.774 | 0.056 | −0.548 | underpowered, wrong-direction δ |

In the two adequately powered categories (intronic n=667, synonymous n=86), LSSIM
does **not** separate pathogenic from benign (p = 0.80 and 0.67). This reproduces
`within_category_analysis.json` and `position_only_control_experiment.json`.

## 4. Decomposition of the headline effect — d collapses 87%

| Quantity | Value |
|---|---:|
| Global AUC (1−LSSIM as score) | **0.9755** |
| Naive Cohen d (pathogenic vs benign LSSIM) | **−2.67** |
| **Category-stratified pooled Cohen d** | **−0.34** |
| Position-only ablation AUC (from project file) | 0.5509 |

Stratifying by consequence category shrinks the effect from **d = −2.67 to −0.34**
(a ~87% reduction). The residual −0.34 is itself dominated by the underpowered,
heterogeneous "other" category (n=19). This is the quantitative proof that the
**"Cohen d = 2.13" headline is a category-distribution artifact**, consistent with
the project's own position-only ablation (AUC 0.977 → 0.55).

## 5. Orthogonality (context, from `mutual_information_analysis.json`)

ARCHCODE↔CADD NMI = 0.024, ARCHCODE↔Label NMI = 0.052, ARCHCODE↔VEP NMI = 0.10.
ARCHCODE shares the most information with **VEP consequence** (≈ category) and almost
none with the actual pathogenicity **Label** — exactly what a category-derived score
would do.

---

## 6. Honest claim we CAN make

> **LSSIM reproduces the consequence-severity ordering of HBB variants by
> construction (it is a deterministic function of the consequence category).**
> Within the only HBB categories where both classes exist in adequate numbers
> (intronic, synonymous), LSSIM does **not** discriminate pathogenic from benign
> (AUC 0.52 / 0.57; Mann–Whitney p = 0.80 / 0.67). The headline pathogenic-vs-benign
> separation (AUC 0.977, naive Cohen d −2.67) is a category-distribution effect:
> stratifying by category collapses the effect to d ≈ −0.34.

## 7. What this result does NOT mean (mandatory)

1. Does **NOT** establish that ARCHCODE/LSSIM predicts pathogenicity in HBB or anywhere.
2. Does **NOT** generalize beyond the HBB ClinVar set analyzed (single locus, specific category mix).
3. Does **NOT** rule out a *mechanistic* (not predictive) use of LSSIM — see Etap 3 (residual position signal), which is a separate, still-open question.
4. Does **NOT** validate any real-world reclassification of VUS. The 641 "pearl-like" VUS remain hypotheses, not reclassifications.

## 8. Go/No-Go

- **Cohen d = 2.13 / AUC 0.977 as independent pathogenicity evidence:** **NO-GO** — falsified as category-distribution artifact.
- **"LSSIM encodes a consequence-severity hierarchy (descriptive, by construction)":** **GO** — true and citable, with the circularity stated explicitly.
- **HBB as a standalone pathogenicity-prediction result:** **NO-GO.**
- **HBB as a worked example of the falsification framework (how a loud claim is killed by matched controls):** **GO** — this is the strongest honest use of HBB.
