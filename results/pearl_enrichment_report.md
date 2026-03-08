# Pearl-like VUS enrichment (exploratory)

**Hypothesis:** Among pearl-like VUS there is enrichment by locus and/or by consequence (regulatory classes).

## Locus enrichment

| Locus | Pearl-like | Not pearl-like |
|------|-----------|----------------|
| HBB | 255 | 1210 |
| BRCA1 | 71 | 7581 |
| TP53 | 13 | 2197 |
| CFTR | 44 | 3454 |
| MLH1 | 111 | 3473 |
| LDLR | 9 | 2149 |
| SCN5A | 0 | 4396 |
| TERT | 76 | 2105 |
| GJB2 | 0 | 575 |
| HBA1 | 0 | 206 |
| GATA1 | 0 | 248 |
| BCL11A | 0 | 250 |
| PTEN | 62 | 2467 |

Global χ²: χ²=1974.458344, p=0.0.

Fisher exact (locus vs rest):
- HBB: OR=15.8882, p=0.0
- BRCA1: OR=0.3735, p=0.0
- TP53: OR=0.2649, p=0.0
- CFTR: OR=0.5731, p=0.000189
- MLH1: OR=1.6184, p=1.5e-05

## Consequence (Category) enrichment

| Category | Pearl-like | Not pearl-like |
|----------|-----------|----------------|
| frameshift | 1 | 57 |
| missense | 13 | 93 |
| other | 33 | 53 |
| splice_region | 2 | 16 |

χ² (Category × pearl): χ²=37.064147, p=0.0.

## Limitations

- Exploratory only; no causal claims.
- Category and locus definitions depend on atlas and summary sources.
- Use wording for manuscript Limitations/Exploratory section only.

