# 🔬 ARCHCODE

Reproducible physics-based framework for 3D genome architecture and chromatin loop dynamics

**Author / Maintainer:** Boiko S.V. (Sergey Boiko)  
**Project type:** Scientific Software / Computational Genomics / Chromatin Modeling  
**License:** MIT  

---

## 📐 Overview

ARCHCODE is a reproducible, physics-based framework for 3D genome architecture, loop extrusion dynamics, and epigenetic memory.

It provides:

- A modular simulation core (loop extrusion, bookmarking, memory channels)
- RS-09 / RS-10 / RS-11 evaluation suites
- A unified reproducibility-oriented pipeline design (tests → analysis → figures → report)
- Real Hi-C data ingestion & comparison interfaces
- Publication-oriented outputs for scientific use

---

## 🔬 Scientific Motivation

Chromatin architecture is highly dynamic yet capable of transmitting structural memory across cell cycles.  
ARCHCODE is designed to model these processes using:

- Loop extrusion physics
- Boundary elements & anchors
- Bookmarking-based memory channels
- Processivity phase diagrams
- Threshold detection for epigenetic inheritance

The system is intended to support both mechanistic studies and data-driven validation.

---

## 🚀 Key Features

### Loop Extrusion Engine

- Polymer representation  
- Bidirectional SMC movement  
- Anchor recognition & pause probabilities  
- Collision resolution  

(Full implementation details are kept internal; the public interface focuses on reproducibility and interoperability.)

### Benchmark Suite (RS-Series)

| Module | Purpose                                                   |
|--------|-----------------------------------------------------------|
| RS-09  | Processivity phase diagram & stability analysis           |
| RS-10  | Bookmarking threshold & inheritance limit                 |
| RS-11  | Multichannel memory & critical surface detection          |
| RS-12  | Sci-Hi-C validation *(planned)*                           |
| RS-13  | Multi-condition architectural benchmarking *(planned)*    |

### Bio-Metrics Engine

- Insulation score  
- TAD boundary detection  
- Compartment-like eigenvector analysis  
- P(s) scaling  
- Pearson correlation to real Hi-C maps  

### Real Hi-C Integration

ARCHCODE is designed to interface with real Hi-C datasets and contact maps.

Planned support includes:

- `.cool` / `.mcool` files  
- GM12878 (Rao et al., 2014)  
- WAPL-KO  
- CdLS (SMC1A mutations)  

A fallback mode is intended to work without heavy external dependencies, enabling lightweight exploratory runs.

---

## 📦 Reproducible Science Pipeline

A unified science pipeline is under active development.

The planned interface:

**Fast mode (quick exploratory runs):**

```bash
python tools/run_pipeline.py run-pipeline --mode fast
```

**Full mode (publication-scale runs):**

```bash
python tools/run_pipeline.py run-pipeline --mode full
```

The pipeline is designed to include:

* Unit tests
* Regression tests
* RS-09, RS-10, RS-11 evaluation
* Real Hi-C analysis
* Model ↔ Data comparison
* Summary report generation

Planned output locations:

* `data/output/pipeline_runs/`
* `docs/reports/`
* `figures/pipeline/`

---

## 📊 Outputs

ARCHCODE is designed to generate:

* Phase diagrams
* Threshold curves
* Memory surfaces
* TAD boundaries
* Insulation profiles
* P(s) curves
* Comparative figures against real Hi-C

These outputs are intended for both exploratory analysis and publication-oriented figures.

---

## 🧩 Project Structure

```
ARCHCODE/
├─ src/archcode/
│  ├─ simulation/
│  ├─ analysis/
│  ├─ rs09/
│  ├─ rs10/
│  ├─ rs11/
│  ├─ real_hic/
│  ├─ comparison/
│  └─ cli.py
├─ configs/
├─ tools/
│  └─ run_pipeline.py
├─ tests/
├─ docs/
├─ data/
├─ LICENSE
└─ README.md
```

The repository currently exposes the structural skeleton and public interfaces.

Core engine implementations and advanced modules remain private.

---

## 🔬 Ongoing Research

ARCHCODE is under active development and internal evaluation across several research directions.

Preliminary internal tests suggest reproducible structural patterns and stable architectural regimes.

Additional modules are under validation and will be announced in future scientific releases.

---

## 🛠️ Future Modules (Private / In Development)

These components are currently in private research stage and are not included in the public release:

* Multi-species universal physics
* Advanced variant impact analysis (structural variation, regulatory rewiring)
* Synthetic chromatin architecture design tools

---

## ✍️ Citation

If you use ARCHCODE in scientific work, please cite:

> Boiko S.V. (2025).  
> ARCHCODE – physics-based reproducible model of 3D genome architecture and chromatin loop dynamics.  
> GitHub: [https://github.com/sergeeey/ARCHCODE](https://github.com/sergeeey/ARCHCODE)

---

## 📬 Contact

For collaboration inquiries or research discussions:

✉️ **[sergeikuch80@gmail.com](mailto:sergeikuch80@gmail.com)**

---

**About**

ARCHCODE – reproducible physics-based model of 3D genome architecture and chromatin loop dynamics.
