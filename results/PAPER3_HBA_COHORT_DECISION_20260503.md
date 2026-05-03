# Paper 3 HBA Cohort Decision

Date: 2026-05-03

This is a gate report, not a manuscript result.

## Executive Verdict

- Can HBA1/HBA2 serve as second regulatory-positive locus? **NOT YET**
- Why: local HBA data contains queryable regulatory-subclass rows, but the primary low-LSSIM gate has `0` regulatory candidates under the whole-locus bottom-5% rule.
- Main blocker: the HBA low-LSSIM tail is coding/nonsense/missense, not regulatory; HBA2-specific local source rows were not found.
- Next required action: rebuild or import a real noncoding HBA/HBA2 regulatory source cohort with Ref/Alt and frozen position controls before any live population query.

## Candidate vs Controls

| Group | n | successful | not_observed | query_failed | interpretation |
|---|---:|---:|---:|---:|---|
| HBA primary low-LSSIM regulatory candidates | 0 | 0 | 0 | 0 | Dry-run gate blocked: `population_filter.py` reported `0/9` matched variants and raised `ValueError`. |
| HBA selected position controls | 0 | 0 | 0 | 0 | No controls can be selected because the primary candidate cohort is empty; control dry-run exposed the zero-row input state. |

## Dry-Run Evidence

Rebuild command:

```powershell
python scripts\paper3_hba_regulatory_rebuild.py
```

Outcome:

- Wrote `results\PAPER3_HBA_REGULATORY_CANDIDATES_20260503.csv`
- Wrote `results\PAPER3_HBA_POSITION_CONTROLS_20260503.csv`
- Wrote `results\PAPER3_HBA_REGULATORY_REBUILD_20260503.md`
- Primary candidates: `0`
- Selected controls: `0`

Candidate dry-run command:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_HBA_REGULATORY_CANDIDATES_20260503.csv --chrom 16 --cohort-column primary_low_lssim_candidate --cohort-op equals --cohort-value true --locus-name HBA --out paper3_hba_candidates_20260503 --rate-limit 3.0 --dry-run
```

Outcome:

- Total variants in atlas: `9`
- Cohort filter: `primary_low_lssim_candidate equals True`
- Result: `0/9 variants (0.0%)`
- Exit: `ValueError: Cohort filter produced 0 variants`

Control dry-run command:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_HBA_POSITION_CONTROLS_20260503.csv --chrom 16 --cohort-column selected_position_control --cohort-op equals --cohort-value true --locus-name HBA_position_controls --out paper3_hba_position_controls_20260503 --rate-limit 3.0 --dry-run
```

Outcome:

- Total variants in atlas: `0`
- Exit: `ZeroDivisionError: division by zero`
- Interpretation: this is a technical edge case from an empty selected-control atlas, not population evidence.

## Allowed Claim

Under the conservative local-source gate, HBA currently has queryable regulatory-subclass rows but no primary low-LSSIM regulatory cohort; HBA should remain a rebuild target rather than a second regulatory-positive locus.

## Not Allowed

- "HBA validates ARCHCODE"
- "multi-locus confirmed"
- "not found proves constraint"
- "Paper 3 ready"
- "ARCHCODE beats VEP/CADD"

## Decision

**STOP** for the current HBA gate.

Do not run live gnomAD for HBA in this state. Continue only after a rebuilt HBA/HBA2 noncoding regulatory source cohort creates non-empty primary candidates and non-empty position controls under the same denominator and coordinate rules.
