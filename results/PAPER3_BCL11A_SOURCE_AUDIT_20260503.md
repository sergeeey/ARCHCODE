# Paper 3 BCL11A Source Audit

Generated from local atlas and locus config only.

- Input atlas: `results\BCL11A_Unified_Atlas_bcl11a_erythroid.csv`
- Locus config: `config\locus\bcl11a_erythroid_95kb.json`
- Bottom-5% LSSIM threshold: `0.9791`
- Audited rows: `11`
- Rows allowed for primary Paper 3 regulatory cohort: `3`

## Mechanism Subclass Counts

| subclass | count |
|---|---:|
| coding_missense_or_synonymous | 7 |
| splice_region_or_intronic | 3 |
| coding_nonsense | 1 |

## Interpretation

This audit is intentionally conservative. Rows are only allowed into the primary Paper 3 regulatory cohort if local HGVS/config evidence supports a promoter-proximal splice/UTR/flank interpretation within 1 kb of a configured feature.

Rows excluded here can still be used in secondary/boundary analyses, but not as clean regulatory-positive evidence.
