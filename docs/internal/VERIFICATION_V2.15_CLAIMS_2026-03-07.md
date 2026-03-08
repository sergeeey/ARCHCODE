# Проверка заявлений v2.15 vs репозиторий (2026-03-07)

Проверка выполнена по артефактам репозитория, `publication_claim_matrix_2026-03-06.json`, `validation_canonical_index_2026-03-06.json`, CLAUDE.md и LEGACY_CLAIM_HYGIENE.

---

## 1. Что подтверждено артефактами репо

| Утверждение v2.15 | Где в репо | Статус |
|-------------------|------------|--------|
| **32,201 вариант, 13 локусов** | `submission_metadata.json` (variants_classified: 32201), `manuscript/body_content.typ` / `body_content_ru.typ`, `docs/COMPARISON_PDF_VS_REPO.md` | Подтверждено |
| **30,952 VUS, 641 pearl-like** | `submission_metadata.json` (vus_scored: 30952), `task5_vus_stratification_summary_2026-03-05.json`, `.claude/memory/activeContext.md` (760 candidates, 641 pearl-like), `body_content.typ` (760 below 0.95, 641 pearl-like) | Подтверждено |
| **AlphaGenome RNA-seq: pearl 2.8× vs benign** | `results/multimodal_pearl_vs_benign_comparison.json`: pearl_mean 16.97, benign_mean 6.09 (≈2.78×), `rna_seq_signal_concentration_ratio` p_value 4.8e-5, n=23+23, Mann-Whitney | Подтверждено численно |
| **Per-locus FPR ≤ 1%** | `results/per_locus_thresholds_summary.json`, `manuscript/FULL_MANUSCRIPT.md` (Table 7, HBB 0.977, TERT 0.968, …) | Подтверждено |
| **Optuna 200 trials, Δr≈0.0001** | Упоминания в FULL_MANUSCRIPT.md, Limitation #3; параметры «manually calibrated», оптимизация подтверждает near-optimal | Подтверждено формулировками |
| **SpliceAI 20/20 pearl SNV = 0.00** | `manuscript/body_content.typ` (стр. 112), `body_content_ru.typ`, `.claude/memory/decisions.md`: VEP REST API с плагином SpliceAI, 20/20 pearl = 0.0000 | Заявлено в manuscript; см. конфликт с Abstract ниже |
| **Экспериментальный RNA-seq: глубины 424K–1,278K** | `results/hbb_novel_junctions_final.json`: depth_hbb_reads WT 424685, B6 736251, A2 1278373; disclaimer exploratory, n=1 | Подтверждено |
| **Валидация splice inconclusive** | Тот же артефакт; нормализованные novel junctions (21.2 / 12.2 / 7.8 per million) не поддерживают гипотезу Loop That Stayed; в manuscript — только Limitations | Подтверждено |

---

## 2. Расхождения и ограничения

### 2.1 Канонический Abstract vs полный manuscript/PDF

В **каноническом** для submission файле `manuscript/ABSTRACT.md` (Data Transparency Declaration):

- **SpliceAI:** «NOT AVAILABLE — API unreachable; replaced by VEP».
- **AlphaGenome:** «NOT USED — Synthetic mock data; excluded entirely».

В **полном** manuscript (`body_content.typ`, FULL_MANUSCRIPT.md) и в PDF v2.15:

- SpliceAI: используется через **Ensembl VEP с плагином SpliceAI**, 20/20 pearl SNV = 0.00.
- AlphaGenome: используется **multimodal (RNA-seq/ATAC)**; 2.8× signal concentration, p≈4.8e-5.

**Вывод:** Для **arXiv/bioRxiv submission** источник истины — ABSTRACT.md: AlphaGenome и SpliceAI в Abstract не заявляются. Если в PDF v2.15 они включены, то PDF и канонический Abstract расходятся; при submission нужно либо привести PDF в соответствие Abstract, либо обновить Abstract с чётким указанием источника данных (VEP+SpliceAI plugin / AlphaGenome SDK) и ограничений.

### 2.2 Governance: что нельзя заявлять

По `results/publication_claim_matrix_2026-03-06.json` и `validation_canonical_index_2026-03-06.json`:

- **C02:** Task1 Pearson > 0.5 — **BLOCKED** (rejected in current setup).
- **C04:** Loop That Stayed как доказанный класс — **BLOCKED** (UNVERIFIED).
- **C07:** Task4 causal mechanism — **BLOCKED**.
- **C09:** Clinical reclassification — **BLOCKED** (NO_GO/UNVERIFIED).

То есть формулировки вида «независимый метод подтверждает pearl» или «клиническая реклассификация» не должны звучать как доказанные утверждения; только как гипотезы/exploratory/ограниченная поддержка.

### 2.3 MaveDB / кросс-вид / 17/17

- MaveDB: в репо есть `data/mavedb_tp53_giacomelli_scores.csv`, `mavedb_tp53_dms_scores.csv`; конкретные r=0.045 (BRCA1 SGE), r=0.383 (TP53 DMS) нужно сверять по скриптам или таблицам manuscript.
- 17/17 pearl консервативны у мыши: в `gnomad_pearl_af_summary.json` — «17/20 queryable pearl SNVs absent from gnomAD» (другая метрика). Явный артефакт «17/17 позиций консервативны у мыши» в проверенных файлах не найден; при использовании в тексте нужна ссылка на конкретный результат/скрипт.

---

## 3. Рекомендуемое предложение для Abstract (RNA-seq)

Предложенная формулировка **соответствует репо** и честно описывает попытку валидации:

```
"An attempted RNA-seq splice junction analysis 
(HUDEP-2 3'HS1-disrupted clones, n=1 per condition) 
was inconclusive due to unequal sequencing depth 
(424K–1,278K reads); definitive validation requires 
biological replicates."
```

Числа 424K–1,278K совпадают с `results/hbb_novel_junctions_final.json` (depth_hbb_reads). Имеет смысл добавить это предложение в Abstract перед submission, если экспериментальный RNA-seq упоминается.

---

## 4. Краткая сводка: что можно писать

- **Можно:** 32,201 вариант / 13 локусов; 30,952 VUS, 641 pearl-like; воспроизводимая вычислительная стратификация; ограниченная поддержка Task2/Task3/Task4/Task5 по каноническим статусам; per-locus пороги FPR≤1%; Optuna как проверка near-optimal параметров; попытка RNA-seq и её inconclusive результат с указанием глубины и n=1.
- **Только с оговорками (и не в Abstract, если там AlphaGenome исключён):** AlphaGenome multimodal 2.8× (есть артефакт, но в каноническом Abstract помечен как NOT USED); SpliceAI 20/20=0 через VEP plugin (в Abstract указано «SpliceAI NOT AVAILABLE»).
- **Нельзя (BLOCKED):** Loop That Stayed как доказанный класс; клиническая реклассификация; Pearson > 0.5 в Task1; причинные биологические механизмы только на основе текущих вычислительных данных.

---

*Проверка выполнена по состоянию репозитория на 2026-03-07. Источники: publication_claim_matrix_2026-03-06.json, validation_canonical_index_2026-03-06.json, results/hbb_novel_junctions_final.json, results/multimodal_pearl_vs_benign_comparison.json, manuscript/ABSTRACT.md, manuscript/body_content.typ, submission_metadata.json.*
