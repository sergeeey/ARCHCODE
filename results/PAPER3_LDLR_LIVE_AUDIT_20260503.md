# Paper 3 LDLR Live Audit

Date: 2026-05-03

This note records the first live gnomAD v4 query on the frozen LDLR candidate/control pair.
It is an audit artifact, not a manuscript claim.

## Inputs

- Candidate atlas: `results/PAPER3_LDLR_STRICT_SUBSET_CANDIDATES_20260503.csv`
- Control atlas: `results/PAPER3_LDLR_MATCHED_CONTROLS_20260503.csv`
- Query tool: `scripts/population_filter.py`
- Live outputs:
  - `results/paper3_ldlr_candidates_live_20260503.csv`
  - `results/paper3_ldlr_candidates_live_20260503.json`
  - `results/paper3_ldlr_controls_live_20260503.csv`
  - `results/paper3_ldlr_controls_live_20260503.json`

## Candidate-side summary

- Frozen candidate subset: 17 rows
- Live rows written: 15
- Successful gnomAD rows: 8
- Query failed rows: 7
- Queryable SNVs: 15
- Non-queryable indels: 2
- Strong evidence absent in all 5 populations: 6
- Weak evidence: 2
- False pearls: 1
- Strong evidence rate: 75.0%
- Max observed AF:
  - AFR: 0.0227524437809987
  - AMR: 0.00209259743656814
  - EAS: 0.00014102781068426693
  - EUR: 0
  - SAS: 0

## Control-side summary

- Frozen matched-control subset: 24 rows
- Live rows written: 24
- Successful gnomAD rows: 12
- Query failed rows: 12
- Queryable SNVs: 24
- Strong evidence absent in all 5 populations: 8
- Weak evidence: 4
- False pearls: 0
- Strong evidence rate: 66.7%
- Max observed AF:
  - AFR: 2.414059482425647e-05
  - AMR: 0
  - EAS: 2.5325431798612168e-05
  - EUR: 0
  - SAS: 2.3321983301459956e-05

## Interpretation

- The candidate side still shows a stronger population signal than the matched controls.
- The control side is not null, which is expected for a real locus-level comparison.
- Several rows failed at query time. Those failures are technical and do not count as evidence of absence.
- Rows marked `gnomAD_v4_not_observed_graphql` still require coordinate/build sanity checks before any stronger interpretation.
- The single candidate false pearl means the LDLR signal is not uniformly benign across the frozen candidate subset.

## Status

- Good enough for a design-level audit.
- Not enough for a manuscript claim.
- Not enough to call LDLR a fully validated second positive locus yet.

## Next action

- If this line continues, add a focused sanity-check pass for the failed rows and the not-observed rows.
- Do not widen the locus search before that pass is complete.
