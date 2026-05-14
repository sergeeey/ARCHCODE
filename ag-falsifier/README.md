# ag-falsifier

**Falsification-first validation harness for AlphaGenome predictions on clinical variants**

[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/geoserg/ag-falsifier)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## One-Line Pitch

**Prevent validation theater:** Automatic statistical controls for AlphaGenome variant effect predictions.

---

## Problem

Testing AI genomics predictions on disease variants is prone to **validation theater**:
- Tests designed to pass (no category-matched controls)
- Circular logic (category = predictor)
- Cherry-picked results (null results hidden)
- Synthetic data passed as real validation

**ag-falsifier** enforces falsification-first methodology automatically.

---

## Features

✅ **Category-matched permutation** (auto-detect category leakage)  
✅ **Test validity tracking** (VALID / PARTIAL / INVALID)  
✅ **Automatic negative controls** (shuffled labels, random windows)  
✅ **Seed sensitivity** (detect unstable p-values)  
✅ **ADR generation** (document null results)  
✅ **Orthogonality detection** (group diff ≠ rank correlation)  

---

## Installation

```bash
# Alpha release (not on PyPI yet)
git clone https://github.com/geoserg/ag-falsifier
cd ag-falsifier
pip install -e .
```

**Dependencies:** `pandas`, `scipy`, `numpy`, `alphagenome-sdk`

---

## Quick Start

```python
from ag_falsifier import AlphaGenomeValidator
import os

# Initialize validator
validator = AlphaGenomeValidator(
    pearls=pearl_variants,  # pd.DataFrame with structural fragility candidates
    controls=benign_variants,  # pd.DataFrame with benign controls
    api_key=os.getenv('ALPHAGENOME_API_KEY')
)

# Run validation (automatic controls)
result = validator.validate(
    modality='CAGE',
    category_matched=True,  # Auto-match controls by variant category
    permutation_test=True,  # 10K permutations
    negative_controls=['shuffled_labels', 'random_windows'],
    seed_sensitivity=[1, 7, 21, 42, 100]
)

# Check result
print(f"Test validity: {result.test_validity}")  # VALID / PARTIAL / INVALID
print(f"p-value: {result.p_value}")
print(f"Verdict: {result.verdict}")  # PASS / WEAK / FAIL

# Generate ADR (Architectural Decision Record)
result.to_adr(path='docs/ADR-029_validation_result.md')
```

---

## Case Studies

### 1. Category-Matched Validation (HBB Promoter)

**Problem:** All HBB promoter variants are pathogenic → 0 non-pathogenic promoter controls

**ag-falsifier detects:**
```python
result.test_validity == "PARTIAL"
result.warning == "15/20 pearls skipped (no promoter controls)"
result.verdict == "WEAK"
```

**Interpretation:** Test cannot validate promoter enrichment (honest limitation documented).

---

### 2. Orthogonality Detection (ARCHCODE × AlphaGenome)

**Problem:** Group difference exists (Mann-Whitney p=4e-6), but rank correlation null (Spearman ρ=0.077)

**ag-falsifier detects:**
```python
result.group_difference_p == 4e-6  # Significant
result.rank_correlation_rho == 0.077  # NULL
result.interpretation == "ORTHOGONAL_MECHANISMS"
```

**Interpretation:** Both methods detect pathogenicity, but via independent rankings.

---

### 3. Variance Diagnostics (Concordance Failure)

**Problem:** ARCHCODE fragility has low variance (CV=3.5%) → cannot correlate

**ag-falsifier detects:**
```python
result.variance_check == "FAIL"
result.cv_predictor == 0.035  # Too low for correlation
result.warning == "Predictor variance <10% → rank correlation unreliable"
```

**Interpretation:** Correlation test not applicable (data limitation).

---

## Workflow

```
1. Load variants (pearls + controls)
   ↓
2. Fetch AlphaGenome predictions (CAGE, ATAC, etc.)
   ↓
3. Run statistical harness:
   • Category-matched permutation
   • Negative controls (shuffled, random)
   • Seed sensitivity
   • Variance diagnostics
   ↓
4. Generate verdict:
   • PASS: all tests pass, test_validity=VALID
   • WEAK: marginal p-value OR test_validity=PARTIAL
   • FAIL: p≥0.05 OR test_validity=INVALID
   ↓
5. Export ADR (Architectural Decision Record)
```

---

## API Reference

### `AlphaGenomeValidator`

**Constructor:**
```python
AlphaGenomeValidator(
    pearls: pd.DataFrame,       # Variant candidates
    controls: pd.DataFrame,     # Benign controls
    api_key: str,               # AlphaGenome API key
    interval: Interval = None   # Genomic interval (auto-detect if None)
)
```

**Methods:**
```python
.validate(
    modality: str = 'CAGE',                    # CAGE, ATAC, RNA_SEQ, etc.
    category_matched: bool = True,             # Auto-match by category
    permutation_test: bool = True,             # Run permutation test
    n_permutations: int = 10000,               # Number of permutations
    negative_controls: List[str] = [...],      # ['shuffled_labels', 'random_windows']
    seed_sensitivity: List[int] = [1,7,21,42,100],
    alpha: float = 0.01                        # Significance threshold
) -> ValidationResult
```

**Result attributes:**
```python
result.test_validity     # "VALID" / "PARTIAL" / "INVALID"
result.p_value           # Primary p-value (category-matched if available)
result.verdict           # "PASS" / "WEAK" / "FAIL"
result.interpretation    # Human-readable interpretation
result.warning           # Warning message if validity compromised
result.to_adr(path)      # Generate ADR markdown
result.to_json(path)     # Export full results
```

---

## Design Principles

### 1. Falsification-First

**Bad practice:**
```python
# Test designed to pass
if pearls.mean() > controls.mean():
    print("SUCCESS!")
```

**ag-falsifier:**
```python
# Test designed to FAIL if hypothesis wrong
result = validator.validate(category_matched=True)
if result.test_validity != "VALID":
    print(f"FAIL: {result.warning}")
```

---

### 2. Test Validity Before p-value

**Bad practice:**
```python
if p_value < 0.05:
    print("Significant!")
```

**ag-falsifier:**
```python
if result.test_validity == "VALID" and result.p_value < 0.05:
    print("Validated!")
elif result.test_validity == "PARTIAL":
    print(f"Partial validity: {result.warning}")
else:
    print("Test not applicable")
```

---

### 3. Document Null Results

**Bad practice:**
```python
# Only report if p<0.05
if p_value < 0.05:
    save_result(...)
```

**ag-falsifier:**
```python
# Always generate ADR (null results = first-class artifacts)
result.to_adr(path=f'docs/ADR-{counter}_result.md')
```

---

## Roadmap

**Alpha release (May 22, 2026):**
- [x] Core validator class
- [x] Category-matched permutation
- [x] Test validity tracking
- [x] ADR generation
- [ ] PyPI package
- [ ] Documentation site

**Beta release (June 2026):**
- [ ] Multi-modality support (CAGE + ATAC + RNA-seq)
- [ ] Automatic category detection
- [ ] Batch processing
- [ ] Web UI (Streamlit)

**v1.0 (July 2026):**
- [ ] Cross-locus benchmarks
- [ ] Pre-registered validation templates
- [ ] Integration with ClinVar API
- [ ] Publication (NAR Genomics)

---

## Citation

If you use ag-falsifier in your research:

```bibtex
@software{boyko2026agfalsifier,
  author = {Boyko, Sergey},
  title = {ag-falsifier: Falsification-First Validation for AlphaGenome},
  year = {2026},
  url = {https://github.com/geoserg/ag-falsifier},
  note = {Alpha release}
}
```

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

**Priority areas:**
1. Multi-locus validation examples
2. Additional negative control types
3. Documentation improvements
4. Bug reports from real-world usage

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Contact

**Sergey Boyko**  
Independent Computational Researcher  
Ronin Institute RIIS 2.0 Fellow  

Email: sergeikuch80@gmail.com  
GitHub: [@geoserg](https://github.com/geoserg)  
ORCID: [0009-0009-2178-5701](https://orcid.org/0009-0009-2178-5701)

---

## Acknowledgments

- AlphaGenome team (DeepMind) for API access
- ARCHCODE project for validation case studies
- Falsification-first methodology inspired by Popper, Taleb, Yudkowsky

---

_"Null results are results. Validation theater is not validation."_
