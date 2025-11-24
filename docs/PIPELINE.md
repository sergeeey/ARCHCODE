# ARCHCODE Pipeline Integration

**RFC-style documentation**

## Overview

The `ARCHCODEPipeline` class provides integrated simulation pipeline that combines all ARCHCODE modules into a single workflow.

## Pipeline Flow

```
Sequence → Feature Extraction → TE Grammar → Non-B Logic →
Epigenetic Compiler → Loop Extrusion → Boundary Stability → Genome-to-Tension
```

## Usage

### Basic Example

```python
from src.archcode_core.pipeline import ARCHCODEPipeline, PipelineConfig

# Initialize pipeline
config = PipelineConfig()
pipeline = ARCHCODEPipeline(config)

# Add boundaries
pipeline.add_boundary(position=100000, strength=0.9, barrier_type="ctcf")

# Analyze stability
prediction = pipeline.analyze_boundary_stability(
    position=100000,
    barrier_strengths=[0.5, 0.3],
    methylation_level=0.1,
    te_motif_effects=[0.2],
    event_order=1,
)
```

### Full Pipeline Example

```python
# Add multiple boundaries
for pos, strength in boundaries:
    pipeline.add_boundary(pos, strength, "ctcf")

# Provide factors from all modules
barrier_strengths_map = {pos: barriers for pos, barriers in ...}
methylation_levels = {pos: level for pos, level in ...}
te_motif_effects_map = {pos: effects for pos, effects in ...}

# Analyze all boundaries
predictions = pipeline.analyze_all_boundaries(
    barrier_strengths_map=barrier_strengths_map,
    methylation_levels=methylation_levels,
    te_motif_effects_map=te_motif_effects_map,
)

# Get summary
summary = pipeline.get_stability_summary()
print(f"Stable boundaries: {summary['stable_count']}")
```

## Integration Points

### 1. ARCHCODE Core
- Provides boundaries via `add_boundary()`
- Uses `LoopExtrusionEngine` for simulation

### 2. Non-B Logic
- Provides energy barriers via `barrier_strengths_map`
- G4, Z-DNA, R-loop barriers

### 3. Epigenetic Compiler
- Provides methylation levels via `methylation_levels`
- Can provide histone modifications

### 4. TE Grammar
- Provides TE motif effects via `te_motif_effects_map`
- Positive/negative effects on stability

### 5. Boundary Stability Predictor
- Integrated automatically
- Calculates stability for all boundaries

## Output

### Stability Predictions

Each prediction contains:
- `position`: Genomic position
- `stability_score`: 0.0-1.0
- `stability_category`: "stable", "variable", "intermediate"
- `confidence`: Prediction confidence

### Summary Statistics

- `total_boundaries`: Total number of boundaries
- `stable_count`: Number of stable boundaries
- `variable_count`: Number of variable boundaries
- `intermediate_count`: Number of intermediate boundaries
- `average_stability`: Average stability score
- `stable_fraction`: Fraction of stable boundaries

## Visualization

Use `examples/plot_boundary_stability.py` to generate:
- Stability profile along chromosome
- CTCF strength overlay
- Category distribution

## Configuration

Pipeline loads configurations from:
- `config/archcode_engine.yaml`
- `config/boundary_stability.yaml`
- `config/nonB_logic.yaml`
- `config/epigenetic_compiler.yaml`
- `config/te_grammar.yaml`

Customize via `PipelineConfig` class.

