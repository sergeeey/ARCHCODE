# DNA2 Genomic Signal Decoder — Анализ для ARCHCODE

**Repository:** https://github.com/shootthesound/DNA2.git  
**Analyzed:** 2026-05-14  
**Status:** [[ARCHCODE]] pattern borrowing candidate

---

## Что такое DNA2

**Comprehensive genomic analysis platform** с 31 модулем анализа:
- 14 traditional genomics (dN/dS, codon usage, CpG islands, NJ phylogenetics)
- 7 signal processing (entropy, compression, autocorrelation, spectral, wavelets)
- 10 advanced (chaos game, multifractal DFA, Lempel-Ziv complexity, codon pair bias)

**Tech stack:** Python 3.10+, Streamlit GUI, BioPython, NumPy, SciPy, scikit-learn

**Validation:**
- Retrodiction suite: 6 test cases, 20/20 assertions passing
- Benchmark suite: 36 assertions, 7 modules validated against literature

---

## Architecture Overview

### Pipeline Structure (31 steps)

```python
STEP_DEFINITIONS = [
    ("download", "Download Genomes", []),
    ("partition", "Partition Genome", ["download"]),
    ("entropy", "Entropy Analysis", ["partition"]),
    ("compression", "Compression Analysis", ["partition"]),
    # ... 27 more steps
    ("cross_genome", "Cross-Genome Synthesis", 
     ["entropy", "compression", "autocorrelation", ...])
]
```

**Key features:**
- Dependency graph tracking
- Step status (PENDING → RUNNING → COMPLETED/FAILED/SKIPPED)
- Auto-skip completed steps
- Multi-genome support

### Caching System

```python
def cache_key(genome_name: str, analysis: str, params: dict) -> str:
    param_str = str(sorted(params.items()))
    h = hashlib.md5(param_str.encode()).hexdigest()[:12]
    return f"{genome_name}_{analysis}_{h}"
```

**Pattern:** Pickle-based cache with deterministic keys  
**Storage:** `results/cache/{key}.pkl`

### Modular Analysis Pattern

```python
@dataclass
class EntropyResults:
    genome_name: str
    entropy_profiles: Dict[str, np.ndarray]
    anomalies: List[AnomalyRegion]

def run_entropy_analysis(genome, partitions, **kwargs) -> EntropyResults:
    # 1. Check cache
    # 2. Run analysis
    # 3. Save to cache
    # 4. Return dataclass result

def plot_entropy_profile(results: EntropyResults) -> Figure:
    # Visualization отдельно
```

---

## Retrodiction Validation Methodology

**Ключевая идея:** Validate tools by replicating known genomic discoveries.

### Test Case Structure

```python
class RetrodictionTest:
    name: str
    genome_keys: List[str]
    
    def run(self) -> TestResult:
        # 1. Download genome with known pattern
        # 2. Run analysis
        # 3. Check if tool detects known pattern
        # 4. Return pass/fail + metrics
```

### Example: TC1 JCVI-syn1.0 Watermarks

**Known discovery:** Gibson et al. 2010 — first synthetic cell has 4 DNA watermark cassettes (~7 KB)

**Retrodiction test:**
- Genome: JCVI-syn1.0 (synthetic) vs M. mycoides (natural parent)
- Analysis: Mathematical patterns, gene editing detection
- Expected: Detect synthetic signatures in watermark regions
- Result: ✅ PASS (4/4 assertions)

### 6 Test Cases Coverage

| Test | Discovery | Modules Validated | Assertions |
|------|-----------|-------------------|------------|
| TC1 | JCVI-syn1.0 watermarks | Math patterns, gene editing | 4/4 ✅ |
| TC2 | SARS-CoV-2 furin site | Gene editing (CGG-CGG) | 3/3 ✅ |
| TC3 | Phage Phi X 174 | Compression, block structure | 3/3 ✅ |
| TC4 | HIV APOBEC3G signature | Mutation spectrum | 4/4 ✅ |
| TC5 | C. ethensis 2.0 codon redesign | Codon usage, gene editing | 3/3 ✅ |
| TC6 | Lambda phage periodicity | Spectral analysis | 3/3 ✅ |

**Total:** 20/20 assertions ✅

---

## Cross-Genome Synthesis

**Feature extraction → clustering → statistical significance**

```python
def run_cross_genome_analysis(all_results):
    # 1. Extract feature vectors from all 31 analyses
    # 2. Hierarchical clustering
    # 3. Permutation tests (1000 permutations)
    # 4. Effect-size filtering
    # 5. Shared anomaly detection
```

**Permutation test pattern:**
- Null hypothesis: feature X не отличается между группами
- Shuffle group labels 1000×
- Compute test statistic (t-test, Mann-Whitney)
- p-value = fraction of permutations where shuffled ≥ observed

---

## Полезные паттерны для ARCHCODE

### 1. Pipeline Orchestration ⭐⭐⭐⭐ (HIGH value)

**Что позаимствовать:**
- Dependency graph для validation workflow
- Step status tracking (PENDING/RUNNING/COMPLETED/FAILED)
- Auto-skip completed steps (check SQLite cache)

**ARCHCODE application:**
```python
VALIDATION_STEPS = [
    ("clinvar_fetch", "Fetch ClinVar", []),
    ("alphagenome_score", "AlphaGenome", ["clinvar_fetch"]),
    ("archcode_ssim", "ARCHCODE SSIM", ["clinvar_fetch"]),
    ("category_matched", "Category-Matched", ["alphagenome_score", "archcode_ssim"]),
    ("concordance", "Concordance", ["alphagenome_score", "archcode_ssim"]),
    ("cross_locus", "Cross-Locus", ["category_matched", "concordance"]),
]
```

**ROI:** 3× validation velocity  
**Effort:** 6 hours  
**Priority:** P1

### 2. Retrodiction Validation ⭐⭐⭐ (MEDIUM-HIGH value)

**Что позаимствовать:**
- Test suite structure (known pattern → detect → assert)
- Auto-run on API updates (regression prevention)
- Systematic coverage (all loci × all mechanisms)

**ARCHCODE application:**
```python
class RETRO_HBB_73bp_Cluster(RetrodictionTest):
    """Known: IVS-II-1 family = regulatory, CAGE disruption"""
    locus = "HBB"
    expected_mechanism = "regulatory"
    
    def run(self) -> TestResult:
        # Assert: regulatory variants → CAGE disruption
        # Assert: coding variants → NULL
```

**10 retrodiction tests:**
1. HBB IVS-II-1 (regulatory)
2. MLH1 promoter (regulatory)
3. TERT C228T/C250T (regulatory gain-of-function)
4. GJB2 coding (NULL expected)
5. TP53 coding (NULL expected)
6. BRCA1 coding (NULL expected)
7-10. Reserve for future loci

**ROI:** 10× regression prevention  
**Effort:** 4 hours  
**Priority:** P1

### 3. Cross-Genome Synthesis ⭐⭐ (MEDIUM value)

**Что позаимствовать:**
- Feature vector extraction
- Permutation tests for statistical significance
- Hierarchical clustering

**ARCHCODE application:**
- Cross-locus validation (HBB, MLH1, TERT, BRCA1, TP53, GJB2)
- Feature vectors: SSIM, CAGE, category, tissue context
- Question: "Do regulatory loci cluster separately from coding?"

**ROI:** 5× systematic cross-locus comparison  
**Effort:** 8 hours  
**Priority:** P2

### 4. Modular Structure ⭐ (LOW-MEDIUM value)

**Что позаимствовать:**
- @dataclass results
- Separation: data → analysis → visualization
- run_*() + plot_*() convention

**ROI:** 2× code reusability  
**Effort:** 12 hours (refactor)  
**Priority:** P3

### 5. Caching ❌ (SKIP)

**DNA2:** Pickle files  
**ARCHCODE:** SQLite (already better — 5000-18000× speedup, queryable)

**Decision:** SKIP, ARCHCODE pattern superior

---

## Что НЕ заимствовать

1. **Streamlit GUI** — не нужен interactive dashboard сейчас
2. **31 analysis modules** — genomics DNA2 ≠ 3D chromatin ARCHCODE
3. **Viral/phage focus** — ARCHCODE = human genomics
4. **Signal processing (chaos game, wavelets, multifractal)** — не релевантно для VUS classification

---

## Implementation Plan

### Phase 1: Retrodiction Suite (4 hours, P1)

**Goal:** Formalize AlphaGenome 7/7 loci validation as test suite

**Deliverables:**
- `ARCHCODE/validation/retrodiction_suite.py`
- `ARCHCODE/validation/retrodiction_cases.py` (10 tests)
- Auto-run script: `python validation/retrodiction_suite.py`

**Success criteria:** 10/10 tests pass, report generated

### Phase 2: Pipeline Orchestrator (6 hours, P1)

**Goal:** Dependency graph для multi-step validation

**Deliverables:**
- `ARCHCODE/validation_pipeline.py`
- Step definitions with dependencies
- CLI: `python validation_pipeline.py --locus HBB --steps category_matched,concordance`

**Success criteria:** Auto-skip completed steps, dependency checking works

### Phase 3: Cross-Locus Synthesis (8 hours, P2)

**Goal:** Statistical cross-locus comparison

**Deliverables:**
- Feature vector extraction (SSIM, CAGE, category, tissue)
- Hierarchical clustering
- Permutation tests (1000 permutations)

**Success criteria:** Answer "Do regulatory loci cluster separately?"

---

## Comparison: DNA2 vs ARCHCODE

| | DNA2 | ARCHCODE |
|---|---|---|
| **Goal** | Genomic signal decoder (31 metrics) | VUS pathogenicity (3D + functional) |
| **Validation** | Retrodiction (replicate discoveries) | Cross-locus (7/7 mechanism) |
| **Pipeline** | 31 steps, dependency graph ✅ | Multi-step ADR (manual) ❌ |
| **Caching** | Pickle files | SQLite ✅ (better) |
| **Cross-comparison** | Cross-genome synthesis ✅ | Cross-locus (less systematic) |
| **Test suite** | 6 retrodiction tests ✅ | Ad-hoc validation ❌ |

**ARCHCODE strengths:**
- SQLite pattern > pickle
- Falsification-first > exploratory
- Forensic audit (5 layers) > single-pass

**DNA2 strengths:**
- Pipeline orchestration
- Retrodiction methodology
- Systematic cross-comparison

---

## Next Actions

**Recommended:** Start with Retrodiction Suite (4h, 10× ROI, lower risk)

**Alternative:** Pipeline Orchestrator first (6h, 3× ROI, higher complexity)

**Decision pending:** User confirmation on which to build first

---

## Links

- [[ARCHCODE]] — main project
- [[AlphaGenome Validation]] — 7/7 loci mechanism specificity
- [[Cross-Locus Validation Framework]] — MLH1, TERT validation
- [[ARCHCODE SQLite Pattern]] — caching (superior to DNA2)
- [[Harvest to Combinatorial Creativity Pipeline]] — where DNA2 was discovered

---

**Tags:** #genomics #validation #retrodiction #pipeline #DNA2 #pattern-borrowing