# PAPER 3 SKELETON — Working Draft

**Working title:**
A Physics-Informed Loop-Extrusion Chromatin Score Reduces to a Consequence-Category
Lookup: A Reproducible Falsification Audit Across Nine Disease Loci

**Status:** SKELETON — REFRAMED per novelty gate (2026-06-12). Numbers filled; prose
placeholders marked `[WRITE: ...]`.
**Positioning (post novelty-check):** This is a **negative-result case study**, not a
novel-framework paper. The heterogeneity/category-inflation critique is established
(Lu et al. 2025, bioRxiv 10.1101/2025.09.05.674459); we *operationalize* it on a new
model class (physics-informed loop-extrusion simulation) and contribute (i) the first
reproducible falsification audit of such a simulator and (ii) a locus-general
**mirror diagnostic** (sign-flip ablation). See `novelty_check.md`.
**Date:** 2026-06-05 (drafted) / 2026-06-12 (reframed)
**Evidence level:** [VERIFIED-INLINE] for all numbers (real ClinVar data + real HUDEP-2 Hi-C)
**Target venues (ranked, negative-result-friendly):**
1. PLOS Computational Biology — accepts rigorous negative results / cautionary studies
2. GigaScience / F1000Research — reproducibility + negative results explicitly welcomed
3. Bioinformatics (Applications Note) or a Matters-Arising-style note
**Estimated length:** 4,000–5,500 words + 5 figures + 2 supplementary tables

---

## TITLE PAGE

**Title:**
A Physics-Informed Loop-Extrusion Chromatin Score Reduces to a Consequence-Category
Lookup: A Reproducible Falsification Audit Across Nine Disease Loci

**Short title:**
Auditing a 3D Chromatin Variant Score

**Author:**
Sergey V. Boiko [ORCID: register before submission]
Independent Researcher, Almaty, Kazakhstan
sergeikuch80@gmail.com

**AI assistance disclosure:**
Computational analyses were performed with AI assistance (Claude, Anthropic).
All code is available at https://github.com/sergeeey/ARCHCODE with full
Co-Authored-By Git history.

---

## ABSTRACT (~250 words)

**Background:**
Aggregate performance metrics for variant pathogenicity predictors are inflated by
consequence-category heterogeneity: pathogenic and benign variants occupy different
category distributions, so a score that merely tracks category appears to discriminate
(Lu et al. 2025). The recommended remedy — within-category, covariate-matched
evaluation — is established for sequence- and deep-learning-based predictors but has
not been applied to *physics-informed* 3D chromatin simulations, which are increasingly
proposed as orthogonal structural layers for variant interpretation. We ask whether a
loop-extrusion structural similarity score (LSSIM) carries any signal beyond
consequence category and regulatory-distance baselines, and we contribute a
locus-general sign-flip diagnostic that decides this directly.

**Methods:**
We developed a six-gate falsification framework for auditing chromatin-based variant
scores and applied it to LSSIM (Local Structural Similarity Index) from the ARCHCODE
loop-extrusion simulation. We tested LSSIM across six experiments spanning four
erythroid loci: HBB matched-category test (n = 1,103 ClinVar variants), regulatory
confound models (K1: R² decomposition; K2: incremental AUC), BCL11A second-locus
test, GATA1 matched-category test (n = 183 variants), a HUDEP-2 real Hi-C retest
(GSM4873116, 5 kb resolution) of the HBB locus, and a multi-locus instrument
characterization using the engine's built-in effect-mode ablations
(categorical / position-only / uniform / inverted / random) across HBB, GATA1, HBA1.

**Results:**
The residual-signal hypothesis was falsified in all six configurations. The decisive
evidence is that LSSIM adds nothing to a consequence-category baseline: it is 90.7%
explained by category alone (R² = 0.907; 93.3% with CTCF distance), and adding it to a
category-only classifier does not improve label prediction (5-fold CV AUC 0.980 vs
0.980). Consistently, the naive pathogenic-vs-benign separation (Cohen's d = −2.67)
collapses by ≥87% after category stratification (residual |d| ≤ 0.34, weighting-
dependent). Within-category tests are underpowered in HBB ClinVar (≤12 pathogenic per
balanced category) and are reported as a secondary check. A built-in effect-mode
ablation across all three loci confirms the mechanism: inverting the category-severity
lookup mirrors the global AUC (AUC_categorical ≈ 1 − AUC_inverted; gaps 0.003 / 0.024 /
0.057 for HBB / GATA1 / HBA1), and position alone is indistinguishable from noise
(position-only ≈ random) — a sign-flip diagnostic of a directional category lookup.
GATA1 showed wrong-direction LSSIM in its most-balanced category (missense AUC = 0.464).
The tissue-matched HUDEP-2 real Hi-C retest failed on resolution: all 1,103 HBB
variants fell in a single 5 kb bin and the analytical model did not reproduce the real
contact map (off-diagonal r = 0.16, p = 0.30).

**Conclusions:**
Operationalising the established matched-control critique (Lu et al. 2025) on a new
model class, we show a physics-informed structural score reduces to a directional
category lookup, and we contribute the mirror diagnostic as a cheap, decisive check.
The audit specifies what a fair test requires — tissue-correct Hi-C at ≤1 kb
resolution, regulatory non-coding variants, and pre-registered matched controls.
Until these conditions are met, LSSIM-based pathogenicity claims are not independently
supported. The audit and diagnostic are reusable for any chromatin structural score.

**Keywords:** β-thalassemia, HBB, GATA1, chromatin loops, LSSIM, falsification
framework, matched controls, negative result, variant interpretation, loop extrusion,
category artifact, 3D genome

---

## 1. INTRODUCTION (~600 words)

### 1.1 The appeal and the risk of 3D chromatin variant scores

Three-dimensional chromatin topology is mechanistically implicated in human disease.
Structural variants that reposition topologically associating domain (TAD) boundaries
can rewire enhancer–promoter contacts and cause developmental phenotypes; disruption
of a CTCF boundary at the *EPHA4* locus, for example, allows enhancers to "hijack"
neighbouring genes and produce limb malformations (Lupiáñez et al. 2015, Cell
161:1012–1025; reviewed in Spielmann et al. 2018, Nat Rev Genet 19:453–467). These
findings motivate a class of computational tools that predict how a variant perturbs
3D genome folding — sequence-based deep-learning models such as Akita (Fudenberg et
al. 2020, Nat Methods 17:1111–1117) and Orca (Zhou 2022, Nat Genet 54:725–734), and
physics-informed loop-extrusion simulations that compute a structural-similarity score
between wild-type and mutant contact maps. Such scores are increasingly proposed as an
*orthogonal* layer for variant interpretation, complementary to sequence conservation
and consequence annotation.

The appeal carries a specific risk. A structural score that *appears* to separate
pathogenic from benign variants may simply be recapitulating a simpler, cheaper
annotation — consequence category, CADD, or distance to a regulatory element — rather
than adding independent 3D information. Distinguishing genuine structural signal from
an annotation proxy requires controls that the headline metric (a single
pathogenic-vs-benign AUC) does not provide.

### 1.2 The matched-control problem

This risk is not hypothetical: aggregate AUC for variant pathogenicity predictors is
inflated by consequence-category heterogeneity. Because pathogenic and benign variants
occupy very different category distributions — in ClinVar, pathogenic variants are
enriched for severe categories (nonsense, frameshift, canonical splice), while benign
variants are dominated by intronic and synonymous changes — a score that merely tracks
category will achieve a high AUC while containing no within-type discriminative
information. Lu et al. (2025, bioRxiv 10.1101/2025.09.05.674459) show that a
substantial part of reported predictor performance reflects this between-category
prevalence difference rather than the ability to separate pathogenic from benign
variants *of the same type*, and that the appropriate remedy is within-category,
covariate-matched evaluation. This is a genomics instance of confounding by group
composition (Simpson's paradox): a between-group association can vanish, or reverse,
once the confounder is held fixed. The matched-control remedy is established for
sequence- and deep-learning-based predictors; whether physics-informed 3D simulations
escape or merely re-express the same artifact has not been tested.

### 1.3 ARCHCODE as a case study

We use ARCHCODE, an open-source physics-informed framework that is **our own prior
work**, as a tractable case study; this paper is therefore a self-correcting audit of a
score we previously promoted, which also accounts for the source-level access we
exploit below.
ARCHCODE runs a mean-field loop-extrusion simulation (Kramer-type kinetics with CTCF
barriers) to produce paired wild-type and mutant contact maps for each variant, and
summarizes their difference as the Local Structural Similarity Index (LSSIM). It is an
ideal benchmark for two reasons: it is fully reproducible and open, and its scoring
path can be traced to source. That tracing reveals the central mechanism — per-variant
perturbation magnitude is set by a hardcoded `CATEGORICAL_EFFECTS` lookup keyed on
consequence category (`generate-unified-atlas.ts`), so LSSIM is, by construction, a
deterministic function of category. Any pathogenic-vs-benign LSSIM gap is therefore at
risk of being a restatement of the category mix — exactly the artifact Lu et al.
describe — making ARCHCODE a clean system in which to demonstrate, and decisively
diagnose, that failure mode.

### 1.4 Aims and contributions

We do **not** claim to introduce the matched-control critique, which is established
(Lu et al. 2025). Our contributions are:
1. The first reproducible, source-traced falsification audit of a *physics-informed
   loop-extrusion* variant score, across three erythroid loci (HBB, GATA1, HBA1; with
   BCL11A as a coverage-limited fourth case).
2. A locus-general **mirror diagnostic**: a sign-flip ablation in which inverting the
   category-severity lookup mirrors the AUC (AUC_categorical ≈ 1 − AUC_inverted),
   directly proving a score is a *directional category lookup* with no positional
   resolution — a sharper test than label permutation (which collapses to 0.5).
3. An explicit specification of what a fair test of such scores requires
   (tissue-correct Hi-C at ≤1 kb, regulatory non-coding variants, pre-registered
   matched controls), grounded in a tissue-matched real-Hi-C retest that fails on
   resolution.

---

## 2. METHODS

### 2.1 The audit gate sequence

We apply the following ordered gate sequence, which consolidates established
matched-control practice (Lu et al. 2025 and references therein) into a single
reproducible checklist for chromatin-based variant scores. We do not claim the
individual controls as novel; the value is the packaged, source-traced application to
a physics-informed score. A score fails the audit if it cannot pass any single gate;
all gates must pass for the score to be considered a valid independent predictor.

**Gate 1 — Category baseline:**
Compute CV AUC for Model B (label ~ consequence category, one-hot encoded) without
the structural score. If category AUC ≥ 0.80, the task is largely solved by
annotation. The structural score must demonstrate *incremental* improvement.

**Gate 2 — Matched-category test (non-circular test):**
Restrict analysis to consequence categories containing both pathogenic and benign
variants with n ≥ 10 per group. Compute within-category Mann-Whitney U AUC.
A score passes only if AUC > 0.60 with p < 0.05 in the most-powered category.
This is the only non-circular test for scores with deterministic category components.

**Gate 3 — Regulatory-distance confound:**
Regress the structural score on consequence category + distance to nearest CTCF
site. Compute R². If R² > 0.80, the score is a structural-annotation proxy, not
independent structural information (Kill criterion K1).

**Gate 4 — Incremental AUC (K2):**
Compare Model B (category) vs Model C (category + structural score). If ΔAUC < 0.01,
the structural score adds no predictive value (Kill criterion K2).

**Gate 5 — Tissue-match gate:**
Verify that regulatory annotations (CTCF ChIP-seq, H3K27ac) used in the simulation
match the biologically relevant tissue for the locus. K562 ≠ erythroid; failing
this gate means the structural context is incorrect regardless of statistics.

**Gate 6 — Resolution gate:**
Verify that the Hi-C data used (or the simulation resolution) is sufficient to
discriminate variants at the scale of interest. For intra-gene variants, ≤1 kb
resolution is required. If all variants fall in a single bin, the test cannot be run.

### 2.2 Data sources

**HBB variants:**
ClinVar HBB variants retrieved via NCBI E-utilities API (2026). n = 1,103 total
(353 pathogenic, 750 benign). Atlas: HBB_Unified_Atlas_95kb.csv. LSSIM computed
by ARCHCODE simulation (CATEGORICAL_EFFECTS lookup, source: generate-unified-atlas.ts
lines 291–352, commit [CITE]). [VERIFIED-INLINE — real ClinVar data, analytical LSSIM]

**GATA1 variants:**
ClinVar GATA1 variants. n = 183 total. Atlas: GATA1_Unified_Atlas_300kb.csv.
Regulatory annotations: ENCODE K562 CTCF, K562 H3K27ac (tissue mismatch — see
Results 3.3). [VERIFIED-INLINE]

**HUDEP-2 Hi-C:**
GEO accession GSM4873116. WT-HUDEP2 capture Hi-C, KR-balanced.
Extracted at 5 kb resolution, chr11:5200000–5250000 (10×10 matrix).
[VERIFIED-INLINE — real public Hi-C data]

**BCL11A:**
ClinVar variants queried via ARCHCODE GraphQL atlas; 3/3 pathogenic-annotated
variants and 6/6 benign-annotated variants returned `not_observed` in
position-matched controls, indicating the atlas coverage does not extend to
these positions. [VERIFIED-INLINE]

### 2.3 Statistical methods

- Cohen's d computed on full pathogenic/benign distribution and within consequence
  category (category-stratified pooled d)
- Mann-Whitney U one-sided AUC: AUC = U/(n_path × n_benign)
- Cliff's delta for effect size
- Bootstrap 95% CIs: 5000 resamples, seed 20260605
- Logistic regression CV AUC: 5-fold stratified, scikit-learn v[VERSION]
- Spearman correlation for CTCF-distance analysis
- Pearson r for Hi-C analytical-vs-real comparison

All analyses: Python 3.11. Code: results/p2_hbb_truth/, results/p3_confound/,
results/p1_gata1_matched/, results/p4_hudep2_hbb/.

---

## 3. RESULTS

### 3.1 HBB: The category artifact quantified

#### 3.1.1 Category distribution creates apparent signal

The HBB ClinVar dataset (n = 1,103) is structurally category-imbalanced:
pathogenic variants are dominated by severe categories (nonsense, frameshift, missense,
splice), none of which contain benign variants in ClinVar HBB. Benign variants are
87.7% intronic. This near-complete category disjointness between pathogenic and benign
groups means any score that differs systematically by consequence category will
achieve high AUC by construction.

#### 3.1.2 LSSIM is a deterministic function of category

Code inspection of `scripts/generate-unified-atlas.ts` (lines 291–352) reveals that
LSSIM is computed via a hardcoded lookup:
```
CATEGORICAL_EFFECTS = { nonsense: 0.10, frameshift: 0.15, splice_*: 0.20,
                        missense: 0.40, intronic: 0.80, synonymous: 0.90, ... }
```
The effectStrength from this lookup scales occupancy reduction, which drives the
contact-map perturbation, which determines LSSIM. LSSIM is therefore a deterministic
function of consequence category: **low LSSIM ⟺ severe category, by construction**.

#### 3.1.3 Cohen's d collapse under stratification

| Analysis | Cohen's d | Interpretation |
|---|---:|---|
| Naive (full pathogenic vs benign) | **−2.67** | Appears strong |
| Category-stratified pooled d (min-weighted) | **−0.34** | Small residual |
| Category-stratified pooled d (size-weighted) | **≈ 0.0** (+0.02) | Effectively null |

The naive d of −2.67 collapses toward zero after category stratification. The exact
residual depends on the per-category weighting: weighting each category's within-class
d by min(n_path, n_benign) gives −0.34, while weighting by total category n gives
≈ 0. We report both: under either choice the effect collapses by ≥87%, and the
stratified |d| ≤ 0.34 — i.e., from a large to a negligible effect. (We do not lean on
the precise value; the robust evidence is K1/K2 below.)

#### 3.1.4 Within-category test (underpowered secondary check)

Within-category comparison is the only non-circular test, but in HBB ClinVar it is
underpowered: severe categories contain zero benign variants, and the categories that
do contain both classes have very few pathogenic variants.

| Category | n | n_path | n_benign | AUC | MW p | Note |
|---|---:|---:|---:|---:|---:|---|
| intronic | 667 | 9 | 658 | 0.524 | 0.80 | most n, but only 9 pathogenic |
| synonymous | 86 | 3 | 83 | 0.570 | 0.62 | 3 pathogenic |
| other | 19 | 12 | 7 | **0.774** | **0.056** | most balanced — trends toward signal |

The most-powered category (intronic) is at chance (AUC 0.524), but with only 9
pathogenic variants this cannot *exclude* a moderate effect. Conversely, the
most-balanced category, `other` (12 vs 7), trends positive (AUC 0.774, p = 0.056).
The within-category evidence is therefore **mixed and underpowered**, and we do not
treat it as decisive. The decisive evidence that LSSIM carries no category-independent
signal is the incremental-AUC and confound analysis (§3.2): adding LSSIM to a
category-only model does not improve prediction, and LSSIM is 90.7% explained by
category alone.

**Mechanistic note on the intronic null.** Within the 658 benign intronic variants,
LSSIM encodes CTCF-anchor proximity with Pearson r = 0.709 (p < 0.0001; Figure S1A):
variants closer to the nearest loop anchor receive lower LSSIM, confirming the
simulator responds to sub-loop 3D architecture. However, the total gradient spans
only 0.005 LSSIM units (0.9915–0.9966), and the 9 pathogenic IVS-II-1 variants
cluster in the intermediate-to-far anchor regime (1,180–2,260 bp from the nearest
CTCF site), with LSSIM values (0.9917–0.9964) fully overlapping the benign
distribution (Figure S1B). This is mechanistically expected: IVS-II-1 splicing
mutations are pathogenic through RNA processing failure, not through chromatin
reorganization — LSSIM correctly classifies them as 3D-benign. The intronic AUC
= 0.524 is therefore not a classifier failure but a structurally correct prediction
for variants whose pathogenicity mechanism is orthogonal to 3D architecture. The
open prediction is that within-category signal *would* emerge for noncoding variants
that disrupt CTCF binding motifs (see §4.3).

[FIGURE 1: Two-panel. Left: naive LSSIM distribution pathogenic vs benign (high d).
Right: within-category distributions showing overlap; intronic AUC dot with 95% CI
straddling 0.5]

[FIGURE S1: (A) Scatter of LSSIM vs. distance to nearest CTCF anchor for n = 658
benign intronic HBB variants (Pearson r = 0.709). Red diamonds: 9 pathogenic IVS-II
variants. (B) LSSIM histograms for benign vs. pathogenic intronic — complete overlap.
Source: FigureS1_intronic_ctcf_gradient.png]

### 3.2 Regulatory confounds: CTCF distance as a proxy

#### 3.2.1 Kill criterion K1 — LSSIM explained by category + CTCF distance

| Model | R² (LSSIM) |
|---|---:|
| LSSIM ~ category alone | **0.907** |
| LSSIM ~ category + CTCF distance | **0.933** |

Category alone explains 90.7% of LSSIM variance. Adding CTCF distance brings R² to
0.933. LSSIM is nearly a deterministic function of two simple structural annotations.
**K1 fires.**

Within intronic variants only (where category is constant), LSSIM correlates with
distance to nearest CTCF site: Spearman ρ = 0.735. The residual LSSIM variance is
substantially driven by regulatory-element distance.

#### 3.2.2 Kill criterion K2 — incremental AUC

| Model | CV AUC |
|---|---:|
| A: label ~ LSSIM only | 0.970 |
| B: label ~ category | 0.980 |
| C: label ~ category + LSSIM | 0.980 |

Model C = Model B: adding LSSIM to category does not improve label prediction
(ΔAUC = 0.000 to three decimal places). **K2 fires.**

[FIGURE 2: Bar chart of model AUCs A–C. Inset: LSSIM vs CTCF-distance scatter
within intronic variants with Spearman ρ annotation]

### 3.3 GATA1 and HBA1: second-locus tests fail tissue-match gate

#### 3.3.1 Pre-gate: non-degeneracy

A preliminary screen confirmed that GATA1 and HBA1 atlases contain sufficient
within-category variant representation (both missense and synonymous categories
have n ≥ 5 per class) to run a matched test, unlike BCL11A (Gate 5 fires before
statistics; see 3.4).

#### 3.3.2 GATA1 tissue mismatch (Gate 5)

The GATA1 atlas uses ENCODE K562 CTCF and H3K27ac ChIP-seq as the regulatory
landscape. K562 is a leukemic myelogenous (CML) cell line; GATA1 is an essential
erythroid/megakaryocyte transcription factor. The biologically relevant tissue
(erythroid progenitors, HUDEP-2, or CD34+ cells) has a substantially different
CTCF and enhancer landscape at the GATA1 locus. **Gate 5 fires before matched
statistics are run.**

#### 3.3.3 GATA1 positional degeneracy (Gate 6 — partial)

All 183 GATA1 variants span 3,117 bp (chrX:48791049–48794166), entirely within
the GATA1 gene body (exons 2–6). A 300 kb simulation window cannot resolve
variants within the same 3 kb bin. There is no regulatory spread.

#### 3.3.4 GATA1 within-category test — wrong direction (Gate 2)

| Category | n | n_path | n_benign | AUC | Direction | MW p |
|---|---:|---:|---:|---:|---|---:|
| missense | 59 | 34 | 25 | **0.464** | ❌ wrong | 0.644 |
| synonymous | 89 | 3 | 86 | **0.314** | ❌ wrong | 0.194 |
| intronic | 22 | 3 | 19 | 0.710 | ✓ (n=3) | 0.228 |

Missense is the most balanced category (34 path, 25 benign). LSSIM for pathogenic
missense variants is *higher* than for benign (ΔLSSIM = +0.00091) — the opposite
of the expected direction. AUC = 0.464, below chance. **Gate 2 fires in the wrong
direction.** K3 fires: GATA1 is not promoted to positive evidence.

[FIGURE 3: GATA1 within-category AUC panel. Left: missense and synonymous AUC
estimates with 95% CIs, showing below-chance with wrong direction. Right: variant
position map showing 3,117 bp clustering.]

### 3.4 BCL11A: second-locus test fails coverage gate

GraphQL queries to the BCL11A ARCHCODE atlas returned `not_observed` for
3/3 pathogenic-annotated and 6/6 benign-annotated variants in position-matched
controls. Atlas coverage does not extend to these positions. The test cannot
be run without atlas expansion. [WRITE: 1–2 sentences on why BCL11A was
prioritized as a candidate — enhancer biology rationale]

### 3.5 HUDEP-2 real Hi-C retest: resolution and model failures

#### 3.5.1 Resolution failure (Gate 6)

HUDEP-2 capture Hi-C (GSM4873116) was extracted at 5 kb resolution over
chr11:5200000–5250000 (10 bins). All 1,103 HBB ClinVar variants
(positions 5225454–5249000) fall in a single bin (bin 5: 5225000–5230000).
At 5 kb resolution, no positional discrimination between variants is possible.

Re-extraction at ≤1 kb (the capture Hi-C data contains sub-kb information) would
provide ~1–2 bins within the HBB gene body and is required for any positional test.

#### 3.5.2 Analytical model vs real Hi-C (Gate 6 — model validity)

| Metric | Value |
|---|---:|
| Pearson r (contact-by-contact, off-diagonal) | **0.16** |
| p-value | 0.30 (not significant) |
| Spearman r | 0.11 |
| SSIM (analytical vs HUDEP-2) | 0.9686 |

The SSIM of 0.97 is misleading — it reflects global distributional similarity
(matched mean and variance after KR normalization), not contact-by-contact agreement.
The Pearson r = 0.16 (p = 0.30) is diagnostic: the analytical mean-field contact
map does not reproduce real HUDEP-2 chromatin organization. **The simulation model
does not validate against the tissue-correct reference.**

#### 3.5.3 Hybrid LSSIM: AUC = 0.50 exactly (Gate 2)

Because all variants share the same 5 kb bin AND the same CATEGORICAL_EFFECTS
per category, the hybrid LSSIM (replacing analytical WT with HUDEP-2 WT) is a
**constant** within every consequence category. AUC = 0.5000 exactly for all
testable categories (intronic, synonymous, other) — the strongest possible null.
This is not near-chance; it is mathematically guaranteed null by the binning.

[FIGURE 4: HUDEP-2 retest figure. Left: 10×10 HUDEP-2 Hi-C heatmap with HBB gene
body marked, showing all variants in bin 5. Right: analytical vs real HUDEP-2
contact correlation scatter, r=0.16 annotated.]

### 3.6 Instrument characterization: the signal is a directional category lookup (8/9 loci)

To establish *what* LSSIM actually resolves, we ran the engine's built-in
effect-mode ablations as calibrated reference signals across **nine unrelated disease
loci** spanning 8,134 ClinVar variants. Each mode sets the per-variant perturbation
magnitude independently: `categorical` (operating point), `position-only` (fixed
magnitude, category erased), `uniform-medium` (sanity copy), `inverted` (category
lookup with swapped sign), and `random` (noise floor). Two diagnostics follow: the
**mirror gap** |AUC_categorical − (1 − AUC_inverted)| and the **position–random gap**
|AUC_position-only − AUC_random|.

| Locus | Disease | nP | nB | cat AUC | mirror gap | pos−rand gap |
|---|---|---:|---:|---:|---:|---:|
| SCN5A | cardiac arrhythmia | 928 | 1560 | 0.589 | **0.000** | 0.001 |
| BCL11A | HbF/intellectual disability | 44 | 49 | 0.901 | **0.001** | 0.185 |
| HBB | β-thalassemia | 353 | 750 | 0.976 | **0.002** | 0.060 |
| PTEN | cancer/PHTS | 703 | 793 | 0.859 | **0.003** | 0.003 |
| TERT | cancer/telomere | 431 | 1658 | 0.841 | **0.023** | 0.019 |
| GATA1 | anemia/leukemia | 52 | 131 | 0.838 | **0.024** | 0.071 |
| HBA1 | α-thalassemia | 67 | 44 | 0.770 | **0.057** | 0.009 |
| LDLR | hypercholesterolemia | 2274 | 1010 | 0.592 | **0.078** | 0.013 |
| GJB2 | deafness | 314 | 155 | 0.853 | *0.108* | 0.007 |

Three results hold across 8/9 loci (mean mirror gap = 0.033): (i) **the mirror
property** — categorical ≈ (1 − inverted), so flipping the category-severity sign
flips the global AUC; (ii) **position alone is noise** — position-only ≈ random ≈
chance at every locus; (iii) **the mirror holds even when category discrimination is
weak** — SCN5A (cat AUC = 0.589, nearest to chance) shows a gap of 0.000, and LDLR
(cat AUC = 0.592, n = 3,284) a gap of 0.078, demonstrating that LSSIM is fully
determined by the category lookup *regardless of* how discriminative that lookup is.

The GJB2 outlier (gap = 0.108) is mechanistically explained: GJB2 ClinVar variants
span 1.9 Mb, six-fold the 300 kb simulation window, compressing all LSSIM values into
a 0.024-unit band near 1.0 (missense σ = 0.00067 vs HBB missense σ = 0.023). The
window-size mismatch creates an asymmetric response between categorical and inverted
modes, not a genuine position signal (position–random gap = 0.007 ≈ 0).

Critically, the within-category missense AUC is **invariant to sign inversion**
(GATA1: 0.464 categorical vs 0.482 inverted; HBA1: 0.578 vs 0.572) — because within a
single category the lookup is constant. The global AUC measures the category lookup
and nothing else; the within-category channel carries no usable signal. The HBB-only
finding is thereby shown to be locus-general across 8 unrelated diseases.

We are explicit that the mirror is **near-tautological** where category separation is
strong: because LSSIM is monotone in the category lookup, inverting the lookup
necessarily approximately reverses the rank order. The mirror is therefore a
*confirmatory diagnostic of lookup-monotonicity*, not independent corroboration of the
negative result (which rests on the incremental-AUC analysis, §3.2). The genuinely
informative quantity is the deviation from a perfect mirror — the gap quantifies the
small non-category (positional/tie) component that survives inversion.

[FIGURE 5: Transfer-function panel across 9 loci. (A) Dot-strip of categorical AUC
and (1 − inverted AUC) per locus — pairs nearly coincide everywhere, confirming the
mirror. (B) Mirror gap per locus, sorted ascending; GJB2 labelled as window-mismatch
outlier. (C) Position–random gap per locus — all near zero. (D) Within-category
missense AUC across all 5 modes for GATA1 and HBA1 — flat near chance regardless of
mode, visualizing sign-invariance.]

[Source: results/p5_instrument/MULTILOCUS_GENERALITY.json; MULTILOCUS_GENERALITY_NOTE.md]

---

## 4. DISCUSSION (~700 words)

### 4.1 Summary of findings

Across six configurations spanning four erythroid loci, the LSSIM structural score
showed no signal independent of consequence category. It (a) adds nothing over a
category-only model (K2: CV AUC 0.980 vs 0.980); (b) is 90.7–93.3% explained by
category and CTCF distance (K1); (c) is at chance in the only non-circular HBB test
(intronic AUC 0.524, p = 0.80) and in the wrong direction in the most-powered GATA1
test (missense AUC 0.464); (d) collapses to exact chance on tissue-matched real Hi-C,
where 5 kb resolution places all 1,103 HBB variants in one bin (AUC 0.5000); and (e)
is revealed by the sign-flip ablation to be a directional category lookup across
eight of nine loci (mirror gaps 0.000–0.108, mean 0.033; GJB2 outlier mechanistically
explained by simulation-window mismatch), with position alone indistinguishable from
noise at every locus. Notably, the mirror holds even when categorical AUC is near
chance (SCN5A gap = 0.000 at cat AUC = 0.589; LDLR gap = 0.078 at cat AUC = 0.592),
showing that LSSIM is a category lookup regardless of how discriminative that lookup is
across 8,134 ClinVar variants spanning eight unrelated diseases.

### 4.2 The root cause is structural, not statistical

The mechanism is traceable to source. Per-variant perturbation magnitude is read from
a hardcoded `CATEGORICAL_EFFECTS` lookup keyed on consequence category, so LSSIM is a
deterministic function of category by construction; the only additional degree of
freedom for non-splice variants is the variant's position, which the ablation shows
carries no discriminative signal. This is not a coding defect — the lookup encodes a
defensible prior that severe consequence classes perturb local occupancy more — but it
means LSSIM *cannot, in principle*, contain category-independent information. The
mirror diagnostic makes this concrete: inverting the lookup's sign inverts the global
AUC, while the within-category channel (where the lookup is constant) is unmoved.

A second, independent failure compounds the first. Even setting category aside, the
mean-field contact map does not reproduce measured chromatin organization: against
tissue-matched HUDEP-2 capture Hi-C the off-diagonal Pearson correlation is r = 0.16
(p = 0.30). The model is therefore mis-specified at the level of the contact map it
purports to perturb. Tissue mismatch aggravates both issues — the GATA1 and HBA1
atlases use K562 (a leukemic line) CTCF and H3K27ac as the regulatory landscape for
genes whose biology is erythroid.

### 4.3 What would constitute a fair test

These negative results define, rather than merely report, the conditions for a valid
test of a 3D structural variant score. Four are necessary: (1) Hi-C from the correct
tissue (HUDEP-2 or CD34+ erythroid progenitors) at ≤1 kb resolution, sufficient to
place intra-gene variants in distinct bins — re-extraction of GSM4873116 at 1 kb is a
concrete near-term step; (2) regulatory non-coding variants (promoter, locus-control-
region, CTCF-binding-disrupting), where 3D structure could plausibly differ between
pathogenic and benign — coding variants clustered in a few kilobases cannot exercise a
300 kb structural model; (3) within-category, covariate-matched controls pre-specified
before scores are computed; and (4) a simulation calibrated to reproduce the measured
contact map (target r > 0.5) before its perturbations are interpreted. None of the
five tested configurations satisfied all four, which is why the structural hypothesis
was untestable in the favourable direction here — not merely unsupported.

### 4.4 A reusable audit, not a new method

We emphasise that the matched-control principle is established (Lu et al. 2025); our
contribution is to operationalise it, with a source-traced negative control, for a
model class to which it had not been applied. The gate sequence used here is a
practical consolidation: any chromatin structural score claiming pathogenicity utility
should (i) exceed a category-only baseline, (ii) show a correctly-signed within-
category AUC, (iii) not be explained by category + regulatory distance, (iv) use
tissue-correct annotations, and (v) operate at a resolution that separates the
variants of interest. The **mirror diagnostic** adds one cheap, decisive check beyond
standard label permutation: where permutation collapses an artifactual AUC to 0.5, a
sign-flip ablation collapses it to 1 − AUC, distinguishing a *directional category
lookup* from mere overfitting.

### 4.5 Relationship to prior work

Our central statistical observation is not new. The category-heterogeneity inflation
of pathogenicity AUC, and the within-type remedy, are stated for frontier sequence and
deep-learning predictors by Lu et al. (2025); the broader confounding of genomic
predictors by annotation and allele-frequency strata is long recognised for tools such
as CADD (Kircher et al. 2014, Nat Genet 46:310–315). What is new here is the
application to a *physics-informed loop-extrusion*
score, the source-level demonstration that its signal is a category lookup, and the
locus-general mirror test. Compared with a bare "no association" report, this audit
specifies exactly which test would have been positive and under what data conditions —
turning a null result into a usable specification for the next experiment.

### 4.6 Limitations

1. ClinVar HBB pathogenic variants are not representative of the full pathogenicity
   spectrum — they are enriched for classic thalassemia mutations (severe coding)
2. GATA1 ClinVar variants are almost entirely from exons 2–6 — no regulatory spread
3. BCL11A atlas coverage was insufficient for the test — result is "cannot test",
   not "fails"
4. The ARCHCODE engine produces analytical (mean-field) contact maps — a stochastic
   polymer simulation might produce different LSSIM distributions
5. This analysis addresses the current ARCHCODE implementation; a version with
   measured Hi-C as input and tissue-correct regulatory features is explicitly
   encouraged

---

## 5. CONCLUSIONS (~100 words)

The hypothesis that a physics-informed loop-extrusion structural score (LSSIM) carries
pathogenicity information independent of consequence category was falsified in every
tested configuration across four erythroid loci. A source-traced sign-flip ablation
shows the apparent discrimination is a directional category lookup: inverting the
lookup mirrors the AUC at all three powered loci, while within-category signal is at
chance. The negative result is not the end point but a specification — a fair test of
such scores requires tissue-correct Hi-C at ≤1 kb, regulatory non-coding variants, and
pre-registered matched controls, none of which the current data provide. We release
the full audit and the mirror diagnostic as a reusable check for chromatin-based
variant scores.

---

## 6. FUTURE DIRECTIONS (optional short section or fold into Discussion)

1. **Re-extract HUDEP-2 Hi-C at 1 kb:** GSM4873116 data is available; re-extraction
   via `hic2cool` at 1 kb is computationally straightforward
2. **Erythroid-specific CTCF ChIP-seq:** Replace K562 CTCF with HUDEP-2 or CD34+
   CTCF for HBB, GATA1, HBA1 atlases
3. **Regulatory variant set:** ClinVar non-coding HBB variants (promoter, LCR,
   enhancer); synthetic regulatory variant VCF at known CTCF-binding positions
4. **Simulation calibration:** Fit Kramer kinetics parameters to HUDEP-2 Hi-C
   contact map rather than literature-derived estimates
5. **MPRA/CRISPR validation:** For any future positive LSSIM signal, require
   orthogonal wet-lab validation (massively parallel reporter assay or CRISPRi
   perturbation) before clinical claim

---

## REFERENCES (verified set + pending — see REFERENCES_REGISTRY.md)

**[VERIFIED-web] — DOI/venue confirmed (2026-06-12):**
- **Lu et al. 2025** — *Genomic heterogeneity inflates the performance of variant
  pathogenicity predictions.* bioRxiv. **DOI: 10.1101/2025.09.05.674459** — *seed /
  closest prior art; cite in Intro 1.2, Discussion 4.4–4.5.*
- **Fudenberg, Kelley & Pollard 2020** — *Predicting 3D genome folding from DNA
  sequence with Akita.* Nat Methods 17:1111–1117. DOI: 10.1038/s41592-020-0958-x
- **Zhou 2022** — *Sequence-based modeling of 3D genome architecture from kilobase to
  chromosome scale* (Orca). Nat Genet 54:725–734. DOI: 10.1038/s41588-022-01065-4
- **Spielmann, Lupiáñez & Mundlos 2018** — *Structural variation in the 3D genome.*
  Nat Rev Genet 19:453–467. DOI: 10.1038/s41576-018-0007-0
- **Lupiáñez et al. 2015** — *Disruptions of topological chromatin domains cause
  pathogenic rewiring of gene–enhancer interactions.* **Cell** 161:1012–1025.
  DOI: 10.1016/j.cell.2015.04.004 — *(corrected: skeleton previously mis-cited venue
  as "Science")*
- **Sabaté et al. 2024** — bioRxiv, cohesin loop duration. DOI: 10.1101/2024.08.09.605990
- **Rao et al. 2014** — *A 3D map of the human genome at kilobase resolution reveals
  principles of chromatin looping.* Cell 159:1665–1680. DOI: 10.1016/j.cell.2014.11.021
- **Treisman, Orkin & Maniatis 1983** — *Specific transcription and RNA splicing
  defects in five cloned β-thalassaemia genes.* **Nature** 302:591–596.
  DOI: 10.1038/302591a0 — *(corrected from skeleton's "Treisman 1982, Cell")*
- **Kircher et al. 2014** — *A general framework for estimating the relative
  pathogenicity of human genetic variants* (CADD). Nat Genet 46:310–315.
  DOI: 10.1038/ng.2892 — *category/strata-confound discussion (4.5)*
- **Landrum et al. 2018** — *ClinVar: improving access to variant interpretations and
  supporting evidence.* Nucleic Acids Res 46(D1):D1062–D1067. DOI: 10.1093/nar/gkx1153

**[PENDING] — verify or drop before submission (do NOT fabricate):**
- Orkin & Kazazian 1984, Annu Rev Genet 18:131–171 — DOI not tool-confirmed; optional
  (treisman1983 already covers β-thal molecular basis)
- Simpson's paradox / confounding-by-composition — 1 methodological ref (Intro 1.2)
- Cohen's d + Mann-Whitney AUC — 1 standard statistics ref (Methods 2.3)
- GEO GSM4873116 (depositing paper), ENCODE accessions — data citations

---

## DATA AVAILABILITY

All code and analysis artifacts:
https://github.com/sergeeey/ARCHCODE

Specific analysis scripts:
- `results/p2_hbb_truth/compute_hbb_severity.py` — HBB matched-category test
- `results/p3_confound/confound_models.py` — K1/K2 confound analysis
- `results/p1_gata1_matched/run_gata1_gate.py` — GATA1 gate
- `results/p4_hudep2_hbb/run_hudep2_gate.py` — HUDEP-2 retest

HUDEP-2 Hi-C: GEO GSM4873116 (public)
ClinVar variants: NCBI E-utilities (public)

Pre-registered governance rules: `results/p0_governance/RULES.md`

---

## FIGURE LEGENDS (drafts)

**Figure 1. HBB category artifact quantified.**
(A) Distribution of ARCHCODE LSSIM by ClinVar label (pathogenic, n = 353; benign,
n = 750). The naive separation (Cohen's d = −2.67) appears strong. (B) Same data
stratified by consequence category, showing near-complete category disjointness:
pathogenic variants are concentrated in severe categories (all LSSIM < 0.5) and
benign variants in intronic/synonymous (LSSIM ≈ 0.99). (C) Within-category
Mann-Whitney AUC for intronic (n = 667) and synonymous (n = 86) — the only
non-circular tests. Both are indistinguishable from chance (intronic: AUC = 0.524,
p = 0.80; 95% CI shown). Cohen's d collapses from −2.67 (naive) to −0.34 (stratified).

**Figure 2. LSSIM is a proxy for category and CTCF distance.**
(A) Incremental AUC of logistic regression models: LSSIM alone (0.970), category
alone (0.980), category + LSSIM (0.980). ΔAUC = 0.000. (B) R² decomposition:
LSSIM ~ category (R² = 0.907), LSSIM ~ category + CTCF distance (R² = 0.933).
(C) Within intronic variants: LSSIM vs. distance to nearest CTCF site (Spearman
ρ = 0.735, n = 667).

**Figure 3. GATA1 matched-category test: wrong direction and tissue mismatch.**
(A) Genomic map of GATA1 locus showing variant positions (all 183 variants within
3,117 bp of the gene body) vs. the 300 kb simulation window. (B) Within-category
Mann-Whitney AUC for missense (n_path = 34, n_benign = 25, AUC = 0.464) and
synonymous (AUC = 0.314). Both are below chance and in the wrong direction.
(C) Tissue annotation: K562 (wrong tissue for GATA1) vs. erythroid-appropriate
tissue (HUDEP-2, CD34+).

**Figure 4. HUDEP-2 real Hi-C retest: resolution and model failures.**
(A) 10×10 HUDEP-2 capture Hi-C contact matrix (chr11:5200000–5250000, 5 kb bins).
Red arrow marks bin 5 (5225000–5230000) containing all 1,103 HBB variants.
(B) Scatter plot: analytical contact map (mean-field) vs. real HUDEP-2 contact
values for each off-diagonal bin pair (Pearson r = 0.16, p = 0.30, not significant).
(C) Within-category AUC = 0.5000 for all testable categories (mathematical null
due to single-bin degeneracy).

**Figure 5. Instrument transfer function: LSSIM is a directional category lookup.**
(A) Global pathogenic-vs-benign AUC by effect-mode for HBB, GATA1, and HBA1. For each
locus the `categorical` bar and the `1 − inverted` bar are shown adjacent: their near
coincidence (mirror gap 0.003 / 0.024 / 0.057) demonstrates that sign-inverting the
category-severity lookup flips the discrimination — the AUC measures the lookup
direction. (B) Mirror gap and position-minus-random gap per locus; the latter ≈ 0
shows position-only ≈ random (no positional resolution). (C) Within-category missense
AUC across all five modes for GATA1 (0.46–0.56) and HBA1 (0.57–0.66), flat and near
chance — sign-invariant because within a category the lookup is constant.
[Source: results/p5_instrument/TRANSFER_FUNCTION_STATS.json]

---

## SUPPLEMENTARY

**Table S1.** Per-category HBB variant statistics: n, n_path, n_benign, mean LSSIM,
bootstrap 95% CI, within-category AUC (where testable), Mann-Whitney p, Cliff's delta.
[Source: HBB_SEVERITY_STATS.json]

**Table S2.** GATA1 within-category test results: all categories, AUC, direction,
Cliff's delta. Plus: model comparison A–E (label ~ LSSIM; ~ category; ~ cat+LSSIM;
~ cat+pos; ~ cat+pos+LSSIM).
[Source: GATA1_GATE_STATS.json]

---

## TODO BEFORE SUBMISSION

- [ ] ORCID: register and add to author line
- [ ] Author name: canonicalize "Boyko" vs "Boiko" (currently "Boyko" in HTML,
      "Boiko" in submission_metadata.json)
- [ ] arXiv badge in README: remove (no arXiv record)
- [ ] Add 3–5 comparator tool references (Akita/Orca/ChromoVar) to Introduction
- [ ] Add Simpson's paradox / confounding citation to Methods 2.2
- [ ] Write all [WRITE: ...] sections (Introduction, Discussion)
- [ ] Generate actual figures from analysis JSON files
- [ ] Verify Python/scikit-learn version numbers in Methods
- [ ] Choose target journal and format accordingly
- [ ] Run bioRxiv pre-submission check (or Research Square as alternative)

---

*Evidence summary: All quantitative claims in this skeleton are [VERIFIED-INLINE] —
computed from real ClinVar-derived HBB/GATA1 atlases and real HUDEP-2 Hi-C data
(GSM4873116). They are NOT [VERIFIED-REAL] independent pathogenicity validation.
Source scripts and JSON outputs are in results/p2_hbb_truth/, results/p3_confound/,
results/p1_gata1_matched/, results/p4_hudep2_hbb/.*
