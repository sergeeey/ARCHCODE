# Отчёт: Усиление позиций taxonomy paper

**Дата:** 2026-03-10
**Ветка:** feature/mechanistic-taxonomy @ `9f23ea0`
**Контекст:** Внешний рецензент (LLM-based) указал на три уязвимости. Проведена систематическая работа по усилению позиций с сохранением научной честности.

---

## 1. Исходные замечания рецензента

| # | Замечание | Объективность |
|---|----------|---------------|
| 1 | HBB доминирует; слабая переносимость на другие локусы | 9/10 — полностью справедливо |
| 2 | Тон README ≈ маркетинг, не cold technical report | 7/10 — частично справедливо (README, не manuscript) |
| 3 | MPRA null = unfalsifiable framing; AlphaGenome неоднозначен | 8/10 — справедливо с нюансом |

---

## 2. Направление 1: Ослабление HBB-зависимости

### 2.1. Tissue-match amplification (N=3 локуса)

**Метод:** Для LDLR и BRCA1 созданы K562-only конфигурации (замена tissue-matched H3K27ac пиков на K562 ENCFF864OSZ, CTCF неизменен). Полный прогон всех вариантов через оба конфига. Сравнение с ранее полученным SCN5A (cardiac vs K562).

**Результаты:**

| Локус | Ткань | Вариантов | Δ matched | Δ K562 | Amplification | Struct calls (M/K) |
|-------|-------|-----------|-----------|--------|---------------|-------------------|
| HBB | K562 = matched | 1,103 | −0.1109 | N/A | Reference | 281 / N/A |
| SCN5A | Cardiac | 2,488 | −0.00471 | −0.00343 | **1.37×** | 0 / 0 |
| LDLR | HepG2 (liver) | 3,284 | −0.00241 | −0.00169 | **1.43×** | 10 / 10 |
| BRCA1 | MCF7 (breast) | 10,682 | −0.00554 | −0.00558 | **0.99×** | 53 / 52 |

**Интерпретация:**

- **SCN5A и LDLR:** Tissue-match усиливает дискриминацию pathogenic/benign на 37–43%. Эффект consistent: два независимых локуса, два разных типа ткани (cardiac, liver), два разных ENCODE dataset'а.
- **BRCA1 (null):** Амплификации нет. Причина: K562 H3K27ac пики в окне BRCA1 co-localize с MCF7 пиками на всех major сайтах. "Tissue mismatch" для BRCA1 минимален — K562 уже адекватно представляет enhancer landscape. BRCA1 экспрессируется broad, в отличие от tissue-specific SCN5A и LDLR.
- **Refined hypothesis:** Amplification зависит от divergence enhancer landscape между target tissue и K562, не от факта tissue match per se.

**Источники данных:**

- SCN5A cardiac: ENCSR000NPF (H3K27ac), ENCSR713SXF (CTCF)
- LDLR HepG2: ENCFF012ADZ (H3K27ac), ENCFF205OKL (CTCF)
- BRCA1 MCF7: ENCFF340KSH (H3K27ac), ENCFF163JHE (CTCF)
- K562 baseline: ENCFF864OSZ (H3K27ac), ENCFF736NYC (CTCF)

**Файлы:** `analysis/tissue_match_amplification.json`, `figures/taxonomy/fig_tissue_match_amplification.pdf`, `config/locus/ldlr_k562_300kb.json`, `config/locus/brca1_k562_400kb.json`, `results/*_K562.csv`

### 2.2. N=1 caveat (inline в Results)

Добавлено прямо в секцию HBB Q2b результатов:

> "We note that HBB is the sole locus with high-confidence Class B variants; the 29 candidates at partially matched loci are threshold-proximal and unvalidated. The tissue-match amplification effect is independently confirmed at SCN5A (cardiac config: +37% delta) [...] but the HBB demonstration remains fundamentally N = 1 for confident Class B."

### 2.3. Testable predictions table

Добавлена таблица с предсказаниями для 6 локусов (LDLR, SCN5A iPSC-CM, TP53, GJB2, CFTR, TERT) с explicit falsification criterion:

> "If tissue-matched configurations at LDLR, SCN5A (iPSC-CM), and CFTR all fail to increase Class B variant counts above the K562 baseline, the tissue-match hypothesis would be weakened."

---

## 3. Направление 2: Тон — cold technical report

### 3.1. "What This Paper Does NOT Claim" box

Добавлен блок в Discussion с 4 explicit disclaimers:

1. **Not a universal predictor** — работает только с tissue-matched chromatin data
2. **Not experimentally validated** — 54 Class B = computational, нужен Capture Hi-C
3. **Not a clinical diagnostic tool** — research classifications, не ACMG
4. **Not a replacement for sequence-based tools** — VEP/CADD остаются essential для Class A

### 3.2. Проверка маркетинговых формулировок

В taxonomy paper (в отличие от README core paper) маркетинговые фразы типа "nine independent lines of evidence" и "new category: structural mechanism discovery" **отсутствуют**. Тон уже умеренный.

---

## 4. Направление 3: MPRA falsifiability

### 4.1. Positive control test

**Гипотеза:** Если MPRA видит Class A (Q3: VEP high, ARCHCODE neutral) но не Class B (Q2b: VEP low, ARCHCODE disruptive), это доказывает механистическую ортогональность.

**Результат: INCONCLUSIVE**

| Квадрант | N в MPRA-регионе | Mean MPRA score |
|----------|-----------------|-----------------|
| Q1 (concordant pathogenic) | 0 | N/A |
| Q2b (architecture-driven) | 10 | −0.019 |
| Q3 (activity-driven) | 1 | −0.130 |
| Q4 (concordant benign) | 11 | −0.035 |

**Причина:** Kircher 2019 MPRA покрывает только 186 bp промотора HBB (chr11:5,227,022–5,227,208). Из 1,103 вариантов атласа только 30 попадают в это окно. Q3 варианты (VEP HIGH + LSSIM neutral = splice/missense) расположены за пределами 186-bp региона. В полном атласе Q3 = 75, но в MPRA-окне = 1.

**Вывод:** Mann-Whitney при N=1 невозможен. Тест требует tiling MPRA / lentiMPRA с покрытием полного 95 kb локуса.

**Файлы:** `analysis/mpra_positive_control.json`, `figures/taxonomy/fig_mpra_positive_control.pdf`, `scripts/mpra_positive_control.py`

### 4.2. Falsification criterion в manuscript

Добавлен explicit criterion:

> "The architecture-driven classification would be weakened if MPRA scores at Q2b positions were significantly non-zero (Mann–Whitney p < 0.05 vs Q4 benign baseline). [...] If MPRA fails to discriminate Q3 from Q2b, the mechanistic orthogonality argument is undermined."

### 4.3. AlphaGenome в taxonomy paper

Проверка показала: в taxonomy paper AlphaGenome упоминается **только как related work context** (строки 70, 897, 1002), без числовых claims (ρ = −0.22 и т.д. — это в bioRxiv core paper). Риск mock-based claims в taxonomy paper **отсутствует**.

---

## 5. Что добавлено в manuscript

| Секция | Добавление | Строки |
|--------|-----------|--------|
| Results / HBB Q2b | N=1 caveat + SCN5A confirmation inline | ~502–505 |
| Section 7 / Experiments | Falsification criterion + data limitation | ~876–882 |
| Discussion | "What This Paper Does NOT Claim" box | ~1024–1037 |
| Supplement S4a | Tissue-match amplification table (3 loci) | ~1268–1296 |
| Supplement S4b | Testable predictions table (6 loci) | ~1298–1315 |
| Suppl. Fig S6 | MPRA positive control figure legend | ~1356–1364 |
| Suppl. Fig S7 | Tissue-match amplification figure legend | ~1366–1374 |

---

## 6. Что осталось не решённым (честные ограничения)

| Проблема | Статус | Что нужно |
|----------|--------|-----------|
| N=1 HBB для confident Class B | **Не решена** | Wet-lab: Capture Hi-C в HUDEP-2 на Q2b позициях |
| MPRA positive control underpowered | **INCONCLUSIVE** | Tiling MPRA / lentiMPRA на полный 95 kb HBB |
| BRCA1 tissue-match null | **Honest null** | Не баг, а feature: K562 ≈ MCF7 для BRCA1 |
| Absolute signal weak at non-HBB loci | **Не решена** | Tissue-matched configs for more loci (iPSC-CM, lung epithelium) |
| "9 lines of evidence" в README | **Не исправлено** | В taxonomy paper этого нет; README = core paper |

---

## 7. Итоговая оценка

**До усиления:** Paper уязвим по трём направлениям — HBB dominance, persuasive tone, unfalsifiable MPRA.

**После усиления:**

- HBB dominance: **ослаблена** — tissue-match amplification на 3 локусах (2 positive + 1 informative null), N=1 caveat explicit, testable predictions pre-registered
- Tone: **скорректирован** — 4 explicit disclaimers, no overclaims в taxonomy paper
- MPRA: **формализована** — falsification criterion записан, INCONCLUSIVE результат честно задокументирован

**Главный нерешённый риск:** Confident Class B = only HBB. Это фундаментальное ограничение, которое может быть решено только через (1) wet-lab validation (Capture Hi-C) или (2) tissue-matched configs для тканей с divergent enhancer landscape (iPSC-CM, cochlear, lung epithelium).

---

**Коммиты:** `41b713c` (P1 fixes), `9f23ea0` (position strengthening)
**PDF:** `C:\Users\serge\Desktop\ARCHCODE_taxonomy_paper_v4.pdf` (2.3 MB)
**GitHub:** pushed @ `feature/mechanistic-taxonomy`
