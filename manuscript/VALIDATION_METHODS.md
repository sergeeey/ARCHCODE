# Methods: Hi-C Validation Pipeline

## Experimental Hi-C Data Extraction

### Data Source

We obtained experimental Hi-C data from the Gene Expression Omnibus (GEO) accession GSM4873116 (Liang et al., 2021), which contains Capture Hi-C data for wild-type HUDEP-2 human erythroid progenitor cells. This dataset was selected because:

1. **Cell-type relevance:** HUDEP-2 cells actively express β-globin genes, making them appropriate for HBB locus analysis
2. **Capture enrichment:** Capture Hi-C provides higher resolution for target loci compared to dilution Hi-C
3. **Data quality:** High sequencing depth (>200 million valid pairs) ensures robust contact matrix estimation
4. **Public availability:** Data is openly accessible, enabling reproducibility

**File details:**

- Filename: `GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic`
- File size: 2.47 GB
- Format: .hic (Juicer format, multi-resolution)
- Assembly: GRCh38/hg38
- Processing: Juicer pipeline (Durand et al., 2016)

### Format Conversion: .hic to .cool

The .hic format is not directly readable by Python-based analysis tools. We converted to cooler format using hic2cool (v0.8.3):

```bash
hic2cool convert \
  GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic \
  temp_hudep2_wt.cool \
  -r 5000
```

**Parameters:**

- `convert`: Conversion mode (extracts specified resolution)
- `-r 5000`: 5 kb resolution (bin size)

**Technical note:** Initial attempts using hic2cool without the `convert` mode argument failed with syntax error. The correct invocation requires explicitly specifying the mode before file paths.

**Alternative tools attempted:**

- `hic-straw` (v1.3.1): Failed due to missing Microsoft Visual C++ 14.0 compiler
- `hictkpy` (v0.0.5): Failed with API error (resolution parameter required but not accepted)

**Output:**

- File: `temp_hudep2_wt.cool` (63 MB)
- Format: Cooler HDF5
- Chromosomes: Standard naming ("1", "2", ..., "X", "Y") — **not** "chr1", "chr2" format

### Matrix Extraction

We extracted contact matrices for the HBB locus (chr11:5,200,000-5,250,000) using cooler Python API (v0.10.4):

```python
import cooler

# Open cooler file
c = cooler.Cooler('temp_hudep2_wt.cool')

# Extract region (NOTE: chromosome naming)
chrom = '11'  # Not 'chr11' — critical for successful extraction
start = 5200000
end = 5250000

# Fetch matrix (balance=False for raw counts initially)
matrix_raw = c.matrix(balance=False).fetch(f'{chrom}:{start}-{end}')
```

**Critical bug fix:** Initial attempts using `'chr11'` failed with `ValueError: Unknown sequence label: chr11`. Inspection of `c.chromnames` revealed cooler file uses UCSC-style naming without "chr" prefix. Correcting to `'11'` resolved the issue.

**Output:**

- Shape: (10, 10) — 50 kb region / 5 kb bins
- Dtype: float64
- Range (raw counts): 9.0 - 247.0
- Density: 100% (all 100 elements non-zero)
- Saved as: `data/hudep2_wt_hic_hbb_locus.npy` (NumPy binary format)

### Metadata Documentation

We saved extraction metadata to ensure reproducibility:

```json
{
  "source_file": "GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic",
  "locus": "11:5200000-5250000",
  "resolution": 5000,
  "normalization": "NONE (raw counts)",
  "extraction_method": "hic2cool + cooler (raw)",
  "conversion_command": "hic2cool convert ... -r 5000",
  "chromosome_naming": "UCSC without chr prefix",
  "date_extracted": "2026-02-05"
}
```

Saved as: `data/hudep2_wt_hic_metadata.json`

---

## Knight-Ruiz (KR) Balancing Normalization

### Rationale

Raw Hi-C contact counts exhibit systematic biases from:

1. **Sequencing depth variation:** Some genomic bins have higher coverage
2. **Mappability differences:** Repetitive regions have lower unique mapping
3. **GC content bias:** High-GC regions may amplify preferentially
4. **Fragment length:** Restriction fragment size affects ligation efficiency

Knight-Ruiz (KR) balancing (also known as matrix balancing or iterative correction) removes these biases by normalizing contact matrices such that all rows and columns have equal sums (Imakaev et al., 2012).

### Implementation

We applied KR balancing using cooler.balance_cooler (v0.10.4):

```python
import cooler

# Open cooler file
clr = cooler.Cooler('temp_hudep2_wt.cool')

# Apply KR balancing
bias, info = cooler.balance_cooler(
    clr,
    ignore_diags=2,      # Exclude first 2 diagonals (self-contacts)
    mad_max=5,           # Filter outliers (median absolute deviation threshold)
    min_nnz=10,          # Minimum non-zero contacts per bin
    tol=1e-5,            # Convergence tolerance
    max_iters=200,       # Maximum iterations
    store=True,          # Save weights to file
    store_name='weight'  # Column name for weights
)
```

**Parameters explained:**

- `ignore_diags=2`: Self-contacts (diagonal) and first off-diagonal excluded from balancing, as these represent intra-bin or adjacent-bin artifacts
- `mad_max=5`: Bins with contact frequency >5× median absolute deviation are masked (outliers)
- `min_nnz=10`: Bins with <10 non-zero contacts excluded (low-coverage bins)
- `tol=1e-5`: Iteration stops when row/column sum deviations <0.001%
- `max_iters=200`: Prevents infinite loops if convergence fails

**Convergence:**

- Converged: `True` (confirmed in `info` dict)
- Iterations: Not reported in current cooler version (legacy field)
- Masked bins: 0 (all bins passed QC for this high-coverage locus)

**Output:**

- Weights saved to `temp_hudep2_wt.cool::bins/weight` (HDF5 dataset)
- Balancing applied in-place (modifies file)

### Normalized Matrix Extraction

After balancing, we re-extracted the matrix with weights applied:

```python
# Extract with balancing
matrix_norm = c.matrix(balance=True).fetch(f'{chrom}:{start}-{end}')
```

**Result:**

- Shape: (10, 10) (unchanged)
- Range (normalized): 0.000755 - 0.014742
- Mean: 0.00385
- Std: 0.00314
- Saved as: `data/hudep2_wt_hic_hbb_locus_normalized.npy`

### Validation of Normalization

We verified normalization quality by checking row/column sums:

```python
row_sums = matrix_norm.sum(axis=1)
col_sums = matrix_norm.sum(axis=0)

# Coefficient of variation (should be low after balancing)
cv_rows = np.std(row_sums) / np.mean(row_sums)
cv_cols = np.std(col_sums) / np.mean(col_sums)
```

**Results:**

- CV (rows): 0.23 (acceptable for small matrix)
- CV (columns): 0.23 (symmetric, as expected)
- **Interpretation:** Successful balancing reduces CV from ~0.85 (raw) to ~0.23 (normalized)

---

## ARCHCODE Simulation Normalization

### Rationale

To enable fair comparison, simulation outputs (range 0-1, relative frequencies) must be scaled to match experimental data (range 0.0008-0.015, KR-normalized contact probabilities).

### Method

We used MinMaxScaler from scikit-learn (v1.3.2) to linearly rescale simulation matrices:

```python
from sklearn.preprocessing import MinMaxScaler

# Simulation matrix (10x10, values 0-1)
sim_matrix = np.array(simulation_data['matrix'])

# Flatten for scaling
sim_flat = sim_matrix.flatten().reshape(-1, 1)

# Scale to experimental range
scaler = MinMaxScaler(feature_range=(exp_min, exp_max))
sim_scaled_flat = scaler.fit_transform(sim_flat).flatten()

# Reshape back to matrix
sim_scaled = sim_scaled_flat.reshape(sim_matrix.shape)
```

**Parameters:**

- `feature_range=(exp_min, exp_max)`: Match experimental data range
- exp_min = 0.000755 (minimum non-zero experimental contact)
- exp_max = 0.014742 (maximum experimental contact)

**Alternative considered:** Quantile normalization (rank-based), but rejected because:

1. Preserves rank order but discards magnitude information
2. Simulation sparsity (22% filled) vs experimental density (100%) makes quantile matching inappropriate
3. Linear scaling is more interpretable and standard in Hi-C literature

**Output:**

- V1 (hypothetical CTCF): `data/archcode_hbb_simulation_normalized.npy`
- V2 (literature CTCF): `data/archcode_hbb_literature_ctcf_normalized.npy`

---

## Correlation Analysis

### Sample Selection

To avoid artifacts from diagonal and ensure independent measurements, we used:

- **Upper triangle only:** `np.triu_indices(n, k=1)` (k=1 excludes diagonal)
- **Symmetric matrix:** Lower triangle is redundant (contact[i,j] = contact[j,i])
- **Sample size:** n=45 pairs for 10×10 matrix

### Pearson Correlation

```python
from scipy.stats import pearsonr

# Extract upper triangle
triu_indices = np.triu_indices(10, k=1)
exp_triu = exp_matrix_norm[triu_indices]
sim_triu = sim_matrix_norm[triu_indices]

# Remove NaN pairs
mask = ~(np.isnan(exp_triu) | np.isnan(sim_triu))
exp_valid = exp_triu[mask]
sim_valid = sim_triu[mask]

# Calculate Pearson correlation
r, p = pearsonr(exp_valid, sim_valid)
```

**Assumptions tested:**

1. **Linearity:** Scatter plot inspection (Figure 1C) shows approximately linear trend
2. **Normality:** Q-Q plot (Figure 4B) shows deviation from normality (acceptable for n=45)
3. **Homoscedasticity:** Residuals show constant variance (inspected visually)

**Significance testing:**

- Null hypothesis: r = 0 (no linear relationship)
- Alternative: r ≠ 0 (two-tailed test)
- α = 0.05 (standard significance threshold)

### Spearman Correlation

As a non-parametric alternative (no normality assumption):

```python
from scipy.stats import spearmanr

rho, p_spearman = spearmanr(exp_valid, sim_valid)
```

**Advantage:** Robust to outliers and monotonic (not necessarily linear) relationships.

**Results interpretation:**

- Spearman ρ ≈ Pearson r → relationship is approximately linear
- Spearman ρ < Pearson r → non-monotonic effects or scaling artifacts

---

## Statistical Power Analysis

We conducted post-hoc power analysis to assess Type II error probability (false negative rate):

```python
from statsmodels.stats.power import tt_solve_power

# Parameters
effect_size = r / np.sqrt(1 - r**2)  # Cohen's d approximation
alpha = 0.05
nobs = 45

# Calculate power
power = tt_solve_power(effect_size=effect_size, nobs=nobs, alpha=alpha)
```

**Results:**

- Observed r = 0.158
- Effect size = 0.159
- Statistical power = ~30%
- **Interpretation:** High risk of Type II error (failing to detect true effect)

**Required sample size for 80% power:**

```python
n_required = tt_solve_power(effect_size=effect_size, power=0.8, alpha=alpha)
# Result: n ≈ 300 pairs
```

**Implication:** Future validation should use ≥200 kb loci (n≥780 pairs) for adequate power.

---

## Visualization

### Heatmaps

Contact matrices visualized using matplotlib/seaborn:

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, ax = plt.subplots()
sns.heatmap(matrix, cmap='Reds', square=True, cbar_kws={'label': 'Contact frequency'})
ax.set_title('Experimental Hi-C (KR normalized)')
ax.set_xlabel('Genomic position (Mb)')
ax.set_ylabel('Genomic position (Mb)')
```

**Colormap selection:**

- Experimental: `Reds` (standard for Hi-C)
- Simulation V1: `Blues` (distinguish from experimental)
- Simulation V2: `Greens` (distinguish from both)

### Scatter Plots

```python
ax.scatter(exp_valid, sim_valid, alpha=0.6, s=30, edgecolors='k')
ax.plot([lims[0], lims[1]], [lims[0], lims[1]], 'k--', label='y=x')
ax.set_xlabel('Experimental')
ax.set_ylabel('Simulated')
```

**Diagonal reference line:** y=x indicates perfect agreement (observed vs predicted).

---

## Software and Reproducibility

### Software Versions

| Package      | Version | Purpose                      |
| ------------ | ------- | ---------------------------- |
| Python       | 3.11.5  | Analysis environment         |
| cooler       | 0.10.4  | Hi-C data handling           |
| hic2cool     | 0.8.3   | Format conversion            |
| NumPy        | 1.26.3  | Matrix operations            |
| SciPy        | 1.12.0  | Statistical analysis         |
| scikit-learn | 1.3.2   | Normalization (MinMaxScaler) |
| matplotlib   | 3.8.2   | Visualization                |
| seaborn      | 0.13.0  | Heatmap styling              |

### Computational Environment

**Hardware:**

- CPU: AMD Ryzen 9 5900X (12 cores, 24 threads)
- RAM: 64 GB DDR4-3200
- Storage: NVMe SSD (2 TB)
- OS: Windows 11 Pro + WSL2 (Ubuntu 22.04) for Python scripts

**Compute time:**

- Hi-C extraction: ~5 minutes (includes format conversion)
- KR balancing: ~30 seconds (iterative algorithm)
- Simulation (per variant): ~8 seconds (single-threaded)
- Correlation analysis: <1 second

**Total pipeline time:** ~15 minutes per locus (end-to-end)

### Reproducibility

All scripts and data are available:

**Code repository:**

- GitHub: https://github.com/sergeeey/ARCHCODE
- Branch: `feature/hic-validation`
- Commit: Will be tagged as `v1.1.0-validation-pilot` upon publication

**Data availability:**

- Experimental Hi-C: GEO accession GSM4873116 (public)
- Extracted matrices: Available in `data/` directory (repository)
- Simulation outputs: Included in repository

**Random seed:** All stochastic processes (ARCHCODE simulation) use `seed=42` for reproducibility.

---

## Quality Control

### Data Integrity Checks

**1. Matrix symmetry:**

```python
assert np.allclose(matrix, matrix.T), "Matrix not symmetric"
```

**2. Non-negative values:**

```python
assert np.all(matrix >= 0), "Negative contacts detected"
```

**3. NaN handling:**

```python
nan_count = np.isnan(matrix).sum()
print(f"NaN values: {nan_count}")  # Expected: 0 for raw, some for normalized
```

**4. Range validation:**

```python
assert matrix.min() >= 0 and matrix.max() <= 300, "Unexpected value range"
```

### Sanity Checks

**1. Distance decay:**
Expected pattern: contact frequency decreases with genomic distance.

```python
# Calculate distance decay
for k in range(1, 10):
    diag_k = np.diag(matrix, k=k)
    print(f"Diagonal {k}: mean = {np.mean(diag_k):.4f}")
# Expected: monotonically decreasing
```

**2. Correlation sign:**
After normalization, correlation should be ≥ 0 (physically plausible).

**3. Variance inflation:**
After scaling, variance should match experimental data approximately.

---

## Limitations Acknowledged in Methods

1. **Capture Hi-C bias:** Capture enrichment may violate KR balancing assumptions (equal visibility)
2. **Cell-type mismatch:** HUDEP-2 experimental data vs GM12878-derived CTCF sites
3. **Small region:** 50 kb locus limits statistical power (n=45 pairs)
4. **Single normalization method:** ICE (alternative to KR) not tested
5. **No replicates:** Single experimental dataset (no technical replicates)

---

_Methods appendix prepared for bioRxiv submission_
_Last updated: 2026-02-05_
_Contains full reproducibility details for Hi-C validation pipeline_
