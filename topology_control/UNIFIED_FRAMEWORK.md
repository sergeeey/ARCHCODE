# Active Topological Regulation (ATR) Framework

**Version:** 0.1.0  
**Status:** Pre-experimental  
**Created:** 2026-04-25  
**Based on:** 9 interdisciplinary hypotheses (mitochondria, DNA topology, dark genome)

---

## Центральная гипотеза

**Клетка регулирует себя не через централизованное управление, а через распределённую топологическую самоорганизацию с фазовыми переходами.**

Это применяется на всех уровнях:
- Митохондрии (redox field, nucleoid compaction, heteroplasmy)
- Ядерный геном (supercoiling, 3D contacts, enhancer condensates)
- Регуляторные сети (spectral graph properties, attractor landscapes)

---

## Четыре топологических слоя

### 1. FIELD LAYER (распределённые поля)

**Концепция:** Клетка создаёт непрерывные поля физических величин, которые распространяются и взаимодействуют.

| Поле | Где | Механизм | Гипотеза |
|------|-----|----------|----------|
| Supercoiling σ(x,t) | Ядерная ДНК | Транскрипция создаёт, TOP1/2 снимают | T1 |
| Redox r(x,t) | Митохондрия | OXPHOS создаёт, антиоксиданты снимают | H1 |
| Accessibility a(x,t) | Хроматин | TF binding, nucleosome remodeling | D1 |

**Математика:**
```
∂φ/∂t = D∇²φ + S(x,t) - R(x,t) - λφ

где:
  φ — поле (σ, r, a)
  D — диффузия/распространение
  S — источники
  R — стоки (ферменты, релаксация)
  λ — decay rate
```

**Критический параметр:** корреляционная длина ξ  
- Если ξ > domain size → field-based control оправдан  
- Если ξ < 1 gene → локальная модель достаточна

---

### 2. GRAPH LAYER (топология связей)

**Концепция:** Состояние системы определяется не только узлами, но и топологией графа связей.

| Граф | Узлы | Рёбра | Гипотеза |
|------|------|-------|----------|
| G_contact | Хроматиновые bins | Hi-C contacts | D1 |
| G_catenation | ДНК петли/кольца | Топологические сцепления | T3 |
| G_regulatory | Гены + энхансеры | E-P interactions | D1, D3 |
| G_mtDNA | Копии мтДНК | Linking numbers | H2 |

**Математика:**
```
Лапласиан: L = D - A
Спектр: Lv = λv

Критические метрики:
  λ₂ — algebraic connectivity
  v₂ — Fiedler vector (разделяет домены)
  Q — модульность
  S — размер гигантской компоненты (перколяция)
```

**Ключевая идея:**  
Варианты/мутации действуют через возмущение спектра:
```
ΔG → ΔL → Δλₖ → Δ(gene expression module)
```

---

### 3. ALGORITHM LAYER (активные процессы)

**Концепция:** Клетка использует ATP-зависимые алгоритмы для неравновесного управления.

| Алгоритм | Где | Что делает | Аналог из CS | Гипотеза |
|----------|-----|------------|--------------|----------|
| TOP2 strand passage | Ядро | Снижает C(G) ниже равновесия | Simulated annealing | T2 |
| Enhancer condensation | Nucleus | Пороговая активация | Phase nucleation | D2 |
| Mitochondrial fission/fusion | Митохондрия | Ресемплинг мтДНК популяций | Particle filtering | H2 |

**Математика:**
```
Топологическая сложность:
C(G) = α|K| + β|C| + γΣ|Lk_ij| + δΣ|σ_i|

где:
  K — узлы (knots)
  C — катенаны
  Lk — linking numbers
  σ — supercoiling

TOP2 bias:
P(G → G') ∝ exp[-β_eff ΔC + μ·ATP + η·Γ_local]
```

**Критическое свойство:** detailed balance нарушен  
→ система активно упрощается, а не просто релаксирует

---

### 4. MEMORY LAYER (топологическая память)

**Концепция:** Прошлые состояния влияют на будущие через топологические/структурные следы.

| Механизм памяти | Где | Как работает | Гипотеза |
|-----------------|-----|--------------|----------|
| Catenation gel | Хроматин | Петли зацеплены → замедляют перестройку | T3 |
| Heteroplasmy drift | Митохондрия | История репликации bias | H2 |
| Nucleoid compaction | мтДНК | Фазовое состояние упаковки | H3 |
| Attractor basin | Cell state | 3D-конфигурация стабилизирует тип клетки | D3 |

**Математика:**
```
Динамика с памятью:
X_t+1 = F(X_t, X_history, G_topology, genotype)

Attractor landscape:
ℰ(X) = -½ X^T W_g X + b^T X + Ω(C,A,E)

Критерий устойчивости:
d(Basin_healthy, Basin_disease)
```

---

## Взаимосвязи слоёв

```
FIELD → GRAPH → ALGORITHM → MEMORY
  ↑_________________________________↓

Пример полного цикла:

1. Транскрипция создаёт supercoiling field (FIELD)
2. Поле изменяет вероятность контактов (GRAPH)
3. TOP2 активно упрощает топологию (ALGORITHM)
4. Катенация сохраняет след перестройки (MEMORY)
5. Память влияет на будущее поле (обратная связь)
```

---

## Центральные предсказания ATR

### Предсказание 1: GWAS variants действуют через топологические возмущения

**Стандартная модель:**
```
SNP → enhancer motif disrupted → nearest gene ↓
```

**ATR модель:**
```
SNP → ΔA_ij (contact change)
    → Δλ_k (spectral shift)
    → entire regulatory module affected
    → state-dependent, threshold effect
```

**Тестируемо:** spectral perturbation лучше предсказывает eQTL, чем distance

---

### Предсказание 2: Локальные правила дают глобальное упрощение

**Стандартная модель:**
```
TOP2 режет случайно → passive relaxation
```

**ATR модель:**
```
TOP2 использует локальную геометрию
    → biased strand passage
    → глобальное C(G) падает ниже равновесия
```

**Тестируемо:** toy ring model с local bias даёт active simplification

---

### Предсказание 3: Фазовые переходы создают threshold effects

**Стандартная модель:**
```
Эффект варианта ∝ изменение affinity (линейно)
```

**ATR модель:**
```
Вариант сдвигает параметр a(g,s)
    → если a < 0, фазовый переход
    → резкий нелинейный эффект
```

**Тестируемо:** risk variants дают state-dependent effects около фазовой границы

---

## Критерии фальсификации (pre-registered)

### Гипотеза T2 (TOP2 annealing)
**KILL если:**
- advantage_score < 1.2
- ИЛИ нужно >5 параметров для упрощения
- ИЛИ эффект исчезает при coarse-graining

**ПРОДОЛЖИТЬ если:**
- advantage > 2.0 И <3 параметров

---

### Гипотеза D1 (Spectral 3D)
**KILL если:**
- Δλ не лучше nearest-gene baseline для eQTL
- ИЛИ сигнал исчезает при matched controls

**ПРОДОЛЖИТЬ если:**
- Δλ даёт +10% AUC для eQTL prediction
- И эффект сохраняется при cell-type matching

---

### Unified Framework
**KILL ВЕСЬ ATR если:**
- T2 И D1 обе провалились
- ИЛИ нет общего математического ядра между слоями

**ПРОДОЛЖИТЬ если:**
- Хотя бы 2 из 4 слоёв подтверждены
- И есть cross-validation между гипотезами

---

## Roadmap

### Phase 1: Core validation (Week 1)
- [ ] T2 toy model
- [ ] D1 spectral analysis
- [ ] Checkpoint: хотя бы одна успешна

### Phase 2: Expansion (Week 2-3)
- [ ] T1 или H1 (в зависимости от Phase 1)
- [ ] D2 condensates

### Phase 3: Specialization (по необходимости)
- [ ] T3, H3, H2, D3

---

## Связь с предыдущими проектами

### ARCHCODE
**Урок:** category leakage, matched controls  
**Применение:** D1 должен контролировать cell-type-specific effects

### Stress Biology
**Урок:** small n misleads, spurious correlations  
**Применение:** массовый sweep параметров, не довольствоваться n=5

---

## Литература (ключевые работы)

1. **CoRR hypothesis** (Allen 2015, PNAS) — field control в митохондриях
2. **Topological epigenetics** (Corless & Gilbert 2024, ScienceDirect) — supercoiling как информация
3. **Olympic gels** (Lu et al. 2024, JCP) — catenation percolation
4. **3D genome GWAS** (Nature Comms 2025) — spectral graph для non-coding variants
5. **TOP2 mechanism** (Berger et al., multiple) — ATP-dependent simplification

---

**Version History:**
- v0.1.0 (2026-04-25): Initial framework, pre-experimental
