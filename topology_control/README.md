# Active Topological Regulation (ATR) Framework

**Version:** 0.1.0  
**Status:** Experimental (Phase 1 validation in progress)  
**Created:** 2026-04-26

---

## Central Hypothesis

**Клетка регулирует себя не через централизованное управление, а через распределённую топологическую самоорганизацию с фазовыми переходами.**

Эта архитектура применяется на всех уровнях:
- **Митохондрии:** redox fields, heteroplasmy filtering, nucleoid compaction
- **Ядерный геном:** supercoiling, 3D contacts, enhancer condensates
- **Регуляторные сети:** spectral graph properties, attractor landscapes

---

## Четыре топологических слоя

| Слой | Концепция | Гипотезы | Статус |
|------|-----------|----------|--------|
| **FIELD** | Распределённые поля (σ, r, a) | T1, H1 | Phase 2 |
| **GRAPH** | Topology графов связей | D1, T3 | Phase 1 ⏳ |
| **ALGORITHM** | Активные ATP-процессы | T2, D2 | Phase 1 ⏳ |
| **MEMORY** | Топологическая память | T3, H2, H3, D3 | Phase 3 |

---

## Quick Start

### 1. Install dependencies

```bash
pip install numpy scipy matplotlib scikit-learn
```

### 2. Run first experiment (T2: TOP2 annealing)

```bash
cd experiments/t2_top2_annealing
python toy_model.py
```

**Expected:** 5-10 min runtime, console output + plot

### 3. Check results

If **SUCCESS** (advantage_score < 0.7):
→ Proceed to Phase 2 experiments

If **KILL** (advantage_score > 0.8):
→ See `KILL_CRITERIA.md` for next steps

---

## Project Structure

```
topology_control/
├── shared_utils/              # Переиспользуемый код
│   ├── topology_utils.py      # Knots, catenanes, linking numbers
│   ├── graph_utils.py         # Spectral analysis, percolation
│   ├── phase_utils.py         # Free energy, order parameters
│   └── __init__.py
├── experiments/
│   ├── t2_top2_annealing/     # Phase 1: TOP2 toy model ⏳
│   ├── d1_spectral_3d/        # Phase 1: GWAS spectral analysis ⏳
│   ├── t1_supercoiling_field/ # Phase 2
│   └── h1_redox_controller/   # Phase 2
├── UNIFIED_FRAMEWORK.md       # Полное описание ATR
├── KILL_CRITERIA.md           # Pre-registration
└── README.md                  # This file
```

---

## Phase 1: Core Validation (Week 1)

**Goal:** Validate foundational hypotheses

| Experiment | Status | Timeline | Kill Criterion |
|------------|--------|----------|----------------|
| **T2: TOP2 annealing** | ⏳ Ready | Day 1-3 | advantage > 0.8 |
| **D1: Spectral 3D** | 📝 Planned | Day 4-7 | AUC(Δλ) <= baseline |

**Checkpoint Day 7:**
- ≥1 SUCCESS → proceed Phase 2
- Both KILL → STOP, pivot to H1 (independent)

---

## Гипотезы (9 total)

### Митохондрии (3)
- **H1:** МтДНК как локальный redox-контроллер (8.6/10)
- **H2:** Мито-эпигенетика как фильтр гетероплазмии (7.1/10)
- **H3:** Нуклеоид как фазовый переключатель (7.0/10)

### Топология ДНК (3)
- **T1:** Геном как поле суперскручивания (8.2/10)
- **T2:** TOP2 как топологический отжиг (8.8/10) ⭐
- **T3:** Катенационная перколяция (7.9/10)

### Тёмный геном (3)
- **D1:** Spectral 3D controller (8.76/10) ⭐
- **D2:** Enhancer condensates (8.62/10)
- **D3:** Spatial memory (8.42/10)

**⭐ = Phase 1 priorities**

---

## Связи между гипотезами

### Кластер 1: Топологическая 3D-регуляция (ЯДРО)
```
T1 (supercoiling) ↔ D1 (spectral) ↔ T2 (TOP2)
         ↓                ↓
    D3 (memory)    T3 (catenation)
```

### Кластер 2: Фазовые переходы
```
H1 (redox) → D2 (condensates) → H3 (nucleoid)
```

### Кластер 3: Стохастический отбор
```
H2 (heteroplasmy) ↔ D3 (attractors)
```

---

## Уроки из предыдущих проектов

### ARCHCODE (2025-2026)
- ✓ Category leakage → matched controls обязательны
- ✓ Small n misleads → n=89 killed n=49 "success"
- ✓ Pre-registration → prevented p-hacking

### Stress Biology (2026-04)
- ✓ Hypothesis REJECTED at n=89 (честно остановлены)
- ✓ Spurious correlations at small n
- ✓ Confounding tests critical

**Применение к ATR:**
- Pre-registered kill criteria (`KILL_CRITERIA.md`)
- Matched controls for D1 (cell-type, distance)
- Null hypothesis first (baseline models)
- Massive parameter sweeps (не n=5)

---

## Kill Criteria (Pre-Registered)

**Phase 1 Global:**
```
IF T2 KILL AND D1 KILL:
  → STOP all topology hypotheses
  → Pivot to H1 (mitochondria)
  → Publish negative result
```

**Per-Hypothesis:**
- See `KILL_CRITERIA.md` for full details
- Criteria LOCKED before experiments start
- No goalpost moving allowed

---

## Contributing

Этот проект — научная валидация гипотез, не open-source разработка.

**Но:**
- Код доступен для review
- Negative results будут опубликованы
- Методология прозрачна

---

## Citation

Если используете код или идеи:

```
@software{atr_framework_2026,
  title = {Active Topological Regulation (ATR) Framework},
  author = {[Your Name]},
  year = {2026},
  url = {https://github.com/...},
  note = {Pre-experimental validation}
}
```

---

## Status Updates

| Date | Event |
|------|-------|
| 2026-04-26 | Project created, Phase 1 ready |
| TBD | T2 results |
| TBD | D1 results |
| TBD | Phase 1 checkpoint |

---

## Contact

Questions about methodology: see `UNIFIED_FRAMEWORK.md`  
Questions about code: see inline docstrings  
Questions about kill criteria: see `KILL_CRITERIA.md`

---

**Version History:**
- v0.1.0 (2026-04-26): Initial framework, ready for Phase 1
