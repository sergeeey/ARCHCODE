# VIZIR Integration Guide

## Overview

VIZIR (Validation, Integration, Zero-trust, Iterative Refinement) framework provides systematic management of Engineering Unknowns through P/S/L configuration layers.

## Architecture

```
Engineering Unknowns
├── Physical Layer (P1-P3)
│   ├── P1: Extrusion Symmetry
│   ├── P2: Supercoiling Dynamics
│   └── P3: Cohesin Loading
│
├── Structural Layer (S1-S3)
│   ├── S1: TAD Boundary Determinism
│   ├── S2: TE Motif Effects
│   └── S3: Non-B DNA Barriers
│
└── Logical Layer (L1-L3)
    ├── L1: Z-DNA Formation Logic
    ├── L2: Epigenetic Compiler Threshold
    └── L3: Kinetochore Tension Calibration
```

## Usage

### Loading Configs

```python
from src.vizir.config_loader import VIZIRConfigLoader

# Initialize loader
loader = VIZIRConfigLoader()

# Load specific unknown
p1_config = loader.load_physical("P1")
s1_config = loader.load_structural("S1")
l1_config = loader.load_logical("L1")

# Load all unknowns
all_physical = loader.load_all_physical()
all_structural = loader.load_all_structural()
all_logical = loader.load_all_logical()
```

### Loading Hypotheses

```python
# Load specific hypothesis
hypothesis_a = loader.load_hypothesis("P1", "hypothesis_a", "physical")
hypothesis_b = loader.load_hypothesis("P1", "hypothesis_b", "physical")

# Use in simulation
vizir_configs = {
    "P1": p1_config,
}
vizir_configs["P1"]["parameters"].update(hypothesis_a["parameters"])
```

### Integration with Modules

```python
from src.archcode_core.extrusion_engine import LoopExtrusionEngine

# Load base config
with open("config/archcode_engine.yaml") as f:
    archcode_config = yaml.safe_load(f)

# Load VIZIR configs
loader = VIZIRConfigLoader()
vizir_configs = {
    "P1": loader.load_physical("P1"),
    "P2": loader.load_physical("P2"),
    "P3": loader.load_physical("P3"),
}

# Initialize engine with VIZIR configs
engine = LoopExtrusionEngine(archcode_config, vizir_configs=vizir_configs)
```

## Hypothesis Comparison

Each Engineering Unknown contains multiple hypotheses:

```python
# Compare hypotheses
hypothesis_a = loader.load_hypothesis("P1", "hypothesis_a", "physical")
hypothesis_b = loader.load_hypothesis("P1", "hypothesis_b", "physical")

# Run simulation with Hypothesis A
vizir_configs_a = {"P1": p1_config}
vizir_configs_a["P1"]["parameters"].update(hypothesis_a["parameters"])
pipeline_a = ARCHCODEPipeline(archcode_config, stability_config)

# Run simulation with Hypothesis B
vizir_configs_b = {"P1": p1_config}
vizir_configs_b["P1"]["parameters"].update(hypothesis_b["parameters"])
pipeline_b = ARCHCODEPipeline(archcode_config, stability_config)

# Compare results
result_a = pipeline_a.analyze_boundary_stability(...)
result_b = pipeline_b.analyze_boundary_stability(...)
```

## Module Integration

### archcode_core

Supports P1, P2, P3:
- P1: Extrusion mode, direction bias
- P2: Supercoiling generation
- P3: Cohesin loading mode

### nonB_logic

Supports S3, L1:
- S3: G4, Z-DNA, R-loop formation parameters
- L1: Z-DNA formation logic weights

### boundary_stability

Supports S1:
- S1: Stability thresholds, factor weights

## Configuration Structure

Each P/S/L config contains:

```yaml
unknown_id: P1
category: Physical
layer: Physical
uncertainty: 0.8
impact_on_model: 0.9
priority: 0.72

description: >
  Description of the unknown

parameters:
  # Parameter values

hypotheses:
  hypothesis_a:
    name: "Hypothesis A name"
    description: "Description"
    parameters:
      # Override parameters

integration:
  archcode_core:
    module: "src/archcode_core/extrusion_engine.py"
    parameter_path: "extrusion_params.extrusion_mode"
```

## Examples

See:
- `examples/vizir_integration_example.py` - Basic usage
- `examples/hypothesis_comparison.py` - Hypothesis comparison

## Benefits

1. **Systematic Hypothesis Testing**: Compare multiple hypotheses for each unknown
2. **Reproducibility**: All parameters tracked in VIZIR ledger
3. **Modularity**: Each unknown is independent configuration
4. **Integration**: Automatic parameter mapping to modules







