# Extended Hypotheses — RNA/TE/G4

**Created:** 2026-04-26  
**Status:** Evaluated, not yet experimentally tested  
**Related to:** ATR Framework (topological control at different levels)

---

## Summary Table

| Domain | Hypothesis | Score | Priority | Key Test |
|--------|-----------|-------|----------|----------|
| **G4** | Раковая уязвимость через G4-клиренс | 9.0/10 | **P0** ⭐⭐⭐ | Λ-index vs drug sensitivity |
| **G4** | Топологический переключатель | 8.8/10 | **P1** ⭐⭐ | G4switch pulse-chase |
| **TE** | HUSH/TRIM28 adversarial learning | 8.4/10 | **P1** ⭐ | Co-evolution + H3K9me3 spread |
| **RNA→DNA** | Error threshold фазовый переход | 8.2/10 | **P2** | Quasispecies simulation |
| **TE** | Graph-rewriting compiler | 8.2/10 | **P2** | TE insertion → modularity |
| **G4** | Эпигенетический диод | 8.0/10 | **P2** | CRISPR G4 motif + epigenome |
| **TE** | Стресс-зависимые энхансеры | 7.8/10 | **P3** | Time-course HUSH KD |
| **RNA→DNA** | Белки как предусловие | 7.6/10 | **P3** | RNP catalytic network |
| **RNA→DNA** | Вирусное уклонение | 7.0/10 | **P3** | Agent-based RNA/DNA parasites |

---

## Domain 1: RNA → DNA Transition

### H-RNA-1: Вирусоподобная технология уклонения от RNA-defense

**Score:** 7.0/10

**Core Idea:** ДНК могла впервые появиться у вирусоподобных элементов как химически изменённый геном, менее уязвимый к RNA-targeting защите; затем была "захвачена" клетками.

**Evidence Level:**
- [ESTABLISHED] Вирусы имеют разнообразие геномов, многие кодируют RNR/TdS
- [INFERRED-MEDIUM] Направление переноса вирус↔клетка трудно доказать
- [SPECULATIVE] ДНК как "stealth genome"

**Falsification:**
```python
# Agent-based model: RNA-cell + RNA-virus + DNA-virus
# With RNA-specific defense pressure
# Kill if: DNA never wins при реалистичных metabolic costs
```

**Strengths:**
- Красивая концептуальная инверсия
- Объясняет вирусное разнообразие геномов

**Weaknesses:**
- "Вирус" до клетки — спорный термин
- Древний HGT direction очень трудно восстановить

---

### H-RNA-2: Фазовый переход через error threshold ⭐

**Score:** 8.2/10

**Core Idea:** Переход к ДНК стал фазовым переходом: когда длина полезного генома превысила error threshold РНК-репликации, ДНК получила резкий скачок допустимой сложности.

**Evidence Level:**
- [ESTABLISHED] Eigen error threshold — классика
- [ESTABLISHED] РНК химически менее стабильна
- [VERIFIED-CODE] Quasispecies model — стандартный инструмент

**Falsification:**
```python
# Quasispecies simulation: RNA vs DNA
# L_max(RNA) vs L_max(DNA) как функция μ, repair
# Kill if: переход всегда плавный, нет критического L_c
```

**Strengths:**
- Математика строгая
- Toy model тривиален (1-2 дня)
- Высокая фальсифицируемость

**Weaknesses:**
- Ранняя жизнь могла быть распределённой сетью (HGT)
- Фазовый переход может быть математическим удобством

**Best hypothesis in RNA→DNA set**

---

### H-RNA-3: Белки как предусловие ДНК через RNP-комплексы

**Score:** 7.6/10

**Core Idea:** ДНК стала возможна только после появления RNA-peptide комплексов, где пептиды взяли на себя радикальную химию синтеза dNTP (RNR-like).

**Evidence Level:**
- [ESTABLISHED] RNR и TdS — сложные белковые ферменты
- [INFERRED-MEDIUM] RNP-мир вероятен
- [SPECULATIVE] Peptide synergy для dNTP flux

**Falsification:**
```python
# Catalytic network: RNA-only vs RNA-peptide
# Measure: dNTP flux достигает threshold?
# Kill if: peptide synergy не даёт преимущества
```

**Strengths:**
- Важная перестановка причинности
- Объясняет сложность RNR/TdS

**Weaknesses:**
- Переносит проблему на "как точная трансляция"
- Параметризация сложнее

---

## Domain 2: Транспозоны и регуляторные сети

### H-TE-1: Распределённый компилятор регуляторных сетей

**Score:** 8.2/10

**Core Idea:** TE-семейство действует как геномная макрокоманда, копирующая cis-regulatory grammar в множество мест; отбор оставляет полезные копии.

**Evidence Level:**
- [ESTABLISHED] TE reshape cis-regulatory landscapes
- [ESTABLISHED] KRAB-ZFP/TRIM28 context-specific repression
- [INFERRED-HIGH] TE как graph-rewriting operator

**Falsification:**
```python
# Regulatory graph + TE insertion events
# Compare: TE-derived modularity vs random insertions
# Kill if: TE не даёт coordination выше baseline
```

**Strengths:**
- Сильная формализация (CS analogy работает)
- Хорошая симулируемость

**Weaknesses:**
- TE-derived elements могут быть passive chromatin marks
- Активные marks ≠ функция

---

### H-TE-2: HUSH/TRIM28 как adversarial learning система ⭐

**Score:** 8.4/10

**Core Idea:** Эволюционная гонка TE vs HUSH/KRAB-ZFP создаёт не только подавление, но и новые cell-type-specific regulatory switches через H3K9me3 spreading.

**Evidence Level:**
- [ESTABLISHED] TE-defense arms race documented
- [ESTABLISHED] H3K9me3 spreading известен
- [INFERRED-HIGH] Defense становится регуляторным модулем

**Falsification:**
```python
# Co-evolution model: TE families vs repressors
# H3K9me3 spreading kernel + gene expression
# Kill if: TE-repressor occupancy не улучшает tissue-specific prediction
```

**Strengths:**
- Объясняет не только подавление, но и новые контуры
- Adversarial learning аналогия сильна

**Weaknesses:**
- H3K9me3 может быть защитным следом, не функцией
- Причинность требует perturbation

**Best hypothesis in TE set**

---

### H-TE-3: Стресс-зависимые скрытые энхансеры

**Score:** 7.8/10

**Core Idea:** TE-derived elements — латентные regulatory modules, включающиеся при ослаблении HUSH/TRIM28 и переводящие клетку в interferon-high/stem-like/EMT states.

**Evidence Level:**
- [ESTABLISHED] TE expression → viral mimicry
- [INFERRED-MEDIUM] TE derepression → state switch
- [WEAK] Причинность (TE activation до или после state switch?)

**Falsification:**
```python
# Time-course HUSH/TRIM28 KD + scRNA/scATAC
# Trajectory inference: TE activation предшествует state transition?
# Kill if: TE activation всегда следует после switch
```

**Strengths:**
- Прямая клиническая релевантность (cancer immunotherapy)
- scRNA/ATAC инструменты готовы

**Weaknesses:**
- TE activation может быть следствием stress/damage
- Viral mimicry может быть побочным эффектом

---

## Domain 3: G-квадруплексы (G4)

### H-G4-1: Топологический переключатель с hysteresis ⭐⭐

**Score:** 8.8/10

**Core Idea:** G4 существуют как метастабильные топологические аттракторы, возникающие при torsional stress; удерживают транскрипционный режим после исчезновения сигнала (hysteresis).

**Evidence Level:**
- [ESTABLISHED] G4 связаны с транскрипцией, суперскручиванием
- [INFERRED-HIGH] Неравновесный топологический аттрактор
- [VERIFIED-CODE] G4switch/ATENA — готовые инструменты

**Falsification:**
```python
# Gillespie + bifurcation: σ → G4 folding → transcription
# Pulse-chase с G4switch на MYC
# Kill if: G4 не создаёт hysteresis window при realistic unfolding rates
```

**Strengths:**
- Фальсифицируемость ОЧЕНЬ высокая
- G4switch/ATENA — готовые экспериментальные инструменты
- Toy model реалистичен (2-3 дня)

**Weaknesses:**
- Hysteresis может идти от TF residence time, не G4
- Нужны temporal data

**Second-best overall**

---

### H-G4-2: Эпигенетический диод

**Score:** 8.0/10

**Core Idea:** G4 работают как directional gates: асимметрично меняют доступ DNMT/TET/histone modifiers, стабилизируя active/repressed states в зависимости от H3K27ac/me3 context.

**Evidence Level:**
- [ESTABLISHED] G4 связаны с H3K27ac/me3, looping
- [INFERRED-MEDIUM] G4 влияет на DNMT1/methylation
- [SPECULATIVE] Directional asymmetry

**Falsification:**
```python
# Bayesian/HMM: G4-state ↔ methylation ↔ histone ↔ loop
# CRISPR base-editing разрушение G4 motif + time-resolved epigenomics
# Kill if: G4-state не добавляет mutual information
```

**Strengths:**
- Красивая концептуальная инверсия
- Multi-omics integration feasible

**Weaknesses:**
- G4 может быть следствием активного хроматина
- Причинность требует perturbation + temporal data

---

### H-G4-3: Раковая уязвимость через дефицит G4-клиренса ⭐⭐⭐

**Score:** 9.0/10

**Core Idea:** Чувствительность опухоли к G4-лигандам определяется фазовым переходом: при превышении Λ = G4-load / helicase-capacity возникает лавинный replication stress.

**Evidence Level:**
- [ESTABLISHED] G4-стабилизаторы в клинических испытаниях (CX-5461)
- [ESTABLISHED] BLM/WRN/FANCJ critical для G4 resolution
- [VERIFIED-CODE] Queueing model + drug response — строго тестируемо

**Falsification:**
```python
# Λ-index = G4-load / (WRN + BLM + FANCJ + HR + TOP)
# Predict: drug sensitivity в patient cohorts
# Validate: isogenic lines ± helicase KD/OE
# Kill if: Λ не даёт прироста над MYC/dose baseline
```

**Strengths:**
- **ПРЯМОЕ КЛИНИЧЕСКОЕ ПРИЛОЖЕНИЕ**
- Данные существуют (CX-5461 trials)
- Математика строгая (queueing theory)
- Patient stratification возможна СЕЙЧАС

**Weaknesses:**
- CX-5461 имеет off-target effects (Pol I, topoisomerase)
- Нужна deconvolution G4-specific vs off-target

**BEST HYPOTHESIS OVERALL** — клинически готова, фальсифицируема, высокий impact

---

## Cross-Domain Connections

### Connection 1: Топологическая память

```
G4-1 (hysteresis) ↔ ATR-T3 (catenation memory) ↔ ATR-D3 (spatial memory)
```

Все три используют **топологические структуры** как память без изменения последовательности.

### Connection 2: Фазовые переходы

```
RNA-DNA-2 (error threshold) ↔ ATR-D2 (condensate nucleation) ↔ G4-3 (clearance overload)
```

Все описывают **критические пороги** и **нелинейные переходы**.

### Connection 3: Неравновесные алгоритмы

```
ATR-T2 (TOP2 annealing) ↔ G4-1 (nonequilibrium attractor) ↔ TE-2 (adversarial co-evolution)
```

Все требуют **ATP/energy drive** и **нарушение detailed balance**.

---

## Recommended Testing Order

### Tier 0: Clinical Ready
1. **G4-3** (раковая уязвимость) — данные существуют, можно начать ретроспективный анализ CX-5461 trials

### Tier 1: High Feasibility
2. **G4-1** (hysteresis) — G4switch/ATENA ready
3. **RNA-DNA-2** (error threshold) — quasispecies trivial
4. **TE-2** (adversarial learning) — ChIP/ATAC/RNA data available

### Tier 2: Medium Feasibility
5. **TE-1** (compiler) — нужна graph integration
6. **G4-2** (диод) — требует causal inference
7. **TE-3** (стресс) — time-course data complex

### Tier 3: Long-Term / Speculative
8. **RNA-DNA-3** (белки) — biochemical parameterization hard
9. **RNA-DNA-1** (вирус) — ancient HGT direction очень трудно

---

## Integration with ATR Framework

**Возможные расширения ATR:**

```
ATR Layer 1 (FIELD)     ← G4-1 (topological field)
ATR Layer 2 (GRAPH)     ← TE-1 (regulatory graph rewriting)
ATR Layer 3 (ALGORITHM) ← RNA-DNA-2 (error-correcting transition)
ATR Layer 4 (MEMORY)    ← G4-2 (epigenetic gate)
```

**Новый слой для ATR?**

```
LAYER 5: EVOLUTIONARY INNOVATION
  ├─ RNA→DNA transition mechanisms
  ├─ TE-driven regulatory rewiring
  └─ G4 as evolvable structural switches
```

---

## Kill Criteria (Pre-Registered)

### For Any Hypothesis

**KILL if:**
- Toy model не даёт сигнала при wide parameter sweep
- Baseline model не хуже (Occam's razor)
- Причинность не доказывается perturbation экспериментом
- Эффект исчезает при matched controls

**SUCCESS if:**
- Effect size > 0.3
- Robustness к параметрам
- Cross-validation на независимых datasets
- Perturbation experiment подтверждает причинность

---

**Version:** 0.1.0  
**Last Updated:** 2026-04-26  
**Status:** Documented, awaiting experimental validation
