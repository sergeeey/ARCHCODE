# ARCHCODE v2.0 Roadmap — Post-Publication Cross-Validation

**Created:** 2026-02-28
**Status:** PLANNED (after bioRxiv v1.0 submission)
**Principle:** Fit on A, Predict on B — no circular validation

---

## Why v2.0 (not before publication)

ARCHCODE v1.0 reports honest Hi-C correlation r=0.16 (not significant, n=12 loci).
Bayesian parameter fitting to a single locus would produce high r but constitutes
overfitting, not validation. Proper validation requires cross-locus prediction.

v1.0 is published with transparent limitations. v2.0 addresses them rigorously.

---

## Phase 1: Micro-C Reference Data (2 loci)

**Goal:** Obtain high-resolution experimental contact matrices for two independent loci.

| Locus             | Region (GRCh38)              | Cell type              | Source            |
| ----------------- | ---------------------------- | ---------------------- | ----------------- |
| HBB (training)    | chr11:5,210,000-5,240,000    | K562 (erythroleukemia) | 4D Nucleome / GEO |
| SOX2 (validation) | chr3:181,700,000-181,750,000 | K562                   | 4D Nucleome / GEO |

**Resolution:** 1000 bp (primary), 500 bp (if available)

**Why K562:** Erythroid lineage relevant to HBB expression. Same cell type for both
loci ensures consistent chromatin state.

**Why SOX2:** Well-characterized enhancer-promoter loop, CTCF-bounded domain,
independent chromosome from HBB.

**Deliverables:**

- `data/reference/HBB_MicroC_K562_1kb.npy`
- `data/reference/SOX2_MicroC_K562_1kb.npy`
- `scripts/fetch_micro_c.py`

---

## Phase 2: Bayesian Cross-Validation

**Goal:** Fit parameters on HBB, predict SOX2 — measure prediction accuracy on unseen locus.

**Method:**

1. `gp_minimize` (scikit-optimize, 50-100 iterations)
2. Parameters: alpha [0.5, 1.5], gamma [0.5, 1.2], k_base [0.0005, 0.01]
3. Objective: minimize L2 distance between ARCHCODE output and HBB Micro-C
4. **Critical:** Evaluate SAME parameters on SOX2 WITHOUT refitting

**Success criteria:**

- HBB (training): Pearson r > 0.5 (expected, since fitted)
- SOX2 (validation): Pearson r > 0.3 (meaningful cross-locus prediction)
- If SOX2 r < 0.15: model does not generalize — report honestly

**Deliverables:**

- `scripts/optimize_kramer_params.py`
- `config/optimal_params.json` (with fit_locus: "HBB", validation_locus: "SOX2")
- `results/cross_validation_report.json`

---

## Phase 3: Topological Data Analysis (TDA)

**Goal:** Add Wasserstein distance as topology-aware comparison metric.

**Method:**

1. Convert contact matrices to distance matrices: D(i,j) = 1 - C(i,j)
2. Compute persistent homology via ripser (H0 and H1)
3. Compare persistence diagrams via persim.wasserstein()

**Why TDA:** SSIM captures pixel-level similarity. Wasserstein distance captures
topological features (loops, domains) that may persist even when pixel values differ.
Complementary to SSIM, not replacement.

**Deliverables:**

- `src/metrics/topology.py`
- Integration into atlas generation pipeline
- Updated manuscript section comparing SSIM vs Wasserstein

**Note:** ripser requires C++ build tools on Windows. Fallback: use gudhi or
run in WSL/Docker.

---

## Phase 4: Updated Manuscript (v2.0 preprint)

**Goal:** Update bioRxiv preprint with cross-validation results.

**Key additions:**

- Methods: Bayesian optimization protocol with cross-validation design
- Results: Training (HBB) and validation (SOX2) correlation values
- Discussion: Whether model generalizes across loci
- New figure: Cross-validation scatter plot (predicted vs observed, both loci)

---

## Timeline (estimated)

| Phase     | Duration      | Dependencies                     |
| --------- | ------------- | -------------------------------- |
| Phase 1   | 1 week        | Micro-C data availability        |
| Phase 2   | 1-2 weeks     | Phase 1 complete                 |
| Phase 3   | 1 week        | Can run in parallel with Phase 2 |
| Phase 4   | 1 week        | Phases 2-3 complete              |
| **Total** | **4-6 weeks** |                                  |

---

## Anti-Overfitting Safeguards

1. Training and validation loci on DIFFERENT chromosomes
2. Parameters fitted ONCE on training locus, never adjusted for validation
3. All code committed BEFORE running validation (pre-registration via git timestamp)
4. Negative results reported honestly (if SOX2 r < 0.15)
5. No post-hoc threshold adjustment

---

_"Fit on A, Predict on B — the only honest way to validate a model."_
