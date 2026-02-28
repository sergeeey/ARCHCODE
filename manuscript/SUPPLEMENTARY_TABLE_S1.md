# Supplementary Table S1: Comprehensive Analysis of 353 HBB Pathogenic Variants

## Table Legend

Complete dataset of 353 β-globin (_HBB_) pathogenic and VUS variants analyzed using
ARCHCODE (physics-based 3D chromatin simulation) and Ensembl VEP (sequence-based predictor).
Variants are sorted by genomic position (chr11, GRCh38).

**Columns:**

1. **ClinVar_ID**: ClinVar accession (VCV format)
2. **Position**: Genomic coordinate on chr11 (GRCh38/hg38)
3. **Category**: Variant functional category (VEP annotation)
   - `splice_donor`, `splice_acceptor`: ±2 bp from exon boundary
   - `splice_region`: ±8 bp from exon boundary
   - `missense`, `nonsense`, `frameshift`: Coding sequence variants
   - `promoter`: -2000 to +200 bp from TSS
   - `5_prime_UTR`, `3_prime_UTR`, `intronic`: Non-coding variants
4. **ARCHCODE_SSIM**: Structural Similarity Index (WT vs Mutant contact matrices)
   - Range: [0,1], higher = more similar to WT (less structural disruption)
   - Thresholds: <0.85 PATHOGENIC, 0.85-0.92 LIKELY_PATHOGENIC, 0.92-0.96 VUS,
     0.96-0.99 LIKELY_BENIGN, ≥0.99 BENIGN
5. **VEP_Score**: Ensembl VEP SIFT/PolyPhen-2 composite pathogenicity score
   - Range: [0,1], higher = more pathogenic
   - Thresholds: ≥0.5 pathogenic, <0.5 non-pathogenic
6. **ARCHCODE_Verdict**: Classification based on SSIM
7. **VEP_Verdict**: Classification based on VEP score
8. **Discordant**: YES if verdicts differ between methods (pathogenic vs benign/VUS), NO otherwise

**Key Findings:**

- **Total variants:** 353
- **Discordant:** cases where ARCHCODE structural signature diverges from VEP sequence prediction
- **Pearl variants:** chromatin-structural outliers with high clinical reclassification potential
  - See "Pearl Variants" section below

---

## Full Dataset

_Note: Due to size constraints, the full table is provided as a separate CSV file:
`HBB_Clinical_Atlas_REAL.csv`_

### Summary Statistics by Category

| Category        | N   | Mean SSIM | Mean VEP Score | % Discordant |
| --------------- | --- | --------- | -------------- | ------------ |
| nonsense        | 40  | 0.8753    | 0.90           | low          |
| frameshift      | 99  | 0.8919    | 0.90           | low          |
| splice_acceptor | 3   | 0.9019    | 0.95           | moderate     |
| splice_donor    | 22  | 0.9087    | 0.95           | moderate     |
| promoter        | 15  | 0.9285    | 0.20           | HIGH         |
| missense        | 125 | 0.9526    | ~0.70          | HIGH         |
| splice_region   | 9   | 0.9641    | 0.50           | moderate     |
| other           | 12  | 0.9676    | varies         | moderate     |
| 5_prime_UTR     | 3   | 0.9801    | 0.20           | moderate     |
| 3_prime_UTR     | 13  | 0.9942    | 0.15           | low          |
| intronic        | 9   | 0.9957    | 0.10           | low          |
| synonymous      | 3   | 0.9989    | 0.05           | low          |

**Interpretation:** `promoter` and `missense` categories show highest discordance rates,
suggesting these variant classes exhibit structural mechanisms detected by ARCHCODE that
are not captured by sequence-based predictors (VEP).

---

### Pearl Variants: Chromatin-Structural Outliers

Variants where ARCHCODE structural signature diverges from VEP sequence prediction,
flagged for clinical reclassification review:

| ClinVar_ID       | Position | Category        | SSIM  | VEP Score | Pearl |
| ---------------- | -------- | --------------- | ----- | --------- | ----- |
| **VCV002024192** | 5226796  | splice_acceptor | 0.900 | 0.20      | YES   |
| **VCV000869358** | 5226971  | frameshift      | 0.891 | 0.15      | YES   |
| **VCV000015471** | 5227099  | promoter        | 0.928 | 0.20      | YES   |
| **VCV002664746** | 5226613  | missense        | 0.949 | 0.20      | YES   |
| **VCV000811500** | 5226613  | missense        | 0.949 | 0.20      | YES   |

**Pearl variant definition:** ARCHCODE SSIM in VUS/LIKELY_BENIGN range (0.88-0.96)
combined with VEP score <0.5 (predicted non-pathogenic), where ClinVar clinical
significance is Pathogenic or Likely Pathogenic. These represent cases where
chromatin topology provides orthogonal evidence to sequence-based classifiers.

**Clinical relevance:** Pearl variants are candidates for ACMG criteria upgrade under
PS3_moderate (functional evidence of structural disruption from ARCHCODE simulation)
combined with existing pathogenic classifications.

---

## Data Availability

**Full dataset:** `HBB_Clinical_Atlas_REAL.csv` (353 rows × 8 columns)

**Format:** Comma-separated values (CSV), UTF-8 encoding

**Download:** Available from corresponding author upon reasonable request or from
GitHub repository (https://github.com/sergeeey/ARCHCODE/tree/main/results)

---

## Methods Summary

**ARCHCODE simulation:**

- Physics-based loop extrusion with Kramer kinetics (α=0.92, γ=0.80;
  MANUALLY CALIBRATED to literature ranges, not fitted to experimental data)
- Analytical contact matrix computation (SSIM calculated on WT vs Mutant matrices)
- Seed=2026 for reproducibility

**VEP prediction:**

- Ensembl Variant Effect Predictor v112 (https://www.ensembl.org/vep)
- SIFT and PolyPhen-2 scores combined as composite pathogenicity metric
- Annotation genome assembly: GRCh38
- Variant consequence classification per Sequence Ontology terms

**Statistical analysis:**

- ACMG/AMP 2015 guidelines for clinical interpretation
- Discordance defined as ARCHCODE structural verdict vs VEP sequence verdict disagreement
- Pearl variant flagging: SSIM 0.88-0.96 AND VEP score <0.5 AND ClinVar = Pathogenic/LP

---

_Supplementary Table S1 prepared for bioRxiv submission_
_Last updated: 2026-02-28_
_Corresponding author: Sergey V. Boyko (sergeikuch80@gmail.com)_
