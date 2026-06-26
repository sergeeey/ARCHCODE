# GATA1 Matched-Test Decision

**Date:** 2026-06-05
**Gate verdict:** `FAIL_PROXY_ONLY`
**K3 kill criterion status:** FIRES — GATA1 is NOT promoted to a positive locus

**Inputs (read-only):**
- `results/GATA1_Unified_Atlas_300kb.csv` (183 variants, ClinVar-derived, real)
- `results/UNIFIED_ATLAS_SUMMARY_GATA1_300kb.json`

**Compute:** `results/p1_gata1_matched/run_gata1_gate.py` → `GATA1_GATE_STATS.json`

> **[VERIFIED-INLINE]** descriptive computation on a ClinVar-derived atlas.
> NOT [VERIFIED-REAL] real-world pathogenicity validation.

---

## 1. Source audit — TWO critical concerns

### Tissue mismatch (critical)
The GATA1 atlas uses **ENCODE K562 CTCF** and **ENCODE K562 H3K27ac** as the
regulatory landscape. **K562 is a leukemic myelogenous cell line.** GATA1 is an
essential erythroid / megakaryocyte transcription factor — its chromatin architecture
in K562 does not reflect its biologically relevant tissue context. Any CTCF-barrier
or enhancer-occupancy modelling using K562 ChIP-seq is the wrong tissue for a GATA1
structural claim.

### Variant clustering — no regulatory spread
All 183 variants span only **3,117 bp** (48791049–48794166 on chrX), entirely within
the GATA1 gene body (~exons 2–6). None lie in the LCR or upstream regulatory region.
A 300kb structural metric computed on a 300kb window cannot resolve variants that
are all within the same 3kb bin — structural context is identical for all of them.
The "3D structural annotation" premise collapses before statistics are even run.

**Source audit verdict: `TISSUE_MISMATCH + NO_REGULATORY_SPREAD`**

---

## 2. Coordinate sanity

| Check | Expected | Observed | Status |
|---|---|---|---|
| Build | GRCh38 | GRCh38 | ✅ |
| Chrom | chrX | chrX (inferred) | ✅ |
| Sim window | 300kb | chrX:48640425-48940425 | ✅ |
| Variant spread | ~300kb | **3,117 bp** | ⚠️ extreme clustering |

---

## 3. Category baseline — already higher than LSSIM alone

| Model | CV AUC |
|---|---:|
| A: label ~ LSSIM | 0.6062 |
| B: label ~ category | **0.8584** |
| C: label ~ category + LSSIM | 0.8572 (**−0.0012**) |
| D: label ~ category + position | 0.8710 |
| E: label ~ category + pos + LSSIM | 0.8708 (**−0.0002**) |

Category alone outperforms LSSIM alone by **0.25 AUC**. Adding LSSIM to category
makes the model *worse* (C < B; E < D). **K2 fires.**

---

## 4. Within-category matched test — the non-circular test

| Category | n | path | benign | ΔLSSIM (p−b) | AUC | MW p | Cliff δ | Direction |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **missense** | 59 | 34 | 25 | **+0.00091** | **0.464** | 0.644 | +0.072 | ❌ WRONG |
| **synonymous** | 89 | 3 | 86 | **+0.000074** | **0.314** | 0.194 | +0.372 | ❌ WRONG |
| intronic | 22 | 3 | 19 | −0.000258 | 0.710 | 0.228 | −0.421 | ✓ (n=3, underpowered) |

**Missense** is the most balanced and informative category (34/25). LSSIM for
pathogenic missense variants is **higher** than for benign — the wrong direction.
AUC **0.464** is below chance. Synonymous similarly below chance (**AUC 0.314**).

The intronic "correct direction" is based on **3 pathogenic variants** — grossly
underpowered and not credible as positive signal.

---

## 5. K1 — how much of LSSIM comes from category?

| Predictor set | R² of LSSIM |
|---|---:|
| Category only | 0.624 |
| Category + position | — (position adds noise, not structure) |

Lower than HBB's R²=0.907 — because all variants are at the same genomic bin,
so position *noise* within the 3kb cluster actually partially decorrelates
LSSIM from its category driver. This is NOT evidence of residual 3D signal;
it is evidence of **positional noise within a coding region** where the 300kb
structural model has no resolution.

---

## 6. Additional flags

- `thresholds_calibrated: false` — no per-locus calibration
- `archcode_structural_pathogenic: 0`, `pearls: 0` — no pearl variants found
- Global LSSIM range: pathogenic mean 0.9951 / benign mean 0.9987 — **delta 0.0036**
  (compare HBB pathogenic mean 0.88 / benign 0.99 — delta 0.11; GATA1 is 30× smaller)

---

## 7. Gate decision

| Gate step | Status | Detail |
|---|---|---|
| Source audit | ❌ FAIL | K562 ≠ erythroid tissue; 3kb regulatory spread |
| Coord sanity | ⚠️ WARN | All coding variants; no regulatory landscape coverage |
| Category baseline | ❌ FAIL K2 | LSSIM adds nothing (−0.0012 AUC) |
| Position baseline | ❌ FAIL K2b | LSSIM adds nothing (−0.0002 AUC) |
| Matched-category test | ❌ FAIL | missense AUC 0.464 (wrong direction); synonymous 0.314 (wrong direction) |
| K3 kill criterion | 🔴 FIRES | GATA1 NOT promoted to positive locus |

**`GATA1_VERDICT = FAIL_PROXY_ONLY`**

> Per governance rule B5 and kill criterion K3 (p0_governance/RULES.md):
> GATA1 does NOT provide evidence of independent LSSIM pathogenicity signal.
> This locus is NOT added to the positive-evidence set.

---

## 8. What does this mean for the program?

**Pattern confirmed across three loci (HBB, BCL11A, GATA1):**
- The more carefully we look, the more the within-category LSSIM signal is null
  or wrong-direction.
- The source audit reveals an additional structural problem: the CTCF/enhancer
  landscape is from the wrong tissue, meaning the simulation is modelling the
  wrong cells even before statistical analysis.

**HBA1** is the next candidate. Before running it, the same tissue question applies:
is the HBA1 atlas built on K562, or on erythroid-specific Hi-C/CTCF data? If K562,
expect the same tissue-mismatch flag.

**Residual-signal hypothesis status:** `[NEEDS-REAL-DATA]` — still unfalsified in
principle (requires correct tissue Hi-C, non-coding regulatory variants, measured
contact maps), but **now falsified on analytical maps with wrong-tissue CTCF** for
both coding-variant-dominated loci tested. The path to any positive claim runs
through Etap 6 (real Hi-C, correct tissue).

---

## 9. What this does NOT mean

1. Does NOT prove ARCHCODE is useless — the engine is real, the framework approach
   is sound; it just has not yet found a clean signal.
2. Does NOT mean GATA1 has no 3D regulatory variation — it means the current atlas
   (K562 CTCF, all coding variants, no regulatory spread) cannot test it.
3. Does NOT close the hypothesis for regulatory / non-coding GATA1 variants run with
   erythroid-specific CTCF data.
