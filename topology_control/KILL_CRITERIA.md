# Kill Criteria — Pre-Registration

**Created:** 2026-04-25  
**Status:** LOCKED (не менять после начала экспериментов)  
**Purpose:** Предотвратить p-hacking и рационализацию

---

## Принципы

1. **Критерии фиксируются ДО запуска симуляций**
2. **Kill = честная остановка, не провал**
3. **Можно pivot, но не передвигать goalpost**
4. **Negative result = публикуемый результат**

---

## Phase 1: Core Validation

### T2: TOP2 как топологический отжиг

**Hypothesis:** TOP2 использует локальные правила strand passage для глобального снижения топологической сложности.

**Toy model:**
- 100-500 ring polymers
- 3 модели strand passage:
  1. Random (baseline)
  2. Angle-biased
  3. Angle + curvature biased

**Success metrics:**
```python
advantage_score = C_final(biased) / C_final(random)

# SUCCESS если:
advantage_score < 0.7  # biased даёт ≥30% упрощения
AND
num_params <= 3        # простые правила
AND
effect_size > 0.3      # Cohen d

# KILL если:
advantage_score > 0.8  # <20% упрощения
OR
num_params > 5         # переобучение
OR
no effect при coarse-graining
```

**Timeline:** 3 дня  
**Checkpoint:** Day 3, 18:00

**If KILL:**
- Записать в `experiments/t2_top2_annealing/NEGATIVE_RESULT.md`
- Pivot на D1 (spectral)
- Не пытаться "спасти" добавлением параметров

**If SUCCESS:**
- Продолжить Phase 2
- Написать draft для bioRxiv

---

### D1: Spectral 3D controller

**Hypothesis:** GWAS SNPs меняют eigenmode контактного графа, что лучше объясняет causal genes, чем distance.

**Dataset:**
- Hi-C matrix (1 TAD, ~1-2 Mb)
- GWAS SNPs в non-coding
- eQTL data

**Success metrics:**
```python
# Baseline models:
baseline_nearest = predict_eQTL_by_distance()
baseline_overlap = predict_eQTL_by_enhancer_overlap()

# ATR model:
spectral_model = predict_eQTL_by_Δλ()

# SUCCESS если:
AUC(spectral) > AUC(baseline) + 0.10  # +10% improvement
AND
effect survives matched controls       # cell-type matching
AND
Δλ₂ correlates with eQTL (p < 0.01)

# KILL если:
AUC(spectral) <= AUC(baseline)
OR
signal disappears при matched controls
OR
нужно >10 eigenvalues для сигнала
```

**Timeline:** 4 дня  
**Checkpoint:** Day 7, 18:00

**If KILL:**
- Negative result draft
- Остановить D2/D3 (зависят от D1)
- Pivot на H1 (mitochondria)

**If SUCCESS:**
- Продолжить D2 (condensates)
- Тестировать на других GWAS loci

---

## Phase 1 Global Checkpoint

**Day 7 decision point:**

```
IF T2 SUCCESS AND D1 SUCCESS:
  → ATR framework VALIDATED (core)
  → Proceed to Phase 2 full speed
  → Write unified paper

ELIF T2 SUCCESS OR D1 SUCCESS:
  → ATR framework PARTIALLY validated
  → Proceed to Phase 2 cautiously
  → Focus on successful branch

ELIF T2 KILL AND D1 KILL:
  → ATR framework WEAK
  → STOP all topology hypotheses
  → Pivot to H1 (mitochondria, independent)
  → Publish negative result
```

**Hard rule:** Не начинать Phase 2, если Phase 1 полностью провалилась.

---

## Phase 2: Expansion

### T1: Supercoiling field

**Hypothesis:** Суперскручивание распространяется на мегабазные расстояния, координируя домены.

**Success metrics:**
```python
# Корреляционная длина:
ξ_σ = calculate_correlation_length(σ(x), σ(x+Δ))

# SUCCESS если:
ξ_σ > 100 kb               # long-range
AND
ξ_σ correlates with TAD size
AND
boundary elements block propagation

# KILL если:
ξ_σ < 10 kb                # локальная модель достаточна
OR
CTCF boundaries не влияют
```

**Timeline:** 5 дней  
**Depends on:** T2 SUCCESS

---

### H1: МтДНК redox controller

**Hypothesis:** Локальная мтДНК экспрессия даёт advantage по задержке управления.

**Success metrics:**
```python
# Advantage при разных задержках:
advantage(τ_ratio) = ROS_events(nuclear) / ROS_events(local)

# SUCCESS если:
advantage(τ_ratio=100) > 1.5   # ≥50% меньше ROS events
AND
effect robust to noise
AND
advantage monotonic в τ_ratio

# KILL если:
advantage < 1.2 для любого реалистичного τ_ratio
OR
эффект исчезает при шуме
```

**Timeline:** 4 дня  
**Independent:** не зависит от T2/D1

---

### D2: Enhancer condensates

**Hypothesis:** Risk variants сдвигают фазовый порог enhancer hub, давая threshold effects.

**Success metrics:**
```python
# Модели:
linear_model = additive_SNP_effects()
threshold_model = phase_transition_model()

# SUCCESS если:
threshold_model > linear_model (likelihood ratio test)
AND
есть чёткий φ_c (critical concentration)
AND
эффект state-dependent

# KILL если:
linear model не хуже
OR
нет порога в реалистичных параметрах
```

**Timeline:** 5 дней  
**Depends on:** D1 SUCCESS

---

## Phase 3: Specialization

**Запускать ТОЛЬКО если:**
- Phase 1: ≥1 SUCCESS
- Phase 2: ≥1 SUCCESS

**Гипотезы:** T3 (catenation), H2 (heteroplasmy), H3 (nucleoid), D3 (memory)

**Общий kill criterion:**
```
Если гипотеза требует >2 недель параметризации
без ясного пути к эксперименту
→ POSTPONE
```

---

## Meta-Level Kill Switches

### Switch 1: "Too Beautiful To Be True"

**Trigger:**
- Все метрики perfect (AUC > 0.99, p < 10⁻¹⁰)
- Модель работает на всех датасетах без исключений
- Нет failure modes

**Action:**
- STOP
- Искать category leakage / data leakage
- Re-check matched controls

**Reason:** ARCHCODE урок — идеальные результаты часто артефакты.

---

### Switch 2: "Parameter Hell"

**Trigger:**
- Нужно >10 параметров для эффекта
- Эффект чувствителен к точной настройке
- Разные датасеты требуют разных параметров

**Action:**
- KILL
- Модель переобучена или неверна

**Reason:** Stress biology урок — сложные модели скрывают отсутствие сигнала.

---

### Switch 3: "Baseline Dominance"

**Trigger:**
- Простая baseline модель не хуже ATR
- Nearest-gene, overlap, или linear-additive достаточны

**Action:**
- KILL соответствующую гипотезу
- ATR не добавляет предсказательной силы

**Reason:** Бритва Оккама.

---

## Positive Control: What Success Looks Like

**Пример из ARCHCODE (что НЕ прошло):**
```
AUC = 0.975 → KILLED by category control (0.98 without physics)
Pearl detection → KILLED by matched control (n=2-3 effective)
Router Class B → KILLED by matched control (p=0.996)
```

**Что должно пройти ATR:**
```
T2: advantage_score < 0.7, <=3 params, robust to perturbations
D1: +15% AUC, survives matched controls, p < 0.001
Cross-validation: T2 predicts Δλ, D1 confirms through eQTL
```

---

## Reporting Negative Results

**Если гипотеза KILLED:**

1. Записать в `NEGATIVE_RESULT.md`:
   - Hypothesis
   - Test performed
   - Kill criterion triggered
   - Why it failed
   - What was learned

2. Commit с меткой `[KILLED]`:
   ```bash
   git commit -m "test: T2 KILLED — advantage_score=0.85 < 0.8 threshold"
   ```

3. Обновить `UNIFIED_FRAMEWORK.md`:
   - Mark hypothesis as FALSIFIED
   - Update framework status

4. Опционально: написать preprint negative result  
   (если методология сильная, даже при negative outcome)

---

## Amendment Protocol

**Можно ли менять kill criteria после начала?**

**ДА, если:**
- Обнаружена техническая ошибка (баг в коде)
- Обнаружен data leakage
- Датасет оказался непригодным

**НЕТ, если:**
- Просто не нравится результат
- Хочется "ещё один шанс"
- Появилась "новая интерпретация"

**Процедура изменения:**
1. Записать в `AMENDMENTS.md` причину
2. Зафиксировать старый критерий
3. Объяснить, почему новый критерий честнее
4. Restart эксперимент с нового листа

---

## Commitment

**Я обязуюсь:**
- Следовать этим критериям
- Не передвигать goalpost
- Публиковать negative results
- Останавливаться при kill switch

**Подпись:** (автоматически timestamped commit)

**Timestamp:** 2026-04-25

---

**Приложение A: Почему это важно**

ARCHCODE и Stress Biology показали:
- Small n обманывает (n=49 → r=0.36, n=89 → r=-0.17)
- Category leakage даёт ложный сигнал (AUC 0.975 → 0.551)
- Matched controls убивают ложные claims (Router p=0.996)

Pre-registration — это не бюрократия, это **интеллектуальная честность**.
