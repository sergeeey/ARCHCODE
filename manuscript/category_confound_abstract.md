# Category-Confound Paper — Title + Abstract (draft v1, 2026-07-04)

All numbers sourced from `results/fig_category_confound_stats.json` + `results/integrative_benchmark.csv`.
Do NOT hand-edit numbers — pull from JSON (recurring "verified subset, claimed whole" guard).

## Title (primary)
**Apparent 3D-structural variant-effect signal is explained by variant category, not structure: a category-matched evaluation across nine disease loci**

### Alternatives
- Category confounding inflates apparent 3D-structural variant-effect signal: a systematic category-matched evaluation
- Structure or category? A positive-control test shows 3D variant-effect scores carry no signal beyond variant category

## Abstract (structured, ~250 words)

**Motivation.** Deep-learning and biophysical models that score variants by predicted disruption of three-dimensional chromatin or protein structure are increasingly proposed for clinical variant interpretation. Their discriminative performance is typically reported *marginally*, pooling variants across functional categories (missense, nonsense, promoter, intronic, …). Because both pathogenicity and structural-disruption scores correlate strongly with functional category, a marginal metric can credit a structural score for discrimination that is fully attributable to category — a confound analogous to the circularity described for missense predictors (Grimm et al., 2015).

**Results.** We evaluated a 3D chromatin structural-disruption score (ARCHCODE) on 24,238 high-confidence ClinVar variants (conflicting and uncertain classifications excluded) across nine disease-associated loci, using a category-matched stratified concordance statistic with bootstrap confidence intervals and CADD as a positive control. Marginally, the structural score separated pathogenic from benign variants (AUC = 0.754, 95% CI 0.748–0.760); however, variant category alone was more predictive (AUC = 0.827), and within-category discrimination collapsed to chance for both structural metrics (SSIM 0.507; log-SSIM 0.430, 95% CI 0.419–0.440). The collapse was systematic across 7 of 8 evaluable loci (only TP53 retained partial signal, 0.794 → 0.664). Under the identical test, the supervised control CADD retained essentially all of its signal (marginal 0.989 → within-category 0.991), demonstrating that category matching preserves genuine per-variant information and that the structural score's collapse reflects absence of signal beyond category rather than an over-conservative test.

**Conclusion.** Apparent pathogenicity signal from 3D-structural variant scores at these loci is explained by variant category, not by structure. We recommend category-matched evaluation with a positive control as a routine guard against category confounding in variant-effect prediction.

## Honest caveats (for Limitations, NOT abstract)
- 9 loci from one project's benchmark; not a genome-wide claim.
- ARCHCODE_LSSIM specifically (one structural metric); other metrics untested here.
- **Label definition (added 2026-07-04):** benchmark's raw Label column mislabels 5,330 "Conflicting" variants as
  Pathogenic and 750 no-significance as Benign. We EXCLUDE conflicting/uncertain → 24,238 high-confidence variants
  (11,858 path / 12,380 benign). Numbers here are on the clean set. Report the exclusion explicitly.
- **HBB uncomputable per-locus:** after cleaning, the HBB benchmark subset (n=353) lacks within-locus label balance,
  so its category-matched AUC is undefined; HBB variants still contribute to the pooled estimate. 8 loci evaluable per-locus.
- TP53 exception retains partial within-category signal (0.794 → 0.664) — reported, not hidden.
- Within-category AUC below 0.5 (0.430) — interpret as "no signal beyond category," NOT as anti-predictor.
- **CADD available on subset** (14,701 / 24,238); CADD's near-perfect AUC (0.99) may itself reflect ClinVar circularity
  (Grimm 2015) — this does NOT weaken its use as a positive control (it demonstrably has within-category signal).
- VEP_Score behaves near-chance (~0.51) — likely encoding of the exported column; CADD is the clean positive control.
- ClinVar labels inherit ClinVar's own category-correlated ascertainment biases.
