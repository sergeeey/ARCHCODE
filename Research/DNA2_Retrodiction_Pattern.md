# DNA2 Retrodiction Validation Pattern

**Source:** https://github.com/shootthesound/DNA2.git  
**Pattern:** Validate genomic analysis tools by replicating known discoveries  
**Status:** Ready for ARCHCODE adaptation

---

## Core Concept

**Retrodiction** = валидация через воспроизведение известных открытий

**Instead of:**
- "Does this tool work?" (unknown answer)
- Synthetic benchmarks (artificial)
- Manual inspection (subjective)

**Use:**
- "Can this tool detect [known discovery]?" (known answer)
- Real genomes with documented patterns
- Automated pass/fail assertions

---

## Why This Works

1. **Ground truth exists** — published discoveries are verified
2. **Realistic data** — real genomes, not synthetic
3. **Clear success criteria** — either detects or doesn't
4. **Regression prevention** — tests survive tool updates
5. **Systematic coverage** — one test per discovery

---

## DNA2 Test Case Structure

```python
@dataclass
class TestResult:
    name: str
    passed: bool
    metrics: Dict[str, float]
    assertions: List[Assertion]  # Each assertion = one claim
    error: Optional[str]

@dataclass
class Assertion:
    description: str  # Human-readable claim
    passed: bool      # Pass/fail
    detail: str       # Evidence or failure reason

class RetrodictionTest:
    name: str = ""
    genome_keys: List[str] = []  # Genomes needed for test
    
    def _ensure_genomes(self):
        """Download genomes if needed"""
        
    def _run_analysis(self, module_path, func_name, genome, partitions, **kwargs):
        """Run analysis module and return results"""
        
    def run(self) -> TestResult:
        """Execute test, return pass/fail + assertions"""
        raise NotImplementedError
```

---

## Example: TC1 JCVI-syn1.0 Watermarks

**Known discovery (Gibson et al. 2010):**
- First synthetic bacterial genome
- Contains 4 DNA watermark cassettes (~7 KB total)
- Modified restriction sites
- Distinct from natural M. mycoides parent

**Retrodiction test implementation:**

```python
class TC1_SyntheticWatermarks(RetrodictionTest):
    name = "TC1: JCVI-syn1.0 Synthetic Watermarks"
    genome_keys = ["jcvi_syn1", "m_mycoides_natural"]
    
    def run(self) -> TestResult:
        result = TestResult(name=self.name, passed=False)
        
        # 1. Ensure genomes downloaded
        self._ensure_genomes()
        
        # 2. Get partitions
        syn_partitions = self._get_partitions("jcvi_syn1")
        nat_partitions = self._get_partitions("m_mycoides_natural")
        
        # 3. Run mathematical pattern detection
        syn_patterns = self._run_analysis(
            "src.mathematical_patterns",
            "run_mathematical_pattern_analysis",
            GENOMES["jcvi_syn1"],
            syn_partitions
        )
        
        nat_patterns = self._run_analysis(
            "src.mathematical_patterns",
            "run_mathematical_pattern_analysis",
            GENOMES["m_mycoides_natural"],
            nat_partitions
        )
        
        # 4. Assertions
        # A1: Synthetic has more pattern hits than natural
        syn_hits = len(syn_patterns.pattern_hits)
        nat_hits = len(nat_patterns.pattern_hits)
        
        result.assertions.append(Assertion(
            description="JCVI-syn1.0 has more mathematical patterns than natural parent",
            passed=syn_hits > nat_hits,
            detail=f"Synthetic: {syn_hits} hits, Natural: {nat_hits} hits"
        ))
        
        # A2: Gene editing score elevated in synthetic
        syn_editing = self._run_analysis(
            "src.gene_editing_detection",
            "run_gene_editing_detection",
            GENOMES["jcvi_syn1"],
            syn_partitions
        )
        
        result.assertions.append(Assertion(
            description="CGG codon pair density elevated in synthetic",
            passed=syn_editing.cgg_density > 0.02,  # Known threshold
            detail=f"Density: {syn_editing.cgg_density:.4f}"
        ))
        
        # A3: Restriction site regularity score > threshold
        result.assertions.append(Assertion(
            description="Restriction site regularity score indicates engineering",
            passed=syn_editing.restriction_regularity > 0.7,
            detail=f"Score: {syn_editing.restriction_regularity:.2f}"
        ))
        
        # A4: Codon optimization score elevated
        result.assertions.append(Assertion(
            description="Codon optimization score above natural baseline",
            passed=syn_editing.codon_opt_score > 0.6,
            detail=f"Score: {syn_editing.codon_opt_score:.2f}"
        ))
        
        # Final verdict
        result.passed = all(a.passed for a in result.assertions)
        result.metrics = {
            "syn_pattern_hits": syn_hits,
            "nat_pattern_hits": nat_hits,
            "cgg_density": syn_editing.cgg_density,
            "restriction_regularity": syn_editing.restriction_regularity,
            "codon_opt_score": syn_editing.codon_opt_score,
        }
        
        return result
```

**Result:** ✅ 4/4 assertions pass

---

## DNA2 Full Test Suite (6 cases)

| Test | Known Discovery | Tool/Module | Assertions |
|------|-----------------|-------------|------------|
| TC1 | JCVI-syn1.0 watermarks | Math patterns, gene editing | 4/4 ✅ |
| TC2 | SARS-CoV-2 furin cleavage site (CGG-CGG) | Gene editing (codon pair) | 3/3 ✅ |
| TC3 | Phage Phi X 174 overlapping genes | Compression, block structure | 3/3 ✅ |
| TC4 | HIV APOBEC3G C→T signature | Mutation spectrum | 4/4 ✅ |
| TC5 | C. ethensis 2.0 codon redesign | Codon usage, gene editing | 3/3 ✅ |
| TC6 | Lambda phage 3-bp periodicity | Spectral analysis (FFT) | 3/3 ✅ |

**Total:** 20/20 assertions ✅

---

## ARCHCODE Adaptation

### Current State

**AlphaGenome validation (2026-05-09):**
- ✅ 7/7 loci perfect mechanism specificity
- ✅ Regulatory loci (HBB, MLH1, TERT) → CAGE disruption
- ✅ Coding loci (GJB2, TP53, BRCA1, F9) → NULL (orthogonal)

**Problem:** Not formalized as test suite, no auto-run, no regression prevention

### Proposed: ARCHCODE Retrodiction Suite

**10 test cases (known mechanisms → detect → assert):**

```python
class RETRO_HBB_73bp_Cluster(RetrodictionTest):
    """
    Known: HBB IVS-II-1 family (73bp cluster) = regulatory, CAGE disruption
    Source: ADR-027 category-matched validation
    """
    name = "RETRO-01: HBB 73bp Cluster Regulatory"
    locus = "HBB"
    expected_mechanism = "regulatory"
    
    def run(self) -> TestResult:
        # 1. Fetch HBB IVS-II-1 variants (VCV000039187, etc.)
        variants = self.fetch_clinvar_variants(locus="HBB", category="regulatory")
        
        # 2. Run AlphaGenome scoring
        scores = self.run_alphagenome(variants)
        
        # 3. Assertions
        # A1: Regulatory variants show CAGE disruption (p < 0.05)
        regulatory = [v for v in variants if v.category == "regulatory"]
        p_value = mann_whitney_test(
            [scores[v.vcv_id].cage_delta for v in regulatory if v.pathogenic],
            [scores[v.vcv_id].cage_delta for v in regulatory if v.benign]
        )
        
        result.assertions.append(Assertion(
            description="Regulatory variants show significant CAGE disruption",
            passed=p_value < 0.05,
            detail=f"Mann-Whitney p={p_value:.6f}"
        ))
        
        # A2: Coding variants do NOT show CAGE disruption (p > 0.05)
        coding = [v for v in variants if v.category == "coding"]
        p_coding = mann_whitney_test(
            [scores[v.vcv_id].cage_delta for v in coding if v.pathogenic],
            [scores[v.vcv_id].cage_delta for v in coding if v.benign]
        )
        
        result.assertions.append(Assertion(
            description="Coding variants show NULL (orthogonal mechanism)",
            passed=p_coding > 0.05,
            detail=f"Mann-Whitney p={p_coding:.6f} (expect >0.05)"
        ))
        
        # A3: Mechanism specificity 100% (regulatory PASS, coding NULL)
        result.assertions.append(Assertion(
            description="Mechanism specificity perfect (regulatory-only detection)",
            passed=(p_value < 0.05) and (p_coding > 0.05),
            detail="Regulatory PASS + Coding NULL = perfect specificity"
        ))
        
        result.passed = all(a.passed for a in result.assertions)
        return result
```

**Full suite (10 tests):**

1. **RETRO-01:** HBB IVS-II-1 73bp cluster (regulatory)
2. **RETRO-02:** MLH1 promoter variants (regulatory)
3. **RETRO-03:** TERT C228T/C250T hotspots (regulatory gain-of-function)
4. **RETRO-04:** GJB2 coding variants (NULL expected)
5. **RETRO-05:** TP53 coding variants (NULL expected)
6. **RETRO-06:** BRCA1 coding variants (NULL expected)
7. **RETRO-07:** F9 hemophilia B variants (NULL expected)
8. **RETRO-08:** Cross-locus regulatory clustering (all 3 regulatory loci)
9. **RETRO-09:** Cross-locus coding NULL (all 4 coding loci)
10. **RETRO-10:** Forensic audit integrity (5-layer verification, all loci)

**Expected:** 10/10 tests pass ✅

---

## Auto-Run Workflow

### Triggers

**When to re-run retrodiction suite:**
1. AlphaGenome API model update
2. ClinVar variant set changes (new P/LP or B/LB)
3. ARCHCODE code changes (structural scoring logic)
4. Before publication submission (integrity gate)
5. Weekly CI/CD (regression monitoring)

### CI/CD Integration

```bash
# .github/workflows/retrodiction.yml
name: Retrodiction Suite

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:      # Manual trigger

jobs:
  retrodiction:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Retrodiction Suite
        run: python validation/retrodiction_suite.py
      - name: Check Results
        run: |
          if grep -q "FAILED" results/reports/retrodiction_report.md; then
            echo "❌ Retrodiction tests failed"
            exit 1
          else
            echo "✅ All retrodiction tests passed"
          fi
```

---

## Benefits vs Traditional Testing

| Approach | Ground Truth | Realistic Data | Auto-Run | Coverage |
|----------|--------------|----------------|----------|----------|
| **Unit tests** | ❌ Synthetic | ❌ Mock data | ✅ Yes | ⚠️ Code paths |
| **Integration tests** | ❌ Expected behavior | ⚠️ Staging data | ✅ Yes | ⚠️ Workflows |
| **Manual validation** | ✅ Real discoveries | ✅ Real genomes | ❌ No | ❌ Ad-hoc |
| **Retrodiction** | ✅ Published discoveries | ✅ Real genomes | ✅ Yes | ✅ Known patterns |

**Retrodiction = best of all worlds**

---

## Implementation Checklist

- [ ] Create `ARCHCODE/validation/retrodiction_suite.py` (runner)
- [ ] Create `ARCHCODE/validation/retrodiction_cases.py` (10 test classes)
- [ ] Implement `RetrodictionTest` base class
- [ ] Implement `TestResult` and `Assertion` dataclasses
- [ ] Write RETRO-01 (HBB 73bp cluster)
- [ ] Write RETRO-02 (MLH1 promoter)
- [ ] Write RETRO-03 (TERT hotspots)
- [ ] Write RETRO-04-07 (coding NULL tests)
- [ ] Write RETRO-08-09 (cross-locus clustering)
- [ ] Write RETRO-10 (forensic audit)
- [ ] Generate `retrodiction_report.md` with results
- [ ] Add CI/CD workflow (weekly auto-run)
- [ ] Document in [[ARCHCODE Validation Framework]]

**Estimated effort:** 4 hours  
**ROI:** 10× regression prevention  
**Priority:** P1

---

## Links

- [[DNA2 Genomic Signal Decoder Analysis]] — full DNA2 analysis
- [[AlphaGenome Validation]] — 7/7 loci mechanism specificity (to formalize)
- [[ARCHCODE]] — main project
- [[Cross-Locus Validation Framework]] — related validation work

---

**Tags:** #retrodiction #validation #testing #DNA2 #pattern #ARCHCODE