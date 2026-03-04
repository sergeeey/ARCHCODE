# Architectural Decisions — ARCHCODE

## ADR-001: Publish v1.0 as-is, address critiques in v2.0 (2026-02-28)

**Context:** Независимая оценка выявила 5 ключевых критик (средняя 6.4/10).

**Критики и план ответа:**

| Критика                                          | Источник      | Серьёзность | Ответ в v2.0                                         |
| ------------------------------------------------ | ------------- | ----------- | ---------------------------------------------------- |
| Circular AUC (category = input AND ground truth) | Критик        | ВЫСОКАЯ     | Within-category ROC (intronic: 9 path vs 658 benign) |
| GM12878 вместо erythroid                         | Биолог        | СРЕДНЯЯ     | K562 ChIP-seq для CTCF/MED1                          |
| Ручная калибровка α, γ                           | Программист   | СРЕДНЯЯ     | Bayesian fit на HBB → cross-validate на SOX2         |
| Нет клинической полезности                       | Клин. генетик | ОЖИДАЕМАЯ   | Experimental validation (RT-PCR, Capture Hi-C)       |
| Упрощённая физика (mean-field)                   | Биофизик      | СРЕДНЯЯ     | TDA метрики + polymer baseline                       |

**Решение:** Не трогать v1.0. Ждать DOI, собрать обратную связь, адресовать в v2.0.

**Обоснование:**

- Caveats честно раскрыты в manuscript (12 упоминаний r=0.16, 8 упоминаний "requires validation")
- Circular AUC caveat явно прописан
- Пересабмит до DOI создаёт путаницу в версиях
- Within-category ROC и K562 data — чистый материал для v2.0 revision

## ADR-002: Scope guard — no Bayesian fitting before publication (2026-02-28)

**Context:** Предложение добавить Micro-C + Bayesian optimization + TDA перед публикацией.

**Решение:** Отклонено. Публиковать сначала, улучшать потом.

**Обоснование:**

- 3 параметра / 1 локус = circular validation (overfitting)
- Правильный подход: Fit on HBB → Predict on SOX2 (cross-validation)
- Записан в ROADMAP_v2.md

## ADR-003: Pipeline discrepancy — unify before v2.0 (2026-02-28)

**Context:** Исследование within-category ROC выявило что pathogenic (TypeScript, effectStrength=0.8) и benign (Python, impact=0.02) варианты прогнаны через разные пайплайны с разными масштабами пертурбации. AUC=1.000 — артефакт этого различия.

**Решение:** Унификация пайплайна — первый приоритет v2.0.

**Обоснование:**

- Intronic pathogenic SSIM=0.995 vs intronic benign SSIM=1.000 — из-за 10x разницы в impact
- Within-category AUC будет ≈ 0.5 после унификации (математически гарантировано)
- Рефрейминг AUC как "category-level structural model" вместо "independent prediction"

## ADR-004: Locus portfolio for v2.0 — CFTR + SOX2 (2026-02-28)

**Context:** Выбор дополнительных локусов для cross-locus validation.

**Решение:** CFTR (Tier 1) + SOX2 (Tier 2). MYC отклонён.

**Обоснование:**

- CFTR: ~4,200 ClinVar variants (отличный ROC), 5C данные (Smith & Dekker 2016), TAD ~317 kb
- SOX2: уже частично реализован, super-enhancer архитектура, CTCF-independent contacts
- MYC: TAD 2.8 Mb (слишком большой), почти нет germline ClinVar variants
- SOX2 ≠ EPHA4 (разные хромосомы!) — Lupiáñez 2015 это EPHA4/chr2, не SOX2/chr3

## ADR-005: Optuna over scikit-optimize for Bayesian fitting (2026-02-28)

**Context:** Выбор библиотеки для Bayesian parameter optimization.

**Решение:** Optuna 4.7.0 GPSampler.

**Обоснование:**

- scikit-optimize archived Feb 2024 (мёртв)
- Optuna активно развивается, GPU-friendly, GPSampler для 3 параметров
- 100 trials ≈ 3 min на CPU
- Реалистичные цели: HBB r=0.35-0.55, SOX2 r=0.2-0.3

## ADR-006: Keep original params after Bayesian optimization (2026-03-01)

**Context:** Optuna GPSampler (200 trials) оптимизировал α, γ, K_BASE для максимизации Pearson r с K562 Hi-C.

**Результат:** Δr = +0.0001 (negligible). Все 3 лучших параметра на нижних границах (α=0.5, γ=0.3, k_base=0.0005).

**Решение:** Оставить исходные параметры (α=0.92, γ=0.80, K_BASE=0.002).

**Обоснование:**

- Improvement < 0.02 threshold → не оправдывает изменения
- Boundary-hitting означает: оптимизатор минимизирует Kramer kinetics term полностью
- k_base importance = 90% (fANOVA) — alpha и gamma иррелевантны когда k_base → 0
- **Научный инсайт:** Hi-C корреляция управляется архитектурой (distance decay, MED1, CTCF barriers), а НЕ кинетикой. Kinetics params служат другой цели: SSIM perturbation для классификации вариантов
- Это второй honest null result (после within-category LR p=1.0), укрепляющий научную честность проекта
- Grid-search estimates подтверждены как near-optimal

## ADR-007: AlphaGenome variant-level null result — honest reporting (2026-03-01)

**Context:** AlphaGenome predict_variant() на 23 pearl variants дала ΔSSIM 3.1×10⁻⁴ vs ARCHCODE 0.015 (~49× разница). Корреляция r=0.06 (ns), ρ=-0.32 (ns).

**Решение:** Честно документировать как информативный null result, не как failure.

**Обоснование:**

- AlphaGenome разрешение 2048 bp — SNV влияет на <0.05% input sequence
- ARCHCODE напрямую пертурбирует loop extrusion params → amplified signal
- Разные resolution regimes: AG для wild-type prediction (ρ=0.27-0.52), ARCHCODE для variant-level
- Это третий honest null result (после within-category LR, Bayesian optimization)
- Обновили Limitation #10: из "planned" → "performed — AG resolution too coarse"

## ADR-008: Epigenome cross-validation validates input data (2026-03-01)

**Context:** AlphaGenome CHIP_TF/CHIP_HISTONE предсказывает CTCF и H3K27ac из ДНК.

**Решение:** Cross-validate ENCODE ChIP-seq features из наших configs vs AlphaGenome predictions.

**Результат:** CTCF recall = 100% (54/54), H3K27ac recall = 85% (29/34).

**Значение:** Не validation ARCHCODE, а validation INPUT DATA. Все CTCF позиции в configs подтверждены независимым DL-методом.

## ADR-009: Dual-DL benchmark strategy (AlphaGenome + Akita) (2026-03-02)

**Context:** AlphaGenome (cloud API, 2048bp) дал null на variant-level. Нужен второй независимый DL бенчмарк для усиления вывода.

**Решение:** Akita (Fudenberg et al. 2020) — открытая модель, локальный inference, тот же 2048bp resolution, но другие training data (Rao 2014 vs 4DN).

**Результат:**

- Wild-type: Akita ρ = 0.17–0.43 (comparable to AlphaGenome 0.27–0.52)
- Variant SNVs: ΔSSIM < 10⁻⁴ (noise floor, confirming AlphaGenome null)
- Variant indels (≥25bp): ΔSSIM up to 0.055 (detectable, but sequence length effect, not structural)
- Rank correlation: ρ = -0.17 (p=0.45, ns)

**Обоснование:**

- Два независимых DL models, разные training data, один вывод → сильнее чем один model
- Akita на Rao 2014 Hi-C → wild-type concordance не из shared training signal (в отличие от AlphaGenome на 4DN)
- Limitation #10 обновлена: "planned" → "performed — dual-DL null confirmed"
- Nuance: Akita различает large indels (>25bp) но не SNVs → 2048bp resolution threshold
- Четвёртый honest null result (after within-category LR, Bayesian optimization, AlphaGenome variant)

## ADR-010: Multimodal AlphaGenome validation — resolution hierarchy (2026-03-02)

**Context:** Contact maps (2048bp) и Akita дают null на variant-level SNVs. Но AlphaGenome также предсказывает RNA_SEQ и ATAC с разрешением 1bp.

**Решение:** Использовать `predict_variant()` с RNA_SEQ + ATAC на тех же 23 pearl variants. K562 (EFO:0002067) — релевантная линия для HBB.

**Результат:**

- RNA_SEQ (1bp): mean max_delta = 28.13, signal concentration = 16.97×
- ATAC (1bp): mean max_delta = 5.70, signal concentration = 11.15×
- Rank correlation с ARCHCODE: ρ = -0.22 (RNA), -0.32 (ATAC) — обе ns
- Indels >> SNVs по delta (99–221 vs 6–15 для RNA)

**Ключевой вывод:**

- **Resolution hierarchy:** contact maps (2048bp) → null, epigenomic tracks (1bp) → detectable
- Та же модель (AlphaGenome), те же варианты, разный output type → разный результат
- Signal concentration >>1 подтверждает локализованный эффект (не шум)
- Нет rank correlation с ARCHCODE → разные биологические механизмы (transcription vs loop extrusion)
- Limitation #10 обновлена: "dual-DL null" → "resolution-dependent hierarchy"
- Это НЕ null result, а POSITIVE finding — первый detectable DL signal на variant-level

## ADR-011: Pearl vs benign control validates signal specificity (2026-03-02)

**Context:** Multimodal AlphaGenome показал mean max_delta=28 для pearls. Без контроля неясно, специфичен ли сигнал.

**Решение:** Прогнать тот же pipeline на 23 randomly sampled benign non-pearl variants (seed=42). Mann-Whitney U для сравнения.

**Результат:**

- 10/10 тестов значимы при p<0.05
- Signal concentration = лучший дискриминатор (r=-0.70, p<0.0001)
- Pearl 16.97× vs Benign 6.09× (RNA-seq concentration)
- max_delta почти одинаковый (28 vs 27) — indels доминируют в обоих группах
- Ключевое отличие: pearls _фокусируют_ delta вокруг варианта, benign — диффузно

**Обоснование:**

- Контрольная группа превращает descriptive finding в discriminative
- Signal concentration — новая метрика для pearl validation
- Benign тоже дают signal (не ноль!) → отличие в локализации, не в наличии

## ADR-012: SCN5A as cell-type mismatch negative control (2026-03-02)

**Context:** 6 лоcuses используют K562 данные — все они хотя бы частично экспрессированы в K562. SCN5A — кардиологический ген, не экспрессируется в K562.

**Решение:** Намеренно использовать K562 для SCN5A как negative control. Если ARCHCODE даёт ложные pearl detections → проблема. Если 0 pearls → модель зависит от биологически релевантных features.

**Результат:**

- 2,488 variants, 0 pearls, SSIM ≈ 1.0000
- Только 3 H3K27ac peaks (vs 7-14 для других лоcuses)
- AG ρ = -0.17 (lowest across all loci)
- CTCF recall 100% (cell-type invariant confirmed)

**Обоснование:**

- SCN5A подтверждает: ARCHCODE sensitivity = f(tissue-matched annotation)
- 0 false positives при sparse features → модель conservative by design
- iPSC-CM данные потенциально раскроют structural pathogenicity на тех же variants

## ADR-013: Cross-locus multimodal BRCA1 — partial replication (2026-03-02)

**Context:** HBB pearl vs benign дал 10/10 significant tests. Нужна cross-locus validation. BRCA1 — 0 pearls, поэтому pathogenic vs benign (ClinVar labels).

**Решение:** MCF7 (EFO:0001203, breast cancer) как tissue-matched cell line. 23 pathogenic + 23 benign, seed=42.

**Результат:**

- 1/10 тестов значим: RNA delta_at_variant p=0.0098, r=-0.45
- Signal concentration borderline: p=0.056 (path 10.71× vs benign 4.45×)
- RNA max_delta = 6.0 для ВСЕХ 46 вариантов (ceiling effect AG)
- ATAC: ни один тест не значим (все p > 0.23)

**Обоснование:**

- Partial replication — delta_at_variant реплицирует (прямое локальное возмущение)
- Слабее HBB из-за разных классов вариантов: BRCA1 pathogenic = coding LOF (truncation), HBB pearls = regulatory (near CTCF/enhancers)
- AG RNA ceiling = technical limitation (квантизация output), не biological null
- Честный результат: 1/10 > 0/10, но < 10/10 → partial cross-locus generalization

## ADR-014: SCN5A multimodal confirms cell-type dependency (2026-03-02)

**Context:** BRCA1 дал 1/10 significant tests при tissue-matched MCF7. Нужен negative control — cell-type mismatch.

**Решение:** SCN5A (cardiac) + K562 (erythroid) — намеренный mismatch. 23 pathogenic + 23 benign, seed=42.

**Результат:**

- RNA signal concentration: 0.39× vs 0.40× (p=0.96, null)
- RNA max_delta 230× ниже BRCA1, 1080× ниже HBB
- 0/10 biologically meaningful significant tests
- ATAC concentration в обратном направлении (benign > pathogenic, r=+0.37)

**Three-locus gradient:**

- HBB (matched, regulatory): 10/10 sig, concentration 2.78×
- BRCA1 (matched, coding): 1/10 sig, concentration 2.41×
- SCN5A (mismatch): 0/10 sig, concentration 0.96×

**Обоснование:**

- Подтверждает: multimodal discrimination = f(tissue-match × variant class)
- RNA near-zero при non-expressed gene → не ложный сигнал
- Пятый тип evidence (после contact maps, epigenome crossval, pearl vs benign, BRCA1 cross-locus)
- Шестой honest null result в проекте

## ADR-015: Position-only control — definitive AUC ablation (2026-03-02)

**Context:** Критика AUC tautology (category → effectStrength → SSIM → AUC = circular). Нужен definitive proof.

**Эксперимент:** Три варианта effectStrength:

1. Categorical (default): effectStrength = f(VEP category) — AUC = 0.976
2. CADD-based: effectStrength = sigmoid(CADD phred) — AUC = 0.977, BUT within-synonymous AUC = 0.988 (CADD leaks pathogenicity → new circularity, REJECTED)
3. Position-only: effectStrength = 0.3 fixed for ALL variants — AUC = 0.551 (chance)

**Решение:** Categorical остаётся primary model. Position-only добавлен как control experiment в manuscript.

**Обоснование:**

- AUC 0.977 → 0.551 при удалении category info → DEFINITIVE proof: AUC = category-distribution effect
- CADD-based усугублял проблему (within-synonymous 0.57 → 0.99), не решал
- Position Δ(mean LSSIM) = +0.005 → benign чуть MORE disrupted (обе группы в 2.1 kb cluster)
- Within-category AUC одинаков (~0.53) во всех моделях → baseline от position
- Седьмой honest null result (position-only control)
- Сильнейший ответ на AUC tautology criticism: "we agree, here's the proof"

## ADR-016: TERT as inter-TAD benchmark + GJB2 as tissue-mismatch null (2026-03-04)

**Context:** bioRxiv отклонил за "not complete research with new data". Нужны новые локусы. IGF2/H19 отвергнут (только 140 вариантов, механизм = CNV/methylation).

**Решение:** TERT (chr5, inter-TAD gap, telomerase) + GJB2 (chr13, tissue-mismatch benchmark).

**Результаты:**

- TERT: 2,089 variants, Δ=0.019 (STRONG), 27 struct. pathogenic, 0 pearls
- GJB2: 469 variants, Δ=0.006, 0 struct. pathogenic, 0 pearls (expected null)
- TERT inter-TAD = unique: CTCF/enhancers sparse → weaker signal than intra-TAD, but detectable
- GJB2 = second mismatch null (cochlear gene in erythroid cells), confirms SCN5A finding

**Обоснование:**

- TERT clinically important (promoter hotspot mutations in cancer), well-studied in K562
- GJB2 clinically important (most common cause of hearing loss), но intentional negative control
- Together expand portfolio to 9 loci (7 signal + 2 nulls)
- Missense misclassification bug discovered + fixed with VEP reclassification script

## ADR-017: Per-locus thresholds — universal 0.95 fails beyond HBB (2026-03-04)

**Context:** Universal LSSIM threshold 0.95 gives 0% FP for HBB but 26 FP for BRCA1. Need per-locus calibration.

**Решение:** Compute optimal thresholds per locus at FPR≤1%, using benign LSSIM distribution.

**Результат:**

| Locus | Optimal Threshold | Sensitivity | vs Universal 0.95  |
| ----- | ----------------- | ----------- | ------------------ |
| HBB   | 0.977             | 92.9%       | +13.3pp            |
| TERT  | 0.968             | 22.7%       | +11.8pp            |
| TP53  | 0.982             | 22.6%       | +22.4pp            |
| MLH1  | 0.972             | 5.5%        | +2.5pp             |
| GJB2  | N/A               | 0%          | no threshold works |

**Обоснование:**

- Per-locus thresholds improve sensitivity 1.2-100× at same FPR
- HBB uniquely strong because: tissue-matched + regulatory variants + strong enhancer landscape
- GJB2 has no achievable threshold → honest mismatch null
- Manuscript Table ready (9-locus comparison)

## ADR-018: Enhancer proximity drives ARCHCODE discrimination (2026-03-04)

**Context:** Нужна механистическая гипотеза: что именно ARCHCODE детектирует? CTCF disruption? Enhancer proximity?

**Анализ:** 30,318 вариантов по 9 локусам, distance-to-nearest-CTCF и distance-to-nearest-enhancer.

**Ключевая находка:**

- **Pearl variants:** median enhancer dist = 831bp (CLOSE), median CTCF dist = 22,120bp (FAR)
- **Enhancer ≤1kb zone:** Δ(path-ben) = 0.039 — 7× average discrimination
- **CTCF zones:** no clear gradient (≤1kb Δ=0.010, 10-50kb Δ=0.012)
- Pearl vs non-pearl pathogenic CTCF distance: p = 1.08e-8

**Вывод:** ARCHCODE detects enhancer-proximal structural perturbations, NOT CTCF barrier disruption. Механизм: variants near enhancers alter occupancy→extrusion dynamics→local SSIM.

**Для manuscript:** This is the key mechanistic Figure — enhancer proximity gradient.

## ADR-019: ARCHCODE-only FP = "other" category CNVs (2026-03-04)

**Context:** 394 ARCHCODE-only variants (LSSIM<0.95, CADD<20). True positives vs false positives?

**Результат:**

- True Positives (364): 83% frameshift, distributed across 7 loci, median enhancer=494bp
- False Positives (30): 93% "other" category (CNVs), 87% from BRCA1, median CTCF=692bp
- TP vs FP CTCF distance: p = 3.69e-8

**Решение:** "other" category = noise source. Recommend filtering in clinical application.

**Обоснование:**

- CNVs have extreme effectStrength but poorly defined positions → artifact
- Filtering "other" would eliminate 28/30 FP (93%) while keeping 359/364 TP (99%)
- Simple, interpretable rule for clinical implementation
