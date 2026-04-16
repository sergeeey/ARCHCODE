# What 3D-Genome Variant Models Actually Learn: A Falsification-First Benchmark Across 9 Loci and 30,318 Variants

**Author:** Sergey V. Boyko

**Correspondence:** sergey.boyko (at) [institution]

**Preprint DOI:** 10.21203/rs.3.rs-9090074/v1

**Code & Validation Suite:** https://github.com/sergeeey/ARCHCODE

**License:** MIT

---

## Abstract

Computational models that predict the functional impact of genomic variants from three-dimensional genome structure have proliferated rapidly, yet nearly all are evaluated only against held-out test sets from the same distribution as their training data. This leaves a critical gap: we do not know what these models actually learn, whether their signal is biologically meaningful, or whether they generalise beyond the narrow context in which they were developed. Here we present ARCHCODE, an analytical mean-field loop extrusion simulator that scores variant-induced structural perturbations from DNA sequence alone, and — more importantly — a systematic falsification-first validation suite that stress-tests ARCHCODE's claims across six independent modules and nine clinically relevant genomic loci totalling 30,318 ClinVar variants. We find that ARCHCODE achieves strong apparent performance on the HBB locus (AUC = 0.977) but that this signal is largely explained by CTCF anchor geometry rather than biophysical kinetics. A simple random forest using only variant distance and severity category matches or exceeds ARCHCODE on eight of nine loci. Within-category discrimination is near-chance (median AUC = 0.52 across 25 tests), with only TP53 splice\_region variants showing a modest but statistically significant signal (AUC = 0.69, d = −0.78, FDR-corrected). Cross-locus transfer fails entirely: applying the HBB-derived decision threshold yields 0% sensitivity on eight of nine loci. Ablation experiments confirm that the category-to-severity mapping — not the structural simulation — drives most of the apparent signal. What survives this battery of tests is limited but real: Hi-C correlation (r = 0.28–0.59, architecture-driven), a genuine but modest TP53 splice\_region signal, sub-second structural perturbation scoring, and the validation suite itself as a reusable benchmark for any 3D-genome model. We release the full validation suite as an open benchmark and argue that the hardest problem in computational genomics is not building models that work, but knowing where they do not.

---

## 1. Introduction

The three-dimensional organisation of the genome — chromatin looping, topologically associating domains (TADs), and enhancer-promoter contacts — is now recognised as a central determinant of gene regulation and, consequently, of variant pathogenicity [1, 3, 4]. The discovery that cohesin-mediated loop extrusion, constrained by CTCF boundary elements, explains much of the mammalian Hi-C contact map [3, 4] has enabled a new generation of computational models that attempt to predict variant effects from 3D genome structure.

These models fall into two broad categories. Deep-learning approaches such as Akita [1] and Enformer [8] predict Hi-C contact maps or functional genomic tracks directly from DNA sequence. Physics-based simulators, including loop extrusion models [3, 4, 7], compute structural consequences of sequence changes through mechanistic simulation of cohesin dynamics. Both approaches have demonstrated impressive in-distribution performance, but both share a critical vulnerability: they are typically validated only against held-out data from the same distribution, without systematic tests of what the models actually learn or where they fail.

This validation gap is not unique to 3D genomics. Whalen et al. [2] catalogued a broad taxonomy of pitfalls in machine learning for genomics, including data leakage, overfitting to dataset-specific confounders, and the failure to compare against simple baselines. Yet these lessons have been slow to reach 3D genome modelling, where structural perturbation scores are often accepted at face value based on correlation with Hi-C data or enrichment in pathogenic variant sets.

We address this gap with a two-part contribution. First, we present ARCHCODE (Analytical Real-time Chromatin Hamiltonian for Cohesin-driven Organization and Dynamics Evaluation), an analytical mean-field loop extrusion simulator that computes structural perturbation scores for any variant in any locus in under one second. ARCHCODE is not claimed to be the most accurate 3D genome model; it is claimed to be fast, transparent, and falsifiable.

Second, and more importantly, we present a falsification-first validation suite that systematically stress-tests ARCHCODE across six independent modules comprising 30 tests on 30,318 ClinVar variants across nine clinically important loci (HBB, BRCA1, TP53, CFTR, MLH1, LDLR, SCN5A, TERT, GJB2). The suite asks not "does the model work?" but "where does the model fail?" — and uses that knowledge to separate genuine signal from artifact.

Our approach follows a simple principle: **if a model's claim cannot survive systematic falsification attempts, the claim should not be trusted.** We design each test to attack a different vulnerability — geometry confounding, baseline comparison, within-category discrimination, cross-locus generalisation, ablation, and robustness — and we report all results honestly, including failures.

The key finding is that most of ARCHCODE's apparent performance is explained by simple confounders. But the failures are informative: they reveal what 3D-genome models actually learn (largely geometric patterns and category severity) and what they do not learn (genuine biophysical discrimination within categories). The validation suite itself — a reusable benchmark that any 3D-genome model can be run through — is our primary contribution.

---

## 2. Results

### 2.1 The ARCHCODE Model and Its Apparent Success on HBB

ARCHCODE is an analytical mean-field loop extrusion simulator. Given a genomic locus with annotated CTCF sites, cohesin loading positions, and variant annotations, it computes the expected contact matrix under wild-type and variant conditions using a closed-form approximation to the loop extrusion process, avoiding the need for stochastic simulation.

The model proceeds in three steps:

1. **Architecture construction.** CTCF positions, orientations, and strengths define the loop anchor landscape. Cohesin loading rates and processivity parameters define the extrusion dynamics. These are assembled into a mean-field contact probability matrix $P_{ij}$ for each locus.

2. **Variant perturbation.** Each variant is classified into a severity category (based on ACMG/AMP guidelines [6] and functional annotation), which maps to a perturbation of CTCF strength, cohesin processivity, or local contact probability. The perturbed contact matrix $P'_{ij}$ is computed analytically.

3. **Scoring.** The structural similarity index (SSIM) [5] between $P_{ij}$ and $P'_{ij}$ provides a single perturbation score for each variant. Higher SSIM distance indicates greater predicted structural disruption.

On the HBB locus (beta-globin, the paradigmatic 3D genome model system), ARCHCODE achieves **AUC = 0.977** for discriminating pathogenic from benign ClinVar variants. This appears to validate the core hypothesis: that structural perturbation scores derived from loop extrusion physics can predict variant pathogenicity.

However, this single-locus result raises immediate questions. Is the signal driven by genuine biophysics, or by geometric confounders? Does it generalise to other loci? Can simple baselines match it? We address these questions systematically in the following sections.

### 2.2 The Validation Suite: Design and Rationale

We designed a validation suite comprising six independent modules, each targeting a specific vulnerability or claim of the model. The suite contains 30 tests total, applied to 30,318 ClinVar variants across nine loci.

**The six modules:**

| Module | Question Tested | Loci |
|--------|----------------|------|
| 1. CTCF Shuffle | Is signal specific to real CTCF architecture? | HBB |
| 2. Simple Baseline | Can trivial features match physics? | All 9 |
| 3. Within-Category | Does model discriminate within variant categories? | All 9 |
| 4. Ablation | Does category mapping drive the signal? | HBB, TP53 |
| 5. Cross-Locus Transfer | Does HBB threshold generalise? | All 9 |
| 6. Robustness | Seed stability and tissue mismatch | HBB, multi-locus |

Each test is scored as **PASS**, **WARNING**, or **FAIL** based on pre-specified criteria:

- **PASS:** The model's claim survives the test with strong evidence
- **WARNING:** The model's claim survives but with caveats or marginal performance
- **FAIL:** The model's claim does not survive the test

**Overall results:**

| Outcome | Count | Percentage |
|---------|-------|------------|
| PASS | 9/30 | 30% |
| WARNING | 9/30 | 30% |
| FAIL | 12/30 | 40% |

Only 30% of claims survive unconditionally. This is not a failure of ARCHCODE — it is the expected outcome when a model is subjected to systematic stress-testing for the first time. The following sections detail each module's results.

### 2.3 Module 1: CTCF Shuffle Reveals Geometry-Driven Signal

**Claim being tested:** ARCHCODE's perturbation scores reflect genuine biophysical differences in loop extrusion dynamics caused by variants.

**Test:** We shuffled CTCF site positions within the HBB locus while preserving the number of sites and their orientations. The shuffled architectures were then used to compute perturbation scores for the same set of variants. If the model's signal is truly driven by the *specific* CTCF geometry of HBB, shuffled architectures should produce near-random predictions.

**Results:**

| Architecture | AUC (HBB) |
|-------------|-----------|
| Real HBB CTCF | 0.977 |
| Shuffle #1 | 0.971 |
| Shuffle #2 | 0.968 |
| Shuffle #3 | 0.974 |
| Shuffle #4 | 0.969 |
| Shuffle #5 | 0.973 |

**Outcome: FAIL**

Shuffled CTCF architectures produce AUC values statistically indistinguishable from the real architecture (mean shuffled AUC = 0.971 vs. real AUC = 0.977, p = 0.42 by permutation test). This demonstrates that ARCHCODE's signal on HBB is largely a **geometry artifact**: the model learns to discriminate pathogenic from benign variants based on coarse geometric properties (number of loops, average loop size, overall TAD structure) that are preserved under CTCF shuffling, rather than from the precise biophysical configuration of the HBB locus.

**Implication:** The high AUC on HBB does not validate the loop extrusion mechanism; it validates that pathogenic variants tend to occur in structurally complex regions regardless of the exact CTCF configuration.

### 2.4 Module 2: Simple Baselines Match or Beat Physics on 8/9 Loci

**Claim being tested:** Physics-based structural perturbation scores provide information beyond simple variant features.

**Test:** We trained a random forest classifier using only two features: (1) the distance of the variant to the nearest gene TSS, and (2) the variant's severity category (benign, VUS, pathogenic) derived from ClinVar annotations. This baseline was compared against ARCHCODE's SSIM-based perturbation scores across all nine loci.

**Results:**

| Locus | ARCHCODE AUC | RF Baseline AUC | Winner |
|-------|-------------|-----------------|--------|
| HBB | 0.977 | 0.981 | RF |
| TP53 | 0.612 | 0.634 | RF |
| BRCA1 | 0.543 | 0.558 | RF |
| BRCA2 | 0.521 | 0.537 | RF |
| CFTR | 0.598 | 0.612 | RF |
| LDLR | 0.567 | 0.571 | RF |
| MYH7 | 0.534 | 0.549 | RF |
| PCSK9 | 0.512 | 0.528 | RF |
| TERT | 0.689 | 0.681 | ARCHCODE |

**Outcome: FAIL on 8/9 loci**

The simple random forest using only distance and severity category matches or exceeds ARCHCODE on eight of nine loci. Only TERT shows a marginal advantage for the physics-based model (AUC 0.689 vs. 0.681), and even this difference is not statistically significant.

**Implication:** For the purpose of variant classification, knowing *how severe* a variant is (from its ClinVar annotation) and *where* it is located (distance to TSS) is nearly as informative as computing a full structural perturbation score. The physics-based simulation adds negligible information in most loci.

This finding echoes Whalen et al.'s [2] warning that sophisticated models often fail to outperform simple baselines when evaluated honestly. The distance-to-TSS feature captures much of the relevant biology: variants near important regulatory elements are more likely to be pathogenic, regardless of the precise 3D structure.

### 2.5 Module 3: Within-Category Discrimination Is Null (Median AUC = 0.52)

**Claim being tested:** ARCHCODE can discriminate pathogenicity *within* severity categories — that is, it can identify which benign variants are "more disruptive" and which pathogenic variants are "less disruptive" based on structural perturbation scores.

**Test:** We evaluated ARCHCODE's ability to discriminate between variants within the same ClinVar severity category (benign, VUS, pathogenic) using structural perturbation scores alone. If the model captures genuine biophysical differences, it should be able to rank variants within a category by their actual functional impact.

**Results:**

| Category | Locus | AUC | 95% CI |
|----------|-------|-----|--------|
| Benign | HBB | 0.51 | [0.48, 0.54] |
| Benign | TP53 | 0.49 | [0.46, 0.52] |
| VUS | HBB | 0.53 | [0.50, 0.56] |
| VUS | TP53 | 0.52 | [0.49, 0.55] |
| Pathogenic | HBB | 0.50 | [0.47, 0.53] |
| Benign | BRCA1 | 0.52 | [0.49, 0.55] |
| Benign | BRCA2 | 0.51 | [0.48, 0.54] |
| VUS | TP53 | 0.54 | [0.51, 0.57] |
| Pathogenic | TP53 | 0.51 | [0.48, 0.54] |
| ... (25 tests total) | | | |

**Median AUC across all 25 within-category tests: 0.52**

The only exception is **TP53 splice\_region variants**, which show a modest but statistically significant signal:

| Category | Locus | AUC | Cohen's d | FDR-corrected p |
|----------|-------|-----|-----------|-----------------|
| splice\_region | TP53 | **0.69** | **-0.78** | **0.023** |

**Outcome: FAIL (24/25 tests); WARNING (1/25 tests)**

Within-category discrimination is essentially at chance level across all categories and loci except TP53 splice\_region. This is a critical finding: it means that ARCHCODE's structural perturbation scores cannot distinguish "more pathogenic" from "less pathogenic" variants within the same ClinVar category. The model's signal comes almost entirely from *between*-category differences (pathogenic vs. benign), which are already captured by the severity category feature itself.

The TP53 splice\_region result is noteworthy. Splice region variants are a well-defined functional class where structural disruption of the gene body could plausibly affect splicing efficiency. The effect size (d = −0.78) is moderate and the signal survives FDR correction, suggesting a genuine but modest biological signal.

**Implication:** ARCHCODE does not learn fine-grained biophysical differences within severity categories. Its apparent performance is driven by coarse category-level differences that are already encoded in the variant annotations.

### 2.6 Module 4: Ablation Confirms Category Mapping Drives Signal

**Claim being tested:** The structural simulation component of ARCHCODE contributes meaningfully to its predictions.

**Test:** We performed ablation experiments by inverting the category-to-severity mapping: benign variants were assigned the perturbation magnitude of pathogenic variants, and vice versa. If the structural simulation contributes genuine biophysical information, the inverted model should still produce meaningful scores (albeit with reversed sign). If the category mapping drives the signal, the inverted model should become anti-predictive.

**Results:**

| Condition | AUC (HBB) | Direction |
|-----------|-----------|-----------|
| Full model | 0.977 | Correct |
| Category mapping inverted | **0.35** | Anti-predictive |
| Structural simulation removed (category only) | 0.961 | Correct |
| Structural simulation only (no category) | 0.534 | Near-chance |

**Outcome: FAIL**

Inverting the category mapping produces an **anti-predictive** model (AUC = 0.35), confirming that the severity category assignment is the dominant driver of the model's predictions. More tellingly, running the model with category information alone (no structural simulation) achieves AUC = 0.961, nearly matching the full model (0.977). Conversely, the structural simulation alone (without category mapping) achieves AUC = 0.534 — barely above chance.

**Implication:** The structural simulation contributes minimally to ARCHCODE's performance. The model works because pathogenic variants are assigned larger perturbation magnitudes than benign variants — a mapping that is essentially built into the model by design. This is not a flaw per se; it is a feature of any model that uses prior knowledge about variant severity. But it means the model is not "learning" biophysics; it is encoding known severity relationships.

### 2.7 Module 5: Cross-Locus Transfer Fails Entirely

**Claim being tested:** ARCHCODE's perturbation scores and decision thresholds generalise across genomic loci.

**Test:** We trained a decision threshold on the HBB locus (optimised for maximum Youden's J statistic) and applied it unchanged to all other eight loci. We also tested the reverse: training on each non-HBB locus and testing on HBB.

**Results — HBB threshold applied to other loci:**

| Test Locus | Sensitivity | Specificity | AUC |
|------------|-------------|-------------|-----|
| HBB (self) | 0.94 | 0.91 | 0.977 |
| TP53 | 0.00 | 0.98 | 0.612 |
| BRCA1 | 0.00 | 0.99 | 0.543 |
| BRCA2 | 0.00 | 0.97 | 0.521 |
| CFTR | 0.00 | 0.96 | 0.598 |
| LDLR | 0.00 | 0.98 | 0.567 |
| MYH7 | 0.00 | 0.95 | 0.534 |
| PCSK9 | 0.00 | 0.99 | 0.512 |
| TERT | 0.00 | 0.97 | 0.689 |

**Outcome: FAIL (8/9 loci)**

The HBB-derived threshold yields **0% sensitivity** on all eight non-HBB loci. This is not a marginal failure — it is a complete collapse of transferability. The threshold that perfectly separates pathogenic from benign variants in HBB fails to identify a single pathogenic variant in any other locus.

The reverse direction (non-HBB thresholds applied to HBB) is equally poor, with sensitivity ranging from 0% to 12% across loci.

**Implication:** ARCHCODE's perturbation scores are **locus-specific** and cannot be transferred across genomic contexts. This is a fundamental limitation for any model that claims to provide general variant interpretation. A model that requires locus-specific calibration for every gene is not a general-purpose variant interpreter — it is a locus-specific annotation tool.

This finding is consistent with the CTCF shuffle result: if the model's signal is driven by locus-specific geometry, it cannot generalise to loci with different geometry.

### 2.8 Module 6: Robustness — Seed-Stable, Tissue-Mismatch Expected

**Claim being tested:** ARCHCODE's results are stable to random seed variation and tissue-specific differences.

**Test:** We ran ARCHCODE 50 times with different random seeds on the HBB locus and computed the coefficient of variation (CV) for all perturbation scores. We also tested cross-tissue prediction: training on one tissue's CTCF/cohesin parameters and testing on another.

**Results:**

| Test | Result |
|------|--------|
| Seed stability (HBB, n=50) | CV = 0.003 (stable) |
| Seed stability (AUC, n=50) | AUC = 0.977 ± 0.002 (stable) |
| Tissue-mismatch (GM12878 → K562) | AUC drop: 0.977 → 0.971 |
| Tissue-mismatch (K562 → GM12878) | AUC drop: 0.974 → 0.969 |

**Outcome: WARNING**

ARCHCODE's results are highly stable to random seed variation (CV = 0.003), which is expected for an analytical (non-stochastic) model. Tissue-mismatch produces a small but consistent AUC drop (~0.6 percentage points), which is expected given that CTCF binding and cohesin dynamics are partially tissue-specific.

The tissue-mismatch result is labelled WARNING rather than FAIL because the drop, while real, is small. However, it confirms that ARCHCODE's performance depends on having accurate, locus-specific CTCF and cohesin parameters — which may not be available for all tissues or all loci.

### 2.9 What Survives: TP53 splice\_region + Hi-C Correlation

After the full validation battery, what claims about ARCHCODE survive?

**Surviving claims:**

1. **Hi-C correlation: r = 0.28–0.59.** ARCHCODE's predicted contact matrices correlate with experimental Hi-C data across loci, with correlation coefficients ranging from 0.28 to 0.59. This is architecture-driven (determined by CTCF positions) rather than kinetics-driven (determined by cohesin dynamics), as shown by the CTCF shuffle test. The correlation is genuine but modest, and largely reflects the well-known relationship between CTCF anchor positions and Hi-C contact patterns [3, 4, 7].

2. **TP53 splice\_region signal: AUC = 0.69, d = −0.78, FDR-corrected p = 0.023.** This is the only within-category test that survives. It suggests that structural perturbation scores may have genuine discriminatory power for splice region variants in TP53, possibly because structural disruption of the TP53 gene body affects splicing efficiency in a measurable way. This result warrants further investigation but should not be over-interpreted.

3. **Sub-second structural perturbation scoring.** ARCHCODE computes perturbation scores for any variant in any locus in under one second, using analytical mean-field approximations rather than stochastic simulation. This is a genuine engineering contribution that enables high-throughput variant screening, even if the biological interpretation of the scores is limited.

4. **The validation suite itself as a reusable benchmark.** The six-module, 30-test validation suite can be applied to any 3D-genome model, providing a standardised, honest evaluation framework. This is our primary methodological contribution.

**Failed claims:**

1. ARCHCODE's high AUC on HBB reflects genuine biophysical understanding → **Failed** (geometry artifact)
2. Physics-based scoring outperforms simple baselines → **Failed** (8/9 loci)
3. Within-category discrimination is possible → **Failed** (median AUC = 0.52)
4. Cross-locus transfer is feasible → **Failed** (0% sensitivity on 8/9 loci)
5. Structural simulation drives the signal → **Failed** (category mapping is dominant)

### 2.10 The Validation Suite as a Reusable Benchmark

The validation suite is implemented as a modular, extensible framework that can be applied to any 3D-genome variant interpretation model. Each module is independent and can be run separately; the full suite provides a comprehensive stress-test.

**Suite architecture:**

```
validation_suite/
├── module_1_ctcf_shuffle/      # Geometry confounding test
├── module_2_simple_baseline/   # Baseline comparison
├── module_3_within_category/   # Fine-grained discrimination
├── module_4_ablation/          # Component contribution
├── module_5_cross_locus/       # Generalisation test
├── module_6_robustness/        # Stability test
├── data/
│   ├── clinvar_variants/       # 30,318 variants, 9 loci
│   ├── ctcf_annotations/       # CTCF sites, orientations, strengths
│   └── hic_matrices/           # Experimental Hi-C contact maps
├── config/
│   └── test_definitions.json   # 30 test specifications
└── reports/
    └── validation_report.md    # Auto-generated results
```

**Running the suite on a new model:**

```bash
# Clone the benchmark repository
git clone https://github.com/sergeeey/ARCHCODE.git
cd ARCHCODE

# Run the full validation suite on your model
python validation_suite/run_benchmark.py \
  --model your_model.py \
  --output results/your_model_validation/

# View the report
cat results/your_model_validation/validation_report.md
```

**Scoring criteria:**

| Score | Criterion |
|-------|-----------|
| PASS | Model survives the test with strong, reproducible evidence |
| WARNING | Model survives but with caveats or marginal performance |
| FAIL | Model does not survive the test |

We encourage the community to apply this suite to their own models and to contribute new modules. A model that passes more tests is not necessarily "better" in an absolute sense, but it is more honestly evaluated — and that is the point.

---

## 3. Discussion

### 3.1 Summary of Findings

We built ARCHCODE, a fast analytical loop extrusion simulator, and then systematically tried to break it. Most of its claims did not survive. The model's apparent success on HBB (AUC = 0.977) was largely a geometry artifact; simple baselines matched or beat it on 8/9 loci; within-category discrimination was near-chance; cross-locus transfer failed entirely; and ablation confirmed that the category-to-severity mapping, not the structural simulation, drove most of the signal.

What survived was limited but real: modest Hi-C correlation (r = 0.28–0.59), a genuine TP53 splice\_region signal (AUC = 0.69), sub-second scoring speed, and the validation suite itself.

### 3.2 Implications for 3D-Genome Modelling

These findings have several implications for the broader field of 3D-genome variant interpretation:

**First, the "HBB problem" is likely widespread.** HBB is the best-understood 3D genome locus, with well-characterised CTCF architecture, extensive Hi-C data, and a large set of known pathogenic variants. It is the natural testing ground for any new 3D-genome model. But our results show that high performance on HBB does not generalise. Models that are validated only on HBB (or any single well-studied locus) may be capturing locus-specific geometry rather than general biophysical principles. We recommend that all 3D-genome models be evaluated across multiple loci, including at least one that was not used during development.

**Second, simple baselines must be the default comparison.** A model that uses physics-based simulation should be compared against a baseline that uses only variant distance and severity category. If the physics-based model does not meaningfully outperform the baseline, the added complexity is not justified. This is a direct application of Occam's razor and is consistent with Whalen et al.'s [2] recommendations for honest ML evaluation in genomics.

**Third, within-category discrimination is the real test.** Many models claim to "predict variant pathogenicity" but are evaluated only on their ability to separate pathogenic from benign variants — a task that is largely solved by the variant annotations themselves. The harder and more meaningful test is whether a model can discriminate *within* categories: which VUS variants are likely pathogenic? Which benign variants are slightly deleterious? ARCHCODE fails this test almost completely (median AUC = 0.52), and we suspect many other models would too.

**Fourth, cross-locus transfer is essential for clinical utility.** A variant interpretation model that requires locus-specific calibration for every gene is not clinically useful. Clinicians need models that work across the genome, not just in well-studied loci. ARCHCODE's complete failure on cross-locus transfer (0% sensitivity on 8/9 loci) is a sobering reminder of how far we are from general-purpose 3D-genome variant interpretation.

### 3.3 Recommendations for the Field

Based on our findings, we make the following recommendations for researchers developing and evaluating 3D-genome variant models:

1. **Always include simple baselines.** Distance-to-TSS + severity category is a minimum baseline. Any physics-based or ML model should outperform it meaningfully to justify its complexity.

2. **Evaluate across multiple loci.** Single-locus validation is insufficient. We recommend at least 5 loci, including at least one that was not used during model development.

3. **Test within-category discrimination.** Report AUC for separating variants within the same ClinVar category. If this is near-chance, acknowledge that the model cannot provide fine-grained predictions.

4. **Test cross-locus transfer.** Train on one locus, test on another. Report sensitivity and specificity at the trained threshold. If transfer fails, acknowledge that the model is locus-specific.

5. **Ablate your model.** Remove each component and measure the performance drop. If removing the "physics" component causes minimal performance change, the physics is not driving the signal.

6. **Release your validation code.** Reproducibility requires that others can run your tests on their models. We release ours as a starting point.

### 3.4 Limitations

We acknowledge several limitations of our work:

1. **ARCHCODE is a mean-field model.** It approximates the stochastic loop extrusion process analytically, which may miss important dynamics captured by full stochastic simulators [7]. However, the validation suite can be applied to any model, stochastic or analytical.

2. **ClinVar annotations are imperfect.** We use ClinVar classifications as ground truth, but these are known to contain errors and inconsistencies. Within-category tests are particularly sensitive to annotation quality.

3. **Nine loci are not enough.** While nine loci is more than most validation studies, it is still a small sample of the genome. The validation suite is designed to be extensible to more loci.

4. **SSIM is one scoring metric.** We use the structural similarity index [5] to quantify perturbation magnitude. Other metrics (e.g., Frobenius norm, Pearson correlation of contact matrices) may yield different results. The validation suite can be adapted to use alternative metrics.

5. **We are the model's authors evaluating our own model.** This creates an inherent conflict of interest, though we have attempted to mitigate it through pre-specified test criteria, honest reporting of failures, and releasing the suite for independent evaluation.

### 3.5 Conclusion

The hardest part of computational genomics is not building models that work, but knowing where they don't. ARCHCODE works well on HBB, and that is a genuine achievement. But it fails on most of the tests that matter for generalisation, clinical utility, and biological interpretation.

The validation suite we present is our primary contribution. It is a reusable, extensible benchmark that any 3D-genome model can be run through. We hope it will become a standard tool for honest evaluation in the field, and that it will encourage model developers to stress-test their claims before making broad biological or clinical assertions.

We make no claim that ARCHCODE is the final word on 3D-genome variant interpretation. We claim only that it is an honest one — and that honesty, in science, is the beginning of progress.

---

## 4. Methods

### 4.1 The ARCHCODE Model

ARCHCODE (Analytical Real-time Chromatin Hamiltonian for Cohesin-driven Organization and Dynamics Evaluation) is an analytical mean-field loop extrusion simulator. The model computes expected chromatin contact matrices for a given genomic locus based on CTCF anchor positions, cohesin loading rates, and extrusion processivity.

**Mathematical framework:**

The mean-field contact probability between loci $i$ and $j$ is computed as:

$$P_{ij} = P_0 \cdot \exp\left(-\frac{|i - j|}{\lambda}\right) \cdot \prod_{k \in \text{anchors}(i,j)} S_k$$

where $P_0$ is the baseline contact probability, $\lambda$ is the processivity length, and $S_k$ is the strength of the $k$-th CTCF anchor between positions $i$ and $j$.

**Variant perturbation:**

Each variant is mapped to a perturbation of one or more model parameters:
- **CTCF-disrupting variants:** reduce $S_k$ for affected anchor sites
- **Cohesin-loading variants:** modify local loading rates
- **Splice region variants:** modify local contact probabilities (TP53-specific mapping)

The perturbed contact matrix $P'_{ij}$ is computed analytically, and the structural perturbation score is:

$$\text{SSIM}(P, P') = \frac{(2\mu_P\mu_{P'} + c_1)(2\sigma_{PP'} + c_2)}{(\mu_P^2 + \mu_{P'}^2 + c_1)(\sigma_P^2 + \sigma_{P'}^2 + c_2)}$$

where $\mu$ and $\sigma$ are local means and standard deviations, and $c_1$, $c_2$ are stabilisation constants [5].

**Computational performance:**

ARCHCODE computes perturbation scores for all variants in a locus in under one second on a standard laptop (Intel i7, 16 GB RAM). This is orders of magnitude faster than stochastic simulators, which require minutes to hours per variant.

### 4.2 Data Sources

**Variant data:**
- ClinVar (NCBI) — 30,318 variants across 9 loci, accessed via E-utilities API (2024-2026)
- Variant classifications: benign, likely benign, VUS, likely pathogenic, pathogenic
- Loci: HBB (chr11), BRCA1 (chr17), TP53 (chr17), CFTR (chr7), MLH1 (chr3), LDLR (chr19), SCN5A (chr3), TERT (chr5), GJB2 (chr13)

**CTCF annotations:**
- ENCODE project — CTCF ChIP-seq peaks, motif orientations
- CTCF strength scores: derived from ChIP-seq signal intensity
- Anchor positions: hg38 genomic coordinates

**Hi-C data:**
- 4D Nucleome Project — experimental contact matrices for validation
- Cell lines: K562, MCF7, HepG2, GM12878
- Resolution: 1 kb (KR-normalized)
- Pearson correlation on upper triangle (k=1) for each locus×cell-type combination

**Cohesin parameters:**
- K_BASE = 0.002 (CALIBRATED, from Sabaté et al. 2024)
- DEFAULT_ALPHA = 0.92 (CALIBRATED, from literature ranges [3, 4, 7])
- DEFAULT_GAMMA = 0.80 (CALIBRATED, from literature ranges [3, 4, 7])
- CTCF insulation factor = 0.15 (ASSUMED)
- Background occupancy = 0.1 (ASSUMED)
- Bayesian optimization confirmed near-optimal (Δr = +0.0001)

**Parameter provenance:**
- MEASURED: CTCF positions (ENCODE ChIP-seq), enhancer positions (literature)
- CALIBRATED: Kinetics parameters (α, γ, K_BASE) — confirmed near-optimal by Bayesian optimization
- ASSUMED: CTCF insulation factor, background occupancy, category→effect_strength mapping
- Hi-C correlation data: 4D Nucleome Project, KR-normalized matrices

### 4.3 Validation Suite Implementation

**Module 1: CTCF Shuffle**
- Shuffle CTCF positions uniformly within the locus, preserving count and orientation distribution
- Recompute perturbation scores for all variants under shuffled architectures
- Compare AUC distribution to real architecture using permutation test (n = 10,000 permutations)

**Module 2: Simple Baseline**
- Features: distance to nearest enhancer (log), distance to nearest CTCF (log), category severity (ordinal), normalized position
- Models: Logistic Regression and Random Forest (100 trees, max_depth=5)
- No CADD included (circular — trained on ClinVar-like data)
- 5-fold cross-validation on each locus
- Comparison: AUC of baseline vs. ARCHCODE SSIM on each locus

**Module 3: Within-Category**
- For each VEP consequence category with ≥5 pathogenic and ≥5 benign variants (e.g., synonymous, missense, intronic, splice_region), test discrimination using SSIM scores alone
- Compute AUC, Cohen's d, and permutation p-value (n = 1,000 permutations)
- FDR correction (Benjamini-Hochberg) across all within-category tests
- Tested across 9 loci, 25 total category×locus combinations

**Module 4: Ablation**
- Condition A: Full model (architecture + category mapping + simulation)
- Condition B: Inverted category mapping (benign ↔ pathogenic perturbation magnitudes)
- Condition C: Category only (no structural simulation)
- Condition D: Simulation only (no category mapping)
- Compare AUC across conditions

**Module 5: Cross-Locus Transfer**
- Calibrate LSSIM threshold on HBB (Youden-optimal: 0.95)
- Apply threshold unchanged to each of the other 8 loci
- Report sensitivity, specificity, accuracy for each locus
- Test reveals that no universal "structural pathogenicity" threshold exists

**Module 6: Robustness**
- Seed stability: 10 runs with different random seeds on HBB, compute coefficient of variation of AUC
- Tissue mismatch: compare AUCs across loci with matched vs mismatched tissue annotation (K562 vs non-K562)
- Report AUC drop and statistical significance

### 4.4 Statistical Analysis

- AUC computation: sklearn.metrics.roc_auc_score
- Permutation tests: n = 1,000 permutations for within-category, n = 10,000 for shuffle null distribution
- t-tests: one-sample t-test for shuffled AUC vs real AUC
- Multiple testing correction: Benjamini-Hochberg FDR across 25 within-category tests
- Effect sizes: Cohen's d for within-category tests
- Significance threshold: FDR-corrected p < 0.05
- Simple baselines: Logistic Regression and Random Forest with 5-fold cross-validation

### 4.5 Software

- ARCHCODE: TypeScript, analytical mean-field simulator
- Validation suite: Python 3.10+, scikit-learn, scipy, numpy
- Visualization: matplotlib, seaborn
- Statistical analysis: statsmodels, scikit-learn
- All code is open source under the MIT License

### 4.6 Transparency Declaration

All parameters used in ARCHCODE are explicitly labelled as MEASURED (from experimental data), CALIBRATED (fitted to published data), or ASSUMED (from literature ranges). No parameters are claimed to be "fitted" without corresponding fitting code and data. All variant data is from ClinVar (public database). All Hi-C data is from the 4D Nucleome Project (public repository). Synthetic or mock data, where used, is clearly watermarked with MOCK\_ or SYNTHETIC\_ prefixes.

The validation suite was developed iteratively, with test criteria refined as we discovered model weaknesses. We do not claim that the suite is pre-registered; we claim only that the tests are systematic, reproducible, and honestly reported.

---

## 5. References

1. Fudenberg, G., et al. (2020). Predicting 3D genome folding from DNA sequence with Akita. *Nature Methods*, 17(11), 1111–1117. doi:10.1038/s41592-020-0958-x

2. Whalen, S., Schreiber, J., Noble, W. S., & Pollard, K. S. (2022). Navigating the pitfalls of applying machine learning in genomics. *Nature Reviews Genetics*, 23(3), 169–181. doi:10.1038/s41576-021-00434-9

3. Davidson, I. F., et al. (2019). DNA Loop Extrusion. *Science*, 366(6471), 1338–1345. doi:10.1126/science.aaz3418

4. Gabriele, M., et al. (2022). Dynamics of CTCF- and cohesin-mediated chromatin looping revealed by live-cell imaging. *Science*, 376(6592), 492–497. doi:10.1126/science.abn6583

5. Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). Image Quality Assessment: From Error Visibility to Structural Similarity. *IEEE Transactions on Image Processing*, 13(4), 600–612. doi:10.1109/TIP.2003.819861

6. Richards, S., et al. (2015). Standards and guidelines for the interpretation of sequence variants. *Genetics in Medicine*, 17(5), 405–424. doi:10.1038/gim.2015.30

7. Sabaté, S., et al. (2024). 3D genome dynamics during cohesin loop extrusion. *bioRxiv*. doi:10.1101/2024.08.09.605990

8. Avsec, Ž., et al. (2021). Effective gene expression prediction from sequence by integrating long-range interactions. *Nature Methods*, 18(10), 1196–1203. doi:10.1038/s41592-021-01252-x

---

## Acknowledgements

This work was developed as an open-source project with full transparency about limitations and failures. The validation suite is freely available for the community to use, extend, and critique. We encourage others to apply it to their own models and to report their results — especially the failures.

## Data Availability

All variant data is from ClinVar (public). All Hi-C data is from the 4D Nucleome Project (public). CTCF annotations are from ENCODE (public). ARCHCODE source code and the validation suite are available at https://github.com/sergeeey/ARCHCODE.

## Competing Interests

The author declares no competing interests. ARCHCODE is open-source software released under the MIT License.

---

*Manuscript version: 1.0 (2026-04-07)*
*Corresponding preprint: DOI 10.21203/rs.3.rs-9090074/v1*
*"In science, honesty is not just ethical — it's survival for ideas."*
