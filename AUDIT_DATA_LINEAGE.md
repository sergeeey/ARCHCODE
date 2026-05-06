# AUDIT DATA LINEAGE

Date: 2026-05-05

## Goal

Map the chain from source data to generated results and final claims. This pass is a documentation audit only; it does not verify every row or rerun every pipeline.

## High-Level Lineage

```text
external biological sources
  -> data/ and reference/
  -> config/locus/*.json
  -> scripts/*.ts and scripts/*.py
  -> results/*.csv / results/*.json
  -> analysis/*.csv / analysis/*.json
  -> figures/ and plots/
  -> README.md / docs/ / manuscript/
  -> public claim matrix and publication surfaces
```

## Source Data Classes

| Class | Paths | Examples | Status |
|---|---|---|---|
| Raw/external biological data | `data/`, `reference/`, `fastq_data/`, `stress_biology/data/` | ClinVar, Hi-C, CADD cache, MPRA, gnomAD, FASTQ/MAF | PARTIAL MAP |
| Locus configs | `config/locus/*.json`, `src/domain/config/locus-config.ts` | HBB, TP53, SCN5A, TERT, LDLR, etc. | PARTIAL MAP |
| Generated primary results | `results/*Unified_Atlas*.csv`, `results/*SUMMARY*.json` | HBB atlas, per-locus summaries | PARTIAL MAP |
| Secondary analysis | `analysis/*.csv`, `analysis/*.json`, `validation_suite/results/*.json` | baselines, within-category, thresholds | PARTIAL MAP |
| Figures | `figures/`, `plots/` | ROC, multi-locus summaries, validation plots | NOT DEEPLY VERIFIED |
| Manuscript/docs claims | `README.md`, `docs/`, `manuscript/` | public and technical narratives | PARTIAL CLAIM MAP |

## Canonical Release Evidence Index

Source: `results/publication_canonical_index_2026-03-30.json`.

| Evidence group | Artifacts |
|---|---|
| Atlas scale | `results/integrative_benchmark_summary.json`, `results/per_locus_thresholds_summary.json` |
| HBB ROC | `results/roc_unified.json` |
| ARCHCODE vs CADD | `results/integrative_benchmark_summary.json` |
| Per-locus thresholds | `results/per_locus_thresholds_summary.json` |
| Hi-C validation | `results/hic_correlation_k562.json`, `results/hic_correlation_k562_95kb.json`, `results/hic_correlation_brca1.json`, `results/hic_correlation_mlh1.json`, `results/hic_correlation_tp53.json`, `results/hic_correlation_ldlr.json` |
| AlphaGenome real API | `results/alphagenome_3way_comparison.json`, `results/alphagenome_ism_promoter.json` |
| MPRA cross-validation | `results/mpra_crossvalidation_summary.json` |
| Ablation | `results/ablation_effectstrength.json` |
| Conservation / gnomAD | `results/conservation_pearl_analysis.json`, `results/gnomad_pearl_af_summary.json` |

## Primary Lineage Examples

| Claim/result | Input | Script | Output | Claim surface |
|---|---|---|---|---|
| 30,318 variants across 9 loci | ClinVar-derived locus atlases | `scripts/generate-unified-atlas.ts` and related pipelines | `results/integrative_benchmark_summary.json`, `results/per_locus_thresholds_summary.json` | `README.md`, claim P01 |
| HBB AUC 0.977 | HBB atlas | ROC scripts such as `scripts/calculate_roc_and_quadrants.py` / `scripts/reproduce_hbb_roc.py` | `results/roc_unified.json` | `README.md`, claim P02 |
| Category drives HBB AUC | HBB atlas | `scripts/ablation_study.py` / related ablation scripts | `results/ablation_effectstrength.json` | `README.md`, claim P09 |
| TP53 within-category signal | TP53 atlas | `validation_suite` / `scripts/tp53_splice_region_deep.py` | `validation_suite/results/within_category_tp53.json`, `results/tp53_splice_region_deep_dive.json` | `README.md`, `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md` |
| AlphaGenome promoter hotspot | HBB selected variants | `scripts/alphagenome_real_experiments.py` | `results/alphagenome_3way_comparison.json`, `results/alphagenome_ism_promoter.json` | `README.md`, claim P06/P07 |
| MPRA null | Kircher MPRA data | `scripts/mpra_crossvalidation.py` | `results/mpra_crossvalidation_summary.json` | `README.md`, claim P08 |
| Paper2 population stratification | HBB pearl subset + gnomAD | `scripts/population_filter.py`, `scripts/query_gnomad_populations.py`, related offline scripts | `results/gnomad_populations_pearls.csv`, `results/gnomad_coverage_check.json` | Paper2 manuscript/docs; current dirty tree contains modified files |
| Paper3 exploratory gates | locus-specific source tables | `scripts/paper3_*` | `results/PAPER3_*`, `docs/PAPER3_*` | Technical/exploratory only |

## Dirty Lineage Risks

| Dirty artifact | Risk |
|---|---|
| `results/HBB_Unified_Atlas.csv` | Primary result file changed; claims depending on HBB atlas need rerun or diff review |
| `results/UNIFIED_ATLAS_SUMMARY.json` | Summary changed; claim matrix may become stale if this is promoted |
| `results/gnomad_populations_pearls.csv` | Population-stratification claims may depend on unstaged changes |
| `scripts/generate-unified-atlas.ts` | Atlas generation logic changed; must be version-paired with result outputs |
| `src/domain/config/locus-config.ts` | Config exposure changed; may alter run semantics |
| `results/spectral_sprint_log.md` | Pilot evidence log changed; not ready for strong claims without lineage map |

## Data Provenance Gaps

| Gap | Impact |
|---|---|
| Not all generated `results/` artifacts are tracked | Hard to reproduce exact narrative state |
| Many untracked Paper3 outputs | Exploratory results can leak into claims |
| Checksums not rerun | Raw/generated integrity not verified in this pass |
| External source resolution not rerun | DOI/API existence not freshly checked |
| Some scripts imply downloads or live APIs | Runs may be time/network/API-key dependent |
| Synthetic scans coexist with real data | Must keep `SYNTHETIC_` labels and exclude from real validation |

## Data-Lineage Verdict

The repository has the components of a defensible lineage system, especially the claim matrix and canonical index, but the present working tree is too dirty for publication-grade reproducibility. Before any new claim is promoted, each claim must name:

1. input files,
2. script command,
3. output artifact,
4. commit hash,
5. provenance class,
6. acceptance criteria,
7. caveats.

