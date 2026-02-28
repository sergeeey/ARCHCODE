# ARCHCODE v2.0 — Сводный исследовательский отчёт

**Дата:** 2026-02-28
**Статус:** v1.0 на bioRxiv (DOI pending), исследование v2.0
**Метод:** 5 параллельных исследовательских агентов

---

## КРИТИЧЕСКАЯ НАХОДКА: Pipeline Discrepancy (Приоритет №0)

**Обнаружено агентом Within-Category ROC.**

В текущем Combined Atlas (1,103 варианта) pathogenic и benign варианты прогнаны через **два разных пайплайна** с **разными масштабами пертурбации**:

| Пайплайн   | Файл                     | Язык       | Intronic impact                                   |
| ---------- | ------------------------ | ---------- | ------------------------------------------------- |
| Pathogenic | `generate-real-atlas.ts` | TypeScript | `effectStrength=0.8` → occ \*= 0.8 (20% снижение) |
| Benign     | `run_benign_pipeline.py` | Python     | `impact=0.02` → occ \*= 0.98 (2% снижение)        |

**Результат:** Intronic pathogenic SSIM = 0.9951-0.9960, intronic benign SSIM = 1.0000. Это **10x разница в пертурбации** для одной и той же категории, просто из-за разных пайплайнов.

**AUC = 1.000 — артефакт разных пайплайнов, а не предсказательная сила модели.**

### Что делать:

1. **Унифицировать пайплайн** — прогнать ВСЕ 1,103 варианта через ОДИН код с ОДНИМИ параметрами
2. **Пересчитать AUC** — после унификации within-category AUC будет ≈ 0.5 (математически гарантировано)
3. **Рефрейминг в manuscript** — честно указать что AUC отражает категориальную стратификацию

---

## Направление 1: Within-Category ROC

### Вердикт: AUC ≈ 0.5 (гарантировано текущей архитектурой)

**Почему:** SSIM — детерминированная функция от (category, bin_position). Внутри одной категории:

- Варианты в одном бине → идентичный SSIM
- Дисперсия SSIM внутри категории ≈ 0.0003 (шум от разных бинов)
- Нет доступа к ClinVar label → нет дискриминации

### Категории с обоими классами:

| Категория  | Pathogenic | Benign | Within-cat AUC возможен?        |
| ---------- | ---------- | ------ | ------------------------------- |
| intronic   | 9          | 658    | n=9 слишком мало (нужно ≥20-30) |
| synonymous | 3          | 83     | n=3 бессмысленно                |
| other      | 12         | 7      | Маргинально (n=19)              |
| missense   | 125        | 0      | Невозможно (нет benign)         |
| nonsense   | 40         | 0      | Невозможно                      |

### Рекомендации:

**Для v1.0 (текущий manuscript):**

- Рефрейминг: "Perfect separation reflects category-level structural impact model, not independent prediction"
- Добавить Limitations: "Position-dependent refinement within categories is planned for v2.0"

**Для v2.0:**

- Добавить CTCF-proximity scaling: `impact = base_impact * f(distance_to_nearest_CTCF)`
- Добавить enhancer-distance модуляцию
- Тогда within-category ROC станет осмысленным тестом

### Ключевые источники:

- Vergara et al. 2008 (Bioinformatics) — small-sample AUC unreliability
- Feng et al. 2017 (Stat Methods Med Res) — 29 методов CI для малых выборок
- POSTRE (Sanchez-Gaya 2023, NAR) — closest existing tool to ARCHCODE
- Akdemir et al. 2020 (Genome Biology) — TAD Fusion Score

---

## Направление 2: K562 Micro-C + CUT&Tag

### Вердикт: Данные доступны, два пути загрузки

### Быстрый путь (~1 час до результата):

1. Скачать `4DNFI18UHVRO.mcool` (7.92 GB, готовый mcool, K562 Hi-C)
   - URL: `https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/230ad652-0232-47f2-97ef-296c7a040bd9/4DNFI18UHVRO.mcool`
2. Скачать CTCF peaks (ENCFF660GHM, ~1 MB)
3. Скачать MED1 peaks (ENCFF882ZEN, ~1 MB)
4. Извлечь HBB и SOX2 регионы через `cooler`

### Оптимальный путь (лучшая наука):

1. Скачать GSE206131 K562 Micro-C pairs (~10-20 GB)
   - Barshad et al. 2024, eLife — настоящий Micro-C (MNase), 250bp resolution
   - URL: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE206nnn/GSE206131/suppl/GSE206131_K562_cis_mapq30_pairs.txt.gz`
2. Построить mcool на 600bp resolution (совпадает с ARCHCODE)
3. Извлечь оба региона с balanced normalization

### ChIP-seq данные:

| Target | Accession                      | Peaks            | Quality              |
| ------ | ------------------------------ | ---------------- | -------------------- |
| CTCF   | ENCSR000EGM (Snyder, Stanford) | 58,684 IDR peaks | Excellent            |
| MED1   | ENCSR269BSA (Myers, HAIB)      | 1,497 peaks      | Moderate (low count) |

### Micro-C vs Hi-C для 30kb окна:

| Свойство                | Hi-C (MboI)         | Micro-C (MNase)          |
| ----------------------- | ------------------- | ------------------------ |
| Фрагменты               | 200-500 bp          | ~150 bp (мононуклеосома) |
| Практическое разрешение | 1-5 kb              | 200 bp - 1 kb            |
| Sub-TAD features        | Едва видны          | Чётко разрешены          |
| Для 30kb/600bp          | Маргинальный сигнал | Хороший сигнал           |

**Рекомендация:** Micro-C (GSE206131) сильно предпочтительнее. Один файл покрывает оба локуса (HBB + SOX2).

### Python код извлечения:

```python
import cooler
import numpy as np

clr = cooler.Cooler('K562_MicroC_600bp.cool')

# HBB region
hbb = clr.matrix(balance=True).fetch('chr11:5,210,000-5,240,000')
np.save('data/reference/HBB_MicroC_K562_600bp.npy', hbb)

# SOX2 region (same file!)
sox2 = clr.matrix(balance=True).fetch('chr3:181,500,000-181,850,000')
np.save('data/reference/SOX2_MicroC_K562_600bp.npy', sox2)
```

### Ключевые источники:

- Barshad et al. 2024, eLife — K562 Micro-C dataset
- Krietenstein et al. 2020, Molecular Cell — Micro-C methodology
- 4D Nucleome: 4DNESI7DEJTM — K562 Hi-C mcool
- ENCODE: ENCSR000EGM (CTCF), ENCSR269BSA (MED1)

---

## Направление 3: Bayesian Cross-Locus Validation

### Вердикт: Optuna 4.7.0, реалистичные цели r=0.35-0.55

### Выбор библиотеки:

| Библиотека      | Статус                        | Рекомендация     |
| --------------- | ----------------------------- | ---------------- |
| scikit-optimize | **МЁРТВ** (archived Feb 2024) | НЕ использовать  |
| Optuna 4.7.0    | Активно развивается           | **Рекомендован** |
| BoTorch (Meta)  | Тяжёлый (PyTorch)             | Избыточно        |

### Optuna GPSampler:

```python
import optuna

def objective(trial):
    alpha = trial.suggest_float('alpha', 0.5, 1.5)
    gamma = trial.suggest_float('gamma', 0.5, 1.2)
    k_base = trial.suggest_float('k_base', 0.0005, 0.01, log=True)

    # Run ARCHCODE simulation with these params
    # Compare with Micro-C reference
    r = compute_correlation(alpha, gamma, k_base, reference_matrix)
    return -r  # minimize negative correlation

study = optuna.create_study(sampler=optuna.samplers.GPSampler())
study.optimize(objective, n_trials=100)  # ~3 min on CPU
```

### Реалистичные ожидания:

| Метрика                   | HBB (training) | SOX2 (validation) |
| ------------------------- | -------------- | ----------------- |
| Pearson r                 | 0.35 — 0.55    | 0.20 — 0.30       |
| Для сравнения: Akita (ML) | 0.61           | —                 |
| Текущий v1.0              | 0.16 (p=0.30)  | N/A               |

### Objective function: рекомендация

- **Pearson correlation** — интерпретируемая, стандартная
- L2 distance — чувствительна к масштабу
- SSIM — подходит, но совпадает с нашей основной метрикой (circular)

### Anti-overfitting протокол:

1. Параметры фитятся **только на HBB**
2. SOX2 — **другая хромосома**, другой ген, другая архитектура
3. Код коммитится **ДО** запуска валидации (git timestamp = pre-registration)
4. 100 trials × 3 параметра = разумное пространство поиска

### Ключевые источники:

- Optuna docs: https://optuna.readthedocs.io/
- GPSampler: Gaussian Process-based Bayesian optimization in Optuna
- Akita (Fudenberg et al. 2020, Nature Methods) — benchmark: r≈0.61

---

## Направление 4: TDA (Persistent Homology)

### Вердикт: Быстрый proof-of-concept (30 мин), не блокировать v2.0

### Рекомендованный стек:

```bash
pip install ripser persim  # минимальный, prebuilt wheels для Windows
```

### Почему H1 (loops), а не H0:

- H0 = connected components (когда регионы объединяются) — менее информативно
- **H1 = cycles/loops** — напрямую ловит петли хроматина (cohesin loops)
- H2 = voids — избыточно для 50×50 матриц

### Преобразование контактной матрицы → фильтрация:

```python
D = 1.0 - (C / C.max())  # distance = 1 - normalized contact
np.fill_diagonal(D, 0)
result = ripser(D, maxdim=1, distance_matrix=True)
```

### Wasserstein distance vs Bottleneck:

- **Wasserstein (order=1)** — суммирует ВСЕ различия → рекомендован
- Bottleneck — только самое большое различие → менее информативен

### Вычислительная стоимость:

- 50 точек, Rips complex до dim=1: **< 1 мс** на матрицу
- Wasserstein для 5-10 точек: **< 0.1 мс**
- **Весь батч 1,103 варианта: 1-2 секунды**

### Ключевой тест: bin-shift robustness

- Петля сдвинута на 1 бин (600 bp): SSIM значительно падает, TDA distance ≈ 0
- Петля удалена полностью: SSIM падает, TDA distance >> 0
- Если подтвердится → TDA добавляет реальную value

### Ожидаемая корреляция с SSIM:

- r(SSIM, Wasserstein) ~ 0.6-0.8
- Если r < 0.85 → TDA добавляет информацию, включаем
- Если r > 0.9 → отложить (дублирует SSIM)

### Единственная публикация TDA + Hi-C:

- Emmett, Schweinhart & Rabadan (2015) — "Multiscale Topology of Chromatin Folding" (arXiv:1511.01426)

### Ключевые источники:

- ripser.py: https://github.com/scikit-tda/ripser.py
- persim: https://github.com/scikit-tda/persim
- Emmett et al. 2015, arXiv:1511.01426
- Otter et al. 2017, EPJ Data Science (TDA roadmap)
- Kokkanti et al. 2024, J. Chem. Phys. (TopoLoop)

---

## Направление 5: Масштабирование на дополнительные локусы

### Вердикт: CFTR (#1) + SOX2 (#2). MYC отклонён.

### ВАЖНАЯ КОРРЕКЦИЯ: SOX2 ≠ EPHA4

- **SOX2** = chr3:181,711,925-181,714,436 (анофтальмия)
- **EPHA4** = chr2 (Lupiáñez et al. 2015, пороки конечностей)
- Это **разные гены на разных хромосомах**

### Рейтинг локусов:

| #     | Локус    | Chr | ClinVar | TAD     | Плюсы                                                   | Минусы                                      |
| ----- | -------- | --- | ------- | ------- | ------------------------------------------------------- | ------------------------------------------- |
| **1** | **CFTR** | 7   | ~4,200  | ~317 kb | Богатый ClinVar, 5C данные, инвариантные TAD boundaries | Большой ген (429 kb)                        |
| **2** | **SOX2** | 3   | ~150    | ~350 kb | Уже частично реализован, super-enhancer, gene desert    | Мало вариантов                              |
| ✗     | MYC      | 8   | ~30-50  | 2.8 Mb  | —                                                       | TAD слишком большой, нет germline вариантов |

### CFTR — Tier 1 (рекомендован):

- **~4,200 ClinVar вариантов** (300+ pathogenic, 300-500 benign) — отличный ROC
- Smith & Dekker 2016: 5C данные, 6 TAD boundaries, все ко-локализуются с CTCF
- CTCF сайты: -80.1 kb, -20.9 kb, +6.8 kb, +48.9 kb (хорошо документированы)
- TAD ~317-400 kb → 400 bins при 1000 bp resolution

```json
{
  "name": "CFTR",
  "chromosome": "chr7",
  "start": 117100000,
  "end": 117500000,
  "resolution_bp": 1000,
  "bins": 400
}
```

### SOX2 — Tier 2 (рекомендован):

- Уже частично реализован (`validation_sox2.json`, 8 CTCF sites)
- SCR super-enhancer ~100 kb от гена
- CTCF-независимый enhancer контакт (Oudelaar 2022) — уникальный тест
- Мало ClinVar вариантов → фокус на корреляции с 4C/5C, не ROC

```json
{
  "name": "SOX2",
  "chromosome": "chr3",
  "start": 181500000,
  "end": 181850000,
  "resolution_bp": 1000,
  "bins": 350
}
```

### Портфолио v2.0:

| Локус | Chr | Окно   | Bins | Механизм                         | Приоритет   |
| ----- | --- | ------ | ---- | -------------------------------- | ----------- |
| HBB   | 11  | 30 kb  | 50   | Insulator/LCR                    | v1.0 (done) |
| CFTR  | 7   | 400 kb | 400  | Invariant TAD + tissue enhancers | v2.0 #1     |
| SOX2  | 3   | 350 kb | 350  | Super-enhancer в gene desert     | v2.0 #2     |

### Ключевые источники:

- Smith & Dekker 2016, Am J Hum Genet — CFTR 5C, invariant TADs
- Alexander et al. 2019, eLife — SOX2 enhancer-promoter dynamics
- Oudelaar et al. 2022, Genes Dev — SOX2 CTCF-independent architecture
- Lupiáñez et al. 2015, Cell — EPHA4 TAD boundary disruption (НЕ SOX2)
- ENCODE: ENCSR000EGM (CTCF K562), ENCSR000AKP (H3K27ac K562)

---

## ТОП-5 ДЕЙСТВИЙ (80/20)

### 1. Унифицировать пайплайн (КРИТИЧНО)

- **Что:** Прогнать все 1,103 варианта через один TypeScript пайплайн
- **Критика:** #1 (Circular AUC) — устраняет артефакт разных пайплайнов
- **Результат:** Честный AUC (вероятно < 1.0 но > 0.5 за счёт категорий)
- **Время:** 1-2 дня
- **Зависимости:** Нет
- **Риск:** AUC сильно упадёт → честно раскрыть

### 2. Скачать K562 Micro-C + CTCF/MED1 ChIP-seq

- **Что:** 4DNFI18UHVRO.mcool (быстро) или GSE206131 pairs (лучше)
- **Критика:** #2 (GM12878 ≠ erythroid)
- **Результат:** Hi-C r > 0.3 (целевая) с K562 вместо GM12878
- **Время:** 1-2 дня (скачивание + обработка)
- **Зависимости:** Нет
- **Риск:** r всё ещё < 0.3 → модель фундаментально ограничена

### 3. Bayesian fit на HBB → predict SOX2

- **Что:** Optuna GPSampler, 100 trials, 3 параметра (α, γ, k_base)
- **Критика:** #3 (Ручная калибровка)
- **Результат:** HBB training r > 0.35, SOX2 validation r > 0.2
- **Время:** 1 неделя
- **Зависимости:** Действие 2 (нужны Micro-C данные)
- **Риск:** SOX2 r < 0.15 → модель не generalize

### 4. Настроить CFTR локус

- **Что:** Config + CTCF sites + ClinVar variants для CFTR
- **Критика:** Generalizability (один локус → три)
- **Результат:** CFTR ROC AUC с ~4,200 вариантами
- **Время:** 1 неделя
- **Зависимости:** Действие 3 (параметры из Bayesian fit)
- **Риск:** CFTR TAD (400 kb) слишком большой для модели

### 5. TDA proof-of-concept

- **Что:** ripser + persim, bin-shift тест, корреляция с SSIM
- **Критика:** #5 (Упрощённая физика — дополнительная метрика)
- **Результат:** r(SSIM, Wasserstein) < 0.85 → TDA добавляет value
- **Время:** 2-3 часа
- **Зависимости:** Нет
- **Риск:** r > 0.9 → TDA дублирует SSIM, откладываем

---

## Timeline v2.0 (4-6 недель)

```
Неделя 1: [Действие 1] Унификация пайплайна + [Действие 2] Скачивание данных
Неделя 2: [Действие 5] TDA PoC + начало [Действие 3] Bayesian fit
Неделя 3: [Действие 3] завершение + валидация SOX2
Неделя 4: [Действие 4] CFTR config + симуляция
Неделя 5: Интеграция результатов + обновление manuscript
Неделя 6: Буфер + ревизия препринта на bioRxiv
```

---

## Честная оценка рисков

| Сценарий          | Вероятность | Последствие                             | Как раскрыть                                       |
| ----------------- | ----------- | --------------------------------------- | -------------------------------------------------- |
| Unified AUC < 0.7 | Высокая     | AUC теряет "wow factor"                 | "Category-level model by design"                   |
| K562 Hi-C r < 0.3 | Средняя     | Модель не валидирована экспериментально | "Motivates higher-resolution physics"              |
| SOX2 r < 0.15     | Средняя     | Нет cross-locus generalization          | "Single-locus tool with acknowledged limits"       |
| 0 pearls в CFTR   | Низкая      | Нет клинической находки                 | "Absence of structural pearls is also informative" |
| TDA ≈ SSIM        | Высокая     | TDA не добавляет value                  | Не включать, упомянуть как explored                |
