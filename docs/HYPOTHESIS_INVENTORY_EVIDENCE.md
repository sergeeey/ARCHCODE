# Инвентарь гипотез — первоисточники и статусы

**Canon Tier:** Technical Full-Scope  
**Назначение:** зафиксировать, **какими файлами** подкреплены ключевые утверждения из обзора гипотез (TP53 within-category, SCN5A cardiac), без правки `.cursor/plans/*`.

---

## 1. TP53: within-category и «остров» splice_region

### 1.1 Validation suite (локус целиком)

**Файл:** [validation_suite/results/within_category_tp53.json](../validation_suite/results/within_category_tp53.json)

| Поле | Значение |
|------|----------|
| `n_variants` | 2794 |
| `overall_auc` | 0.6691 |
| `median_within_cat_auc` | 0.6368 |
| `n_surviving_fdr` | **4** (все протестированные категории) |

**Категория `splice_region`:** `auc` = **0.6906**, `cohens_d` = **-0.776**, `bh_q` = 0, `survives_fdr` = true.

**Наблюдение:** в этом артефакте **не только** `splice_region` проходит FDR — проходят также `other`, `synonymous`, `intronic`. Публичные формулировки вроде «единственный остров — splice_region» нужно сверять с портфелем из **25 тестов** (все локусы × категории) и с тем, какой акцент вы выбираете (сильнейший эффект / единственный локус с портфельным пережитием FDR). Иначе возможна **семантическая недосказанность** между README и этим JSON.

### 1.2 Deep dive (подмножество splice_region)

**Файл:** [results/tp53_splice_region_deep_dive.json](../results/tp53_splice_region_deep_dive.json)

| Метрика | Значение |
|---------|----------|
| `n_variants` | 139 (73 pathogenic / 66 benign) |
| `original_auc` | 0.6906 (совпадает с validation suite) |
| `original_cohens_d` | -0.78 |
| `permutation_p` | 0.0002 (`n` = 10000) |
| `fdr_bh_q` | 0.00125, `fdr_survives` = true |
| `cv_auc_mean` | 0.688 |

**Критичный контроль (baselines в том же файле):**

| Baseline | AUC |
|----------|-----|
| `lr_auc` | 0.452 |
| `rf_auc` | **0.825** |
| `position_only_auc` | 0.431 |

**Интерпретация (осторожно):** SSIM/LSSIM на этом подмножестве **значимо** отделяет классы, но **Random Forest на тех же простых признаках** в этом артефакте **сильнее** по AUC, чем структурный скор. Для честного позиционирования «острова» это означает: сигнал **не обязательно** «уникальная физика», пока не показано превосходство над RF с жёстким matched-дизайном и внешней репликацией.

### 1.3 Связанный код

- [scripts/tp53_splice_region_deep.py](../scripts/tp53_splice_region_deep.py) — генерация `tp53_splice_region_deep_dive.json` (проверять актуальность при изменении пайплайна).

---

## 2. SCN5A cardiac (`scn5a_cardiac_250kb`)

### 2.1 Полный прогон атласа

**Файл:** [results/UNIFIED_ATLAS_SUMMARY_SCN5A_250kb.json](../results/UNIFIED_ATLAS_SUMMARY_SCN5A_250kb.json)

| Поле | Значение |
|------|----------|
| `locus_config_id` | `scn5a_cardiac_250kb` |
| `statistics.total_variants` | **2488** |
| `provenance.thresholds_calibrated` | **true** (в смысле метаданных summary после pipeline fix) |
| Дата в файле | 2026-03-24 |

**Исходные варианты:** `data/scn5a_cardiac_variants.csv` (указано в summary).

**Вывод:** **полный прогон** ClinVar-когорты под cardiac-конфиг **зафиксирован** этим summary и CSV ([results/SCN5A_Unified_Atlas_250kb.csv](../results/SCN5A_Unified_Atlas_250kb.csv) — путь используется в [scripts/tissue_match_amplification.py](../scripts/tissue_match_amplification.py)).

### 2.2 Сравнение K562 vs cardiac

**Файл:** [analysis/scn5a_cardiac_comparison.json](../analysis/scn5a_cardiac_comparison.json)

- Вердикт в JSON: cardiac конфиг **усиливает** разделение и число structural calls относительно K562 (коэффициенты `amplification` в файле).
- Это **не** отменяет оговорок конфига про пороги (см. ниже).

### 2.3 Конфиг и пороги

**Файл:** [config/locus/scn5a_cardiac_250kb.json](../config/locus/scn5a_cardiac_250kb.json)

В блоке `thresholds` и `_thresholds_note` явно указано:

- пороги **скопированы** с `scn5a_400kb` (K562 / mismatch-контекст калибровки);
- **обязательна перекалибровка** под cardiac и под другое число бинов (250 vs 400), иначе сравнение SSIM между конфигами некорректно.

**Сводный статус:**

| Вопрос | Ответ по репозиторию |
|--------|----------------------|
| Был ли прогон атласа? | **Да** — см. `UNIFIED_ATLAS_SUMMARY_SCN5A_250kb.json`, 2488 вариантов. |
| Есть ли сравнение с K562? | **Да** — `analysis/scn5a_cardiac_comparison.json`. |
| Завершена ли **публикационная** перекалибровка порогов под cardiac? | **Нет / не задокументирована как закрытая** — конфиг требует recalibration; summary `thresholds_calibrated: true` **не отменяет** это предупреждение в JSON конфига. |

### 2.4 Визуализация / цифры для текста

- [scripts/plot_scn5a_cardiac_comparison.py](../scripts/plot_scn5a_cardiac_comparison.py) → `figures/taxonomy/fig_scn5a_cardiac_comparison.*`

---

## 3. Как использовать этот файл

- Для **negative result / methods** paper: ссылаться на §1 baselines (RF > SSIM) и на §2 противоречие `thresholds_calibrated` vs `REQUIRES RECALIBRATION`.
- Для **узкого биологического** трека: TP53 — пререгистрировать, что именно сравнивается (SSIM vs RF vs position-only) и на каком подмножестве.
