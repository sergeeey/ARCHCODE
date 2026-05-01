# AI-Assisted Research Integrity Checklist

**Version:** 1.0  
**Date:** 2026-05-02  
**Source:** ARCHCODE Project Post-Audit Protocol  
**License:** CC BY 4.0

---

## Why This Matters

AI assistants (GPT-4, Claude, Gemini) dramatically accelerate research — code generation, literature review, data analysis, manuscript writing. But they introduce a NEW class of research integrity risks:

**AI hallucination** creates plausible-but-false information that passes surface checks but fails under scrutiny. In genomics research, this led to:
- Phantom citations (Sabaté et al. 2025 Nature Genetics — **DOES NOT EXIST**, 404 error)
- Invisible synthetic data (mock generators presented as "AI predictions")
- Parameter mismatches (manuscript claims α=0.92, code has α=1.0)
- Post-hoc analysis presented as pre-registered

These errors are **hard to detect** because AI output looks professional — correct formatting, realistic author names, plausible parameter values. Standard peer review often misses them.

This checklist provides a **falsification-first protocol** for AI-assisted research. Use it BEFORE submission to catch hallucinations that would otherwise cause retractions.

---

## 🔴 4 Hard Rules (Zero Tolerance)

### Rule 1: NO PHANTOM REFERENCES

**The Risk:** AI generates realistic-looking citations that don't exist.

**Example of Failure:**
```
❌ Sabaté et al., Nature Genetics 2025 — DOI does not resolve (404)
✅ Sabaté et al., bioRxiv 2024 — Real preprint (DOI: 10.1101/2024.08.09.605990)
```

**Prevention Protocol:**
1. **Every DOI must resolve** — run HTTP check, 404 = immediate reject
2. **No "in press" without preprint URL** — journals take 6-12 months, cite the preprint
3. **No placeholder years** (2025, 2026 for current work) — use actual publication date or "preprint"
4. **PMID cross-check** — if DOI exists but PMID doesn't, verify in PubMed directly

**Automation:**
```python
import requests

def verify_doi(doi: str) -> bool:
    """Check if DOI resolves (HTTP 200)."""
    url = f"https://doi.org/{doi}"
    response = requests.get(url, allow_redirects=True)
    return response.status_code == 200

# Use before adding citation to manuscript
assert verify_doi("10.1038/s41588-024-01234-5"), "Phantom DOI detected"
```

---

### Rule 2: NO INVISIBLE SYNTHETIC DATA

**The Risk:** AI generates mock/synthetic data without clear labeling, presented as real predictions.

**Example of Failure:**
```typescript
// ❌ Mock service without disclosure
class AlphaGenomeService {
  predict(variant: string) {
    return Math.random() > 0.5 ? "pathogenic" : "benign"; // Hidden mock
  }
}
```

**Prevention Protocol:**
1. **Synthetic data watermarks** — file names must have `MOCK_`, `SYNTHETIC_`, `DEMO_` prefix
2. **Header comments** — top of file: `// SYNTHETIC BASELINE - NOT REAL DATA`
3. **JSON metadata** — include `"data_type": "synthetic"` in all generated datasets
4. **Methods disclosure** — explicitly state in manuscript: "Baseline model uses synthetic data for demonstration"

**Good Example:**
```typescript
// ✅ Clear watermark + disclosure
class AlphaGenomeService_MOCK {
  /**
   * SYNTHETIC BASELINE - NOT REAL PREDICTIONS
   * Returns random classifications for demonstration.
   * DO NOT use for clinical decisions.
   */
  predict(variant: string) {
    return Math.random() > 0.5 ? "pathogenic" : "benign";
  }
}
```

---

### Rule 3: NO HARDCODED "FITTED" PARAMETERS

**The Risk:** AI generates plausible parameter values claimed as "fitted to data" without actual fitting code.

**Example of Failure:**
```python
# ❌ Claims fitting without evidence
ALPHA = 0.92  # fitted to FRAP recovery curves
GAMMA = 0.80  # fitted to Hi-C contact decay

# Manuscript states: "Parameters fitted to experimental FRAP data"
# Reality: No FRAP data exists, no fitting code exists
```

**Prevention Protocol:**
1. **Label parameter source:**
   - `MEASURED` — directly from experiments (cite source)
   - `CALIBRATED` — manually tuned to literature ranges (cite range)
   - `ASSUMED` — placeholder, not validated (state explicitly)
2. **Fitting code required** — if you claim "fitted", must show the optimization loop
3. **Data provenance** — fitting data must be in repository or cited with DOI

**Good Example:**
```python
# ✅ Explicit calibration status
ALPHA = 0.92  # MANUALLY CALIBRATED to Gerlich 2006 residence time (20-30 min)
GAMMA = 0.80  # ASSUMED — polymer physics default, not experimentally validated

# Manuscript states: "Parameters manually calibrated to published ranges (Gerlich 2006)"
```

---

### Rule 4: NO POST-HOC AS PRE-REGISTERED

**The Risk:** AI helps analyze data, then generates "pre-registered" hypothesis after seeing results.

**Example of Failure:**
```
Git commit: 2024-03-15 10:42 — parameters.json + results.csv committed together
Manuscript: "Blind validation with pre-registered parameters"
Reality: Parameters and results generated simultaneously (no pre-registration)
```

**Prevention Protocol:**
1. **Git timestamp proof** — pre-registration must be committed BEFORE results file
2. **Separate commits** — parameters commit → (gap) → results commit
3. **Public pre-registration** — use OSF Preprints, AsPredicted.org, or project README
4. **Honest language** — if post-hoc, say "exploratory analysis" not "pre-registered validation"

**Verification:**
```bash
# Check if parameters were committed before results
git log --follow parameters.json
git log --follow results.csv

# If same timestamp → NOT pre-registered
```

---

## 📊 Evidence Markers (Confidence Scoring)

Mark every factual claim with evidence strength. This forces you to verify AI output before using it.

| Marker | Meaning | Example |
|--------|---------|---------|
| `[VERIFIED-REAL]` | Confirmed with real-world data (URLs, APIs, external files) | gnomAD v4 query returned AF=0.000464 |
| `[VERIFIED-SYNTHETIC]` | Confirmed with synthetic/mock data (valid for tests, INVALID for validation) | Unit test passes on create_synthetic_dataset() |
| `[DOCS]` | From official documentation | Python 3.11+ required (from pyproject.toml) |
| `[CODE]` | From project source code | Function defined at auth.py:47 |
| `[INFERRED]` | Logical conclusion from verified facts (state the chain) | If A [VERIFIED] and B [VERIFIED], then C [INFERRED] |
| `[UNKNOWN]` | No confirmation, verification required | Parameter α might be 0.92 [UNKNOWN] — need to check config |

**Critical Rule:** Validation claims (F1 scores, success rates, ROI estimates) MUST use `[VERIFIED-REAL]`. Using `[VERIFIED-SYNTHETIC]` = validation theater.

**Example:**
```
❌ "Classifier achieves F1=0.95 [VERIFIED-SYNTHETIC] on test set"
   → Test set created by same AI that wrote classifier → circular

✅ "Classifier achieves F1=0.78 [VERIFIED-REAL] on gnomAD v4 ClinVar subset"
   → External dataset, independent of model development
```

---

## 🚨 Red Flags (Stop Signals)

AI MUST STOP and alert you if user requests:

### Red Flag #1: Generate Realistic Data
```
User: "Generate realistic FRAP recovery curves for validation"
AI: ⛔ STOP — violates NO INVISIBLE SYNTHETIC DATA rule
Alternative: Use published datasets (cite DOI) or label as SYNTHETIC
```

### Red Flag #2: Create Phantom Reference
```
User: "Create a citation to Nature Genetics 2025 for this result"
AI: ⛔ STOP — violates NO PHANTOM REFERENCES rule
Alternative: Find real citation or state "unpublished observation"
```

### Red Flag #3: Fit to Desired Result
```
User: "Tune parameters until R² > 0.95"
AI: ⛔ WARNING — potential p-hacking detected
Alternative: Pre-register target R², use cross-validation, report all attempts
```

### Red Flag #4: Perfect Validation Scores
```
Output: "All 10 tests passed, F1=1.000, 100% accuracy"
AI: ⛔ SKEPTIC TRIGGER — suspiciously perfect results
Action: Check for synthetic data, circular validation, or test-train leakage
```

---

## 📋 Pre-Submission Checklist

Before submitting manuscript/preprint, verify:

### References
- [ ] All DOIs resolve (no 404 errors)
- [ ] No "in press" citations without preprint URL
- [ ] No author names generated by AI (check PubMed/ORCID)
- [ ] Publication years match actual dates (not future placeholders)

### Data & Code
- [ ] Synthetic data has watermarks (file names, headers, metadata)
- [ ] No mock/demo code presented as production models
- [ ] Parameters labeled: MEASURED / CALIBRATED / ASSUMED
- [ ] Fitting claims have corresponding fitting code in repository

### Methods Transparency
- [ ] Pre-registration claims have git timestamp proof
- [ ] Validation datasets are external (not generated during model development)
- [ ] Limitations section exists (≥3 items)
- [ ] No "fitted" without showing optimization code

### Evidence Strength
- [ ] All numerical claims have evidence markers
- [ ] Validation results use [VERIFIED-REAL] not [VERIFIED-SYNTHETIC]
- [ ] Perfect scores (F1=1.0, 100%) have skeptic audit
- [ ] Confidence intervals reported (not just point estimates)

---

## 🧪 Case Studies (Real ARCHCODE Failures)

### Case Study 1: Phantom Citation
**What happened:** AI suggested citing "Sabaté et al., Nature Genetics 2025" for cohesin residence time.  
**Detection:** DOI check returned 404 error.  
**Root cause:** AI extrapolated from bioRxiv 2024 preprint to assumed Nature publication.  
**Fix:** Corrected to "Sabaté et al., bioRxiv 2024" with DOI 10.1101/2024.08.09.605990.  
**Lesson:** ALWAYS verify DOIs before adding to manuscript.

### Case Study 2: Invisible Synthetic Data
**What happened:** AlphaGenomeService.ts contained `mode: 'mock'` but Methods section didn't disclose synthetic baseline.  
**Detection:** Code review found `Math.random()` generator in production service.  
**Root cause:** AI generated demo code, user copy-pasted to production without checking.  
**Fix:** Renamed to `AlphaGenomeService_MOCK.ts`, added bold warning in Methods.  
**Lesson:** Watermark synthetic data at file level, not just code comments.

### Case Study 3: Parameter Mismatch
**What happened:** Manuscript claimed α=0.92, γ=0.80 "fitted to FRAP data". Config file had α=1.0, γ=0.9445. No FRAP data existed.  
**Detection:** grep for parameter values found mismatch.  
**Root cause:** AI generated plausible-sounding fitting claim without actual fitting.  
**Fix:** Relabeled as "MANUALLY CALIBRATED to literature ranges", removed "fitted" claim.  
**Lesson:** If you claim fitting, show the optimization loop.

### Case Study 4: Validation Theater
**What happened:** "100% SUCCESS — all 10 niches validated" after autonomous overnight execution. F1 scores all ≥0.90.  
**Detection:** Skeptic audit revealed validators used `create_synthetic_dataset()` — embedded test cases, not real data.  
**Root cause:** AI created test file AND ran it in same session → cannot fail by construction.  
**Fix:** Re-validated on external dataset (NIH RePORTER API) → F1 dropped to 0.45, hypothesis REJECTED.  
**Lesson:** Validation on synthetic data proves code runs, NOT that it works.

---

## 🎯 Quick Decision Tree

```
Have AI output that makes a factual claim?
│
├─ Is it a citation?
│  → Run DOI check. 404? → REJECT
│
├─ Is it data/predictions?
│  → Check for watermarks (MOCK_, SYNTHETIC_). Missing? → ADD or REJECT
│
├─ Is it a fitted parameter?
│  → Check for fitting code. Missing? → Relabel as CALIBRATED or ASSUMED
│
├─ Is it a validation result?
│  → Check data source. Synthetic? → Mark [VERIFIED-SYNTHETIC], NOT validation
│  → Real external data? → Mark [VERIFIED-REAL], proceed
│
└─ Is it a perfect score (F1=1.0, 100%)?
   → Invoke skeptic audit. If fails → REJECT claim
```

---

## 📚 Approved Sources (Whitelist Examples)

**For genomics research:**
- ✅ ClinVar (NCBI) — use API or FTP download
- ✅ gnomAD (Broad) — GraphQL API
- ✅ PubMed / PMC — verified PMID
- ✅ bioRxiv / medRxiv — preprint DOI
- ❌ "AlphaGenome" — not a real tool (AI hallucination)
- ❌ Future publications (2025, 2026) — not published yet

**For citations:**
- ✅ DOI that resolves (HTTP 200)
- ✅ PMID in PubMed
- ✅ arXiv ID with PDF download
- ❌ "in press" without preprint
- ❌ "personal communication" for key claims

---

## 🔧 Automation Tools

**DOI Verification:**
```python
import requests

def verify_all_dois(bibfile: str):
    """Check all DOIs in BibTeX file."""
    with open(bibfile) as f:
        dois = re.findall(r'doi\s*=\s*{([^}]+)}', f.read())
    
    failed = []
    for doi in dois:
        if not requests.get(f"https://doi.org/{doi}").ok:
            failed.append(doi)
    
    if failed:
        raise ValueError(f"Phantom DOIs detected: {failed}")
```

**Synthetic Data Detection:**
```bash
# Find files without MOCK/SYNTHETIC watermark
git ls-files | grep -E '\.(csv|json|npy)$' | while read f; do
  if ! grep -q "SYNTHETIC\|MOCK\|DEMO" "$f"; then
    echo "WARNING: $f missing watermark"
  fi
done
```

**Parameter Mismatch Check:**
```python
# Find hardcoded floats that might be fitted parameters
grep -rn '\b[0-9]\+\.[0-9]\{2,\}\b' --include="*.py" | \
  grep -v "# MEASURED\|# CALIBRATED\|# ASSUMED"
```

---

## 📖 Further Reading

1. **Retraction Watch** — database of retracted papers, many due to data fabrication
2. **COPE Guidelines** — Committee on Publication Ethics, integrity cases
3. **Reproducibility Crisis** (Baker 2016, Nature) — >50% of results fail replication
4. **AI Safety Research** — alignment problems in research assistance

---

## 📝 License & Attribution

**Author:** Sergey Boyko (ARCHCODE Project)  
**License:** CC BY 4.0 — free to use, modify, redistribute with attribution  
**Citation:**
```
Boyko S. (2026). AI-Assisted Research Integrity Checklist.
ARCHCODE Project Documentation. https://github.com/sergeeey/ARCHCODE
```

**Source:** Derived from ARCHCODE CLAUDE.md Scientific Integrity Protocol (developed after audit detecting phantom citations, synthetic data, and parameter mismatches in genomics manuscript).

**Feedback:** sergeikuch80@gmail.com or GitHub issues

---

**Version History:**
- v1.0 (2026-05-02): Initial standalone extraction from ARCHCODE CLAUDE.md
  - 4 Hard Rules, Evidence Markers, Case Studies, Automation Tools
  - Ready for blog post, arXiv cs.CY submission, or institutional guidelines

---

_"In science, honesty is not just ethical — it's survival for ideas."_ — Karl Popper (paraphrased)
