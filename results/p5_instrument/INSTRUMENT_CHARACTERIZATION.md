# Etap 5 — Instrument Characterization (Multi-Locus Transfer Function)

**Date:** 2026-06-05
**Method:** Real TS engine `generate-unified-atlas.ts` run across 5 effect-modes
**Loci:** HBB (n=1103), GATA1 (n=183), HBA1 (n=111) — all ClinVar-derived, real
**Compute:** `results/p5_instrument/compute_transfer_function.py` → `TRANSFER_FUNCTION_STATS.json`
**Origin:** cross-domain bridge (metrology: characterize the instrument's transfer
function with built-in reference signals before trusting its readings)

> **[VERIFIED-INLINE]** — fresh computation on real ClinVar atlases produced by the
> project's own engine via the built-in `--effect-mode` ablation switches. This is a
> DESCRIPTIVE characterization of what the LSSIM instrument can resolve. It is **NOT**
> [VERIFIED-REAL] real-world pathogenicity validation.
>
> **Governance:** canonical categorical atlases were read READ-ONLY for the baseline;
> ablation modes wrote suffixed files (`*_INVERTED.csv` etc.) — no canonical file
> was overwritten.

---

## The reference-signal logic (why this is a fair test)

The engine exposes 5 effect-modes that set the per-variant perturbation magnitude
`effectStrength` independently of everything else (`getEffectStrength`, source lines
328–352). They act as **calibrated reference signals** for the instrument:

| Mode | What it injects | What a passing AUC would mean |
|---|---|---|
| `categorical` | severity from category lookup (nonsense=0.1 … synonymous=0.9) | the operating point used for all published claims |
| `position-only` | fixed 0.3 for **every** variant (category erased) | discrimination from variant **position** alone |
| `uniform-medium` | fixed 0.5 for every variant | sanity copy of position-only |
| `inverted` | category lookup with **swapped sign** (nonsense=0.9 … synonymous=0.1) | sign-flip negative control |
| `random` | random 0.1–0.9 per variant (seed 42) | noise floor |

**Two diagnostics:**
- **Mirror gap** = `|AUC_categorical − (1 − AUC_inverted)|`. If ≈ 0, the global AUC is
  a *directional category lookup* — flipping the lookup's sign flips the AUC. No
  positional or structural content survives the flip.
- **Position-vs-random gap** = `|AUC_position-only − AUC_random|`. If ≈ 0, the
  instrument has **zero positional resolution** — position carries no more signal
  than noise.

---

## Transfer function — global LSSIM AUC by mode, across three loci

| Mode | HBB | GATA1 | HBA1 |
|---|---:|---:|---:|
| categorical (operating point) | **0.975** | **0.838** | **0.770** |
| position-only | 0.551 | 0.463 | 0.607 |
| uniform-medium | 0.551 | 0.462 | 0.604 |
| inverted (sign-flip) | **0.022** | **0.138** | **0.287** |
| random (noise floor) | 0.490 | 0.533 | 0.616 |
| **1 − inverted** | 0.978 | 0.862 | 0.713 |
| **mirror gap** | **0.003** | **0.024** | **0.057** |
| **position − random gap** | 0.061 | 0.071 | 0.009 |

[VERIFIED-INLINE tool: scipy Mann-Whitney U on real atlases; HBB from precomputed
`ablation_effectstrength.json` 2026-03-04]

### Reading the table

1. **The mirror holds at all three loci.** `categorical ≈ 1 − inverted` for HBB
   (gap 0.003), GATA1 (0.024) and HBA1 (0.057). Flipping the category-severity sign
   flips the global AUC. **The global discrimination is the directional category
   lookup — at every locus tested, not just HBB.** This is the generalization HBB
   alone could not establish.

2. **Position alone is noise, at all three loci.** `position-only ≈ random ≈ 0.5±0.1`
   (gaps 0.061 / 0.071 / 0.009). Erasing the category and keeping only the variant
   position collapses AUC to chance. The instrument has **no positional resolving
   power** for pathogenicity.

3. **The mirror sharpens as the category distribution sharpens.** HBB
   (category-disjoint: severe=all-pathogenic, intronic=mostly-benign) gives a near
   perfect mirror (0.003) and extreme AUC (0.975). GATA1/HBA1 (more balanced, more
   missense) give a softer mirror (0.024 / 0.057) and lower AUC (0.838 / 0.770).
   The AUC magnitude tracks **category-distribution extremity**, exactly as a lookup
   artifact predicts.

---

## Within-category (the non-circular test) is invariant to the lookup

For the only category with both classes at n ≥ 5 (missense), the within-category AUC
**does not move when the lookup is inverted** — because within one category the
category lookup is a constant:

| Locus, missense (n_path / n_ben) | categorical | position-only | uniform | inverted | random |
|---|---:|---:|---:|---:|---:|
| GATA1 (34 / 25) | 0.464 | 0.468 | 0.461 | 0.482 | 0.556 |
| HBA1 (50 / 18) | 0.578 | 0.577 | 0.571 | 0.572 | 0.663 |

- **GATA1 missense ≈ chance and flat** across every mode → no category-independent
  signal of any kind.
- **HBA1 missense ≈ 0.57 and flat** across categorical/position/uniform/**inverted**
  → the weak 0.57 is **not** the category signal (it survives sign-inversion
  unchanged); it is a small positional/sampling effect, below any useful threshold
  for n=50/18, and is *not* what the headline AUC measures.

This is the cleanest possible statement of the negative result: **the global AUC
measures the category lookup and nothing else; the within-category channel, where the
lookup is held constant, carries no usable signal.**

---

## What this adds over the HBB-only result

| | HBB alone (prior) | + GATA1 + HBA1 (this) |
|---|---|---|
| Mirror property | observed once (0.022) | **locus-general** (3/3 loci mirror) |
| Position = noise | observed once | **3/3 loci** |
| AUC ~ category extremity | not testable (1 locus) | **confirmed** (0.975 → 0.838 → 0.770 as distribution balances) |
| Risk it's an HBB quirk | open | **closed** |

---

## Verdict

`INSTRUMENT_CHARACTERIZED — DIRECTIONAL CATEGORY LOOKUP, ZERO POSITIONAL RESOLUTION (3/3 loci)`

The ablation transfer function converts the negative result from *"we found no signal
on HBB"* into a **mechanistic instrument characterization**: across three independent
erythroid loci, mean-field LSSIM is a sign-directional consequence-category lookup
with no positional resolving power. This is a reusable benchmark any
mean-field chromatin score should be required to pass.

### Output artifacts
- `results/p5_instrument/TRANSFER_FUNCTION_STATS.json` — all AUCs + diagnostics
- `results/p5_instrument/compute_transfer_function.py` — analysis (seeded, read-only)
- `results/{GATA1,HBA1}_Unified_Atlas_300kb_{POSITION_ONLY,UNIFORM_MEDIUM,INVERTED,RANDOM}.csv`
  — engine ablation outputs (suffixed; canonical untouched)
- `results/ablation_effectstrength.json` — HBB ablation (precomputed 2026-03-04)

### What this does NOT mean
- Does NOT mean LSSIM is "wrong" — it correctly encodes the prior that severe
  categories perturb structure more. It means LSSIM is **redundant** with category.
- Does NOT test the fair regime (≤1 kb tissue-correct Hi-C + regulatory variants).
  That regime remains untested; this characterizes only the current analytical engine.
- Does NOT establish causality or real-world performance. Descriptive only.
