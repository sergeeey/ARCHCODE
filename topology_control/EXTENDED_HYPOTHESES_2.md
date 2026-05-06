# Extended Hypotheses Set 2 — 3D-Genome, DNA Computing, Quantum Effects

**Created:** 2026-04-26  
**Status:** Evaluated (computational + theoretical)  
**Related to:** ATR Framework expansion, cross-domain integration

---

## Summary Table

| Domain | Hypothesis | Score | Priority | Key Test |
|--------|-----------|-------|----------|----------|
| **3D-Genome** | Болезнь как 3D-attractor переход | 8.76/10 | **P0** ⭐⭐⭐ | SV-induced neo-TAD prediction |
| **DNA Comp** | ДНК как реакционный сопроцессор | 8.72/10 | **P1** ⭐⭐ | CRN-logic SNR in vivo |
| **3D-Genome** | Surface-регуляция доменов | 8.69/10 | **P1** ⭐ | Surface index + expression |
| **3D-Genome** | Активный полимер near-critical | 8.63/10 | **P2** | Scaling exponent α vs cell type |
| **DNA Comp** | Граница через irreversible write | 8.62/10 | **P2** | Recombinase memory vs stateless |
| **Quantum** | Bias + selection = направленность | 8.61/10 | **P2** | Quantum-score + adaptive loci |
| **Quantum** | Туннелирование создаёт mutation bias | 8.60/10 | **P3** | DFT barriers vs real spectra |
| **DNA Comp** | ДНК как медленная reservoir-память | 8.58/10 | **P3** | Chromatin memory capacity |
| **Quantum** | Среда измеряет через decoherence | 8.50/10 | **P3** | Γ vs polymerase timescale |

---

## Domain 1: 3D-Genome Organization

### H-3D-1: Активный полимер на границе фрактального режима

**Score:** 8.63/10

**Core Idea:** Клеточно-специфичная 3D-организация генома возникает из настройки активного полимера около критического режима, где loop extrusion, compartmental segregation и chromatin state создают фракталоподобное contact scaling только на ограниченных масштабах.

**Evidence Level:**
- [ESTABLISHED] Fractal globule и loop extrusion признаны механизмами
- [ESTABLISHED] Compartmental segregation доказана
- [INFERRED-HIGH] Фрактальность как динамический режим, не архитектурный план
- [WEAK] "Near-critical" может быть параметрической подгонкой

**Falsification:**
```python
# Active polymer simulation: loop extrusion + compartments
# Measure: P(s) ~ s^(-α) scaling exponent
# Kill if: α фиксирован без extrusion (fractal — пассивное свойство)
# Kill if: α не коррелирует с cell-type-specific enhancer-promoter contacts
```

**Strengths:**
- Объединяет polymer physics + loop extrusion + compartments
- Фальсифицируемая через scaling analysis
- Может объяснить клеточную специфичность через параметры активности

**Weaknesses:**
- Hi-C averaging может создавать ложное scaling
- "Near-critical" может быть post-hoc подгонкой
- Требует single-cell Micro-C для проверки

**Cross-validation:** С ATR-T1 (supercoiling field), ATR-D1 (spectral 3D)

---

### H-3D-2: Регуляторная активность на поверхности доменов ⭐

**Score:** 8.69/10

**Core Idea:** Клеточно-специфичные гены включаются преимущественно тогда, когда их энхансеры и промоторы размещены на поверхностях TAD/subTAD-доменов; ошибки болезни часто возникают при перемещении регуляторных элементов с поверхности в ядро домена или наоборот.

**Evidence Level:**
- [ESTABLISHED] Cell-type-specific CRE enriched на domain surfaces (Springer 2025)
- [ESTABLISHED] Disease-associated non-coding variants enriched там же
- [INFERRED-MEDIUM] Surface position повышает accessibility
- [WEAK] Причинность: surface → activity или activity → surface?

**Falsification:**
```python
# Surface index S_i = 1 - d_core / d_boundary
# Model: P(gene ON) ~ f(S_i, contact, ATAC, H3K27ac)
# Kill if: S_i не добавляет прироста prediction после ATAC/Hi-C
# Kill if: CRISPR-изменение boundary не меняет expression при const sequence
```

**Strengths:**
- **НОВАЯ геометрическая переменная** в регуляции
- Прямые клинические приложения (GWAS non-coding variants)
- Multi-omics integration feasible
- Может объяснить часть "enhancer paradox"

**Weaknesses:**
- Surface может быть следствием активной транскрипции
- Требует 3D-позиционирование + perturbation эксперименты
- Micro-C разрешение может быть недостаточным

**BEST IN 3D-GENOME SET** (новая механистическая ось)

**Cross-validation:** С ATR-D1 (spectral), G4-2 (epigenetic diode)

---

### H-3D-3: Болезнь как переход в патологический 3D-attractor ⭐⭐⭐

**Score:** 8.76/10

**Core Idea:** Структурные варианты вызывают болезнь не только через одиночный enhancer hijacking, а через перевод локального хроматина в новый 3D-attractor: neo-TAD или pathological compartment state, где несколько генов одновременно получают неправильные контакты.

**Evidence Level:**
- [ESTABLISHED] SV меняют 3D-хроматин и вызывают болезни (ScienceDirect 2024)
- [ESTABLISHED] Enhancer/silencer hijacking, neo-TADs доказаны в раке
- [INFERRED-HIGH] Neo-TAD как устойчивый attractor
- [INFERRED-MEDIUM] Системный эффект на несколько генов сразу

**Falsification:**
```python
# Simulate: normal contact map + SV → loop extrusion recalculation
# Predict: dysregulated gene set
# Validate: CRISPR-engineered SV + Capture-C/RNA-seq
# Kill if: SV-эффект объясняется только copy number/gene disruption
# Kill if: predicted neo-loop не появляется in vivo
```

**Strengths:**
- **ПРЯМОЕ КЛИНИЧЕСКОЕ ПРИЛОЖЕНИЕ**
- Объясняет multi-gene dysregulation patterns
- Akita/Orca-like prediction models ready
- Меняет парадигму: от "одна поломка" к "системный переход"
- Cancer evolution + developmental disorders

**Weaknesses:**
- Tumor heterogeneity затрудняет Hi-C
- SV-эффекты могут быть пассажирами selection
- Требует isogenic validation

**BEST OVERALL IN SET 2** — клинически готова, сильная механистика

**Cross-validation:** С ATR-D2 (condensate nucleation), ATR-D3 (spatial memory)

---

## Domain 2: DNA Computing

### H-DNA-1: ДНК как реакционный сопроцессор, не CPU ⭐⭐

**Score:** 8.72/10

**Core Idea:** Универсальные ДНК-вычисления внутри клетки станут возможны только как ограниченный реакционный сопроцессор, где ДНК/РНК-цепи реализуют CRN-логику, а клетка поставляет энергию, компартменты, деградацию и считывание через белковые выходы.

**Evidence Level:**
- [ESTABLISHED] DNA strand displacement может реализовывать CRN (PNAS)
- [ESTABLISHED] Nucleic acid circuits работают в клетках млекопитающих (Science 2025)
- [INFERRED-HIGH] Теоретическая универсальность ≠ практическая масштабируемость in vivo
- [WEAK] Максимальный размер схемы in vivo неизвестен

**Falsification:**
```python
# CRN-модель: DNA/RNA strand displacement + degradation + noise + dilution
# Minimal: 3-input AND-NOT gate
# Baseline: protein logic без strand displacement
# Kill if: leakage/noise уничтожает SNR при <10 gates
# Kill if: toxicity появляется при <5 gates
```

**Strengths:**
- Реалистичная архитектурная рамка (не "ДНК-ноутбук")
- Синтетическая биология приложения
- Компартментализация как feature, не bug
- Терапевтические схемы (biosensors, controllers)

**Weaknesses:**
- Off-target hybridization может быть недооценён
- Эволюционная стабильность схем под вопросом
- Ресурсная цена для клетки

**SECOND-BEST IN SET 2** — практическая важность для synthetic biology

**Cross-validation:** С RNA→DNA transition, TE regulatory networks

---

### H-DNA-2: Граница хранения/вычисления через необратимую запись

**Score:** 8.62/10

**Core Idea:** ДНК переходит от хранения к вычислению в момент, когда молекулярное событие необратимо меняет последовательность или эпигенетическое состояние так, что будущий ответ клетки зависит от истории входов.

**Evidence Level:**
- [ESTABLISHED] DNA archival storage (Church, Goldman, DNA Fountain)
- [ESTABLISHED] Recombinase memory circuits в synthetic biology (Frontiers 2025)
- [INFERRED-HIGH] Запись события превращает геном в stateful automaton
- [INFERRED-MEDIUM] I(D_t+1; x_t | D_t) > 0 как критерий вычисления

**Falsification:**
```python
# Finite-state machine на ДНК-состояниях
# Task: "A before B" temporal logic
# Baseline: stateless promoter logic
# Kill if: stateful DNA memory не решает задачу лучше
# Kill if: error rate записи >10% делает память бесполезной
```

**Strengths:**
- Чёткий формальный критерий (mutual information)
- Применимо к cellular event recording
- Lineage tracing, history-dependent therapies
- Automata-theoretic framework

**Weaknesses:**
- Необратимость мешает reusability
- Error propagation в длинных записях
- Белки всё равно делают основную работу

**Cross-validation:** С H2 (mito-epigenetics filter), D3 (spatial memory)

---

### H-DNA-3: Клетка использует ДНК как медленную reservoir-память

**Score:** 8.58/10

**Core Idea:** В естественных клетках ДНК/хроматин выполняет не роль универсального процессора, а роль медленного reservoir-memory слоя: он хранит историю сигналов через accessibility, methylation, looping и nucleosome positioning, а быстрая обработка идёт через РНК, белки и метаболиты.

**Evidence Level:**
- [ESTABLISHED] Microbial computing обзоры подчёркивают ограничения digital logic (ScienceDirect 2025)
- [ESTABLISHED] DNA neural networks in vitro (Nature 2025)
- [INFERRED-MEDIUM] Chromatin states как reservoir для temporal задач
- [WEAK] Computational advantage хроматина над GRN не доказан

**Falsification:**
```python
# Multi-timescale GRN: RNA (fast) + chromatin (slow)
# Task: delayed stimulus response classification
# Kill if: chromatin-state variables не улучшают prediction
# Kill if: memory capacity не растёт с chromatin complexity
```

**Strengths:**
- Объясняет клеточную память без постоянных белковых петель
- Developmental biology relevance
- Reservoir computing — растущая область
- scRNA/ATAC data integration

**Weaknesses:**
- Chromatin memory может быть следствием белковых петель
- Трудно отделить от долгоживущих белков
- Требует temporal perturbation experiments

**Cross-validation:** С ATR-MEMORY слоем, H3 (nucleoid compaction)

---

## Domain 3: Quantum Effects in Mutagenesis

### H-Q-1: Туннелирование создаёт mutation bias hotspots

**Score:** 8.60/10

**Core Idea:** Протонное туннелирование не направляет эволюцию к полезным признакам, но создаёт локальные "квантово-чувствительные" мутационные горячие точки, которые затем могут усиливаться отбором, стрессом и репарацией.

**Evidence Level:**
- [ESTABLISHED] Proton transfer может создавать редкие таутомеры (ScienceDirect 2024)
- [ESTABLISHED] DFT/NEO-DFT расчёты tunneling barriers (RSC 2025)
- [INFERRED-MEDIUM] Разные локусы имеют разные quantum barriers
- [WEAK] Вклад tunneling относительно deamination/oxidative damage неизвестен

**Falsification:**
```python
# DFT: энергетические барьеры для AT/GC в разных контекстах
# WKB approximation для tunneling probability
# Baseline: классическая термальная модель
# Kill if: quantum term не улучшает prediction mutation spectra
# Kill if: repair/polymerase context объясняет всё
```

**Strengths:**
- Микрофизический механизм известен
- DFT/quantum chemistry инструменты готовы
- Может объяснить часть mutation bias
- Sequence context mapping feasible

**Weaknesses:**
- Вклад может быть биологически мал
- Требует real mutation spectra для validation
- Water/protein окружение усложняет расчёты

**Cross-validation:** С stress biology (ATP mutagenesis REJECTED), repair bias

---

### H-Q-2: Среда измеряет квантовый исход через decoherence

**Score:** 8.50/10

**Core Idea:** Клеточная среда при стрессе может ускорять decoherence и фиксацию некоторых таутомерных состояний через репликацию/транскрипцию/repair, но это создаёт mutation bias, а не истинную направленную эволюцию.

**Evidence Level:**
- [ESTABLISHED] Open quantum system models применялись к ДНК (Nature)
- [WEAK] Старые adaptive mutation модели через decoherence остаются гипотезой (ScienceDirect 1999)
- [INFERRED-LOW] Stress меняет coupling DNA ↔ environment
- [UNKNOWN] Coherence lifetime таутомеров in vivo

**Falsification:**
```python
# Open quantum model: base-pair + bath + replication window
# Measure: Γ (decoherence rate) vs stress
# Kill if: Γ всегда >> polymerase timescale (coherence irrelevant)
# Kill if: stress не меняет P_fix через Γ
```

**Strengths:**
- Красивая квантовая рамка
- Объясняет роль среды без магии
- Open quantum systems — строгая математика
- Связка stress + decoherence + fixation

**Weaknesses:**
- **LOWEST CONFIDENCE (0.55)** в наборе
- Biological decoherence может быть слишком быстрой
- Трудно проверить экспериментально in vivo
- Может быть физически красива, но биологически нерелевантна

**Cross-validation:** С stress-induced mutagenesis литературой

---

### H-Q-3: Направленность из bias + selection, не из квантов ⭐

**Score:** 8.61/10

**Core Idea:** Квантовые эффекты могут быть нижним физическим уровнем некоторых мутационных bias, но направленность адаптации возникает только на верхнем уровне: через стресс-зависимое изменение mutation rate, repair bias и селекцию.

**Evidence Level:**
- [ESTABLISHED] Mutation bias существует и силён (ResearchGate)
- [ESTABLISHED] Stress-induced mutagenesis ускоряет адаптацию (Oxford Biology)
- [INFERRED-HIGH] Quantum-sensitive positions могут совпадать с adaptive-relevant
- [INFERRED-MEDIUM] Отбор усиливает впечатление "направленности"

**Falsification:**
```python
# Популяционная модель на fitness landscape
# Mutation operators: M_classical + M_repair + M_stress + M_quantum
# Baseline: uniform random mutations
# Kill if: M_quantum не ускоряет adaptive peak достижение
# Kill if: quantum component вторичен после repair/stress учёта
```

**Strengths:**
- **Разрешает парадокс** "направленной эволюции"
- Многоуровневая архитектура (quantum → bias → selection)
- Эволюционно правдоподобна
- Высокая simulatability (9.0)
- Information theory метрики (I(Mutation; Fitness Gain))

**Weaknesses:**
- Quantum layer может быть избыточным
- Любой bias можно подогнать под результат
- Требует quantum-sensitive genome map

**BEST IN QUANTUM SET** — объединяет физику + эволюцию

**Cross-validation:** С adaptive mutation литературой, evolvability theory

---

## Cross-Domain Connections

### Connection 1: Топологическая память + DNA computing

```
ATR-T3 (catenation) ↔ H-DNA-2 (irreversible write) ↔ ATR-D3 (spatial memory)
```

Все три используют **физическую структуру** как память.

### Connection 2: Активные системы вне равновесия

```
ATR-T2 (TOP2 annealing) ↔ H-3D-1 (near-critical polymer) ↔ H-DNA-1 (CRN co-processor)
```

Все требуют **ATP/energy** и **non-equilibrium dynamics**.

### Connection 3: Mutation landscape shaping

```
H-Q-3 (bias + selection) ↔ Stress Biology (REJECTED) ↔ ATR framework (topological stress)
```

Разные уровни формирования **мутационной доступности**.

### Connection 4: Disease mechanisms

```
H-3D-3 (3D-attractor) ↔ G4-3 (clearance overload) ↔ D1 (spectral perturbation)
```

Все описывают **фазовые переходы** в патологию.

---

## Recommended Testing Order

### Tier 0: Clinical/High Impact Ready

1. **H-3D-3** (3D-attractor disease) — SV clinical data exists
2. **H-3D-2** (surface regulation) — GWAS non-coding data available

### Tier 1: High Feasibility

3. **H-DNA-1** (DNA co-processor) — CRN simulation straightforward
4. **H-Q-3** (bias + selection) — population model + mutation spectra
5. **H-3D-1** (active polymer) — scaling analysis on public Hi-C

### Tier 2: Medium Complexity

6. **H-Q-1** (tunneling hotspots) — DFT calculations feasible
7. **H-DNA-2** (write boundary) — recombinase circuit models
8. **H-DNA-3** (reservoir memory) — scRNA temporal analysis

### Tier 3: High Uncertainty

9. **H-Q-2** (decoherence) — требует quantum dynamics + biology integration

---

## Integration with ATR Framework

**Новые слои для рассмотрения:**

```
LAYER 5: EVOLUTIONARY DYNAMICS
  ├─ Quantum mutation bias (H-Q-1, H-Q-3)
  ├─ 3D-genome evolution (H-3D-3)
  └─ Computational substrates (H-DNA series)

LAYER 6: DISEASE MECHANISMS
  ├─ 3D-attractor transitions (H-3D-3)
  ├─ Surface mislocalization (H-3D-2)
  └─ Enhancer/silencer hijacking
```

**Связи с существующими слоями:**

```
ATR-FIELD    ← H-3D-1 (polymer near-critical regime)
ATR-GRAPH    ← H-3D-2 (surface as graph property)
ATR-ALGORITHM ← H-DNA-1 (CRN as biochemical algorithm)
ATR-MEMORY   ← H-DNA-2, H-DNA-3 (DNA state memory)
```

---

## Kill Criteria (Pre-Registered)

### For Any Hypothesis

**KILL if:**
- Baseline model не хуже (Occam's razor)
- Эффект исчезает при matched controls
- Параметры не имеют biological plausibility
- Toy model не даёт сигнала при wide sweep

**SUCCESS if:**
- Effect size > 0.3
- Robustness к параметрам
- Independent dataset validation
- Perturbation experiment confirms causality

---

## Top 3 Overall Recommendations

### 1. H-3D-3: Disease as 3D-Attractor (8.76/10) ⭐⭐⭐
- **Why:** Прямое клиническое приложение, SV data exists, меняет paradigm
- **Next step:** Isogenic CRISPR SV + Capture-C validation
- **Timeline:** 6-12 months pilot

### 2. H-DNA-1: DNA Co-Processor (8.72/10) ⭐⭐
- **Why:** Synthetic biology impact, CRN simulation ready, therapeutic potential
- **Next step:** Minimal 3-input circuit in mammalian cells
- **Timeline:** 3-6 months proof-of-concept

### 3. H-3D-2: Surface Regulation (8.69/10) ⭐
- **Why:** Новый механистический слой, GWAS integration, multi-omics ready
- **Next step:** Surface index + scRNA/ATAC correlation analysis
- **Timeline:** 2-4 months computational validation

---

**Version:** 0.1.0  
**Last Updated:** 2026-04-26  
**Status:** Documented, integration with ATR pending T2 results
