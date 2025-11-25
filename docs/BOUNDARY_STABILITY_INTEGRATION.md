# Boundary Stability Predictor - Integration Guide

## Overview

The Boundary Stability Predictor integrates with all ARCHCODE modules to predict TAD boundary stability across cells.

## Integration Points

### 1. ARCHCODE Core (CTCF Sites)

```python
from src.archcode_core.extrusion_engine import Boundary
from src.boundary_stability import StabilityCalculator

# Get CTCF strength from archcode_core
boundary = Boundary(position=100000, strength=0.8, ...)
ctcf_strength = boundary.strength

# Use in stability calculation
calculator = StabilityCalculator(config)
prediction = calculator.calculate_stability(
    position=boundary.position,
    ctcf_strength=ctcf_strength,
    ...
)
```

### 2. Non-B Logic (Energy Barriers)

```python
from src.nonB_logic.barrier_model import BarrierHierarchy, EnergyBarrier
from src.boundary_stability import StabilityCalculator

# Get barriers from nonB_logic
barriers = [barrier1, barrier2, barrier3]  # G4, Z-DNA, R-loops
barrier_strengths = [b.strength for b in barriers]

# Use in stability calculation
prediction = calculator.calculate_stability(
    position=position,
    ctcf_strength=ctcf_strength,
    barrier_strengths=barrier_strengths,
    ...
)
```

### 3. Epigenetic Compiler (Methylation)

```python
from src.epigenetic_compiler.methylation_model import MethylationModel
from src.boundary_stability import StabilityCalculator

# Get methylation level from epigenetic_compiler
methylation_model = MethylationModel(config)
methylation_level = methylation_model.get_boundary_strength(position)

# Use in stability calculation
prediction = calculator.calculate_stability(
    position=position,
    ctcf_strength=ctcf_strength,
    methylation_level=1.0 - methylation_level,  # Inverse relationship
    ...
)
```

### 4. TE Grammar (TE Motifs)

```python
from src.te_grammar.motif_dictionary import MotifDictionary
from src.boundary_stability import StabilityCalculator

# Get TE motif effects from te_grammar
motif_dict = MotifDictionary(config)
motifs = motif_dict.find_motifs(sequence)
te_effects = [motif.strength for motif in motifs]

# Use in stability calculation
prediction = calculator.calculate_stability(
    position=position,
    ctcf_strength=ctcf_strength,
    te_motif_effects=te_effects,
    ...
)
```

## Full Integration Example

```python
import yaml
from src.boundary_stability import StabilityCalculator
from src.archcode_core.extrusion_engine import Boundary
from src.nonB_logic.barrier_model import BarrierHierarchy
from src.epigenetic_compiler.methylation_model import MethylationModel
from src.te_grammar.motif_dictionary import MotifDictionary

# Load all configs
with open("config/boundary_stability.yaml") as f:
    stability_config = yaml.safe_load(f)

# Initialize all modules
calculator = StabilityCalculator(stability_config)
# ... initialize other modules ...

# For each boundary position
for boundary in boundaries:
    # Collect factors from all modules
    ctcf_strength = boundary.strength
    
    barriers = get_barriers_at_position(boundary.position)
    barrier_strengths = [b.strength for b in barriers]
    
    methylation_level = methylation_model.get_boundary_strength(boundary.position)
    
    sequence = get_sequence_at_position(boundary.position)
    motifs = motif_dict.find_motifs(sequence)
    te_effects = [m.strength for m in motifs]
    
    # Predict stability
    prediction = calculator.calculate_stability(
        position=boundary.position,
        ctcf_strength=ctcf_strength,
        barrier_strengths=barrier_strengths,
        methylation_level=1.0 - methylation_level,
        te_motif_effects=te_effects,
        event_order=get_event_order(boundary.position),
        total_events=len(boundaries),
    )
    
    print(f"Boundary at {boundary.position}: {prediction.stability_category}")
```

## Output Usage

Stability predictions can be used to:

1. **Filter stable boundaries** for downstream analysis
2. **Adjust merotelic probabilities** in genome_to_tension bridge
3. **Prioritize boundaries** for experimental validation
4. **Understand variability** in chromatin architecture

## Configuration

All parameters in `config/boundary_stability.yaml`:

- `stable_threshold`: 0.7 (≥0.7 → stable)
- `variable_threshold`: 0.4 (≤0.4 → variable)
- `barrier_multiplier`: 1.0
- `te_multiplier`: 1.0








