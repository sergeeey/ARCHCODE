# T2: TOP2 as Topological Annealing — Toy Model

**Status:** ⏳ Ready to run  
**Created:** 2026-04-26  
**Hypothesis:** TOP2 uses local geometric rules to achieve global topological simplification

---

## Hypothesis

TOP2 implements a localized неравновесный алгоритм topological annealing: strand passage events are biased by local crossing geometry, and this local bias produces global simplification of C(G) below equilibrium without knowledge of the full topology graph.

---

## Kill Criteria (Pre-Registered)

**KILL if:**
- `advantage_score > 0.8` (less than 20% improvement over random)
- `num_params > 5` (overfitting)
- `effect_size < 0.05` (too weak)

**SUCCESS if:**
- `advantage_score < 0.7` (≥30% improvement)
- `num_params <= 3` (simple rules)
- `effect_size > 0.3` (strong effect)

---

## Experimental Design

### System
- **200 ring polymers** (entangled initial state)
- **500 TOP2 events** (strand passage attempts)
- **Topological complexity:** C(G) = α|K| + β|C| + γΣ|Lk| + δΣ|σ|

### Models

| Model | Description | Parameters | Hypothesis |
|-------|-------------|------------|------------|
| **Random** | Baseline: p = 0.5 always | 0 | Passive relaxation |
| **Angle** | p ∝ exp(-\|θ - π/2\| / β) | 1 (β_angle) | TOP2 prefers perpendicular crossings |
| **Angle+Curv** | p ∝ exp(-\|θ - π/2\| / β₁) exp(-κ / β₂) | 2 (β_angle, β_curv) | TOP2 avoids high curvature |

### Metrics

```python
advantage_score = C_final(biased) / C_final(random)

# Lower is better:
# 1.0 = no effect
# 0.7 = 30% better than random (SUCCESS threshold)
# 0.5 = 50% better than random (very strong)
```

---

## How to Run

```bash
cd D:/ДНК/topology_control/experiments/t2_top2_annealing
python toy_model.py
```

**Expected runtime:** ~5-10 minutes

**Output:**
- Console: step-by-step progress + kill criteria check
- Plot: `complexity_evolution.png`
- Results: printed to console

---

## Interpretation

### If SUCCESS
→ Local geometric rules ARE sufficient for global simplification  
→ TOP2 acts as active topological optimizer  
→ Proceed to Phase 2 (T1 supercoiling field or H1 redox controller)

### If KILL
→ Local rules NOT sufficient OR toy model too simplified  
→ Options:
  1. Test with real polymer dynamics (HOOMD-blue)
  2. Pivot to D1 (spectral 3D) — independent test of ATR framework
  3. Publish negative result (falsification valuable)

### If MARGINAL (passes kill but not success)
→ Review assumptions:
  - Is ring model adequate? (vs real chromosomes)
  - Are parameters realistic? (β values)
  - Is complexity metric C(G) correct?

→ Decision: continue with caution or pivot

---

## Caveats

### [WEAK] Simplifications
1. **Rings are closed** — real chromatin has open domains
2. **No knot detection** — using simplified proxy (catenanes)
3. **Discrete events** — real TOP2 is continuous process
4. **No ATP energetics** — model is kinematic, not thermodynamic

### [INFERRED] Why These Are Acceptable for Toy Model
- Goal: test CONCEPT (local → global), not quantitative fit
- If toy model fails → real system unlikely to succeed
- If toy model succeeds → warrants more detailed simulation

---

## Next Steps After Run

### Immediately After
1. Check kill criteria
2. If SUCCESS: commit results
3. If KILL: write `NEGATIVE_RESULT.md`

### If SUCCESS
1. **Robustness check:** increase to 500 rings, 1000 steps
2. **Parameter sensitivity:** sweep β_angle ∈ [0.1, 2.0]
3. **Coarse-graining test:** aggregate rings → super-rings, check if effect persists
4. **Cross-validation:** compare with pyknotid/Topoly (real knot detection)

### If KILL
1. Document in `experiments/t2_top2_annealing/NEGATIVE_RESULT.md`
2. Update `UNIFIED_FRAMEWORK.md` → mark T2 as FALSIFIED
3. Pivot to D1 (spectral 3D controller)
4. Consider: write Methods paper on topology simulation even if hypothesis failed

---

## Files

```
t2_top2_annealing/
├── toy_model.py          # Main simulation
├── config.yaml           # Parameters (not used yet, for future)
├── README.md             # This file
└── [GENERATED]
    ├── complexity_evolution.png
    └── NEGATIVE_RESULT.md (if KILL)
```

---

## Связь с Unified Framework

**Tier 0 Core Validation:**
- T2 + D1 must BOTH pass for ATR framework to proceed
- If T2 fails but D1 succeeds → framework still viable (different layer)
- If T2 succeeds → strengthens Algorithm Layer of ATR

**Cross-Validation:**
- T2 predicts: C(G) should decrease with TOP2 activity
- D1 predicts: Δλ₂ should correlate with C(G) change
- If both true → mutual reinforcement

---

**Timestamp:** 2026-04-26  
**Pre-Registration:** See `../../KILL_CRITERIA.md`
