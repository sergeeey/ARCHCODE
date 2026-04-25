# Email Draft — Collaboration Proposal to Dr. Bilinsky

**Status:** DRAFT — DO NOT SEND until Experiment 1 is complete  
**Send after:** Month 3, after H0 correlation results available  
**Personalize:** Insert actual results, adjust tone based on outcome

---

## Email Template (Positive Result Scenario)

**Subject:** Collaboration proposal — ATP & endogenous mutagenesis (inspired by your Biomath 2025 paper)

---

Dear Dr. Bilinsky,

I recently read your excellent paper on dose-survival curves and the R/Q state hypothesis (Biomath 14, 2025). Your ATP-based mechanism for radiosensitivity inspired me to test a related hypothesis: **does cellular stress (ATP deficit) also drive endogenous mutagenesis rates?**

I completed a 3-month computational meta-analysis using TCGA data (n=[INSERT N] samples across [INSERT N_TISSUES] tissue types) and found **[INSERT RESULT]**:

- Spearman correlation between cell doubling time and mutation rate: r = [INSERT R], p = [INSERT P]
- Effect robust across [INSERT N_SIGNIFICANT] tissue types
- ATP proxy (OXPHOS gene expression) negatively correlated with mutation rate: r = [INSERT R_ATP]

**My interpretation:** This aligns with your framework. Fast-dividing cells spend more time in state Q (low ATP, vulnerable nuclear envelope), which may not only increase radiosensitivity to external damage (your finding), but also permit DNA replication errors to accumulate (my finding).

I'm a [RIIS Fellow / RIIS Fellow candidate, pending May 2026 decision], computational genomics background, currently independent researcher in Kazakhstan. I believe your wet-lab expertise in ATP manipulation + my computational pipeline could lead to a strong collaboration.

**Proposed next steps (if you're interested):**

1. **Short call** (30 min) to discuss preliminary results
2. **Shared preprint** — combine computational analysis (my part) + theoretical framework (co-authored)
3. **Wet-lab validation** (if feasible) — manipulate ATP (oligomycin, pyruvate) and measure mutation rate in cell culture

I'm happy to share:
- Full analysis code (Python/R, reproducible)
- Preliminary figures
- Hypothesis document with kill criteria

Would you be interested in discussing this? I'm flexible on timeline and authorship.

Best regards,  
Sergey Boyko

---

**Attachments to include:**
- `HYPOTHESIS.md` (hypotheses & kill criteria)
- `results/fig1_correlation.png` (main result)
- `results/h0_stats.json` (statistics)

---

## Email Template (Negative Result Scenario)

**Subject:** Negative result — ATP & mutagenesis (lessons from your Biomath 2025 framework)

---

Dear Dr. Bilinsky,

I read your Biomath 2025 paper on radiosensitivity and ATP-driven R/Q states. Your framework inspired me to test whether cellular stress (ATP deficit) also drives endogenous mutagenesis.

I completed a 3-month computational meta-analysis (TCGA, n=[INSERT N]) and found **no significant correlation** between cell doubling time and mutation rate (r = [INSERT R], p = [INSERT P]).

**Why I'm still writing:**

1. **Negative results are valuable** — this prevents others from pursuing the same hypothesis
2. **Your mechanism may still apply** — but to radiation damage specifically, not replication errors
3. **Alternative interpretation** — perhaps ATP affects DNA repair (radiosensitivity), but not replication fidelity (mutagenesis)

I plan to publish this as a negative result paper in PLOS Computational Biology or F1000Research. Would you be interested in:
- **Co-authorship** — as the inspiration for the hypothesis (you'd review methods/interpretation)
- **Brief commentary** — explaining why ATP might affect radiosensitivity but not mutagenesis

No pressure — I understand if you're busy. Just wanted to share the result with you since your work directly inspired it.

Best regards,  
Sergey Boyko

---

**Attachments:**
- `HYPOTHESIS.md`
- `results/null_result_summary.pdf`

---

## Timing Guidelines

### When to send (POSITIVE result):

- **Immediately after H0 checkpoint** (Month 3) if r > 0.4, p < 0.01
- Attach preliminary results
- Emphasize collaboration potential

### When to send (NEGATIVE result):

- **After manuscript draft** (Month 5)
- Attach preprint or draft
- Emphasize negative result value, less pressure on collaboration

### When NOT to send:

- Before Experiment 1 is complete (no data = vaporware)
- If borderline result (0.3 < r < 0.4) — wait for more data or wet-lab first

---

## Follow-Up Strategy

### If no response after 1 week:

- Check spam folder (yours)
- Send polite follow-up: "Just checking if my previous email reached you..."

### If no response after 2 weeks:

- Accept decline gracefully
- Move to Plan B: other RIIS Fellows in cell biology

### If interested:

- Schedule Zoom call (30 min)
- Share full code + data
- Discuss authorship early (avoid conflicts later)

---

## Alternative Collaborators (Plan B)

If Bilinsky declines or doesn't respond:

1. **RIIS Fellows in cell biology** (search RIIS directory)
2. **Authors of ATP live-cell imaging papers** (PubMed search)
3. **Radiobiology labs** (already familiar with stress biology)
4. **Cancer metabolism researchers** (overlap with ATP/OXPHOS)

---

## Authorship Guidelines (if collaboration happens)

**Fair authorship model:**

- **First author:** Whoever did majority of work (likely you for computational)
- **Last author:** Whoever provided critical wet-lab validation (Bilinsky if she does Experiment 3)
- **Co-first:** If contributions equal (computational + wet-lab)

**Discuss upfront:**

- Data ownership
- Code sharing (open source?)
- Publication venue preference
- Timeline expectations

---

**Status:** DRAFT. Do NOT send until Month 3 results available.

**Last Updated:** 2026-04-25
