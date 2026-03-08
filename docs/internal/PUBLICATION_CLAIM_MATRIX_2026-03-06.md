# PUBLICATION_CLAIM_MATRIX_2026-03-06

Primary governance sources:
- `results/validation_canonical_index_2026-03-06.json`
- `results/publication_claim_matrix_2026-03-06.json`

## Matrix

| Claim ID | Claim (short) | Status | Evidence | Required wording | Forbidden wording |
|---|---|---|---|---|---|
| C01 | Validation stack is reproducible with explicit claim tiers. | ALLOWED | `results/validation_canonical_index_2026-03-06.json` | Reproducible computational validation with explicit claim governance. | External-lab reproducibility guarantee without independent reruns. |
| C02 | Task1 achieved strong Pearson (>0.5) vs Hi-C. | BLOCKED | `results/task1_alphagenome_benchmark_brca1mb_1mb_2026-03-06.json`, `results/task1_akita_benchmark_brca1mb_1mb_2026-03-06.json`, `docs/internal/VALIDATION_EXECUTION_2026-03-06_TASK1_1MB.md` | Pearson hypothesis rejected in current setup; keep exploratory. | Any claim that Pearson target was achieved. |
| C03 | Task1 shows limited structural signal via LSSIM. | ALLOWED_WITH_CAVEAT | `results/validation_canonical_index_2026-03-06.json` | Supported-with-limits wording; include setup constraints. | Publication-grade benchmark superiority claims. |
| C04 | Loop That Stayed is proven pathogenic class. | BLOCKED | `results/task2_canonical_status_2026-03-06.json` | UNVERIFIED hypothesis wording only. | Definitive mechanistic/clinical proof. |
| C05 | Task2 supports model-discordance observation. | ALLOWED | `results/task2_canonical_status_2026-03-06.json` | Observational discordance only. | Escalation to causality/clinical utility. |
| C06 | Task3 weak-CTCF no-effect is supported in-model. | ALLOWED_WITH_CAVEAT | `results/task3_canonical_status_2026-03-06.json` | Explicit `SUPPORTED_IN_MODEL` plus external validation disclaimer. | External biological validation claim. |
| C07 | Task4 proves tissue-causal biology. | BLOCKED | `results/task4_canonical_status_2026-03-06.json` | Restrict to input-feature alignment. | Causal/clinical proof from Task4 alone. |
| C08 | Task4 supports context-aware input alignment. | ALLOWED | `results/task4_canonical_status_2026-03-06.json`, `results/task4_epigenome_crossval_2026-03-06.json` | Alignment/consistency support only. | Causal or clinical extrapolation. |
| C09 | Task5 enables clinical reclassification of VUS. | BLOCKED | `results/task5_canonical_status_2026-03-06.json`, `results/hbb_vus_validation_report_2026-03-06.json` | Clinical reclassification remains UNVERIFIED / NO_GO. | Clinical deployment claim. |
| C10 | Task5 provides reproducible stratification for hypothesis generation. | ALLOWED_WITH_CAVEAT | `results/task5_canonical_status_2026-03-06.json`, `results/task5_vus_stratification_summary_2026-03-06.json` | Hypothesis-generating, supported-with-limits. | Clinical utility overclaim. |

## Rewrite Guidance

- For any `BLOCKED` claim:
  - downgrade to `EXPLORATORY`/`UNVERIFIED` language;
  - add explicit boundary sentence: "orthogonal experimental validation required."
- For `ALLOWED_WITH_CAVEAT`:
  - keep scope at model/input-alignment level;
  - include setup limitations and non-clinical disclaimer.

## Verdict

`READY_WITH_LIMITS` for publication drafting under strict claim governance.
