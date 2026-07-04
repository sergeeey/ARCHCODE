# Category-Confound Paper — Related Work (draft v1, 2026-07-04)

All citations verified real (WebSearch 2026-07-04). Preprints marked. Pull exact DOIs/pages at assembly.

## Related Work

**Computational prediction of 3D-structural variant effects.** A growing family of methods
scores genetic variants by their predicted disruption of three-dimensional genome or protein
organization. For structural variants, svMIL and svMIL2 use multiple-instance learning to
predict pathogenic TAD-boundary–disrupting somatic SVs, reporting an average AUC of 0.86 across
cancer types [Nieboer & de Ridder 2020; Nieboer et al. 2021], and POSTRE predicts SV pathomechanisms
(enhancer adoption, neo-TAD formation) from tissue-specific chromatin data [POSTRE 2025, preprint].
Sequence-to-function models such as Enformer and AlphaGenome predict chromatin contact maps and
regulatory tracks from DNA and are increasingly repurposed for variant interpretation
[AlphaGenome 2025, preprint]. The score evaluated here (ARCHCODE) belongs to this family,
quantifying variant-induced change in a simulated CTCF/cohesin contact map. Across these methods,
discriminative performance is typically reported as a single pooled (marginal) AUC over variants
of heterogeneous functional categories.

**Circularity and confounding in variant-effect evaluation.** The risk that pooled benchmarks
credit a predictor for signal it did not learn is well documented for missense predictors.
Grimm et al. showed that evaluation is hindered by two types of circularity — the same variant,
or different variants from the same protein, appearing in both training and test sets — which
inflates apparent accuracy and can even rank the most circular tool as the most accurate
[Grimm et al. 2015]. Subsequent work formalized protein-aware splits to prevent this leakage
[Heijl et al. 2020, preprint], and recent large benchmarks of 65 variant-effect predictors
explicitly pre-process datasets to reduce biases that inflate performance [Radjasandirane et al. 2025].
Our analysis concerns a distinct but related confounder: variant *functional category*
(e.g., nonsense, promoter, intronic) is simultaneously a strong predictor of pathogenicity and
strongly correlated with structural-disruption scores, so a pooled AUC can reflect category
composition rather than per-variant structural signal.

**Marginal success masking finer-grained failure.** Our finding parallels a recurring pattern in
genomic deep learning: strong marginal metrics can conceal failure on the question of interest.
Sasse et al. and Huang et al. independently reported that models excelling at population-level
expression prediction (Enformer, Basenji2, ExPecto, Xpresso) fail to predict expression differences
*across individuals*, frequently mispredicting even the direction of a variant's effect
[Sasse et al. 2023; Huang et al. 2023]; a 2025 evaluation reached similar conclusions for
AlphaGenome's personal-genome predictions while noting the difficulty of defining negative controls
[AlphaGenome 2025, preprint]. In each case the informative test is not the marginal one but a
stratified or matched comparison that isolates the claimed capability. We apply this logic to
structural pathogenicity scoring through a category-matched (stratified concordance) evaluation.

**Positive controls and stratified evaluation.** Distinguishing a real-but-weak effect from a
confounded one requires a reference the test is known to pass. We adopt CADD as a positive control:
because it retains its discrimination under category matching, any collapse of a competing score
cannot be attributed to an over-conservative test. This design also guards against the
"garden of forking paths," whereby flexible, post-hoc pooled analyses can manufacture apparent
signal [Gelman & Loken 2014]. To our knowledge, category-matched evaluation with an explicit
positive control has not been systematically applied to 3D-structural variant-effect scores.

## References (verified 2026-07-04)

- Grimm et al. 2015 — "The Evaluation of Tools Used to Predict the Impact of Missense Variants Is
  Hindered by Two Types of Circularity." Human Mutation 36(5):513-523.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4409520/ (doi:10.1002/humu.22768)
- Heijl et al. 2020 (preprint) — "Mind the gap: preventing circularity in missense variant prediction."
  bioRxiv 2020.05.06.080424. https://www.biorxiv.org/content/10.1101/2020.05.06.080424v1.full
- Radjasandirane et al. 2025 — "Insights for variant clinical interpretation based on a benchmark of 65
  variant effect predictors." Genomics. https://www.sciencedirect.com/science/article/pii/S0888754325000527
- Sasse et al. 2023 — "Benchmarking of deep neural networks for predicting personal gene expression
  from DNA sequence highlights shortcomings." Nature Genetics 55:2060-2064.
  https://www.nature.com/articles/s41588-023-01524-6 (PMC10055057)
- Huang et al. 2023 — "Personal transcriptome variation is poorly explained by current genomic deep
  learning models." Nature Genetics. https://www.nature.com/articles/s41588-023-01574-w
- svMIL / Nieboer & de Ridder 2020 — "svMIL: predicting the pathogenic effect of TAD boundary-disrupting
  somatic structural variants through multiple instance learning." Bioinformatics 36(Suppl_2):i692.
  Authors VERIFIED 2026-07-04: Marleen M. Nieboer, Jeroen de Ridder.
  https://academic.oup.com/bioinformatics/article/36/Supplement_2/i692/6055921
- Nieboer et al. 2021 — "Predicting pathogenic non-coding SVs disrupting the 3D genome in 1646 whole cancer
  genomes using multiple instance learning." Scientific Reports 11.
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8277903/
- POSTRE 2025 (preprint) — POSTRE, distinguishing benign from pathogenic duplications via 3D
  regulatory prediction. medRxiv 2025.06.27.25329768.
  https://www.medrxiv.org/content/10.1101/2025.06.27.25329768
- AlphaGenome 2025 (preprint) — "AlphaGenome Enhances Personal Gene Expression Prediction but Retains
  Key Limitations." bioRxiv 2025.08.05.668750. https://pmc.ncbi.nlm.nih.gov/articles/PMC12440111/
- Gelman & Loken 2014 — "The Statistical Crisis in Science" (garden of forking paths). American Scientist 102(6):460.

## Assembly notes
- svMIL authorship VERIFIED (Nieboer & de Ridder 2020) — earlier draft had a fabricated "Kester", corrected.
- Mind the Gap: confirm published (non-preprint) version exists; if so, cite that.
- ARCHCODE self-reference: cite the project's own preprint (Research Square rs-9090074) as the method under evaluation.
