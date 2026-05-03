# Paper 3 HBA Full Queryable Atlas

This file is derived from the local HBA 300kb atlas and does not modify the source atlas.

- Input atlas: `results\HBA1_Unified_Atlas_300kb.csv`
- Locus config: `config\locus\hba1_300kb.json`
- Rows in source atlas: `111`
- Queryable SNVs recovered: `108`
- HBA2-position rows by nearest gene: `5`
- Queryable HBA2-position SNVs: `4`
- Recovery source: UCSC hg38 sequence API + local `HGVS_c` substitution

## Queryable Category Counts

| Category | n |
|---|---:|
| missense | 68 |
| intronic | 12 |
| synonymous | 12 |
| splice | 9 |
| nonsense | 5 |
| other | 2 |

## Guardrail

This is a queryability/provenance table. It is not population evidence and does not establish a regulatory-positive locus.
