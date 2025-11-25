# ARCHCODE Technical Specification

**Version:** 1.0  
**Date:** November 25, 2025  
**Status:** Internal / Private  
**Author:** ARCHCODE Development Team

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Simulation Engine (private)](#3-simulation-engine-private)
4. [RS-Metrics Formal Spec](#4-rs-metrics-formal-spec)
5. [Memory Channels](#5-memory-channels)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [Validation Protocol](#7-validation-protocol)
8. [Hi-C Integration (internal)](#8-hi-c-integration-internal)
9. [TERAG Cognitive Layer](#9-terag-cognitive-layer)
10. [Extension Modules](#10-extension-modules)

---

## 1. Purpose & Scope

### 1.1 Project Mission

ARCHCODE is a **physics-based computational framework** for modeling 3D genome architecture and chromatin loop dynamics. The system simulates:

- **Loop extrusion** via SMC complexes (cohesin, condensin)
- **Boundary stability** and TAD formation
- **Epigenetic memory** transmission across cell cycles
- **Processivity phase transitions** (Collapse → Transition → Stable)
- **Bookmarking-based memory channels** (CTCF-mediated)

### 1.2 Scientific Objectives

1. **Quantitative Prediction**: Predict architectural stability from molecular parameters (NIPBL velocity, WAPL lifetime, bookmarking fraction)

2. **Phase Diagram Mapping**: Identify critical thresholds for:
   - Processivity (RS-09): λ = NIPBL_velocity × WAPL_lifetime
   - Bookmarking (RS-10): Memory retention threshold ~0.3-0.4
   - Multichannel Memory (RS-11): Epigenetic compensation surface

3. **Biological Validation**: Compare predictions with real Hi-C data (GM12878, CdLS, WAPL-KO)

4. **Clinical Translation**: Enable diagnostic/prognostic applications for architectural disorders

### 1.3 Scope Boundaries

**In Scope:**
- Loop extrusion physics (1D polymer model)
- Boundary element recognition (CTCF motifs)
- Epigenetic bookmarking dynamics
- TAD boundary stability
- Phase diagram generation
- Real Hi-C data comparison

**Out of Scope (v1.0):**
- Full 3D polymer dynamics (FISH validation)
- Chromosome-scale simulations (>10 Mb)
- Real-time visualization
- Multi-species universal parameters
- Synthetic chromatin design tools

### 1.4 Target Users

- **Primary**: Computational biologists, chromatin researchers
- **Secondary**: Clinical geneticists (CdLS, WAPL-related disorders)
- **Tertiary**: Synthetic biology engineers

---

## 2. High-Level Architecture

### 2.1 System Layers

```
┌─────────────────────────────────────────────────────────┐
│              TERAG Cognitive Layer                        │
│  (Mission Orchestration, Validation, Explanation)        │
└────────────────────┬──────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────┐
│              ARCHCODE Core API                            │
│  (RS-09/10/11, Pipeline, Comparison)                     │
└────────────────────┬──────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────┐
│              Simulation Engine (Private)                  │
│  (Loop Extrusion, Bookmarking, Memory Channels)           │
└────────────────────┬──────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────┐
│              Bio-Metrics Engine                          │
│  (Insulation, P(s), TAD Calling, Correlation)             │
└────────────────────┬──────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────┐
│              Data Layer                                   │
│  (Hi-C Files, Configs, Results, Reports)                  │
└────────────────────────────────────────────────────────────┘
```

### 2.2 Component Overview

**TERAG Cognitive Layer:**
- Mission definitions (YAML)
- Result validation
- Explanation generation
- Integration adapter (`ArchcodeAdapter`)

**ARCHCODE Core API:**
- `run_rs09_summary()`: Processivity phase diagram
- `run_rs10_summary()`: Bookmarking threshold
- `run_rs11_summary()`: Multichannel memory surface
- `run_pipeline()`: Unified validation pipeline

**Simulation Engine (Private):**
- `ExtrusionEngine`: Loop extrusion physics
- `BookmarkingEngine`: CTCF memory dynamics
- `MemoryChannel`: Epigenetic compensation

**Bio-Metrics Engine:**
- `compute_insulation()`: Insulation score
- `compute_ps_curve()`: P(s) scaling
- `detect_tad_boundaries()`: TAD calling
- `compare_archcode_vs_real()`: Correlation analysis

**Data Layer:**
- `.cool` / `.mcool` files (Hi-C data)
- YAML configs (`pipeline_fast.yaml`, `pipeline_full.yaml`)
- JSON results (`rs09_results.json`, etc.)
- Markdown reports (`PIPELINE_SUMMARY_*.md`)

### 2.3 Data Flow

```
User Input (YAML/CLI)
    ↓
TERAG Adapter
    ↓
ARCHCODE API
    ↓
Simulation Engine → Bio-Metrics Engine
    ↓
Results (JSON/CSV/PNG)
    ↓
TERAG Validation → Report Generation
```

---

## 3. Simulation Engine (private)

### 3.1 Loop Extrusion Model

**Core Equation:**
```
λ = v_extrusion × τ_cohesin
```

Where:
- `λ`: Processivity (effective loop size)
- `v_extrusion`: NIPBL velocity (kb/min)
- `τ_cohesin`: WAPL lifetime (min)

**Implementation:**
- **Polymer Representation**: 1D linear chain with boundaries
- **Cohesin Dynamics**: Bidirectional movement, collision resolution
- **Boundary Recognition**: CTCF motif strength (0.0-1.0)
- **Unloading Probability**: WAPL-dependent stochastic process

### 3.2 Processivity Phases

**Phase 1: Collapse** (λ < 0.51)
- Unstable boundaries
- High cell-to-cell variation
- TAD collapse observed

**Phase 2: Transition** (0.51 ≤ λ < 1.0)
- Partial stability
- Stochastic boundary formation
- Intermediate variation

**Phase 3: Stable** (λ ≥ 1.0)
- Stable TAD boundaries
- Low variation
- Reproducible architecture

### 3.3 Bookmarking Dynamics

**Memory Accumulation:**
```
M(t) = M(t-1) × (1 - decay_rate) + bookmarking_fraction × CTCF_strength
```

**Restoration Probability:**
```
P_restore = bookmarking_fraction^α × epigenetic_strength^β
```

Where:
- `α ≈ 2-3`: Bookmarking exponent
- `β ≈ 1-2`: Epigenetic compensation exponent

### 3.4 Memory Channels

**Channel 1: CTCF Bookmarking**
- Direct CTCF binding memory
- Threshold: ~0.3-0.4

**Channel 2: Epigenetic Compensation**
- Histone modifications (H3K27me3, H3K9me3)
- Compensates for low bookmarking
- Strength: 0.0-1.0

**Channel 3: Multichannel Synergy**
- Combined effect: `M_total = M_CTCF + M_epigenetic × (1 - M_CTCF)`
- Critical surface: `M_total > 0.6` → Stable Memory

---

## 4. RS-Metrics Formal Spec

### 4.1 RS-09: Processivity Phase Diagram

**Input Parameters:**
- `processivity_range`: (min, max, steps) or list of values
- `cycles`: Number of simulation cycles per point
- `genome_len`: Genome length (bins)

**Output Metrics:**
- `stable_fraction`: Fraction of points in Stable phase
- `collapse_threshold`: Critical λ for Collapse → Transition
- `stable_threshold`: Critical λ for Transition → Stable
- `phase_map`: 2D array (processivity × stability)

**Formal Definition:**
```
RS-09(λ) = {
    Collapse    if λ < λ_collapse
    Transition  if λ_collapse ≤ λ < λ_stable
    Stable      if λ ≥ λ_stable
}
```

**Validation:**
- Unit test: `test_processivity_law`
- Regression: `test_rs09_phase_mission`
- Expected: CV < 0.01 (high reproducibility)

### 4.2 RS-10: Bookmarking Threshold

**Input Parameters:**
- `bookmarking_values`: List of bookmarking fractions [0.0, 0.1, ..., 1.0]
- `cycles`: Number of cycles
- `processivity`: Fixed processivity value

**Output Metrics:**
- `threshold`: Critical bookmarking fraction
- `jaccard_index`: Memory similarity metric
- `memory_regimes`: List of (bookmarking, regime) pairs

**Formal Definition:**
```
RS-10(bk) = {
    Drift       if bk < bk_threshold
    Memory      if bk ≥ bk_threshold
}
```

Where `bk_threshold ≈ 0.3-0.4` (percolation transition).

**Validation:**
- Unit test: `test_phase_transition_threshold`
- Regression: `test_rs10_bookmarking_mission`
- Expected: Threshold detection within ±0.05

### 4.3 RS-11: Multichannel Memory

**Input Parameters:**
- `bookmarking_range`: (min, max, steps)
- `epigenetic_range`: (min, max, steps)
- `cycles`: Number of cycles per point

**Output Metrics:**
- `memory_matrix`: 2D array (bookmarking × epigenetic)
- `phase_regimes`: Dict with counts (stable_memory, drift, partial)
- `critical_surface`: Boolean array (threshold detection)
- `phase_map`: Visualization data

**Formal Definition:**
```
RS-11(bk, epi) = {
    Stable Memory    if M_total(bk, epi) > 0.6
    Partial Memory   if 0.4 < M_total(bk, epi) ≤ 0.6
    Drift            if M_total(bk, epi) ≤ 0.4
}
```

Where:
```
M_total(bk, epi) = bk + epi × (1 - bk)
```

**Validation:**
- Unit test: `test_bookmarking_fraction_impact`
- Regression: `test_rs11_memory_mission`
- Expected: Critical surface detection, reproducible phase map

---

## 5. Memory Channels

### 5.1 Channel Architecture

```
┌─────────────────────────────────────────┐
│         Memory Channel System           │
├─────────────────────────────────────────┤
│                                         │
│  Channel 1: CTCF Bookmarking            │
│  ┌─────────────────────────────────┐    │
│  │ M_CTCF = f(bookmarking_fraction)│    │
│  │ Threshold: ~0.3-0.4            │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Channel 2: Epigenetic Compensation    │
│  ┌─────────────────────────────────┐    │
│  │ M_epi = f(epigenetic_strength)  │    │
│  │ Compensates low bookmarking     │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Channel 3: Multichannel Synergy       │
│  ┌─────────────────────────────────┐    │
│  │ M_total = M_CTCF + M_epi×(1-M)  │    │
│  │ Critical: M_total > 0.6        │    │
│  └─────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

### 5.2 Channel 1: CTCF Bookmarking

**Mechanism:**
- CTCF binding sites act as "bookmarks"
- Survive mitosis via protein-DNA interactions
- Restore architecture post-mitosis

**Mathematical Model:**
```
M_CTCF(t) = M_CTCF(t-1) × (1 - decay) + bookmarking_fraction × CTCF_strength
```

**Parameters:**
- `bookmarking_fraction`: 0.0-1.0 (fraction of boundaries with CTCF)
- `decay_rate`: ~0.1-0.2 per cell cycle
- `CTCF_strength`: 0.0-1.0 (binding affinity)

**Threshold Detection:**
- Percolation transition at `bookmarking_fraction ≈ 0.3-0.4`
- Below threshold: Drift (no memory)
- Above threshold: Memory (stable architecture)

### 5.3 Channel 2: Epigenetic Compensation

**Mechanism:**
- Histone modifications (H3K27me3, H3K9me3)
- DNA methylation patterns
- Compensate for low CTCF bookmarking

**Mathematical Model:**
```
M_epi = epigenetic_strength^β
```

Where `β ≈ 1-2` (non-linear compensation).

**Synergy with Channel 1:**
```
M_total = M_CTCF + M_epi × (1 - M_CTCF)
```

This ensures:
- If `M_CTCF` is high → `M_total ≈ M_CTCF` (CTCF dominates)
- If `M_CTCF` is low → `M_total ≈ M_epi` (epigenetic compensates)

### 5.4 Channel 3: Multichannel Critical Surface

**Critical Surface Definition:**
```
M_total(bk, epi) = 0.6
```

This defines a curve in (bookmarking, epigenetic) space:
- Below curve: Drift
- Above curve: Stable Memory
- Near curve: Partial Memory (stochastic)

**RS-11 Implementation:**
- Grid scan: 50×50 points
- For each point: Compute `M_total`, classify regime
- Generate phase map visualization
- Detect critical surface (contour at `M_total = 0.6`)

---

## 6. Data Flow Diagrams

### 6.1 RS-09 Processivity Flow

```
Input: processivity_range, cycles, genome_len
    ↓
For each processivity value λ:
    ├─ Initialize ExtrusionEngine(λ)
    ├─ Run cycles
    ├─ Compute stability_score
    └─ Classify phase (Collapse/Transition/Stable)
    ↓
Aggregate Results:
    ├─ stable_fraction
    ├─ collapse_threshold
    ├─ stable_threshold
    └─ phase_map (2D array)
    ↓
Output: rs09_results.json + phase_map.png
```

### 6.2 RS-10 Bookmarking Flow

```
Input: bookmarking_values, cycles, processivity
    ↓
For each bookmarking fraction bk:
    ├─ Initialize BookmarkingEngine(bk)
    ├─ Run cycles
    ├─ Compute memory_score (Jaccard index)
    └─ Classify regime (Drift/Memory)
    ↓
Threshold Detection:
    ├─ Find bk_threshold (percolation point)
    └─ Validate threshold (~0.3-0.4)
    ↓
Output: rs10_results.json + threshold_curve.png
```

### 6.3 RS-11 Multichannel Flow

```
Input: bookmarking_range, epigenetic_range, cycles
    ↓
Grid Scan (50×50):
    For each (bk, epi) point:
        ├─ Compute M_CTCF(bk)
        ├─ Compute M_epi(epi)
        ├─ Compute M_total = M_CTCF + M_epi×(1-M_CTCF)
        └─ Classify regime (Stable/Partial/Drift)
    ↓
Critical Surface Detection:
    ├─ Find contour M_total = 0.6
    ├─ Generate phase_map
    └─ Count regimes
    ↓
Output: rs11_results.json + memory_surface.png + phase_map.json
```

### 6.4 Pipeline Flow

```
CLI: python tools/run_pipeline.py run-pipeline --mode fast/full
    ↓
1. Unit Tests
    ├─ Core Physics (17 tests)
    └─ Memory Physics (6 tests)
    ↓
2. Regression Tests
    ├─ RS-09 regression
    ├─ RS-10 regression
    └─ RS-11 regression
    ↓
3. RS-09 Simulation
    └─ Generate phase diagram
    ↓
4. RS-10 Simulation
    └─ Detect bookmarking threshold
    ↓
5. RS-11 Simulation
    └─ Generate memory surface
    ↓
6. Real Hi-C Analysis
    ├─ Load .cool file
    ├─ Compute insulation
    ├─ Compute P(s)
    └─ Detect TAD boundaries
    ↓
7. ARCHCODE ↔ Real Comparison
    ├─ Align vectors (interpolation)
    ├─ Compute correlations
    └─ Generate comparison figure
    ↓
8. Report Generation
    └─ PIPELINE_SUMMARY_<timestamp>.md
```

---

## 7. Validation Protocol

### 7.1 Unit Testing

**Core Physics Tests (17 tests):**
- `test_cohesin_position_tracking`
- `test_processivity_law`
- `test_barrier_collision_detection`
- `test_weak_boundary_passage`
- `test_wapl_unloading_probability`
- `test_multiple_cohesins_independent`
- `test_extrusion_direction`
- `test_processivity_zero_velocity`
- `test_processivity_zero_lifetime`
- `test_boundary_strength_threshold`
- `test_processivity_linear_relationship`

**Memory Physics Tests (6 tests):**
- `test_bookmarking_accumulation`
- `test_memory_decay`
- `test_bookmarking_restoration_probability`
- `test_phase_transition_threshold`
- `test_boundary_phase_adjustment`
- `test_bookmarking_fraction_impact`

**Coverage Target:** >80% for core modules

### 7.2 Regression Testing

**RS-09 Regression:**
- Run 3 times, compare results
- Expected: CV < 0.01 (high reproducibility)
- Metric: `stable_fraction`, `collapse_threshold`

**RS-10 Regression:**
- Run 3 times, compare threshold
- Expected: Threshold within ±0.05
- Metric: `threshold`, `jaccard_index`

**RS-11 Regression:**
- Run 3 times, compare phase map
- Expected: Critical surface reproducible
- Metric: `phase_regimes`, `memory_matrix`

### 7.3 External Validation

**Real Hi-C Comparison:**
- Dataset: GM12878 (Rao et al., 2014)
- Resolution: 1 Mb
- Metrics:
  - P(s) correlation: Target >0.7
  - Insulation correlation: Target >0.7
  - TAD boundary overlap: Target >0.5

**Multi-Condition Benchmark (RS-13):**
- WT GM12878 (baseline)
- CdLS (SMC1A mutations)
- WAPL-KO (overactivation)
- Compare P(s), Insulation, APA scores

**scHi-C Robustness (RS-12):**
- Downsample to 100%, 30%, 10%, 3%, 1% coverage
- Compute P(s), Insulation, Boundary recall
- Validate ARCHCODE stability at low coverage

### 7.4 Validation Checklist

- [ ] All unit tests pass (17/17 core, 6/6 memory)
- [ ] All regression tests pass (CV < 0.01)
- [ ] RS-09 phase diagram matches expected thresholds
- [ ] RS-10 threshold detected (~0.3-0.4)
- [ ] RS-11 critical surface detected
- [ ] Real Hi-C correlations >0.7
- [ ] Pipeline completes without errors
- [ ] Reports generated successfully

---

## 8. Hi-C Integration (internal)

### 8.1 Data Format Support

**Cooler Format (.cool, .mcool):**
- Standard Hi-C data format
- Chromosome-resolved contact maps
- Resolution: 1 kb - 1 Mb

**Loading:**
```python
import cooler
c = cooler.Cooler('data/real_hic/GM12878_1000kb.cool')
matrix = c.matrix(balance=True)
```

**Fallback Mode:**
- If `cooltools` not available → Use basic insulation algorithm
- Simple local minima detection for TAD boundaries
- Reduced functionality but still usable

### 8.2 Analysis Pipeline

**Step 1: Load Hi-C Data**
- Read `.cool` file
- Extract chromosome (e.g., chr1)
- Balance matrix (ICE normalization)

**Step 2: Compute Metrics**
- Insulation score: `compute_insulation(matrix, window=500kb)`
- P(s) curve: `compute_ps_curve(matrix, max_distance=10Mb)`
- TAD boundaries: `detect_tad_boundaries(insulation_score)`

**Step 3: Comparison**
- Align ARCHCODE and Real Hi-C vectors (interpolation)
- Compute Pearson correlation
- Generate comparison figure

### 8.3 Comparison Algorithm

**Vector Alignment:**
```python
from scipy.interpolate import interp1d

def align_vectors(vec1, vec2, pos1, pos2):
    # Interpolate to common positions
    f = interp1d(pos1, vec1, kind='linear', fill_value='extrapolate')
    vec1_aligned = f(pos2)
    return vec1_aligned, vec2
```

**Normalization:**
- Z-score normalization before correlation
- Handle NaN/inf values
- Ensure same length vectors

**Correlation:**
```python
from scipy.stats import pearsonr

corr, p_value = pearsonr(vec1_aligned, vec2)
```

### 8.4 Output Formats

**JSON Results:**
```json
{
  "ps_correlation": 0.85,
  "insulation_correlation": 0.78,
  "tad_boundary_overlap": 0.62,
  "archcode_ps": [...],
  "real_ps": [...],
  "archcode_insulation": [...],
  "real_insulation": [...]
}
```

**Visualization:**
- 2×2 subplot:
  - Top-left: P(s) comparison (log-log)
  - Top-right: Insulation distribution (histogram)
  - Bottom-left: Insulation profiles (line plot)
  - Bottom-right: Correlation summary (table)

---

## 9. TERAG Cognitive Layer

### 9.1 Architecture

**TERAG Adapter:**
- Bridge between TERAG (Logic) and ARCHCODE (Physics)
- Converts YAML missions to ARCHCODE API calls
- Returns standardized JSON results

**Mission Types:**
- `memory_scan`: RS-11 multichannel memory
- `processivity_phase`: RS-09 phase diagram
- `bookmarking_threshold`: RS-10 threshold detection
- `real_hic_benchmark`: RS-13 multi-condition

### 9.2 Mission Format

**YAML Structure:**
```yaml
mission:
  id: "RS-11-MEM-INTEGRATION"
  name: "Multi-Channel Memory Phase Scan"
  description: "Detecting the bookmarking threshold via Adapter."

parameters:
  mission_type: "memory_scan"
  genome_len: 2000
  processivity: 250
  bookmarking_min: 0.0
  bookmarking_max: 1.0
```

### 9.3 Adapter Implementation

**Class: `ArchcodeAdapter`**
```python
class ArchcodeAdapter:
    def __init__(self, mode='fast'):
        self.mode = mode
    
    def run_mission(self, mission_config: dict) -> dict:
        mission_type = mission_config.get("parameters", {}).get("mission_type")
        # Route to appropriate handler
        # Return standardized JSON
```

**Result Format:**
```json
{
  "status": "success",
  "mission_id": "RS-11-MEM-INTEGRATION",
  "execution_time": 0.51,
  "mode": "fast",
  "data": {
    "scan_results": [...],
    "threshold_detected": true
  }
}
```

### 9.4 Validation & Explanation

**TERAG Validator:**
- Checks result format
- Validates metrics (thresholds, correlations)
- Generates explanations

**Explanation Generation:**
- Natural language summaries
- Phase diagram interpretations
- Clinical relevance (CdLS, WAPL-KO)

---

## 10. Extension Modules

### 10.1 RS-12: scHi-C Robustness

**Purpose:** Validate ARCHCODE stability with sparse/low-coverage data

**Method:**
- Downsample Hi-C matrix (Poisson/binomial)
- Coverage levels: 100%, 30%, 10%, 3%, 1%
- Compute P(s), Insulation, Boundary recall
- Compare with 100% reference

**Output:**
- `RS12_scihic_robustness.json`
- Figures: `RS12_ps_vs_coverage.png`, `RS12_insulation_vs_coverage.png`

### 10.2 RS-13: Multi-Condition Benchmark

**Purpose:** Compare ARCHCODE predictions across biological conditions

**Conditions:**
- WT GM12878 (baseline)
- CdLS (SMC1A mutations, low processivity)
- WAPL-KO (overactivation, high processivity)

**Metrics:**
- P(s) scaling
- Insulation profiles
- Boundary strength
- APA (Aggregate Peak Analysis) scores

**Output:**
- `RS13_summary.json`
- Per-condition comparisons: `RS13_<condition>_comparison.json`
- Figures: `RS13_ps_<condition>.png`, `RS13_insulation_<condition>.png`

### 10.3 Publication Figures Module

**Figure 2: RS-09 Processivity Phase Diagram**
- Heatmap: stability vs processivity
- Contour lines: phase boundaries
- Annotations: Collapse/Transition/Stable thresholds

**Figure 3: RS-10/RS-11 Memory Architecture**
- RS-10: Jaccard/Memory vs bookmarking_fraction
- RS-11: 2D surface (bookmarking × epigenetic_strength)
- Critical surface overlay

**Figure 4: Real Hi-C Benchmark**
- 2×2 subplot:
  - P(s) real vs ARCHCODE (log-log)
  - Insulation distribution (histogram)
  - Insulation profiles (line plot)
  - Correlation summary (table)

### 10.4 Future Extensions

**Planned Modules:**
- Multi-species universal physics
- Advanced variant impact analysis
- Synthetic chromatin design tools
- Real-time visualization
- Interactive phase diagrams

**Research Directions:**
- Full 3D polymer dynamics
- Chromosome-scale simulations
- Machine learning integration
- Clinical diagnostic tools

---

## Appendix A: Mathematical Notation

- `λ`: Processivity (effective loop size)
- `v_extrusion`: NIPBL velocity (kb/min)
- `τ_cohesin`: WAPL lifetime (min)
- `bk`: Bookmarking fraction (0.0-1.0)
- `epi`: Epigenetic strength (0.0-1.0)
- `M_CTCF`: CTCF bookmarking memory
- `M_epi`: Epigenetic compensation memory
- `M_total`: Total multichannel memory
- `P(s)`: Contact probability at distance s
- `CV`: Coefficient of variation

---

## Appendix B: File Structure

```
ARCHCODE/
├── src/
│   ├── archcode/
│   │   ├── cli.py
│   │   ├── simulation/      # Private: Loop extrusion engine
│   │   ├── analysis/        # Bio-metrics engine
│   │   ├── rs09/            # RS-09 implementation
│   │   ├── rs10/            # RS-10 implementation
│   │   ├── rs11/            # RS-11 implementation
│   │   ├── real_hic/        # Hi-C integration
│   │   └── comparison/     # ARCHCODE ↔ Real comparison
│   └── integration/
│       └── archcode_adapter.py  # TERAG adapter
├── configs/
│   ├── pipeline_fast.yaml
│   └── pipeline_full.yaml
├── tools/
│   ├── run_pipeline.py
│   └── build_validation_report.py
├── experiments/
│   ├── run_RS12_scihic_robustness.py
│   └── run_RS13_multi_condition_benchmark.py
├── tests/
│   ├── unit/
│   └── regression/
├── docs/
│   ├── TECH_SPEC_ARCHCODE.md
│   └── reports/
└── data/
    ├── real_hic/
    └── output/
```

---

## Appendix C: Configuration Reference

**Pipeline Fast Mode:**
```yaml
rs09:
  grid_size: 11
  cycles: 10

rs10:
  bookmarking_values: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
  cycles: 10

rs11:
  grid_size: 11
  cycles: 10
```

**Pipeline Full Mode:**
```yaml
rs09:
  grid_size: 50
  cycles: 50

rs10:
  bookmarking_values: [0.0, 0.1, ..., 1.0]  # 11 values
  cycles: 50

rs11:
  grid_size: 50
  cycles: 50
```

---

**End of Technical Specification**

*This document is internal and private. For public documentation, see `README.md`.*



