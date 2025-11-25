# ARCHCODE Full Pipeline

## Overview

Full ARCHCODE Pipeline integrates all components into a complete causal chain:

```
Extrusion Engine → Stability Model → Collapse Simulator → Risk Scoring → Output
```

## Architecture

```mermaid
graph LR
    A[Extrusion Engine] --> B[Stability Predictor]
    B --> C[Collapse Simulator]
    C --> D[Risk Scorer]
    D --> E[Output Exporters]
```

## Components

### 1. ARCHCODEFullPipeline

Main pipeline class that orchestrates all stages:

```python
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline

pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)

results = pipeline.run_full_analysis(
    boundaries_data=[...],
    barrier_strengths_map={...},
    methylation_map={...},
    collapse_events={...},
    enhancer_promoter_pairs=[...],
)
```

### 2. Processing Stages

#### Stage 1: Boundary Addition
- Add boundaries to pipeline
- Extract CTCF strengths, positions

#### Stage 2: Stability Analysis
- Calculate stability scores for all boundaries
- Categorize: stable/variable/intermediate
- Use VIZIR S1 config for thresholds

#### Stage 3: Collapse Simulation
- Simulate collapse events (methylation, CTCF loss, TE insertion)
- Calculate collapse probabilities
- Model collapse dynamics (gradual/sudden)

#### Stage 4: Risk Scoring
- Calculate enhancer hijacking risk
- Calculate oncogenic contact risk
- Compute total risk score

#### Stage 5: Output Generation
- Export to JSON, CSV, VIZIR log
- Generate summary statistics

## Output Formats

### JSON Format

```json
{
  "metadata": {
    "format_version": "1.0",
    "exporter": "ARCHCODE JSONExporter",
    "schema": "archcode_results_v1"
  },
  "boundaries": [...],
  "stability_predictions": [...],
  "collapse_results": {...},
  "summary": {...}
}
```

### CSV Format

Separate CSV files for:
- Boundaries (`*_boundaries.csv`)
- Stability predictions (`*_stability.csv`)
- Collapse results (`*_collapse.csv`)

### VIZIR Log Format

```json
{
  "experiment_id": "...",
  "results": {...},
  "config_hash": "..."
}
```

## Usage Example

See `examples/full_pipeline_example.py` for complete example.

## Integration with Experiments

Full pipeline integrates with experiments framework:

```python
from experiments.base_experiment import BaseExperiment
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline

class MyExperiment(BaseExperiment):
    def run(self):
        pipeline = ARCHCODEFullPipeline(...)
        results = pipeline.run_full_analysis(...)
        
        # Export
        exporter = ARCHCODEExporter()
        exporter.export_full_pipeline_results(...)
        
        return ExperimentResult(...)
```

## Data Flow

1. **Input**: Boundaries, factors (barriers, methylation, TE)
2. **Processing**: Stability → Collapse → Risk
3. **Output**: JSON, CSV, VIZIR log + summary statistics

## Summary Statistics

Pipeline generates:
- Boundary counts (stable/variable/intermediate)
- Average stability scores
- Collapse statistics
- Risk metrics

## VIZIR Integration

- Uses VIZIR P/S/L configs
- Records provenance
- Tracks config hashes
- Ensures reproducibility










