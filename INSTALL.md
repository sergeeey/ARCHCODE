# ARCHCODE Installation Guide

## Quick Start

### Option 1: pip (Recommended)

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Option 2: Conda

```bash
conda env create -f environment.yml
conda activate archcode
```

### Option 3: Auto Setup Script

```bash
python setup_archcode.py
```

## Core Dependencies

### Essential (Must Have)
- `numpy`, `scipy`, `numba` - Scientific computing
- `pandas`, `pyyaml`, `tqdm` - Data handling
- `matplotlib`, `seaborn`, `plotly` - Visualization

### ML/DL Stack
- `torch` - Deep learning
- `einops` - Tensor operations
- `transformers` - Pre-trained models

### Bioinformatics
- `biopython` - DNA sequence handling
- `pyfaidx` - FASTA access
- `pyBigWig` - BigWig file reading
- `cooler`, `cooltools` - Hi-C data
- `pybedtools` - BED file operations
- `regex` - Pattern matching

### Architecture
- `pydantic` - Configuration validation
- `graphviz` - Diagrams

## Troubleshooting

### Windows Issues

Some bioinformatics packages may require:
- Visual C++ Build Tools
- Conda (for cooler, pyBigWig)

### Alternative Installation

If some packages fail, install core stack first:

```bash
pip install numpy scipy numba pandas pyyaml tqdm matplotlib seaborn plotly pydantic
```

Then install bioinformatics packages via conda:

```bash
conda install -c bioconda biopython pyfaidx pybigwig cooler cooltools pybedtools
```

## Verification

```python
python -c "import numpy, scipy, numba, pandas, yaml, torch, matplotlib, biopython, pydantic; print('✅ All OK')"
```







