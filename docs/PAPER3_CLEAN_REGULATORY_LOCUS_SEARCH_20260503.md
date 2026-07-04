# Paper 3 Clean Regulatory Locus Search

**Date:** 2026-05-03  
**Question:** Can the downloaded local data provide a second clean regulatory locus for Paper 3?

## Searched Local Source

Path:

`C:\Users\serge\Desktop\ДНК\ДНК Образцы СКАЧЕННЫЙ`

Main usable contents:

- HUDEP2 Hi-C / capture-Hi-C `.hic`
- CD34/HUDEP2 bigWig tracks: CTCF, GATA1, H3K27ac, H3K27me3, ATAC
- `GSE131055_RAW.tar` containing H3K27ac MANGO interaction files and peak files

No ready variant tables (`.csv`, `.bed`, `.vcf`) were found in that folder.

## Key Finding

The folder contains **real erythroid regulatory evidence**, but not a ready second Paper 3 variant cohort.

The most useful file is:

`GSM3762825_1482819_1512832_Hudep2_D3_H3K27AC.interactions.all.mango.txt.gz`

It provides H3K27ac interaction intervals that can be used to define clean regulatory anchors.

## MANGO Interaction Overlap

Local script output files:

| Locus | Output |
|---|---|
| HBA1 | `results/PAPER3_HBA1_MANGO_VARIANT_OVERLAP_20260503.csv` |
| BCL11A | `results/PAPER3_BCL11A_MANGO_VARIANT_OVERLAP_20260503.csv` |
| GATA1 | `results/PAPER3_GATA1_MANGO_VARIANT_OVERLAP_20260503.csv` |
| FOXP3 | `results/PAPER3_FOXP3_MANGO_VARIANT_OVERLAP_20260503.csv` |
| HBB | `results/PAPER3_HBB_MANGO_VARIANT_OVERLAP_20260503.csv` |

| Locus | MANGO anchor overlaps | Variant hits in anchors | Queryable SNVs | Status |
|---|---:|---:|---:|---|
| HBA1 | 145 | 804 | 0 | strong regulatory context, but local variants lack Ref/Alt |
| BCL11A | 7 | 34 | 34 | queryable, but same promoter-proximal coding/splice cluster already failed position-control interpretation |
| GATA1 | 25 | 0 | 0 | regulatory anchors exist, no local variant hits in those anchors |
| FOXP3 | 16 | 0 | 0 | regulatory anchors exist, no local variant hits in those anchors |
| HBB | 258 | 1066 | 741 | strong, but this is Paper 2 anchor, not independent second locus |

## Verdict

**Clean regulatory anchors: yes.**  
**Clean second positive regulatory variant cohort in local files: not yet.**

The downloaded folder can support building a better Paper 3 dataset, but it does not by itself solve the second-locus problem because:

1. HBA1 has strong erythroid interaction support but missing local Ref/Alt alleles.
2. BCL11A has alleles, but current variants are promoter-proximal coding/splice mixed and failed the position-control screen.
3. GATA1/FOXP3 have regulatory anchors but no overlapping local variant hits.
4. HBB is excellent but not independent evidence.

## Best Next Action

Build a new HBA1/HBA2 regulatory candidate table by recovering Ref/Alt alleles for the HBA1 MANGO-overlap variants.

Minimum required columns:

- `ClinVar_ID`
- `Position_GRCh38`
- `Ref`
- `Alt`
- `HGVS_c`
- `MANGO_anchor_start`
- `MANGO_anchor_end`
- `interaction_partner`
- `interaction_count`
- `interaction_pvalue`
- `include_primary_paper3`

Until Ref/Alt are recovered, HBA1 cannot be queried against gnomAD with `scripts/population_filter.py`.

## Current Answer

The project contains enough downloaded regulatory data to **construct** a queryable erythroid MANGO-anchored HBA1 screen, but I did not find a ready-to-query clean second positive locus already sitting in the project.

## HBA1 Build Attempt

After this search, HBA1 Ref/Alt alleles were recovered for local MANGO-overlap rows using:

- UCSC hg38 sequence API for the reference base;
- local `HGVS_c` substitutions for the alternate base;
- a sanity check requiring `UCSC_hg38_ref == HGVS_ref`.

Artifacts:

| File | Purpose |
|---|---|
| `scripts/paper3_hba1_recover_alleles.py` | recovers HBA1 Ref/Alt alleles |
| `results/PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.csv` | queryable HBA1 MANGO-overlap atlas |
| `results/PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.md` | allele recovery summary |
| `scripts/paper3_hba1_screen.py` | builds HBA1 low-LSSIM and matched-control cohorts |
| `results/PAPER3_HBA1_MANGO_CANDIDATES_20260503.csv` | HBA1 low-LSSIM candidate cohort |
| `results/PAPER3_HBA1_MANGO_CONTROLS_20260503.csv` | HBA1 matched controls |
| `results/PAPER3_HBA1_MANGO_POPULATION_SCREEN_COMPARISON_20260503.md` | candidate vs control gnomAD comparison |

Build result:

| Check | Result |
|---|---:|
| MANGO-overlap HBA1 rows | 67 |
| Ref/Alt recovered with UCSC/HGVS match | 66 |
| Low-LSSIM candidates | 4 |
| Matched controls | 4 |

Population screen:

| Group | n | query failures | all-population zero AF | max AF |
|---|---:|---:|---:|---:|
| low-LSSIM candidates | 4 | 0 | 4 | 0.000000684246 |
| matched controls | 4 | 0 | 1 | 0.00000657203 |

Interpretation:

> HBA1 is now a candidate positive erythroid/MANGO-anchored screen. It is not yet a clean regulatory-only locus because the low-LSSIM candidates are currently annotated as coding/nonsense/missense, not enhancer/promoter-only variants.

Practical verdict:

- Ready as **Paper 3 pilot evidence**: yes, with caveat.
- Ready as **clean regulatory-only positive locus**: not yet.
- Best next improvement: recover or import HBA2/HBA enhancer/regulatory noncoding variants inside MANGO anchors, then repeat the same candidate/control screen.
