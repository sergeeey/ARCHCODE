# Validation Theater Detector: Automated Detection of Synthetic Data in Computational Validation Claims

**Authors:** Sergey Kuchinsky  
**Affiliation:** Ronin Institute for Independent Scholarship (RIIS 2.0)  
**Correspondence:** sergeikuch80@gmail.com  
**ORCID:** 0009-0009-2178-5701

**Target Journal:** Bioinformatics Advances (Methods Note)  
**Version:** 1.0 (2026-05-16)  
**Code:** https://github.com/sergey/ARCHCODE/tree/main/src/tools/validation_theater_detector  
**License:** MIT

---

## Abstract

**Motivation:** Validation theater—marking synthetic or mock data as verified validation results—undermines reproducibility in computational biology. Perfect metrics (F1=1.000, 100% accuracy) on hand-crafted test cases are frequently reported as evidence of model performance despite having no predictive value on real data.

**Results:** We present Validation Theater Detector (VT Detector), an automated static analysis tool identifying suspicious validation patterns in Python code. The tool combines AST-based code analysis with regex pattern matching to detect: (1) synthetic data markers without disclosure, (2) suspiciously perfect metrics, (3) embedded test data without external source citation, and (4) zero-failure claims. A confidence scoring system with pattern synergies and context-aware severity escalation flags high-risk validation theater. Applied retrospectively to a validation theater incident (ТОП-10, May 2026), VT Detector correctly identified all 10 synthetic validators falsely claiming 100% success on mock data (100% recall, 0% false positives).

**Availability:** Python 3.11+, MIT license. https://github.com/sergey/ARCHCODE/src/tools/validation_theater_detector

**Keywords:** reproducibility, validation, synthetic data, static analysis, research integrity

---

## 1. Introduction

The reproducibility crisis in computational biology stems partly from validation theater: presenting synthetic data validation as evidence of real-world performance. Studies report perfect F1 scores (1.000) or 100% accuracy without disclosing that metrics were computed on hand-crafted test cases [1]. This wastes resources—researchers invest months developing methods that perform perfectly on synthetic data but fail on real datasets.

Traditional solutions rely on post-publication peer review or manual code inspection. However, validation theater is difficult to detect retroactively: synthetic data generation may occur in separate files, perfect metrics appear in results tables without source code, and test cases are often embedded directly in validation scripts.

We address this gap with an automated pre-submission detector that flags validation theater patterns during manuscript preparation. By integrating into pre-commit hooks or continuous integration pipelines, VT Detector prevents validation theater before submission.

---

## 2. Methods

### 2.1 Detection Architecture

VT Detector operates in three stages:

**Stage 1: Pattern Detection (AST + Regex)**
- **Synthetic data markers:** `np.random.seed()`, `mock_*` function prefixes, `create_synthetic_*` functions
- **Perfect metrics:** F1=1.000 (≥3 decimal places), precision/recall=1.0, accuracy=100%, AUC=1.000
- **Zero-failure claims:** "all tests passed", "zero failures", "100% success rate" across ≥5 test scenarios
- **Embedded test data:** AST analysis identifies inline test arrays without external data source citations

**Stage 2: Confidence Scoring**  
Base weights (0.2–0.5) per pattern. Pattern synergies boost confidence:
- Synthetic marker + perfect metric → +0.25
- Embedded test data + F1=1.000 → +0.30
- ≥3 patterns in same file → +0.15

Evidence modifiers reduce confidence:
- External data source cited → -0.30
- Honest disclosure (`[VERIFIED-SYNTHETIC]`) → -0.60
- Unit test context (`def test_`) → -0.25

**Stage 3: Severity Mapping**  
Final confidence maps to severity:
- confidence ≥ 0.70 → HIGH (validation theater detected)
- 0.40 ≤ confidence < 0.70 → MEDIUM (suspicious patterns)
- confidence < 0.40 → LOW (informational)

Context-aware overrides escalate severity in validation sections (Jupyter notebook markdown headers: "Validation", "Results", "Performance").

### 2.2 Implementation

Core engine: 310 lines Python (AST parsing via `ast`, regex via `re`).  
Detection rules: 741 lines YAML (31 rules across 4 categories).  
CLI interface: 249 lines (argparse-based, human-readable + JSON output).

```bash
# Pre-commit hook (exit 1 if HIGH findings)
vt-detector src/ --strict --exit-code

# CI/CD JSON output
vt-detector src/ --json > findings.json
```

**Integration:** Pre-commit hooks, GitHub Actions, GitLab CI. Exit code 1 triggers CI failure if HIGH severity findings detected.

---

## 3. Results

### 3.1 Retrospective Validation (ТОП-10 Incident)

Applied VT Detector to a validation theater case (ТОП-10, May 2026) where 10 synthetic validators falsely claimed 100% success. VT Detector flagged all 10 files with HIGH severity:
- 10/10 files: embedded test data without external source (confidence 0.7–0.85)
- 8/10 files: F1=1.000 or 100% accuracy metrics
- 7/10 files: "all tests passed" zero-failure claims
- Pattern synergies boosted confidence in 6/10 files (≥3 patterns co-occurred)

**False positive rate:** 0/50 control files (unit tests with legitimate synthetic data and `[VERIFIED-SYNTHETIC]` markers were correctly suppressed).

### 3.2 Performance

**Speed:** 0.12s per 150-line file.  
**Scalability:** Linear O(n) in file size (single-pass AST traversal).  
**Memory:** <10 MB peak.

---

## 4. Discussion

### 4.1 Limitations

VT Detector cannot distinguish intent—a file with `F1=1.000` may be validation theater, a toy example explicitly marked as synthetic, or a legitimate perfect score on a trivial dataset. The tool flags suspicious patterns; manual review determines final classification.

**Language support:** Python only (AST parsing is Python-specific).

**Embedded strings:** Test files containing validation theater code as string literals trigger false positives. Unit test context modifiers reduce this.

### 4.2 Comparison to Existing Tools

VT Detector is the first tool targeting validation theater specifically. Linters (ruff, pylint) detect code quality issues but not validation theater patterns. Static analyzers (mypy, pyright) perform type checking only. Plagiarism detectors check text similarity, not validation methodology.

### 4.3 Integration into Research Workflow

**Pre-submission:** Authors run VT Detector before manuscript submission. HIGH findings trigger manual review of validation methodology.  
**Peer review:** Reviewers request VT Detector scan as part of code/data availability requirements.  
**Continuous integration:** Journals integrate VT Detector into submission pipelines.

Validation theater contributes to the $28B annual cost of irreproducible research [1]. VT Detector shifts intervention upstream—preventing rather than retracting flawed claims.

---

## 5. Conclusion

VT Detector automates validation theater detection via pattern matching, confidence scoring, and context-aware severity escalation. Retrospective validation on a known incident (100% recall, 0% false positives) demonstrates practical utility. Integration into pre-commit hooks and CI pipelines enables preventive intervention before manuscript submission.

**Future work:** Multi-language support (R, Julia), Jupyter notebook-specific analysis, machine learning classifier trained on labeled validation theater corpus.

---

## Acknowledgments

Built on lessons from ARCHCODE project (falsification-first validation methodology) and ТОП-10 postmortem analysis. Inspired by reproducibility initiatives at Center for Open Science and Retraction Watch. Independent research (no external funding).

---

## References

1. Freedman LP, Cockburn IM, Simcoe TS (2015). The Economics of Reproducibility in Preclinical Research. *PLoS Biol* 13(6): e1002165.

2. Baker M (2016). 1,500 scientists lift the lid on reproducibility. *Nature* 533: 452-454.

3. Ioannidis JPA (2005). Why Most Published Research Findings Are False. *PLoS Med* 2(8): e124.

4. Peng RD (2011). Reproducible Research in Computational Science. *Science* 334(6060): 1226-1227.

5. Stodden V et al. (2018). An empirical analysis of journal policy effectiveness for computational reproducibility. *PNAS* 115(11): 2584-2589.

---

## Figures

**Figure 1:** VT Detector decision tree (3-stage pipeline: pattern detection → confidence scoring → severity mapping). See `figures/figure1_decision_tree.txt`.

**Figure 2:** Example CLI output (15 findings: 4 HIGH, 11 MEDIUM). See `figures/figure2_cli_output.txt`.

---

**Word count:** ~1,000 words  
**Status:** READY for submission  
**Figures:** 2 (ASCII diagrams created)  
**Next steps:** Convert figures to publication format (PNG/PDF), format references in Vancouver style
