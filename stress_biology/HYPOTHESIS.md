# Hypotheses — Stress Biology & Mutagenesis

**Version:** 1.0  
**Created:** 2026-04-25  
**Frozen:** Yes (do not modify after starting Experiment 1)

---

## Core Hypothesis (H0)

### Statement

> **Cellular doubling time inversely correlates with somatic mutation rate.**

**Механизм (Bilinsky-inspired):**

1. Fast-dividing cells spend more time in **state Q** (low ATP, vulnerable)
2. State Q → reduced nuclear envelope stability → less DNA damage protection
3. Less protection → more replication errors → higher mutation rate

**Quantitative prediction:**

- Spearman r > 0.4 (doubling time vs mutation rate)
- p < 0.01 (after multiple testing correction)
- Effect robust across tissue types (at least 5/10 tissues)

**Baseline (null model):**

- No correlation (r ≈ 0)
- OR weak correlation driven by tissue type confounding (like ARCHCODE genomics!)

**Kill criterion:**

- r < 0.3 after 3 months → hypothesis killed
- r > 0.3 but p > 0.05 → underpowered, need more data or wet-lab

---

## Supporting Hypotheses

### H1: Tissue-Specific Mutation Burden

**Statement:**

> High-proliferation tissues (colon, skin, blood) show 2-5× higher mutation rates than low-proliferation tissues (brain, heart).

**Testable prediction:**

| Tissue | Proliferation Rate | Expected Mutation Rate |
|--------|-------------------|----------------------|
| Colon | High (3-5 days doubling) | >100 mutations/Mb |
| Skin | High (2-3 days) | >80 mutations/Mb |
| Blood | High (varies, 1-10 days) | 50-150 mutations/Mb |
| Brain | Low (quiescent) | <30 mutations/Mb |
| Heart | Low (post-mitotic) | <20 mutations/Mb |

**Data source:** TCGA + Sender et al. 2016 (Cell)

**Statistical test:** Mann-Whitney U (high vs low proliferation groups)

**Kill criterion:** p > 0.05 OR effect size < 1.5×

---

### H2: Cell Cycle Phase Mutation Spectrum

**Statement:**

> Cells in S/G2 (active replication) accumulate different mutation types than G0/G1 (quiescent).

**Predicted spectrum shift:**

- **S/G2 (replication errors):** More C>T transitions, indels
- **G0/G1 (oxidative damage):** More C>A transversions, double-strand breaks

**Data source:** Single-cell RNA-seq + single-cell WGS (10X Genomics)

**Statistical test:** Chi-square test on mutation type distribution

**Kill criterion:** p > 0.01 OR Cramér's V < 0.2 (weak association)

---

### H3: ATP Proxy Correlates with Mutation Rate

**Statement:**

> Computational ATP proxy (OXPHOS gene expression) negatively correlates with mutation rate.

**ATP proxy definition:**

```python
ATP_proxy = mean([
    COX1, COX2, COX3, COX4, COX5A, COX5B, COX6A, COX7A,
    ATP5A, ATP5B, ATP5C, ATP5D, ATP5F, ATP5G, ATP5H,
    NDUFB1, NDUFB2, NDUFB3  # Complex I
])
```

**Prediction:**

- Spearman r < -0.3 (negative correlation: more ATP → fewer mutations)
- Mechanism: high ATP → better repair machinery → lower mutation rate

**Validation:**

- Compare ATP proxy with published ATP measurements (luciferase assays)
- Expected r > 0.5 (proxy vs real ATP)

**Kill criterion:** r > -0.2 (weak or wrong direction)

---

## Null Hypotheses (what we're trying to kill)

### NULL-1: Confounding by tissue type

> Mutation rate differences are driven by tissue type, not proliferation rate.

**How to test:**

- Within-tissue analysis (e.g., fast vs slow colon samples)
- If within-tissue r < 0.2 → confounded

**If NULL-1 confirmed:**

- ARCHCODE v1 lesson: "category drives signal, not mechanism"
- Need matched controls (same tissue, different proliferation)

---

### NULL-2: Technical artifacts

> Mutation rate differences are sequencing artifacts (coverage, batch effects).

**How to test:**

- Control for:
  - Sequencing depth (normalize by coverage)
  - Batch (include batch as covariate)
  - Purity (tumor content)

**If NULL-2 confirmed:**

- Pipeline issue, not biology
- Fix preprocessing, re-run

---

### NULL-3: ATP proxy is not ATP

> OXPHOS gene expression doesn't reflect actual ATP levels.

**How to test:**

- Cross-validate with published ATP measurements
- If r < 0.3 → proxy failed

**If NULL-3 confirmed:**

- Need direct ATP measurement (wet-lab required)
- Computational proxy insufficient

---

## Experiment Design

### Experiment 1: Correlation Analysis (3 months)

**Input:**

- TCGA mutation data (MAF files, n > 1000)
- Doubling time from literature (PubMed mining)

**Analysis:**

```R
# Spearman correlation
cor.test(doubling_time, mutation_rate, method = "spearman")

# Bootstrap 95% CI (10K iterations)
boot_r <- boot(data, cor_spearman, R = 10000)

# Multiple testing correction (Bonferroni)
p_adj <- p.adjust(p_values, method = "bonferroni")
```

**Output:**

- `results/h0_scatter.png`
- `results/h0_stats.json`

---

### Experiment 2: ATP Proxy Validation (1 month)

**Input:**

- RNA-seq data (TCGA, GTEx)
- Published ATP measurements (literature)

**Analysis:**

```python
# Compute ATP proxy
atp_proxy = expression_matrix[oxphos_genes].mean(axis=1)

# Correlate with mutation rate
r, p = spearmanr(atp_proxy, mutation_rate)
```

**Output:**

- `results/h3_atp_proxy.png`

---

### Experiment 3: Wet-Lab Validation (6 months, optional)

**Design:**

| Condition | ATP manipulation | Expected mutation rate |
|-----------|-----------------|----------------------|
| Control | Normal | Baseline |
| Low ATP | Oligomycin (inhibit Complex V) | **2-3× higher** |
| High ATP | Pyruvate + creatine | **0.5× lower** |

**Measurement:**

- Whole-genome sequencing after 10 passages
- Count de novo mutations (compared to passage 0)

**Collaborator needed:** Wet-lab with WGS capacity

---

## Falsification Protocol (ARCHCODE-style)

### Pre-registration

- Freeze hypotheses BEFORE seeing data
- Commit this file to git
- No p-hacking, no HARKing (Hypothesizing After Results Known)

### Matched Controls

- Same tissue, different proliferation → isolate proliferation effect
- Example: fast-growing colon tumor vs slow-growing colon tumor

### Baseline Comparison

- Null model: tissue type alone (no proliferation info)
- If null model AUC > 0.7 → confounded (ARCHCODE lesson learned)

### Within-Category Tests

- Test correlation within each tissue separately
- If 0/10 tissues significant → overall effect is artifact

---

## Expected Outcomes (probability estimates)

| Outcome | Probability | Implication |
|---------|-----------|-------------|
| **Null result** (r < 0.3) | 60% | Negative result, publish in PLOS Comp Bio |
| **Weak positive** (0.3 < r < 0.5) | 30% | Theoretical paper, needs wet-lab validation |
| **Strong positive** (r > 0.5) | 10% | High-impact, proceed to Experiment 3 |

---

## Publication Strategy

### Null Result

**Журналы:** PLOS Computational Biology, F1000Research, PeerJ

**Title:** "No Evidence for Correlation Between Cell Cycle Duration and Somatic Mutation Rate: A Meta-Analysis of TCGA Data"

**Impact:** Prevents others from wasting time on wrong hypothesis

---

### Weak Positive

**Журналы:** Bioessays, Trends in Cell Biology, Genome Biology (correspondence)

**Title:** "Cell Proliferation Rate Weakly Predicts Mutation Burden: A Computational Framework Inspired by Radiosensitivity Models"

**Impact:** Theoretical contribution, opens wet-lab questions

---

### Strong Positive

**Журналы:** Nature Cell Biology, Nature Genetics, Cell

**Title:** "ATP Availability Determines Somatic Mutation Rate via Nuclear Envelope Stability"

**Impact:** Mechanistic discovery, paradigm shift

---

## Revision History

- **2026-04-25:** Initial version, hypotheses frozen
- **[Future]:** No changes allowed after Experiment 1 starts (prevents p-hacking)

---

**Status:** FROZEN. Proceed to data collection.
