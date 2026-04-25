# Final Decision — Stress Biology Project

**Date:** 2026-04-25  
**Status:** 🔴 **HYPOTHESIS REJECTED** — Kill criterion met  
**Verdict:** Publish negative result

---

## Executive Summary

**Гипотеза H0 провалена на Month 2 checkpoint.**

**Progression:**
- n=5: r=-0.500 (неправильное направление)
- n=49: r=+0.364 (правильное направление, ложная надежда)
- n=89: r=-0.173 (неправильное направление, окончательный провал)

**Test без COAD (n=79):**
- r=-0.052, p=0.649 (корреляция отсутствует)
- COAD MSI-high был НЕ единственной проблемой
- Даже без outliers, эффект NULL или обратный

**Kill criteria:**
- Month 2: r > 0.1 → FAILED (r=-0.17)
- Month 3: r > 0.3 → FAILED (r=-0.17)

**Вердикт:** Longer doubling time does NOT predict higher mutation rates.

---

## Root Cause Analysis

### Почему n=49 выглядело успешным?

**1. Sampling bias (выбор тканей)**

n=49 включал только 5 тканей:
- COAD (24h): 16.57 mut/Mb (MSI-high outlier)
- LUAD (48h): 6.18 mut/Mb (средний)
- BRCA (100h): 1.47 mut/Mb (низкий)

Эти 5 тканей случайно создали позитивный градиент.

**2. COAD MSI-high contamination**

COAD samples содержат MSI-high (~30% всех COAD в TCGA):
- MSI-high: 50-200 mut/Mb
- MSS (нормальный COAD): 5-10 mut/Mb

COAD (24h doubling time) → 16.57 mut/Mb среднее = искусственно высокая точка.

**3. Недостаточный размер выборки**

n=49 не покрыл разнообразие тканей. Добавление PRAD + THCA сломало паттерн.

### Почему n=89 убило гипотезу?

**Killer tissues:**

| Tissue | Doubling Time | Mutation Rate | Prediction | Reality |
|--------|--------------|---------------|------------|---------|
| PRAD | 120h (slowest) | 0.86 mut/Mb | HIGHEST | LOW |
| THCA | 72h (slow) | 0.31 mut/Mb | HIGH | LOWEST |

**PRAD и THCA имеют:**
- Самое ДЛИННОЕ время деления
- Самые НИЗКИЕ мутационные ставки

**Это ПРОТИВОПОЛОЖНО предсказанию:**
- Hypothesis: slow division → more Q state time → MORE mutations
- Reality: slow division → FEWER mutations

---

## Possible Explanations (Почему гипотеза неверна)

### 1. Fast division → MORE repair, not LESS

**Alternative mechanism:**
- Fast division = более активный метаболизм
- Больше ATP available
- БОЛЬШЕ возможностей для repair
- Accumulated errors LOWER

Slow division:
- Метаболизм снижен
- Меньше repair cycles
- Но и меньше replication errors

**Net effect:** NULL or weakly negative

### 2. Tissue-specific repair dominates

**Проблема:**
- Between-tissue comparison confounded by:
  - DNA repair capacity (tissue-intrinsic)
  - Cell type differences (epithelial vs blood)
  - Microenvironment
  - Telomere dynamics
  - Senescence rates

**Example:**
- THCA (thyroid): Very stable tissue, low turnover, efficient repair → 0.31 mut/Mb
- PRAD (prostate): Slow cycling, androgen-driven, stringent checkpoints → 0.86 mut/Mb

Doubling time ≠ ATP deficit → repair failure.

### 3. Bilinsky mechanism applies ONLY to radiation

**Original Bilinsky 2025 finding:**
- R/Q states predict radiosensitivity
- Radiation damage during mitosis (Q state) → more severe
- But this is about radiation-induced damage, not replication errors

**Replication errors:**
- Occur during S phase (DNA synthesis)
- Repaired by mismatch repair (MMR), not radiation repair
- Different mechanism → different biology

**Conclusion:** ATP-driven radiosensitivity ≠ ATP-driven mutagenesis

### 4. Within-tissue effect exists, between-tissue null

**Possible:**
- Within COAD: faster cells → more mutations
- Within PRAD: faster cells → more mutations
- But comparing COAD vs PRAD → tissue-specific factors dominate

**Requires different test:**
- Same tissue, different proliferation markers (Ki67, MKI67)
- TCGA has RNA-seq data for this
- But high effort, low probability of success given current failure

---

## Decision Matrix

### Option A: Kill Project, Publish Negative Result (✅ RECOMMENDED)

**Rationale:**
- Hypothesis clearly rejected (r=-0.17 at n=89, r=-0.05 at n=79)
- Pre-registration prevents p-hacking
- Negative result has scientific value

**Publication target:**
- PLOS Computational Biology
- F1000Research
- bioRxiv → medRxiv (clinical relevance)

**Title:**
> "No Evidence for Cell Doubling Time–Somatic Mutation Rate Association in TCGA Pan-Cancer Analysis (n=89)"

**Structure:**
1. Introduction: Bilinsky 2025 framework, hypothesis extension
2. Methods: TCGA data, pre-registration, kill criteria
3. Results: n=5 → n=49 → n=89 progression, confounding test
4. Discussion: Why n=49 misled, tissue-specific factors, ATP ≠ mutagenesis
5. Conclusion: Radiosensitivity mechanism does not generalize to mutagenesis

**Value:**
- Prevents other researchers from wasting time
- Demonstrates rigorous falsification
- Pre-registration case study

**Timeline:**
- Manuscript: 2-3 weeks
- Submission: May 2026
- Review: 1-2 months

**Effort:** LOW (1 month total)

---

### Option B: Pivot to H3 (ATP Proxy) (⚠️ HIGH RISK)

**Rationale:**
- Doubling time is a PROXY for ATP
- Test ATP directly (OXPHOS expression from RNA-seq)
- Hypothesis: High OXPHOS → low ATP availability → more mutations

**Advantages:**
- Direct mechanism test (not proxy)
- Uses same TCGA samples (RNA-seq available)
- If works → stronger evidence than doubling time

**Disadvantages:**
- H0 (doubling time) already failed → H3 likely also fails
- OXPHOS ≠ actual ATP levels (expression ≠ activity)
- Tissue-specific confounding remains
- No reason to believe this will succeed

**Recommendation:** ONLY if user has strong prior belief in ATP mechanism

**Timeline:** 2-3 weeks for test

---

### Option C: Within-Tissue Test (⚠️ VERY HIGH RISK)

**Rationale:**
- Between-tissue comparison confounded
- Same tissue, different proliferation → cleaner test

**Method:**
1. Download RNA-seq for COAD samples (n=10)
2. Extract proliferation markers: Ki67, MKI67, CCND1
3. Correlate proliferation proxy with mutation rate within COAD

**Expected:**
- If hypothesis true: r > 0 within COAD
- If still null/negative → hypothesis definitively dead

**Disadvantages:**
- Small sample (n=10 per tissue)
- Proliferation markers ≠ actual doubling time
- High effort (RNA-seq processing)
- Low probability of success given n=89 failure

**Recommendation:** NOT worth the effort

**Timeline:** 3-4 weeks

---

### Option D: Close Project, Move to Next (✅ ALSO VALID)

**Rationale:**
- Hypothesis failed
- Negative result publication = moderate value
- User time better spent on ARCHCODE, ChernoffPy, other projects

**Advantages:**
- Zero additional effort
- Lessons learned already documented
- Pre-registration protocol validated

**Disadvantages:**
- No publication from 1 week of work
- But publication is not mandatory for exploratory projects

---

## Final Recommendation

### Primary: **Option A (Publish Negative Result)**

**Why:**
1. Scientific honesty: we predicted r>0.4, got r=-0.17 → report it
2. Pre-registration proves hypothesis was genuine (not p-hacked)
3. Prevents replication waste (others won't try the same)
4. Demonstrates ARCHCODE falsification lessons applied to new domain
5. Adds to portfolio: "rigorous methodology" track record

**Narrative:**
> "We pre-registered a hypothesis linking cell doubling time to somatic mutation rates, based on Bilinsky 2025 ATP framework. Data from 89 TCGA samples across 7 cancer types rejected the hypothesis (r=-0.17, p=0.11). Small-sample analysis (n=49) initially showed spurious support (r=+0.36), but larger sample revealed the effect was driven by MSI-high contamination and sampling bias. This case study demonstrates the importance of pre-registration and adequate sample sizes in computational biology."

**Next steps:**
1. Write manuscript (2-3 weeks)
2. Submit to F1000Research or PLOS Comp Bio
3. Move to next project (ARCHCODE taxonomy, ChernoffPy)

---

### Secondary: **Option D (Close, No Publication)**

**If user prefers:**
- Focus on high-impact projects (ARCHCODE)
- Treat this as method validation (pre-registration protocol works)
- Documented in stress_biology/ for future reference

---

## What We Learned

**Positive outcomes (даже при провале гипотезы):**

1. **Pre-registration protocol works**
   - Prevented p-hacking at n=49
   - Forced honest reporting of n=89 failure
   - Git timestamp proves hypothesis was genuine

2. **ARCHCODE falsification lessons transferred**
   - Confounding test (tissue type vs doubling time) applied correctly
   - Matched controls concept considered
   - Baseline comparison performed

3. **Simpson's paradox is real**
   - n=5: wrong direction
   - n=49: right direction (spurious)
   - n=89: wrong direction (true signal)
   - Small samples CANNOT be trusted

4. **Negative results have value**
   - Saves community effort
   - Demonstrates rigorous methodology
   - Adds to falsification track record

5. **Sample size matters**
   - n=49 insufficient for 7-tissue comparison
   - n=89 minimum for reliable effect detection
   - Future: start with n=100+ for between-group tests

---

## Files Created This Session

```
stress_biology/
├── data/
│   ├── batch_merged.csv           (n=49)
│   └── all_merged.csv             (n=89)
├── results/
│   ├── PRELIMINARY_RESULTS.md     (n=5, r=-0.5)
│   ├── BATCH_RESULTS_N49.md       (n=49, r=+0.36)
│   ├── CONFOUNDING_ANALYSIS.md    (tissue type test)
│   ├── CRITICAL_N89_FAILURE.md    (n=89, r=-0.17, hypothesis rejected)
│   └── FINAL_DECISION.md          (this file)
├── HYPOTHESIS.md                  (pre-registered, frozen)
└── SESSION_REPORT.md              (work log)
```

---

## Status

**Project:** 🔴 KILLED (hypothesis rejected)

**Recommendation:** Publish negative result (Option A)

**Timeline:**
- Manuscript: 2-3 weeks
- Submission: May 2026

**Alternative:** Close project, move to ARCHCODE/ChernoffPy (Option D)

---

**Generated:** 2026-04-25  
**Analyst:** Claude Sonnet 4.5 + Sergey Boyko  
**Data:** 89 TCGA samples, 7 tissues, 3 sample sizes (n=5, n=49, n=89)  
**Verdict:** ATP-driven mutagenesis hypothesis REJECTED by data
