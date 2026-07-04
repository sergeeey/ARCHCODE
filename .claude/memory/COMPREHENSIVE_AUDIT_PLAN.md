# COMPREHENSIVE PROJECT AUDIT PLAN
**Date:** 2026-04-29
**Scope:** Complete codebase integrity verification
**Duration:** Deep systematic check (no rush)

---

## AUDIT OBJECTIVES

1. **Code Integrity** — no mock data, no fabricated metrics
2. **Scientific Honesty** — real p-values, honest null results
3. **Data Provenance** — all results traceable to real computations
4. **Manuscript Consistency** — text matches data files
5. **Configuration Conflicts** — no contradicting parameters
6. **Git History** — no result manipulation via amends

---

## AUDIT PHASES

### PHASE 1: Scripts Audit (Code Integrity)
**Target:** All `.py` and `.ts` files in `scripts/`
**Checks:**
- [ ] No `MOCK_`, `SYNTHETIC_`, `DEMO_` prefixes without disclosure
- [ ] No random data generators disguised as real data
- [ ] No hardcoded "fitted" parameters without data source
- [ ] All imports/dependencies exist
- [ ] No phantom API calls (AlphaGenome mock mode, etc.)
- [ ] Print/console.log statements use real data, not placeholders

**Method:**
```bash
# Check for mock indicators
grep -r "MOCK\|SYNTHETIC\|DEMO\|mock.*mode\|placeholder" scripts/ --include="*.py" --include="*.ts"

# Check for random generators
grep -r "random\|rand\|np\.random\|Math\.random" scripts/ --include="*.py" --include="*.ts"

# Check for fitted parameters
grep -r "fitted\|calibrated\|optimized" scripts/ --include="*.py" --include="*.ts"
```

---

### PHASE 2: Results Data Integrity
**Target:** All files in `results/`
**Checks:**
- [ ] CSV files contain real data (not placeholder values like 0.999, 1.000)
- [ ] p-values are realistic (not suspiciously round: 0.001, 0.05, etc.)
- [ ] Sample sizes match between files (n=50 in text = n=50 in CSV)
- [ ] No duplicate rows (copy-paste artifacts)
- [ ] Effect sizes (Cohen's d) match statistical expectations
- [ ] Timestamps in files match git commit dates

**Method:**
```bash
# Check for suspiciously perfect correlations
grep -r "r=1.0\|r=0.999\|correlation.*1.00" results/

# Check for round p-values
grep -r "p=0.001\|p=0.01\|p=0.05\|p=1.0" results/

# Verify sample sizes consistency
grep -r "n=" results/ | sort | uniq
```

---

### PHASE 3: Manuscript-Data Consistency
**Target:** `manuscript/*.typ` vs `results/*.csv`
**Checks:**
- [ ] H1 validation numbers in text match `results/H1_*.txt`
- [ ] H2 phase boundary rejection stats match `results/phase_boundary/correlation_results.txt`
- [ ] H4 codeword distance values match `results/codeword_distances.csv`
- [ ] No contradictions between abstract and results sections
- [ ] Figures match data files (S2-S4)

**Method:**
- Extract all quantitative claims from manuscript
- Cross-check against results files
- Flag discrepancies

---

### PHASE 4: Scientific Honesty Check
**Target:** All hypothesis tests and claims
**Checks:**
- [ ] Null results documented (H2 REJECTED, H4 REINTERPRETED)
- [ ] No p-hacking indicators (multiple tests without correction)
- [ ] Pre-registration timestamps (if claimed)
- [ ] No selective reporting (all loci tested are reported)
- [ ] Honest effect size interpretation (d=1.36 = "large", not "medium")
- [ ] Limitations section exists and accurate

**Red Flags to Check:**
- Claims of "pre-registered" without git proof
- Missing negative results
- Suspiciously good fit (R²>0.99 without explanation)
- Parameters that match literature too perfectly

---

### PHASE 5: Parameter Consistency Audit
**Target:** All config files and constants
**Checks:**
- [ ] `src/domain/constants/biophysics.ts` parameters match manuscript Methods
- [ ] LSSIM thresholds consistent (0.95 everywhere?)
- [ ] Genomic coordinates consistent across scripts
- [ ] No conflicts between Python and TypeScript parameters

**Method:**
```bash
# Find all parameter definitions
grep -r "ALPHA\|GAMMA\|K_BASE\|threshold" src/ scripts/ --include="*.ts" --include="*.py"

# Check LSSIM threshold consistency
grep -r "0.95\|0.90\|LSSIM" scripts/ manuscript/
```

---

### PHASE 6: Mock Data Detection
**Target:** Entire codebase
**Checks:**
- [ ] No AlphaGenome mock mode in production code
- [ ] No synthetic contact matrices without watermark
- [ ] No fabricated ClinVar IDs
- [ ] No phantom DOIs (check against CLAUDE.md violations)

**Known Issues from CLAUDE.md:**
- Sabaté et al. 2025 (Nature Genetics) — DOES NOT EXIST ❌
- AlphaGenome mock mode disclosure ✅ (should be documented)

**Method:**
```bash
# Check for known violations
grep -r "Sabaté.*2025\|Nature Genetics 2025" manuscript/ results/

# Check AlphaGenome usage
grep -r "AlphaGenome\|mode.*mock" scripts/ src/
```

---

### PHASE 7: Git History Integrity
**Target:** Commit history
**Checks:**
- [ ] No amended commits after results known
- [ ] No force pushes that hide failures
- [ ] Timestamps match workflow (simulation → analysis → manuscript)
- [ ] No deleted branches hiding failed hypotheses

**Method:**
```bash
# Check for amended commits
git log --all --oneline | grep "amend\|fixup"

# Check reflog for force operations
git reflog | grep "reset --hard\|rebase"
```

---

### PHASE 8: Cross-File Consistency
**Target:** All files with shared data
**Checks:**
- [ ] HBB atlas: n=1103 consistent across all scripts
- [ ] TP53 atlas: n=2794 consistent
- [ ] BRCA1 atlas: n=10682 consistent
- [ ] Pearl count: 20 variants (not 15, not 25)
- [ ] Genomic coordinates match GRCh38

**Method:**
- Extract n= from all files
- Compare across scripts, results, manuscript
- Flag inconsistencies

---

### PHASE 9: Dependency & Environment Check
**Target:** All imports and requirements
**Checks:**
- [ ] All Python packages in requirements.txt exist
- [ ] All npm packages in package.json exist
- [ ] No missing imports
- [ ] No version conflicts
- [ ] Reproducible environment

**Method:**
```bash
# Check Python imports
python -c "import pandas, numpy, scipy, matplotlib, seaborn" || echo "FAIL"

# Check TypeScript imports
npm list || echo "FAIL"
```

---

### PHASE 10: Final Integrity Verification
**Target:** Complete system
**Checks:**
- [ ] README.md claims match actual capabilities
- [ ] CLAUDE.md scientific integrity rules followed
- [ ] No technical debt hiding quality issues
- [ ] All figures regenerable from data
- [ ] Manuscript compiles without errors

---

## AUDIT EXECUTION ORDER

1. **Phase 6** (Mock Data Detection) — CRITICAL, check first
2. **Phase 1** (Scripts Audit) — verify code integrity
3. **Phase 2** (Results Data) — verify data authenticity
4. **Phase 3** (Manuscript Consistency) — cross-check claims
5. **Phase 4** (Scientific Honesty) — null results documented
6. **Phase 5** (Parameter Consistency) — no conflicts
7. **Phase 7** (Git History) — no manipulation
8. **Phase 8** (Cross-File Consistency) — sample sizes match
9. **Phase 9** (Dependencies) — reproducibility
10. **Phase 10** (Final Verification) — compilation test

---

## SUCCESS CRITERIA

**PASS:** All phases complete with 0 critical issues
**WARNING:** Minor inconsistencies (document, don't block)
**FAIL:** Fabricated data, phantom references, or result manipulation detected

---

## OUTPUT FORMAT

Each phase produces:
```
PHASE X: [NAME] — STATUS
  ✅ PASS: [check description]
  ⚠️  WARNING: [issue + mitigation]
  ❌ FAIL: [critical issue + location]
  
Summary: X/Y checks passed
```

Final report: `AUDIT_REPORT_20260429.md`
