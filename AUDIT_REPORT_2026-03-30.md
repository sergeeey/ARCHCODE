# ARCHCODE — Полный аудит репозитория

**Дата аудита:** 2026-03-30
**Репозиторий:** https://github.com/sergeeey/ARCHCODE.git
**Ветка:** main (275 коммитов)
**Аудитор:** Claude Opus 4.6 по запросу пользователя
**Цель:** Проверить проект на обман, ложь и достоверность заявлений

---

## 1. ОБЩЕЕ ОПИСАНИЕ ПРОЕКТА

### Что это
ARCHCODE — физический симулятор экструзии хроматиновых петель (loop extrusion), реализованный на TypeScript/React/Three.js (фронтенд) + Python (data pipeline). Заявляет способность обнаруживать патогенные геномные варианты через анализ 3D-структуры хроматина.

### Ключевая идея
Симулятор строит wild-type и мутантную контактные карты хроматина и сравнивает их через Structural Similarity Index (LSSIM). Низкий LSSIM = структурное нарушение = потенциально патогенный вариант. Заявляется обнаружение "pearl-вариантов" — невидимых для существующих инструментов (VEP, SpliceAI, CADD).

### Автор
- **Sergey V. Boyko** (в metadata иногда "Boiko" — непоследовательная транслитерация)
- Affiliation: "Independent Researcher, Almaty, Kazakhstan"
- Email: sergeikuch80@gmail.com
- ORCID: пустая строка в metadata
- Публикационная история: **ноль предыдущих работ** в геномике/биоинформатике [VERIFIED через web search]

### Технический стек
- Frontend: React + TypeScript + Three.js + D3 + Vite + Tailwind
- Backend/Data: Python 3.11+ (pandas, sklearn, matplotlib, seaborn, ripser)
- CI/CD: GitHub Actions (3 workflow), Docker
- AI-помощник: Claude (Opus 4.5/4.6, Sonnet 4.5/4.6) — 75% коммитов с Co-Authored-By

---

## 2. ЧТО РЕАЛЬНО РАБОТАЕТ [VERIFIED]

### 2.1. Движок симуляции — настоящий

**Файлы:**
- `src/engines/LoopExtrusionEngine.ts` (396 строк) — базовый движок
- `src/engines/MultiCohesinEngine.ts` (827 строк) — расширенный с Kramer kinetics
- `src/engines/contactMatrix.ts` (194 строк) — контактные матрицы, P(s)-кривые

**Что делает:**
- Моделирует когезин-зависимую экструзию петель
- Двунаправленное движение с конфигурируемой скоростью
- CTCF-барьеры с конвергентным правилом (R...F)
- Стохастическое блокирование (85% эффективность)
- Kramer rate theory kinetics (occupancy-dependent unloading)
- Seeded RNG для воспроизводимости

**Вердикт:** Это реальная физическая симуляция, а не шелл или заглушка. Код грамотный.

### 2.2. ClinVar данные — настоящие

**Файлы:**
- `data/hbb_real_variants.csv` — реальные VCV-идентификаторы (VCV000439130 и т.д.)
- `data/clinvar_hbb_raw.json` — скачано через NCBI ClinVar E-utilities API, 2026-02-27, 431 вариант
- `data/cftr_variants.csv` — реальные ClinVar данные для CFTR на chr7
- Скрипт `scripts/download_clinvar_generic.py` (222 строки) — реальные API-вызовы к NCBI

**Числа:**
- HBB pathogenic: 353 варианта (352 строки данных + заголовок) — сходится с манускриптом
- HBB combined (path + benign): 1,103 варианта — сходится
- Integrative benchmark: 30,318 вариантов по 9 локусам — сходится

### 2.3. Бенчмарки — честные

- **Akita:** Pearson r = −0.126 (отрицательная корреляция — честно показана)
- **AlphaGenome (real API):** Pearson r = 0.052 (практически нулевая — честно показана)
- **Hi-C:** r = 0.28–0.59 по 8 комбинациям locus×cell-type — подан как modest, не как триумф

### 2.4. Цитируемые работы — реальные

| Ссылка | Статус |
|--------|--------|
| Sabate et al. bioRxiv 2024 (DOI: 10.1101/2024.08.09.605990) | [VERIFIED] — "Universal dynamics of cohesin-mediated loop extrusion", Pasteur Institute |
| AlphaGenome (DeepMind) | [VERIFIED] — Nature 2025, GitHub, реальный инструмент |
| Gabriele et al. 2022 (Science) | [VERIFIED] — DOI резолвится |
| Wang et al. 2004 SSIM (IEEE) | [VERIFIED] — DOI резолвится |
| Gerlich 2006, Davidson 2019, Sanborn 2015, Landrum 2018 | [VERIFIED] — стандартные работы в области |

### 2.5. Zenodo — существует

- DOI: 10.5281/zenodo.18867448 [VERIFIED]
- Self-deposited, 61 просмотр, 52 скачивания
- Файл: `ARCHCODE_arXiv_v2.pdf` (3.9 MB)
- НЕ рецензировано (Zenodo принимает любые загрузки)

### 2.6. Конфигурация — честно промаркирована

- `config/default.json` — параметры с литературными ссылками, явные предупреждения ("Ganji 2018 studied CONDENSIN, not cohesin!")
- Прямо написано: `"alphaGenome: Validation uses mock data, not real AlphaGenome API"`
- `src/domain/constants/biophysics.ts` — параметры разделены на "MODEL PARAMETER" и "LITERATURE-BASED"

### 2.7. Самоаудит — проведён

- `FALSIFICATION_REPORT.md` (2026-02-04) — нашёл 5 блокирующих проблем
- `HALUGATE_REPORT.md` — цитационные ошибки
- `CLAUDE.md` — жёсткие правила после аудита (NO PHANTOM REFERENCES, NO INVISIBLE SYNTHETIC DATA)
- Это редкость — автор документировал свои собственные ошибки

### 2.8. Фигуры — реальные

- 24 фигуры в `figures/` (PDF + PNG), 16 в `plots/`
- Размеры 27–493 KB — не заглушки
- Визуально: реальные matplotlib/seaborn графики (violin plots, bar charts, scatter)

### 2.9. CI/CD — грамотный

- `security-gates.yml` — lint, build, tests, coverage (60/55/60/60), gold-standard regression, bandit
- `nightly-strict-real.yml` — ночной прогон с реальным AlphaGenome API (если ключ настроен)
- `secrets-history-scan.yml` — еженедельный gitleaks

---

## 3. ЧТО ЛОЖЬ ИЛИ КРИТИЧЕСКАЯ ПРОБЛЕМА [VERIFIED]

### 3.1. ЦИРКУЛЯРНАЯ ЛОГИКА AUC — ГЛАВНАЯ ПРОБЛЕМА

**Где:** `scripts/generate-unified-atlas.ts`, строки 291–303

**Механизм:** Патогенность варианта закодирована через hardcoded lookup-таблицу:
```typescript
const CATEGORICAL_EFFECTS = {
  nonsense: 0.1,      // сильное возмущение → низкий SSIM → "патогенный"
  frameshift: 0.15,
  splice_donor: 0.2,
  splice_acceptor: 0.2,
  missense: 0.4,
  synonymous: 0.9,    // слабое возмущение → высокий SSIM → "доброкачественный"
  intronic: 0.8,
  // ...
};
```

Категория варианта из ClinVar аннотаций НАПРЯМУЮ определяет effectStrength → который определяет возмущение матрицы → который определяет SSIM → который определяет "патогенность". Это замкнутый круг.

**Доказательство — собственный ablation проекта (`results/ablation_effectstrength.json`):**

| Режим | Логика | AUC |
|-------|--------|-----|
| categorical | nonsense=0.1, syn=0.9 | **0.975** |
| position-only | все варианты = 0.3 | 0.551 |
| uniform-medium | все варианты = 0.5 | 0.551 |
| inverted | nonsense=0.9, syn=0.1 | 0.022 (зеркально!) |
| random | случайные 0.1–0.9 | 0.490 |

**Вывод:** Без категориальной таблицы AUC = случайное угадывание (0.49–0.55). С инвертированной таблицей AUC = 1−0.975 = 0.022. Это математическое доказательство того, что AUC полностью определяется lookup-таблицей, а не "структурным сигналом".

Сам проект в `conclusions` пишет: *"This ablation definitively proves ARCHCODE's AUC is a category-distribution effect"* — но формулирует как "not circular or artifactual", что является софистикой.

**Дополнительно:** Benign SSIM mean = 1.0000 (range 0.9996–1.0) — подозрительно идеально. Benign варианты (в основном synonymous/intronic) получают effectStrength 0.8–0.9 → минимальное возмущение → SSIM ≈ 1.0 по конструкции.

### 3.2. PDF-ПРЕПРИНТ СОДЕРЖИТ ФАЛЬСИФИКАЦИИ

PDF (`ARCHCODE_Preprint_EN.pdf`, 2026-02-04) — это **до-аудитная версия**, которая лежит на Zenodo для скачивания. Сравнение с текущим markdown-манускриптом (2026-03-04):

| Пункт | PDF (Feb 4) — на Zenodo | Markdown (Mar 4) — в репо |
|-------|-------------------------|---------------------------|
| Параметры FRAP | "fitted to FRAP data (Sabate et al. 2025)" — **ФАНТОМНАЯ ССЫЛКА** (DOI 404) | "manually calibrated to published literature ranges" |
| AlphaGenome | Представлен как **реальный production-инструмент** "version 2026.1", "publicly available API" — **нулевое раскрытие mock** | Частично исправлено (но противоречия остались) |
| Клиническая реклассификация | "Рекомендуем реклассифицировать VCV327, VCV026, VCV302 из VUS в Likely Pathogenic" | "NO_GO / UNVERIFIED" |
| Loop That Stayed | "First documented class", "paradigm-shifting" | "Hypothesis-generating", "UNVERIFIED" |
| Тип модели | "Stochastic Monte Carlo", "high-throughput" | "Analytical mean-field" |
| Количество локусов | 1 (HBB, 367 вариантов) | 9 (30,318 вариантов) |
| Ограничения | 4 пункта, мягкие, повторяют фантомное R²=0.89 | 16 пунктов, жёсткие |
| R² claim | R²=0.89 "on blind loci" | AUC=0.977 с обширными оговорками |

**КРИТИЧНО:** PDF с фантомной ссылкой и клиническими рекомендациями лежит на Zenodo (52 скачивания). Любой скачавший получит версию с фальсификациями.

### 3.3. AlphaGenome — ТРИ ВЗАИМОИСКЛЮЧАЮЩИХ УТВЕРЖДЕНИЯ В ОДНОМ РЕПО

| Файл | Утверждение |
|------|-------------|
| `manuscript/ABSTRACT.md:81` | "AlphaGenome: NOT USED, Synthetic mock data; **excluded entirely**" |
| `manuscript/abstract_content.typ:21` | "AlphaGenome multimodal analysis **independently confirms** pearl disruption (RNA-seq signal 2.8x, p<0.0001)" |
| `manuscript/FULL_MANUSCRIPT.md:225` | "AlphaGenome benchmark: **REAL**, SDK v0.6.0, Spearman ρ=0.12–0.52" |
| `manuscript/FULL_MANUSCRIPT.md:1633` | Целая секция "AlphaGenome Benchmark" с детальными числами |
| Проектный `CLAUDE.md` approved sources | "❌ AlphaGenome — **SYNTHETIC, not real tool**" |
| `config/default.json` | "alphaGenome: Validation uses **mock data**, not real AlphaGenome API" |
| `src/services/AlphaGenomeService.ts` | `mode: "mock"` — генератор случайных чисел по категории варианта |

Три состояния одновременно: "excluded" + "independently confirms" + "REAL SDK". Это непубликуемо и указывает на отсутствие контроля качества.

### 3.4. FRAP-ДАННЫЕ БЫЛИ ФАБРИКОВАНЫ (ЗАТЕМ ЧАСТИЧНО ИСПРАВЛЕНЫ)

**Исходная версия (PDF):**
- Заявлено: параметры α=0.92, γ=0.80 "fitted to experimental FRAP data (Sabate et al., Nature Genetics 2025)"
- Реальность: DOI `10.1038/s41588-025-02406-9` возвращал **404** — статья не существует
- Реальные значения в `kramer_kinetics_fit.json`: α=1.0, γ=0.9445, MSE=13.32 (не заявленные 0.92/0.80/5.33)
- Файлов FRAP-данных нет нигде в репозитории

**Текущая версия (markdown):**
- Исправлено на "manually calibrated to published literature ranges from Gerlich et al., 2006; Hansen et al., 2017; Sabate et al., 2024"
- Sabate et al. теперь ссылается на реальный bioRxiv препринт (DOI: 10.1101/2024.08.09.605990) — это правильно
- Но в PDF на Zenodo всё ещё старая версия

### 3.5. "СЛЕПАЯ ВАЛИДАЦИЯ" НЕ БЫЛА СЛЕПОЙ

- Параметры и результаты валидации закоммичены в **одном коммите** (2026-02-03, 5c061bc), с разницей ~10 минут
- Файла пре-регистрации нет в репозитории
- Нельзя заявлять "pre-registered blind validation" без timestamp proof

### 3.6. KRAMER KINETICS — НЕ ВНОСЯТ ВКЛАДА

Графики `plots/bayesian_fit_contours.png` показывают: корреляция с Hi-C варьируется от **0.5584 до 0.5588** по всему пространству параметров alpha/gamma/k_base.

Диапазон: **0.0004** (четыре десятитысячных).

Это значит: Kramer kinetics — декоративный элемент. Какие бы параметры ни подставить, результат практически одинаковый. Физическая основа модели (заявленная как ключевое преимущество) **не влияет на предсказательную силу**.

### 3.7. ЭКСПЕРИМЕНТАЛЬНАЯ ВАЛИДАЦИЯ НЕ ЗАВЕРШЕНА

Файлы в корне репо раскрывают:

**`⏰_REAL_DATA_TONIGHT.txt`** — инструкции по замене mock AlphaGenome на реальные SpliceAI данные. Указывает скачать ClinVar VCF и запустить SpliceAI локально.

**`⏰_START_HERE_TONIGHT.txt`** — инструкции по скачиванию RNA-seq FASTQ (SRR12837671, SRR12837674, SRR12837675) для анализа сплайс-сайтов. Прямо написано: "If D3 shows high aberrant splicing → Validates 'Loop That Stayed' → Functional validation STRONG (compensates weak Hi-C r=0.16)".

**`docs/TONIGHT_CHECKLIST.md`** — to-do лист на 2026-03-06 для загрузки FASTQ и бенчмарков.

Все три файла показывают: ключевые валидации **запланированы, но не выполнены**. bioRxiv отклонил статью именно по этой причине: "not complete research with new data".

### 3.8. arXiv — НЕ СУЩЕСТВУЕТ

- `submission_metadata.json` указывает arXiv как "Pending endorsement (q-bio.GN, code B9P837)"
- README badge ведёт на https://arxiv.org/ (главная, не на статью)
- PDF на Zenodo назван `ARCHCODE_arXiv_v2.pdf`
- Web search: **записи на arXiv не найдено** [VERIFIED]

---

## 4. ЧТО СПОРНО (нюансы, не чёрно-белое)

### 4.1. AI co-authorship — НЕ обман

75% коммитов (205 из 275) содержат `Co-Authored-By: Claude`. Это прозрачно. Автор не скрывает AI-помощь в коде. Однако:
- В манускрипте AI-помощь НЕ упомянута
- При рецензировании это будет проблемой (многие журналы требуют раскрытия AI use)

### 4.2. Контроли — ЕСТЬ, но опровергают заявления

- Ablation study (5 режимов) — это контроль. Но он **доказывает** циркулярность, а не валидирует модель.
- Hi-C benchmark — это контроль. Но корреляция слабая (r=0.28–0.59).
- CADD cross-validation — это контроль. Но 17 pearl-вариантов из 30,318 — это 0.06%.

### 4.3. "Просто промоторные варианты" — чрезмерное упрощение

Движок моделирует петлевую экструзию, не промоторы. Pearl-варианты — интересная концепция. Проблема в том, что без категориального кодирования движок не отличает pathogenic от benign.

### 4.4. Однодневные спринты — подозрительно, но не преступление

| Ветка | Дата | Коммитов | Содержание |
|-------|------|----------|------------|
| TERAG | 2025-11-25 | 10 за 1 день | Полный pipeline, фигуры, самоаудит, скелет v0.1 |
| AlphaGenome | 2026-02-03 | 10 за 1 день | API-интеграция, слепая валидация, Kramer kinetics |
| main | разные даты | 69 пар коммитов < 5 мин | Быстрый AI-assisted workflow |

Это характерно для AI-assisted разработки, но не является обманом само по себе.

### 4.5. INTEGRITY_CHECK — самореферентный

`INTEGRITY_CHECK_20260304.txt` заявляет "PASS - NO DISCREPANCIES FOUND". Но проверяет только:
- Совпадение чисел в манускрипте с числами в CSV-файлах проекта

НЕ проверяет:
- Правильность самих CSV (получены ли они из реального ClinVar)
- Воспроизводимость симуляции
- Реальность AlphaGenome данных
- Наличие экспериментальной валидации

Это circular verification — манускрипт соответствует своим же данным.

---

## 5. GIT-ИСТОРИЯ: ПАТТЕРНЫ [VERIFIED]

### Авторство
| Alias | Коммитов | Email |
|-------|----------|-------|
| Sergey | 233 | serge@example.com |
| ARCHCODE Project | 31 | archcode@project.local |
| sergeeey | 9 | sergeikuch80@gmail.com |
| Sergey Boyko | 2 | sergeikuch80@gmail.com |

100% коммитов от одного человека под 4 alias'ами.

### AI Co-Authorship
| AI Tool | Коммитов |
|---------|----------|
| Claude Opus 4.6 | 136 |
| Claude Opus 4.5 | 34 |
| Claude Opus 4.6 (1M context) | 19 |
| Claude Sonnet 4.5 | 14 |
| Claude Sonnet 4.6 | 1 |
| Cursor | 1 |

### Хронология
- Первый коммит: 2025-11-25 01:15:30 +0500
- Последний коммит: 2026-03-24 17:35:48 +0500
- Активный период: ~4 месяца
- Самый продуктивный день: 2025-11-25 — **36 коммитов** (первый день, весь скелет проекта)
- 69 пар коммитов с интервалом менее 5 минут

---

## 6. СТАТУС ПУБЛИКАЦИЙ [VERIFIED]

| Площадка | Статус |
|----------|--------|
| bioRxiv | **ОТКЛОНЁН** (2026-02, "not complete research with new data") |
| arXiv | **НЕ НАЙДЕН** (заявлен как "pending endorsement", но записи нет) |
| Research Square | "READY TO SUBMIT" (не подано) |
| Zenodo | **Опубликован** (self-deposited, DOI: 10.5281/zenodo.18867448, 52 скачивания) |
| Peer-reviewed journal | **Нет** |

---

## 7. ОЦЕНКА ПО КАТЕГОРИЯМ

| Аспект | Оценка | Комментарий |
|--------|--------|-------------|
| Техническая реализация | **7/10** | Работающий движок, профессиональная структура, CI/CD |
| Научная обоснованность | **2/10** | Циркулярная логика AUC, нечувствительность Kramer kinetics |
| Честность данных | **3/10** | Фальсифицированные FRAP, mock-as-real AlphaGenome, противоречия |
| Самокоррекция | **6/10** | Аудит проведён и задокументирован, но не все проблемы исправлены |
| Публикабельность | **2/10** | bioRxiv отклонил заслуженно; PDF на Zenodo содержит фальсификации |
| Прозрачность AI-use | **7/10** | В коммитах — прозрачно; в манускрипте — не упомянуто |
| Экспериментальная валидация | **0/10** | Ни одного wet-lab или real-data эксперимента не завершено |

---

## 8. КЛАССИФИКАЦИЯ: ОБМАН vs ЗАБЛУЖДЕНИЕ vs НАУКА

### Это НЕ чистое мошенничество
- Движок работает
- ClinVar данные настоящие
- Самоаудит проведён
- Ссылки (кроме одной фантомной) на реальные работы
- AI-помощь прозрачна в коммитах

### Это НЕ наука в текущем состоянии
- Главное заявление (AUC) — артефакт категориального кодирования
- Нет экспериментальной валидации
- PDF с фальсификациями на Zenodo
- Нет peer review

### Это — амбициозная попытка одиночного исследователя с AI-помощником
Автор:
1. Построил работающий симулятор (ценно)
2. Переоценил свои результаты и наделал overclaims (проблема)
3. AI сгенерировал фантомные ссылки, а автор не проверил (опасно)
4. Провёл самоаудит и частично исправился (честно)
5. Оставил до-аудитный PDF на Zenodo (безответственно)
6. Не довёл до конца ни одну экспериментальную валидацию (критично для науки)

---

## 9. РЕКОМЕНДАЦИИ

### Если проект ваш — что нужно сделать:

1. **НЕМЕДЛЕННО: Убрать или заменить PDF на Zenodo.** Текущий PDF содержит фантомную ссылку (Sabate 2025 Nature Genetics), фабрикованные FRAP-данные, клинические рекомендации по реклассификации VUS. Это может быть расценено как научная недобросовестность.

2. **Убить AUC 0.977 как headline metric.** Собственный ablation доказывает: AUC = f(category lookup table). Честная формулировка: "AUC reflects category encoding, not independent structural prediction. Position-only mode yields AUC ≈ 0.55 (chance level)."

3. **Разрешить противоречие AlphaGenome.** Одно из трёх:
   - (a) Полностью удалить из всех файлов манускрипта
   - (b) Пометить как MOCK_SYNTHETIC везде без исключения
   - (c) Получить реальный API-доступ и перезапустить бенчмарк
   Текущее состояние (excluded + confirms + REAL в разных файлах) — непубликуемо.

4. **Сузить scope до HBB proof-of-concept.** 8 из 9 локусов дают 0 pearl-вариантов. Честная статья: "HBB-specific structural annotation layer as hypothesis-generating tool."

5. **Получить хотя бы один экспериментальный результат.** Файлы `⏰_REAL_DATA_TONIGHT.txt` показывают — автор сам знает, что нужен RNA-seq или Capture Hi-C. Без этого любой рецензент отклонит.

6. **Переформулировать pearl-варианты.** Не "invisible to VEP" (overclaim), а "variants where sequence-based and structural annotations diverge — hypothesis for experimental follow-up."

7. **Раскрыть AI co-authorship в манускрипте.** В коммитах прозрачно, но в статье не упомянуто. Большинство журналов требуют disclosure.

8. **Удалить файл `abstract_content.typ`** или привести его в соответствие с ABSTRACT.md. Сейчас он содержит утверждение "AlphaGenome independently confirms" которое прямо противоречит "AlphaGenome excluded."

9. **Исправить README:** убрать AlphaGenome статистику (p = 4.8×10⁻⁵) которая основана на mock-данных, или явно пометить как SYNTHETIC.

10. **Убрать arXiv badge из README** — записи на arXiv не существует.

### Если вы оцениваете чужой проект:

- **Движок** — заслуживает технического уважения как proof-of-concept
- **Headline claims** — не подтверждены собственными же контролями
- **PDF на Zenodo** — содержит фальсификации и опасен для цитирования
- **Общая оценка** — не мошенничество, но не готов к публикации. Рекомендация: reject in present form, major revision с описанными выше исправлениями

---

## 10. ПРИЛОЖЕНИЕ: КЛЮЧЕВЫЕ ФАЙЛЫ ДЛЯ ПРОВЕРКИ

| Файл | Зачем смотреть |
|------|----------------|
| `scripts/generate-unified-atlas.ts:291-303` | Hardcoded categorical effects — корень циркулярной логики |
| `results/ablation_effectstrength.json` | Ablation доказывает: AUC = category encoding |
| `manuscript/ABSTRACT.md:81` | "AlphaGenome: excluded" |
| `manuscript/abstract_content.typ:21` | "AlphaGenome independently confirms" (противоречие) |
| `manuscript/FULL_MANUSCRIPT.md:225` | "AlphaGenome: REAL" (ещё одно противоречие) |
| `manuscript/FULL_MANUSCRIPT.md:1633` | Целая секция AlphaGenome Benchmark |
| `CLAUDE.md` | "AlphaGenome — SYNTHETIC, not real tool" |
| `config/default.json` | "alphaGenome: Validation uses mock data" |
| `src/services/AlphaGenomeService.ts` | `mode: "mock"` — генератор случайных чисел |
| `FALSIFICATION_REPORT.md` | Собственный аудит проекта |
| `plots/bayesian_fit_contours.png` | Kramer kinetics нечувствительны (Δr = 0.0004) |
| `⏰_REAL_DATA_TONIGHT.txt` | Валидация запланирована, но не выполнена |
| `⏰_START_HERE_TONIGHT.txt` | RNA-seq ещё не скачан |

---

*Этот аудит проведён Claude Opus 4.6 по запросу пользователя. Все утверждения с маркером [VERIFIED] подтверждены чтением файлов, git history, или web-запросами. Аудит не является peer review и не заменяет экспертную рецензию.*
