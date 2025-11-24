# Z-DNA Formation Logic

**RFC-style documentation**

## Overview

Z-DNA formation is **NOT noise** - it is a controlled process with specific physical-chemical conditions.

## Formation Conditions

### 1. Sequence Preference

Z-DNA requires **alternating purine-pyrimidine** sequences:

- **Most favorable**: GC repeats (`GCGCGC...`)
- **Also favorable**: GT, AC, AT alternating patterns
- **Minimum length**: ~6 bp (configurable)

Sequence preference weight: **0.6** (60% of formation probability)

### 2. Negative Supercoiling (Torque)

Z-DNA is stabilized by **negative supercoiling**:

- **Threshold**: torque < -0.05 (negative = supercoiling)
- **Mechanism**: Negative supercoiling unwinds DNA, promoting Z-DNA
- **Torque weight**: **0.3** (30% of formation probability)

### 3. Transcription Effect

Active transcription creates **negative supercoiling** ahead of RNA polymerase:

- Transcription → negative supercoiling → Z-DNA formation
- This is a **controlled biological process**, not noise
- Transcription boost: +0.5 to torque score

### 4. Ionic Conditions

High salt concentrations stabilize Z-DNA:

- Base stabilization: **0.1** (10% of formation probability)
- Configurable via `ionic_stabilization` parameter

## Formation Probability

```
P(Z-DNA) = sequence_score × 0.6 + torque_score × 0.3 + 0.1
```

Where:
- `sequence_score`: GC repeat / alternating pattern score (0.0-1.0)
- `torque_score`: Negative supercoiling score (0.0-1.0)
- Base stabilization: 0.1

**Threshold**: P(Z-DNA) > 0.5 → barrier forms

## Biological Significance

Z-DNA formation is **functionally important**:

1. **Gene regulation**: Z-DNA forms at promoters, affects transcription
2. **Chromatin structure**: Creates energy barriers for loop extrusion
3. **Protein binding**: ZBP1, ADAR1 specifically recognize Z-DNA
4. **Genome stability**: Z-DNA regions are hotspots for recombination

## Model Implementation

See `src/nonB_logic/barrier_model.py::ZDNAModel`:

- `detect_zdna()`: Main detection logic
- `_calculate_sequence_preference()`: Sequence scoring
- `_check_alternating_pattern()`: Alternating pattern detection

## Configuration

All parameters in `config/nonB_logic.yaml`:

```yaml
z_dna_parameters:
  transition_threshold: -0.05      # Negative torque threshold
  sequence_preference_weight: 0.6
  torque_weight: 0.3
  ionic_stabilization: 0.1
  min_gc_repeat_length: 6
  barrier_strength: 0.6
```

## Engineering Unknowns

**Risk L1**: Exact transition threshold calibration
- Current: -0.05 (placeholder)
- Requires: Experimental torque measurements
- Impact: Medium (0.5)

## References

- Z-DNA formation requires negative supercoiling
- GC repeats are most favorable sequence
- Transcription creates negative supercoiling
- Z-DNA is functionally important, not noise







