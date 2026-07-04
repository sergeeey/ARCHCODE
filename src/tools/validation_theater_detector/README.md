# Validation Theater Detector

**Status:** In Development (Day 1/3)  
**ROI Score:** 19/20 (from harvest scan)  
**Origin:** ARCHCODE ТОП-10 postmortem (May 2026) — prevented $1.4M disaster

---

## Purpose

Автоматическая детекция validation theater — когда synthetic/mock данные выдаются за реальную валидацию результатов.

**Problem this solves:**
- F1=1.000 на synthetic data → marked [VERIFIED] → submission disaster
- Embedded test cases (inline data) без external source → circular validation
- "100% success" across all tests → suspiciously perfect, likely synthetic
- Zero failures → tests too weak or data hand-crafted

**Real-world impact:**
- ТОП-10 (May 2026): 100% SUCCESS on synthetic, 0-50% on real data
- ARCHCODE router (Apr 2026): AUC=0.98 on category artifact, not 3D structure
- Reproducibility crisis: $28B/year (Freedman 2015)

---

## Architecture

### Core Components

```
src/tools/validation_theater_detector/
├── __init__.py          — public API
├── core.py              — detection engine (AST + regex + heuristics)
├── rules/               — YAML-based detection patterns
│   ├── synthetic_markers.yaml       — code patterns (np.random.seed, mock_*)
│   ├── metric_patterns.yaml         — suspicious metrics (F1=1.000, 100%)
│   └── confidence_scoring.yaml      — scoring rules
├── cli.py               — command-line interface
└── tests/
    └── test_vt_detector.py
```

### Detection Pipeline (3 stages)

**Stage 1: Code Pattern Detection (AST + regex)**
- Scan for synthetic data markers: `np.random.seed()`, `mock_*`, `create_synthetic_*`
- Detect embedded test cases: `data = [("input", "label"), ...]` without external API/file
- Flag inline heredocs with test data: `python -c "..."`, `python <<EOF`

**Stage 2: Metric Analysis**
- Round perfect numbers: F1=1.000, precision=1.0, accuracy=100%
- Zero failures: "all tests passed", "no edge cases", "100% success"
- Suspiciously high success rate: actual >> expected base rate

**Stage 3: Context Verification**
- Check for external data source citations (URLs, API calls, file paths)
- Verify test/data files predate validation code (git timestamp)
- Cross-check [VERIFIED] markers against evidence type (REAL vs SYNTHETIC)

### Output Format

```python
TheaterFinding(
    file="validation.py",
    line=42,
    severity=Severity.HIGH,  # HIGH | MEDIUM | LOW
    pattern="embedded_test_data",
    message="Inline test data without external source",
    confidence=0.85,
    suggestion="Cite external dataset URL or mark as [VERIFIED-SYNTHETIC]"
)
```

### Severity Classification

| Severity | Criteria | Action |
|----------|----------|--------|
| **HIGH** | Synthetic data + [VERIFIED] marker OR F1=1.000 + validation claim | Block commit |
| **MEDIUM** | Embedded test data OR round perfect metrics | Warning |
| **LOW** | Suspicious patterns but unclear context | Info |

### Confidence Scoring

Formula: `confidence = Σ(pattern_weight × match_strength)`

| Pattern | Weight | Match Strength |
|---------|--------|----------------|
| `np.random.seed()` | 0.3 | 1.0 if found |
| Embedded test data | 0.4 | 1.0 if no external source cited |
| F1=1.000 | 0.5 | 1.0 if in validation context |
| Zero failures | 0.3 | 1.0 if ≥5 tests |
| No URL citations | 0.2 | 1.0 if no http:// or API calls |

**Thresholds:**
- confidence ≥ 0.7 → HIGH severity
- 0.4 ≤ confidence < 0.7 → MEDIUM
- confidence < 0.4 → LOW

---

## Usage

### CLI

```bash
# Scan single file
vt-detector validation.py

# Scan directory recursively
vt-detector src/ --recursive

# Strict mode (HIGH only)
vt-detector src/ --strict

# JSON output (for CI/CD)
vt-detector src/ --json > findings.json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validation-theater-detector
        name: Validation Theater Detector
        entry: vt-detector
        language: python
        args: ["--strict"]
        files: \.(py|ipynb)$
```

### Python API

```python
from validation_theater_detector import detect_theater, Severity

findings = detect_theater("src/", recursive=True)

high_severity = [f for f in findings if f.severity == Severity.HIGH]
if high_severity:
    print(f"⛔ BLOCKED: {len(high_severity)} HIGH severity findings")
    for finding in high_severity:
        print(f"  {finding.file}:{finding.line} — {finding.message}")
    exit(1)
```

---

## Detection Rules (Examples)

### Rule 1: Synthetic Data Markers

```yaml
# rules/synthetic_markers.yaml
- pattern: "np\\.random\\.seed\\("
  severity: MEDIUM
  weight: 0.3
  message: "Random seed detected — likely synthetic data"
  
- pattern: "mock_|MOCK_|create_synthetic_"
  severity: HIGH
  weight: 0.4
  message: "Synthetic data function call"
```

### Rule 2: Embedded Test Data

```python
# Detected pattern (AST analysis):
test_data = [
    ("abstract 1", "LABEL"),
    ("abstract 2", "LABEL"),
]

# Missing: external source citation
# → HIGH severity if used in validation context
```

### Rule 3: Perfect Metrics

```yaml
# rules/metric_patterns.yaml
- pattern: "F1\\s*=\\s*1\\.0{3,}"
  severity: HIGH
  weight: 0.5
  message: "Perfect F1 score (1.000) — suspiciously round"
  
- pattern: "100%|100\\.0%"
  severity: MEDIUM
  weight: 0.3
  message: "100% success rate — verify on real data"
```

---

## Testing Strategy

### Test Cases (test_vt_detector.py)

1. **Positive cases (should detect):**
   - File with `np.random.seed()` + validation claim → HIGH
   - Embedded test data without URL → HIGH
   - F1=1.000 in results section → HIGH
   - "All tests passed" across 5+ scenarios → MEDIUM

2. **Negative cases (should NOT detect):**
   - `np.random.seed()` in unit test (not validation) → LOW or skip
   - F1=0.987 (not round) → skip
   - External dataset cited: `response = requests.get("...")` → skip

3. **Edge cases:**
   - Synthetic data + [VERIFIED-SYNTHETIC] marker → LOW (honest disclosure)
   - F1=1.000 on toy dataset (explicitly marked) → MEDIUM

### Validation

Run detector on ARCHCODE codebase (self-test):
- Should flag ТОП-10 synthetic validators (retrospective)
- Should NOT flag honest [VERIFIED-SYNTHETIC] markers
- Should NOT flag external data sources (ClinVar API, ENCODE downloads)

---

## Roadmap

### Phase 1 (Day 1): Core Engine ✅ IN PROGRESS
- [x] Project structure
- [ ] AST-based code analysis
- [ ] Pattern matching engine
- [ ] Confidence scoring

### Phase 2 (Day 2): Detection Rules
- [ ] YAML schema design
- [ ] Synthetic markers catalog
- [ ] Metric patterns
- [ ] Confidence scoring rules

### Phase 3 (Day 3): CLI + Integration
- [ ] Command-line interface
- [ ] Pre-commit hook integration
- [ ] Test suite
- [ ] Self-test on ARCHCODE codebase

---

## Success Criteria

- **Retrospective test:** Detect ТОП-10 synthetic validators (100% recall)
- **False positive rate:** <10% on ARCHCODE codebase
- **Performance:** <1 sec per 1000 lines of code
- **Usability:** 1-liner CLI command, zero-config pre-commit hook

---

## References

- ТОП-10 postmortem (2026-05-01): validation theater incident
- ARCHCODE falsification lessons: `docs/ADR-027_73bp_cluster_validation.md`
- Skeptic triggers: `~/.claude/rules/skeptic-triggers.md`
- Audit verification gate: `~/.claude/rules/audit-verification-gate.md`

---

**Last Updated:** 2026-05-16  
**Status:** Day 1/3 — Core engine in progress  
**Next:** Implement AST-based pattern detection
