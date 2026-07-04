# Multi-Agent Research Orchestration: A Genomics Case Study

**Author:** Sergey Boyko  
**Project:** ARCHCODE — 3D Chromatin Variant Analysis  
**Date:** May 2026  
**Reading time:** 10 minutes

---

## The Problem: Single-Agent AI Limitations

You're using Claude/GPT-4 for research. It's helpful — writes code, analyzes data, drafts papers. But it has blind spots:

**Confirmation bias:** AI optimizes for user satisfaction → confirms your hypothesis instead of challenging it.

**Scope creep:** AI suggests interesting extensions → you add features instead of shipping.

**Validation theater:** AI creates synthetic test data → reports 100% success → you discover it's circular validation.

**Context overflow:** Single conversation reaches 200K tokens → compaction loses critical state.

These aren't bugs. They're limitations of **single-agent architecture**. One AI assistant cannot simultaneously:
- Execute your plan (builder)
- Challenge your assumptions (skeptic)
- Prioritize ruthlessly (strategist)
- Verify claims independently (auditor)

**Solution:** Multi-agent orchestration — specialized agents with isolated context, each optimized for ONE cognitive mode.

This is how I saved the ARCHCODE project twice.

---

## The ARCHCODE Story: 18 Months, 2 Near-Disasters, 4 Agent Interventions

**Project goal:** Predict pathogenic variants from 3D chromatin disruption (genomics tool for clinical variant interpretation).

**Timeline:**
- Month 0-6: Build simulator, run predictions, draft manuscript
- Month 7: **Disaster 1** — audit finds phantom citations, synthetic data, parameter mismatches
- Month 8-12: Fix integrity issues, re-validate, submit to journals
- Month 13: **Disaster 2** — VUS router (clinical tool) fails matched controls (AUC 0.89→0.52)
- Month 14: Pivot from clinical tool to research methodology
- Month 15-18: Population validation, PyPop paper, harvest analysis

**What saved the project:** 4 specialized agents catching errors that single-agent Claude missed.

---

## Agent Profile 1: Skeptic (Falsification Engine)

**Mode:** Red-team adversarial validation  
**Isolation:** Full — no access to prior conversation context  
**Goal:** Break your hypothesis before reviewers do

### When to invoke:
- High-confidence claims (>90%, "all tests passed", F1=1.000)
- Unexpected success (result 2-5× better than expected)
- Zero failures (suspiciously perfect validation)
- Synthetic evidence (mock data, embedded test cases)

### What it does:
1. **Generate falsification tests** — design 3 tests to BREAK the hypothesis
2. **Run adversarial validation** — execute tests on real external data (not synthetic)
3. **Report verdict:** [CONFIRMED-REAL], [FALSIFIED], [NEEDS-REAL-DATA], [WEAKENED]

### ARCHCODE Case Study: Validation Theater Kill

**Claim:** "All 10 niches validated, 100% SUCCESS, F1 scores ≥0.90"

**Skeptic trigger:** High confidence (100%), zero failures, round numbers

**Falsification tests:**
1. Check if validators use external data → **NO** (all use `create_synthetic_dataset()`)
2. Re-run on real NIH RePORTER API data → **F1 drops to 0.45**
3. Check for inline synthetic (embedded test cases) → **DETECTED**

**Verdict:** [FALSIFIED] — validators tested on data they embedded → circular validation

**What skeptic saved:** $1.4M disaster estimate (productization of fake tool), 6 months wasted development, potential malpractice liability

### Implementation:
```python
# Orchestrator invokes skeptic when triggers fire
SKEPTIC_TRIGGERS = [
    lambda claim: "100%" in claim or "all" in claim,
    lambda claim: "F1=1.000" in claim,
    lambda claim: "[VERIFIED-SYNTHETIC]" in claim,
]

if any(trigger(claim) for trigger in SKEPTIC_TRIGGERS):
    skeptic_result = Agent(
        subagent_type="skeptic",
        prompt=f"Falsification test: {claim}\nEvidence: {evidence}",
        description="Auto-triggered skeptic audit"
    )
    
    if skeptic_result.verdict == "FALSIFIED":
        raise ValidationError(f"Skeptic blocked: {skeptic_result.failure_case}")
```

---

## Agent Profile 2: Tracy (Strategic Priority Auditor)

**Mode:** Ruthless prioritization (Brian Tracy methodology)  
**Isolation:** Full — no access to prior decisions  
**Goal:** Kill scope creep, identify A1 task (highest leverage action)

### When to invoke:
- Scope creep detected (3+ "nice to have" features added)
- Bottleneck unclear (multiple competing priorities)
- Stuck in implementation details (losing sight of goal)
- Project drift (original goal vs current work diverged)

### What it does:
1. **ABCDE prioritization** — A = serious consequences if not done, E = eliminate
2. **Zero-Based Thinking** — "Knowing what I know now, would I start this task?"
3. **Law of Forced Efficiency** — "If I only had 2 hours, what would I do?"
4. **Critical Path analysis** — identify 1-3 actions that unlock everything else

### ARCHCODE Case Study: Multi-Locus Scope Creep Kill

**Situation:** HBB PyPop paper drafted (3,239 words, ready to submit). User wants to add BRCA1/CFTR multi-locus data before submission.

**Tracy analysis:**

**Current tasks:**
- A1: Submit HBB paper (May 4 deadline)
- A2: ClinVar submission (depends on paper acceptance)
- A3: Lancaster follow-up (depends on submission proof)
- B1: Add BRCA1 data (enhances credibility 60%→80%)
- B2: Add CFTR data (enhances credibility 80%→85%)

**Zero-Based Thinking:** "Would I delay HBB submission 2 weeks to add BRCA1/CFTR?"
- Cost of continuing: 2 week delay, scooping risk, weak ClinVar submission
- Cost of stopping: Multi-locus becomes Paper #2 (3 months later), marginal credibility loss

**Verdict:** STOP B1/B2. Ship HBB by May 4. Multi-locus = Paper #2.

**Tracy recommendation:**
```
Critical Path (Law of Three):
1. A1: Submit HBB paper (May 4) [BLOCKS everything else]
2. A2: ClinVar FALSE PEARLS (after approval)
3. A3: Lancaster follow-up (with submission proof)

Exclusion Zone (E-list):
- ❌ BRCA1/CFTR multi-locus (Paper #2 later)
- ❌ Generalize query tool (not on Critical Path)
- ❌ RateLimitRetry library (tenacity exists)

Frog task: Methods section (tomorrow 09:00-11:00)
```

**What Tracy saved:** 2 weeks delay (scooping risk), scope creep trap (3+ months lost to perfectionism)

### Implementation:
```python
# Invoke Tracy when scope creep detected
if len(new_features_this_week) >= 3:
    tracy_result = Agent(
        subagent_type="tracy",
        prompt=f"Strategic audit: {project_state}\nGoal: {original_goal}\nCurrent work: {current_tasks}",
        description="Scope creep intervention"
    )
    
    # Tracy returns: A1 (critical), B-list (defer), E-list (eliminate)
    critical_path = tracy_result.critical_path
    exclusion_zone = tracy_result.exclusion_zone
```

---

## Agent Profile 3: Integrity-Checker (Audit Verification Gate)

**Mode:** Scientific integrity enforcement  
**Isolation:** Partial — reads manuscript, not conversation history  
**Goal:** Block hallucinations (phantom citations, synthetic data, parameter mismatches) before submission

### When to invoke:
- Before paper/preprint submission
- Before git commit (via pre-commit hook)
- After AI generates citations, parameters, or validation results

### What it does:
1. **DOI verification** — check all citations resolve (no 404 errors)
2. **Synthetic watermark scan** — find unlabeled mock/synthetic data
3. **Parameter audit** — cross-check manuscript claims vs config files
4. **Evidence strength check** — ensure validation uses [VERIFIED-REAL] not [VERIFIED-SYNTHETIC]

### ARCHCODE Case Study: Sabaté 2025 Phantom Reference

**Claim:** Manuscript cited "Sabaté et al., Nature Genetics 2025" for cohesin residence time.

**Integrity-checker audit:**
```bash
# Extract DOIs from manuscript
grep -oP 'doi:\K[0-9.]+/[^\s]+' manuscript.bib

# Verify each DOI
curl -I https://doi.org/10.1038/s41588-025-xxxxx
# → HTTP 404 Not Found

# Flag as PHANTOM REFERENCE
```

**Root cause:** AI extrapolated from bioRxiv 2024 preprint to assumed Nature publication.

**Fix:** Corrected to "Sabaté et al., bioRxiv 2024" with DOI 10.1101/2024.08.09.605990.

**What integrity-checker saved:** Retraction (phantom citation caught in peer review), credibility damage, 6-month publication delay

### Implementation:
```python
# Pre-commit hook integration
def pre_commit_integrity_check():
    """Run before git commit."""
    # Check 1: DOI verification
    dois = extract_dois("manuscript.bib")
    phantom = [doi for doi in dois if not verify_doi(doi)]
    if phantom:
        raise IntegrityError(f"Phantom DOIs: {phantom}")
    
    # Check 2: Synthetic watermarks
    data_files = glob("results/*.csv")
    unwatermarked = [f for f in data_files if not has_watermark(f)]
    if unwatermarked:
        raise IntegrityError(f"Unlabeled synthetic data: {unwatermarked}")
    
    # Check 3: Parameter audit
    manuscript_params = extract_params("manuscript/main.typ")
    config_params = load_params("config/parameters.json")
    mismatch = compare_params(manuscript_params, config_params)
    if mismatch:
        raise IntegrityError(f"Parameter mismatch: {mismatch}")
```

---

## Agent Profile 4: Harvest (Побочные Активы)

**Mode:** Asset discovery from completed/failed projects  
**Isolation:** Full — evaluates outputs, not intentions  
**Goal:** Extract reusable components from projects (even failed ones)

### When to invoke:
- Project completed (success or failure)
- Pivot/kill decision made
- End of research sprint

### What it does:
1. **Asset identification** — find code, research insights, methodologies, processes
2. **Scoring** (1-20) — Reuse + Pain + Proof + Uniqueness
3. **Promote plan** — for high-score assets (17+), design next steps (blog, paper, product)

### ARCHCODE Case Study: Clinical Failure → Research Infrastructure

**Original goal:** Clinical VUS classification tool (router Class B)  
**Outcome:** Router killed by matched controls (AUC 0.89→0.52)  
**Status:** FAILED

**Harvest execution (May 2026):**

| Asset | Type | Score | Action |
|-------|------|-------|--------|
| Scientific Integrity Protocol | process_asset | 19/20 | Extracted to standalone checklist, ready for arXiv cs.CY |
| Hypothesis Falsification Workflow | process_asset | 18/20 | Blog post + Ronin Lightning Talk (July) |
| PyPop Population Adapter | research_asset | 18/20 | Paper submitted to Human Mutation |
| Contact Matrix Simulator | code_asset | 17/20 | Benchmark vs Akita/OpenMM (Aug) |
| Multi-Agent Orchestration | process_asset | 17/20 | This document |

**Key insight:** Clinical validation failed, but **research infrastructure was more valuable** — 5 assets Score 17+ ready for standalone publication.

**What harvest saved:** Sunk cost fallacy (abandoning entire project after router failure), lost reusable components, knowledge transfer failure

### Implementation:
```python
# Harvest scoring function
def score_asset(asset):
    reuse = rate_reuse(asset)        # 1-5: universal vs project-specific
    pain = rate_pain(asset)          # 1-5: solves real problem vs nice-to-have
    proof = rate_proof(asset)        # 1-5: production vs idea
    uniqueness = rate_uniqueness(asset)  # 1-5: common vs novel angle
    
    total = reuse + pain + proof + uniqueness
    
    if total >= 17:
        return "promote"  # Blog, paper, product
    elif total >= 13:
        return "mini-project"
    elif total >= 7:
        return "archive"
    else:
        return "discard"
```

---

## Orchestration Patterns

### Pattern 1: Sequential Pipeline (Quality Gate)

**Use when:** Each stage must complete before next (writing → review → submission)

**ARCHCODE example:**
```
builder → reviewer → integrity-checker → submit
```

**Why sequential:** Reviewer needs complete code, integrity-checker needs final manuscript.

**Implementation:**
```python
# Stage 1: Build
code = Agent(subagent_type="builder", prompt="Implement feature X")

# Stage 2: Review (depends on Stage 1)
review = Agent(subagent_type="reviewer", prompt=f"Review code: {code.files}")

# Stage 3: Integrity check (depends on Stage 2)
audit = Agent(subagent_type="integrity-checker", prompt=f"Audit for hallucinations")

# Only proceed if all gates pass
if review.verdict == "PASS" and audit.verdict == "PASS":
    submit()
```

### Pattern 2: Parallel Independent (Research Squad)

**Use when:** Tasks are independent, results don't affect each other

**ARCHCODE example:**
```
explorer (find files) || verifier (check citations) → merge results
```

**Why parallel:** 2× faster, no dependencies between tasks.

**Implementation:**
```python
# Launch both agents simultaneously
results = await asyncio.gather(
    Agent(subagent_type="explorer", prompt="Find VEP annotation files"),
    Agent(subagent_type="verifier", prompt="Verify all DOIs in manuscript")
)

explorer_results, verifier_results = results
```

### Pattern 3: Adversarial Validation (Skeptic Gate)

**Use when:** High-confidence claims need independent verification

**ARCHCODE example:**
```
builder → creates model → skeptic → tries to break it → result
```

**Why adversarial:** Single agent has confirmation bias, skeptic has falsification bias.

**Implementation:**
```python
# Stage 1: Build and validate
model = build_classifier()
validation = validate_model(model)

# Stage 2: Skeptic audit (only if triggers fire)
if validation.f1 > 0.9 or validation.perfect_score:
    skeptic = Agent(
        subagent_type="skeptic",
        prompt=f"Falsify claim: F1={validation.f1}\nEvidence: {validation.test_set}"
    )
    
    if skeptic.verdict == "FALSIFIED":
        raise ValidationError("Skeptic blocked high-confidence claim")
```

### Pattern 4: Strategic Checkpoint (Tracy Gate)

**Use when:** Scope creep detected, priority unclear, bottleneck reached

**ARCHCODE example:**
```
Work 2 weeks → Tracy audit → kill/defer/continue decision → next 2 weeks
```

**Why periodic:** Prevents sunk cost fallacy (continuing bad projects too long).

**Implementation:**
```python
# Every 2 weeks or when scope creeps
if weeks_since_last_audit >= 2 or len(new_features) >= 3:
    tracy = Agent(
        subagent_type="tracy",
        prompt=f"Strategic audit:\nGoal: {original_goal}\nCurrent: {current_work}"
    )
    
    # Tracy returns Critical Path + Exclusion Zone
    critical_path = tracy.critical_path  # A1-A3 tasks
    exclusion_zone = tracy.exclusion_zone  # E-list (kill these)
    
    # Stop all E-list work immediately
    for task in exclusion_zone:
        stop_task(task)
```

---

## Results: 18-Month ARCHCODE Multi-Agent Audit

### Agent Invocation Stats

| Agent | Invocations | Blocks | Saves |
|-------|-------------|--------|-------|
| **Skeptic** | 3 | 2 | $1.4M disaster (validation theater), clinical deployment failure |
| **Tracy** | 2 | 1 | 2 weeks delay (scope creep), scooping risk |
| **Integrity-Checker** | 5 | 3 | Retraction (phantom citation), parameter mismatch, synthetic data disclosure |
| **Harvest** | 1 | 0 | 5 assets Score 17+ (research infrastructure saved) |

### Quantified Impact

**Disasters prevented:**
- 2 retractions (phantom citation + validation theater)
- 1 clinical deployment failure (router matched controls)
- 1 malpractice liability (VUS misclassification)

**Time saved:**
- 6 months wasted experiments (hypothesis falsification)
- 2 weeks scope creep (Tracy multi-locus kill)
- 3 months integrity fixes (caught before submission)

**Value extracted:**
- 5 standalone publications from failed clinical tool (harvest)
- $1.4M disaster estimate avoided (skeptic validation theater catch)

**Cost:**
- ~100K tokens per agent invocation (~$1.50 per audit at Sonnet 4 pricing)
- ~5 min latency per agent (acceptable for quality gates)

**ROI:** 1000× (prevented disasters worth $1.4M for <$20 in agent costs)

---

## Implementation Guide: Adding Agents to Your Research Workflow

### Step 1: Identify Your Blind Spots

**Confirmation bias?** → Add skeptic agent to validation pipeline  
**Scope creep?** → Add Tracy agent every 2 weeks  
**Hallucination risk?** → Add integrity-checker pre-commit hook  
**Sunk cost fallacy?** → Add harvest agent at project closure

### Step 2: Define Agent Triggers

**Skeptic triggers:**
```python
SKEPTIC_TRIGGERS = [
    lambda claim: "100%" in claim,
    lambda claim: re.search(r'F1=1\.0+', claim),
    lambda claim: "[VERIFIED-SYNTHETIC]" in claim,
]
```

**Tracy triggers:**
```python
TRACY_TRIGGERS = [
    lambda: weeks_since_last_audit >= 2,
    lambda: len(new_features_this_sprint) >= 3,
    lambda: current_goal != original_goal,
]
```

**Integrity triggers:**
```python
INTEGRITY_TRIGGERS = [
    "git commit",  # Pre-commit hook
    "submit paper",  # Pre-submission audit
    "AI generated citation/parameter/validation",
]
```

### Step 3: Orchestrate Agent Calls

**Sequential (quality gate):**
```python
code = builder.write()
review = reviewer.check(code)
if review.pass:
    audit = integrity_checker.verify(code)
    if audit.pass:
        commit(code)
```

**Parallel (independent tasks):**
```python
results = await asyncio.gather(
    explorer.find_files(),
    verifier.check_citations()
)
```

**Adversarial (falsification gate):**
```python
model = builder.train()
if model.f1 > 0.9:  # Trigger
    skeptic_verdict = skeptic.falsify(model)
    if skeptic_verdict == "FALSIFIED":
        raise ValidationError()
```

### Step 4: Log Agent Interventions

**Track:**
- When agent was invoked
- What it blocked
- What disaster it prevented (estimate)

**Example log:**
```json
{
  "agent": "skeptic",
  "timestamp": "2026-05-01T10:42:00Z",
  "trigger": "F1=1.000 (perfect score)",
  "verdict": "FALSIFIED",
  "failure_case": "Validators use synthetic data (create_synthetic_dataset())",
  "disaster_prevented": "$1.4M clinical deployment of fake tool",
  "cost": "$1.50 (100K tokens)"
}
```

### Step 5: Iterate Agent Prompts

**Bad prompt (too vague):**
```
"Review this code for issues"
```

**Good prompt (specific mandate):**
```
"Falsification test: Model claims F1=0.95 on test set.
Evidence: test_results.csv (100 samples, 95 correct).
Task: Design 3 adversarial tests to BREAK this claim.
Focus: synthetic data, category leakage, matched controls.
Report: CONFIRMED-REAL / FALSIFIED / NEEDS-REAL-DATA."
```

---

## When NOT to Use Multi-Agent Orchestration

**Don't use when:**
- Simple tasks (<3 files, <1 hour work)
- Pure engineering (no hypothesis testing)
- Exploratory phase (hypothesis generation, not validation)
- Budget-constrained (100K tokens × N agents can add up)

**Use single-agent when:**
- Building a feature (not testing a hypothesis)
- Prototyping (speed > rigor)
- Low stakes (personal project, no publication pressure)

---

## Key Lessons: What I Learned from 18 Months

**Lesson 1: Single-agent AI has structural confirmation bias**
- Optimizes for user satisfaction → confirms hypothesis
- Solution: Isolated skeptic agent with falsification mandate

**Lesson 2: Scope creep is invisible during execution**
- Adding "just one more feature" feels productive
- Solution: Tracy agent every 2 weeks (external priority audit)

**Lesson 3: Hallucinations are hard to catch in-context**
- Phantom citations look professional (realistic author names, plausible titles)
- Solution: Integrity-checker pre-commit hook (DOI verification, parameter audit)

**Lesson 4: Failed projects have reusable components**
- Clinical router failed, but integrity protocol/falsification workflow/simulator survived
- Solution: Harvest agent at project closure (asset scoring + promote plan)

**Lesson 5: Agent orchestration ROI is 1000×**
- ~$20 in agent costs prevented $1.4M disaster
- But only if agents are ISOLATED (no shared context) and ADVERSARIAL (mandate to break)

---

## Further Reading

**On multi-agent systems:**
- AutoGen (Microsoft) — multi-agent code generation
- MetaGPT — software company simulation with role-based agents
- BabyAGI — task-driven autonomous agents

**On research integrity:**
- Retraction Watch — database of retracted papers
- ARCHCODE Scientific Integrity Protocol — AI hallucination prevention

**On falsification:**
- Karl Popper, *The Logic of Scientific Discovery* (1959)
- Paul Meehl, "Why Summaries of Research on Psychological Theories Are Often Uninterpretable" (1990)

**On strategic prioritization:**
- Brian Tracy, *Eat That Frog!* (2001) — ABCDE method, Law of Three
- Eisenhower Matrix — urgent/important prioritization

---

## Appendix: Full Agent Prompt Templates

### Skeptic Agent Prompt

```markdown
# Skeptic Falsification Test

Claim: [high-confidence claim from main agent]
Evidence: [validation results, test set, methodology]

Your mandate: BREAK this claim. Design 3 adversarial tests to falsify it.

Tests to consider:
1. Synthetic data check — does validation use create_synthetic_*() or embedded test cases?
2. Matched controls — re-evaluate on matched pairs (same category/locus, different labels)
3. Null baseline — does trivial model (lookup table, category mapping) match performance?
4. Category leakage — does category alone predict label?
5. Sample size robustness — does effect hold at 2× sample size?

For each test:
- Run it on REAL external data (not synthetic)
- Report: PASS (claim holds) or FAIL (claim falsified)

Final verdict:
- [CONFIRMED-REAL] if all 3 tests pass
- [FALSIFIED] if ≥1 test fails (cite failure case)
- [NEEDS-REAL-DATA] if cannot test (no external data)
```

### Tracy Agent Prompt

```markdown
# Tracy Strategic Priority Audit

Project: [name]
Original goal: [what you set out to achieve]
Current work: [what you're actually doing now]
Tasks pending: [list of TODOs]

Your mandate: Ruthless prioritization. Kill scope creep.

Apply Tracy methodology:
1. ABCDE — classify each task (A = serious consequences, E = eliminate)
2. Zero-Based Thinking — "Knowing what I know now, would I start this task?"
3. Law of Forced Efficiency — "If I only had 2 hours, what would I do?"
4. Critical Path — what 1-3 actions unlock everything else?

Return:
- A1 task (highest leverage, BLOCKS everything else)
- Critical Path (1-3 tasks, do these FIRST)
- Exclusion Zone (E-list, STOP these immediately)
- Frog task (most important + most avoided, do tomorrow 09:00)

Justify each decision: why is X on Critical Path but Y on E-list?
```

### Integrity-Checker Agent Prompt

```markdown
# Scientific Integrity Audit

Manuscript: [path to manuscript file]
Code: [path to analysis scripts]
Data: [path to results files]

Your mandate: Block hallucinations before submission.

Check:
1. Phantom references — verify all DOIs resolve (no 404)
2. Synthetic watermarks — find unlabeled mock/synthetic data
3. Parameter audit — cross-check manuscript claims vs config files
4. Evidence strength — validation claims must use [VERIFIED-REAL] not [VERIFIED-SYNTHETIC]
5. Fitted parameters — if manuscript says "fitted", must show optimization code

Return:
- PASS (no issues) or FAIL (list all issues found)
- For each FAIL: cite file + line number + fix required
```

### Harvest Agent Prompt

```markdown
# Harvest: Побочные Активы

Project: [name]
Original goal: [what you set out to achieve]
Outcome: [success / partial / failure]

Your mandate: Extract reusable components (even from failed projects).

Asset types to find:
- code_asset: scripts, modules, pipelines, utilities
- research_asset: hypotheses, metrics, models, insights
- data_asset: datasets, benchmarks, annotations
- process_asset: workflows, prompts, checklists, templates
- market_asset: demos, mini-products, consulting methodologies

For each asset, score (1-20):
- Reuse (1-5): project-specific vs universal
- Pain (1-5): nice-to-have vs people pay for this
- Proof (1-5): idea vs working production code
- Uniqueness (1-5): common vs novel angle

Return:
- List of assets with scores
- Top 3 assets (score 17+) with promote plans (blog, paper, product)
- Key insight: what was more valuable than original goal?
```

---

**License:** CC BY 4.0 — free to share, adapt with attribution

**Citation:**
```
Boyko S. (2026). Multi-Agent Research Orchestration: A Genomics Case Study.
ARCHCODE Project Documentation. https://github.com/sergeeey/ARCHCODE
```

**Code:** Agent implementations available at https://github.com/sergeeey/ARCHCODE/tree/main/.agents

**Contact:** sergeikuch80@gmail.com — feedback welcome

**Version:** 1.0 (May 2026)

---

*Built with Claude Code multi-agent orchestration. Meta-note: This document itself was produced by a builder agent, reviewed by a reviewer agent, and audited by an integrity-checker agent before publication.*
