# Stress Biology & ATP-Driven Mutagenesis

**Status:** 🚧 Work in Progress (Month 0)  
**Hypothesis:** Cellular stress (ATP deficit) drives somatic mutation rate  
**Inspired by:** Bilinsky 2025 (Biomath) — radiosensitivity R/Q states

---

## Quick Start

### 1. Read the Spec

```bash
cat SPEC.md          # Technical specification
cat HYPOTHESIS.md    # Detailed hypotheses & kill criteria
cat ROADMAP.md       # 6-month timeline
```

### 2. Setup Environment

```bash
# Python dependencies (TODO: create requirements.txt)
pip install pandas numpy scipy matplotlib seaborn

# R dependencies
# install.packages(c("jsonlite", "boot", "ggplot2"))
```

### 3. Data Collection (Month 1)

```bash
# Download TCGA mutation data
python scripts/download_tcga.py --tissue COAD --output data/tcga_mutations.csv

# Extract mutation rates from MAF files
python scripts/extract_mutation_rates.py --maf data/raw/COAD.maf --output data/processed/rates.csv
```

### 4. Analysis (Month 2-3)

```bash
# Correlation analysis (H0)
Rscript scripts/correlation_analysis.R --data data/merged.csv --output results/h0_stats.json
```

---

## Project Structure

```
stress_biology/
├── SPEC.md              # Full technical specification
├── HYPOTHESIS.md        # Hypotheses (H0, H1, H2, H3) + kill criteria
├── ROADMAP.md           # 6-month timeline & milestones
├── README.md            # This file
├── scripts/             # Analysis scripts
│   ├── download_tcga.py
│   ├── extract_mutation_rates.py
│   └── correlation_analysis.R
├── data/                # Data files (gitignored)
│   ├── raw/            # Downloaded TCGA MAF files
│   └── processed/      # Parsed mutation rates
├── results/             # Analysis outputs (gitignored)
│   ├── h0_stats.json
│   └── fig1_correlation.png
└── docs/                # Additional documentation
```

---

## Core Hypothesis (H0)

> **Doubling time inversely correlates with mutation rate** (r > 0.4, p < 0.01)

**Mechanism:**  
Fast-dividing cells → more time in state Q (low ATP) → vulnerable nuclear envelope → more replication errors

**Kill Criterion:**  
r < 0.3 after 3 months → hypothesis killed, publish negative result

---

## Timeline

| Month | Task | Checkpoint |
|-------|------|-----------|
| 1 | Data collection (TCGA + literature) | n > 1000 samples |
| 2 | H1: Tissue-specific rates | p < 0.05? |
| 3 | **H0: Main correlation** | **r < 0.3 → KILL** |
| 4 | H3: ATP proxy | r > 0.3? |
| 5 | Manuscript draft | — |
| 6 | Bilinsky email + collaboration | — |

---

## Contact for Collaboration

**After Experiment 1 results:**

Email Bilinsky (Biomath 2025 author) with:
- Preliminary results (H0 correlation)
- Hypothesis doc
- Proposal for wet-lab validation (if H0 passed)

**RIIS Connection:** Both RIIS Fellows → natural collaboration pathway

---

## Related Work

- **Bilinsky 2025** (Biomath) — R/Q states, ATP-driven radiosensitivity
- **ARCHCODE v1** — 3D chromatin structure (closed, negative result)
- **Sender 2016** (Cell) — tissue proliferation rates reference

---

## License

MIT (code), CC-BY-4.0 (data/docs)

---

**Current Status:** Specifications written, scripts stubbed, ready for Month 1 data collection.

**Next Step:** Test TCGA API access, download first 10 samples.
