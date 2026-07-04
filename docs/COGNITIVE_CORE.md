# ARCHCODE Cognitive Core

This document captures **implicit design decisions** and their rationale so they are not lost during refactoring or handover. Use it for onboarding and for answering reviewers.

---

## Constants and parameters

### Why `velocity = 1000` (bp/step)

- **Literature**: Davidson et al. (2019) Science — human **cohesin** single-molecule: 0.5 kb/s mean, up to 2.1 kb/s max.
- ⚠️ **WARNING**: Ganji et al. (2018) studied **CONDENSIN**, not cohesin! Condensin is faster (~1.5 kb/s).
- **In code**: Default 1000 bp/step in engine config; constant `EXTRUSION_SPEED_BP_PER_S: 1000` in `src/domain/constants/biophysics.ts`.
- **Justification**: 1000 bp/step is upper range of cohesin literature values, chosen for faster simulation dynamics.
- **Note**: Steps are dimensionless; the label "bp/step" means "base pairs moved per simulation step." Mapping to real time is via `BIOLOGICAL_TIME_SCALE` (tunable).

### Why `processivity = 600` kb (MODEL PARAMETER)

- **Literature**: Davidson et al. (2019) — average extruded loop size **33 kb** in single-molecule assay.
- **Model value**: 600 kb (~18× higher than literature).
- **Justification**: Higher processivity allows formation of domain-scale TADs (100s of kb) observed in Hi-C. Single-molecule conditions differ from in vivo (no nucleosomes, no other proteins).
- **Uncertainty**: HIGH — this is a calibration parameter, not a measured constant.

### Why unloading probability ~0.0005–0.0008

- **Target**: Mean residence time ~20 min (Gerlich et al. 2006).
- **Logic**: At 1 s/step, 20 min = 1200 steps → probability per step ≈ 1/1200 ≈ 0.000833.
- **In code**: `COHESIN_PARAMS.UNLOADING_PROBABILITY` in `src/domain/constants/biophysics.ts` (value may be 0.000833 or 0.0005 depending on calibration).
- **CALIBRATION NEEDED**: In vivo residence time for specific cell types (e.g. GM12878) is not fixed in the code; document any cell-specific calibration.

### Why convergent efficiency 85%

- **Source**: Rao et al. (2014) Cell — convergent CTCF pairs enriched at loop anchors; ensemble estimate ~80–95%.
- **In code**: `CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY: 0.85` in `src/domain/constants/biophysics.ts`.
- **Note**: This is an **ensemble** parameter, not single-molecule; single-molecule efficiency may differ.

### MODEL PARAMETER vs LITERATURE-BASED

- **LITERATURE-BASED**: Value taken from papers (e.g. speed range, residence time order of magnitude).
- **MODEL PARAMETER**: Tunable for calibration; may have high uncertainty (e.g. bookmarking efficiency 50% — no direct measurement). See comments in `biophysics.ts`.

---

## Time and steps

### Steps are dimensionless

- Simulation **steps** are discrete events (one cohesin move per step, etc.). They are **not** seconds.
- **Biological time** mapping: `BIOLOGICAL_TIME_SCALE` in `SIMULATION_CONFIG` (e.g. 1 s/step) is a **tunable** mapping, not a physical constant.
- So "20 minutes residence time" means "~1200 steps at current time scale" — approximate and scale-dependent.

### Event time `t` vs step in ArchcodeRun

- In experiment run events, **`step`** is the **source of truth** for ordering and replay (two runs with same seed → same events by step).
- **`t`** is wall-clock ms since run start (auxiliary); it can drift between runs. See `src/domain/models/experiment.ts` and comments in `src/pages/Simulator.tsx`.

---

## Validation and ground truth

- **Current validation**: Mock/synthetic contact maps (and optional AlphaGenome-style API mock). See `src/validation/alphagenome.ts`, `KNOWN_ISSUES.md`.
- **Publication target**: Correlation against **experimental Hi-C** (e.g. Rao et al. 2014, ENCODE) with Pearson r ≥ 0.7. Do not state "validated against AlphaGenome" without clarifying mock vs real API.

---

## CALIBRATION NEEDED (documented limitations)

| Item                  | Condition                                          | Consequence                                          |
| --------------------- | -------------------------------------------------- | ---------------------------------------------------- |
| Residence time        | Unloading calibrated to ~20 min; not cell-specific | Cannot claim "20 min in GM12878" without calibration |
| Convergent efficiency | 85% from ensemble data                             | Single-molecule behavior may differ                  |
| Bookmarking           | 50% assumed                                        | No direct measurement; high uncertainty              |

When publishing or applying to a specific cell type, document these and, if possible, cite or add calibration data.
