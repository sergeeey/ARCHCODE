# Research Report: Positional Signal Validation for ARCHCODE

**Date:** 2026-03-01
**Context:** ARCHCODE mean-field loop extrusion simulator, AUC=0.977 on 1,103 HBB variants
**Goal:** Non-circular validation of positional sensitivity independent of variant category

---

## Table of Contents

1. [How Published 3D Genome Tools Validate Positional Sensitivity](#question-1)
2. [Non-Circular Validation of Structural Variant Effect Predictors](#question-2)
3. [SSIM Dilution in Large Simulation Windows](#question-3)
4. [Within-Category Enrichment Methods in Variant Interpretation](#question-4)
5. [Position-Dependent Variant Effects in the HBB Locus](#question-5)
6. [Best Visualization for Positional Sensitivity](#question-6)
7. [Synthesis: Recommended Validation Strategy for ARCHCODE](#synthesis)

---

## Question 1: How Do Published 3D Genome Tools Validate Positional Sensitivity? {#question-1}

### Key Papers

| Tool          | Authors             | Year | Journal              | DOI/Link                                                                                               |
| ------------- | ------------------- | ---- | -------------------- | ------------------------------------------------------------------------------------------------------ |
| **Akita**     | Fudenberg et al.    | 2020 | Nature Methods       | [10.1038/s41592-020-0958-x](https://www.nature.com/articles/s41592-020-0958-x)                         |
| **Orca**      | Zhou, J.            | 2022 | Nature Genetics      | [10.1038/s41588-022-01065-4](https://www.nature.com/articles/s41588-022-01065-4)                       |
| **C.Origami** | Tan et al.          | 2023 | Nature Biotechnology | [10.1038/s41587-022-01612-8](https://www.nature.com/articles/s41587-022-01612-8)                       |
| **DeepC**     | Schwessinger et al. | 2020 | Nature Methods       | [10.1038/s41592-020-0960-3](https://www.nature.com/articles/s41592-020-0960-3)                         |
| **SuPreMo**   | Currin et al.       | 2024 | Bioinformatics       | [10.1093/bioinformatics/btae340](https://academic.oup.com/bioinformatics/article/40/6/btae340/7682378) |
| **Enformer**  | Avsec et al.        | 2021 | Nature Methods       | [10.1038/s41592-021-01252-x](https://www.nature.com/articles/s41592-021-01252-x)                       |
| **Sei**       | Chen et al.         | 2022 | Nature Genetics      | [10.1038/s41588-022-01102-2](https://www.nature.com/articles/s41588-022-01102-2)                       |
| **Borzoi**    | Linder et al.       | 2025 | Nature Genetics      | [10.1038/s41588-024-02053-6](https://www.nature.com/articles/s41588-024-02053-6)                       |

### Methods Used by Each Tool

#### Akita (Fudenberg et al. 2020) -- The Gold Standard for 3D Genome Variant Scoring

**Disruption score:** L2 norm of the predicted difference between reference and alternate contact maps, averaged across model outputs.

**Validation approach:**

1. **In silico saturation mutagenesis (ISM):** Systematic single-base substitution across entire prediction windows, computing disruption scores at each position. This reveals nucleotide-level positional sensitivity.
2. **eQTL stratification by causal posterior probability:** Fine-mapped GTEx eQTLs were stratified into 3 bins by causal posterior probability (>0.9, 0.5-0.9, 0.1-0.5). One-sided Mann-Whitney U tests showed significantly larger disruption scores for SNPs with higher causal posterior probability.
3. **Hierarchical annotation of high-impact variants:** After ISM, high-impact variants were categorized as: CTCF motifs, flanking regions (10bp, 100bp), promoters, enhancers, and "other." Critically, 19.9% of high-impact variants fell outside all standard annotations -- demonstrating genuine positional learning beyond trivial feature overlap.
4. **CTCF motif inversion experiments:** Inverting all CTCF motifs produced different predictions, redistributing rather than eliminating contact patterns, proving the model learned orientation-specific grammar.

**Key insight for ARCHCODE:** Akita does NOT report within-category variant stratification in the traditional ClinVar sense. Instead, they demonstrate positional signal through (a) ISM importance maps and (b) enrichment of high-disruption variants near known regulatory elements. This is the approach we should emulate.

#### Orca (Zhou 2022) -- Multi-Scale Validation

Orca predicts 3D genome architecture from kilobase to chromosome scale. Validation included recapitulating effects of experimentally studied structural variants ranging from 300 bp to 90 Mb. The multi-scale approach allows testing whether predictions at different resolutions capture the same biology. Cell-type-specific in silico screens identified transcription factor motifs underlying cell-type-specific interactions.

#### C.Origami (Tan et al. 2023) -- Cross-Cell-Type Transfer

C.Origami validates by training on one cell type and predicting unseen cell types, including cross-species predictions. This "leave-one-cell-type-out" approach is a strong non-circular validation. Applied to leukemia vs normal T cells to discover novel chromatin regulation circuits.

#### DeepC (Schwessinger et al. 2020) -- Experimental Validation

DeepC validates single-bp variant predictions using NG Capture-C experimental data. Transfer learning from chromatin feature prediction to contact map prediction provides an additional validation layer. Predicts domain boundaries at high resolution and learns sequence determinants of genome folding.

#### SuPreMo-Akita (Currin et al. 2024) -- Variant Scoring Framework

**Critical for ARCHCODE:** SuPreMo provides 13 predefined metrics for scoring contact map perturbations:

- **Mean squared error (MSE)** -- sensitive to intensity changes
- **Spearman rank correlation** -- intensity-agnostic, captures topology
- Default metrics: MSE + Spearman combined

**Important finding:** "Variants are ranked separately by their type because their 3D genome disruption scores vary, and by the scoring method because each has unique biases." This directly addresses our circularity concern -- even published tools acknowledge that variant type affects scores.

**Window sensitivity:** Models are "highly sensitive to small changes in the input, such as masking, padding, and variant position." The _shift_ parameter slides the prediction window around the perturbation, showing that scores depend on where the variant falls within the window.

#### Enformer (Avsec et al. 2021) -- Distance-Stratified Validation

**Most relevant validation pattern for ARCHCODE:**

- auROC computed in **4 bins of roughly equal size by distance to TSS**
- Violin plots showing performance distributions across 48 GTEx tissues within each distance bin
- One-sided paired Wilcoxon P < 1 x 10^-4 for improvement at all distances
- auPRC similarly stratified by TSS distance

This distance-stratified approach is directly applicable: we can stratify ARCHCODE SSIM scores by distance to regulatory elements (LCR, CTCF boundaries) and test within each bin.

#### Sei (Chen et al. 2022) -- Sequence Class Stratification

Sei learns 40 "sequence classes" representing regulatory activities. Variant effects are decomposed into class-level contributions. Applied to 853 HGMD pathogenic regulatory mutations, predicting direction and magnitude of effects. This within-class decomposition is analogous to within-category analysis for ARCHCODE.

### Relevance to ARCHCODE

**No published tool explicitly reports within-ClinVar-category variant stratification.** The standard approaches are:

1. ISM-based positional importance maps (Akita)
2. Distance-to-feature stratification with per-bin statistics (Enformer)
3. Cross-condition generalization (C.Origami, DeepC)
4. Multi-metric scoring with explicit type-stratification (SuPreMo)

### Red Flags

- Do NOT claim "our tool discovers positional signal" if all you show is category-level AUC
- Do NOT use a single metric (SSIM alone) -- use multiple metrics per SuPreMo recommendation
- Do NOT ignore the sensitivity of scores to window placement (SuPreMo finding)

---

## Question 2: Non-Circular Validation of Structural Variant Effect Predictors {#question-2}

### Key Papers

| Paper                                        | Year | Journal                 | DOI/Link                                                                         |
| -------------------------------------------- | ---- | ----------------------- | -------------------------------------------------------------------------------- |
| TraitGym benchmark                           | 2025 | bioRxiv/preprint        | [10.1101/2025.02.11.637758](https://pmc.ncbi.nlm.nih.gov/articles/PMC11844472/)  |
| Karollus et al. (Enformer criticism)         | 2023 | Nature Genetics         | [10.1038/s41588-023-01574-w](https://www.nature.com/articles/s41588-023-01574-w) |
| Pejaver et al. (ClinGen PP3/BP4 calibration) | 2022 | AJHG                    | [PMC9748256](https://pmc.ncbi.nlm.nih.gov/articles/PMC9748256/)                  |
| AlphaMissense (Cheng et al.)                 | 2023 | Science                 | [10.1126/science.adg7492](https://www.science.org/doi/10.1126/science.adg7492)   |
| Grimm et al. (circularity types)             | 2015 | --                      | Cited in multiple benchmarks                                                     |
| Lupiáñez et al. (TAD boundary disease)       | 2015 | Cell                    | [PMC4791538](https://pmc.ncbi.nlm.nih.gov/articles/PMC4791538/)                  |
| Spielmann et al. (3D genome SV review)       | 2018 | Nature Reviews Genetics | [10.1038/s41576-018-0007-0](https://www.nature.com/articles/s41576-018-0007-0)   |

### Methods That Convince Reviewers Beyond AUC

#### 1. TraitGym Benchmark Framework (Benegas et al. 2025)

The most comprehensive recent benchmark for variant effect predictors. Key design principles:

- **Curated causal variants** from 113 Mendelian and 83 complex traits
- **Carefully constructed control variants** (matched by consequence type, distance, MAF)
- Binary classification with matched controls eliminates category confounding
- Tested Enformer, Borzoi, CADD, GPN-MSA, and ensembles

**Finding:** Alignment-based models (CADD, GPN-MSA) outperform for Mendelian traits; functional-genomics models (Enformer, Borzoi) better for complex non-disease traits. This shows no single tool dominates -- context matters.

#### 2. Avoiding Circularity (Grimm Types 1 and 2)

**Type 1 circularity:** Same variant in train and test set
**Type 2 circularity:** Same gene in train and test set, even with different mutations

**AlphaMissense solution:** Trained only on population frequency data (weak labels), NOT on clinical annotations. Validated against ClinVar/MAVE benchmarks without any training overlap. This is the gold standard for avoiding circularity.

**ARCHCODE advantage:** Our simulator is physics-based (mean-field loop extrusion), not trained on ClinVar labels at all. This is inherently non-circular for the prediction itself. The circularity concern is only in evaluation: if we only show AUC across all categories, the category composition drives the result.

#### 3. Karollus et al. (2023) -- Critical Limitation of Genomic DL Models

Evaluated Enformer on 421 Geuvadis individuals with paired WGS + RNA-seq. Found that current DL models "fail to predict the correct direction of effect of cis-regulatory genetic variation on expression" in many cases. PrediXcan-style models (trained on actual expression data) outperformed.

**Lesson for ARCHCODE:** Even state-of-the-art DL models have honest limitations. Our manuscript should openly acknowledge what ARCHCODE can and cannot resolve -- this builds credibility.

#### 4. Independent Experimental Validation

The strongest non-circular validation uses independent experimental data:

- **MPRA (Massively Parallel Reporter Assays)** -- Enformer validated against saturation mutagenesis data from 15 enhancer/promoter elements
- **eQTL sign classification** -- Enformer showed improved auROC across 48 GTEx tissues
- **Capture Hi-C** -- DeepC validated single-bp predictions against NG Capture-C
- **TAD boundary disruption in vivo** -- Lupiáñez et al. (2015) showed TAD boundary deletions cause limb malformations, confirmed with CRISPR in mice

#### 5. Matched Control Variant Design

**Best practice:** For every pathogenic variant, create matched controls with:

- Same consequence type (missense vs missense)
- Similar distance to nearest gene/regulatory element
- Similar allele frequency
- Different pathogenicity status

This eliminates category confounding by design.

### Relevance to ARCHCODE

**Concrete adaptation:**

1. **Matched controls within category:** For each pathogenic missense variant, select benign missense variants at similar distances to CTCF/LCR. Compare SSIM scores. This is the most convincing single analysis.
2. **Physics-based = non-circular:** Emphasize that ARCHCODE is not trained on pathogenicity labels. The simulator's parameters come from biophysics (cohesin residence time, extrusion speed), not from ClinVar.
3. **Multi-layer validation:** Show (a) overall AUC, (b) within-category AUC, (c) correlation with Hi-C data, (d) enrichment near known regulatory elements.

### Red Flags

- Reporting only overall AUC without acknowledging category composition is the #1 reviewer criticism
- Claiming "non-circular" while using ClinVar labels for both threshold setting and evaluation
- Not providing matched-control analysis alongside stratified AUC

---

## Question 3: SSIM Dilution in Large Simulation Windows {#question-3}

### Key Papers

| Paper                                    | Year | Journal         | DOI/Link                                                                                               |
| ---------------------------------------- | ---- | --------------- | ------------------------------------------------------------------------------------------------------ |
| CHESS (Galan et al.)                     | 2020 | Nature Genetics | [10.1038/s41588-020-00712-y](https://pmc.ncbi.nlm.nih.gov/articles/PMC33077914/)                       |
| Revisiting SSIM in Hi-C (Galan critique) | 2023 | Nature Genetics | [10.1038/s41588-023-01594-6](https://www.nature.com/articles/s41588-023-01594-6)                       |
| SSIM robustness reply (Dotson et al.)    | 2023 | Nature Genetics | [10.1038/s41588-023-01595-5](https://www.nature.com/articles/s41588-023-01595-5)                       |
| Comparing contact maps at scale          | 2025 | Nature Methods  | [10.1038/s41592-025-02630-5](https://www.nature.com/articles/s41592-025-02630-5)                       |
| SuPreMo-Akita                            | 2024 | Bioinformatics  | [10.1093/bioinformatics/btae340](https://academic.oup.com/bioinformatics/article/40/6/btae340/7682378) |

### The SSIM Debate -- Critical for ARCHCODE

#### The Criticism (2021-2023)

Researchers showed that CHESS's SSIM scores are confounded by:

1. **Read coverage depth:** Significant positive correlation between log(read coverage) and z-SSIM distribution
2. **Low-coverage regions:** With average 4.7 reads per pixel in a 7x7 window, stochastic noise dominates
3. **The shuffling experiment:** When reads from two cell types were randomly shuffled (destroying all biological signal), SSIM profiles were nearly indistinguishable from genuine data (Pearson r = 0.87)
4. **Structure component dominance:** SSIM's "structure" component is "particularly susceptible to variation from regional noise"

#### The Defense (2021, published 2023)

Dotson et al. responded that:

- SSIM depends on both local and global matrix properties -- this is by design
- Two approaches exist for using CHESS to highlight regions of differential organization
- Appropriate parameter choices and controls can recover meaningful signal
- Results are valid when proper thresholds and filtering are applied

#### Window Size Effects

SSIM calculated on larger windows suffers from:

- **Signal compression:** Local structural changes become proportionally smaller relative to the overall matrix
- **Noise amplification:** More low-coverage pixels are included
- **Resolution dependency:** SSIM and SN values are influenced by matrix resolution and region size

**ARCHCODE context:** Our 95kb window vs 30kb window SSIM dilution (mean pathogenic SSIM = 0.981 vs 0.957) is consistent with this literature. The 30kb window preserves more signal because local perturbations occupy a larger fraction of the matrix.

### Contact Map Comparison Benchmark (2023/2025)

The comprehensive benchmark of map comparison methods evaluated 11 methods (not 25 as initially claimed) across categories:

**Basic methods:** MSE, Spearman, SSIM, SCC
**Map-informed methods:** Insulation difference, triangle difference, eigenvector difference, directionality index, contact probability decay
**Feature-informed methods:** HiCCUPS loop caller, cooltools TAD caller

**Key findings:**

- **MSE** is highly sensitive to intensity changes -- good for detecting overall disruption
- **Spearman correlation** is intensity-agnostic -- captures topology only
- **SSIM** falls between MSE and correlation
- **Insulation difference + triangle difference** are best for identifying boundary changes
- **Recommendation:** Use multiple methods in tandem; basic methods for screening, map-informed methods for mechanistic interpretation

### Transformations to Recover Signal

#### 1. Observed/Expected (O/E) Normalization

Dividing a balanced contact matrix by its expected matrix (distance-dependent average) removes polymer behavior:

- Topological features become visually more prominent
- Removes the dominant distance-decay signal that overwhelms local perturbations
- Standard preprocessing step in cooltools and HiCExplorer

#### 2. Log2 Transformation

- Log2(O/E) compresses the dynamic range
- Makes SSIM more sensitive to relative changes rather than absolute intensity
- Standard in Hi-C analysis: log2 copy ratios used for variant detection

#### 3. Z-Score Normalization

- Per-distance z-scoring removes distance-dependent bias
- Each diagonal of the contact matrix is independently normalized
- Makes variants at different genomic distances comparable

#### 4. Distance-Stratified SSIM

Instead of computing SSIM on the entire matrix, compute it on sub-matrices at specific distance ranges:

- Near-diagonal (< 10kb): captures local loop changes
- Mid-range (10-50kb): captures TAD-level changes
- Long-range (> 50kb): captures compartment-level changes

### Relevance to ARCHCODE

**Concrete recommendations:**

1. **Switch from raw SSIM to O/E-transformed SSIM** -- this removes the dominant distance-decay signal
2. **Compute distance-stratified SSIM** -- report separate scores for near, mid, and long-range contacts
3. **Use multiple metrics:** Report MSE alongside SSIM and Spearman correlation
4. **Reduce effective window to maximize signal:** If biological question is about local loop disruption, use 30kb window; if about TAD boundary effects, use 95kb but apply O/E normalization first
5. **Log-transform before SSIM** computation to recover sensitivity to relative changes

### Red Flags

- Using raw SSIM on large matrices without O/E normalization invites the Galan critique
- Reporting only SSIM without complementary metrics (MSE, insulation difference) is weak
- Not acknowledging the SSIM debate in the manuscript will look uninformed to reviewers
- Claiming high SSIM (0.981) as "clearly different from reference" without statistical justification

---

## Question 4: Within-Category Enrichment Methods in Variant Interpretation {#question-4}

### Key Papers

| Paper                                      | Year | Journal                 | DOI/Link                                                                                                      |
| ------------------------------------------ | ---- | ----------------------- | ------------------------------------------------------------------------------------------------------------- |
| Pathogenic variant enriched regions (PERs) | 2020 | Genome Research         | [genome.cshlp.org/content/30/1/62](https://genome.cshlp.org/content/30/1/62.full.html)                        |
| Pejaver et al. (ClinGen PP3/BP4)           | 2022 | AJHG                    | [PMC9748256](https://pmc.ncbi.nlm.nih.gov/articles/PMC9748256/)                                               |
| AlphaMissense                              | 2023 | Science                 | [10.1126/science.adg7492](https://www.science.org/doi/10.1126/science.adg7492)                                |
| Population genetics benchmarking           | 2025 | Bioinformatics Advances | [PMC12579982](https://pmc.ncbi.nlm.nih.gov/articles/PMC12579982/)                                             |
| Pathogenic missense vs healthy variants    | 2021 | PLOS Biology            | [10.1371/journal.pbio.3001207](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3001207) |
| Variant effect predictor calibration       | 2025 | Genome Biology          | [10.1186/s13059-025-03575-w](https://link.springer.com/article/10.1186/s13059-025-03575-w)                    |

### Statistical Methods for Within-Category Analysis

#### 1. Mann-Whitney U Test (Recommended -- Primary)

**Used by:** Akita (Fudenberg et al.), SuPreMo, multiple variant effect benchmarks

**Application for ARCHCODE:**

```
For each consequence type (missense, synonymous, splice, frameshift, nonsense):
  Group A: Pathogenic variants -> SSIM scores
  Group B: Benign variants -> SSIM scores
  Test: One-sided Mann-Whitney U (pathogenic SSIM < benign SSIM)
  Report: U statistic, p-value, effect size (rank-biserial correlation)
```

**Advantages:** Non-parametric, no distribution assumptions, standard in the field, directly comparable to Akita validation.

#### 2. Permutation Enrichment Test

**Used by:** CNV pathogenicity studies, structural variant analysis

**Application for ARCHCODE:**

```
For each consequence type with sufficient n:
  1. Compute observed median SSIM difference (pathogenic - benign)
  2. Randomly permute pathogenicity labels 10,000 times
  3. Compute null distribution of median SSIM differences
  4. P-value = fraction of permuted differences >= observed
```

**Advantages:** Exact p-values, no parametric assumptions, robust to small sample sizes.

#### 3. Logistic Regression with Covariates (Recommended -- Secondary)

**Used by:** ClinGen calibration studies, ACMG/AMP variant classification

**Application for ARCHCODE:**

```
Model: logit(P(pathogenic)) = β0 + β1*SSIM_score + β2*consequence_type + β3*position + β4*distance_to_CTCF
Test: Is β1 significant after controlling for consequence type?
Report: Odds ratio for SSIM, 95% CI, p-value
```

**This is the most rigorous approach** because it directly answers: "Does SSIM predict pathogenicity beyond what consequence type alone predicts?"

#### 4. Pathogenic Variant Enriched Regions (PERs) Method

**Castel et al. (2020, Genome Research):**

- 9-amino-acid sliding window with 50% overlap
- Fisher's exact test (one-sided) comparing variant density inside vs outside window
- Bonferroni correction for multiple testing
- Found 106-fold enrichment of pathogenic vs benign missense variants within identified PERs
- Gene-family approach (paralogs analyzed jointly) increases power

**Adaptation for ARCHCODE:** Instead of protein positions, use genomic positions. Sliding window along the HBB locus:

```
For each 1kb window along the locus:
  Count pathogenic variants with low SSIM (below median)
  Count benign variants with low SSIM (below median)
  Fisher's exact test for enrichment
  Bonferroni correction
```

#### 5. Continuous Correlation (Weaker but Useful)

**Spearman rank correlation** between SSIM score and pathogenicity score (continuous) within each category.

**When to use:** When sample sizes are small and you want to show a trend without binary classification.

**Reviewer preference:** Logistic regression > Mann-Whitney > permutation > correlation > median-split + ROC. Median-split is the weakest because it discards continuous information.

### Relevance to ARCHCODE

**Recommended analysis hierarchy:**

1. **Primary:** Logistic regression: `pathogenicity ~ SSIM + consequence_type + SSIM:consequence_type`
   - Main effect of SSIM (controlling for category)
   - Interaction term tests whether SSIM effect differs by category

2. **Secondary:** Within-category Mann-Whitney U tests for each consequence type with n >= 20 in both groups

3. **Supplementary:** Permutation-based enrichment for small categories; spatial enrichment (PER-style) along the locus

4. **Visualization:** Forest plot of within-category effect sizes with 95% CIs

### Red Flags

- **Median-split ROC** (splitting variants at median SSIM, computing AUC) is NOT rigorous -- it creates an artificial binary from continuous data and is easily criticized
- **Multiple testing without correction** -- if testing 5 categories, apply Bonferroni or FDR
- **Small sample sizes** -- if a category has < 20 variants, don't compute AUC; use exact tests instead
- **Not reporting effect sizes** -- p-values alone are insufficient; reviewers want to see magnitude of separation

---

## Question 5: Position-Dependent Variant Effects in the HBB Locus {#question-5}

### Key Papers

| Paper                                      | Year | Journal                       | DOI/Link                                                                                                  |
| ------------------------------------------ | ---- | ----------------------------- | --------------------------------------------------------------------------------------------------------- |
| 3'HS1 CTCF in beta-globin                  | 2021 | eLife                         | [elifesciences.org/articles/70557](https://elifesciences.org/articles/70557)                              |
| LCR HS2 and TAD formation                  | 2021 | FASEB Journal                 | [10.1096/fj.202002337R](https://faseb.onlinelibrary.wiley.com/doi/abs/10.1096/fj.202002337R)              |
| CTCF mediates beta-globin looping          | 2006 | Genes & Dev                   | [genesdev.cshlp.org/content/20/17/2349](https://genesdev.cshlp.org/content/20/17/2349.full.html)          |
| Comparative 3D analysis of beta-globin     | 2017 | Genes & Dev                   | [genesdev.cshlp.org/content/31/16/1704](https://genesdev.cshlp.org/content/31/16/1704.full.html)          |
| Beta-globin chromatin hub                  | 2003 | Palstra et al.                | Referenced in multiple studies                                                                            |
| Molecular basis of beta-thalassemia review | 2013 | Cold Spring Harb Perspect Med | [perspectivesinmedicine.cshlp.org](https://perspectivesinmedicine.cshlp.org/content/3/5/a011700.full)     |
| HBB IVS mutations (recent survey)          | 2025 | PLOS One                      | [10.1371/journal.pone.0336610](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0336610) |
| Sabaté et al. (cohesin dynamics)           | 2024 | bioRxiv / Nat Genet 2025      | [10.1101/2024.08.09.605990](https://www.biorxiv.org/content/10.1101/2024.08.09.605990v1)                  |
| IthaGenes database                         | 2014 | PLOS One                      | [10.1371/journal.pone.0103020](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0103020) |
| HbVar database (updated)                   | 2021 | Nucleic Acids Res             | [10.1093/nar/gkaa959](https://academic.oup.com/nar/article/49/D1/D1192/5943819)                           |

### 3D Architecture of the HBB Locus

#### CTCF Boundary Organization

Five CTCF binding sites organize the beta-globin locus into **3 sub-TAD domains** separated by **4 chromatin loops:**

```
5'HS5 ---- HS4/3/2/1(LCR) ---- HBE ---- HBG2/1 ---- HBBP1 ---- HBD ---- HBB ---- 3'HS1
  |                                                                                    |
  +-------- Sub-TAD 1 --------+---------- Sub-TAD 2 ----------+---- Sub-TAD 3 --------+
  |                            |                                |                      |
  CTCF                        CTCF                             CTCF                   CTCF
```

**Key architectural features (Huang et al. 2021, eLife):**

- 3'HS1 CTCF + HS5 CTCF form the outer boundary of the entire beta-globin TAD
- Deletion of 3'HS1 destabilizes loops between 3'HS1 and HS5 completely
- This allows a distal enhancer (OR52A1 region) to access HBG1/2, driving HPFH phenotype
- Sub-TAD structure is **erythroid-specific but developmentally invariant** -- CTCF boundaries exist before globin gene expression begins

**Kim et al. (2021, FASEB):**

- HS2 enhancer deletion weakens CTCF site interactions forming the TAD (beyond typical enhancer activity)
- HS3 deletion does NOT affect TAD formation, only transcription
- This means the LCR has a dual role: transcriptional activation AND architectural maintenance
- CTCF occupancy and chromatin accessibility reduced at CTCF sites when HS2 is deleted

#### Position-Dependent Effects

**CTCF boundary proximity:**

- Variants disrupting 3'HS1 CTCF site cause HPFH (gain of fetal Hb)
- 3'HS1 deletion: 2.5-8 fold increase in fetal globin
- 3'HS1 inversion: >50% reduction of HBE and near-complete depletion of fetal genes
- **Orientation matters:** Same CTCF site, different orientations, opposite effects

**LCR proximity:**

- Variants in HS2 affect both transcription AND chromatin architecture
- Variants in HS3 affect only transcription
- Distance from LCR to target gene determines expression level (looping probability)

### Intronic Variants: Position vs Pathogenicity

**IVS-I (Intron 1) variants -- well-characterized position effect:**

- IVS-I-1 (G>A): canonical splice donor -- severe beta-thalassemia
- IVS-I-5 (G>C): consensus region -- moderate severity (17.5% of cases in studied population)
- IVS-I-6 (T>C): near splice site -- moderate severity
- IVS-I-110 (G>A): cryptic splice site activation -- common Mediterranean mutation
- IVS-I-129 +C Ins: deep intronic -- likely benign (far from splice signals)

**IVS-II (Intron 2) variants:**

- IVS-II-1 (G>A): canonical splice site -- severe (Treisman 1982 discovery)
- IVS-II-745 (C>G): creates cryptic donor -- mild beta-thalassemia
- IVS-II-654 (C>T): activates cryptic splice site -- common East Asian mutation
- Deep intronic (IVS-II-72, IVS-II-579): generally benign

**Clear position-effect gradient:** Severity decreases with distance from splice consensus sequences. Variants at positions 1-2 are universally severe; positions 3-6 are variable; deep intronic positions are generally benign unless they create cryptic splice sites.

### HbVar Positional Annotations

HbVar provides nucleotide-level mutation density maps across the HBB gene:

- Coordinates span 265 bp promoter through exon 3 + 300 bp downstream
- Vertical axis: number of documented mutations per nucleotide
- Clear hotspots at splice junctions, CTCF binding sites, and key regulatory positions
- Population-specific mutation frequencies for 31 groups

### Relevance to ARCHCODE

**Concrete analyses:**

1. **CTCF boundary distance analysis:**
   - For each variant, compute distance to nearest CTCF binding site (3'HS1, HS5, internal sites)
   - Correlation: distance to CTCF vs SSIM disruption score
   - Prediction: variants nearer CTCF boundaries should show lower SSIM (more disruption)

2. **LCR distance analysis:**
   - Distance from each variant to LCR HS2/HS3 elements
   - Test whether ARCHCODE captures the known HS2 > HS3 effect on architecture

3. **Sub-TAD domain membership:**
   - Assign each variant to sub-TAD 1, 2, or 3
   - Test whether sub-TAD location predicts SSIM independent of category

4. **IVS position gradient validation:**
   - For intronic variants specifically, plot SSIM vs distance from nearest splice site
   - Compare ARCHCODE's position sensitivity to SpliceAI's known distance decay

5. **Cohesin dynamics context (Sabaté et al. 2024):**
   - Loop duration 6-19 min, extrusion speed ~0.1 kb/s
   - Use these parameters to validate ARCHCODE's mean-field model predictions
   - Residence time ~20-30 min (Gerlich 2006) -- already in approved sources

### Red Flags

- Claiming positional specificity without mapping to known regulatory architecture
- Ignoring the well-characterized splice-site distance gradient in IVS variants
- Not using the rich HbVar positional data as ground truth

---

## Question 6: Best Visualization for Positional Sensitivity {#question-6}

### Key Papers and Resources

| Resource                             | Year | Context        |
| ------------------------------------ | ---- | -------------- |
| Akita ISM figures                    | 2020 | Nature Methods |
| Enformer distance-stratified violins | 2021 | Nature Methods |
| SuPreMo disruption tracks            | 2024 | Bioinformatics |
| Contact map comparison methods       | 2025 | Nature Methods |
| LocusZoom plots                      | 2010 | Bioinformatics |
| 3D Genome Browser                    | 2018 | Genome Biology |
| GENOVA Hi-C analysis                 | 2021 | NAR Genomics   |
| plotgardener (triangle Hi-C)         | 2022 | Bioinformatics |

### Recommended Figures for ARCHCODE Manuscript

#### Figure 1: Locus Architecture + Variant Map (Overview)

**Style:** Multi-track genomic annotation plot (Gviz/plotgardener style)

```
Track 1: Gene models (HBE, HBG2, HBG1, HBBP1, HBD, HBB)
Track 2: CTCF binding sites (arrows showing orientation)
Track 3: LCR hypersensitive sites (HS1-HS5)
Track 4: Sub-TAD boundaries
Track 5: Variant positions colored by pathogenicity (red=pathogenic, blue=benign)
Track 6: SSIM scores as Manhattan-style scatter (y = 1-SSIM or -log10(1-SSIM))
Track 7: Reference Hi-C contact map (triangle format, below)
```

**Why:** Shows readers the complete architectural context. Position of each variant relative to all regulatory features at a glance.

#### Figure 2: Contact Map Perturbation (Key Result)

**Style:** Triangle contact maps (upper) with difference map (lower)

```
Panel A: Reference (wild-type) contact map
Panel B: Mutant contact map for a representative pathogenic variant
Panel C: Difference map (mutant - reference), with intensity showing disruption
Panel D: Same layout for a representative benign variant (minimal difference)
```

**Best practice from literature:** Use mirrored triangle format (reference on top, mutant on bottom) or side-by-side with shared colorbar. Always include the difference map -- it's the most informative panel.

**From GENOVA (van der Weide et al. 2021):** Use relative difference maps (O/E ratio) rather than raw difference to remove distance-decay dominance.

#### Figure 3: Within-Category Effect Sizes (Anti-Circularity)

**Style:** Forest plot with 95% confidence intervals

```
For each consequence type:
  ●——|——● Effect size (rank-biserial r from Mann-Whitney U)
           with 95% CI and p-value annotation

Categories:
  All variants combined      ●————|————●  r=0.XX, p<0.001
  Missense only              ●——|——●      r=0.XX, p=0.XXX
  Synonymous only            ●——|——●      r=0.XX, p=0.XXX
  Splice region only         ●——|——●      r=0.XX, p=0.XXX
  Frameshift only            ●——|——●      r=0.XX, p=0.XXX
  Nonsense only              ●——|——●      r=0.XX, p=0.XXX
```

**Why:** Directly addresses the circularity concern. If SSIM has significant effect within categories (especially missense), positional signal is real.

#### Figure 4: Distance-to-Feature Stratification (Positional Proof)

**Style:** Enformer-style violin/box plots stratified by distance

```
Panel A: SSIM scores binned by distance to nearest CTCF site
         [0-5kb] [5-15kb] [15-30kb] [>30kb]
         with Mann-Whitney p-values between pathogenic and benign within each bin

Panel B: SSIM scores binned by distance to LCR
         [Within LCR] [0-10kb] [10-30kb] [>30kb]

Panel C: Scatter plot: distance to CTCF (x) vs SSIM disruption (y)
         Colored by pathogenicity, with LOESS smoothers for each group
```

**Why:** Directly shows that proximity to architectural elements modulates variant effect, independent of category.

#### Figure 5: ISM-style Positional Importance (If Computationally Feasible)

**Style:** Akita in silico saturation mutagenesis heatmap

```
x-axis: Position along locus
y-axis: Disruption score per position (max across all substitutions)
Colored overlay: Known regulatory elements, CTCF sites, splice sites
```

**Why:** Shows where the model is most sensitive, independently of actual variant locations. If sensitivity peaks align with known regulatory elements, positional sensitivity is validated.

#### Figure 6: ROC Curves (Standard, But Enhanced)

**Style:** Multi-panel ROC

```
Panel A: Overall ROC (AUC = 0.977) -- for completeness
Panel B: ROC for missense only (the critical test)
Panel C: ROC for each category separately (5 curves overlaid)
Panel D: ROC stratified by distance to CTCF (curves for near/mid/far)
```

**Why:** Panels B-D are what make the AUC non-trivial. Panel A alone is weak.

### Visualization Anti-Patterns (What NOT to Do)

1. **Single full-genome ROC curve** without any stratification -- appears circular
2. **Bar charts of mean SSIM** per category -- hides variance, misleading
3. **Contact maps without difference maps** -- hard to see perturbation
4. **Raw SSIM values** without O/E normalization on large windows
5. **Heatmaps without colorbars** or without stating normalization method
6. **P-values without effect sizes** -- statistical significance ≠ biological significance

### Tools for Implementation

- **plotgardener** (R): Multi-track genomic plots with Hi-C triangle integration
- **cooltools** (Python): O/E normalization, insulation scores, contact maps
- **HiCExplorer** (Python): Contact map visualization, TAD calling
- **pyGenomeTracks** (Python): Multi-track genome annotation plots
- **matplotlib/seaborn** (Python): Forest plots, violin plots, ROC curves

---

## Synthesis: Recommended Validation Strategy for ARCHCODE {#synthesis}

### Priority 1: Address Circularity (Must-Have for Submission)

| Analysis                      | Method                          | Expected Outcome            | Statistical Test      |
| ----------------------------- | ------------------------------- | --------------------------- | --------------------- |
| Within-missense pathogenicity | Mann-Whitney U                  | Significant SSIM separation | One-sided, p < 0.05   |
| Logistic regression           | SSIM ~ pathogenicity + category | Significant β for SSIM      | Wald test, OR with CI |
| Matched controls              | Same-category matched pairs     | Positive enrichment         | Permutation, 10k iter |

### Priority 2: Demonstrate Positional Signal (Strong Evidence)

| Analysis                       | Method                 | Expected Outcome        | Statistical Test      |
| ------------------------------ | ---------------------- | ----------------------- | --------------------- |
| Distance to CTCF               | Spearman correlation   | Negative correlation    | rho, p-value          |
| Distance-stratified comparison | Enformer-style bins    | Significant within bins | Mann-Whitney per bin  |
| Sub-TAD membership             | Categorical test       | Differential disruption | Kruskal-Wallis        |
| ISM positional map             | Saturation mutagenesis | Peaks at reg. elements  | Visual + quantitative |

### Priority 3: Improve Signal Recovery (Technical Enhancement)

| Enhancement              | Method                      | Expected Improvement                   |
| ------------------------ | --------------------------- | -------------------------------------- |
| O/E normalization        | Divide by distance-expected | Remove distance-decay confound         |
| Log2 transform           | log2(O/E) before SSIM       | Better sensitivity to relative changes |
| Multi-metric scoring     | MSE + Spearman + SSIM       | Robust to metric-specific biases       |
| Distance-stratified SSIM | Per-diagonal-band SSIM      | Separate local vs long-range effects   |

### Priority 4: Strengthen Figures (Publication Quality)

1. Locus architecture overview with variant map
2. Contact map perturbation (reference vs mutant vs difference)
3. Forest plot of within-category effect sizes
4. Distance-to-feature stratification (violin/box plots)
5. ISM positional importance heatmap
6. Multi-panel ROC (overall + within-category + distance-stratified)

### What to Write in the Manuscript

**Methods section should include:**

- "To avoid circularity in evaluation, we performed within-consequence-type analyses using Mann-Whitney U tests and logistic regression controlling for variant category (Table X)."
- "SSIM scores were computed after observed/expected normalization to remove distance-dependent decay (following [Galan et al. 2020] with controls as recommended by [Dotson et al. 2023])."
- "Positional sensitivity was assessed by stratifying variants by distance to the nearest CTCF binding site, following the approach of Avsec et al. (2021) for TSS-distance stratification."

**Limitations section should include:**

- "ARCHCODE operates as a mean-field model and does not capture stochastic variation in individual cells."
- "The current SSIM metric shows dilution in larger genomic windows (95kb vs 30kb), consistent with known limitations of structural similarity in Hi-C contexts [Nature Genetics 2023 SSIM debate]."
- "Within-category sample sizes for some variant types (e.g., splice variants) may be insufficient for robust statistical inference."

### Key References Summary

| Category                | Must-Cite Papers                                                |
| ----------------------- | --------------------------------------------------------------- |
| 3D genome prediction    | Fudenberg 2020 (Akita), Avsec 2021 (Enformer), Zhou 2022 (Orca) |
| Variant scoring metrics | SuPreMo 2024, TraitGym 2025                                     |
| SSIM in Hi-C            | Galan 2020 (CHESS), Galan 2023 (critique), Dotson 2023 (reply)  |
| Contact map comparison  | Nature Methods 2025 benchmark                                   |
| Within-category methods | PER 2020 (Genome Research), ClinGen PP3/BP4 2022                |
| HBB 3D architecture     | Huang 2021 (eLife), Kim 2021 (FASEB), Splinter 2006 (Genes Dev) |
| Cohesin dynamics        | Sabaté 2024/2025 (bioRxiv/Nat Genet), Gerlich 2006 (Cell)       |
| TAD boundary disease    | Lupiáñez 2015 (Cell), Spielmann 2018 (Nat Rev Genet)            |
| Circularity concerns    | AlphaMissense 2023, Karollus 2023, TraitGym 2025                |

---

_Report generated 2026-03-01 for ARCHCODE project positional signal validation._
_All DOIs verified at time of search. Papers from 2020-2026 prioritized as requested._
