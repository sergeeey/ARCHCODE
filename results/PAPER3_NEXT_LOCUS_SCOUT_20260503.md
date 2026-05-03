# Paper 3 Next Locus Scout

Date: 2026-05-03

Local-source scout only. No gnomAD queries were run.

## Summary

| locus | queryable SNVs | regulatory SNVs | bottom5 regulatory SNVs | controls possible | verdict |
|---|---:|---:|---:|---:|---|
| HBA_full | 108 | 23 | 0 | 23 | STOP_current_gate |
| GATA1 | 0 | 0 | 0 | 0 | REBUILD_REF_ALT |
| LDLR | 2344 | 587 | 122 | 465 | REBUILD_SOURCE |
| LDLR_K562 | 2344 | 587 | 120 | 467 | REBUILD_SOURCE |
| TERT | 1957 | 481 | 8 | 473 | TRY_NEXT_DRY_RUN |
| TERT_SKNS | 1957 | 481 | 0 | 481 | REBUILD_SOURCE |
| HBG1_source_only | 0 | 0 | 0 | 0 | IMPORT_ARCHCODE_ATLAS |
| BCL11A_erythroid | 182 | 17 | 3 | 14 | STOP_control_confound |
| CFTR | 2592 | 783 | 69 | 714 | BOUNDARY_ONLY |

## Interpretation

- TRY_NEXT_DRY_RUN loci: `TERT`
- Rebuild/import candidates: `GATA1, LDLR, LDLR_K562, TERT_SKNS, HBG1_source_only`
- Boundary-only loci: `CFTR`
- Stopped/blocked loci: `HBA_full, BCL11A_erythroid`

## Recommended Next Step

Run a source audit and dry-run gate for `TERT` before any live gnomAD query.

## Guardrails

- Do not pool loci into one headline result.
- Do not treat queryability as evidence of regulatory constraint.
- Do not run live gnomAD unless candidate and control cohorts are non-empty and <=20 rows each.
- Prior blocked loci remain blocked unless their source/control gate is rebuilt.
