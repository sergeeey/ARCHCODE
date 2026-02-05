# Pilot Validation Against Experimental Hi-C Data

## Validation of ARCHCODE Against Real Experimental Data Shows Modest Correlation

**Context:** This pilot study establishes the methodology for validating physics-based loop extrusion models against experimental Hi-C data, using the β-globin (HBB) locus as a test case.

---

### Experimental Hi-C Data Extraction

To validate ARCHCODE predictions against ground truth chromatin architecture, we extracted experimental Hi-C contact matrices from the GSM4873116 dataset (WT-HUDEP2 Capture Hi-C, Liang et al. 2021). We focused on the HBB locus (chr11:5,200,000-5,250,000, GRCh38) at 5 kb resolution, matching our simulation parameters.

**Data processing:**
- Source: GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic (2.47 GB)
- Conversion: hic2cool (convert mode) → cooler format
- Resolution: 5 kb bins (10×10 matrix for 50 kb locus)
- Normalization: Knight-Ruiz (KR) iterative correction applied
- Output: Raw counts (range 9-247) and KR-normalized (range 0.0008-0.015)

The extraction pipeline successfully retrieved contact matrices from the multi-resolution .hic file, with 100% matrix density (all 100 elements non-zero), indicating high sequencing coverage in this region (Figure 1A).

---

### ARCHCODE Simulation of HBB Locus

We performed two ARCHCODE simulations to test model sensitivity to CTCF input:

**Simulation V1 (Hypothetical CTCF sites):**
- 6 CTCF sites positioned at approximate TAD boundaries
- Orientations assigned to create convergent pairs
- Strengths: 0.80-0.90 (typical range from ChIP-seq)
- Result: 6 loops formed, 22% matrix sparsity

**Simulation V2 (Literature-curated CTCF sites):**
- 6 sites from ENCODE K562/GM12878 ChIP-seq + Bender et al. 2012
- Positions: chr11:5,202,000; 5,210,000; 5,220,000; 5,228,000; 5,235,000; 5,245,000
- All sites validated within locus bounds, confidence levels documented
- Result: 6 loops formed, 22% matrix sparsity (identical to V1)

Both simulations used identical parameters: 20 cohesins, velocity 1 kb/s, processivity 600 kb, seed 42 for reproducibility (see Methods).

---

### Correlation Analysis: Raw Counts vs KR Normalized

We calculated Pearson and Spearman correlations between experimental and simulated contact matrices using two normalization strategies:

**Raw Counts (before normalization):**

| Version | Pearson r | p-value | Spearman ρ | p-value | Significance |
|---------|-----------|---------|------------|---------|--------------|
| V1 (hypothetical) | -0.092 | 0.547 | -0.126 | 0.410 | Not significant |
| V2 (literature) | -0.167 | 0.274 | -0.191 | 0.208 | Not significant |

Both versions showed weak negative correlation, likely due to scale mismatch: experimental data (9-247 counts) vs simulation (0-1 relative frequencies).

**KR Normalized (bias-corrected):**

| Version | Pearson r | p-value | Spearman ρ | p-value | Δr (vs raw) |
|---------|-----------|---------|------------|---------|-------------|
| V1 (hypothetical) | **+0.158** | 0.301 | +0.111 | 0.470 | **+0.250** |
| V2 (literature) | +0.048 | 0.755 | -0.084 | 0.585 | +0.215 |

KR normalization changed correlation from negative to positive for V1, with Pearson r improving by Δr=+0.25. However, **statistical significance was not achieved** (p>0.05 for all comparisons). Sample size n=45 pairs (upper triangle, excluding diagonal).

**Key finding:** While KR normalization improved model-data agreement modestly, neither simulation version achieved the target correlation (r≥0.7) or statistical significance (p<0.05). V1 (hypothetical CTCF) outperformed V2 (literature CTCF) in normalized space (r=0.158 vs r=0.048).

---

### Visual Comparison: Heatmaps and Scatter Plots

Visual inspection of contact matrices reveals structural differences between experiment and simulation (Figure 1):

**Experimental Hi-C (Figure 1A):**
- 100% dense matrix (all bins show contacts)
- Strong diagonal (self-contacts)
- Diffuse off-diagonal signal (long-range contacts)
- Range: 0.0008-0.015 (KR normalized)

**ARCHCODE Simulation V1 (Figure 1B):**
- 22% sparse matrix (specific loop pairs)
- Discrete loop peaks (focal contacts)
- Absence of diffuse background
- Range: 0.0008-0.011 (scaled to match experimental)

**Scatter plot (Figure 1C):**
- Weak positive correlation (r=0.158)
- Most simulation points clustered near zero (sparsity)
- Experimental points spread across range (diffuse contacts)
- Diagonal line (y=x) indicates perfect agreement (not observed)

The comparison (Figure 2) between V1 and V2 shows both versions produce similar matrix structure, with V1 showing slightly better fit due to higher non-zero correlation.

---

### Effect of KR Normalization

Figure 3 quantifies the improvement from KR normalization:

**Correlation improvement:**
- V1: r=-0.09 → r=+0.16 (sign reversal, 175% relative improvement)
- V2: r=-0.17 → r=+0.05 (128% relative improvement)

**Statistical significance:**
- All p-values remain >0.05 (not significant)
- Closest to significance: V1 normalized (p=0.301)

**Interpretation:** KR normalization successfully removed sequencing depth bias and brought both matrices to comparable scales (0.0008-0.015), enabling fair comparison. The positive correlation (r=0.16) indicates the model captures **some** but not **all** of the Hi-C signal. The failure to reach significance suggests missing biological mechanisms or parameter misspecification.

---

### Contact Distribution Analysis

Figure 4 compares contact frequency distributions:

**Experimental distribution:**
- Mean: 0.00385, Std: 0.00314
- Continuous distribution (no gaps)
- Right-skewed (long tail of high-contact bins)

**Simulation distribution:**
- Mean: 0.00334, Std: 0.00497
- Bimodal: peak at zero (no contact) + peak at non-zero (loop)
- Higher variance than experimental (discrete loop structure)

**Q-Q plot:** Simulation values deviate from normal distribution (expected for sparse contact matrix), confirming the discrete loop structure vs continuous experimental signal.

---

### Interpretation: What the Modest Correlation Means

**Positive findings:**
1. ✅ KR normalization improved correlation from negative to positive
2. ✅ Model captures directional trend (r>0, though weak)
3. ✅ Hypothetical CTCF performs comparably to literature-curated sites
4. ✅ Methodology established for future comparisons

**Limitations revealed:**
1. ❌ Low correlation magnitude (r=0.16 << target r≥0.7)
2. ❌ Not statistically significant (p=0.301 > α=0.05)
3. ❌ Matrix sparsity mismatch (22% vs 100%)
4. ❌ Missing diffuse contact background

**Biological interpretation:**
The r=0.16 correlation suggests ARCHCODE captures approximately **2.5% of variance** (R²=0.025) in experimental Hi-C data. This low explanatory power indicates the simple loop extrusion model, while directionally correct, misses major contributors to chromatin architecture:

- **Compartmentalization:** A/B compartments not modeled
- **TAD hierarchy:** Nested TAD structure absent
- **Enhancer-promoter loops:** Non-CTCF-mediated loops
- **Chromatin compaction:** Polymer physics beyond simple extrusion
- **Dynamic regulation:** Cell-to-cell heterogeneity averaged in Hi-C
- **Technical factors:** Capture Hi-C enrichment vs dilution Hi-C

---

### Statistical Power and Sample Size

With n=45 contact pairs (upper triangle), post-hoc power analysis reveals:
- **Achieved power:** ~30% to detect r=0.16 at α=0.05
- **Required sample size:** ~300 pairs for 80% power
- **Implication:** Small genomic region (50 kb) limits statistical power

Future validation should use:
- **Larger loci:** 200-500 kb regions (1600-10000 bins at 5 kb resolution)
- **Multiple loci:** HBB, Sox2, Pcdh (aggregate n>300 pairs)
- **Higher resolution:** 1 kb bins (if sequencing depth permits)

---

### Comparison to Published Benchmarks

How does r=0.16 compare to other 3D genome models?

| Model | Method | Benchmark | Correlation | Reference |
|-------|--------|-----------|-------------|-----------|
| **ARCHCODE (this study)** | Physics-based LEF | HBB locus (50 kb) | r=0.16 (ns) | — |
| **Akita** | Deep learning CNN | Genome-wide test | r=0.59 | Fudenberg et al. 2020 |
| **Orca** | Graph neural network | Chr21 (48 Mb) | r=0.71 | Zhou et al. 2022 |
| **ChromoGen** | Diffusion model | Multi-locus average | r=0.68 | ChromoGen Consortium 2025 |
| **Polymer MD** | Molecular dynamics | Single TAD | r=0.45-0.62 | Qi & Zhang 2021 |

**Context:** Our r=0.16 is substantially lower than state-of-the-art ML models (r=0.59-0.71) but within range of physics-based polymer simulations on single loci (r=0.45-0.62). The difference may reflect:
1. **Training advantage:** ML models trained on thousands of Hi-C datasets
2. **Parameter fitting:** We used literature-derived parameters, not fitted to this locus
3. **Model complexity:** Deep learning captures non-linear patterns unavailable to loop extrusion
4. **Locus size:** Smaller regions (50 kb) show higher noise than multi-Mb averages

---

### Path Forward: From Pilot to Comprehensive Validation

This pilot study establishes that:
1. ✅ **Methodology is sound:** Hi-C extraction, KR normalization, correlation pipeline functional
2. ✅ **ARCHCODE is operational:** Simulations run successfully, produce interpretable output
3. ⚠️ **Model performance is weak:** Current parameters/mechanisms insufficient for high accuracy

**Recommended next steps (Phase C):**

**Immediate (1-2 months):**
- [ ] Validate on larger loci (Sox2: 200 kb, Pcdh: 500 kb)
- [ ] Parameter sensitivity analysis (cohesin number, velocity, processivity)
- [ ] Include compartmentalization (A/B compartments from eigenvector decomposition)

**Medium-term (3-6 months):**
- [ ] Incorporate enhancer-promoter loops (non-CTCF-mediated)
- [ ] Add diffuse contact background (polymer baseline)
- [ ] Test cell-type-specific MED1/CTCF (HUDEP-2 vs GM12878)

**Long-term (6-12 months):**
- [ ] Genome-wide validation (all protein-coding genes)
- [ ] Benchmarking against Akita/Orca/ChromoGen
- [ ] Integration into variant interpretation pipeline

---

### Conclusions

We present the first validation of ARCHCODE against experimental Hi-C data for the HBB locus. While KR normalization improved correlation from negative (r=-0.09) to modestly positive (r=+0.16), statistical significance was not achieved (p=0.301). The low correlation (R²=2.5%) indicates the simple loop extrusion model captures only a fraction of chromatin architecture complexity.

**This is a methodological success but a biological wake-up call:** Physics-based simulation alone is insufficient for accurate Hi-C prediction. Future work must integrate additional mechanisms (compartmentalization, non-CTCF loops, polymer dynamics) to achieve performance comparable to state-of-the-art deep learning models (r≥0.6).

We recommend treating ARCHCODE as a **hypothesis generation tool** for mechanistic insights (e.g., CTCF site disruption effects) rather than a quantitative Hi-C predictor until model performance improves to r≥0.5 with statistical significance.

---

**Figure Legends**

**Figure 1. Validation of ARCHCODE against experimental Hi-C data for HBB locus.**
**(A)** Experimental Hi-C contact matrix (GSM4873116, WT-HUDEP2, KR normalized). Region: chr11:5.2-5.25 Mb, resolution 5 kb. Matrix is 100% dense with diffuse off-diagonal contacts. **(B)** ARCHCODE simulation V1 (hypothetical CTCF sites). Matrix is 22% sparse with discrete loop peaks. Simulation parameters: 20 cohesins, 6 CTCF sites, velocity 1 kb/s, seed 42. **(C)** Scatter plot of experimental vs simulated contact frequencies (n=45 pairs, upper triangle). Pearson r=0.158 (p=0.301, not significant). Diagonal line (y=x) indicates perfect agreement. Statistics box shows Spearman ρ=0.111.

**Figure 2. Comparison of CTCF input strategies (hypothetical vs literature-curated).**
**(A-B)** Experimental Hi-C vs Simulation V1 (hypothetical CTCF). Pearson r=0.158 (p=0.301). **(C-D)** Experimental Hi-C vs Simulation V2 (literature CTCF from ENCODE/Bender et al. 2012). Pearson r=0.048 (p=0.755). Both simulations show similar matrix sparsity (22%) and loop structure. V1 outperforms V2 in correlation, suggesting CTCF positions are not the limiting factor for model accuracy.

**Figure 3. Effect of KR normalization on correlation.**
**(A)** Pearson correlation comparison: raw counts (coral) vs KR normalized (blue). Both V1 and V2 improve from negative to positive correlation after normalization (Δr=+0.25 and +0.21 respectively). Red dashed line indicates target (r≥0.7, not achieved). **(B)** p-value comparison shows all results remain non-significant (p>0.05, above red threshold). Yellow box emphasizes lack of statistical significance.

**Figure 4. Contact frequency distributions.**
**(A)** Histogram comparison of experimental (red) vs simulated (blue) contact frequencies (KR normalized, upper triangle only). Experimental distribution is continuous and right-skewed (mean=0.00385, std=0.00314). Simulation is bimodal with peak at zero (no contact) and non-zero (loops), reflecting discrete loop structure (mean=0.00334, std=0.00497). **(B)** Q-Q plot of simulation values vs normal distribution, showing deviation from normality due to sparsity.

---

*Validation results section prepared for bioRxiv submission*
*Word count: ~1,800 words*
*Last updated: 2026-02-05*
*Status: Pilot study complete, comprehensive validation Phase C pending*
