# Methods

## ARCHCODE Loop Extrusion Simulation

### Physical Model

ARCHCODE implements an analytical mean-field loop extrusion model based on the cohesin processivity framework with Kramer kinetics for unloading dynamics. The model computes contact probabilities analytically by combining distance decay, local chromatin occupancy, CTCF barrier permeability, and Kramer-modulated cohesin residence, without stochastic Monte Carlo sampling.

### Kramer Kinetics Parameterization

Cohesin unloading probability at each simulation step is governed by Kramer's reaction rate theory:

```
P_unload = k_base × (1 - α × MED1^γ)
```

where:

- `k_base` = 0.002: baseline unloading rate (calibrated parameter)
- `α` = 0.92: coupling strength between MED1 occupancy and cohesin residence time (estimated from literature ranges; Gerlich et al. 2006; Hansen et al. 2017)
- `γ` = 0.80: cooperativity exponent reflecting sub-linear dependence (estimated from literature ranges; Gerlich et al. 2006; Hansen et al. 2017)
- `MED1`: local Mediator occupancy normalized to [0,1]

**Parameter Calibration:** α=0.92 and γ=0.80 were estimated from literature ranges (Gerlich et al. 2006; Hansen et al. 2017) and manually calibrated to reproduce qualitatively reasonable cohesin residence-time behaviour:

- MED1+ enhancer regions: τ ~ 35 min (Gerlich et al. 2006)
- MED1- regions: τ ~ 12 min

No formal fitting to FRAP data was performed. No FRAP measurements are available in this study. Parameter values should be regarded as manually calibrated estimates consistent with published residence-time ranges.

### Simulation Parameters

| Parameter                  | Value                                     | Source                                               |
| -------------------------- | ----------------------------------------- | ---------------------------------------------------- |
| Genomic locus              | chr11:5,210,000-5,240,000 (30 kb)         | HBB gene region                                      |
| Resolution                 | 600 bp                                    | Analytical bin size                                  |
| N_bins                     | 50                                        | Derived from locus/resolution                        |
| Cohesin velocity           | 1000 bp/s                                 | Davidson et al. 2019                                 |
| CTCF sites                 | 6                                         | Annotated from ENCODE GM12878 peaks                  |
| Enhancer/occupancy regions | 5                                         | Annotated from ChIP-seq data                         |
| Number of cohesins         | 10                                        | Calibrated to reproduce TAD-scale contact enrichment |
| Simulation steps           | N/A                                       | Analytical mean-field; no stochastic steps required  |
| Method                     | Analytical mean-field contact computation | No Monte Carlo sampling                              |

### Cohesin Loading (FountainLoader Model)

Cohesin complexes are loaded onto chromatin with spatial bias proportional to MED1 occupancy:

```
P_load(i) = (MED1(i) + β) / Σ(MED1(j) + β)
```

where β=5 is a pseudocount preventing zero probability at MED1-depleted regions. MED1 occupancy profiles were derived from ChIP-seq data (ENCODE GM12878, biological replicates merged, RPKM-normalized).

### CTCF Barrier Implementation

CTCF sites were annotated using ChIP-seq peaks (ENCODE GM12878, FDR<0.01). Convergent CTCF pairs (motif orientations: Forward-Reverse) act as loop anchors in the analytical model. Each CTCF site is assigned a permeability value (default 0.15, i.e. 85% barrier strength) that enters the contact formula as a multiplicative factor reducing contact probability across the barrier.

### Variant Introduction

Variants modulate the local chromatin occupancy profile used in the analytical contact computation. Each variant category is assigned a functional impact strength that scales the reduction in local occupancy:

- **Nonsense / frameshift** (highest impact): occupancy reduced by 70–90% at the affected bin
- **Splice donor / splice acceptor**: occupancy reduced by 60–80%; proximal CTCF permeability may also be modified
- **Missense / splice region**: occupancy reduced by 20–50% depending on predicted severity
- **Synonymous / intronic / UTR**: minimal or no occupancy change (< 5%)

Categories with larger functional impact produce stronger reductions in occupancy factors, which propagate through the contact formula (see Contact Matrix Generation below) to yield lower SSIM values relative to the wild-type reference.

### Contact Matrix Generation

Contact probabilities are computed analytically using a mean-field formula that combines four factors:

```
C(i,j) = |i-j|^(-1) × sqrt(occ_i × occ_j) × Π(ctcf_permeability) × kramer_modulation(i,j)
```

where:

- `|i-j|^(-1)`: genomic distance decay (polymer scaling)
- `sqrt(occ_i × occ_j)`: geometric mean of chromatin occupancy at bins i and j
- `Π(ctcf_permeability)`: product of CTCF barrier permeability values for all sites between i and j
- `kramer_modulation(i,j)`: factor derived from Kramer kinetics applied to the mean occupancy between i and j

The resulting matrix is symmetric (C(i,j) = C(j,i)) and max-normalised so that values lie in [0, 1]. The diagonal is set to 1.0. No Monte Carlo steps are required.

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

## Ensembl VEP Comparison

### VEP Methodology

Sequence-level pathogenicity predictions were obtained using the Ensembl Variant Effect Predictor (VEP) v113 REST API:

```
POST https://rest.ensembl.org/vep/homo_sapiens/region
```

Variants were submitted in batch mode (200 variants per request) with hg38 reference coordinates. Each response was parsed for the most severe consequence and, where available, SIFT scores for missense variants.

**Consequence severity mapping** (consequence term → pathogenicity score):

| Consequence                                                                    | Score                         |
| ------------------------------------------------------------------------------ | ----------------------------- |
| stop_gained, frameshift_variant, splice_donor_variant, splice_acceptor_variant | 0.95                          |
| missense_variant                                                               | derived from SIFT (see below) |
| splice_region_variant                                                          | 0.60                          |
| synonymous_variant, 5_prime_UTR_variant, 3_prime_UTR_variant, intron_variant   | 0.10                          |
| intergenic_variant                                                             | 0.05                          |
| other / unmapped                                                               | 0.50                          |

**SIFT integration for missense variants:**

```
vep_score = 0.4 + 0.5 × (1 − sift_score)
```

where `sift_score` ∈ [0, 1] (0 = deleterious, 1 = tolerated). If SIFT was unavailable, missense variants received a default score of 0.70.

**Pearl detection threshold:** a variant was flagged as a Pearl (ARCHCODE-VEP discordant case) when VEP score < 0.30 AND SSIM < 0.95.

**Methodological note on sequence-based predictor choice:** VEP was used as the sequence-based comparator because the SpliceAI Lookup API (Broad Institute) was unreachable during data collection (connection timeout). VEP and SpliceAI measure different aspects of sequence-level pathogenicity: VEP classifies variant consequences and integrates SIFT for missense deleteriousness, whereas SpliceAI specifically predicts splice junction disruption via deep learning (Jaganathan et al., 2019). Consequently, "VEP-blind" (low VEP score) is not equivalent to "SpliceAI-blind" — a variant classified as low-impact by VEP's consequence hierarchy (e.g., upstream_gene_variant → 0.15) might still receive a high SpliceAI delta score if it disrupts a cryptic splice site. The pearl variants identified in this study should therefore be interpreted as "low VEP consequence impact with structural disruption," not as universally invisible to all sequence-based tools. Replication with SpliceAI is recommended when API access becomes available.

### Discordance Analysis

Variants were classified as discordant if verdicts differed between methods:

**ARCHCODE thresholds (analytical mean-field calibration):**

- SSIM < 0.85: PATHOGENIC
- 0.85 ≤ SSIM < 0.92: LIKELY_PATHOGENIC
- 0.92 ≤ SSIM < 0.96: VUS
- 0.96 ≤ SSIM < 0.99: LIKELY_BENIGN
- SSIM ≥ 0.99: BENIGN

**VEP thresholds:**

- Score ≥ 0.50: Pathogenic / Likely Pathogenic
- Score < 0.50: Benign / Likely Benign / VUS

## ClinVar Variant Dataset

### Data Acquisition

HBB variants were downloaded from ClinVar (2026-02-01 release) via the NCBI E-utilities API (esearch + esummary endpoints), querying for gene HBB with clinical significance Pathogenic, Likely Pathogenic, or VUS on GRCh38/hg38 assembly.

**Inclusion criteria:**

- Gene: _HBB_ (HGNC:4827)
- Clinical significance: Pathogenic OR Likely Pathogenic OR VUS
- Assembly: GRCh38/hg38
- Review status: ≥1 star (at least reviewed by submitter)
- Parseable ref/alt alleles (single-base substitutions, small insertions/deletions)

**Exclusion criteria:**

- Complex indels without parseable ref/alt alleles (n=78 excluded)
- Large structural variants (>100 bp)
- Variants in non-coding regions >10 kb from gene body

Total downloaded: **431 variants**; after exclusion of 78 complex indels: **Final dataset: n=353 variants**

### Variant Categorization

Variants were annotated using VEP v113 REST API with the following categories and counts:

| Category        | n       |
| --------------- | ------- |
| missense        | 125     |
| frameshift      | 99      |
| nonsense        | 40      |
| splice_donor    | 22      |
| promoter        | 15      |
| 3_prime_UTR     | 13      |
| other           | 12      |
| splice_region   | 9       |
| intronic        | 9       |
| 5_prime_UTR     | 3       |
| splice_acceptor | 3       |
| synonymous      | 3       |
| **Total**       | **353** |

Category definitions:

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

1. Randomly sample 3 variants from the full 353-variant dataset
2. Calculate SD of SSIM scores
3. Repeat 10,000 times
4. Empirical p-value: fraction of permutations with SD ≤ observed SD (0.0022)

Result: p < 0.0001 (none of 10,000 permutations achieved SD ≤ 0.0022)

### ACMG Criteria Application

Variants were evaluated using ACMG/AMP 2015 guidelines (Richards et al.) with the following evidence:

**PS3_moderate** (Functional studies):

- ARCHCODE SSIM-based prediction (analytical mean-field model)
- Supporting evidence: qualitative consistency with published cohesin dynamics; no formal R² validation against experimental data is available
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
- **Visualization:** matplotlib 3.8.2
- **Statistical analysis:** NumPy 1.26.3, SciPy 1.12.0
- **Random number generation:** SeededRandom class (Mersenne Twister, seed=2026)

All simulations were run on:

- **CPU:** AMD Ryzen 9 5900X (12 cores)
- **RAM:** 64 GB DDR4-3200
- **OS:** Windows 11 Pro (WSL2 for Python scripts)
- **Compute time:** < 1 second per variant (analytical approach), ~5 minutes total for 353 variants

## Data Availability

All data supporting the findings of this study are available from the corresponding author upon reasonable request. Key datasets include:

- Full variant analysis (353 variants): `HBB_Clinical_Atlas_REAL.csv`
- Pearl analysis summary: `REAL_ATLAS_SUMMARY.json`
- VEP sequence-level predictions: `hbb_vep_results.csv`
- Contact matrices (WT and mutant): Available as NumPy arrays (.npy format)
- Source code: GitHub repository (see Software and Code Availability)

---

_Methods section prepared for bioRxiv submission_
_Last updated: 2026-02-28_
