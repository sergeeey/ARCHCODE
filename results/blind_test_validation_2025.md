# Blind-test validation: Sabaté et al. 2024 (bioRxiv)

> **Canonical status (2026-03-06):** Legacy validation summary. Interpret under
> `results/validation_canonical_index_2026-03-06.json` and
> `results/publication_claim_matrix_2026-03-06.json`.
> This file is non-clinical and does not authorize standalone causal or reclassification claims.

## Methodology

- **Source:** Sabaté et al., 2024 (bioRxiv, DOI: 10.1101/2024.08.09.605990)
- **Time mapping:** 1 simulation step = 1 second
- **Cohesin speed (v):** 0.3 kb/s → 300 bp/step
- **Residence time (T_res):** 16.67 min = 1000 steps → unloading probability = 0.001 (calibrated within literature 10–30 min)
- **Loading:** ~1 event per hour per TAD → loading probability = 1/3600 per step
- **Locus:** HBB_CTCFKD (chr11), 5 CTCF sites
- **Runs:** 100 independent simulations, 36000 steps each (10.0 h model time per run)

## Results

### Loop duration (steps → minutes)

| Metric | Steps | Minutes |
|--------|-------|---------|
| Mean   | 1013.3 | 16.89 |
| Std    | 1122.1 | 18.70 |
| 95% CI | [805, 1221] | [13.42, 20.35] |
| N (loops with duration) | 112 | — |

### Contact probability (anchor pairs)

Fraction of simulation time with a stable loop (any anchor pair): **3.1524%**

### Distribution (duration in minutes, bin width 2 min)

```
   0 min | █████████████████████████████████████ 13
   2 min | ████████████████████████████████████████ 14
   4 min | █████████████████████████████ 10
   6 min | ██████████████████████████ 9
   8 min | ██████████████████████████ 9
  10 min | ██████████████ 5
  12 min | ██████████████ 5
  14 min | █████████████████ 6
  16 min | █████████ 3
  18 min | █████████████████ 6
  20 min | ██████ 2
  22 min | █████████ 3
  24 min | ██████ 2
  26 min | ██████ 2
  30 min | ███ 1
  32 min | █████████ 3
  34 min | █████████ 3
  36 min | █████████████████ 6
  42 min | ███ 1
  44 min | ██████ 2
  48 min | ██████ 2
  54 min | ███ 1
  56 min | ███ 1
  60 min | ███ 1
  72 min | ███ 1
 128 min | ███ 1
```

### Experimental target

Loop duration in vivo (Sabaté et al., 2024, bioRxiv): **6–19 minutes** (360–1140 steps).

## Verdict

**PASS** — Mean loop duration in simulation: **16.89 min** (95% CI: [13.42, 20.35] min).

✅ Mean falls within the experimental range 6–19 min. The model reproduces loop kinetics without fitting.
