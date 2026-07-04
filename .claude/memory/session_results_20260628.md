# Session Results — 2026-06-28
## "Есть ли открытие в ARCHCODE?" — полный аудит

**Branch:** experiment/spectral-collapse-pilot
**Duration:** ~4 hours
**Focus:** Поиск потенциала scientific discovery + 3 новых теста

---

## Гипотезы запущены и результаты

### H_CSI (CTCF Signal Index как предиктор)
**Результат:** ОТКЛОНЁН
- r = −0.16 для CSI vs delta_pb (N=14 локусов)
- K562 CSI самый высокий, но это отражает эритроидный контекст, а не структурную чувствительность
- Вывод: CSI не объясняет delta_pb вне HBB

### H_buffer (N_CTCF как структурный буфер)
**Результат:** ОТКЛОНЁН
- Без HBB: Spearman ρ = −0.21, p = 0.50 — нет сигнала
- Конфаунд: HBB имеет 5 пиков И маленькое окно (30kb) — неразличимо
- Вывод: N_CTCF не является предиктором при N=14

### H_tissue_match (tissue context)
**Результат:** BORDERLINE — HBB leverage point
- Pearson r = 0.53, p = 0.049 (N=14)
- Spearman ρ = 0.48, p = 0.082
- Removing HBB → r = 0.37, p = 0.22
- **Добавлено в рукопись:** dual-regime параграф, строка 1143 (`taxonomy_paper/body_content.typ`)

---

## Dual-Regime META-Находка [INFERRED]

HBB Δ_pb = 0.111 vs все остальные 13 локусов: 0.000–0.019 (5.9× gap)
- Режим 1: compact TAD + tissue-specific + window ≤95kb → сильный сигнал
- Режим 2: housekeeping genes + 300-400kb windows → слабый сигнал
- **Pearl зарегистрирован:** `pearl_dual_regime.json`, next_check 2026-08-01

---

## Conservation Analysis (сегодня — новое)

### Ensembl GERP constrained elements — HBB pearls [VERIFIED-REAL]

**Метод:** Ensembl REST API, feature=constrained, N=17 уникальных pearl позиций

| Группа | В constrained | % | N |
|--------|--------------|---|---|
| ARCHCODE pearls | 16 | 94.1% | 17 позиций |
| Random non-pearl | 57 | 28.5% | 200 позиций |

**Fisher's exact: OR = 40.14, p ≈ 0** [VERIFIED-REAL]

**Крупнейший constrained element:** chr11:5,226,572-5,226,801 (score=81.3, 229bp) — содержит 5 pearl позиций

**Честная оценка:**
- Частичный category confound: controls не category-matched (много intronic)
- Missense within-category: 100% vs 81% — тренд есть, N мал для stat
- **Ключевой clean факт:** 100% HBB promoter вариантов = pearls (0 non-pearl promoter вариантов)
- Mann-Whitney missense pearls vs non-pearls: p=0.0005 (но это частично circular — pearls defined by lower lssim)

### CTCF Motif Test (H2) — НЕГАТИВНЫЙ (информативный)

**Метод:** Ensemble regulatory + genome-wide BED files (IMR90, HCT116, cardiac, A549)

**Результат:** Pearls находятся на **21.6–22.2kb** от ближайшего CTCF peak
- CTCF peak center: chr11:5,204,979 (все клеточные линии сходятся)
- Pearl диапазон: chr11:5,226,596–5,227,172

**Вывод:** Механизм НЕ "вариант разрушает CTCF binding". Pearls = **intra-loop structural variants** — находятся внутри CTCF-anchored loop, не на якорях.

---

## 5 Линий Доказательств (итог)

| # | Линия | Статус | Сила |
|---|-------|--------|------|
| 1 | ARCHCODE LSSIM disruption | ✅ | p=0.0005 within-category missense |
| 2 | AlphaGenome CAGE -43% | ✅ VERIFIED-REAL | независимый метод, те же координаты |
| 3 | Ортогональность (MaveDB N=1422) | ✅ VERIFIED-REAL | NMI≈0.025 — отдельная ось |
| 4 | GERP evolutionary constraint | ✅ VERIFIED-REAL | OR=40 (частичный confound) |
| 5 | CTCF motif overlap | ❌ НЕГАТИВНЫЙ | уточняет механизм (intra-loop) |

**Вердикт:** 4 конвергирующих линии → уровень сильного preprint claim.
Не "открытие" уровня Nature до мокрой лаборатории (Capture Hi-C или CRISPRi).

---

## Claim (для рукописи/outreach)

> ARCHCODE identifies evolutionarily constrained intra-loop regulatory variants at HBB  
> that are orthogonal to all sequence-based methods (VEP, CADD, MPRA, AlphaGenome)  
> and confirmed by independent CAGE disruption signal.  
> Mechanism: disruption of chromatin loop interior, NOT CTCF anchor binding.

---

## Следующий Шаг (лаборатория)

**Нужно для подтверждения:**
- Allele-specific Capture Hi-C на pearl позициях OR
- CRISPRi knockdown на pearl positions в эритроидных клетках (K562)

**Контакт:** Elphège Nora (UCSF) — письмо отправлено 2026-05-08, follow-up 2026-05-29.
Нора специализируется на allele-specific Hi-C в эритроидных клетках — идеальный коллаборатор.

---

## ⚠️ CRITICAL UPDATE (late session) — conservation lines COLLAPSED to category confound

Два теста запущены ПОСЛЕ первичной записи. Меняют картину.

### gnomAD positional constraint — NULL [VERIFIED-REAL]
- Source: gnomAD r4 GraphQL, region chr11:5,225,400-5,227,600, 2239 variants → `analysis/gnomad_hbb_region.json`
- Pearls (N=17) vs controls (N=794): Mann-Whitney p=0.999 (НЕТ depletion)
- Common var (AF>0.001): 0/17 pearls vs 15/794 ctrl — но base rate 1.9%, ожидалось 0.3 → не сигнал
- Median maxAF: pearls 1.97e-05 > ctrl 1.69e-06 (в обратную сторону)
- **Вердикт: gnomAD НЕ даёт 5-ю линию. NULL.**

### phyloP100way base-level — АРБИТР, вскрыл конфаунд [VERIFIED-REAL]
- Source: UCSC API phyloP100way, region → `analysis/phylop_hbb.json`
- **Whole-set:** pearls mean=2.263 vs ctrl 0.537, conserved(>2) 53% vs 16%, Mann-Whitney p≈0
  → H_C (element-not-base selection) ФАЛЬСИФИЦИРОВАН: base-conservation ЕСТЬ, gnomAD-null = underpower
- **Category-matched (missense vs missense):** pearl N=3 mean=1.446 vs ctrl N=83 mean=4.421
  → сигнал РАЗВЕРНУЛСЯ: pearls МЕНЕЕ консервативны внутри категории (p=0.94)

### Диагноз: GERP + phyloP оба конфаундены категорией
- Pearls = 15/17 promoter (88%); controls = 667/794 intronic (84%)
- «pearls > controls» в обоих тестах = promoter-vs-intronic, НЕ pearl-vs-nonpearl
- Это тот же category leakage, что апрель-2026 (AUC=0.98 из категории)

### ИСПРАВЛЕННАЯ карта линий (моя прежняя «3 из 4 независимы» была оптимистична)
| Линия | Прежний статус | Реальность |
|-------|----------------|-----------|
| GERP OR=40 | независима | ❌ конфаунд категории |
| phyloP | (новая) | ❌ конфаунд категории |
| AlphaGenome CAGE −43% | независима | ⚠️ ПОД ПОДОЗРЕНИЕМ (CAGE=promoter-активность, pearls=промоторы → возможно тавтология) |
| CTCF 22kb геометрия | независима | ✅ держится (чистая геометрия) |
| 100% promoter penetrance | чистый факт | ✅ реален, но возможно тривиален (ARCHCODE как «детектор промоторов» на HBB) |

**Жёсткий открытый вопрос:** добавляет ли ARCHCODE что-то СВЕРХ «это промоторный вариант»?
100% penetrance = нет контраста внутри промоторов → не на чем показать различение.

---

## 🔴 РЕШАЮЩИЙ ТЕСТ (для вторника, когда обновятся лимиты)

**AlphaGenome negative control — RESCUE-OR-KILL, НЕ просто усиление.**
- ISM на matched НЕ-pearl позициях (включая другие консервативные/промотор-смежные) в HBB локусе
- Если −43% CAGE уникален для pearls даже vs другие консервативные позиции → ARCHCODE добавляет реальное → находка жива
- Если другие консервативные позиции тоже дают −43% → ARCHCODE = «промотор/conservation детектор» → апрель снова
- Цена: ~3-5ч, реальные ISM-вызовы. НЕ запускать при <50% бюджета.
- **Это единственный тест, который сейчас имеет значение.** Всё остальное (outreach Норе) — ПОСЛЕ него.

---

## Припаркованные гипотезы (НЕ разворачивать до закрытия ARCHCODE-теста)

| Гипотеза | Единственный реальный мост к ARCHCODE | Forbidden claim |
|----------|---------------------------------------|-----------------|
| **ATPH** (active topological pores, LLPS, Active Model B+, TDA β₁) | LLPS-конденсаты на HBB-LCR; persistent homology на Hi-C картах vs SSIM | «топ.поры = CTCF-петли» — ложный друг, разные объекты |
| **QEC-MWPM** (компенсаторная эволюция как Edmonds/Blossom декодер на графе эпистаза) | негативный эпистаз в 3D-хабах / коллапс TAD; pearls могут иметь компенсаторных партнёров | MWPM требует АДДИТИВНЫХ весов, эпистаз НЕаддитивен по определению → fatal без решения |
- Статус: `[CANDIDATE]`, revival после того как ARCHCODE-claim выживет или умрёт
- Цитаты QEC-гипотезы НЕ верифицированы (подозрительны: APS-DOI `wfyl-wtz3`, arxiv 2512.18273) — проверять руками перед использованием

---

## Файлы

- `taxonomy_paper/body_content.typ:1143` — dual-regime параграф добавлен
- `pearl_dual_regime.json` — pearl registry entry
- `pearl_h4.json` — H4 CTCF distance pearl (21kb mid-range = 72% FP)
- `analysis/discovery_locus_ranking.json` — delta_pb для всех 15 локусов
- `analysis/v1_hbb_features.csv` — 1103 варианта, 27 pearls, полные фичи
- `analysis/gnomad_hbb_region.json` — gnomAD r4 регион (NULL test) [new]
- `analysis/phylop_hbb.json` — phyloP100way регион (confound arbiter) [new]
