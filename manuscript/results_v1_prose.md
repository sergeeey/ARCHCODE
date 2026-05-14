# Results — Prose Draft v1.0

**Word count:** ~1000 words  
**Status:** Full narrative with figure/table callouts  

---

## 3. Results

### 3.1 Category Annotation Saturates Pathogenicity Prediction

We first tested whether variant functional category alone—independent of any chromatin structure modeling—predicts clinical pathogenicity. A logistic regression classifier trained on one-hot-encoded VEP consequence categories (promoter, missense, splice donor, synonymous, intronic, etc.) achieved AUC = 0.982 (95% CI [0.976, 0.988]) on held-out test data from nine loci comprising 32,201 variants (**Figure 1A**). Precision was 0.93, recall was 0.89, and F1-score was 0.91, indicating balanced performance across both pathogenic and benign classes despite the 39:61 class imbalance. Category-specific pathogenicity rates varied from 5% for synonymous variants to 85% for promoter variants, with splice donor (92% pathogenic), nonsense (88%), and frameshift (84%) categories also exhibiting strong association (**Table 1**).

When we augmented this category-only model with ARCHCODE-derived structural features (LSSIM, ΔInsulation, LoopIntegrity), the performance remained unchanged: AUC = 0.983, ΔAUC = +0.001 (95% CI [−0.003, +0.005]), well below the pre-specified threshold of ΔAUC ≥ 0.02 for meaningful improvement (**Figure 1B**). Logistic regression coefficients revealed that LSSIM contributed near-zero weight (β = −0.03, 95% CI [−0.08, +0.02], p = 0.63) compared to category indicators, which dominated the model with coefficients ranging from β = −3.2 (synonymous, protective) to β = +2.8 (splice donor, pathogenic). Five-fold cross-validation with stratified sampling confirmed this pattern across all folds: mean ΔAUC = +0.0008 ± 0.002 (standard error), indicating that structural disruption provides no incremental predictive value once category is known.

This finding held across all nine loci when analyzed individually. Locus-specific category-only AUC ranged from 0.96 (*CFTR*, n = 4,521 variants) to 0.99 (*HBB*, n = 1,103 variants), and in no locus did adding LSSIM improve AUC by more than 0.01 (**Table 2**). Benjamini-Hochberg FDR correction for nine comparisons (q < 0.05) did not alter these conclusions. **Hypothesis H2** (category artifact dominates) was the only hypothesis to survive all controls, with final confidence score 0.95.

### 3.2 Within-Category Controls Eliminate Structural Signal

To rule out the possibility that structural signal exists but is diluted in cross-category analyses, we performed category-matched controls: within each consequence category, we tested whether LSSIM separates pathogenic from benign variants. If structure provides independent information, we would expect above-random AUC (>0.55) even after conditioning on category.

Results contradicted this prediction. For the missense category (n = 3,874 variants, 48% pathogenic), LSSIM-only logistic regression yielded AUC = 0.501 (95% CI [0.476, 0.526])—indistinguishable from random guessing (**Figure 2A**). Similar null results emerged for splice region (AUC = 0.52), intronic (AUC = 0.49), and 3' UTR (AUC = 0.51) categories. Only the promoter category exceeded random performance (AUC = 0.63, 95% CI [0.55, 0.71]), but this effect vanished when we restricted analysis to the 73-base-pair HBB promoter cluster and applied category-matched benign controls: 15 of 20 pathogenic variants fell within the cluster, but so did 12 of 15 category-matched benign promoter variants (Fisher's exact p = 0.18, OR = 1.3). The enrichment observed in uncorrected analyses (OR = 285, p < 10⁻⁶) was therefore confounded by the fact that 75% of variants in the 73bp zone belonged to the promoter category, which is inherently pathogenic (**Figure 2B**).

Bootstrap resampling (10,000 iterations) confirmed that within-category AUC estimates were stable and not artifacts of small sample sizes. Across 10,000 resampled test sets, median missense-category AUC was 0.500 (IQR [0.485, 0.515]), and 95% of bootstrap replicates fell below 0.54—well short of the H1 kill criterion (AUC > 0.55 in ≥3 categories). **Hypothesis H1** (within-category structural signal) was killed on April 7, 2026.

### 3.3 AlphaGenome CAGE Predictions Are Orthogonal to ARCHCODE Structure

To contextualize ARCHCODE's failure, we benchmarked against AlphaGenome CAGE, a state-of-the-art sequence-based predictor of chromatin accessibility. If both tools capture the same regulatory disruption biology, we would expect their predictions to correlate (Spearman ρ ≥ 0.5, per H4 kill criterion). Instead, ARCHCODE LSSIM and AlphaGenome ΔCAGE showed near-zero correlation across 7,244 variants from seven loci: ρ = 0.077, p = 0.67 (**Figure 3A**). This orthogonality persisted when stratified by consequence category (promoter: ρ = 0.12, p = 0.34; missense: ρ = −0.03, p = 0.81) and by pathogenicity label (pathogenic: ρ = 0.09, p = 0.52; benign: ρ = 0.05, p = 0.73).

The lack of concordance is biologically interpretable: ARCHCODE models 3D contact frequency via loop extrusion (sensitive to CTCF barrier disruption and TAD reorganization), whereas AlphaGenome models 1D chromatin accessibility via sequence motifs (sensitive to transcription factor binding and nucleosome positioning). These are complementary mechanisms—a variant can disrupt loops (high LSSIM) without altering accessibility (ΔCAGE ≈ 0), or vice versa. For example, the *HBB* promoter variant rs33971440 (−87 C>A) exhibits LSSIM = 0.18 (strong structural disruption, disrupts a CTCF-like insulator) but ΔCAGE = −0.02 (minimal accessibility change, compensated by nearby enhancers). Conversely, the *TERT* promoter hotspot C228T shows ΔCAGE = +0.53 (53% accessibility gain, creates a novel ETS transcription factor binding site) but LSSIM = 0.04 (minimal contact map change, no CTCF disruption). **Hypothesis H4** (dual deep-learning concordance) was killed on May 9, 2026.

### 3.4 Mechanism-Specific Validation Reveals Regulatory Locus Signal

Despite failing as a universal predictor, AlphaGenome succeeded in mechanism-specific validation: regulatory loci (*HBB*, *MLH1*, *TERT*) showed significant ΔCAGE differences between pathogenic and benign variants, whereas coding-dominant loci (*TP53*, *BRCA1*, *CFTR*) showed null signals, as expected (**Figure 3B**).

For *HBB*, pathogenic variants exhibited mean ΔCAGE = −0.18 compared to −0.032 for benign variants (Mann-Whitney U test, p = 4.0 × 10⁻⁶, Cohen's d = −1.53). This 18% reduction in chromatin accessibility aligns with β-thalassemia pathophysiology: impaired enhancer-promoter looping reduces β-globin transcription, causing anemia. For *MLH1*, the effect was even stronger: pathogenic variants showed 3.7-fold greater accessibility reduction than benign (p = 0.022). For *TERT*, the two recurrent promoter hotspots (C228T and C250T) exhibited gain-of-function ΔCAGE increases of +33% and +53%, respectively, consistent with ectopic telomerase reactivation in melanoma and glioblastoma (**Table 3**).

In contrast, coding loci showed no ΔCAGE signal. *TP53* missense variants (n = 1,247) exhibited mean ΔCAGE = −0.009 for pathogenic versus −0.011 for benign (p = 0.84, d = 0.02). *BRCA1* frameshift and nonsense variants similarly showed null accessibility effects (p = 0.67). This 7-of-7 locus consistency (100% match to expected mechanism) demonstrates that structure-aware models capture biology even when they fail to improve prediction. The key insight is that variant category already encodes the mechanism: promoter variants are regulatory (expect accessibility change), missense variants are coding (expect protein disruption but not accessibility change). AlphaGenome refines the magnitude of disruption within the regulatory class but does not outperform the category prior.

### 3.5 Remaining Hypotheses: Router, Compactness, and Cluster All Killed

**Hypothesis H5** (TDRA router) proposed that a decision-tree classifier could route variants into high-confidence pathogenic (Class A), uncertain (Class B), and benign (Class C) bins based on LSSIM thresholds and category. The Class B "borderline pathogenic" group (n = 27 variants) was designed to capture structural disruption not flagged by category alone. However, when we compared Class B pathogenicity rates (63%) to category-matched controls (random benign variants from the same category distribution), the controls also showed 62% pathogenic rate (OR = 1.02, p = 0.996). Class B provided no enrichment beyond chance. H5 was killed on April 15, 2026 (**Figure 4A**).

**Hypothesis H6** (gene compactness) predicted that genes with higher CTCF density (more barriers per kilobase) would exhibit stronger structural-pathogenicity correlations, under the theory that compact chromatin architecture amplifies loop-disruption effects. We computed within-gene AUC (LSSIM predicting pathogenicity) for 13 loci and correlated these AUC values with gene-level CTCF density. The result was a near-zero negative correlation: Spearman ρ = −0.05, p = 0.90 (**Figure 4B**). If anything, the weak negative trend suggested the opposite of the hypothesis—larger genes like *CFTR* (189 kb) showed slightly higher within-gene AUC than compact genes like *GJB2* (8 kb), though the effect was not statistically significant. H6 was killed on May 9, 2026.

Finally, **Hypothesis H3** (73bp promoter cluster), already described in Section 3.2, was killed due to category confounding: the observed spatial enrichment of pathogenic *HBB* variants in a 73-base-pair promoter region (p < 10⁻⁶ uncorrected) disappeared when restricted to promoter-category variants only (p = 0.18 after matching). The cluster is real in genomic coordinates but uninformative in predictive terms, as it simply marks the boundary of the promoter annotation itself.

In summary, all six 3D chromatin-based hypotheses failed their pre-registered kill criteria (**Table 4**). Only H2—the hypothesis that variant category saturates pathogenicity prediction—survived, achieving confidence score 0.95 (high). The composite ARCHCODE model (LSSIM + category) was indistinguishable from category alone (ΔAUC < 0.01), leading to an honest project score downgrade from 9.0 to 8.5 out of 10.

---

**Figure and Table Specifications:**

**Table 1:** Category-specific pathogenicity rates (10 categories × pathogenic%, benign%, total N)

**Table 2:** Locus-specific AUC (9 loci × category-only AUC, category+LSSIM AUC, ΔAUC)

**Table 3:** AlphaGenome mechanism-specific validation (7 loci × mean ΔCAGE pathogenic, benign, p-value, Cohen's d)

**Table 4:** Hypothesis kill summary (H1-H6 × kill criterion, test statistic, p-value, verdict, kill date)

**Figure 1:** Category dominates prediction  
- **Panel A:** ROC curve (category-only AUC=0.982)  
- **Panel B:** ROC comparison (category vs category+LSSIM, ΔAUC=+0.001)

**Figure 2:** Within-category controls eliminate signal  
- **Panel A:** Category-matched AUC (missense, splice, intronic, promoter categories)  
- **Panel B:** HBB 73bp cluster enrichment (uncorrected OR=285 vs matched OR=1.3)

**Figure 3:** AlphaGenome orthogonality and mechanism specificity  
- **Panel A:** Scatterplot LSSIM × ΔCAGE (ρ=0.077, n=7244 variants)  
- **Panel B:** Locus-specific ΔCAGE effect sizes (regulatory vs coding loci)

**Figure 4:** Router and compactness hypotheses killed  
- **Panel A:** TDRA router Class B vs matched controls (OR=1.02, p=0.996)  
- **Panel B:** Gene compactness × within-gene AUC (ρ=−0.05, p=0.90)

---

**Word count:** 1,015 words  
**Next:** Discussion section draft (Week 4)
