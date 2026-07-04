# ARCHCODE Hypothesis Evaluation — 2026-05-10

**Context:** 6 новых гипотез предложены в момент PROJECT_FREEZE (May 9 - June 5)

**Критерии оценки (composite score /10):**
- Testability (проверяемость) — 30%
- Effort/ROI (трудоёмкость/отдача) — 25%
- Scientific value (научная ценность) — 25%
- Risk mitigation (низкий риск false positive) — 10%
- Alignment с PROJECT_FREEZE — 10%

---

## О1: Tissue Match → AUC ↑

**Суть:** Добавить tissue expression match как признак в классификатор → ΔAUC измеримо выше.

**Оценка:**
- **Testability:** 9/10 — чистый A/B test (baseline AUC vs +tissue_match AUC)
- **Effort/ROI:** 8/10 — 1 день работы, GTEx API доступен, ClinVar датасет готов
- **Value:** 6/10 — улучшение классификатора, НО H2 уже показала category dominance (AUC=0.98 от category alone)
- **Risk:** 4/10 — ВЫСОКИЙ риск ещё одного category artifact (tissue ≈ category leakage)
- **Alignment:** 2/10 — нарушает "no new claims" (ΔAUC = новый claim)

**Composite Score:** (9×0.3 + 8×0.25 + 6×0.25 + 4×0.1 + 2×0.1) = **6.6/10**

**Вердикт:** Хорошая инженерная гипотеза, но рискует повторить H2 (category artifact). Требует категориально-matched контроль (promoter variants matched by tissue expression).

**Kill Criterion:** ΔAUC < 0.02 OR category-matched control показывает ΔAUC < 0.01 → H отвергается.

---

## О2: FOXP3 Patients in Hotspots

**Суть:** Пациенты с FOXP3 мутациями чаще попадают в известные pathogenic hotspots (ClinVar/OMIM).

**Оценка:**
- **Testability:** 10/10 — простой chi-square test (hotspot vs non-hotspot × pathogenic vs benign)
- **Effort/ROI:** 7/10 — 3 часа работы, но узкий scope (один ген, X-linked)
- **Value:** 5/10 — limited generalizability (N=1 locus, специфичный паттерн)
- **Risk:** 6/10 — sex bias confounding (X-linked), sampling bias (ClinVar ascertainment)
- **Alignment:** 2/10 — нарушает "no new loci" (FOXP3 не был в 9 основных loci)

**Composite Score:** (10×0.3 + 7×0.25 + 5×0.25 + 6×0.1 + 2×0.1) = **6.8/10**

**Вердикт:** Самая быстрая и чистая гипотеза, но узкий scope. Хорошая proof-of-concept для hotspot enrichment analysis.

**Kill Criterion:** OR < 1.5 OR p > 0.05 (chi-square) OR sex-adjusted OR < 1.3 → H отвергается.

---

## О3: Benford's Law на SSIM Scores

**Суть:** SSIM scores от 3D-структур следуют закону Бенфорда — аномалии детектируются через отклонение.

**Оценка:**
- **Testability:** 7/10 — KS-test прост, НО применимость Benford к [0,1] распределениям под вопросом
- **Effort/ROI:** 9/10 — 30 минут (самая дешёвая гипотеза), quick falsification
- **Value:** 3/10 — Benford работает для чисел с широким диапазоном (log-uniform), SSIM ∈ [0,1] — 1 порядок
- **Risk:** 2/10 — ОЧЕНЬ ВЫСОКИЙ риск false hypothesis (Benford применим к размерам файлов, популяциям, не similarity scores)
- **Alignment:** 2/10 — новый метод валидации (нарушает freeze)

**Composite Score:** (7×0.3 + 9×0.25 + 3×0.25 + 2×0.1 + 2×0.1) = **5.5/10**

**Вердикт:** Дешёво проверить, но скорее всего ЛОЖНАЯ гипотеза. Benford требует log-uniform distribution (экспоненциальный рост), SSIM = bounded similarity metric.

**Kill Criterion:** KS-test p > 0.05 для реальных SSIM vs. Benford OR shuffle test показывает те же отклонения → закон не применим.

**Литература check:** Benford validated на: размеры файлов (10^1 - 10^9 bytes), финансы (0.01 - 10^6 USD), НО similarity scores [0,1] не попадают в этот класс.

---

## Н1: ARCHCODE + VEP Router

**Суть:** VEP (Variant Effect Predictor) как upstream роутер — отсеивать benign варианты до ARCHCODE, экономить compute.

**Оценка:**
- **Testability:** 8/10 — требует интеграция VEP API, precision/recall metrics чёткие
- **Effort/ROI:** 7/10 — 1 неделя (VEP REST API + threshold tuning), но сильное engineering improvement
- **Value:** 8/10 — практическое ускорение pipeline (VEP scores бесплатны), реальная production value
- **Risk:** 6/10 — VEP может не добавить сигнала (уже много predictors в VEP: SIFT, PolyPhen, CADD)
- **Alignment:** 1/10 — **КРИТИЧЕСКОЕ нарушение:** 1 неделя работы = 20% от 5-week manuscript timeline

**Composite Score:** (8×0.3 + 7×0.25 + 8×0.25 + 6×0.1 + 1×0.1) = **7.2/10**

**Вердикт:** ЛУЧШАЯ инженерная гипотеза в списке. Хорошо определённый scope, чёткие метрики, практическая ценность. НО нарушает freeze.

**Kill Criterion:** 
- Precision < 0.90 на VEP-filtered subthreshold cases → роутер не работает
- OR recall@99% precision не улучшается vs. ARCHCODE alone → нет выигрыша

**Рекомендация:** Отложить до ПОСЛЕ manuscript submission (June 5+). Это engineering improvement, не validation.

---

## Н2: Фармакогеномика CYP2D6

**Суть:** ARCHCODE предсказывает патогенность CYP2D6 вариантов для drug metabolism (codeine, tamoxifen, antidepressants).

**Оценка:**
- **Testability:** 6/10 — НЕЯСНЫЙ scope (что именно тестируем? Star-alleles? Rare variants? Clinical outcomes?)
- **Effort/ROI:** 6/10 — 2-3 дня, НО "платная часть" непонятна (PharmGKB free, CPIC free, что стоит денег?)
- **Value:** 9/10 — ОЧЕНЬ ВЫСОКАЯ клиническая ценность (FDA warnings, precision medicine), $$$ potential
- **Risk:** 5/10 — CYP2D6 специфичен (star-allele nomenclature, copy number variations), ARCHCODE обучен на general pathogenic variants
- **Alignment:** 0/10 — **ПОЛНОСТЬЮ НОВЫЙ ПРОЕКТ** (новый locus, новый phenotype, новый endpoint)

**Composite Score:** (6×0.3 + 6×0.25 + 9×0.25 + 5×0.1 + 0×0.1) = **6.1/10**

**Вердикт:** Высокая ценность, НО слабо определённый scope. Требует уточнения:
1. Что тестируем: star-alleles (known) vs rare variants (unknown)?
2. Endpoint: enzyme activity (in vitro) vs clinical outcomes (slower metabolism)?
3. Данные: PharmGKB (free), CPIC (free) — что платное?
4. Применимость ARCHCODE: обучен на structural disruption (promoter loops), CYP2D6 = coding gene (missense)

**Kill Criterion:** (не может быть сформулирован без уточнения scope)

**Рекомендация:** НЕ запускать до уточнения scope. Если цель = rare CYP2D6 variants → требует отдельное обучение (PharmGKB labels ≠ ClinVar pathogenic).

---

## Н3: Mpemba Effect × Chromatin 3D Structure

**Суть:** Связь InfoMpemba эффекта (горячее охлаждается быстрее через информационную насыщенность) и chromatin 3D remodeling — domains как information-rich systems.

**Оценка:**
- **Testability:** 4/10 — требует Hi-C datasets (ENCODE), DoWhy causal identification, strong biological prior
- **Effort/ROI:** 3/10 — 2+ НЕДЕЛИ (не 2 дня!), очень низкий ROI на current phase
- **Value:** 10/10 — Nature/Science-level если работает (новый physical mechanism для chromatin dynamics)
- **Risk:** 2/10 — КРАЙНЕ ВЫСОКИЙ риск провала (теория без данных, interdisciplinary gap, может быть spurious analogy)
- **Alignment:** 0/10 — **PhD thesis scope**, не "one more experiment"

**Composite Score:** (4×0.3 + 3×0.25 + 10×0.25 + 2×0.1 + 0×0.1) = **4.5/10**

**Вердикт:** Самая амбициозная, НО слишком рискованно и трудоёмко для current phase. Требует:
1. Hi-C time-series данные (heat shock → chromatin remodeling)
2. DoWhy causal graph (information entropy → relaxation time)
3. Physical model (Mpemba в chromatin = stronger loops relax faster?)
4. Biological validation (wet-lab experiment или strong in silico evidence)

**Kill Criterion:** (не может быть сформулирован — гипотеза слишком широкая)

**Рекомендация:** Отложить до ПОСЛЕ ARCHCODE paper. Это отдельный проект (6+ месяцев), не extension.

**Alternative approach:** Сформулировать УЗКУЮ версию гипотезы:
- H3.1: CTCF loops с более высоким contact frequency (stronger) показывают faster relaxation после heat shock (Hi-C time-series)
- Testable за 1 неделю на ENCODE данных
- Kill criterion: Spearman ρ(contact_strength, relaxation_time) > -0.3 → no Mpemba-like effect

---

## ИТОГОВЫЙ РЕЙТИНГ (Composite Scores)

| Rank | Hypothesis | Score | Effort | Value | Verdict |
|------|-----------|-------|--------|-------|---------|
| 1 | **Н1 (VEP router)** | 7.2/10 | 1 неделя | Engineering | **DEFER to post-manuscript** |
| 2 | **О2 (FOXP3 hotspots)** | 6.8/10 | 3 часа | Narrow scope | **FAST, but violates freeze** |
| 3 | **О1 (Tissue match)** | 6.6/10 | 1 день | Classifier | **Risk: category artifact** |
| 4 | **Н2 (CYP2D6)** | 6.1/10 | 2-3 дня | High $$$ | **CLARIFY scope first** |
| 5 | **О3 (Benford)** | 5.5/10 | 30 мин | Low | **Likely FALSE hypothesis** |
| 6 | **Н3 (Mpemba×chromatin)** | 4.5/10 | 2+ недели | Nature-level | **PhD thesis, not experiment** |

---

## 🚨 CRITICAL ALERT: PROJECT_FREEZE VIOLATION

**ВСЕ 6 гипотез нарушают PROJECT_FREEZE (May 9 - June 5):**

**PROJECT_FREEZE status (activeContext.md:3,17,23):**
- ✅ Timeline: May 9 - June 5 (5 weeks to manuscript v1.0)
- ✅ Stop rules active: **NO new loci, claims, or experiments**
- ✅ Next: Week 1 — manuscript outline v0.1 (Introduction + Methods draft, 2000 words)
- ✅ Score: 9.0 → 8.5 (честный downgrade: no predictor, framework is main value)
- ✅ H2 (Category Artifact) dominates, confidence 0.95

**Violations:**
- О1: new claim (ΔAUC from tissue match) ❌
- О2: new locus (FOXP3) ❌
- О3: new validation method (Benford anomaly detection) ❌
- Н1: 1 week effort (20% of 5-week timeline) ❌
- Н2: new project (pharma application) ❌
- Н3: new project (interdisciplinary theory) ❌

---

## RECOMMENDATION: DEFER ALL 6 UNTIL POST-SUBMISSION

**Rationale:**
1. **Manuscript priority:** 5 weeks для manuscript v1.0 (June 5 deadline)
2. **Diminishing returns:** Score 8.5/10 уже достигнут, новые эксперименты добавят <0.2 пункта
3. **Scope creep protection:** 6 гипотез = 2-4 недели работы = нарушение timeline
4. **Falsification-first integrity:** Лучше честный 8.5/10 paper с freeze, чем overclaim 9.5/10 с rushed experiments

**Post-submission roadmap (June 5+):**
1. **Week 1-2 (June 5-19):** Н1 (VEP router) — engineering improvement
2. **Week 3 (June 19-26):** О2 (FOXP3) + О1 (tissue match) — fast validation
3. **Week 4 (June 26 - July 3):** Н2 scope clarification → pilot test
4. **Q3 2026:** Н3 narrow version (H3.1: CTCF relaxation) — если Hi-C данные доступны

**Bypass option (ONLY if user explicitly overrides freeze):**
- О2 (FOXP3): 3 часа, не нарушает manuscript writing (параллельно)
- О3 (Benford): 30 мин, quick falsification (скорее всего kill)

---

**Status:** Evaluation complete, awaiting user decision on freeze override.

**Created:** 2026-05-10
**Author:** Claude Code Sonnet 4.5
**Evidence level:** [INFERRED] — composite scoring based on stated parameters
