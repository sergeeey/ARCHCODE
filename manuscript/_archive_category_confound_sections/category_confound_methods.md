# Category-Confound Paper — Methods (draft v1, 2026-07-04)

Matches `scratchpad/fig_category_confound.py` exactly. Numbers → `results/fig_category_confound_stats.json`.

## Methods

### Dataset
We used a benchmark of 30,318 ClinVar single-nucleotide and short-indel variants spanning nine
disease-associated loci (BRCA1, CFTR, GJB2, HBB, LDLR, MLH1, SCN5A, TERT, TP53), each annotated with
a functional category, a ClinVar clinical-significance term, and three variant-effect scores: the
3D chromatin structural-disruption score under evaluation (ARCHCODE log-SSIM), CADD (PHRED-scaled),
and a VEP-derived score.

### Labels and categories
Variants were assigned a binary outcome from their ClinVar clinical significance. Pathogenic =
{Pathogenic, Likely pathogenic, Pathogenic/Likely pathogenic (and its compound terms)}; Benign =
{Benign, Benign/Likely benign, Likely benign}. Variants with **conflicting classifications**
(n = 5,330) or **no reported significance** (n = 750) were **excluded** as not constituting a
high-confidence label, leaving **24,238 variants** (11,858 pathogenic, 12,380 benign). Functional
category (14 levels: missense, nonsense, frameshift, synonymous, intronic, promoter, splice_donor,
splice_acceptor, splice_region, inframe_deletion, inframe_indel, 3′/5′_UTR, other) was taken as
provided and used as the stratification variable.

### Discrimination metric
For a score *s* oriented so that larger values indicate greater predicted pathogenicity, and binary
label *y* (1 = pathogenic, 0 = benign), the marginal discrimination is the concordance (c-statistic,
equivalent to the ROC AUC):

  C = [ Σ_{i:yᵢ=1} Σ_{j:yⱼ=0} ( 𝟙[sᵢ > sⱼ] + ½·𝟙[sᵢ = sⱼ] ) ] / (n₁·n₀),

computed efficiently from mid-ranks (ties receive average ranks) via the rank-sum identity
C = (R₁ − n₁(n₁+1)/2) / (n₁·n₀), where R₁ is the summed rank of pathogenic variants. Each score was
**oriented** by flipping its sign, if necessary, so that its marginal C ≥ 0.5; the identical
orientation was then applied to the category-matched statistic, ensuring a fair comparison.

### Category-matched (stratified) concordance
To isolate signal beyond variant category we computed a stratified c-statistic that compares
pathogenic and benign variants **only within the same functional category**. For category *k* with
pathogenic set Pₖ and benign set Bₖ,

  cₖ = [ Σ_{i∈Pₖ} Σ_{j∈Bₖ} ( 𝟙[sᵢ > sⱼ] + ½·𝟙[sᵢ = sⱼ] ) ] / (|Pₖ|·|Bₖ|),

and the stratified concordance is the pair-count–weighted average over categories containing both
labels:

  C_strat = ( Σₖ |Pₖ|·|Bₖ|·cₖ ) / ( Σₖ |Pₖ|·|Bₖ| ).

C_strat is the probability that, given a pathogenic and a benign variant **of the same category**,
the score ranks them correctly; it is a stratified (conditional) Harrell's C. Weighting by the number
of comparable pairs |Pₖ|·|Bₖ| automatically down-weights near-monomorphic categories (e.g. frameshift,
almost entirely pathogenic) and gives the dominant weight to well-balanced categories.

### Positive control
CADD served as a positive control: a variant-effect predictor known to carry per-variant
pathogenicity information. Because the same stratification is applied to every score, a predictor that
retains its discrimination under category matching demonstrates that the procedure preserves genuine
per-variant signal; a score whose discrimination collapses to chance under the identical procedure
therefore lacks signal beyond category rather than being penalized by an over-conservative test.
(Note: CADD's high marginal concordance may itself be partly inflated by ClinVar circularity
(Grimm et al. 2015); this does not affect its validity as a positive control here.)

### Uncertainty and per-locus analysis
95% confidence intervals were obtained by nonparametric bootstrap: variants were resampled with
replacement B = 1,000 times and the statistic recomputed, with intervals taken as the 2.5th–97.5th
percentiles (random seed fixed at 20260704 for reproducibility). Analyses were repeated within each
locus; the HBB benchmark subset (n = 353) lacked within-locus label balance after cleaning, leaving
its stratified statistic undefined, so it was reported only in the pooled estimate (eight loci
evaluable per-locus).

### Implementation
All analyses used Python 3.11 (numpy, pandas, scipy.stats.rankdata). Code and the exact statistics
underlying every figure value are released as `fig_category_confound.py` and
`fig_category_confound_stats.json`.

## Assembly notes
- Confirm exact category level names/counts against final dataset export.
- Cross-check every reported number against fig_category_confound_stats.json before submission (integrity-checker).
- ARCHCODE method itself: cite project preprint (Research Square rs-9090074) in Dataset paragraph.
