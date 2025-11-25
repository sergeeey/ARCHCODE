# 🔬 ARCHCODE  
**Reproducible physics-based model of 3D genome architecture and chromatin loop dynamics**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-publication--ready-green)
![Reproducibility](https://img.shields.io/badge/reproducibility-verified-brightgreen)

---

### **Author / Maintainer:** **Boiko S.V. (Sergey Boiko)** **Project type:** Scientific Software / Computational Genomics / Chromatin Modeling  
**License:** MIT  

---

## 📐 Overview

ARCHCODE is a fully reproducible, physics-based simulation engine for 3D genome architecture, loop extrusion dynamics, and epigenetic memory.

It provides:
- A modular simulation core (loop extrusion, bookmarking, memory channels)  
- RS-09 / RS-10 / RS-11 benchmark suites  
- A complete reproducibility pipeline (tests → analysis → figures → report)  
- Real Hi-C data ingestion & comparison  
- Publication-ready outputs for scientific use  

---

## 🔬 Scientific Motivation

Chromatin architecture is highly dynamic yet capable of transmitting structural memory across cell cycles.  
ARCHCODE models these processes using:
- Loop extrusion physics  
- Boundary elements & anchors  
- Bookmarking-based memory channels  
- Processivity phase diagrams  
- Threshold detection for epigenetic inheritance  

The system is designed to support both mechanistic studies and data-driven validation.

---

## 🚀 Key Features

### **Loop Extrusion Engine**
- Polymer representation  
- Bidirectional SMC movement  
- Anchor recognition & pause probabilities  
- Collision resolution  

### **Benchmark Suite (RS-Series)**
| Module | Purpose |  
|--------|---------|  
| RS-09 | Processivity phase diagram & stability analysis |  
| RS-10 | Bookmarking threshold & inheritance limit |  
| RS-11 | Multichannel memory & critical surface detection |  
| RS-12 | Sci-Hi-C validation |  
| RS-13 | Multi-condition architectural benchmarking |  

### **Bio-Metrics Engine**
- Insulation score  
- TAD boundary detection  
- Compartment-like eigenvector analysis  
- P(s) scaling  
- Pearson correlation to real Hi-C maps  

### **Real Hi-C Integration**
Supports:
- `.cool` / `.mcool` files  
- GM12878 (Rao et al., 2014)  
- WAPL-KO  
- CdLS (SMC1A mutations)  

Fallback mode works without external dependencies.

---

## 📦 Reproducible Science Pipeline

Run the full validation workflow with one command:

**Fast mode (15–30 seconds):**
```bash
python tools/run_pipeline.py run-pipeline --mode fast
````

**Full mode (multi-hour publication mode):**

```bash
python tools/run_pipeline.py run-pipeline --mode full
```

**Pipeline includes:**

  - Unit tests
  - Regression tests
  - RS-09, RS-10, RS-11
  - Real Hi-C analysis
  - Model ↔ Data comparison
  - Summary report generation

**Results saved to:**

  - `data/output/pipeline_runs/`
  - `docs/reports/`
  - `figures/pipeline/`

-----

## 📊 Outputs

ARCHCODE automatically generates:

  - Phase diagrams
  - Threshold curves
  - Memory surfaces
  - TAD boundaries
  - Insulation profiles
  - P(s) curves
  - Comparative figures against real Hi-C

-----

## 🧩 Project Structure

```text
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
├─ tests/
├─ docs/
├─ data/
├─ LICENSE
└─ README.md
```

-----

## 🔬 Ongoing Research

ARCHCODE is actively used in several research directions.  
Preliminary findings indicate promising reproducible structural patterns and stable architectural regimes.

Additional modules are under validation and will be announced in future scientific releases.

### 🛠️ Future Modules (Private / In Development)

These components are currently in private research stage and not included in the public release:

  - Multi-species universal physics
  - Variant Impact Predictor (disease-associated SV analysis)
  - Synthetic architecture design tools

-----

## ✍️ Citation

If you use ARCHCODE in scientific work, please cite:

```text
Boiko S.V. (2025). 
ARCHCODE – physics-based reproducible model of 3D genome architecture and chromatin loop dynamics.
GitHub: [https://github.com/sergeeeyy/ARCHCODE](https://github.com/sergeeeyy/ARCHCODE)
```

-----

## 📬 Contact

For collaboration inquiries or research discussions:  
✉️ sergeikuch80@gmail.com

