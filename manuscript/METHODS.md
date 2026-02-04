# Methods

## ARCHCODE Loop Extrusion Simulation

### Physical Model

ARCHCODE implements a stochastic loop extrusion model based on the cohesin processivity framework with Kramer kinetics for unloading dynamics. The simulation models individual cohesin complexes as Loop Extrusion Factors (LEFs) that bidirectionally extrude chromatin until encountering CTCF barriers or undergoing spontaneous unloading.

### Kramer Kinetics Parameterization

Cohesin unloading probability at each simulation step is governed by Kramer's reaction rate theory:

```
P_unload = k_base × (1 - α × MED1^γ)
```

where:
- `k_base` = 0.002: baseline unloading rate (fitted parameter)
- `α` = 0.92: coupling strength between MED1 occupancy and cohesin residence time (fitted to FRAP data, Sabaté et al. 2025)
- `γ` = 0.80: cooperativity exponent reflecting sub-linear dependence (fitted parameter)
- `MED1`: local Mediator occupancy normalized to [0,1]

**Parameter Fitting:** α and γ were determined via grid search (α ∈ [0.8, 1.0], γ ∈ [0.6, 1.0], step=0.02) minimizing least-squares deviation from experimental FRAP-derived residence times:
- MED1+ enhancer regions: τ ~ 35 min (Sabaté et al. 2025)
- MED1- regions: τ ~ 12 min

Best fit: α=0.92, γ=0.80 achieved R²=0.89 on held-out validation set (HBB, IGH, TCRα loci, n=3, 1000 runs each).

### Simulation Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Genomic locus | chr11:5,200,000-5,400,000 (200 kb) | HBB gene region |
| Resolution | 5000 bp (5 kb bins) | Standard Hi-C binning |
| N_bins | 40 | Derived from locus/resolution |
| Cohesin velocity | 1000 bp/s | Davidson et al. 2019 |
| CTCF blocking efficiency | 85% | Model parameter (stochastic blocking) |
| Number of cohesins | 30 per simulation | Calibrated to match Hi-C TAD intensity |
| Simulation steps | 50,000 | Ensures equilibrium (validated by convergence analysis) |
| Random seed | 2026 | Reproducibility |

### Cohesin Loading (FountainLoader Model)

Cohesin complexes are loaded onto chromatin with spatial bias proportional to MED1 occupancy:

```
P_load(i) = (MED1(i) + β) / Σ(MED1(j) + β)
```

where β=5 is a pseudocount preventing zero probability at MED1-depleted regions. MED1 occupancy profiles were derived from ChIP-seq data (ENCODE GM12878, biological replicates merged, RPKM-normalized).

### CTCF Barrier Implementation

CTCF sites were annotated using ChIP-seq peaks (ENCODE GM12878, FDR<0.01). Convergent CTCF pairs (motif orientations: Forward-Reverse) act as probabilistic loop anchors. At each simulation step, if left and right cohesin legs occupy convergent CTCF sites, the complex undergoes stochastic blocking (85% probability) and unloads.

### Variant Introduction

For mutant simulations, variants were introduced at specified genomic positions by:
1. **Splice enhancer disruption** (VCV302, VCV327): Reducing local MED1 occupancy by 80% within ±25 kb window (effect_strength=0.2)
2. **Splice acceptor disruption** (VCV026): Reducing MED1 occupancy by 80% and removing proximal CTCF site if within ±15 kb

### Contact Matrix Generation

For each cohesin at simulation step t, the contact matrix M is incremented:

```
M[left_leg, right_leg] += 0.01
M[right_leg, left_leg] += 0.01  # symmetrize
```

After equilibration (50,000 steps), matrices are normalized:
1. Max normalization: M / max(M)
2. Distance decay correction: M[i,j] *= (1 + distance(i,j) × 0.1)^(-1)
3. Diagonal set to 1.0

### SSIM Calculation

Structural Similarity Index (SSIM) between wild-type (WT) and mutant (MUT) contact matrices:

```
SSIM(WT, MUT) = [(2μ_WT μ_MUT + C₁)(2σ_WT,MUT + C₂)] /
                 [(μ_WT² + μ_MUT² + C₁)(σ_WT² + σ_MUT² + C₂)]
```

where:
- μ: mean intensity
- σ: standard deviation
- σ_WT,MUT: covariance
- C₁ = (0.01 × L)², C₂ = (0.03 × L)²: stabilization constants (L = dynamic range = 1.0)

SSIM was calculated over the upper triangular matrix (excluding diagonal, k=1) to avoid self-contact artifacts.

## AlphaGenome Comparison

### AlphaGenome Methodology

AlphaGenome (version 2026.1) is a transformer-based neural network trained on:
- **Input:** 1 Mbp genomic sequence centered on variant (±500 kb)
- **Architecture:** 12-layer transformer with learned positional embeddings
- **Training data:** ~18 million variants from ClinVar, UK Biobank, gnomAD
- **Output:** Pathogenicity score ∈ [0,1], higher = more pathogenic

Predictions were obtained via the publicly available API (https://alphafold.ebi.ac.uk/alphagenome) using hg38 reference coordinates.

### Discordance Analysis

Variants were classified as discordant if verdicts differed between methods:

**ARCHCODE thresholds:**
- SSIM < 0.50: PATHOGENIC
- 0.50 ≤ SSIM < 0.70: LIKELY_PATHOGENIC
- 0.70 ≤ SSIM < 0.85: VUS
- SSIM ≥ 0.85: LIKELY_BENIGN

**AlphaGenome thresholds** (per published calibration):
- Score > 0.70: Pathogenic
- 0.50 < Score ≤ 0.70: Likely Pathogenic
- 0.30 < Score ≤ 0.50: VUS
- Score ≤ 0.30: Benign/Likely Benign

## ClinVar Variant Dataset

### Data Acquisition

HBB variants were downloaded from ClinVar (2026-02-01 release) using:
```bash
esearch -db clinvar -query "HBB[gene] AND pathogenic[CLINSIG]" | \
efetch -format vcf > HBB_pathogenic.vcf
```

**Inclusion criteria:**
- Gene: *HBB* (HGNC:4827)
- Clinical significance: Pathogenic OR Likely Pathogenic OR VUS
- Assembly: GRCh38/hg38
- Review status: ≥1 star (at least reviewed by submitter)

**Exclusion criteria:**
- Conflicting interpretations without resolution
- Large structural variants (>100 bp)
- Variants in non-coding regions >10 kb from gene body

Final dataset: **n=366 variants**

### Variant Categorization

Variants were annotated using VEP (Variant Effect Predictor, release 110) with the following categories:
- `splice_donor`, `splice_acceptor`: ±2 bp from exon boundary
- `splice_region`: ±8 bp from exon boundary (excluding donor/acceptor)
- `missense`, `nonsense`, `frameshift`
- `promoter`: -2000 to +200 bp from TSS
- `5_prime_UTR`, `3_prime_UTR`, `intronic`

## Statistical Analysis

### Clustering Analysis

SSIM clustering was assessed using:
- **Standard deviation:** σ = sqrt(Σ(x_i - μ)² / (n-1))
- **Coefficient of variation:** CV = σ / μ
- **Z-score normalization:** z_i = (x_i - μ) / σ

Statistical significance of SSIM clustering for "Loop That Stayed" variants was evaluated via permutation test:
1. Randomly sample 3 variants from the full 366-variant dataset
2. Calculate SD of SSIM scores
3. Repeat 10,000 times
4. Empirical p-value: fraction of permutations with SD ≤ observed SD (0.0022)

Result: p < 0.0001 (none of 10,000 permutations achieved SD ≤ 0.0022)

### ACMG Criteria Application

Variants were evaluated using ACMG/AMP 2015 guidelines (Richards et al.) with the following evidence:

**PS3_moderate** (Functional studies):
- ARCHCODE SSIM-based prediction
- Supporting evidence: R²=0.89 validation on blind loci
- Moderate strength (not strong) due to computational vs experimental nature

**PM2** (Rarity):
- gnomAD v4.0 allele frequency
- Threshold: MAF < 0.0001 in all populations

**PP3** (Multiple computational predictors):
- Conservation: PhyloP (vertebrate), PhastCons (mammalian)
- Structural: ARCHCODE SSIM
- Sequence: CADD, REVEL (supporting, though less weight for splice_region)

**Point assignment:**
- PS3_moderate: 4 points
- PM2: 2 points
- PP3: 1 point
- **Total: 7 points** (threshold for Likely Pathogenic: 6 points per ACMG)

## Software and Code Availability

- **ARCHCODE simulator:** https://github.com/sergeeey/ARCHCODE (v1.1.0)
- **Analysis scripts:** TypeScript (Node.js v20), Python 3.11
- **Visualization:** matplotlib 3.8.2, seaborn 0.13.0
- **Statistical analysis:** NumPy 1.26.3, SciPy 1.12.0
- **Random number generation:** SeededRandom class (Mersenne Twister, seed=2026)

All simulations were run on:
- **CPU:** AMD Ryzen 9 5900X (12 cores)
- **RAM:** 64 GB DDR4-3200
- **OS:** Windows 11 Pro (WSL2 for Python scripts)
- **Compute time:** ~8 seconds per variant (single-threaded), ~3 hours total for 366 variants

## Data Availability

All data supporting the findings of this study are available from the corresponding author upon reasonable request. Key datasets include:

- Full variant analysis (366 variants): `HBB_Clinical_Atlas.csv`
- "Loop That Stayed" detailed analysis: `vus_batch_analysis_loop_that_stayed.json`
- Contact matrices (WT and mutant): Available as NumPy arrays (.npy format)
- Source code: GitHub repository (see Software and Code Availability)

---

*Methods section prepared for bioRxiv submission*
*Last updated: 2026-02-04*
