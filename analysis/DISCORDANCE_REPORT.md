# ARCHCODE Discordance Analysis Report
## Date: 2026-03-09

## Key Finding

ARCHCODE captures a mechanistically distinct axis of pathogenicity: enhancer-proximal structural disruption invisible to VEP/CADD.

## 2×2 Matrix Results

Thresholds: LSSIM < 0.95 (structural), VEP >= 0.5 or CADD >= 20 (sequence)

Quadrant,N_Total,N_Pathogenic,N_Benign,Precision,Pct_Dataset,Mean_Enhancer_Dist,Top3_Categories
Q1,270,270,0,1.0,0.89,543.0,"frameshift(98), missense(88), nonsense(53)"
Q2,261,231,30,0.8851,0.86,620.0,"frameshift(204), other(32), promoter(15)"
Q3,10385,8666,1681,0.8345,34.25,25138.0,"synonymous(8187), intronic(1670), missense(414)"
Q4,19402,8021,10669,0.4134,63.99,26749.0,"synonymous(6930), frameshift(5661), intronic(4329)"


Total variants: 30318

## Q2 Structural Blind Spots

- **N total:** 261
- **N pathogenic:** 231
- **N benign:** 30
- **Mean enhancer distance:** 620 bp (Q3: 25138 bp)
- **Mann-Whitney U (Q2 < Q3):** p=3.37e-129
- **Dominant loci:** BRCA1, MLH1, CFTR
- **Dominant categories:** frameshift, other, promoter
- **Pearl overlap:** 50/261

## Q3 Sequence Channel

- **N total:** 10385
- **Dominant categories:** synonymous, intronic, missense
- **Mean enhancer distance:** 25138 bp (vs Q2: 620 bp)

## Tissue Specificity

Locus,N_Total,N_Q2,N_Q3,Q2_Ratio,Tissue_Match
HBB,1103,25,75,0.0227,1.0
BRCA1,10682,79,4067,0.0074,0.5
TP53,2794,4,1105,0.0014,0.5
CFTR,3349,36,1121,0.0107,0.0
MLH1,4060,72,1243,0.0177,0.5
LDLR,3284,10,1442,0.003,0.0
SCN5A,2488,0,694,0.0,0.0
TERT,2089,35,414,0.0168,0.5
GJB2,469,0,224,0.0,0.0


- **Spearman r (Q2_Ratio vs Tissue_Match):** 0.697
- **p-value:** 0.0370

## NMI Validation

- ARCHCODE vs VEP: 0.0022 (paper: 0.101, diff: 0.0988)
- ARCHCODE vs CADD: 0.2457 (paper: 0.024, diff: 0.2217)
- VEP vs CADD: 0.0124 (paper: 0.231, diff: 0.2186)

Full NMI results:
{
  "ARCHCODE_vs_VEP": 0.0022,
  "ARCHCODE_vs_CADD": 0.2457,
  "VEP_vs_CADD": 0.0124,
  "ARCHCODE_vs_ClinVar": 0.0168,
  "VEP_vs_ClinVar": 0.1315
}

## Hypothesis B Status

**GO**

Criteria met:
1. Enhancer proximity Q2 < Q3: PASS (p=3.37e-129)
2. Tissue specificity correlation: PASS (rho=0.697, p=0.0370)
3. Sufficient Q2 variants: PASS (n=261)

## Next Steps

1. Integrate Q2 list into manuscript as Table N (Structural Blind Spots)
2. Build per-locus Q2 case studies (HBB pearls as anchor)
3. Submit discordance figure to bioRxiv revision
