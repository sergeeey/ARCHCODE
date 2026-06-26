# Paper 3 — Skeptic Review (A5, FL context-asymmetric)

**Date:** 2026-06-12
**Mode:** Skeptic Engine Режим 3 (claims/experiment audit). Independent recomputation
from raw CSVs/JSON — manuscript numbers NOT trusted.
**Verdict:** CORE SURVIVES (rests on K1/K2, which reproduce). **2 overclaims must be
fixed before submission.** No kill.

---

## Per-claim verdicts

### C1 — "AUC 0.975 is a category artifact" → **WEAKENED (survives via K1/K2)**
[ФАКТ] naive Cohen d = **−2.671** reproduces exactly from CSV.
[ФАКТ] Two cracks found by recomputation:

1. **The −0.34 stratified d is weighting-dependent (researcher d.o.f.).**
   `compute_hbb_severity.py:149` pools within-category d weighted by
   `min(n_path, n_benign)` → **−0.344**. Re-pooling weighted by **total category n**
   gives **+0.019** (≈0, opposite sign). Both support "collapse from −2.67," but the
   headline number is **not unique**.
   → Fix: state the weighting explicitly + report sensitivity (|d| ≈ 0 to 0.34), or
   drop the precise −0.34 and say "collapses to near zero (≤0.34 depending on
   weighting)."

2. **The within-category "non-circular test" is underpowered AND not cleanly null.**
   [ФАКТ] HBB intronic: **nP = 9**, nB = 658, AUC 0.524 (p 0.80) — consistent with
   null but cannot exclude a moderate effect (9 pathogenic).
   [ФАКТ] The **most-balanced** testable category, `other` (nP = 12, nB = 7), gives
   **AUC 0.774, p = 0.056** — a *positive trend*, not null. A hostile reviewer will cite
   this against a "uniformly null within-category" reading.
   → Fix: do NOT headline the within-category AUC. Rest C1 on K1+K2 (below). Report
   the within-category test honestly with power caveat and the `other` trend.

[ВЫВОД] C1's robust legs are K1 and K2, not the within-category AUC.

### C4 — "LSSIM adds nothing over category" → **CONFIRMED (C1's strongest leg)**
[ФАКТ] CV AUC: category 0.980 vs category+LSSIM 0.980 (actually 0.9802 → 0.9799, i.e.
adding LSSIM marginally *hurts*). K1: R²(LSSIM~category) = 0.907. Both reproduce.
This is the load-bearing evidence; promote it to the headline of C1.

### C2 — "mirror property is locus-general" → **CONFIRMED as DIAGNOSTIC / WEAKENED as independent evidence**
[ФАКТ] gaps 0.003 / 0.024 / 0.057 reproduce.
[ВЫВОД] **The mirror is near-tautological where category separation is strong.** Given
LSSIM is monotone in a category lookup, inverting the lookup necessarily ≈reverses the
rank order → AUC → ≈ (1 − AUC). So the HBB mirror (gap 0.003) largely *re-expresses*
C1's mechanism; it is **not independent corroboration**. The genuinely informative
quantity is the **deviation** from a perfect mirror (gap growing 0.003 → 0.057 as
categories balance), which measures the non-category component.
→ Fix: present the mirror as a *confirmatory diagnostic of lookup-monotonicity*, not as
independent evidence. Frame the growing gap, not the near-zero gap, as the finding.

### C3 — "position alone is noise" → **CONFIRMED**
[ФАКТ] position-only ≈ random at all loci (gaps 0.061 / 0.071 / 0.009). HBA1
position-only 0.607 sits slightly above 0.5 but ≈ its own random (0.616) — consistent.

### C5 — "HUDEP-2 real Hi-C fails" → **NOT RE-VERIFIED this pass**
[НЕИЗВЕСТНО] r = 0.16 was not recomputed here (requires the .npy contact matrix).
[ВЫВОД] "all 1103 variants in one 5 kb bin" is structurally near-certain (HBB ClinVar
span < one 5 kb bin on the extraction grid). → Action: re-verify r = 0.16 independently
before submission (load `data/hudep2_wt_hic_hbb_locus.npy`, recompute off-diagonal
Pearson).

### Sign-convention probe (c) → **no error**
[ФАКТ] Orientation consistent across recompute: AUC = P(LSSIM_path < LSSIM_ben); naive
d negative (pathogenic lower LSSIM); inverted mode flips correctly (path → higher
LSSIM). No interpretation-flipping bug.

### Reproducibility probe (d) → **all numbers reproduce EXCEPT −0.34** (weighting-dependent; see C1).

---

## Strongest objection (one)
The manuscript leads its negative result with its **two weakest items** — an
underpowered within-category AUC (nP = 9) and a near-tautological mirror — while its
**robust** evidence (K1 R² = 0.907; K2 ΔAUC ≈ 0) is presented as supporting detail. A
competent reviewer inverts this and the headline looks fragile. The science is right;
the **load order is wrong**.

## Required edits (before A6 self-review)
1. **Re-rank C1 evidence:** K2 (ΔAUC≈0) + K1 (R²=0.907) become the headline; within-
   category AUC demoted to a power-caveated secondary check that also reports `other`
   (0.774, p=0.056).
2. **−0.34 → disclose weighting + sensitivity** (min-weighted −0.34; size-weighted ≈0).
3. **Mirror → reframe as confirmatory diagnostic**, emphasize the growing gap, drop any
   "independent evidence" phrasing.
4. **C5 r=0.16 → re-verify** from the .npy before submission.

## Confidence: HIGH that the core conclusion holds; HIGH that the 3 framing fixes are required.
