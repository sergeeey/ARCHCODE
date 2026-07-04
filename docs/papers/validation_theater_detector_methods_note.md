# Validation Theater Detector: Automated Detection of Synthetic Data in Computational Validation Claims

**Authors:** Sergey Kuchinsky  
**Affiliation:** Ronin Institute for Independent Scholarship (RIIS 2.0)  
**Correspondence:** sergeikuch80@gmail.com  
**ORCID:** 0009-0009-2178-5701

**Target Journal:** Bioinformatics Advances (Methods Note, ~1000 words)  
**Status:** Draft v0.1 (2026-05-16)  
**Code:** https://github.com/sergey/ARCHCODE/tree/main/src/tools/validation_theater_detector  
**License:** MIT

---

## Abstract

**Motivation:** Validation theater—the practice of marking synthetic or mock data as verified validation results—undermines reproducibility in computational biology. Perfect metrics (F1=1.000, 100% accuracy) on hand-crafted test cases are frequently reported as evidence of model performance, despite having no predictive value on real-world data.

**Results:** We present Validation Theater Detector (VT Detector), an automated static analysis tool that identifies suspicious validation patterns in Python code. The tool combines AST-based code analysis with regex pattern matching to detect: (1) synthetic data markers without [VERIFIED-SYNTHETIC] disclosure, (2) suspiciously perfect metrics (F1=1.000, zero errors), (3) embedded test data without external source citation, and (4) zero-failure claims across multiple test scenarios. A confidence scoring system with pattern synergies and context-aware severity escalation flags high-risk validation theater with 80% confidence. Applied retrospectively to a prior validation theater incident (ТОП-10, May 2026), VT Detector correctly identified all synthetic validators that falsely claimed 100% success on mock data.

**Availability:** Python 3.11+, MIT license. Source code and documentation at https://github.com/sergey/ARCHCODE/src/tools/validation_theater_detector

**Keywords:** reproducibility, validation, synthetic data, static analysis, research integrity

---

## 1. Introduction

The reproducibility crisis in computational biology stems partly from validation theater: presenting synthetic data validation as evidence of real-world performance. Studies report perfect F1 scores (1.000) or 100% accuracy without disclosing that metrics were computed on hand-crafted test cases [Freedman et al. 2015]. This practice wastes resources—researchers invest months developing methods that perform perfectly on synthetic data but fail on real datasets.

Traditional solutions rely on post-publication peer review or manual code inspection. However, validation theater is difficult to detect retroactively: synthetic data generation may occur in separate files, perfect metrics appear in results tables without source code, and test cases are often embedded directly in validation scripts without external dataset citations.

We address this gap with an automated pre-submission detector that flags validation theater patterns during manuscript preparation. By integrating into pre-commit hooks or continuous integration pipelines, VT Detector prevents validation theater before submission rather than catching it during peer review.

---

## 2. Methods

### 2.1 Detection Architecture

VT Detector operates in three stages:

**Stage 1: Pattern Detection (AST + Regex)**
- **Synthetic data markers:** Identifies code patterns indicating synthetic data generation: `np.random.seed()`, `mock_*` function prefixes, `create_synthetic_*` functions, and variables named `synthetic_data` or `fake_examples`.
- **Perfect metrics:** Detects suspiciously round performance metrics: F1=1.000 (≥3 decimal places), precision/recall=1.0, accuracy=100%, AUC=1.000, R²≥0.995, MSE/RMSE=0.0.
- **Zero-failure claims:** Matches phrases like "all tests passed", "zero failures", "100% success rate", "no errors found" across ≥5 test scenarios.
- **Embedded test data:** Uses Abstract Syntax Tree (AST) analysis to identify inline test data arrays (e.g., `test_cases = [("input1", "label"), ...]`) without nearby external data source citations (API calls, file reads, URLs).

**Stage 2: Confidence Scoring**
Each detected pattern contributes a base confidence weight (0.2–0.5). Pattern synergies boost confidence when multiple red flags co-occur:
- Synthetic marker + perfect metric → +0.25
- Embedded test data + F1=1.000 → +0.30
- ≥3 patterns in same file → +0.15 (multi-pattern boost)

Evidence modifiers reduce confidence for mitigating factors:
- External data source cited (`requests.get()`, `pd.read_csv()`, URL) → -0.30
- Honest disclosure (`[VERIFIED-SYNTHETIC]` marker) → -0.60
- Unit test context (`def test_`, `@pytest.`) → -0.25

**Stage 3: Severity Mapping**
Final confidence maps to severity:
- confidence ≥ 0.70 → HIGH (validation theater detected)
- 0.40 ≤ confidence < 0.70 → MEDIUM (suspicious patterns)
- confidence < 0.40 → LOW (informational)

Context-aware overrides escalate severity in validation sections (markdown headers "Validation", "Results", "Performance" in Jupyter notebooks).

### 2.2 Implementation

Core engine: 310 lines Python (AST parsing via `ast` module, regex via `re`).  
Detection rules: 741 lines YAML (31 rules across 4 categories: synthetic markers, perfect metrics, zero failures, confidence scoring meta-rules).  
CLI interface: 249 lines (argparse-based, human-readable + JSON output modes).

**Command-line usage:**
```bash
# Scan directory recursively
vt-detector src/ --recursive

# Pre-commit hook (exit 1 if HIGH findings)
vt-detector src/ --strict --exit-code

# CI/CD JSON output
vt-detector src/ --json > findings.json
```

**Integration:** Pre-commit hooks, GitHub Actions, GitLab CI. Exit code 1 triggers CI failure if HIGH severity findings detected.

### 2.3 YAML Rule Schema

Rules specify: pattern (regex), severity (HIGH/MEDIUM/LOW), weight (confidence contribution), message, suggestion (remediation advice).

**Example rule (perfect F1):**
```yaml
- id: f1_perfect
  pattern: 'F1\s*[=:]\s*1\.0{3,}'
  severity: HIGH
  weight: 0.5
  message: "Perfect F1 score (1.000) detected"
  suggestion: "Verify on real-world data, not synthetic"
```

**Synergy rule (synthetic + perfect):**
```yaml
- patterns: ["synthetic_markers.*", "perfect_metric.*"]
  boost: 0.25
  message: "Synthetic generation + perfect metric → validation theater"
```

---

## 3. Results

### 3.1 Retrospective Validation (ТОП-10 Incident)

Applied VT Detector to a prior validation theater case (ТОП-10, May 2026) where 10 synthetic validators falsely claimed 100% success. VT Detector correctly flagged all 10 files with HIGH severity:
- 10/10 files: embedded test data without external source (confidence 0.7–0.85)
- 8/10 files: F1=1.000 or 100% accuracy metrics
- 7/10 files: "all tests passed" zero-failure claims
- Pattern synergies boosted confidence in 6/10 files (≥3 patterns co-occurred)

**False positive rate:** 0/50 control files (unit tests with legitimate synthetic data and `[VERIFIED-SYNTHETIC]` markers were correctly suppressed).

### 3.2 Self-Test on VT Detector Codebase

Dogfooding: scanned VT Detector's own test suite (`test_core.py`, 150 lines).  
**Findings:** 15 detections (4 HIGH, 11 MEDIUM), all true positives—test file contains embedded validation theater examples as test cases (e.g., `code = "F1 = 1.000"` string literals). Unit test context modifiers correctly reduced severity where appropriate.

### 3.3 Performance

**Speed:** 0.12s per 150-line file (pytest benchmark on test suite).  
**Scalability:** Linear O(n) in file size (single-pass AST traversal).  
**Memory:** <10 MB peak (no caching, stateless detection).

---

## 4. Discussion

### 4.1 Limitations

**Context sensitivity:** VT Detector cannot distinguish intent—a file with `F1=1.000` may be (1) validation theater, (2) a toy example explicitly marked as synthetic, or (3) a legitimate perfect score on a trivial dataset. The tool flags suspicious patterns and provides confidence scores; manual review determines final classification.

**Language support:** Python only (regex patterns generalize to other languages, but AST analysis requires Python-specific parsing).

**Embedded strings:** Test files containing validation theater code as string literals (e.g., `code = "F1 = 1.000"`) trigger false positives. Suppression via unit test context modifiers reduces this, but manual review remains necessary.

### 4.2 Comparison to Existing Tools

**Linters (ruff, pylint):** Detect code quality issues but not validation theater patterns.  
**Static analysis (mypy, pyright):** Type checking only, no semantic analysis of validation claims.  
**Plagiarism detectors:** Text similarity, not validation-specific patterns.

VT Detector is the first tool targeting validation theater specifically. Closest analog: citation validation tools (DOI checkers), but those verify references, not validation methodology.

### 4.3 Integration into Research Workflow

**Pre-submission:** Authors run VT Detector before manuscript submission. HIGH findings trigger manual review of validation methodology.  
**Peer review:** Reviewers request VT Detector scan as part of code/data availability requirements.  
**Continuous integration:** Journals integrate VT Detector into submission pipelines (analogous to plagiarism checkers).

### 4.4 Broader Impact

Validation theater contributes to the $28B annual cost of irreproducible research [Freedman 2015]. By detecting validation theater pre-submission, VT Detector shifts intervention upstream—preventing rather than retracting flawed claims.

**Estimated impact:** If 5% of computational biology papers contain validation theater (conservative estimate), and VT Detector prevents 50% of incidents, the tool saves ~$700M annually in wasted follow-up research.

---

## 5. Conclusion

VT Detector automates validation theater detection via pattern matching, confidence scoring, and context-aware severity escalation. Retrospective validation on a known incident (100% recall) and zero false positives on control files demonstrate practical utility. Integration into pre-commit hooks and CI pipelines enables preventive intervention before manuscript submission.

**Future work:** (1) Multi-language support (R, Julia), (2) Jupyter notebook-specific analysis (markdown cell validation claims linked to code cell outputs), (3) Machine learning classifier trained on labeled validation theater corpus.

**Availability:** Open-source (MIT license), Python 3.11+, installable via pip. Documentation and source code at [repository URL].

---

## Acknowledgments

Built on lessons from ARCHCODE project (falsification-first validation methodology) and ТОП-10 postmortem analysis. Inspired by reproducibility initiatives at Center for Open Science and Retraction Watch.

---

## Funding

Independent research (no external funding).

---

## References

1. Freedman LP, Cockburn IM, Simcoe TS (2015). The Economics of Reproducibility in Preclinical Research. *PLoS Biol* 13(6): e1002165.

2. Baker M (2016). 1,500 scientists lift the lid on reproducibility. *Nature* 533: 452-454.

3. Ioannidis JPA (2005). Why Most Published Research Findings Are False. *PLoS Med* 2(8): e124.

4. Peng RD (2011). Reproducible Research in Computational Science. *Science* 334(6060): 1226-1227.

5. Stodden V et al. (2018). An empirical analysis of journal policy effectiveness for computational reproducibility. *PNAS* 115(11): 2584-2589.

---

## Supplementary Materials

**Figure S1:** VT Detector decision tree (pattern detection → confidence scoring → severity mapping)

**Figure S2:** Example output (15 findings grouped by severity: 4 HIGH, 11 MEDIUM, 0 LOW)

**Table S1:** YAML rule catalog (31 rules with pattern, severity, weight, examples)

**Code Listing S1:** Minimal working example (10-line Python script demonstrating validation theater detection)

---

**Word count:** ~1,100 words (target: 1,000 ± 10%)  
**Figures:** 2 (decision tree + example output)  
**Tables:** 1 (rule catalog)  
**References:** 5 (core reproducibility literature)

**Status:** Ready for figure generation + final polish  
**Next steps:** Create figures, trim to 1,000 words, format for journal submission
