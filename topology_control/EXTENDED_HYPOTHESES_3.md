# Extended Hypotheses Set 3 — G4, DNA Topology, Epigenetic Inheritance

**Created:** 2026-04-26  
**Status:** Evaluated (literature-based + computational)  
**Related to:** ATR Framework Layer 5-7 expansion

---

## Summary Table

| Domain | Hypothesis | Score | Priority | Key Test |
|--------|-----------|-------|----------|----------|
| **G4** | Раковая уязвимость через G4-clearance | 8.65/10 | **P0** ⭐⭐⭐ | Λ-index vs drug response |
| **Topology** | Геном как торсионное поле | 8.56/10 | **P0** ⭐⭐ | σ-field correlation length |
| **Topology** | TopoII+SMC топологический отжиг | 8.53/10 | **P1** ⭐ | Monte Carlo strand passage |
| **G4** | G4 как 3D-якорь chromatin looping | 8.51/10 | **P1** | Graph perturbation analysis |
| **Epigenetics** | Память↔стирание фазовый переход | 8.47/10 | **P1** | ODE feedback/reprogramming |
| **G4** | G4 как hysteresis-память транскрипции | 8.47/10 | **P2** | Pulse-chase G4switch/ATENA |
| **Topology** | Катенационная перколяция | 8.35/10 | **P2** | Network percolation model |
| **Epigenetics** | Эпиметки как шумный канал | 8.28/10 | **P2** | Markov environment simulation |
| **Epigenetics** | Ламарковская как selected policy | 8.20/10 | **P3** | Policy evolution model |

---

## Domain 1: G-Quadruplexes (G4)

### H-G4-3: Раковая уязвимость через дефицит G4-клиренса ⭐⭐⭐

**Score:** 8.65/10

**Core Idea:** Чувствительность опухоли к G4-лигандам определяется критическим отношением Λ = G4-load / G4-clearance-capacity; при превышении порога возникает фазоподобный переход в replication stress, DNA damage и гибель клетки.

**Evidence Level:**
- [ESTABLISHED] G4-лиганды могут подавлять онкогены, мешать репликации (MDPI 2025)
- [ESTABLISHED] Промоторы MYC, KRAS, hTERT — G4-регулируемые (RSC 2025)
- [ESTABLISHED] Теломерные G4 + hTERT dual-target стратегия (ScienceDirect 2025)
- [INFERRED-HIGH] Опухоли с высокой G4-load и низким repair должны быть чувствительнее
- [SPECULATIVE] Критический порог Λ_c для фазового перехода

**Falsification:**
```python
# Λ-index = G4-load / (α·WRN + β·BLM + γ·FANCJ + δ·HR + ε·TOP)
# Data: G4 maps + RNA-seq + repair expression + drug response
# Baseline: dose-only, MYC-only, G4-count-only
# Kill if: Λ не лучше baseline
# Kill if: isogenic WRN+/- не сдвигает sensitivity
```

**Strengths:**
- **КЛИНИЧЕСКИ ГОТОВА** — данные существуют
- Queueing theory математически строгая
- WRN/BLM biomarkers уже используются
- Прямой patient stratification

**Weaknesses:**
- G4-лиганды имеют off-target эффекты
- Нужна деконволюция G4-specific vs off-target
- Некоторые G4 могут быть недоступны in vivo

**BEST IN G4 SET** — clinical ready, mechanism clear

**Integration with ATR:**
- Связь с ATR-ALGORITHM (active processes)
- Связь с G4-3 (уже в EXTENDED_HYPOTHESES.md)
- Новый слой: MOLECULAR STRESS THRESHOLDS

---

### H-G4-2: G4 как топологический якорь 3D-регуляции ⭐

**Score:** 8.51/10

**Core Idea:** Подмножество G4 в промоторах и энхансерах действует как топологические якоря, которые повышают вероятность enhancer-promoter looping через G4-reader белки; нарушение G4 меняет не только локальную транскрипцию, но и спектр контактного графа домена.

**Evidence Level:**
- [ESTABLISHED] ssG4-seq показал G4 в промоторах/энхансерах + SP1 как G4-reader (Nature 2025)
- [ESTABLISHED] В MuSC G4 связаны с looping, TF-binding, MAX синергия (Springer 2025)
- [INFERRED-HIGH] G4-reader стабилизирует контакт
- [INFERRED-MEDIUM] G4 perturbation меняет спектральные свойства

**Falsification:**
```python
# Contact graph G=(V,E), A_ij' = A_ij + ΔA(G4_i, Reader_i)
# Spectral perturbation: Δλ_k = λ_k(L') - λ_k(L)
# Kill if: G4-state не улучшает prediction сверх ATAC/TF/distance
# Kill if: G4 ablation не меняет modularity домена
```

**Strengths:**
- Новая геометрическая переменная в 3D-регуляции
- ssG4-seq/BG4 данные доступны
- Graph theory framework строгий
- Multi-omics integration

**Weaknesses:**
- G4 может быть маркером, не причиной
- Требует perturbation для causality
- Hi-C resolution ограничение

**Cross-validation:** С ATR-D1 (spectral 3D), H-3D-2 (surface regulation)

---

### H-G4-1: G4 как переключатель транскрипционной памяти с hysteresis

**Score:** 8.47/10

**Core Idea:** G4-структуры в промоторах и энхансерах создают hysteresis-петлю транскрипции: после краткого сигнала активации/репрессии G4 может удерживать локус в изменённом состоянии дольше, чем длится исходный сигнал.

**Evidence Level:**
- [ESTABLISHED] G4 в промоторах/энхансерах связаны с transcription activation (Nature 2025)
- [INFERRED-MEDIUM] G4 стабилизирует looping или TF residence time
- [SPECULATIVE] G4 создаёт hysteresis (зависимость от истории)
- [UNKNOWN] Lifetime G4 in vivo под действием хеликаз

**Falsification:**
```python
# Minimal model: G4 folding/unfolding + TF + looping + transcription
# State: (G_t, C_t, T_t) — G4 state, contact, output
# Memory: M = ∫(T_G4 - T_¬G4)dt после снятия сигнала
# Kill if: G4 perturbation не меняет memory window
# Cheapest test: pulse-chase G4switch/ATENA + RT-qPCR
```

**Strengths:**
- G4switch технология ready (PubMed 2025)
- Pulse-chase экспериментально доступен
- Hysteresis формализуем строго
- Связь с эпигенетической памятью

**Weaknesses:**
- G4 может быть следствием active chromatin
- TF residence time может объяснить всё
- Требует temporal data

**Cross-validation:** С ATR-MEMORY слоем, H-EPI-1 (фазовый переход памяти)

---

## Domain 2: DNA Topology & Coordination

### H-TOPO-1: Геном как торсионное поле с фазовым переходом ⭐⭐

**Score:** 8.56/10

**Core Idea:** Геном координирует топологические переходы через поле суперскручивания σ(x,t); при превышении критического отношения "генерация / релаксация" система переходит из режима локальных суперкоилов в режим длинноволновых коррелированных доменов.

**Evidence Level:**
- [ESTABLISHED] Транскрипция генерирует суперскручивание, топоизомеразы релаксируют (ScienceDirect 2024)
- [ESTABLISHED] Genome-wide supercoiling domains существуют (PubMed 2024)
- [INFERRED-HIGH] Напряжение распространяется дальше одного гена
- [SPECULATIVE] Критический режим создаёт genome-scale topological phase

**Falsification:**
```python
# PDE: ∂σ/∂t = D∇²σ + S_Pol - R_Topo - λσ
# Correlation length: ξ_σ = ∫⟨σ(x)σ(x+r)⟩dr
# Kill if: ξ_σ не растёт резко при изменении S/R ratio
# Kill if: σ-field не улучшает prediction экспрессии
```

**Strengths:**
- Объединяет транскрипцию + топологию + 3D
- PDE framework строгий
- Supercoiling domains уже измерены
- Может объяснить дальнодействующую координацию

**Weaknesses:**
- Может быть переименованием known supercoiling biology
- Трудно измерить σ(x,t) in vivo напрямую
- Требует validation через topo inhibitors

**BEST IN TOPOLOGY SET** — сильная формализация, данные существуют

**Integration with ATR:**
- Прямая связь с ATR-T1 (supercoiling field)
- Расширение на genome-wide масштаб
- FIELD layer ATR framework

---

### H-TOPO-2: TopoII + cohesin как неравновесный топологический отжиг ⭐

**Score:** 8.53/10

**Core Idea:** Клетка распутывает геном через совместный алгоритм: cohesin/condensin концентрируют топологически важные пересечения, а TopoII выполняет ATP-driven biased strand passage, снижая глобальную сложность узлов и катенанов ниже равновесного уровня.

**Evidence Level:**
- [ESTABLISHED] Type II topo снижают узлы/катенаны ниже equilibrium (Science 1997, PMC)
- [ESTABLISHED] Loop extrusion ключевой механизм организации (ScienceDirect 2025)
- [INFERRED-HIGH] SMC подводят crossings к TopoII-friendly состояниям
- [SPECULATIVE] TopoII+SMC = biological topological annealing

**Falsification:**
```python
# Topological complexity: C(G) = αK + βC + γΣ|Lk| + δΣ|σ|
# Ring polymer + SMC extrusion + TopoII passage events
# Kill if: локальные biased rules не дают global simplification
# Kill if: geometry-only объясняет всё (TopoII+SMC не нужны)
```

**Strengths:**
- Элегантная концепция (локальное → глобальное)
- Simulated annealing аналогия сильна
- Polymer simulation feasible
- Прямая связь с ATR-T2

**Weaknesses:**
- TopoII bias может быть простой геометрией
- Требует knot detection (pyknotid/Topoly)
- Toy model может не отражать in vivo

**SECOND-BEST IN TOPOLOGY** — красивая механистика

**Integration with ATR:**
- ЭТО И ЕСТЬ ATR-T2! Прямое совпадение
- Validation ATR-T2 = validation H-TOPO-2

---

### H-TOPO-3: Катенационная перколяция как фазовый переход

**Score:** 8.35/10

**Core Idea:** При снижении TopoII активности или росте loop density хроматин может переходить через порог катенационной перколяции: от независимых сцеплений к гигантской топологически связанной компоненте.

**Evidence Level:**
- [ESTABLISHED] Топологические проблемы включают катенаны (PMC 2025)
- [ESTABLISHED] Type II topo подавляют catenanes (Science 1997)
- [INFERRED-MEDIUM] Граф катенации может иметь percolation threshold
- [WEAK] Хроматиновые петли не идеальные замкнутые кольца

**Falsification:**
```python
# Catenane graph: A_ij = 1 if domains i,j catenated
# Giant component size: S = max|C_k| / N
# Kill if: S всегда растёт линейно, без порога
# Kill if: polymer simulation с realistic loops не даёт percolation
```

**Strengths:**
- Новая концепция (topological gel)
- Percolation theory строгая
- NetworkX implementation trivial
- Может объяснить segregation errors

**Weaknesses:**
- **HIGHEST HALLUCINATION RISK (5.0)** в наборе
- Петли не идеальные кольца
- Может быть ложным переносом из ring polymers
- Требует доказательства catenation graph существует

**Cross-validation:** С ATR-T3 (catenation memory) — проверить связь

---

## Domain 3: Epigenetic Inheritance

### H-EPI-1: Граница памяти/стирания как фазовый переход ⭐

**Score:** 8.47/10

**Core Idea:** Стабильность эпиметки определяется фазовым переходом между режимом памяти и стирания: если сила self-sustaining feedback DNMT/H3K9me3/sRNA превышает порог репрограммирования, метка переживает поколение.

**Evidence Level:**
- [ESTABLISHED] PGC проходят масштабное methylation erasure (Cambridge 2024)
- [ESTABLISHED] H3K9me3 участвует в восстановлении DNA methylation (Nature Comm 2025)
- [INFERRED-HIGH] H3K9me3 как промежуточный слой памяти
- [SPECULATIVE] Критический параметр λ_c отделяет наследуемые от нестабильных

**Falsification:**
```python
# Two-layer network: methylation ↔ histone ↔ smallRNA
# m_t+1 = σ(a·m_t + b·h_t + c·r_t - η·R_t)
# Order parameter: Φ = lim(m_T + h_T)/(m_0 + h_0)
# Kill if: устойчивость всегда плавная, без порога
# Kill if: single-locus data показывают экспоненциальное затухание
```

**Strengths:**
- Объясняет почему некоторые метки проходят reprogramming
- H3K9me3 данные сильные (Nature Comm 2025)
- ODE model simple
- Фазовый переход строго формализуем

**Weaknesses:**
- "Фазовый переход" может быть украшением
- Ограничено imprinted loci?
- Требует perturbation validation

**BEST IN EPIGENETICS SET** — mechanism clear, evidence strong

**Cross-validation:** С G4-1 (hysteresis memory), ATR-MEMORY layer

---

### H-EPI-2: Эпиметки как шумный канал предсказания среды

**Score:** 8.28/10

**Core Idea:** Эпигенетическое наследование становится адаптивным только когда взаимная информация I(E_parent; E_offspring) > C_mislead; иначе эпиметки остаются шумом.

**Evidence Level:**
- [ESTABLISHED] Эпимутации могут быть нейтральными/вредными/адаптивными
- [INFERRED-MEDIUM] sRNA inheritance стратегии specialist/generalist (ScienceDirect 2025)
- [INFERRED-MEDIUM] Адаптивность зависит от предсказуемости среды
- [WEAK] Для большинства систем I(E_p;E_o) неизвестна

**Falsification:**
```python
# Fitness: W = W_0 + α·1(M=E_o) - β·1(M≠E_o) - γC_M
# Adaptive if: E[W|M] > E[W|∅] AND I(M;E_o) > 0
# Kill if: наследуемые метки не повышают fitness в predictable env
# Kill if: это просто bet-hedging, не направленная адаптация
```

**Strengths:**
- Строгий information-theoretic критерий
- Разделяет adaptive vs noise
- Simulation straightforward
- Объясняет когда TEI выгодно

**Weaknesses:**
- Может быть bet-hedging под другим именем
- Требует long-term fitness measurements
- Environmental predictability трудно измерить

**Cross-validation:** С evolutionary theory of plasticity

---

### H-EPI-3: "Ламарковская" адаптация как отобранный алгоритм

**Score:** 8.20/10

**Core Idea:** "Ламарковская" адаптация — это дарвиновски отобранный алгоритм наследуемой пластичности: геном кодирует правила записи environmental signals в sRNA/marks, а отбор сохраняет только те правила, которые статистически повышают fitness.

**Evidence Level:**
- [ESTABLISHED] sRNA inheritance распространено, но adaptive роль спорна (ScienceDirect 2025)
- [ESTABLISHED] Сперматозоид передаёт chromatin/methylation/ncRNA (Nature 2023)
- [INFERRED-MEDIUM] Отбор на механизм записи/стирания
- [WEAK] Policy π(M|E) редко доказана как adaptive

**Falsification:**
```python
# Policy: π_θ(M|E_p)
# Fitness: J(θ) = E[W(M,E_o)]
# Evolution: θ_t+1 = θ_t + η∇J
# Kill if: policy не даёт gain над random/genetic baseline
# Kill if: после исключения genetics/maternal/microbiome эффект исчезает
```

**Strengths:**
- Примиряет "ламарковское" с дарвиновским
- Policy learning framework строгий
- Simulation feasible
- Объясняет направленность без магии

**Weaknesses:**
- Может быть переименованием adaptive plasticity
- Требует исключения всех confounders
- Evidence strength lowest (7.4)

**Cross-validation:** С reinforcement learning theory, bet-hedging

---

## Cross-Domain Connections

### Connection 1: Метастабильные структурные состояния

```
G4-1 (hysteresis) ↔ H-EPI-1 (memory/erasure) ↔ H-TOPO-1 (σ-field domains)
```

Все три используют **структурные метастабильные состояния** как информационный слой.

### Connection 2: Фазовые переходы и пороги

```
G4-3 (Λ > Λ_c) ↔ H-TOPO-3 (percolation) ↔ H-EPI-1 (feedback threshold)
```

Все описывают **резкие переходы** при превышении критического параметра.

### Connection 3: Топологическая сложность

```
H-TOPO-2 (C(G) simplification) ↔ H-TOPO-3 (catenane graph) ↔ ATR-T2/T3
```

Все работают с **топологическими инвариантами** (узлы, катенаны, linking).

### Connection 4: Адаптация через структуру

```
H-EPI-2 (channel) ↔ H-EPI-3 (policy) ↔ G4-3 (cancer vulnerability)
```

Все описывают **адаптивное использование** структурной информации.

---

## Integration with ATR Framework

**Новые слои:**

```
LAYER 5: EPIGENETIC MEMORY
  ├─ G4 hysteresis (H-G4-1)
  ├─ Chromatin memory phase transition (H-EPI-1)
  └─ Heritable plasticity (H-EPI-2, H-EPI-3)

LAYER 6: TOPOLOGICAL COORDINATION
  ├─ Torsional field (H-TOPO-1) ← ATR-T1 extension
  ├─ Active simplification (H-TOPO-2) ← ATR-T2 validation
  └─ Catenane gel (H-TOPO-3) ← ATR-T3 extension

LAYER 7: MOLECULAR STRESS THRESHOLDS
  ├─ G4-clearance overload (G4-3) ⭐⭐⭐
  ├─ Topological catastrophe (H-TOPO-3)
  └─ Replication stress (связь с Stress Biology REJECTED)
```

**Связи с существующими гипотезами:**

```
H-TOPO-2 = ATR-T2 (DIRECT MATCH — validation of same hypothesis)
H-TOPO-1 ↔ ATR-T1 (expansion to genome-wide scale)
H-TOPO-3 ↔ ATR-T3 (catenation memory ← percolation gel)
H-G4-3 ↔ G4-3 from EXTENDED_HYPOTHESES.md (same, duplicate)
H-G4-2 ↔ H-3D-2 (surface regulation) — both geometric addressing
H-EPI-1 ↔ ATR-MEMORY layer
```

---

## Recommended Testing Order

### Tier 0: Clinical Ready / ATR Validation

1. **H-TOPO-2** (TopoII+SMC annealing) — **THIS IS T2 EXPERIMENT RUNNING NOW** ✅
2. **G4-3** (cancer clearance) — clinical data exists, roadmap ready

### Tier 1: Strong Evidence, High Feasibility

3. **H-TOPO-1** (torsional field) — supercoiling domains measured, PDE straightforward
4. **H-G4-2** (3D-anchor) — ssG4-seq data available, graph analysis ready
5. **H-EPI-1** (memory phase) — H3K9me3 data strong, ODE model simple

### Tier 2: Medium Complexity

6. **H-G4-1** (hysteresis) — G4switch ready, but temporal data needed
7. **H-EPI-2** (channel) — simulation easy, empirical test hard
8. **H-EPI-3** (policy) — elegant framework, evidence weakest

### Tier 3: High Risk / Speculative

9. **H-TOPO-3** (percolation) — beautiful idea, but loops ≠ rings concern

---

## Kill Criteria (Pre-Registered)

### Global

**KILL hypothesis if:**
- Baseline model не хуже (Occam's razor)
- Effect disappears at matched controls
- Toy model не даёт сигнала при wide parameter sweep
- Parameters biologically implausible

**SUCCESS if:**
- Effect size > 0.3
- Robustness к параметрам
- Independent dataset validation
- Perturbation experiment confirms

### Domain-Specific

**G4 hypotheses:**
- Kill if G4 не добавляет prediction power сверх accessibility/TF
- Kill if G4-ligand effects объясняются off-target

**Topology hypotheses:**
- Kill if σ-field не коррелирует с expression/contacts
- Kill if TopoII bias = simple geometry (no "algorithm")
- Kill if percolation не появляется при realistic loop model

**Epigenetics hypotheses:**
- Kill if phase transition = mathematical artifact
- Kill if I(E_p;E_o) не повышает fitness
- Kill if policy не лучше genetic-only baseline

---

## Top 3 Overall from Set 3

### 1. G4-3: Cancer Clearance Vulnerability (8.65/10) ⭐⭐⭐
- **Why:** Clinical ready, queueing theory строгая, patient stratification
- **Action:** Already in G4_CLEARANCE_ROADMAP.md
- **Timeline:** Start Week 1 computational validation

### 2. H-TOPO-1: Genome as Torsional Field (8.56/10) ⭐⭐
- **Why:** Genome-wide data exists, PDE framework strong, ATR-T1 expansion
- **Action:** Begin after T2 results (if SUCCESS or KILL)
- **Timeline:** 2-3 weeks PDE simulation

### 3. H-TOPO-2: TopoII+SMC Annealing (8.53/10) ⭐
- **Why:** **THIS IS T2 RUNNING NOW** — direct validation
- **Action:** Awaiting results (~25 min remaining)
- **Decision:** If SUCCESS → proceed D1; if KILL → analyze failure mode

---

## Sources Integration

All hypotheses include literature citations:

**G4:**
- RSC Publishing 2025 (G4 state-of-art)
- Nature 2025 (ssG4-seq)
- Springer 2025 (MuSC G4)
- MDPI 2025 (G4 ligands cancer)
- Nature 2025 (ATENA)
- PubMed 2025 (G4switch)
- ScienceDirect 2025 (telomere targeting)

**Topology:**
- ScienceDirect 2024 (topological epigenetics)
- PubMed 2024 (supercoiling domains)
- PMC (TopoII simplification below equilibrium)
- ScienceDirect 2025 (cohesin physics)
- Science 1997 (TopoII equilibrium)
- PMC 2025 (DNA topology coordinator)

**Epigenetics:**
- Cambridge 2024 (PGC reprogramming)
- Tel Aviv University (Przibram experiments)
- ScienceDirect (intergenerational vs transgenerational)
- PubMed 2023 (Lamarckian terminology)
- ScienceDirect 2025 (sRNA inheritance)
- Nature Comm 2025 (H3K9me3 germline editing)
- Nature 2023 (sperm epigenome)

---

**Version:** 0.1.0  
**Last Updated:** 2026-04-26  
**Status:** Documented, awaiting T2 results for priority decision
