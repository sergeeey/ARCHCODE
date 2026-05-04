# Paper 3 GATA1 Source Inventory

Date: 2026-05-03

Local-source inventory only. No gnomAD query was run.

## Executive Verdict

- Decision: **STOP_LOCAL_POSITIVE_GATE / REBUILD_REF_ALT_ONLY**
- Can GATA1 serve as the second regulatory-positive locus from current local rows? **NO / NOT YET**
- Queryable SNVs after HGVS allele recovery: `182`
- Primary promoter/enhancer-like regulatory candidates: `0`
- Primary controls selected: `0`
- Main blocker: local GATA1 rows are mostly coding or splice/intronic disease variants; Ref/Alt can be recovered for many SNVs, but that does not create a clean noncoding regulatory-positive cohort.
- Next required action: import a true GATA1 regulatory source set or switch to a documented regulatory locus with queryable noncoding SNVs and matched controls.

## Inventory Counts

| Metric | Value |
| --- | --- |
| atlas rows | 183 |
| source rows | 227 |
| queryable SNVs after recovery | 182 |
| promoter/enhancer-like queryable rows | 0 |
| splice/intronic queryable rows | 27 |
| coding queryable rows | 154 |
| bottom 5% queryable rows | 12 |
| primary regulatory candidates | 0 |

## Bottom-5 Mechanism Composition

| mechanism_subclass | bottom5 rows |
| --- | --- |
| coding_missense | 11 |
| coding_nonsense | 1 |

## Regulatory-Like Rows After Recovery

No promoter/enhancer-like queryable rows were recovered from the current local GATA1 source set.

## Dry-Run / Live Gate

- `population_filter.py` dry-run: **SKIPPED** because primary regulatory candidates are empty.
- Live gnomAD: **NOT RUN**.

## Allowed Claim

GATA1 local rows show recoverable SNV queryability, but current local sources do not support a clean regulatory-positive Paper 3 cohort.

## Not Allowed

- "GATA1 validates ARCHCODE"
- "multi-locus confirmed"
- "Paper 3 ready"
- "not found proves constraint"
- "ARCHCODE beats VEP/CADD"

## Reproducibility

```powershell
python scripts\paper3_gata1_source_inventory.py
```
