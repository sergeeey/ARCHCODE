# ARCHCODE Blind Spot Benchmark v1.0

**Generated:** 2026-03-07

## Overview

This benchmark dataset evaluates the ability of variant effect predictors to detect
structural variants that are invisible to sequence-based methods.

## Pearl Definition

A "pearl" variant meets all criteria:
- **VEP score < 0.30** (sequence-blind)
- **LSSIM < 0.95** (structurally disruptive)
- **ClinVar: Pathogenic or Likely Pathogenic**

## Statistics

| Metric | Value |
|--------|-------|
| Total variants | 353 |
| Total pearls | 15 |
| Blind spot detection rate | 76.77% |

## Quadrant Distribution

| Quadrant | Description | Count |
|----------|-------------|-------|
| Q1 | Both detect | 15 |
| Q2 | ARCHCODE only (pearls) | 274 |
| Q3 | VEP only | 753 |
| Q4 | Neither | 61 |

## Pearls by Locus

### HBB (15 pearls)

- VCV002664746: c.279C>G (LSSIM=0.9166, VEP=0.2)
- VCV000811500: c.279C>A (LSSIM=0.9173, VEP=0.2)
- VCV000015208: c.279C>R (LSSIM=0.9492, VEP=0.2)
- VCV000618675: c.249G>C (LSSIM=0.9159, VEP=0.2)
- VCV002024192: NM_000518.5(HBB):c.93-33_96delinsACTGTCCCTTGGGCTGTTTTCCTACCCTCAGATTA (LSSIM=0.9004, VEP=0.2)
- ... and 10 more

## Usage

### Baseline Comparison

Compare sequence-based predictors (VEP, SpliceAI, CADD) against ARCHCODE:

```python
import pandas as pd

df = pd.read_csv("benchmark_variants.tsv", sep="\t")

# Blind spot detection rate
pearls = df[df["pearl"] == True]
print(f"Blind spot rate: {len(pearls) / len(df):.2%}")

# By locus
for locus in df["locus"].unique():
    locus_df = df[df["locus"] == locus]
    locus_pearls = locus_df[locus_df["pearl"] == True]
    print(f"{locus}: {len(locus_pearls)} pearls ({len(locus_pearls) / len(locus_df):.2%})")
```

## Citation

If you use this benchmark, please cite:

```
Boyko, S.V. ARCHCODE reveals structural blind spot in variant interpretation.
Preprint planned; DOI to be added upon submission.
```

## License

MIT License - See LICENSE file in main repository.
