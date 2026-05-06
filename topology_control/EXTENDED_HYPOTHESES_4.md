# Extended Hypotheses — Extrachromosomal DNA (ecDNA)

**Created:** 2026-04-26  
**Status:** Evaluated, not yet experimentally tested  
**Related to:** ATR Framework (topological control), EXTENDED_HYPOTHESES_3.md (topology layer)

---

## Summary Table

| Domain | Hypothesis | Score | Priority | Key Test |
|--------|-----------|-------|----------|----------|
| **ecDNA** | Percolation phase transition | 8.71/10 | **P0** ⭐⭐⭐ | P_∞(N) vs N in single cells |
| **ecDNA** | Topological variational principle | 8.43/10 | **P1** ⭐⭐ | Lk distribution vs cGAS-STING |
| **ecDNA** | Bifurcation resistance | 8.43/10 | **P1** ⭐⭐ | Hysteresis loop in drug pulse |
| **ecDNA** | Reservoir computing hubs | 8.33/10 | **P1** ⭐ | Echo state network test |
| **ecDNA** | Spectral gap autonomy | 8.26/10 | **P2** | λ₂ vs oncogene expression |
| **ecDNA** | Bet-hedging inheritance | 8.02/10 | **P2** | Pólya urn fit to lineage |
| **ecDNA** | RD-wave amplification | 8.02/10 | **P2** | Fisher-KPP traveling front |

---

## Domain: ecDNA Topological Clustering

### H-ECD-1: Percolation Phase Transition in ecDNA Clustering ⭐⭐⭐

**Score:** 8.71/10

**Core Idea:** При превышении критического числа ecDNA копий (N > N_c) возникает фазовый переход: отдельные ecDNA элементы формируют гигантский кластер ("hub"), резко меняющий доступность генов и транскрипционный output.

**Mathematical Formulation:**

Order parameter:
```
P_∞(N) = lim_{t→∞} P(ecDNA ∈ giant_cluster | N copies)

P_∞(N) ≈ 0           при N < N_c
P_∞(N) ≈ (N - N_c)/N при N > N_c
```

Critical exponent β:
```
P_∞(N) ~ (N - N_c)^β  при N → N_c⁺
```

**Evidence Level:**

- [ESTABLISHED] ecDNA hubs наблюдаются экспериментально (Morton 2024, Nature)
- [ESTABLISHED] Percolation theory — классическая теория фазовых переходов
- [INFERRED-HIGH] Giant cluster появляется резко при критической плотности
- [SPECULATIVE] β-exponent для ecDNA clustering

**Falsification:**

```python
# Single-cell imaging: count ecDNA + measure hub membership
# Plot P_∞(N) = fraction in largest cluster vs N
# Fit: piecewise linear (N_c, slope_after)
# Kill if: transition gradual (R² < 0.7 for two-regime fit)
# Kill if: N_c varies >3× across replicates (no universal threshold)
```

**Minimal Test:**

1. Single-cell FISH: track ecDNA copy number N per cell (n=200 cells)
2. Cluster analysis: largest connected component size
3. Plot P_∞(N), fit percolation model
4. Predict: N_c = 20-50 copies, β ≈ 0.4-0.6 (mean-field percolation)

**Evaluation:**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 9.0 | Percolation для ecDNA впервые |
| Rigor | 9.0 | Order parameter строго определён |
| Falsifiability | 9.5 | Критический N_c измеряем |
| Feasibility | 8.0 | Single-cell FISH доступно |
| Simplicity | 8.5 | Классическая percolation theory |
| Impact | 9.0 | Объясняет hub formation |
| Integration | 8.5 | Связь с ATR-T3 (catenation) |
| Mechanism | 8.5 | Phase transition чёткий |
| Scope | 8.0 | Все ecDNA+ раки |
| Predictions | 9.0 | N_c, β-exponent |

**Discovery Score:** 8.71/10

**Strengths:**

- Строгая математика (percolation — solved problem)
- Экспериментально тестируемо (single-cell microscopy)
- Объясняет резкость перехода к hub phenotype
- Универсальный N_c для разных раков

**Weaknesses:**

- Hub formation может быть от активной кластеризации (моторные белки), не passive percolation
- N_c может зависеть от ядерного объёма, типа ecDNA
- 3D clustering сложнее 2D/3D lattice percolation

**Best hypothesis in ecDNA set**

---

### H-ECD-2: Spectral Gap of Hi-C Graph as Autonomy Invariant

**Score:** 8.26/10

**Core Idea:** Автономность ecDNA (устойчивая транскрипция независимо от хроматинового контекста) кодируется в спектральном разрыве λ₂ Hi-C графа: высокий λ₂ = сильная связность внутри ecDNA, слабая с хромосомами.

**Mathematical Formulation:**

Laplacian spectrum:
```
L = D - A  (D = degree matrix, A = adjacency from Hi-C)
0 = λ₁ ≤ λ₂ ≤ ... ≤ λ_n

Spectral gap: Δλ = λ₂ - λ₁ = λ₂  (для связного графа λ₁=0)
```

Hypothesis:
```
λ₂(ecDNA hub) >> λ₂(chr control)
→ high algebraic connectivity = autonomous module
```

**Evidence Level:**

- [ESTABLISHED] Hi-C detects ecDNA hubs (Morton 2024)
- [ESTABLISHED] Spectral graph theory — standard tool
- [INFERRED-MEDIUM] λ₂ коррелирует с modularity
- [WEAK] λ₂ предсказывает экспрессию онкогенов

**Falsification:**

```python
# Hi-C data: build graph (nodes = bins, edges = contacts)
# Compute Laplacian spectrum, extract λ₂
# Compare: ecDNA hubs vs chromosome TADs
# Regression: λ₂ vs oncogene expression (MYC, EGFR)
# Kill if: λ₂(ecDNA) ≤ λ₂(chr) + 2σ
# Kill if: R²(λ₂ → expression) < 0.4
```

**Minimal Test:**

1. Hi-C в ecDNA+ клетках (n=10 samples)
2. Выделить ecDNA hub subgraph
3. λ₂ для hub vs TAD control
4. Predict: λ₂(hub) ≈ 2-5× выше

**Evaluation:**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 9.0 | Spectral gap для ecDNA впервые |
| Rigor | 8.5 | Laplacian defined строго |
| Falsifiability | 8.5 | λ₂ measurable |
| Feasibility | 7.5 | Hi-C дорого |
| Simplicity | 7.5 | Spectral theory не тривиальна |
| Impact | 8.0 | Предсказывает автономность |
| Integration | 8.5 | Связь с ATR-D3 (graph layer) |
| Mechanism | 8.0 | Algebraic connectivity → autonomy |
| Scope | 8.0 | ecDNA+ cancers |
| Predictions | 8.5 | λ₂ threshold |

**Discovery Score:** 8.26/10

**Strengths:**

- Количественный invariant (λ₂)
- Связь с модульностью (Fiedler vector)
- Hi-C data доступны

**Weaknesses:**

- λ₂ чувствителен к resolution (bin size)
- Autonomy может быть от копийности, не топологии
- Hi-C artefacts (ligation bias)

---

### H-ECD-3: Topological Variational Principle — Lk Balances Transcription vs Immunity

**Score:** 8.43/10

**Core Idea:** ecDNA оптимизирует linking number (Lk) как компромисс: отрицательное суперскручивание активирует транскрипцию, но слишком сильное → разрывы → cGAS-STING → immune clearance.

**Mathematical Formulation:**

Free energy:
```
F(Lk) = E_transcription(Lk) + E_mechanical(Lk) + E_immune(Lk)

E_transcription ~ -α·Lk  (negative Lk favors unwinding)
E_mechanical ~ β·(Lk - Lk₀)²  (torsional strain)
E_immune ~ γ·Θ(|Lk| - Lk_crit)  (threshold for cGAS activation)

Optimal: dF/dLk = 0 → Lk* balances expression vs detection
```

**Evidence Level:**

- [ESTABLISHED] Negative supercoiling активирует транскрипцию
- [ESTABLISHED] ecDNA вызывает cGAS-STING (Møller 2024)
- [INFERRED-MEDIUM] Lk влияет на cGAS detection
- [SPECULATIVE] Variational principle для Lk

**Falsification:**

```python
# Measure Lk distribution in ecDNA via psoralen crosslinking + 2D gel
# Correlate: Lk vs oncogene expression vs cGAS activation
# Test: artificially increase |Lk| via gyrase → immune response ↑?
# Kill if: Lk distribution random, no peak at predicted Lk*
# Kill if: cGAS activation не коррелирует с |Lk|
```

**Minimal Test:**

1. ecDNA purification + Lk measurement (n=50 molecules)
2. Plot Lk distribution
3. Predict: peak at Lk* = -0.03 to -0.05 (σ ~ -0.03)
4. Perturbation: gyrase treatment → shift Lk → measure cGAS

**Evaluation:**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 9.0 | Lk optimization принцип новый |
| Rigor | 8.5 | Variational формализм строгий |
| Falsifiability | 8.5 | Lk measurable |
| Feasibility | 7.5 | Lk measurement трудоёмко |
| Simplicity | 8.0 | Three-term energy понятна |
| Impact | 9.0 | Объясняет immune evasion |
| Integration | 9.0 | Прямая связь с ATR-T1 (torsion) |
| Mechanism | 8.5 | Trade-off explicit |
| Scope | 8.0 | ecDNA+ cancers |
| Predictions | 8.5 | Lk*, gyrase effect |

**Discovery Score:** 8.43/10

**Strengths:**

- Строгий variational принцип
- Объясняет immune evasion puzzle
- Perturbation experiment feasible (gyrase/topotecan)
- Прямая связь с ATR-T1

**Weaknesses:**

- Lk measurement сложна (2D gel + crosslinking)
- cGAS может реагировать на dsDNA breaks, не Lk
- E_immune threshold неизвестен

---

## Domain: ecDNA Amplification Dynamics

### H-ECD-4: Reversible Drug Resistance as Bifurcation with Hysteresis ⭐⭐

**Score:** 8.43/10

**Core Idea:** Быстрая обратимая устойчивость к таргетной терапии — не мутации, а бифуркация в двухъямном потенциале числа ecDNA копий n. Hysteresis объясняет, почему для возврата нужна длительная drug holiday.

**Mathematical Formulation:**

Double-well potential:
```
V(n; λ) = -αn² + βn⁴ + λn  (λ = drug selection pressure)

dn/dt = -dV/dn + noise

Stable states: dV/dn = 0 → n_low(λ), n_high(λ)
```

Hysteresis loop:
```
λ_on  < λ_off  (bifurcation points не совпадают)
→ switching asymmetry
```

**Evidence Level:**

- [ESTABLISHED] ecDNA copy number меняется быстро (Chapman 2023)
- [ESTABLISHED] Reversible resistance documented
- [INFERRED-HIGH] Bistability в n
- [SPECULATIVE] Hysteresis loop

**Falsification:**

```python
# Drug pulse experiment: on/off cycles
# Measure n(t) in single-cell time-course
# Fit: V(n; λ) double-well model
# Measure: λ_on vs λ_off (hysteresis width)
# Kill if: switching symmetric (λ_on ≈ λ_off ± 10%)
# Kill if: time to switch не зависит от history
```

**Minimal Test:**

1. EGFR-inhibitor pulse (n=100 cells, live imaging)
2. Track ecDNA-EGFR copy number via FISH
3. Measure λ_on (drug → high n) vs λ_off (drug removal → low n)
4. Predict: λ_off < λ_on (hysteresis Δλ ≈ 20-40%)

**Evaluation:**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 8.5 | Hysteresis для ecDNA впервые |
| Rigor | 9.0 | Bifurcation theory строгая |
| Falsifiability | 9.0 | λ_on, λ_off measurable |
| Feasibility | 8.5 | Drug pulse experiments routine |
| Simplicity | 8.5 | Double-well potential standard |
| Impact | 8.5 | Clinical (dosing schedule) |
| Integration | 8.0 | Связь с ATR-D2 (memory) |
| Mechanism | 8.5 | Bistability explicit |
| Scope | 8.0 | ecDNA-driven resistance |
| Predictions | 8.5 | Hysteresis width |

**Discovery Score:** 8.43/10

**Strengths:**

- Клинически важно (resistance management)
- Drug pulse протоколы стандартны
- Предсказывает оптимальные drug holidays
- Прямая связь с ATR-D2 (memory layer)

**Weaknesses:**

- n может быть indirect readout (clonal selection)
- Noise может маскировать hysteresis
- Model fitting требует temporal resolution

---

### H-ECD-5: Asymmetric Inheritance as Optimal Bet-Hedging

**Score:** 8.02/10

**Core Idea:** Неравное распределение ecDNA при делении — не шум, а оптимальная bet-hedging стратегия: параметр асимметрии σ эволюционирует для максимизации survival вероятности популяции при флуктуирующем drug давлении.

**Mathematical Formulation:**

Pólya urn model:
```
Распределение после деления:
n_daughter1 ~ Binomial(n_mother, 0.5 + σ)
n_daughter2 = n_mother - n_daughter1

σ = asymmetry parameter (0 = random, σ>0 = biased)
```

Fitness landscape:
```
W(σ | drug_schedule) = E[survival_prob]

Optimal σ* зависит от variance drug schedule
```

**Evidence Level:**

- [ESTABLISHED] Asymmetric ecDNA inheritance (Lange 2022)
- [ESTABLISHED] Bet-hedging theory — эволюционная биология
- [INFERRED-MEDIUM] σ адаптивен
- [WEAK] σ оптимизирован под drug variance

**Falsification:**

```python
# Lineage tracing: measure σ distribution
# Simulate: Pólya urn with drug cycles
# Optimize: σ* for max survival
# Compare: observed σ vs predicted σ*
# Kill if: observed σ случаен (SD(σ) > 0.2)
# Kill if: |observed - σ*| > 3 SD
```

**Minimal Test:**

1. Single-cell lineage tracing (n=50 divisions)
2. Fit Pólya urn → extract σ per cell line
3. Simulate drug schedules → calculate σ*
4. Predict: σ* ≈ 0.1-0.2 для clinical dosing

**Evaluation:**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 8.0 | Bet-hedging для ecDNA новый угол |
| Rigor | 8.0 | Pólya urn standard model |
| Falsifiability | 8.0 | σ measurable |
| Feasibility | 7.5 | Lineage tracing трудоёмко |
| Simplicity | 8.5 | Model простой |
| Impact | 7.5 | Объясняет inheritance variance |
| Integration | 7.5 | Weak link to ATR |
| Mechanism | 8.0 | Evolutionary optimization |
| Scope | 8.0 | ecDNA+ tumors |
| Predictions | 8.5 | σ* depends on drug schedule |

**Discovery Score:** 8.02/10

**Strengths:**

- Эволюционная логика строгая
- Объясняет non-random segregation
- Lineage tracing становится routine

**Weaknesses:**

- σ может быть побочный эффект (motor proteins)
- Optimal σ* зависит от многих параметров (fitness landscape complex)
- Трудно доказать optimization (adaptationist fallacy)

---

### H-ECD-6: ecDNA Hubs as Reservoir Computers ⭐

**Score:** 8.33/10

**Core Idea:** ecDNA hub — не просто хранилище генов, а вычислительная структура типа Reservoir Computer: нелинейная динамика внутри hub обрабатывает сигналы (stress, drugs), output = транскрипционный ответ.

**Mathematical Formulation:**

Echo State Network:
```
x(t+1) = tanh(W_res·x(t) + W_in·u(t))  (reservoir dynamics)
y(t) = W_out·x(t)                       (readout layer)

x = hidden state (ecDNA cluster config)
u = input (drug, stress signals)
y = output (gene expression)
```

Reservoir property:
```
Echo State Property: ||x(t)|| bounded, fading memory
→ rich transient dynamics без training W_res
```

**Evidence Level:**

- [ESTABLISHED] ecDNA hubs имеют сложную 3D структуру
- [ESTABLISHED] Reservoir computing — proven computational paradigm
- [INFERRED-MEDIUM] Hub dynamics нелинейная
- [SPECULATIVE] Readout layer W_out trainable

**Falsification:**

```python
# Stimulus-response experiment: drug pulse → expression time-course
# Fit: ESN model with random W_res, train W_out only
# Test: Echo State Property (memory kernel decay)
# Benchmark: ESN vs linear model vs random network
# Kill if: ESN accuracy ≤ linear model
# Kill if: memory kernel не экспоненциальный (no fading memory)
```

**Minimal Test:**

1. Drug pulse experiment: 10 doses × 5 time points (n=50 conditions)
2. Measure: gene expression (y), cluster config (proxy for x)
3. Fit ESN, train W_out
4. Test: predict held-out drug response
5. Predict: ESN R² > 0.6, linear R² < 0.4

**Evaluation:**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 9.5 | Reservoir computing для ecDNA совершенно новый |
| Rigor | 8.0 | ESN математика строгая |
| Falsifiability | 8.5 | Benchmark vs linear testable |
| Feasibility | 7.5 | Stimulus-response data complex |
| Simplicity | 7.0 | ESN не тривиален |
| Impact | 9.0 | Вычислительная парадигма меняет взгляд |
| Integration | 8.5 | Связь с ATR-D4 (algorithmic memory) |
| Mechanism | 8.5 | Reservoir dynamics explicit |
| Scope | 8.0 | ecDNA hubs |
| Predictions | 8.5 | Memory kernel, ESN accuracy |

**Discovery Score:** 8.33/10

**Strengths:**

- Радикально новая парадигма (computation, not storage)
- ESN testing стандартен (machine learning)
- Объясняет non-monotonic dose-response
- Прямая связь с ATR-D4 (algorithmic layer)

**Weaknesses:**

- Echo State Property может не держаться (chaotic dynamics)
- W_out training требует много measurements
- Трудно измерить x(t) напрямую (cluster config)

---

### H-ECD-7: Fast Amplification as Reaction-Diffusion Wave

**Score:** 8.02/10

**Core Idea:** Быстрая амплификация ecDNA копий — не просто удвоение, а autocatalytic replication front (Fisher-KPP wave), распространяющийся по ядру и создающий "invasion" pattern.

**Mathematical Formulation:**

Fisher-KPP equation:
```
∂n/∂t = D·∇²n + r·n·(1 - n/K)

n = ecDNA copy density
D = diffusion coefficient
r = replication rate
K = carrying capacity

Traveling wave solution:
n(x,t) = f(x - v·t)  with speed v = 2√(D·r)
```

**Evidence Level:**

- [ESTABLISHED] ecDNA amplification быстрая (days)
- [ESTABLISHED] Fisher-KPP — классическая RD модель
- [INFERRED-MEDIUM] Autocatalytic replication (hub seeding)
- [WEAK] Spatial wave pattern

**Falsification:**

```python
# Live imaging: ecDNA-FISH time-lapse (n=20 cells, 48h)
# Measure: n(x,t) spatial density map
# Fit: traveling wave model → extract v, D, r
# Test: v ≈ 2√(D·r) (Fisher-KPP prediction)
# Kill if: no traveling front (random nucleation)
# Kill if: v vs √(D·r) correlation R² < 0.5
```

**Minimal Test:**

1. Time-lapse FISH: ecDNA count per 1μm³ voxel (3D+time)
2. Plot n(x,t) heatmap
3. Fit Fisher-KPP, extract v
4. Predict: v ≈ 0.5-2 μm/hour

**Evaluation:**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 8.5 | RD wave для ecDNA впервые |
| Rigor | 8.5 | Fisher-KPP строгая |
| Falsifiability | 8.0 | Wave speed measurable |
| Feasibility | 7.0 | 3D+time imaging тяжело |
| Simplicity | 8.0 | Fisher-KPP standard |
| Impact | 7.5 | Объясняет amplification speed |
| Integration | 8.0 | Связь с ATR-T2 (replication dynamics) |
| Mechanism | 8.0 | Autocatalytic clear |
| Scope | 8.0 | Fast amplifiers |
| Predictions | 8.5 | Wave speed v |

**Discovery Score:** 8.02/10

**Strengths:**

- Fisher-KPP — proven framework
- Предсказывает amplification rate
- Объясняет spatial clustering

**Weaknesses:**

- 3D time-lapse imaging очень трудоёмко
- Autocatalysis может быть артефакт (clonal expansion)
- Diffusion в ядре ограничен (не свободный)

---

## Cross-Domain Connections

### Connection 1: Topology Across Scales

```
ATR-T1 (torsional field) ↔ H-ECD-3 (Lk variational principle)
ATR-T3 (catenation) ↔ H-ECD-1 (percolation clustering)
```

Обе используют **топологические инварианты** (Lk, linking patterns) для функциональной регуляции.

### Connection 2: Phase Transitions

```
H-ECD-1 (percolation N_c) ↔ EXTENDED_HYPOTHESES_2 H-3D-3 (3D-attractor)
H-ECD-4 (bifurcation) ↔ RNA-DNA-2 (error threshold)
```

Все описывают **критические пороги** с резкими phenotypic shifts.

### Connection 3: Computational Memory

```
H-ECD-6 (reservoir computing) ↔ ATR-D4 (algorithmic memory)
H-ECD-2 (spectral gap) ↔ ATR-D3 (graph layer)
```

ecDNA как **distributed computing substrate**, не просто regulatory module.

### Connection 4: Immune Evasion

```
H-ECD-3 (Lk optimization) ↔ TE-3 (viral mimicry)
```

Обе балансируют **активность vs immune detection**.

---

## Integration with ATR Framework

**Возможные расширения ATR:**

```
ATR Layer 1 (FIELD)     ← H-ECD-3 (Lk variational field)
ATR Layer 2 (GRAPH)     ← H-ECD-2 (spectral gap), H-ECD-1 (percolation)
ATR Layer 3 (ALGORITHM) ← H-ECD-6 (reservoir computing)
ATR Layer 4 (MEMORY)    ← H-ECD-4 (hysteresis), H-ECD-5 (bet-hedging)
```

**Новый слой для ATR?**

```
LAYER 6: EXTRACHROMOSOMAL COMPUTATION
  ├─ Percolation clustering (H-ECD-1)
  ├─ Spectral autonomy (H-ECD-2)
  ├─ Topological optimization (H-ECD-3)
  ├─ Bistable resistance (H-ECD-4)
  ├─ Bet-hedging inheritance (H-ECD-5)
  ├─ Reservoir computing (H-ECD-6)
  └─ RD-wave amplification (H-ECD-7)
```

Альтернативно: **ecDNA как реализация всех 4 ATR слоёв на экстрахромосомном уровне**.

---

## Recommended Testing Order

### Tier 0: High Feasibility + Impact

1. **H-ECD-1** (percolation) — single-cell FISH routine, N_c measurable
2. **H-ECD-4** (bifurcation) — drug pulse стандартен, clinical impact

### Tier 1: Medium Feasibility

3. **H-ECD-6** (reservoir computing) — stimulus-response feasible, paradigm shift
4. **H-ECD-3** (Lk variational) — Lk measurement трудна, но immune link важен

### Tier 2: Requires Advanced Tech

5. **H-ECD-2** (spectral gap) — Hi-C дорого
6. **H-ECD-7** (RD-wave) — 3D time-lapse imaging heavy
7. **H-ECD-5** (bet-hedging) — lineage tracing + evolutionary modeling complex

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

### Hypothesis-Specific

**H-ECD-1 (Percolation):**

- KILL if: R²(two-regime fit) < 0.7
- KILL if: N_c variance > 3× across replicates

**H-ECD-2 (Spectral Gap):**

- KILL if: λ₂(ecDNA) ≤ λ₂(chr) + 2σ
- KILL if: R²(λ₂ → expression) < 0.4

**H-ECD-3 (Lk Variational):**

- KILL if: Lk distribution random (no peak)
- KILL if: cGAS activation не коррелирует с |Lk|

**H-ECD-4 (Bifurcation):**

- KILL if: λ_on ≈ λ_off ± 10% (no hysteresis)
- KILL if: switching time не зависит от history

**H-ECD-5 (Bet-Hedging):**

- KILL if: σ random (SD > 0.2)
- KILL if: |observed σ - σ*| > 3 SD

**H-ECD-6 (Reservoir):**

- KILL if: ESN accuracy ≤ linear baseline
- KILL if: no fading memory (non-exponential kernel)

**H-ECD-7 (RD-Wave):**

- KILL if: no traveling front visible
- KILL if: R²(v vs √(D·r)) < 0.5

---

## Literature Check (2026-04-26)

**User performed web search before submission. Ближайшие known works:**

- Morton et al. 2024 (Nature) — ecDNA hubs in cancer
- Chapman et al. 2023 (Nature Genetics) — ecDNA copy number dynamics
- Møller et al. 2024 (Nature) — ecDNA triggers cGAS-STING
- Lange et al. 2022 (Cancer Discovery) — asymmetric ecDNA segregation

**Ни одна из гипотез H-ECD-1..7 не обнаружена в доступной литературе.**

---

**Version:** 0.1.0  
**Last Updated:** 2026-04-26  
**Status:** Documented, awaiting experimental validation
