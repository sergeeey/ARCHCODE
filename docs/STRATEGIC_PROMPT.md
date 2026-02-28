# ARCHCODE Strategic Development Prompt v1.0

## Как использовать

Этот промпт — самодостаточный контекстный документ. Вставь его в начало
сессии с любой LLM (Claude, GPT-4, Gemini) для стратегического планирования
развития проекта ARCHCODE. Содержит реальные метрики, честные ограничения,
и конкретные пути монетизации.

---

## КОНТЕКСТ ПРОЕКТА

### Что такое ARCHCODE

ARCHCODE (Architecture-Constrained Decoder) — аналитический симулятор
петлевой экструзии хроматина. Предсказывает как точечные мутации нарушают
3D-структуру генома через модель когезин-CTCF взаимодействий.

**Формула ядра:**

```
P_unload = k_base × (1 - α × MED1^γ)
C(i,j) = |i-j|^(-1) × sqrt(occ_i × occ_j) × Π(ctcf_perm) × kramer_mod(i,j)
```

**Ключевое отличие от конкурентов:** аналитический (не стохастический),
детерминированный, <1 секунды на вариант, не требует GPU. Enformer и Akita
требуют GPU и предсказывают контактные карты, но не классифицируют варианты.
ARCHCODE делает и то, и другое.

### Валидированные метрики (реальные, не синтетические)

| Метрика                | HBB (95kb)                   | CFTR (317kb)              |
| ---------------------- | ---------------------------- | ------------------------- |
| ClinVar варианты       | 1,103 (353 P + 750 B)        | 3,349 (1,756 P + 1,593 B) |
| ROC AUC                | 0.977                        | не вычислялся (нужен)     |
| Hi-C корреляция (K562) | r=0.53 (30kb), r=0.59 (95kb) | нет Hi-C данных           |
| Pearl варианты         | 20 (VEP<0.30 + SSIM<0.95)    | 0 (SSIM dilution)         |
| Within-category LR     | ΔAUC=-0.001, p=1.0           | ΔAUC=+0.007, p=1.0        |

### Честные ограничения (не скрывать)

1. **~35% дисперсии объяснено** — r=0.59 означает R²≈0.35. Остальные 65% —
   polymer physics, compartments, non-CTCF loops
2. **Category-level classifier** — предсказывает по категории (nonsense vs
   synonymous), НЕ внутри категории. Доказано на 2 локусах.
3. **Нет missense sensitivity** — 0/125 missense детектированы. Для missense
   нужен AlphaFold/ESM, не хроматин
4. **SSIM dilution** — при 317×317 матрицах SSIM сжимается до 0.9948-1.0000,
   теряя разрешающую способность
5. **Нет экспериментальной валидации** — pearl варианты не подтверждены RT-PCR
6. **Bayesian null** — Optuna (200 trials) показала Δr=+0.0001. Параметры
   кинетики нерелевантны для Hi-C корреляции (k_base importance=90%)

### Реальные сильные стороны

1. **Скорость** — 1,103 варианта за 50 секунд на CPU. Можно скринить миллионы
2. **Прозрачность** — аналитическая формула, не чёрный ящик. Каждый результат
   воспроизводим (seed=2026)
3. **Научная честность** — 2 honest null results опубликованы, это редкость
4. **Параметризованный pipeline** — добавление нового локуса = 1 JSON config
5. **Уникальная ниша** — pearl detection (VEP-blind + structurally disruptive)
   не делает никто
6. **bioRxiv preprint** — опубликован, DOI есть

---

## СТРАТЕГИЧЕСКИЕ ПУТИ РАЗВИТИЯ

### PATH A: Научная платформа (Publication Machine)

**Цель:** 3-5 публикаций за 12 месяцев, построение научного авторитета

**Шаги:**

1. Масштабирование на ACMG 59 actionable genes (не "весь геном" — это хайп)
   - Tier 1 (есть Hi-C + много ClinVar): BRCA1, BRCA2, TP53, MLH1, MSH2
   - Tier 2 (много ClinVar, нет Hi-C): SCN5A, KCNQ1, LMNA, RYR1
   - Фильтр: ≥500 ClinVar variants AND TAD size 50-500 kb
2. Для каждого локуса: config → atlas → within-category test → Hi-C correlation
3. Публикация: "Cross-locus structural pathogenicity atlas" (Nature Methods target)

**80/20:** Скрипт автоматического подбора локусов (ClinVar density × 4DN Hi-C
availability) даст 80% value. Ручная настройка конфигов — оставшиеся 20%.

**Публикации:**

- Paper 2: "ARCHCODE Atlas: Structural pathogenicity across 20 disease loci"
- Paper 3: "Topological data analysis reveals persistent homology signatures
  of pathogenic chromatin disruption" (TDA/ripser)
- Paper 4: "Structural variant interpretation via analytical loop extrusion"
  (SVs — deletion/inversion effects on contact maps)
- Paper 5: "Population-specific 3D structural risk profiles" (gnomAD AF ×
  ARCHCODE SSIM per population)

### PATH B: Инструмент для исследователей (Open Source Leadership)

**Цель:** ARCHCODE как стандартный инструмент в toolbox геномики

**Шаги:**

1. NPM пакет: `npm install archcode` — CLI tool для любого локуса
2. Web demo: загрузи VCF → получи SSIM heatmap (Streamlit/Gradio, 1 день)
3. Bioconda recipe: `conda install -c bioconda archcode`
4. Galaxy toolshed integration (для биологов без CLI)

**80/20:** NPM пакет + web demo покрывают 80% пользователей. Galaxy/Bioconda
— long tail.

**Неочевидный ход:** Опубликовать ARCHCODE contact matrices как benchmarking
dataset для Enformer/Akita. Это позиционирует проект как инфраструктуру,
а не конкурента. Сообщество начнёт цитировать.

### PATH C: Коммерческая диагностика (Long-term, требует валидации)

**Цель:** B2B SaaS для генетических лабораторий

**Предусловия (без них — нереально):**

- ≥1 экспериментальная валидация pearl варианта (RT-PCR или Capture Hi-C)
- ≥10 локусов в атласе
- Регуляторное одобрение (CE-IVD или FDA 510(k) для software as medical device)

**Модель:**

- API: $0.10 per variant query (batch pricing для лабораторий)
- Report: $50 per patient panel (20 генов × все варианты)
- Enterprise: $5K/month unlimited access

**Неочевидный ход:** Не продавать диагностику напрямую. Продавать
приоритизацию для экспериментальной валидации. "Из 500 VUS в вашей
лаборатории, вот 12 которые стоит проверить первыми" — это не medical
device, это research tool. Меньше регуляторных барьеров.

### PATH D: AI-интеграция (Pragmatic, не хайповый)

**Цель:** ARCHCODE как feature в AI-pipeline, а не отдельный продукт

**Реалистичные интеграции:**

1. **ARCHCODE × AlphaFold Multimer** — белковая структура (AlphaFold) +
   хроматиновая структура (ARCHCODE) = полная структурная картина варианта.
   Для одного варианта: "AlphaFold говорит белок стабилен, но ARCHCODE
   показывает что 3D-контакт промотор-энхансер разрушен"
2. **ARCHCODE embeddings** — вектор SSIM-disruption по всем позициям как
   feature для gradient boosting классификатора (XGBoost). Input: VEP score
   - SSIM + distance features → output: refined pathogenicity
3. **Fine-tune small LM** — обучить маленькую модель (phi-3-mini) предсказывать
   SSIM из sequence context. Но только после 10+ локусов в training data.

**Что НЕ делать:**

- Не строить RAG на 2 локусах — это демо, не продукт
- Не "тренировать нейросеть на Байесовских результатах" — 200 trials это
  не dataset, это один эксперимент
- Не заявлять "AI-powered diagnostics" без экспериментальной валидации

### PATH E: Структурные варианты (Highest scientific impact, non-obvious)

**Цель:** Применить ARCHCODE к SVs (делеции, инверсии, транслокации)

**Почему это золотая жила:**

- SVs напрямую разрушают 3D-топологию (удаляют CTCF-сайты, инвертируют
  ориентацию мотивов, перемещают энхансеры)
- VEP практически бесполезен для non-coding SVs
- ARCHCODE может моделировать: "что произойдёт с контактной картой если
  удалить 50 kb между позициями X и Y?"
- Lupiáñez 2015 (EPHA4 inversions → limb malformations) — классический
  пример SV-mediated disease через 3D disruption
- Конкуренция минимальна: нет быстрых аналитических SV-интерпретаторов

**Реализация:**

1. Добавить `--sv deletion:start-end` и `--sv inversion:start-end` в pipeline
2. Для deletion: удалить bins из матрицы, пересчитать SSIM
3. Для inversion: перевернуть CTCF-ориентации в затронутом регионе
4. Валидация: Rao 2014 (Hi-C after CTCF deletion), Lupiáñez 2015

**80/20:** Deletion modeling покрывает 70% клинически значимых SVs. Инверсии
и транслокации — дополнительные 20%.

### PATH F: Фармакогеномика (Speculative but high-value)

**Цель:** Предсказать как генетические варианты в 3D-контексте влияют на
лекарственный ответ

**Логика:**

- CYP2D6, CYP3A4 (метаболизм лекарств) имеют сложную регуляторную архитектуру
- Вариант в энхансере CYP2D6 может не менять белок, но снижать экспрессию
  через разрушение 3D-контакта → медленный метаболизм → токсичность препарата
- ARCHCODE может предсказать: "этот вариант разрушает энхансер-промотер
  контакт CYP2D6 → потенциально poor metabolizer"

**Предусловие:** Hi-C данные для печени (HepG2 есть в ENCODE/4DN)

---

## ПРИОРИТИЗАЦИЯ (80/20)

### Следующие 30 дней (MVP)

1. **Автоматизация подбора локусов** — скрипт: ClinVar API → отфильтровать
   гены с ≥500 variants + TAD size 50-500 kb + наличие Hi-C в 4DN → ранжировать
2. **3-5 новых локусов** — BRCA1, TP53, MLH1 (cancer panel, максимум цитирований)
3. **TDA proof-of-concept** — ripser на HBB, получить persistence diagrams
4. **NPM пакет** — `npx archcode --locus BRCA1 --vcf variants.vcf`

### Следующие 90 дней

5. **SV modeling** — `--sv deletion` для HBB (валидация: γ-globin deletion)
6. **Web demo** — Streamlit, загрузка VCF, визуализация contact map
7. **Paper 2 submission** — multi-locus atlas (≥10 генов)

### Следующие 6 месяцев

8. **Experimental collaboration** — найти lab для RT-PCR валидации pearl
   вариантов (K562 cells)
9. **AlphaFold integration** — combined structural score
10. **Benchmarking dataset** — опубликовать contact matrices для Enformer/Akita

---

## НЕОЧЕВИДНЫЕ ВОЗМОЖНОСТИ

### 1. "Анти-pearl" анализ

Вместо поиска "VEP-blind but structurally disruptive" → искать "VEP-positive
but structurally benign". Это варианты где VEP предсказывает патогенность, но
3D-структура не нарушена. Потенциально: reclassification benign candidates.
**У нас уже есть данные** — Q3 quadrant (95 pathogenic by VEP, SSIM≥0.95).

### 2. Инверсия модели (Gene Therapy Design)

Вместо "given variant → predict disruption" →
"given desired contact pattern → what CTCF edits achieve it?"
CRISPR-teams могут использовать для planning regulatory edits.

### 3. Synthetic Lethality Screen

Два варианта по отдельности безвредны (SSIM≈1.0), но вместе разрушают
3D-контакт (SSIM<0.90). ARCHCODE может скринить пары за секунды.
Релевантно для compound heterozygosity в β-thalassemia.

### 4. Эволюционный анализ

Сравнить SSIM-профили human vs. chimp vs. mouse для одних и тех же позиций.
Позиции с высоким SSIM-divergence = потенциальные "structural innovations"
в эволюции.

### 5. Prenatal Screening Tool

Для пар-носителей β-thalassemia: "какова структурная тяжесть конкретной
комбинации вариантов у эмбриона?" Не заменяет генетическое консультирование,
но приоритизирует случаи для детального анализа.

### 6. Patent Strategy

Патентуемо: метод pearl detection (комбинация VEP<threshold + SSIM<threshold
для идентификации структурно-патогенных вариантов невидимых для sequence
analysis). Utility patent, не software patent.

---

## РИСКИ И MITIGATION

| Риск                              | Вероятность    | Mitigation                                       |
| --------------------------------- | -------------- | ------------------------------------------------ |
| Enformer/Akita обгонят            | Средняя        | Позиционировать как complementary, не competing  |
| Нет экспериментальной валидации   | Высокая        | Найти collaboration через bioRxiv контакты       |
| SSIM dilution на больших матрицах | Подтверждённая | Threshold recalibration per matrix size          |
| Hype без substance                | Средняя        | Публиковать honest nulls, строить reputation     |
| Regulatory barriers для клиники   | Высокая        | Позиционировать как research tool, не diagnostic |

---

## МЕТРИКИ УСПЕХА (KPIs)

| Горизонт   | Метрика                 | Target             |
| ---------- | ----------------------- | ------------------ |
| 3 месяца   | Локусов в атласе        | ≥10                |
| 3 месяца   | GitHub stars            | ≥50                |
| 6 месяцев  | Цитирования bioRxiv     | ≥5                 |
| 6 месяцев  | Paper 2 submitted       | Yes                |
| 12 месяцев | Experimental validation | ≥1 pearl confirmed |
| 12 месяцев | NPM weekly downloads    | ≥100               |

---

## ЗАПРОС К AI-АССИСТЕНТУ

Используй этот контекст для:

1. Планирования конкретных технических задач (scripts, configs, pipeline)
2. Написания grant proposals / white papers
3. Подготовки презентаций для потенциальных collaborators
4. Архитектурных решений при масштабировании на новые локусы
5. Стратегических рекомендаций по приоритизации задач

**Принцип:** 20% усилий → 80% результата. Всегда спрашивай: "Что минимально
необходимо чтобы это заработало?" перед тем как планировать идеальное решение.

**Ограничения:** Не создавай фантомных ссылок. Не генерируй синтетические
данные без watermark. Не обещай клиническую применимость без экспериментальной
валидации. Следуй протоколу из CLAUDE.md проекта.
