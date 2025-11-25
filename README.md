ARCHCODE
Reproducible physics-based model of 3D genome architecture and chromatin loop dynamics

Author / Maintainer: Boiko S.V. (Sergey Boiko)
Project type: Scientific Software / Computational Genomics / Chromatin Modeling
License: MIT

📐 Overview

ARCHCODE is a fully reproducible, physics-based simulation engine for
3D genome architecture, loop extrusion dynamics, and epigenetic memory.

It provides:

A modular simulation core (loop extrusion, bookmarking, memory channels)

RS-09 / RS-10 / RS-11 benchmark suites

A complete reproducibility pipeline (tests → analysis → figures → report)

Real Hi-C data ingestion & comparison

Publication-ready outputs for scientific use

🔬 Scientific Motivation

Chromatin architecture is highly dynamic yet capable of transmitting structural memory across cell cycles. ARCHCODE models these processes using:

Loop extrusion physics

Boundary elements & anchors

Bookmarking-based memory channels

Processivity phase diagrams

Threshold detection for epigenetic inheritance

The system is designed to support both mechanistic studies and data-driven validation.

🚀 Key Features
1. Loop Extrusion Engine

Polymer representation

Bidirectional SMC movement

Anchor recognition & pause probabilities

Collision resolution

2. Benchmark Suite (RS-Series)
Module	Purpose
RS-09	Processivity phase diagram and stability analysis
RS-10	Bookmarking threshold and inheritance limit
RS-11	Multichannel memory & critical surface detection
RS-12	Sci-Hi-C validation
RS-13	Multi-condition architectural benchmarking
3. Bio-Metrics Engine

Insulation score

TAD boundary detection

Compartment-like eigenvector analysis

P(s) scaling

Pearson correlation to real Hi-C maps

4. Real Hi-C Integration

Compatible with:

.cool / .mcool files

GM12878 (Rao et al.)

WAPL-KO

CdLS (SMC1A mutations)

Fallback mode works without external dependencies.

📦 Reproducible Science Pipeline

Run the entire validation stack with one command:

Fast mode (15–30 seconds)
python tools/run_pipeline.py run-pipeline --mode fast

Full mode (multi-hour publication mode)
python tools/run_pipeline.py run-pipeline --mode full


Pipeline performs:

Unit tests

Regression tests

RS-09, RS-10, RS-11

Real Hi-C analysis

Model ↔ Data comparison

Summary report generation

Reports saved to:

docs/reports/PIPELINE_SUMMARY_<timestamp>.md

📊 Outputs

ARCHCODE automatically generates:

Phase diagrams

Threshold curves

Memory surfaces

TAD boundaries

Insulation profiles

P(s) curves

Comparative figures against real Hi-C

All results are saved to:

data/output/pipeline_runs/
figures/pipeline/

🧩 Project Structure
ARCHCODE/
  ├─ src/archcode/
  │   ├─ simulation/
  │   ├─ analysis/
  │   ├─ rs09/
  │   ├─ rs10/
  │   ├─ rs11/
  │   ├─ real_hic/
  │   ├─ comparison/
  │   └─ cli.py
  ├─ configs/
  ├─ tools/
  ├─ tests/
  ├─ docs/
  ├─ data/
  ├─ LICENSE
  └─ README.md

✍️ Citation

If you use ARCHCODE in scientific work, please cite:

Boiko S.V. (2025).
ARCHCODE – physics-based reproducible model of 3D genome architecture and chromatin loop dynamics.
GitHub: https://github.com/sergeeey/ARCHCODE

🤝 Contributions

PRs are welcome.
Bug reports → GitHub Issues.
For collaboration inquiries: add your email here if you want.
