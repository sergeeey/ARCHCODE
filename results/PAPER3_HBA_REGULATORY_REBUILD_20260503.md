# Paper 3 HBA Regulatory Rebuild

Date: 2026-05-03

This is a gate artifact, not a manuscript result.

## Source Inventory

|File|Exists|Rows|Queryable SNVs|Regulatory candidates|Synthetic risk|Status|
|---|---|---|---|---|---|---|
|config\locus\hba1_300kb.json|True|0|0|0|0|features ctcf_sites,enhancers,genes|
|config\locus\hba1_90kb_focused.json|True|0|0|0|0|features ctcf_sites,enhancers,genes|
|data\clinvar_hba1_variants.csv|True|170|0|0|0|missing Position_GRCh38,Ref,Alt,HGVS_c,Category,Source,ARCHCODE_LSSIM|
|data\hba1_mutagenesis_variants.csv|True|372|372|0|372|synthetic_or_mutagenesis_only|
|data\hba1_pathogenic_positions.txt|True|41|0|0|0|text_positions_only|
|data\hba1_variants.csv|True|111|0|0|0|missing Position_GRCh38,Ref,Alt,HGVS_c,Category,Source,ARCHCODE_LSSIM|
|results\HBA1_Unified_Atlas_300kb.csv|True|111|0|0|0|not_queryable_ref_alt|
|results\NPRL3_Unified_Atlas_hba1_focused.csv|True|111|0|0|0|not_queryable_ref_alt|
|results\NPRL3_Unified_Atlas_hba1_mutagenesis.csv|True|372|372|0|372|synthetic_or_mutagenesis_only|
|results\PAPER3_HBA1_MANGO_CANDIDATES_20260503.csv|True|4|4|0|0|missing Position_GRCh38,HGVS_c,Source,ARCHCODE_LSSIM|
|results\paper3_hba1_mango_candidates_20260503.json|True|0|0|0|0|json_no_locus_features|
|results\PAPER3_HBA1_MANGO_CONTROLS_20260503.csv|True|4|4|0|0|missing Position_GRCh38,HGVS_c,Source,ARCHCODE_LSSIM|
|results\paper3_hba1_mango_controls_20260503.json|True|0|0|0|0|json_no_locus_features|
|results\PAPER3_HBA1_MANGO_POPULATION_SCREEN_COMPARISON_20260503.md|True|0|0|0|0|not_tabular|
|results\PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.csv|True|67|66|9|0|candidate_space_available|
|results\PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.md|True|0|0|0|0|not_tabular|
|results\PAPER3_HBA1_MANGO_SCREEN_20260503.md|True|0|0|0|0|not_tabular|
|results\PAPER3_HBA1_MANGO_VARIANT_OVERLAP_20260503.csv|True|804|0|0|0|missing Position_GRCh38,Ref,Alt,HGVS_c,Category,Source,ARCHCODE_LSSIM|
|results\PAPER3_HBA_POSITION_CONTROLS_20260503.csv|True|0|0|0|0|not_queryable_ref_alt|
|results\PAPER3_HBA_REGULATORY_CANDIDATES_20260503.csv|True|9|9|9|0|candidate_space_available|
|results\PAPER3_HBA_REGULATORY_REBUILD_20260503.md|True|0|0|0|0|not_tabular|
|results\UNIFIED_ATLAS_SUMMARY_HBA1_300kb.json|True|0|0|0|0|json_no_locus_features|
|results\UNIFIED_ATLAS_SUMMARY_hba1_focused.json|True|0|0|0|0|json_no_locus_features|
|results\UNIFIED_ATLAS_SUMMARY_hba1_mutagenesis.json|True|0|0|0|0|json_no_locus_features|
|scripts\paper3_hba1_recover_alleles.py|True|0|0|0|0|script|
|scripts\paper3_hba1_screen.py|True|0|0|0|0|script|
|scripts\paper3_hba_regulatory_rebuild.py|True|0|0|0|0|script|

## Config Feature Audit

| Feature | Present in local HBA configs |
|---|---:|
| promoter | False |
| enhancer | True |
| CRE | False |
| DHS | False |
| CTCF | True |
| TAD | False |

## Rebuild Inputs

- Primary queryable source atlas: `results\PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.csv`
- HBA2-specific source rows found locally: `0`
- Queryable non-synthetic source rows: `66`
- Queryable regulatory-subclass source rows: `9`
- Whole-locus bottom-5% LSSIM threshold: `0.994425`
- Regulatory-subset exploratory bottom-5% threshold: `0.9964`

## Whole-Locus Bottom-5% Rows

| ClinVar_ID | Position_GRCh38 | Ref | Alt | HGVS_c | Category | mechanism_subclass | ARCHCODE_LSSIM |
|---|---:|---|---|---|---|---|---:|
| VCV004533035 | 177331 | G | T | c.349G>T | nonsense | coding_nonsense | 0.9857 |
| VCV003579879 | 177017 | A | T | c.184A>T | nonsense | coding_nonsense | 0.9867 |
| VCV003766985 | 177400 | A | G | c.418A>G | missense | coding_missense | 0.9943 |
| VCV002428618 | 177379 | G | A | c.397G>A | missense | coding_missense | 0.9944 |

## Candidate Gate

| Gate | n | Interpretation |
|---|---:|---|
| regulatory candidate space | 9 | Queryable non-synthetic regulatory-subclass rows exist. |
| primary low-LSSIM regulatory candidates | 0 | Requires regulatory subclass and whole-locus bottom 5% LSSIM. |
| secondary regulatory LSSIM < 0.99 | 0 | Boundary-only gate; not primary. |
| exploratory regulatory-subset bottom 5% | 2 | Not used for the primary Paper 3 gate because it changes the denominator post hoc. |
| selected position controls | 0 | Controls are selected only after primary candidates exist. |

## Dry-Run Commands

Candidate dry-run gate:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_HBA_REGULATORY_CANDIDATES_20260503.csv --chrom 16 --cohort-column primary_low_lssim_candidate --cohort-op equals --cohort-value true --locus-name HBA --out paper3_hba_candidates_20260503 --rate-limit 3.0 --dry-run
```

Control dry-run gate:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_HBA_POSITION_CONTROLS_20260503.csv --chrom 16 --cohort-column selected_position_control --cohort-op equals --cohort-value true --locus-name HBA_position_controls --out paper3_hba_position_controls_20260503 --rate-limit 3.0 --dry-run
```

## Gate Result

The current local HBA queryable source does not produce a primary low-LSSIM regulatory cohort. The low-LSSIM tail is coding/nonsense/missense, while queryable regulatory-subclass rows sit outside the primary bottom-5% and outside the secondary `LSSIM < 0.99` boundary.
