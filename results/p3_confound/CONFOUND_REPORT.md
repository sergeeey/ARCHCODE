# Etap 3 — Regulatory-Confound Test (Kill Criteria K1 & K2)

**Date:** 2026-06-05
**Compute:** `results/p3_confound/confound_models.py` → `CONFOUND_STATS.json`
**Inputs (read-only):** `results/HBB_Unified_Atlas_95kb.csv`, `data/hbb_ctcf_sites_literature.json`
**Cross-checks:** `results/mutual_information_analysis.json`, `results/ctcf_distance_analysis.json`, `results/lssim_enhancer_distance_report.json`

> **[VERIFIED-INLINE]** descriptive computation on the project's own ClinVar-derived
> atlas (real data). Tests a DESCRIPTIVE question. NOT real-world validation.

## Question (EstimandOps L0)

Descriptive/predictive. *Does LSSIM carry useful information beyond (a) consequence
category and (b) genomic position (distance to CTCF)?* This is the plan's central
Etap-3 question and the difference between a publishable "residual 3D signal" claim
and a "trivial regulatory-distance proxy" (kill criterion K1).

## Results

### K2 — does LSSIM add value for the LABEL over category? (5-fold CV AUC)

| Model | Features | CV AUC |
|---|---|---:|
| A | LSSIM only | 0.970 |
| B | consequence category | **0.980** |
| C | category + LSSIM | 0.980 |

**Category alone beats LSSIM alone, and adding LSSIM to category does not improve
prediction (0.980 → 0.980).** → **K2 FIRES: LSSIM adds nothing over category.**
LSSIM is in fact a *lossy* re-encoding of category (it scores slightly worse).

### K1 — how much of LSSIM is just category + CTCF distance?

| Predictors of LSSIM | R² |
|---|---:|
| category only | **0.907** |
| category + distance-to-CTCF | 0.9325 |
| within-intronic: LSSIM vs CTCF-distance (Spearman ρ) | **0.735** |

LSSIM is **~91% determined by consequence category alone**; the remaining variation is
largely **distance-to-CTCF** (within the intronic category ρ = 0.735). → **K1 FIRES:
LSSIM is a deterministic structural-annotation proxy of (category + regulatory
distance), not independent 3D structural information.**

## Verdict

> On the HBB ClinVar atlas, **both kill criteria fire**. LSSIM ≈ f(consequence
> category + distance-to-CTCF). It provides **no residual signal** beyond annotations
> already available from VEP consequence and CTCF positions. The "LSSIM adds residual
> 3D structural information" hypothesis is **NOT supported** by this data.

## What this does NOT mean

1. Does **NOT** prove the residual-signal hypothesis is false for *other* loci or with
   *real* Hi-C-derived contact maps (the current maps are analytical/mean-field, not
   measured). It is falsified **on this analytical-HBB data only**.
2. Does **NOT** condemn the engine: a structural-annotation layer that faithfully
   re-expresses (category + CTCF distance) can still be a useful *visualization /
   hypothesis-prioritization* tool — it just must not be sold as independent evidence.
3. Does **NOT** test enhancer distance robustly (HBB enhancer-distance ρ is
   sign-inconsistent in `lssim_enhancer_distance_report.json`: +0.41 vs −0.39) —
   flagged as a data-quality issue to resolve before any enhancer claim.

## Consequence for the program

- The "residual 3D information" claim cannot rest on analytical contact maps. To keep
  it alive it must be re-tested on **real Hi-C** (Etap 6) at a locus with a
  **non-degenerate** category×label matrix (Etap 5). Until then it is `[NEEDS-REAL-DATA]`.
- The honest, defensible positioning is **mechanistic annotation + falsification
  framework**, exactly as the plan concluded — not prediction.
