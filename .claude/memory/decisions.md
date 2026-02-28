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
