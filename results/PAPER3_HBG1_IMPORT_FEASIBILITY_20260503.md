# Paper 3 HBG1 Import Feasibility

Date: 2026-05-03

Source-only import feasibility. No ARCHCODE atlas was generated and no gnomAD query was run.

## Executive Verdict

- Decision: **IMPORT_ARCHCODE_ATLAS_BEFORE_DRY_RUN**
- Can HBG1 serve as the second regulatory-positive locus now? **NOT YET**
- Source-only candidate rows: `79`
- Source-only control rows: `127`
- Main blocker: HBG1 has queryable MPRA-like source rows inside the HBB 95kb sub-TAD config, but no HBG1 ARCHCODE atlas/LSSIM values have been generated for these source variants.
- Next required action: generate or import an HBG1/HBB-subTAD ARCHCODE atlas for the Kircher HBG1 rows, then rerun candidate/control selection and dry-run gate.

## Config Coverage

| Metric | Value |
| --- | --- |
| config | hbb_95kb_subTAD.json |
| config window | chr11:5200000-5295000 |
| HBG1 gene in config | True |
| HBG1 interval | 5248187-5249852 (-) |
| source rows | 907 |
| queryable SNVs | 822 |
| inside config window | 907 |
| promoter-side rows | 744 |

## Source Effect Counts

| mpra_effect_class | rows |
| --- | --- |
| intermediate | 567 |
| near_zero | 242 |
| strong_negative | 94 |
| strong_positive | 4 |

## Local Runner Readiness

| Check | Status |
| --- | --- |
| generate-unified-atlas supports `--locus hbg1` | False |
| locus-config alias supports `hbg1` | False |
| data/hbg1_variants.csv exists | False |
| HBG1 atlas output exists | False |

Runner blocker: the current generic atlas path is not wired for HBG1. The next implementation step is a targeted HBG1 atlas runner/import, not population screening.

## Source-Only Candidate Rows

| Chromosome | Position | Ref | Alt | Value | P-Value | distance_to_hbg1_tss_bp | nearest_feature_name |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | 5249951 | T | C | -1.92 | 0.0 | 99 | HBG1 |
| 11 | 5249999 | G | A | -1.13 | 7.58910192293048e-261 | 147 | HBG1 |
| 11 | 5249969 | T | C | -0.93 | 2.10717893077925e-208 | 117 | HBG1 |
| 11 | 5249945 | G | A | -1.18 | 2.01555780449475e-206 | 93 | HBG1 |
| 11 | 5249941 | A | T | -1.29 | 9.057404635837e-197 | 89 | HBG1 |
| 11 | 5249942 | T | A | -1.21 | 1.3264256812800901e-196 | 90 | HBG1 |
| 11 | 5249969 | T | A | -1.13 | 2.12706285492777e-181 | 117 | HBG1 |
| 11 | 5250002 | G | A | -1.19 | 1.54050648244206e-164 | 150 | HBG1 |
| 11 | 5249884 | T | C | -0.8 | 5.0169362312303e-160 | 32 | HBG1 |
| 11 | 5249998 | G | A | -1.0 | 1.63249665543173e-159 | 146 | HBG1 |
| 11 | 5249968 | A | T | -1.23 | 3.49512247868953e-159 | 116 | HBG1 |
| 11 | 5249942 | T | C | -0.86 | 2.67421762340642e-157 | 90 | HBG1 |
| 11 | 5249941 | A | G | -1.04 | 1.03740477600088e-155 | 89 | HBG1 |
| 11 | 5250004 | G | A | -0.98 | 4.84287219207765e-152 | 152 | HBG1 |
| 11 | 5250001 | G | A | -1.15 | 3.09986769084812e-142 | 149 | HBG1 |
| 11 | 5249943 | T | C | -0.82 | 2.35844861533296e-137 | 91 | HBG1 |
| 11 | 5249998 | G | T | -1.0 | 3.1391802302021995e-123 | 146 | HBG1 |
| 11 | 5249972 | G | A | -0.88 | 6.92298805421704e-121 | 120 | HBG1 |
| 11 | 5249944 | G | A | -0.83 | 1.48993632899943e-116 | 92 | HBG1 |
| 11 | 5249968 | A | G | -0.82 | 3.06415771319102e-105 | 116 | HBG1 |

## Source-Only Control Rows

| Chromosome | Position | Ref | Alt | Value | P-Value | distance_to_hbg1_tss_bp | nearest_feature_name |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | 5249854 | G | A | -0.01 | 0.788911065877373 | 2 | HBG1 |
| 11 | 5249857 | T | A | -0.01 | 0.878680982525192 | 5 | HBG1 |
| 11 | 5249857 | T | G | -0.04 | 0.550219696657617 | 5 | HBG1 |
| 11 | 5249860 | G | T | -0.02 | 0.809332701803882 | 8 | HBG1 |
| 11 | 5249860 | G | A | -0.02 | 0.72329732027179 | 8 | HBG1 |
| 11 | 5249861 | G | A | 0.02 | 0.703139899335484 | 9 | HBG1 |
| 11 | 5249862 | A | C | 0.02 | 0.813158499575033 | 10 | HBG1 |
| 11 | 5249863 | A | G | 0.0 | 0.989940108599081 | 11 | HBG1 |
| 11 | 5249863 | A | T | -0.01 | 0.81097588738519 | 11 | HBG1 |
| 11 | 5249866 | G | A | -0.0 | 0.899683863217611 | 14 | HBG1 |
| 11 | 5249868 | T | C | -0.01 | 0.750672228561433 | 16 | HBG1 |
| 11 | 5249869 | G | C | 0.04 | 0.753940033168324 | 17 | HBG1 |
| 11 | 5249870 | A | C | 0.0 | 0.960989625697747 | 18 | HBG1 |
| 11 | 5249871 | A | C | 0.01 | 0.951071946792338 | 19 | HBG1 |
| 11 | 5249871 | A | G | -0.01 | 0.742026387205765 | 19 | HBG1 |
| 11 | 5249872 | G | T | -0.02 | 0.721708446863647 | 20 | HBG1 |
| 11 | 5249872 | G | C | 0.05 | 0.653142430063733 | 20 | HBG1 |
| 11 | 5249873 | G | C | -0.04 | 0.59041312631635 | 21 | HBG1 |
| 11 | 5249874 | G | T | -0.04 | 0.661880616241527 | 22 | HBG1 |
| 11 | 5249878 | T | G | 0.04 | 0.657805186284943 | 26 | HBG1 |

## Dry-Run / Live Gate

- `population_filter.py` dry-run: **NOT RUN** because HBG1 source rows do not yet have ARCHCODE_LSSIM and frozen candidate/control gate columns.
- Live gnomAD: **NOT RUN**.

## Allowed Claim

HBG1 is the best current source-import target because local MPRA-like rows provide non-empty candidate/control source pools inside the HBB 95kb sub-TAD config, but it is not a Paper 3 population cohort until ARCHCODE atlas values are generated.

## Not Allowed

- "HBG1 validates ARCHCODE"
- "multi-locus confirmed"
- "Paper 3 ready"
- "not found proves constraint"
- "ARCHCODE beats VEP/CADD"

## Decision

**IMPORT_ARCHCODE_ATLAS_BEFORE_DRY_RUN**

Proceed only to an HBG1 ARCHCODE atlas/config import step. Do not run population screening from source-only rows.

## Reproducibility

```powershell
python scripts\paper3_hbg1_import_feasibility.py
```
