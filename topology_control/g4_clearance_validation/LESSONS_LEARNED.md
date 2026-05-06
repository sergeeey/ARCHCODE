# Lessons Learned — G4-3 Week 1

**Project:** G4-clearance vulnerability hypothesis testing  
**Duration:** 2026-04-26, 5 hours  
**Outcome:** Hypothesis KILLED, Process SUCCESS

---

## Top 3 Lessons

### 1. Mock Validation Is Insufficient

**What happened:**
- Mock data: AUC=0.827 ✓
- Real data: AUC=0.467 ✗
- Collapse: -0.36 AUC points

**Why:**
- Mock data has no confounders
- Synthetic relationships too clean
- Proxy metrics work in controlled environment, fail in reality

**Fix:**
```python
# OLD (wrong):
1. Build pipeline
2. Test on mock (n=500 synthetic)
3. If pass → run on full real data

# NEW (right):
1. Build pipeline
2. Test on mock (n=500 synthetic)
3. Reality-check on SMALL real subset (n=50-100)
4. If reality-check passes → full real data
5. If reality-check fails → hypothesis likely weak
```

**Cost of lesson:** 1.5 hours wasted on full analysis of failed hypothesis  
**Saved in future:** 1-4 hours per hypothesis (quick reality-check filters out weak ones)

---

### 2. Proxy Metrics Compound Uncertainty

**What happened:**
- G4-load = MYC*10 + EGFR*5 + 100 (proxy #1)
- Helicase capacity = SUM(10 genes) (proxy #2)
- Λ-index = proxy #1 / proxy #2 (double uncertainty)

**Why failed:**
- Each proxy has error
- Ratio propagates both errors
- Real biology more complex than simple formulas

**Evidence:**
- WRN alone: ρ=-0.102 (weak but real signal)
- Λ-index (composite): ρ=0.046 (no signal)
- **Simpler > complex for weak effects**

**Fix:**
- Prefer direct measurements (WRN expression, not calculated index)
- If proxy needed, validate it first (does MYC correlate with G4-seq?)
- Avoid ratios of proxies (compounded uncertainty)

---

### 3. Pre-Registration Protects Integrity

**What happened:**
- Kill criteria: AUC < 0.65 → KILL
- Real AUC: 0.467
- Temptation: "refine G4-load formula and retry"
- Decision: **KILL per protocol**

**Why this matters:**
- Sunk cost bias: "spent 5 hours, must succeed"
- P-hacking temptation: "just one more tweak"
- Pre-registration: objective stop criterion

**Counterfactual (if no pre-registration):**
```
Try G4-load formula v2 → AUC=0.51 → still fail
Try v3 → AUC=0.58 → still fail
Try v4 + cancer-type covariate → AUC=0.67 → "success!"
→ p-hacked result, unpublishable, loss of integrity
```

**Actual (with pre-registration):**
```
AUC=0.467 < 0.65 → KILL → document → move on
→ honest negative result, publishable, integrity preserved
```

**Lesson:** Pre-registration turns potential failure into methodological success.

---

## Secondary Lessons

### 4. Pipeline Speed Matters

**Time breakdown:**
- Pipeline build: 2.5 hours
- Mock test: 0.5 hours
- Real data: 1.5 hours
- **Total: 4.5 hours** to falsify hypothesis

**Compare to traditional:**
- Write grant: weeks
- Recruit collaborators: months
- Wet-lab experiments: months
- Result: same (negative)

**Value:** Computational falsification 100× faster than wet-lab.

**Application:** Test 10 hypotheses computationally in 2 days, pick strongest 1-2 for wet-lab.

---

### 5. Negative Results Are Results

**Cultural problem:**
- Science values positive results
- Negative results = "failed experiment"
- Publication bias against negatives

**Reality:**
- G4-3 process: ✓ (pre-registered, falsified cleanly)
- G4-3 outcome: ✗ (no predictive signal)
- **This is how science should work**

**Publishable as:**
- "Λ-Index Does Not Predict G4-Helicase Dependency: A Pre-Registered Negative Result"
- Journals: PLOS ONE, F1000Research, bioRxiv
- Value: Saves others from repeating failed approach

---

### 6. Data Availability ≠ Data Quality

**What we had:**
- DepMap: 1,190 cell lines, expression + CRISPR ✓
- Coverage: All target genes present ✓
- Sample size: Adequate for statistics ✓

**What we lacked:**
- Direct G4 measurement (G4-seq)
- Drug response to G4-ligands (CX-5461)
- Validation cohort

**Lesson:** 
Large dataset with proxies < small dataset with direct measurements.

**For next hypothesis:**
Check data quality first:
- Is endpoint directly measured or proxy?
- Is predictor directly measured or calculated?
- Prefer small-n direct > large-n proxy

---

## Tactical Lessons

### 7. Code Organization

**What worked:**
```
scripts/
├── 01_download_*.py    (modular, reusable)
├── 02_calculate_*.py   (clear purpose)
├── 03_baseline_*.py    (self-contained)
└── 06_depmap_*.py      (real data adaptation)
```

**Why:**
- Each script = one job
- Easy to debug
- Easy to reuse for next hypothesis

### 8. Documentation During, Not After

**Files created during work:**
- README.md (plan)
- WEEK1_LOG.md (daily progress)
- DATA_SOURCES.md (download guide)
- DAY1_SUMMARY.md (checkpoint)

**Value:**
- Context preserved
- Decisions explained
- Easy to resume after break

**Anti-pattern:** "I'll document after it works"
- If it fails → no documentation
- If it succeeds → forgot why it works

---

## Strategic Lessons

### 9. Kill Criteria Prevent Scope Creep

**Without kill criteria:**
```
AUC=0.467 → "let's try better formula"
→ "let's add covariates"
→ "let's subset to specific cancer"
→ "let's combine with other features"
→ endless iteration, no conclusion
```

**With kill criteria:**
```
AUC=0.467 < 0.65 → KILL → DONE
→ 30 min decision time
→ move to next hypothesis
```

**Efficiency gain:** Hours to days saved per hypothesis.

---

### 10. Tracy Framework Applied to Science

**Tracy principles used:**

1. **Zero-Based Thinking:**
   - "Knowing AUC=0.467, would I start this?" → NO → KILL

2. **Law of Forced Efficiency:**
   - 27 hypotheses → kill fast, not perfect each

3. **Pre-registered kill criteria = ABCDE:**
   - A = pass kill criteria
   - E = fail kill criteria → exclude

4. **Sunk cost resistance:**
   - 5 hours invested ≠ reason to continue
   - Cost of continuation > cost of stopping

**Result:** Scientific decision-making clarity.

---

## Quantified Lessons

| Lesson | Old Approach | New Approach | Time Saved |
|--------|--------------|--------------|------------|
| Mock validation | Trust mock result | Reality-check (n=50) | 1-4 hours |
| Proxy metrics | Use calculated indices | Prefer direct measurements | Hypothesis quality ↑ |
| Pre-registration | Iterate until success | Kill per criteria | Hours to days |
| Documentation | After completion | During work | Context loss → 0 |
| Kill criteria | Subjective | Objective (AUC<0.65) | Decision time: hours → 30 min |

---

## Application to Next Hypothesis

**Checklist before starting:**

- [ ] Endpoint directly measured? (not proxy)
- [ ] Predictor directly measured? (not calculated)
- [ ] Kill criteria pre-registered?
- [ ] Reality-check plan (test on n=50 before n=1000)?
- [ ] Data quality verified (not just availability)?
- [ ] Expected effect size > 0.3? (avoid fishing for weak signals)
- [ ] Time budget: <1 day? (rapid falsification)

**If any ✗ → reconsider hypothesis.**

---

## Meta-Lesson

**Science is a falsification engine, not a validation engine.**

G4-3 outcome = ✗  
G4-3 process = ✓  

**This is the correct priority.**

Outcome success with process failure → unreproducible  
Process success with outcome failure → **honest science**

---

**Documented:** 2026-04-26  
**Time investment:** 5 hours  
**Return:** Validated pipeline + negative result + 10 transferable lessons  
**ROI:** High (lessons apply to all 26 remaining hypotheses)
