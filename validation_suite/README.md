# ARCHCODE Validation Suite

**Falsification framework for 3D-genome models.**

Not a tool for discovering pathogenic variants. A tool for **stress-testing claims** made by 3D-genome prediction methods.

---

## Purpose

When a 3D-genome model claims to discover "invisible" pathogenic variants, what should we check?

This suite implements a battery of **falsification tests** that every physics-based variant predictor should pass before claiming discovery:

| Test | What it checks | Kill criterion |
|------|---------------|----------------|
| **CTCF Shuffle** | Is signal specific to real CTCF architecture? | Shuffled AUC ≥ real AUC |
| **Simple Baseline** | Does physics beat simple features? | Baseline AUC ≥ 0.95 |
| **Within-Category** | Does model discriminate within variant categories? | Median within-cat AUC ≈ 0.5 |
| **Ablation** | Which components drive the signal? | — |
| **Cross-Locus** | Does signal transfer to new loci? | AUC drops > 0.1 on new locus |
| **Robustness** | Is signal stable across parameters? | High variance across seeds/settings |

---

## Repository paths

Tests resolve `config/locus` and `results/` relative to the repository root (parent of `validation_suite/`). To point elsewhere, set **`ARCHCODE_ROOT`** to an absolute path of the clone.

## Quick Start

```bash
# Run all tests on all loci
python -m validation_suite run --all

# Run specific test on specific locus
python -m validation_suite run --test ctcf_shuffle --locus HBB TP53

# View summary
python -m validation_suite summary

# Generate HTML report
python -m validation_suite report
```

---

## Test Details

### 1. CTCF Shuffle Negative Control

**Null hypothesis:** The model's discrimination signal is specific to the biological arrangement of CTCF sites, not a generic property of having any barriers.

**Method:** Shuffle CTCF positions (preserving inter-site distance distribution), recompute LSSIM for all variants, compare AUC.

**Kill criterion:** Median shuffled AUC ≥ real AUC → signal is geometry artifact.

### 2. Simple Baseline (No Circular Features)

**Null hypothesis:** The physics-based model adds discriminative value beyond simple spatial features.

**Method:** Train LR and RF on distance-to-enhancer, distance-to-CTCF, category severity, position. **NO CADD** (circular — trained on ClinVar). Compare to SSIM AUC.

**Kill criterion:** Best baseline AUC ≥ 0.95 → physics not needed.

### 3. Within-Category Discrimination

**Null hypothesis:** The model discriminates pathogenic from benign variants **within** the same consequence category.

**Method:** For each variant category with ≥ 5 pathogenic AND ≥ 5 benign, compute AUC. Apply FDR correction across categories.

**Kill criterion:** Median within-category AUC ≈ 0.5 → all signal is category-driven.

### 4. Ablation Suite

**Purpose:** Decompose which components drive the signal.

**Ablation modes:**
- `categorical`: Real effect strength mapping
- `position_only`: Fixed effect strength (0.3) — removes category signal
- `uniform_medium`: Fixed effect strength (0.5)
- `inverted`: Reversed effect strength
- `random`: Random effect strength

### 5. Cross-Locus Transfer

**Null hypothesis:** A threshold trained on one locus transfers to others.

**Method:** Train LSSIM threshold on HBB, apply to all other loci. Measure AUC drop.

### 6. Robustness

**Checks:**
- Seed stability (different random seeds for landscape generation)
- Resolution sensitivity (600bp vs 1000bp vs 2000bp)
- Tissue mismatch (K562 annotations on non-K562 loci)

---

## Interpreting Results

| Verdict | Meaning | Action |
|---------|---------|--------|
| **PASS** | Model adds genuine value | Proceed with claim |
| **WARNING** | Signal is fragile/marginal | Narrow scope, add caveats |
| **FAIL** | Simple methods work as well or better | Reframe or abandon claim |
| **SKIPPED** | Insufficient data | Collect more data or drop test |

---

## What This Is NOT

- ❌ Not a clinical validation tool
- ❌ Not a benchmark for "best predictor"
- ❌ Not proof that 3D-genome models are useless

## What This IS

- ✅ A stress-test for specific claims made by physics-based models
- ✅ A reproducible framework anyone can run on their own model
- ✅ A way to find **where** (not whether) a model actually works

---

## License

Same as parent project.

---

## Citation

If you use this validation suite, cite:

> ARCHCODE Validation Suite v1.0. github.com/sergeeey/ARCHCODE/validation_suite
