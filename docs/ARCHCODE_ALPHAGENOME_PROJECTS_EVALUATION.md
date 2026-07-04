# ARCHCODE × AlphaGenome: Проектная Оценка (10-балльная шкала)

**Дата:** 2026-05-08  
**Baseline:** HBB CAGE p=2.77e-4 (5.5×), MLH1 p=0.022 (3.7×), BRCA1/TP53 ns (coding loci)  
**Текущие данные:** 12 AlphaGenome JSON результатов, 9 loci, 1,103 HBB variants, 20 pearls  

---

## Метрика оценки

| Критерий | Вес | Описание |
|----------|-----|----------|
| **Feasibility** | 25% | Реализуемость с текущими ресурсами (API quota, время, данные) |
| **Impact** | 30% | Научный/продуктовый вес (публикация, цитирование, применимость) |
| **Novelty** | 20% | Новизна (не duplicate чужих работ) |
| **Time to completion** | 15% | Скорость (Days/Weeks/Months) |
| **Risk** | 10% | Риск провала (null result, API limits, circular logic) |

**Итоговая шкала:**
- 9-10: Exceptional (сделать в первую очередь)
- 7-8: Strong (высокий приоритет)
- 5-6: Moderate (второй приоритет, если ресурсы позволяют)
- 3-4: Weak (отложить или не делать)
- 1-2: Avoid (высокий риск провала или низкая ценность)

---

## Проект 1: ARCHCODE × AlphaGenome Concordance Benchmark

**Описание:** Бенчмарк согласованности ARCHCODE LSSIM vs AlphaGenome multimodal outputs (CAGE, ATAC, RNA-seq, contact, histone) на 9 loci × 30K variants.

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 8/10 | ✓ API access есть, 12 JSON уже готовы. ✗ Нужно 9 loci × multimodal (CAGE+ATAC+RNA+contact) = дорого (API quota), ~100-200 USD |
| **Impact** | 9/10 | ✓ Первый independent clinical benchmark для AlphaGenome regulatory variants. ✓ DeepMind не опубликовал ClinVar validation. ✓ Публикуемо в Bioinformatics/NAR. ✗ Не breakthrough, но solid методологический вклад |
| **Novelty** | 8/10 | ✓ AlphaGenome + clinical variants — неизведанная территория. ✓ Falsification-first benchmark — уникально. ✗ Concordance analysis сам по себе стандартен |
| **Time** | 6/10 | ~2-3 недели (API calls медленные, rate limits, multimodal = 5 outputs × 30K variants = большой объём). ✗ Риск timeout/quota |
| **Risk** | 7/10 | ⚠️ Риск: null concordance (ARCHCODE category artifact, AlphaGenome coding-blind). ✓ Но null result тоже публикуем (честный вывод) |

**Итого:** **7.8/10** — Strong  
**Рекомендация:** Делать, но **ограничить scope:** HBB + MLH1 (regulatory loci, где есть сигнал) + BRCA1 (negative control, coding). Не все 9 loci (слишком дорого, много null).

**MVP (1 week):**
- HBB: pearls vs controls, CAGE + ATAC + contact
- Concordance: Spearman ρ (LSSIM vs AlphaGenome delta)
- Statistical gate: permutation + matched controls
- Output: concordance_benchmark_HBB.json + ADR-027

---

## Проект 2: 73bp HBB Promoter Cluster — Category-Matched Validation

**Описание:** ADR-026 выявил category leakage (75% pearls = promoter, 68% zone = promoter). Следующий шаг: category-matched control — сравнить promoter pearls vs random promoter variants в той же зоне.

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 9/10 | ✓ Данные есть (HBB_Unified_Atlas.csv). ✓ Код есть (validate_73bp_cluster.py). ✓ Нужно только добавить category-matched sampling (10 строк кода) |
| **Impact** | 6/10 | ✓ Научно честно (исключает circularity). ✓ Нужно для Paper 3. ✗ Узкий scope (только HBB 73bp). ✗ Если FAIL → убивает promoter cluster как discovery |
| **Novelty** | 5/10 | ✗ Category-matched controls — стандартная практика. ✓ Но в ARCHCODE не применялась (честный gap) |
| **Time** | 9/10 | 1-2 дня (скрипт готов, нужно только добавить category-matched permutation) |
| **Risk** | 5/10 | ⚠️ HIGH RISK: если promoter pearls НЕ обогащены в 73bp зоне по сравнению с random promoter variants → cluster провален. ✓ Но это честный null result |

**Итого:** **6.8/10** — Moderate  
**Рекомендация:** Делать **обязательно** (блокирует Paper 3), но ожидать FAIL. Если FAIL → честно документировать и pivot на cross-category consistency (Option B из ADR-026).

**MVP (2 days):**
- Modify validate_73bp_cluster.py: добавить `category_matched_control()`
- Null hypothesis: random promoter variants (N=15, из 1,103 HBB)
- Test: промоторные pearls в 73bp зоне vs random промоторные variants в 73bp зоне
- Verdict: PASS/FAIL (p<0.01 with category-matched control)

---

## Проект 3: AlphaGenome Multimodal Pearl Validation (HBB + MLH1)

**Описание:** Расширить CAGE-only validation на multimodal: CAGE + ATAC + RNA-seq + histone + contact для всех 20 HBB pearls + MLH1 pearls.

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 7/10 | ✓ API access. ✗ Дорого (20 pearls × 5 modalities × 2 loci = ~$50-100 USD API cost). ✗ Rate limits (медленно) |
| **Impact** | 8/10 | ✓ Multimodal = сильнее чем CAGE-only. ✓ Покажет какие modalities согласуются (CAGE yes, contact no). ✓ Публикуемо как supplement к Paper 3 |
| **Novelty** | 7/10 | ✓ Multimodal clinical validation — мало кто делал. ✗ Концепция multimodal не нова (DeepMind сами продвигают) |
| **Time** | 7/10 | ~1 week (API calls + analysis + visualization) |
| **Risk** | 6/10 | ⚠️ Риск: modalities diverge (CAGE yes, ATAC/contact no) → сложно интерпретировать. ✓ Но это тоже информативно |

**Итого:** **7.1/10** — Strong  
**Рекомендация:** Делать как **Paper 3 validation layer**, но только HBB (MLH1 = nice-to-have, не критично).

**MVP (1 week):**
- HBB 20 pearls: CAGE + ATAC + RNA-seq + H3K27ac (4 modalities, contact skip — уже null из ADR-007)
- Compare pearls vs benign controls (matched by category if possible)
- Output: multimodal_validation_HBB.json
- Metrics: per-modality p-values + multimodal concordance score

---

## Проект 4: AlphaGenome ISM (In-Silico Mutagenesis) Promoter Scan

**Описание:** Для HBB 73bp cluster: сделать полный ISM scan (мутация каждой позиции → AlphaGenome CAGE delta). Визуализация: heatmap позиций с наибольшим CAGE disruption.

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 8/10 | ✓ Код уже есть (`alphagenome_ism_promoter.json`). ✓ Нужно только расширить на 73bp (было 15bp). ✗ 73bp × 3 alt bases = 219 API calls (~$20-30) |
| **Impact** | 7/10 | ✓ Красивая визуализация (publication figure). ✓ Покажет hotspot positions внутри 73bp. ✗ Узкий scope (только HBB) |
| **Novelty** | 6/10 | ✗ ISM — стандартная техника (Avsec et al. используют сами). ✓ Но на clinical locus — ново |
| **Time** | 8/10 | 3-4 дня (API calls + heatmap viz) |
| **Risk** | 7/10 | ✓ Low risk (ISM guaranteed to work, question is signal strength) |

**Итого:** **7.2/10** — Strong  
**Рекомендация:** Делать как **Paper 3 Figure** (красивая визуализация для публикации). Но **после** category-matched validation (Проект 2) — если cluster провален, ISM бессмыслен.

**MVP (3 days):**
- ISM scan: chr11:5227099-5227172 (74bp), all positions, A/C/G/T → CAGE delta
- Heatmap: position × alt base, color = CAGE disruption magnitude
- Mark pearl positions (overlay)
- Output: ism_scan_73bp_HBB.json + figure

---

## Проект 5: Falsification-First AlphaGenome Wrapper (ag-falsifier)

**Описание:** Open-source Python библиотека, которая wraps AlphaGenome API и автоматически запускает falsification tests (matched controls, permutation, shuffled labels, modality agreement).

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 7/10 | ✓ Код уже есть (validate_73bp_cluster.py = proof of concept). ✗ Нужно generalize для любого locus/variant set |
| **Impact** | 9/10 | ✓ Высокий impact: community tool, не только для ARCHCODE. ✓ DeepMind community нуждается в validation harness. ✓ Цитируемо (методологический вклад) |
| **Novelty** | 9/10 | ✓ Никто не сделал falsification-first wrapper для AlphaGenome. ✓ Уникальная ниша |
| **Time** | 5/10 | ~2-3 weeks (generalize, docs, tests, PyPI package) |
| **Risk** | 6/10 | ⚠️ Риск: мало кто будет использовать (узкая аудитория — только AlphaGenome users). ✓ Но даже 10 users = success |

**Итого:** **7.4/10** — Strong  
**Рекомендация:** Делать как **standalone open-source проект** (отдельный repo, не в ARCHCODE). Название: `ag-falsifier` или `alphagenome-integrity`. Target: GitHub trending, Python Weekly, DeepMind forums.

**MVP (2 weeks):**
```python
from ag_falsifier import validate_hypothesis

result = validate_hypothesis(
    variants=["chr11:5227100:G>A", ...],
    controls="matched",  # category-matched benign
    modalities=["CAGE", "ATAC"],
    tests=["fisher", "permutation", "shuffle", "modality_agreement"]
)

print(result.verdict)  # PASS / WEAK / FAIL
print(result.report())  # Markdown ADR
```

---

## Проект 6: ARCHCODE × AlphaGenome Closed-Loop Discovery System

**Описание:** Automated pipeline: ARCHCODE генерирует structural hypotheses → AlphaGenome валидирует → LLM agent пишет interpretation → user approves → next iteration.

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 5/10 | ✗ Сложная интеграция (ARCHCODE TS + AlphaGenome Python + LLM agent + feedback loop). ✗ Нужен orchestrator |
| **Impact** | 8/10 | ✓ Если работает — это breakthrough (autonomous discovery system). ✗ Если не работает — пустая демонстрация |
| **Novelty** | 10/10 | ✓ Никто не делал closed-loop genomics discovery с LLM agent + multimodal validation |
| **Time** | 3/10 | ~1-2 months (долго, сложно, много moving parts) |
| **Risk** | 4/10 | ⚠️ HIGH RISK: может не converge (ARCHCODE null, AlphaGenome null, LLM hallucination). ⚠️ Может быть validation theater |

**Итого:** **6.0/10** — Moderate  
**Рекомендация:** **Отложить** до тех пор, пока Проекты 1-3 не покажут, что concordance реально работает. Если concordance FAIL → closed-loop бессмыслен.

**Defer until:** ARCHCODE × AlphaGenome concordance ≥ 0.5 (Spearman ρ) на хотя бы 1 locus.

---

## Проект 7: Cross-Locus AlphaGenome CAGE Transfer Test

**Описание:** Проверить, работает ли AlphaGenome CAGE на других regulatory loci (не только HBB + MLH1). Тест: TERT promoter mutations, GJB2 enhancer variants, CFTR regulatory region.

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 8/10 | ✓ Данные есть (9 loci portfolio). ✓ API access. ✗ Дорого (9 loci × 15 variants = ~$50-100 API cost) |
| **Impact** | 7/10 | ✓ Покажет generalizability. ✗ Уже знаем, что coding loci (BRCA1, TP53) = null (ADR batch_cage_9loci.json) |
| **Novelty** | 5/10 | ✗ Cross-locus validation — стандартная практика. ✓ Но на AlphaGenome CAGE — ново |
| **Time** | 7/10 | ~1 week (API calls + analysis) |
| **Risk** | 6/10 | ⚠️ Риск: большинство loci покажут null (coding-dominant). ✓ Но это информативно (mechanism specificity) |

**Итого:** **6.6/10** — Moderate  
**Рекомендация:** Делать как **secondary priority** (после Проектов 1-3). Фокус: только regulatory loci (TERT promoter, GJB2, CFTR). Skip coding (BRCA1, TP53 — уже null).

**MVP (1 week):**
- TERT promoter mutations (C228T, C250T — known hotspots)
- GJB2 enhancer-proximal variants
- CFTR regulatory region (5' UTR, promoter)
- Output: cross_locus_cage_validation.json

---

## Проект 8: One-Page External Brief для Outreach

**Описание:** Написать 1-страничный brief для outreach (Arc Institute, DeepMind, Ginkgo, Elphège Nora, Geoff Fudenberg).

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 10/10 | ✓ Просто написать (1-2 часа) |
| **Impact** | 8/10 | ✓ Может открыть collaboration / endorsement / wet-lab validation. ✗ Риск: игнор (low response rate в cold outreach) |
| **Novelty** | 4/10 | ✗ Brief — не научный вклад |
| **Time** | 10/10 | 1 день (написать + review) |
| **Risk** | 8/10 | ✓ Low risk (если игнор — ничего не теряем) |

**Итого:** **8.0/10** — Strong  
**Рекомендация:** Делать **немедленно** (Quick win, low effort, high potential upside).

**Structure:**
```markdown
# ARCHCODE × AlphaGenome: Falsification-First Regulatory Variant Validation

**One-line pitch:** Independent AlphaGenome-based validation workflow for disease-associated regulatory variants, with falsification-first controls and preliminary HBB concordance results.

## Current Signal
- HBB pearls: CAGE -18% vs benign -0.1% (p=2.77e-4, AlphaGenome real API)
- MLH1: CAGE -3.7× stronger for pathogenic (p=0.022)
- BRCA1/TP53: null (coding loci, expected)

## Validation Workflow
- ARCHCODE structural fragility → AlphaGenome multimodal outputs
- Matched controls, permutation, shuffled labels, modality agreement
- ADR log: null results as first-class artifacts

## Ask
Feedback on: (a) validation harness as open-source tool, (b) HBB 73bp cluster as case study, (c) wet-lab collaboration.

[1-page PDF] | [GitHub] | [Contact]
```

---

## Проект 9: MemGraph Transfer Test (AlphaGenome Hypotheses)

**Описание:** Интеграция AlphaGenome результатов в MemGraph Research Platform (Days 4-6). Тест: можно ли transferить AlphaGenome-validated hypotheses между проектами?

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 6/10 | ✓ MemGraph infrastructure готова (Days 1-3). ✗ Нужно интегрировать AlphaGenome outputs в graph |
| **Impact** | 6/10 | ✓ Proof of concept для cross-project hypothesis transfer. ✗ Узкая аудитория (только ARCHCODE + будущие genomics проекты) |
| **Novelty** | 7/10 | ✓ Cross-project genomic hypothesis transfer — ново |
| **Time** | 6/10 | ~1 week (integration + transfer test) |
| **Risk** | 6/10 | ⚠️ Риск: слишком мало validated hypotheses (только HBB + MLH1) для transfer test |

**Итого:** **6.2/10** — Moderate  
**Рекомендация:** **Defer** до тех пор, пока не будет ≥3 validated loci (сейчас только 2). Это более meta-проект (про MemGraph), чем про AlphaGenome.

---

## Проект 10: AlphaGenome Forum Post / Blog (Community Contribution)

**Описание:** Написать пост для DeepMind/AlphaGenome community: "First independent clinical validation of AlphaGenome CAGE on disease variants".

### Оценка

| Критерий | Score | Обоснование |
|----------|-------|-------------|
| **Feasibility** | 10/10 | ✓ Легко написать (2-3 часа) |
| **Impact** | 7/10 | ✓ Visibility в DeepMind community. ✓ Может привести к collaboration. ✗ Не peer-reviewed (меньше scientific credit) |
| **Novelty** | 5/10 | ✗ Blog post — не научный вклад. ✓ Но первый independent validation — ново |
| **Time** | 9/10 | 1-2 дня (написать + review) |
| **Risk** | 8/10 | ✓ Low risk (если игнор — ничего не теряем) |

**Итого:** **7.8/10** — Strong  
**Рекомендация:** Делать **после** завершения Проектов 1-3 (чтобы было что показать). Post structure: HBB results + validation workflow + code/data links.

**Target:** DeepMind forums, LessWrong, Twitter/X genomics community.

---

## Итоговый Рейтинг (Top 10 → Top 5)

| Rank | Проект | Score | Priority | Timeline |
|------|--------|-------|----------|----------|
| **1** | **One-Page External Brief** | 8.0 | P0 | 1 day |
| **2** | **AlphaGenome Forum Post** | 7.8 | P1 | 1-2 days |
| **3** | **Concordance Benchmark (HBB+MLH1)** | 7.8 | P0 | 1 week |
| **4** | **ag-falsifier (Open-Source Wrapper)** | 7.4 | P1 | 2 weeks |
| **5** | **ISM Promoter Scan (73bp HBB)** | 7.2 | P2 | 3 days |
| 6 | Multimodal Pearl Validation | 7.1 | P2 | 1 week |
| 7 | 73bp Category-Matched Validation | 6.8 | P0 | 2 days |
| 8 | Cross-Locus CAGE Transfer | 6.6 | P3 | 1 week |
| 9 | MemGraph Transfer Test | 6.2 | P3 | 1 week |
| 10 | Closed-Loop Discovery System | 6.0 | DEFER | 1-2 months |

---

## Рекомендованный 14-дневный план

### Week 1: Quick Wins + Validation Gate

| День | Проект | Deliverable |
|------|--------|-------------|
| **1** | One-Page External Brief | `ARCHCODE_AlphaGenome_Brief_2026.pdf` |
| **2-3** | 73bp Category-Matched Validation | `ADR-027_73bp_category_matched.md` (честный null result если FAIL) |
| **4-7** | Concordance Benchmark (HBB only) | `concordance_benchmark_HBB.json` + `ADR-028` |

### Week 2: Publication Layer + Community

| День | Проект | Deliverable |
|------|--------|-------------|
| **8-10** | ISM Promoter Scan (73bp HBB) | `ism_scan_73bp_HBB.json` + heatmap figure |
| **11-12** | AlphaGenome Forum Post | Blog post + code links |
| **13-14** | ag-falsifier (MVP) | GitHub repo + PyPI package (alpha) |

**Total output:** 6 deliverables, 2 weeks, ~$100-150 API cost.

---

## Что НЕ делать (Anti-Priorities)

❌ **Closed-Loop Discovery System** — слишком рано, нужен concordance proof first  
❌ **MemGraph Transfer Test** — слишком мало validated hypotheses (2 loci)  
❌ **Full 9-loci AlphaGenome batch** — дорого ($500+), много null results (coding loci)  
❌ **Nucleotide Transformer integration** — уже провалено 3 раза (ADR-025), pivot to AlphaGenome  
❌ **Within-category AUC improvement** — circular (ADR-003), не исправить без унификации pipeline  

---

## Критические Assumptions (честно)

### Assumption 1: AlphaGenome CAGE generalizability

**Claim:** HBB + MLH1 работают → другие regulatory loci тоже сработают.  
**Risk:** Может быть promoter-specific artifact (не enhancer, не CTCF).  
**Test:** Cross-locus CAGE transfer (Проект 7).  

### Assumption 2: Category-matched control passes

**Claim:** 73bp cluster enrichment сохранится после category matching.  
**Risk:** HIGH — если FAIL, cluster killed.  
**Test:** Проект 2 (обязателен для Paper 3).  

### Assumption 3: Multimodal concordance

**Claim:** CAGE + ATAC + RNA-seq + histone согласуются.  
**Risk:** Modalities могут diverge (CAGE yes, ATAC no).  
**Test:** Проект 3.  

### Assumption 4: Community interest в ag-falsifier

**Claim:** AlphaGenome users нуждаются в validation harness.  
**Risk:** Узкая аудитория (может быть <100 users worldwide).  
**Test:** GitHub stars, PyPI downloads после релиза.  

---

## Честный Baseline Check (Zero-Based)

**Вопрос:** Если бы у меня НЕ было AlphaGenome API, что бы я делал?

**Ответ:**
1. ARCHCODE standalone — уже убито within-category null (ADR-003)
2. Router Class B — убито matched controls (p=0.996)
3. 73bp cluster — убито category leakage (ADR-026)

**Вывод:** AlphaGenome API = единственный живой validation pathway. Без него ARCHCODE = dead end.

**Следствие:** Делать фокус на AlphaGenome integration максимальным приоритетом.

---

## Final Recommendation (Жёсткий приоритет)

### Top 3 Projects (Must Do)

1. **One-Page External Brief** (1 day) — quick win, opens doors
2. **73bp Category-Matched Validation** (2 days) — blocks Paper 3, expect FAIL but document honestly
3. **Concordance Benchmark (HBB only)** (1 week) — core scientific contribution

### Next 2 Projects (High Value)

4. **ag-falsifier** (2 weeks) — community tool, long-term citation value
5. **AlphaGenome Forum Post** (1-2 days) — visibility, low effort

### Everything Else = DEFER

Wait until Top 5 complete, then re-evaluate based on:
- Concordance results (if null → pivot)
- Category-matched results (if FAIL → kill 73bp cluster)
- Community response (if high interest → expand ag-falsifier)

---

**Честный итог:** AlphaGenome API превращает ARCHCODE из "killed by falsification" в "validation platform". Но это работает ТОЛЬКО если:

1. ✅ Concordance ≥ 0.5 (Spearman ρ) на хотя бы 1 regulatory locus
2. ✅ Category-matched controls pass (73bp cluster survives)
3. ✅ Multimodal outputs agree (CAGE + ATAC + RNA-seq)

Если все 3 FAIL → ARCHCODE × AlphaGenome тоже killed. Но это честный null result, публикуемый как "границы 3D-genome variant interpretation".

**Science survives honesty.**
