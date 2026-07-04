# AlphaGenome Research Repository Analysis

**Date**: 2026-02-03
**Repository**: https://github.com/google-deepmind/alphagenome_research
**Purpose**: Integration context for ARCHCODE validation

---

## Overview

AlphaGenome is a unified DNA sequence model (Nature 2026) that analyzes DNA sequences up to 1M bp with single base-pair resolution. Outputs include:

- Gene expression (RNA-seq, CAGE, PRO-cap)
- Splicing patterns
- Chromatin features (ATAC, DNase, ChIP)
- **Contact maps** (key for ARCHCODE integration)

---

## Model Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ SequenceEncoder │ ──► │ TransformerTower │ ──► │ SequenceDecoder │
│  (Conv blocks)  │     │  (9 layers +     │     │   (UpRes)       │
│   1bp → 128bp   │     │  pairwise attn)  │     │   128bp → 1bp   │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌────────────────┐
                        │ Pair Activations │
                        │  (Contact Maps)  │
                        └────────────────┘
```

### Key Components

1. **SequenceEncoder**: Convolutional downsampling (1bp → 2 → 4 → 8 → 16 → 32 → 64 → 128bp)
2. **TransformerTower**: 9 attention blocks with interleaved pairwise updates
3. **SequenceDecoder**: Transposed convolutions back to 1bp
4. **Heads**: Separate prediction heads for each output type

---

## Contact Map Variant Scoring

From `contact_map.py` - implements Zhou 2022 (Orca) strategy:

```python
# "1-Mb structural impact score"
# Average absolute log fold change of interactions
# between the disruption position and all other positions

abs_diff = jnp.abs(alt - ref).mean(axis=0)
output = abs_diff[jnp.argmax(masks), :]
```

**Reference**: https://doi.org/10.1038/s41588-022-01065-4

---

## Regression Metrics

From `regression_metrics.py` - matches our ARCHCODE implementation:

```python
# State accumulation for metrics
RegressionState:
    pearsonr        # Standard Pearson R
    pearsonr_log1p  # Pearson R on log1p-transformed values
    sq_error        # Squared error for MSE
    abs_error       # Absolute error for MAE
    count           # Sample count

# Final metrics
{
    'pearsonr': _pearsonr_result(state.pearsonr),
    'pearsonr_log1p': _pearsonr_result(state.pearsonr_log1p),
    'mse': state.sq_error / state.count,
    'mae': state.abs_error / state.count,
}
```

### Pearson R Implementation

```python
def _pearsonr_result(state):
    x_mean = state.x_sum / state.count
    y_mean = state.y_sum / state.count

    covariance = state.xy_sum - state.count * x_mean * y_mean

    x_var = state.xx_sum - state.count * x_mean * x_mean
    y_var = state.yy_sum - state.count * y_mean * y_mean
    variance = x_var**0.5 * y_var**0.5

    return covariance / (variance + eps)
```

---

## Evaluation Datasets

From `variant_eval_examples.ipynb`:

| Dataset               | Output Type       | Metric         | Score |
| --------------------- | ----------------- | -------------- | ----- |
| ClinVar Splice Site   | SPLICE_SITE_USAGE | AUPRC          | 0.570 |
| ClinVar Noncoding     | RNA_SEQ           | AUPRC          | 0.659 |
| sQTL Causality        | SPLICE_JUNCTIONS  | Weighted AUPRC | 0.764 |
| eQTL Sign             | RNA_SEQ           | Weighted AUROC | 0.810 |
| Enhancer-Gene Linking | RNA_SEQ           | AUPRC          | 0.749 |

---

## Hardware Requirements

| Task      | Minimum Hardware |
| --------- | ---------------- |
| Inference | NVIDIA H100 GPU  |
| Training  | TPU v3 or higher |

---

## Dependencies

```toml
dependencies = [
    'alphagenome',      # Base SDK (PyPI)
    'jax',              # GPU acceleration
    'dm-haiku',         # Neural network layers
    'chex',             # Array checking
    'tensorflow',       # Data loading (TFRecords)
    'kagglehub',        # Model weights download
    'huggingface_hub',  # Alternative weights source
]
```

---

## Model Weights Access

### Kaggle

```python
from alphagenome_research.model import dna_model
model = dna_model.create_from_kaggle('all_folds')
```

### HuggingFace

```python
model = dna_model.create_from_huggingface('all_folds')
```

**Note**: Requires accepting non-commercial model terms.

---

## Implications for ARCHCODE

### Validation

1. **Our metrics are correct** - AlphaGenome uses same Pearson R, MSE, MAE
2. **Contact map scoring** - Orca method applicable to our validation
3. **Mock mode remains valuable** - H100 required for real inference

### Integration Options

1. **API Mode** (Current)
   - Use AlphaGenome API for predictions
   - Requires API key from DeepMind
   - Best for casual validation

2. **Local Mode** (Future)
   - Install `alphagenome_research` package
   - Download weights from Kaggle/HuggingFace
   - Requires H100 GPU

3. **Python Wrapper** (Recommended)
   - Create `scripts/alphagenome_wrapper.py`
   - Call from TypeScript via child_process
   - Bridge between our TS codebase and their Python SDK

---

## Citation

```bibtex
@article{alphagenome,
  title={Advancing regulatory variant effect prediction with {AlphaGenome}},
  author={Avsec, Žiga and Latysheva, Natasha and Cheng, Jun and Novati, Guido
          and Taylor, Kyle R. and Ward, Tom and ...},
  journal={Nature},
  volume={649},
  number={8099},
  year={2026},
  doi={10.1038/s41586-025-10014-0},
  publisher={Nature Publishing Group UK London}
}
```

---

## Files of Interest

| File                                   | Purpose                             |
| -------------------------------------- | ----------------------------------- |
| `model/dna_model.py`                   | Main model interface                |
| `model/model.py`                       | Core architecture                   |
| `model/heads.py`                       | Output heads including contact maps |
| `model/variant_scoring/contact_map.py` | Contact map scoring (Orca)          |
| `evals/regression_metrics.py`          | Metrics implementation              |
| `colabs/variant_eval_examples.ipynb`   | Evaluation examples                 |

---

_Analysis by ARCHCODE Team_
_Author: Бойко Сергей Валерьевич_
