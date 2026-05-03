# Data Notes — PyPop HBB Human Mutation Submission

This directory contains the data files supporting the Human Mutation Brief Report submission:

- `gnomad_populations_pearls.csv` — initial population-stratified gnomAD query table for 17 ARCHCODE variants. The manuscript focuses on 15 HBB promoter variants; 2 missense rows are retained for provenance.
- `gnomad_populations_summary.json` — summary statistics derived from the initial query table.
- `gnomad_coverage_check.json` — authoritative follow-up coverage check for the two East Asian-enriched variants.
- `HBB_Unified_Atlas.csv` — source atlas for ARCHCODE/VEP/CADD annotations.
- `scripts/population_filter.py` — generic reproducible gnomAD v4 population query CLI.

## Authoritative Allele Frequencies

Use `gnomad_coverage_check.json` for the two variants highlighted in the manuscript:

- `VCV000015471`: `AF_EAS = 0.000648` from gnomAD v4 genome data (`AC_EAS = 24`, `AN_EAS = 37,034`).
- `VCV000015466`: `AF_EAS = 0.000464` from gnomAD v4 exome data (`AC_EAS = 17`, `AN_EAS = 36,610`).

`gnomad_populations_pearls.csv` contains an earlier preliminary value for `VCV000015471` (`AF_EAS = 0.000193`). That value is superseded by the May 2 coverage check above and is not used in the manuscript.

Genome data is primary for `VCV000015471` because the follow-up query provided the authoritative East Asian allele count/number used in the submission. Exome data is primary for `VCV000015466` for the same reason.

## Variant Counts

The manuscript cohort is:

- 15 HBB promoter variants.
- 12 successfully queried/found in gnomAD v4.
- 3 not observed in the queried gnomAD v4 datasets.

“Not observed in gnomAD” means the variant was not found in the queried gnomAD v4 exome/genome records. It does not prove universal constraint or pathogenicity.

## Reproduction

Use `scripts/population_filter.py` for new or repeated population-stratified queries. Example pattern:

```bash
python scripts/population_filter.py --atlas results/HBB_Unified_Atlas.csv --chrom 11 --cohort-column Pearl --cohort-op equals --cohort-value true --locus-name HBB --out hbb_pearls
```

