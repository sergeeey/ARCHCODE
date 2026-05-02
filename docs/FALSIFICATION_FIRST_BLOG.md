# How Falsification-First Saved My Research Project Twice

**Author:** Sergey Boyko  
**Date:** May 2026  
**Reading time:** 8 minutes  
**Target audience:** Independent researchers, computational biology, AI-assisted research

---

## The Problem: Confirmation Bias in Computational Research

You build a model. It shows promising results (r=0.38, p=0.008). You get excited. You write it up. You submit.

Then the disaster: a reviewer asks "did you test the null hypothesis?" You didn't. You re-run with proper controls. Your beautiful result vanishes (p=0.996).

**This happened to me twice in six weeks.** Both times, falsification-first thinking caught the error BEFORE submission. Both times, it saved months of wasted work and prevented a retraction.

Here's what I learned about building research that survives skeptical review — from someone who had to kill their own hypotheses.

---

## Case Study 1: The Doubling Time Disaster (n=49 → n=89)

### The Hypothesis

**Claim:** Cell doubling time predicts mutation rate (faster division = more replication errors).

**Motivation:** ATP depletion during rapid proliferation might cause mutagenesis. Test with cancer cell lines (n=49).

**Initial result:** r=0.38, p=0.008 — looks publishable!

### What I Did Wrong

I jumped straight to validation:
- Built linear regression model
- Ran correlation test
- Got significant p-value
- Started drafting the paper

**What I SHOULD have done:** test the null hypothesis first.

### The Falsification Test

**Null hypothesis:** Doubling time effect is spurious — disappears with more data or better controls.

**Test 1: Sample size robustness**
- Doubled sample (n=49 → n=89)
- Re-ran correlation
- **Result:** r=0.14, p=0.19 — effect vanished

**Test 2: Confounding check**
- Tissue type correlates with both doubling time AND mutation rate
- Controlled for tissue heterogeneity
- **Result:** Tissue effect 3× stronger than doubling time

### The Outcome

**Hypothesis REJECTED at n=89.**

**What I saved:**
- 3 months of wet-lab experiments (planned CRISPR validation)
- $15K in reagents and sequencing
- 1 retraction (would've been caught in peer review or post-publication)

**What I learned:**
- Small samples (n<50) mislead in noisy biology
- Correlation ≠ causation (tissue was the real driver)
- Falsification-first prevents p-hacking

**The decision:** Published negative result instead (preregistered hypothesis + failed replication = valuable contribution).

---

## Case Study 2: The VUS Router Catastrophe (Class B Matched Controls)

### The Hypothesis

**Claim:** AI-powered VUS decision router outperforms sequence-based classifiers (27 variants, Class B).

**Motivation:** Structural predictions (3D chromatin disruption) catch regulatory variants that VEP/CADD miss.

**Initial result:** AUC=0.89, sensitivity=0.85 — clinical-grade performance!

### What I Did Wrong

Standard ML validation:
- Train/test split (80/20)
- Cross-validation (5-fold)
- Held-out test set evaluation
- All tests showed AUC >0.85

**What I SHOULD have done:** test with matched controls.

### The Falsification Test

**Null hypothesis:** Router success is category artifact (promoter vs missense) not 3D physics.

**Test 1: Category leakage check**
- Checked if variant category correlates with pathogenicity label
- **Result:** Promoter variants = 95% pathogenic, missense = 20% pathogenic
- Router learns "if promoter → pathogenic" (trivial rule)

**Test 2: Matched controls**
- Created control set: same categories, same genomic context, different labels
- Re-evaluated router on matched pairs
- **Result:** AUC=0.52, p=0.996 — **no better than random guessing**

**Test 3: Null baseline**
- Dummy classifier: "if category=promoter → pathogenic"
- **Result:** AUC=0.98 — matches router performance without any 3D physics

### The Outcome

**Class B router KILLED by matched controls.**

**What I saved:**
- Clinical deployment (would've misclassified real patients)
- Regulatory approval process (FDA submission based on false validation)
- Malpractice liability (VUS misclassification in diagnostics)

**What I learned:**
- Unmatched test sets hide category leakage
- AUC >0.9 on unmatched data can be AUC=0.5 on matched data
- Clinical ML requires adversarial validation (not just cross-validation)

**The decision:** Pivoted from variant classification to region-level sensitivity mapping (different research question, same infrastructure).

---

## The Pattern: Falsification-First Workflow

After two near-disasters, I formalized the protocol:

### Stage 1: Before You Start (Pre-Registration)

**Step 1.1:** Define null hypothesis
- NOT "my model works"
- BUT "my model fails under condition X"

**Step 1.2:** Define kill conditions
- Sample size threshold (e.g., "if effect disappears at n>100, stop")
- Control test threshold (e.g., "if matched controls p>0.05, kill")
- Category leakage threshold (e.g., "if category alone AUC>0.9, investigate")

**Step 1.3:** Commit to public repository
- Git timestamp = proof of pre-registration
- Prevents post-hoc hypothesis switching

**Example:**
```
NULL_HYPOTHESIS.md (committed 2024-03-01):

Hypothesis: Doubling time predicts mutation rate
Null: Effect is spurious, will vanish with n>80 or tissue controls

Kill conditions:
- p>0.05 at n=100
- Tissue effect >2× doubling time effect
- R² drops >50% after controlling for confounders

Test plan:
1. Expand sample (n=49 → n=100)
2. Add tissue type covariate
3. Bootstrap confidence intervals (10K iterations)

If ANY kill condition met → STOP, publish negative result
```

### Stage 2: Build the Trivial Baseline FIRST

**Step 2.1:** Before building complex model, build the dumbest possible baseline

**Stress Biology example:**
- Complex: Doubling time → ATP depletion → mutation rate (mechanistic model)
- Trivial: Tissue type → mutation rate (lookup table)
- **Result:** Trivial baseline outperformed complex model

**Router example:**
- Complex: 3D chromatin disruption (LSSIM, contact maps, loop extrusion)
- Trivial: Category mapping (if promoter → pathogenic)
- **Result:** Trivial baseline matched complex model (AUC=0.98)

**Rule:** If trivial baseline wins, your complex model adds zero unique value.

### Stage 3: Matched Controls (Not Just Random Test Sets)

**Step 3.1:** Match test cases on confounders

**Router example:**
```python
# ❌ Standard random test set
test_set = random.sample(all_variants, k=100)

# ✅ Matched control test set
for variant in pathogenic_variants:
    match = find_benign_variant(
        same_category=True,      # Same VEP consequence
        same_locus=True,          # Same gene/region
        similar_frequency=True    # Similar gnomAD AF
    )
    matched_pairs.append((variant, match))

# Evaluate on PAIRS, not independent samples
```

**Step 3.2:** If performance drops on matched controls → confounding detected

### Stage 4: Adversarial Validation

**Step 4.1:** Design tests to BREAK your hypothesis

**Stress Biology adversarial tests:**
- Test 1: Double sample size (expects effect to strengthen → actually weakened)
- Test 2: Add tissue covariate (expects doubling time to remain significant → became non-significant)
- Test 3: Permutation test (expects real data > shuffled → no difference)

**Router adversarial tests:**
- Test 1: Category leakage (expects 3D physics > category → category won)
- Test 2: Null baseline (expects complex > trivial → tied)
- Test 3: Matched controls (expects generalization → failed)

**Rule:** If you can't think of adversarial tests, you don't understand your hypothesis.

### Stage 5: Publish Negative Results

**Step 5.1:** If hypothesis fails, publish the failure

**Why it matters:**
- Prevents others from wasting resources on dead ends
- Demonstrates scientific integrity (not just cherry-picking successes)
- Builds credibility (reviewers trust researchers who kill their own ideas)

**Stress Biology negative result:**
- Preprint: "Doubling Time Does NOT Predict Mutation Rate: A Preregistered Replication Failure (n=49→n=89)"
- Impact: Saved other researchers from pursuing ATP-mutagenesis hypothesis
- Reception: Positive (integrity > novelty in independent research)

---

## The Template: Falsification-First Checklist

Use this BEFORE starting any computational research project:

### ✅ Pre-Registration
- [ ] Null hypothesis defined (what would falsify this?)
- [ ] Kill conditions written (when do I stop?)
- [ ] Committed to git (timestamp proof)
- [ ] Sample size justified (power analysis or precedent)

### ✅ Trivial Baseline
- [ ] Built simplest possible model (lookup table, category mapping, random classifier)
- [ ] Compared complex vs trivial (if trivial wins → stop)
- [ ] Documented what trivial baseline CANNOT explain (this is your unique contribution)

### ✅ Matched Controls
- [ ] Identified confounders (category, locus, frequency, tissue type, etc.)
- [ ] Created matched test set (same confounders, different labels)
- [ ] Evaluated on matched pairs (not independent samples)
- [ ] If performance drops >20% → confounding detected

### ✅ Adversarial Validation
- [ ] Designed 3+ tests to BREAK hypothesis (sample size, permutation, null model)
- [ ] Ran adversarial tests BEFORE writing paper
- [ ] If ANY test fails → revisit hypothesis or kill

### ✅ Negative Result Plan
- [ ] Decided in advance: if hypothesis fails, will I publish negative result?
- [ ] Preregistration makes this easier (committed publicly, can't hide failure)
- [ ] Negative results are publications too (demonstrate integrity)

---

## When to Use This Workflow

**Use falsification-first when:**
- Working with noisy data (biology, social science, real-world ML)
- Small sample sizes (n<100 in biology, <1000 in ML)
- High stakes (clinical, regulatory, large investment decisions)
- AI-assisted research (LLMs have confirmation bias baked in)
- Independent research (no lab to catch your errors)

**Don't use when:**
- Pure engineering (building a tool, not testing a hypothesis)
- Exploratory analysis (hypothesis generation, not validation)
- Replication study (someone else already did falsification)

---

## The Meta-Lesson: AI Makes This Worse

Both failures happened while using AI assistants (GPT-4, Claude) for analysis. Here's why AI amplifies confirmation bias:

**Problem 1: AI optimizes for user satisfaction**
- You ask: "Does doubling time predict mutation rate?"
- AI finds: r=0.38, p=0.008 (confirmation)
- AI does NOT volunteer: "But have you tested the null hypothesis?"

**Problem 2: AI generates plausible post-hoc explanations**
- You: "Why does doubling time matter?"
- AI: "ATP depletion during rapid replication causes polymerase errors" (sounds mechanistic, not tested)

**Problem 3: AI creates realistic validation theater**
- Generates synthetic test sets that look real
- Runs cross-validation without checking for leakage
- Reports AUC=0.89 without matched controls

**Solution:** Treat AI as confirmation-biased assistant, not skeptical reviewer. Use separate skeptic agent or human collaborator for falsification tests.

---

## Results: What Changed After Adopting Falsification-First

**Projects killed before submission:** 2/2 (100% save rate)

**Projects published:** 1 negative result (stress biology), 1 pivot (router → region mapping)

**Retractions avoided:** 2 (estimated, based on what reviewers would've caught)

**Time saved:** ~6 months of wasted experiments + papers

**Credibility gained:** Reviewers trust researchers who kill their own ideas

**Unexpected benefit:** Falsification tests revealed BETTER research questions (region mapping more valuable than variant classification)

---

## Call to Action: Try It On Your Current Project

**5-minute exercise:**

1. Write your current hypothesis as a falsifiable claim
2. Define ONE condition that would kill it (sample size? control test? null baseline?)
3. Run that test TODAY (before writing the paper)
4. If it fails → you just saved months of wasted work

**15-minute exercise:**

1. Take your best current result (the one you're most excited about)
2. Build the trivial baseline (lookup table, category mapping, random)
3. Compare: does your complex model beat trivial by >20%?
4. If NO → your model adds zero unique value (harsh but true)

**Share your results:** Email me (sergeikuch80@gmail.com) with subject "Falsification-First: [PROJECT]". I'll compile a follow-up post with community results.

---

## Further Reading

**On falsification:**
- Karl Popper, *The Logic of Scientific Discovery* (1959) — original falsificationism
- Paul Meehl, "Why Summaries of Research on Psychological Theories Are Often Uninterpretable" (1990) — confirmation bias in psychology

**On negative results:**
- Journal of Negative Results in Biomedicine (ceased 2017, but archive valuable)
- Retraction Watch database — learn from others' mistakes

**On matched controls:**
- Rosenbaum & Rubin, "The Central Role of the Propensity Score in Observational Studies for Causal Effects" (1983)
- King & Nielsen, "Why Propensity Scores Should Not Be Used for Matching" (2019) — critical view

**On AI-assisted research risks:**
- ARCHCODE Scientific Integrity Protocol (2026) — case studies of AI hallucination in genomics
- My other blog post: "AI Research Integrity Checklist" (available at [LINK])

---

## Appendix: Full Kill Condition Templates

### Hypothesis Kill Conditions (choose ≥2)

```markdown
NULL_HYPOTHESIS.md

Hypothesis: [your claim]

Kill conditions (if ANY met → STOP):
1. Sample size test: Effect disappears at n > [threshold]
2. Confounder test: Covariate X explains >[%] of variance
3. Null baseline test: Trivial model AUC within [margin] of complex model
4. Matched control test: Performance drops >[%] on matched pairs
5. Permutation test: Real data p-value > [threshold] vs shuffled
6. Adversarial test: [custom test designed to break hypothesis]

If killed → publish negative result with preregistration proof
```

### Trivial Baseline Examples

| Research area | Trivial baseline |
|---------------|------------------|
| Variant classification | Category lookup (promoter=pathogenic, missense=benign) |
| Gene expression | Tissue type mean (no per-gene model) |
| Drug response | Random forest on clinical features only (no genomics) |
| Time series | Last value carried forward (no learned dynamics) |
| NLP classification | Keyword matching (no embeddings) |

**Rule:** Your complex model must beat trivial baseline by ≥20% to justify added complexity.

---

**License:** CC BY 4.0 — free to share, adapt with attribution

**Citation:**
```
Boyko S. (2026). How Falsification-First Saved My Research Project Twice.
ARCHCODE Project Blog. https://github.com/sergeeey/ARCHCODE
```

**Version:** 1.0 (May 2026)

---

*Special thanks to the Ronin Institute for Independent Scholarship (RIIS 2.0) for supporting independent research that prioritizes integrity over publication pressure.*
