# Reproducing ARCHCODE Results

This document specifies a single command sequence that reproduces all numerical claims in `manuscript/manuscript_v2_full.md` and `README.md`. **Docker is optional** — local install works for preprint-level reproduction; Docker is recommended only for journal submission.

**Target audience:** Peer reviewers, independent researchers, ARCHCODE collaborators.
**Expected runtime:** ~3 minutes on commodity hardware (no GPU required).
**Last verified:** 2026-05-25 (commit chain: `a3bbef2` → `82cd3e1` → `c3f62b3` → `d81e0cd`)

---

## TL;DR — One-Command Reproduction

```bash
# 1. Clone repo
git clone https://github.com/sergeeey/ARCHCODE.git
cd ARCHCODE

# 2. Install Python dependencies (canonical: requirements.txt or pyproject.toml)
pip install -r requirements.txt
# OR: pip install -e ".[test]"

# 3. Install Node.js dependencies (for simulation engine tests)
npm install

# 4. Run reproduction
python -m pytest tests/test_alphagenome_invariants.py -v && \
  npm test && \
  python scripts/count_unique_variants.py
```

If all three pass with the expected outputs below, **the manuscript's numerical claims are reproduced**.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | ≥ 3.11 | Tested on 3.11.13 (miniconda `ape311`) |
| Node.js | ≥ 20 | Required for TypeScript simulation engine |
| npm | bundled with Node.js | |
| git | any modern | |
| Disk | ~500 MB | mostly `data/` and `results/` |
| GPU | not required | All claims reproducible on CPU |

**Verify environment:**
```bash
python --version  # >= 3.11
node --version    # >= v20
npm --version     # >= 10
```

---

## Expected Outputs

### 1. Python invariant tests (Layer 5 audit)

```bash
$ python -m pytest tests/test_alphagenome_invariants.py -v
```

Expected:
```
tests/test_alphagenome_invariants.py::TestCAGEValueRange::test_pathogenic_cage_range PASSED
tests/test_alphagenome_invariants.py::TestCAGEValueRange::test_benign_cage_range PASSED
tests/test_alphagenome_invariants.py::TestNoNaN::test_no_nan_in_means PASSED
tests/test_alphagenome_invariants.py::TestNoNaN::test_no_nan_in_ratio PASSED
tests/test_alphagenome_invariants.py::TestSampleSize::test_minimum_sample_size PASSED
tests/test_alphagenome_invariants.py::TestSampleSize::test_sample_size_consistency PASSED
tests/test_alphagenome_invariants.py::TestPValueValidity::test_p_value_range PASSED
tests/test_alphagenome_invariants.py::TestPValueValidity::test_no_nan_p_values PASSED
tests/test_alphagenome_invariants.py::TestLocusConsistency::test_core_7_loci_present PASSED
tests/test_alphagenome_invariants.py::TestLocusConsistency::test_no_duplicate_loci PASSED
tests/test_alphagenome_invariants.py::TestStatisticalConsistency::test_ratio_matches_means PASSED
tests/test_alphagenome_invariants.py::TestStatisticalConsistency::test_cohen_d_direction PASSED
tests/test_alphagenome_invariants.py::test_layer5_audit_pass PASSED

============================= 13 passed in <1s ==============================
```

### 2. TypeScript simulation engine tests

```bash
$ npm test
```

Expected:
```
 ✓ src/__tests__/LoopExtrusionEngine.test.ts (13 tests)
 ✓ src/__tests__/regression/gold-standard.test.ts
 ✓ src/__tests__/regression/loops.test.ts
 ...

 Test Files  6 passed (6)
      Tests  49 passed (49)
```

### 3. Variant count verification (Layer 7 provenance)

```bash
$ python scripts/count_unique_variants.py
```

Expected:
```
Core 9 Loci Check
======================================================================
  HBB         1,103 variants
  TP53        2,794 variants
  BRCA1      10,682 variants
  MLH1        4,060 variants
  TERT        2,089 variants
  GJB2          469 variants
  CFTR        3,349 variants
  GATA1         183 variants
  PTEN        1,496 variants

  CORE TOTAL 26,225 variants
```

### 4. Manuscript key statistics (HBB pilot result)

```bash
$ python -c "
import json
with open('results/alphagenome_batch_cage_9loci.json') as f:
    d = json.load(f)
for locus, s in d['results'].items():
    if isinstance(s, dict) and 'p' in s:
        p = s.get('p')
        ratio = s.get('ratio')
        if p is not None and ratio is not None:
            print(f'{locus}: ratio={ratio:.2f}, p={p:.4e}')
"
```

Expected (key values for manuscript claims):
```
TP53: ratio=0.80, p=5.58e-01     # coding null (correct)
TERT: ratio=0.91, p=6.48e-01     # insufficient hotspot controls
GJB2: ratio=1.07, p=8.44e-01     # coding null (correct)
MLH1: ratio=3.68, p=2.25e-02     # nominal, fails Bonferroni (α=0.007)
BRCA1: ratio=1.00, p=6.68e-01    # coding null (correct)
HBB_reference: ratio=5.40, p=4.00e-06    # PILOT — Bonferroni-robust ✅
```

> **Note:** CFTR is excluded (NaN values) due to documented interval mismatch.
> See `docs/ADR-033_Forensic_Audit_Summary.md` Layer 5 and Section 4.4 of the manuscript.

### 5. MLH1 power analysis (closes ADR-036 OQ#1)

```bash
$ python scripts/power_analysis_mlh1.py
```

Expected:
```
Observed (current cohort):
  N total = 30 (15 path + 15 ben)
  Mann-Whitney p = 0.0225
  Recovered Z = 2.282
  Effect size r = 0.417 (medium)
  Cohen's d ≈ 0.589

Target:
  α = 0.007 (Bonferroni 7 tests)
  Power = 0.8

Required (Mann-Whitney, ARE=0.864):
  n per group ≈ 83
  N total ≈ 167
  Increase factor: 5.6×
```

---

## Data Provenance Checksums

| File | SHA-256 (first 16 chars) | Description |
|------|--------------------------|-------------|
| `results/alphagenome_batch_cage_9loci.json` | `343985aa70759570` | AlphaGenome CAGE batch results (7 loci pathogenic vs benign) |
| `results/dataset_count_verification.txt` | (regenerated by script) | Per-locus dedup count |

Verify locally:
```bash
python -c "
import hashlib
files = ['results/alphagenome_batch_cage_9loci.json']
for f in files:
    with open(f, 'rb') as fh:
        print(f, hashlib.sha256(fh.read()).hexdigest()[:16])
"
```

If checksums diverge from the table above: the data has been regenerated (intentionally or by accident). Cross-check with `git log results/alphagenome_batch_cage_9loci.json` to see history.

---

## Key Claims and Where to Verify

| Manuscript claim | Section | Verification command |
|------------------|---------|----------------------|
| 26,225 core variants | Abstract, Methods 2.2 | `python scripts/count_unique_variants.py` |
| HBB p=4×10⁻⁶ (Bonferroni-robust) | Abstract, Section 3.4 | Section 4 above |
| MLH1 p=0.022 (fails Bonferroni) | Section 3.4 | Section 4 above |
| MLH1 requires N≥~167 for 80% power | Methods 2.5 | `python scripts/power_analysis_mlh1.py` |
| 6 hypotheses killed (H1-H6) | Section 3 | Per-hypothesis ADRs in `docs/ADR-*.md` |
| Coding null (TP53, BRCA1, CFTR, GJB2) | Section 3.4 | Section 4 above |
| TERT hotspots +33%, +53% CAGE | Section 3.4 | `python -c "import json; d=json.load(open('results/tert_hotspots_cage_test.json')); print(d)"` |
| Code trust hardened (P0 audit) | — | `python -m pytest tests/ -v` |

---

## Optional — Full Reproduction with Docker

For journal submission level reproducibility, a `Dockerfile` will be added in a future commit. The local install above is sufficient for preprint verification.

```bash
# Future (not yet implemented):
# docker build -t archcode:v2.18 .
# docker run --rm archcode:v2.18 make reproduce
```

**Status:** P2 task — pending journal submission. Tracked in `docs/ADR-036_manuscript_reframe_HBB_pilot.md` open questions.

---

## Troubleshooting

### `KeyError: 'HBB'` when reading AlphaGenome JSON
HBB is stored as `HBB_reference` in the AlphaGenome batch results (documented in P0 audit, Layer 7). Use `d['results']['HBB_reference']`, not `d['results']['HBB']`.

### CFTR returns NaN in invariant tests
**Expected.** CFTR has a documented interval mismatch between ClinVar coordinates and AlphaGenome's interval expectation. The invariant tests skip CFTR explicitly (see `tests/test_alphagenome_invariants.py:50` — `# Skip CFTR - known interval mismatch (NaN)`). This is **not** silent corruption (Layer 5 audit verified).

### `npm test` fails on Windows with `LF will be replaced by CRLF`
Cosmetic warning. Set `git config core.autocrlf true` to silence.

### Discrepancy: README says "30,318" but I get "26,225"
**Expected.** Preprint v1 (Research Square `rs-9090074`) used the raw ClinVar fetch count (30,318). After P0 deduplication audit (May 2026, commit `a3bbef2`), the verified core count is **26,225**. See `docs/NUMBER_PROVENANCE.md` for full reconciliation. The manuscript v2 (in revision) uses 26,225 throughout.

### `pyproject.toml` install fails
Use `pip install -r requirements.txt` instead — equivalent dependencies, no pyproject.toml resolution required.

---

## Reproducibility Guarantees

This document is the **single source of truth** for reproducing ARCHCODE numerical claims. If a command in this document fails, **that is a reproducibility bug** to be reported as a GitHub issue:

https://github.com/sergeeey/ARCHCODE/issues/new?labels=reproducibility

We commit to:
1. All numerical claims in `manuscript_v2_full.md` are reproducible by the commands above
2. Test invariants are auto-checked (`tests/test_alphagenome_invariants.py`, 13 tests)
3. Number provenance is documented (`docs/NUMBER_PROVENANCE.md`)
4. Known limitations are disclosed (`docs/ADR-035_loop_extrusion_collision_detection.md`)

**Verified commit chain (May 25, 2026):**
- `a3bbef2` — Dataset count verified (26,225)
- `82cd3e1` — 13 invariant tests added
- `c3f62b3` — Manuscript reframe (HBB pilot, ADR-036)
- `d81e0cd` — MLH1 power analysis (~167 required N)
