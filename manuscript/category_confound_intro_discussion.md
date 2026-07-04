# Category-Confound Paper — Intro / Results / Discussion / Limitations (draft v1, 2026-07-04)

Numbers → `results/fig_category_confound_stats.json`. Do not hand-edit; verify via integrity-checker.

## Introduction

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
predictor of pathogenicity, and structural-disruption scores are strongly correlated with category
(coding-disrupting variants tend to sit in different structural contexts than intronic ones). A pooled
AUC therefore cannot distinguish a score that reads out biology from one that merely reads out
category composition — a confound in the same family as the circularity long known to inflate missense
predictor benchmarks [Grimm et al. 2015].

Here we ask a deliberately narrow question: does a 3D-structural variant-effect score add pathogenicity
signal *beyond* variant category? We answer it with a category-matched (stratified) concordance
statistic evaluated across nine disease-associated loci, and we anchor the test with a positive
control (CADD) that is known to carry per-variant signal. The design turns an ambiguous "does it
work?" into a falsifiable one: a real per-variant signal must survive category matching, and a valid
test must let the positive control survive.

## Results

Marginally, the structural score (ARCHCODE log-SSIM) discriminated pathogenic from benign variants
across the pooled set of 24,238 high-confidence variants (concordance C = 0.754, 95% CI 0.748–0.760).
Variant category alone, however, was a stronger predictor (C = 0.827), a first indication that the
marginal signal is largely categorical. When variants were compared only within the same functional
category, discrimination collapsed to chance for both ARCHCODE metrics (SSIM C = 0.507; log-SSIM
C = 0.430, 95% CI 0.419–0.440; Fig. 1A, filled points), systematically: 7 of 8 evaluable loci fell to
the chance line, with only TP53 retaining partial within-category signal (0.794 → 0.664). The slightly
sub-0.5 log-SSIM value is not a sign-flipped signal (Simpson's paradox): the within-category direction
is inconsistent across strata (7 of 10 categories below, 3 above 0.5) and an over-optimistic
per-stratum-oriented bound reaches only 0.57.

This collapse is not an artifact of an over-strict test. Applied identically, two positive controls of
opposite provenance retained discrimination: the supervised CADD (0.989 → 0.991) and the unsupervised
conservation score phyloP (0.790 → 0.894 — in fact stronger within category, as removing the categorical
confound exposes the true per-variant conservation signal; Fig. 1B). A VEP-derived score sat at chance in
both settings (≈0.51). The contrast is the core result: under one and the same procedure, two
independent predictors keep their signal while both ARCHCODE structural metrics lose all of it. That a
purely unsupervised score (phyloP) survives is decisive — it shows the stratified test does not simply
penalize scores untrained on the labels.

## Discussion

At these nine loci, the apparent ability of a 3D-structural score to rank pathogenic above benign
variants is explained by variant category, not by structure. The interpretation is disciplined by the
positive control: because CADD survives the identical test, the structural score's collapse reflects
absence of signal beyond category rather than a penalty imposed by the method.

This pattern echoes a broader lesson in genomic modelling — that strong marginal performance can mask
failure on the finer question of interest. Sequence-to-function networks that excel at population-level
prediction fail to predict expression differences across individuals, often mistaking even the
direction of a variant's effect [Sasse et al. 2023; Huang et al. 2023], and similar limits have been
reported for AlphaGenome's personal-genome predictions [AlphaGenome 2025]. In each case the honest
evaluation is a stratified or matched one that isolates the claimed capability. Our contribution is to
make that evaluation explicit for 3D-structural pathogenicity scores and to pair it with a positive
control, so that a null result is interpretable rather than merely disappointing.

We stress what this does **not** show. It does not show that three-dimensional genome organization is
irrelevant to disease — the biology of TAD and loop disruption is well established. It does not show
that structural simulation is useless for its other purposes (visualization, hypothesis generation,
mechanism at individual loci). And it does not generalize beyond the nine loci and the single score
examined here. What it does show is specific and actionable: at the level of per-variant pathogenicity
ranking, this structural score contributes nothing a variant's category does not already provide, and
any benchmark that reports only a pooled AUC would have credited it for signal it does not carry. We
therefore recommend that category-matched evaluation with an explicit positive control be adopted as a
routine guard when a variant-effect score is claimed to capture structure.

## Limitations

- **Scope.** Nine loci from a single curated benchmark; this is not a genome-wide claim, and locus
  selection was not randomized.
- **Two metrics, not the full composite.** We evaluate both ARCHCODE similarity metrics (SSIM and
  log-SSIM) and both collapse; the method's full composite (insulation- and loop-integrity deltas) was
  not available at nine-locus scale and could behave differently — a scoping caveat, not a tested claim.
- **TP53 exception.** TP53 retained partial within-category signal (0.664) and is reported as such,
  not averaged away.
- **Positive controls.** Two controls of opposite provenance both survive: supervised CADD (training
  overlaps ClinVar; subset 14,701/24,238) and unsupervised phyloP conservation (never trained on the
  labels). Because both survive, the stratified test is not harsh on supervised or unsupervised scores
  per se, and ARCHCODE's collapse is specific. (phyloP available for 95% of variants, 23,038.)
- **Sub-0.5 within-category AUC.** SSIM sits at exactly chance (0.507); log-SSIM (0.430) lies slightly
  below, which we interpret as "no signal beyond category," not as an inverse predictor — the Simpson's-
  paradox alternative was tested and rejected (see Results).
- **Label source.** Labels derive from ClinVar and inherit its ascertainment biases, which are
  themselves correlated with category; conflicting and uncertain classifications were excluded.
- **HBB.** After label cleaning the HBB subset lacked within-locus label balance, so its per-locus
  statistic is undefined; HBB contributes only to the pooled estimate.

## Conclusion
Apparent 3D-structural variant-effect signal at these loci is explained by variant category, not by
structure. Category-matched evaluation with a positive control cheaply separates the two and should be
standard practice.
