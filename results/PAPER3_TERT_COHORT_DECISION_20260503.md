# Paper 3 TERT Cohort Decision

Date: 2026-05-03

This is a dry-run gate report, not a manuscript result.

## Executive Verdict

- Can TERT serve as the second regulatory-positive locus? **NOT YET**
- Why: TERT is the first local post-HBA locus with a non-empty low-LSSIM regulatory candidate cohort and non-empty controls, and dry-run passed for both groups.
- Main blocker: TERT promoter/5_prime_UTR rows need a separate germline/somatic/source semantics audit before population interpretation.
- Next required action: audit the 8 candidates and 8 controls against source semantics and exact Kircher overlap, then decide whether a strict small live gnomAD query is scientifically justified.

## Candidate vs Controls

| Group | n | dry-run matched | successful | not_observed | query_failed | interpretation |
|---|---:|---:|---:|---:|---:|---|
| TERT low-LSSIM regulatory candidates | 8 | 8 | 0 | 0 | 0 | Dry-run passed; no live gnomAD query was run. |
| TERT position controls | 8 | 8 | 0 | 0 | 0 | Dry-run passed; controls are usable for a source audit but not yet for live interpretation. |

## Source Notes

- Candidate rows: `6` promoter_or_5_prime_UTR and `2` splice_region.
- Candidate rows with exact Kircher source overlap: `6/8`.
- Controls: `8` selected rows; some controls are not perfect mechanism matches because the non-bottom 5_prime_UTR pool is limited.
- TERT promoter variants can have mixed germline/somatic/cancer-predisposition semantics, so ClinVar category alone is not enough for a positive regulatory locus claim.

## Dry-Run Evidence

Candidate dry-run:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_TERT_REGULATORY_CANDIDATES_20260503.csv --chrom 5 --cohort-column tert_low_lssim_candidate --cohort-op equals --cohort-value true --locus-name TERT --out paper3_tert_candidates_20260503 --rate-limit 3.0 --dry-run
```

Outcome:

- Total variants in atlas: `8`
- Result: `8/8 variants (100.0%)`
- Expected runtime if live were allowed: `~0.4 minutes`

Control dry-run:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_TERT_POSITION_CONTROLS_20260503.csv --chrom 5 --cohort-column tert_position_control --cohort-op equals --cohort-value true --locus-name TERT_position_controls --out paper3_tert_position_controls_20260503 --rate-limit 3.0 --dry-run
```

Outcome:

- Total variants in atlas: `8`
- Result: `8/8 variants (100.0%)`
- Expected runtime if live were allowed: `~0.4 minutes`

## Allowed Claim

TERT is the current best local next dry-run candidate after HBA failed the regulatory gate, but it is not yet a second regulatory-positive locus.

## Not Allowed

- "TERT validates ARCHCODE"
- "TERT confirms multi-locus generalization"
- "not found in gnomAD proves constraint"
- "Paper 3 ready"
- "ARCHCODE beats VEP/CADD"

## Decision

**REBUILD / AUDIT BEFORE LIVE**

Do not run live gnomAD until the TERT source semantics audit is complete and the position-control matching limitations are explicitly accepted or fixed.
