# Paper 3 CFTR Regulatory Screen

Generated from local CFTR atlas and locus config only.

- Input atlas: `results\CFTR_Unified_Atlas_317kb.csv`
- Locus config: `config\locus\cftr_317kb.json`
- Bottom-5% LSSIM threshold: `0.9814`
- Primary low-LSSIM regulatory candidates: `26`
- Position control pool within 1.5 kb of configured features: `52`
- Position controls selected for pilot: `26`

## Candidate Subclasses

| subclass | count |
|---|---:|
| 5_prime_utr_or_promoter | 18 |
| genomic_other | 8 |

## Control Subclasses

| subclass | count |
|---|---:|
| splice_region_or_intronic | 25 |
| genomic_other | 1 |

## Interpretation Guardrail

CFTR is a mechanism-boundary candidate because the local config notes K562 tissue mismatch and literature-derived enhancer occupancy. Passing this screen would identify a useful regulatory test locus, not a final validation result.
