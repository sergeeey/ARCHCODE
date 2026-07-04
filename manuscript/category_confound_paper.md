# Apparent 3D-structural variant-effect signal is explained by variant category, not structure: a category-matched evaluation across nine disease loci

*Assembled draft v1 — 2026-07-04. Full manuscript stitched from section files. All numbers sourced
from `results/fig_category_confound_stats.json`; run integrity-checker before submission.*

**Author:** Sergey Boyko (RIIS / independent). ORCID 0009-0009-2178-5701.
**Method under evaluation (ARCHCODE):** cite project preprint Research Square rs-9090074.

---

## Abstract

**Motivation.** Deep-learning and biophysical models that score variants by predicted disruption of
three-dimensional chromatin or protein structure are increasingly proposed for clinical variant
interpretation. Their discriminative performance is typically reported *marginally*, pooling variants
across functional categories. Because both pathogenicity and structural-disruption scores correlate
strongly with functional category, a marginal metric can credit a structural score for discrimination
fully attributable to category — a confound analogous to the circularity described for missense
predictors (Grimm et al., 2015).

**Results.** We evaluated a 3D chromatin structural-disruption score (ARCHCODE) on 24,238
high-confidence ClinVar variants (conflicting and uncertain classifications excluded) across nine
disease-associated loci, using a category-matched stratified concordance statistic with bootstrap
confidence intervals and two positive controls — CADD (supervised) and phyloP conservation (unsupervised). Marginally, the structural score separated
pathogenic from benign variants (AUC = 0.754, 95% CI 0.748–0.760); however, variant category alone
was more predictive (AUC = 0.827), and within-category discrimination collapsed to chance for both
structural metrics (SSIM 0.507; log-SSIM 0.430, 95% CI 0.419–0.440). The collapse was systematic across
7 of 8 evaluable loci (only TP53 retained partial signal, 0.794 → 0.664). Under the identical test, two
positive controls of different kinds retained their signal — the supervised predictor CADD
(0.989 → 0.991) and an unsupervised conservation score, phyloP (0.790 → 0.894) — demonstrating that
category matching preserves genuine per-variant information for scores of both types, and that the
structural score's collapse is specific to it rather than an artifact of an over-conservative test.

**Conclusion.** For the ARCHCODE structural-similarity scores at these nine loci, apparent pathogenicity
signal is explained by variant category rather than by structure beyond category. We recommend
category-matched evaluation with a positive control as a routine guard whenever a variant-effect score
is claimed to capture structure.

---

## 1. Introduction

Classifying genetic variants as pathogenic or benign is a central, unsolved problem in clinical
genomics, and a large fraction of observed variants remain of uncertain significance. To extend
prediction beyond protein-coding consequence, a growing family of methods scores variants by their
predicted disruption of three-dimensional genome or protein organization — from multiple-instance
models of TAD-boundary–disrupting structural variants [Nieboer & de Ridder 2020] to sequence-to-function
networks that emit chromatin contact maps [AlphaGenome 2025]. Such 3D-structural scores are attractive
because they promise a mechanism (loop or domain disruption) that annotation-based scores do not model.

The evidence offered for these methods is almost always a single pooled discrimination metric — an
AUC computed over variants of every functional category at once. This pooling is precisely where a
subtle failure can hide. Functional category (nonsense, promoter, intronic, …) is by itself a strong
predictor of pathogenicity, and structural-disruption scores are strongly correlated with category. A
pooled AUC therefore cannot distinguish a score that reads out biology from one that merely reads out
category composition — a confound in the same family as the circularity long known to inflate missense
predictor benchmarks [Grimm et al. 2015].

Here we ask a deliberately narrow question: does a 3D-structural variant-effect score add pathogenicity
signal *beyond* variant category? We answer it with a category-matched (stratified) concordance
statistic across nine disease-associated loci, anchored by a positive control (CADD) known to carry
per-variant signal. The design turns an ambiguous "does it work?" into a falsifiable one: a real
per-variant signal must survive category matching, and a valid test must let the positive control survive.

## 2. Related Work

**Computational prediction of 3D-structural variant effects.** svMIL/svMIL2 use multiple-instance
learning to predict pathogenic TAD-boundary–disrupting somatic SVs (average AUC 0.86 across cancer
types) [Nieboer & de Ridder 2020; Nieboer et al. 2021]; POSTRE predicts SV pathomechanisms from tissue-specific
chromatin data [POSTRE 2025]; Enformer and AlphaGenome emit contact maps and regulatory tracks from
sequence [AlphaGenome 2025]. The score evaluated here (ARCHCODE) belongs to this family. Across these
methods, performance is typically a single pooled AUC over heterogeneous categories.

**Circularity and confounding in variant-effect evaluation.** Grimm et al. showed evaluation is
hindered by two types of circularity — same variant, or same protein, in train and test — inflating
apparent accuracy [Grimm et al. 2015]; later work formalized protein-aware splits [Heijl et al. 2020],
and large benchmarks pre-process data to reduce inflating biases [Radjasandirane et al. 2025]. Our confounder is
distinct but related: functional *category* is both a strong pathogenicity predictor and correlated
with structural scores.

**Marginal success masking finer-grained failure.** Models excelling at population-level expression
prediction fail across individuals, mispredicting even the direction of effect [Sasse et al. 2023;
Huang et al. 2023]; similar limits are reported for AlphaGenome [AlphaGenome 2025]. The informative
test is stratified, not marginal.

**Positive controls and stratified evaluation.** We adopt CADD as a positive control and guard against
the "garden of forking paths" [Gelman & Loken 2014]. To our knowledge, category-matched evaluation with
an explicit positive control has not been systematically applied to 3D-structural variant-effect scores.

## 3. Methods

*(Full formulas in `category_confound_methods.md`.)*

**Dataset.** 30,318 ClinVar variants across nine loci (BRCA1, CFTR, GJB2, HBB, LDLR, MLH1, SCN5A,
TERT, TP53), annotated with functional category, ClinVar significance, and three scores (ARCHCODE
log-SSIM, CADD PHRED, VEP).

**Labels.** Pathogenic/Benign from ClinVar significance; conflicting (n=5,330) and no-significance
(n=750) excluded → 24,238 high-confidence variants (11,858 pathogenic / 12,380 benign).

**Discrimination.** Marginal concordance C (= ROC AUC) via mid-ranks; each score oriented to marginal
C ≥ 0.5, applied identically to the stratified statistic.

**Category-matched concordance.** Stratified c-statistic comparing pathogenic vs benign only within
the same category, weighted by comparable pairs:
C_strat = ( Σₖ |Pₖ||Bₖ| cₖ ) / ( Σₖ |Pₖ||Bₖ| ), where cₖ is the within-category concordance. This is a
conditional Harrell's C; it answers whether the score ranks a same-category pathogenic/benign pair
correctly.

**Positive controls.** Two controls of different kinds, so that survival cannot be attributed to score
provenance: CADD (supervised; training overlaps ClinVar) and phyloP100way conservation (unsupervised;
never trained on the labels), fetched from UCSC over each locus (95% variant coverage, 23,038 variants).
If both retain discrimination under the identical stratification, a competing score's collapse cannot be
blamed on the test being harsh on supervised or on unsupervised scores.

**Robustness to category definition.** The conclusion does not depend on the binning scheme. Removing
any single category one at a time (leave-one-category-out) left ARCHCODE's within-category concordance
in the range 0.417–0.478 (all below 0.55), so the collapse is driven by no single stratum, including the
dominant synonymous class (drop-synonymous = 0.478). Under a coarse three-group scheme (protein-
truncating / protein-substitution / noncoding-regulatory), ARCHCODE rose modestly to 0.538 (log-SSIM) and
0.594 (SSIM) — expected, since coarser groups retain more within-group category composition — while both
positive controls kept near-full discrimination (phyloP 0.869, CADD 0.990). Under every binning the
controls dominate the structural score by a wide margin; the qualitative conclusion is invariant to
category granularity.

**Uncertainty.** Nonparametric bootstrap (B=1,000, seed 20260704), 2.5–97.5 percentile CIs. Per-locus
repeated; HBB per-locus undefined after cleaning (label imbalance), pooled only.

**Implementation.** Python 3.11 (numpy, pandas, scipy). Code: `analysis/fig_category_confound.py`;
statistics: `results/fig_category_confound_stats.json`.

## 4. Results

Marginally, ARCHCODE's structural-similarity scores discriminated pathogenic from benign across 24,238
variants (SSIM C = 0.783; log-SSIM C = 0.754, 95% CI 0.748–0.760). Category alone was more predictive
(C = 0.827). Within category, discrimination collapsed to chance for **both** metrics (SSIM C = 0.507;
log-SSIM C = 0.430, 95% CI 0.419–0.440; **Fig. 1A**), systematically across 7 of 8 evaluable loci; only
TP53 retained partial signal (0.794 → 0.664). The slightly sub-0.5 value for log-SSIM is not a
sign-flipped (Simpson's-paradox) signal: the within-category direction is inconsistent across strata
(7 of 10 categories below, 3 above 0.5), it is driven by weak miscalibration in the large synonymous
stratum, and an over-optimistic per-stratum-oriented bound — choosing each category's sign from its own
labels — reaches only 0.57. The primary similarity metric (SSIM) sits at exactly chance.

The collapse is not an artifact of an over-strict test. Applied identically, both positive controls
retained discrimination: the supervised CADD (0.989 → 0.991) and the unsupervised conservation score
phyloP (0.790 → 0.894 — in fact *stronger* within category, as removing the categorical confound exposes
the true per-variant conservation signal; **Fig. 1B**). A VEP-derived score sat at chance in both
settings (≈0.51). Under one and the same procedure, two independent predictors of opposite provenance
keep their signal while both ARCHCODE structural metrics lose all of it.

**Figure 1.** `results/fig_category_confound.png`. (A) Per-locus marginal vs category-matched AUC
(dumbbell); all but TP53 collapse to the chance line. (B) Method comparison: both positive controls —
CADD (supervised) and phyloP (unsupervised) — survive category matching, while both ARCHCODE metrics
(SSIM, log-SSIM) collapse and VEP sits at chance. phyloP's within-category AUC (0.894) exceeds its
marginal (0.790) — removing the categorical confound exposes the true per-variant conservation signal.
Bootstrap 95% CI; phyloP on the 95% conservation-covered subset (23,038).

## 5. Discussion

At these nine loci, the apparent ability of a 3D-structural score to rank pathogenic above benign
variants is explained by variant category, not by structure; the positive control disciplines this
interpretation. The pattern echoes a broader lesson — strong marginal performance masking failure on
the finer question [Sasse et al. 2023; Huang et al. 2023; AlphaGenome 2025]. Our contribution is to make
the stratified evaluation explicit for 3D-structural pathogenicity scores and pair it with a positive
control, so a null result is interpretable.

We stress what this does **not** show: not that 3D genome organization is irrelevant to disease; not
that structural simulation is useless for visualization or mechanism at individual loci; and not
anything beyond the nine loci and single score examined. What it shows is specific: at per-variant
pathogenicity ranking, this structural score contributes nothing category does not already provide, and
a pooled-AUC benchmark would have credited it for absent signal. We recommend category-matched
evaluation with a positive control as a routine guard.

## 6. Limitations

Nine loci from one benchmark (not genome-wide). Two ARCHCODE similarity metrics (SSIM, log-SSIM) were
tested and both collapse; the method's full composite (insulation- and loop-integrity deltas) was not
available at nine-locus scale and could behave differently — a scoping caveat, not a tested claim.
**Positive controls.** To exclude that survival depends on score provenance we use two controls: the
supervised CADD (training overlaps ClinVar; available for a subset, 14,701/24,238) and the unsupervised
phyloP conservation (never trained on the labels); both survive category matching, so the stratified test
is not harsh on supervised or unsupervised scores per se, and ARCHCODE's collapse is specific. TP53 retains partial signal
(reported, not averaged away); within-category C = 0.430/0.507 is read as "no signal beyond category,"
not inverse prediction (Simpson's paradox tested and rejected, see Results). ClinVar ascertainment biases
correlate with category; HBB per-locus is undefined after cleaning.

## 7. Data and Code Availability

Benchmark: `results/integrative_benchmark.csv`. Analysis code: `analysis/fig_category_confound.py`
(main analysis + figure), `analysis/phylop_control.py` (unsupervised phyloP control). Statistics:
`results/fig_category_confound_stats.json`, `results/phylop_control.json`. Conservation source: UCSC
phyloP100way (hg38). ARCHCODE method: Research Square rs-9090074 (DOI 10.21203/rs.3.rs-9090074/v1).

## References

1. Grimm et al. 2015. Human Mutation 36(5):513–523. doi:10.1002/humu.22768. (PMC4409520)
2. Heijl et al. 2020 (preprint). bioRxiv 2020.05.06.080424.
3. Radjasandirane et al. 2025. Genomics. S0888754325000527.
4. Sasse et al. 2023. Nature Genetics 55:2060–2064. doi:10.1038/s41588-023-01524-6.
5. Huang et al. 2023. Nature Genetics. doi:10.1038/s41588-023-01574-w.
6. Nieboer & de Ridder 2020 (svMIL). Bioinformatics 36(Suppl_2):i692.
7. Nieboer et al. 2021. Scientific Reports 11. (PMC8277903)
8. POSTRE 2025 (preprint). medRxiv 2025.06.27.25329768.
9. AlphaGenome limitations 2025 (preprint). bioRxiv 2025.08.05.668750. (PMC12440111)
10. Gelman & Loken 2014. American Scientist 102(6):460.

---

## Pre-submission checklist
- [ ] integrity-checker: every number vs fig_category_confound_stats.json + integrative_benchmark.csv
- [ ] Verify all 10 references resolve (no 404); confirm svMIL2/Benchmark-65 exact author+year
- [ ] Confirm "Mind the Gap" published version vs preprint
- [ ] Figure 1 exported at journal DPI; panel labels legible
- [ ] Venue decision: NAR Genomics & Bioinformatics vs Bioinformatics vs Genome Research
- [ ] Cover letter framing: methods/cautionary, Grimm-2015 lineage
- [ ] Cooling-off 24h + skeptic pass before submit
