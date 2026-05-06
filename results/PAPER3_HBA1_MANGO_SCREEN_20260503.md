# Paper 3 HBA1 MANGO Screen

HBA1 queryable alleles were recovered from UCSC hg38 sequence plus local HGVS_c substitutions.

- Queryable MANGO-overlap SNVs: `66`
- Bottom-5% LSSIM threshold: `0.9944`
- Low-LSSIM candidates: `4`
- Matched controls selected: `4`

## Candidate Category Counts

| category | count |
|---|---:|
| nonsense | 2 |
| missense | 2 |

## Control Category Counts

| category | count |
|---|---:|
| missense | 4 |

## Guardrail

This is MANGO-anchored and queryable, but not a clean regulatory-only cohort because the low-LSSIM candidates are coding/nonsense in the current local annotation.
