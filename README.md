# ARCHCODE v1.0

**Full-Stack Genome Architecture Simulation**

ARCHCODE is an engineering model of non-coding 3D genome architecture, integrated with mitotic nucleus simulator (Cellular Kernel).

## Purpose

ARCHCODE simulates:
- **Loop extrusion** → TAD formation
- **Boundary stability** → Cell-to-cell variation
- **Mitotic tension** → Segregation errors
- **Epigenetic dynamics** → Topology changes

## Architecture

```
DNA sequence → chromatin topology → mitotic tension → SAC consensus → anaphase decision
```

Model = ARCHCODE Core + Cellular Kernel + TE Grammar + Non-B Logic + LTL Verification

## VIZIR Framework

ARCHCODE follows **VIZIR 2.0** principles:
- **Validation**: Test all modules
- **Integration**: Modular architecture
- **Zero-trust**: No magic constants, all in config
- **Iterative Refinement**: Version control, changelogs
- **Reproducibility**: Integrity ledger, provenance tracking

See `.vizir/` for:
- `integrity_ledger.json` - Configuration checksums
- `provenance.log` - Parameter origin tracking

## Directory Layout

```
ARCHCODE_v1.0/
├── .vizir/                    # VIZIR integrity & provenance
│   ├── integrity_ledger.json
│   └── provenance.log
│
├── bin/                       # Target: C++/CUDA executables
│   ├── archcode_engine        # Loop extrusion kernel
│   ├── twist_calculator       # Supercoiling calculator
│   └── topology_analyzer      # TAD analyzer
│
├── lib/                       # Target: Shared libraries
│
├── config/                    # YAML configurations
│   ├── physical/              # Physical layer Unknowns (P1-P3)
│   │   ├── P1_extrusion_symmetry.yaml
│   │   ├── P2_supercoiling.yaml
│   │   └── P3_cohesin_loading.yaml
│   ├── structural/            # Structural layer Unknowns (S1-S3)
│   │   ├── S1_tad_boundaries.yaml
│   │   ├── S2_te_motifs.yaml
│   │   └── S3_nonb_dna.yaml
│   ├── logical/               # Logical layer Unknowns (L1-L3)
│   │   ├── L1_zdna_formation.yaml
│   │   ├── L2_epigenetic_compiler.yaml
│   │   └── L3_kinetochore_tension.yaml
│   └── [module configs]       # Module-specific configs
│
├── specs/                     # Research Specifications
│   ├── RS-01.md              # Loop Extrusion Engine
│   ├── RS-02.md              # TE Motif Dictionary
│   ├── RS-03.md              # Non-B DNA Barriers
│   ├── RS-04.md              # Mitotic Tension Bridge
│   ├── RS-05.md              # Topology Analyzer
│   ├── RS-06.md              # Boundary Stability Predictor
│   └── RS-07.md              # Boundary Collapse Simulation
│
├── src/                       # Python implementation (v1.0-alpha)
│   ├── archcode_core/        # Loop Extrusion Engine
│   ├── te_grammar/           # TE Motif Dictionary
│   ├── nonB_logic/           # Non-B DNA Barriers
│   ├── epigenetic_compiler/  # Methylation Compiler
│   ├── genome_to_tension/     # Tension Mapper
│   ├── boundary_stability/    # Stability Predictor
│   └── risk_matrix/          # Risk Analyzer
│
├── cellular_kernel/           # SAC Consensus Engine (integrated)
│   ├── src/agents.py         # Kinetochore agents
│   ├── src/bus.py            # MCC signal bus
│   ├── src/kernel.py         # APC/C controller
│   └── src/verifier.py       # LTL verifier
│
├── mcp_genomic_data/          # MCP Server for genomic data
│   ├── server.py              # MCP server
│   ├── tools.py              # Genomic data tools
│   └── setup_mcp.py          # Cursor setup
│
├── risk_matrix/              # VIZIR Risk Matrix
│   ├── P1.yaml, P2.yaml, P3.yaml
│   ├── S1.yaml, S2.yaml, S3.yaml
│   └── L1.yaml, L2.yaml, L3.yaml
│
├── data/                      # Data directory
│   ├── input/                # Input genomic data
│   └── output/               # Simulation results
│
├── examples/                  # Usage examples
├── tests/                     # Unit tests
└── docs/                      # Documentation (RFC-style)
```

## Modules

### ARCHCODE Core
**Loop Extrusion Engine** - 1D simulation of TAD formation
- Asymmetric extrusion
- Supercoiling dynamics
- Cohesin loading (NIPBL sites)

### TE Grammar
**Transposon Motif Dictionary** - TE effects on boundaries
- WAPL-recruiting sequences
- Boundary-stabilizing motifs
- Effect quantification

### Non-B Logic
**Energy Barrier Models** - G4, Z-DNA, R-loops
- Formation conditions
- Barrier strength
- Hierarchy resolution

### Epigenetic Compiler
**Methylation Topology Compiler** - CpG methylation effects
- CTCF inactivation threshold
- Boundary collapse
- Topology updates

### Genome-to-Tension Bridge
**3D Topology → Mitotic Tension** - Risk mapping
- Boundary stability → merotelic risk
- Tension calibration (Aurora B)
- Cellular kernel integration

### Boundary Stability Predictor
**TAD Boundary Stability** - Cell-to-cell variation
- Multiplicative stability model
- Factor aggregation
- Category prediction (stable/variable/intermediate)

### Boundary Collapse Simulator
**TAD Boundary Collapse** - Collapse dynamics
- Collapse triggers (methylation, mutations, TE)
- Consequences (enhancer hijacking, oncogenic contacts)
- Risk scoring

### Cellular Kernel
**SAC Consensus Engine** - Mitotic checkpoint
- Kinetochore agents
- MCC signal bus
- LTL verification

## Engineering Unknowns

### Physical Layer (P1-P3)
- **P1**: Loop extrusion asymmetry mechanism
- **P2**: Supercoiling dynamics
- **P3**: Cohesin loading site selection

### Structural Layer (S1-S3)
- **S1**: TAD boundary determinism
- **S2**: TE motif effects
- **S3**: Non-B DNA barrier formation

### Logical Layer (L1-L3)
- **L1**: Z-DNA formation logic
- **L2**: Epigenetic compiler threshold
- **L3**: Kinetochore tension calibration

See `config/physical/`, `config/structural/`, `config/logical/` for detailed configurations.

## Research Specifications

- **RS-01**: Loop Extrusion Engine (P1, P2, P3)
- **RS-02**: TE Motif Dictionary (S2)
- **RS-03**: Non-B DNA Barriers (S3, L1)
- **RS-04**: Mitotic Tension Bridge (L2, L3)
- **RS-05**: Topology Analyzer (S1)
- **RS-06**: Boundary Stability Predictor (B1)
- **RS-07**: Boundary Collapse Simulation (B2)

See `specs/` for detailed specifications.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup MCP Genomic Data Server (optional)
python mcp_genomic_data/setup_mcp.py
```

## Configuration

All parameters configured via YAML:

### Engineering Unknowns
- `config/physical/P1_extrusion_symmetry.yaml`
- `config/physical/P2_supercoiling.yaml`
- `config/physical/P3_cohesin_loading.yaml`
- `config/structural/S1_tad_boundaries.yaml`
- `config/structural/S2_te_motifs.yaml`
- `config/structural/S3_nonb_dna.yaml`
- `config/logical/L1_zdna_formation.yaml`
- `config/logical/L2_epigenetic_compiler.yaml`
- `config/logical/L3_kinetochore_tension.yaml`

### Module Configs
- `config/archcode_engine.yaml` - Loop extrusion
- `config/te_grammar.yaml` - TE motifs
- `config/nonB_logic.yaml` - Energy barriers
- `config/epigenetic_compiler.yaml` - Methylation
- `config/genome_to_tension.yaml` - Tension mapping
- `config/boundary_stability.yaml` - Stability model
- `config/boundary_collapse.yaml` - Collapse simulator

## Usage

### Basic Pipeline

```python
from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs

# Load configurations
archcode_config, stability_config = load_pipeline_configs()

# Initialize pipeline
pipeline = ARCHCODEPipeline(
    archcode_config=archcode_config,
    stability_config=stability_config,
)

# Add boundaries
pipeline.add_boundary(position=100000, strength=0.9, barrier_type="ctcf")

# Analyze stability
prediction = pipeline.analyze_boundary_stability(
    boundary=pipeline.boundaries[0],
    methylation_level=0.2,
)

print(f"Stability: {prediction.stability_category}")
```

### MCP Genomic Data

```python
from mcp_genomic_data.tools import fetch_ctcf_chipseq

# Fetch CTCF ChIP-seq data
ctcf_data = await fetch_ctcf_chipseq("chr1", 1000000, 2000000)
```

## Development

### VIZIR Principles
- **Validation**: Test all modules (`pytest`)
- **Integration**: Modular architecture
- **Zero-trust**: No magic constants, all in config
- **Iterative Refinement**: Version control, changelogs
- **Reproducibility**: Integrity ledger, provenance tracking

### Code Style
- Production-quality Python
- Type hints
- RFC-style Markdown documentation
- YAML-driven configuration

### Testing

```bash
# Run tests
pytest

# Check coverage
pytest --cov=src

# Lint
ruff check src/
```

## Version

**1.0.0-alpha**

Current implementation: Python reference simulator  
Target architecture: C++/CUDA kernel (see `bin/`)

## License

MIT

## References

- ARCHCODE Mission: `ARCHCODE_MISSION.md`
- Architecture: `docs/ARCHITECTURE.md`
- MCP Integration: `docs/MCP_GENOMIC_DATA_INTEGRATION.md`
