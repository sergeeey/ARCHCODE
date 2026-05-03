# Paper 3 TERT Regulatory Screen

Date: 2026-05-03

This is a source/dry-run cohort artifact, not a manuscript result.

- Input atlas: `results\TERT_Unified_Atlas_300kb.csv`
- Kircher source table: `data\kircher_TERT_GRCh38.tsv`
- Queryable non-synthetic SNVs: `1957`
- Queryable regulatory-subclass SNVs: `481`
- Whole-locus bottom-5% LSSIM threshold: `0.978`
- Low-LSSIM regulatory candidates: `8`
- Selected position controls: `8`
- Candidate rows with exact Kircher overlap: `6`

## Candidate Mechanism Counts

| mechanism_subclass | n |
|---|---:|
| promoter_or_5_prime_UTR | 6 |
| splice_region | 2 |

## Dry-Run Commands

Candidate dry-run:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_TERT_REGULATORY_CANDIDATES_20260503.csv --chrom 5 --cohort-column tert_low_lssim_candidate --cohort-op equals --cohort-value true --locus-name TERT --out paper3_tert_candidates_20260503 --rate-limit 3.0 --dry-run
```

Control dry-run:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_TERT_POSITION_CONTROLS_20260503.csv --chrom 5 --cohort-column tert_position_control --cohort-op equals --cohort-value true --locus-name TERT_position_controls --out paper3_tert_position_controls_20260503 --rate-limit 3.0 --dry-run
```

## Gate Caveat

Do not run live gnomAD from this artifact alone. TERT promoter/5_prime_UTR rows need a separate germline/somatic/source semantics audit before population interpretation.
