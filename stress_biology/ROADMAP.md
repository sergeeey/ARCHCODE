# Roadmap — Stress Biology Project

**Timeline:** 6 months (2026-04 to 2026-10)  
**Phase:** Computational meta-analysis → Wet-lab collaboration (optional)

---

## Phase 1: Data Collection (Month 1)

**Goal:** Собрать TCGA mutation data + doubling time из литературы

### Week 1-2: TCGA Pipeline

- [ ] Setup TCGA API access (test with 10 samples)
- [ ] Download MAF files (mutation annotation format)
- [ ] Parse MAF → mutation rate per sample
- [ ] Quality control: remove low-coverage samples (<30×)

**Deliverable:** `data/tcga_mutations.csv` (n > 1000 samples)

---

### Week 3-4: Literature Mining

- [ ] PubMed API: search "doubling time" + tissue type
- [ ] Extract doubling time for 10 tissue types
- [ ] Validate with Sender et al. 2016 (Cell) reference values

**Deliverable:** `data/doubling_times.csv`

---

## Phase 2: Hypothesis Testing (Month 2-3)

### Month 2: H1 (Tissue-Specific)

- [ ] Group samples by tissue (colon, skin, blood, brain, heart)
- [ ] Mann-Whitney U test (high vs low proliferation)
- [ ] Plot heatmap: tissue × mutation rate

**Deliverable:** `results/fig1_tissue_heatmap.png`

---

### Month 3: H0 (Main Correlation)

**Checkpoint:** KILL OR CONTINUE decision

- [ ] Spearman correlation (doubling time vs mutation rate)
- [ ] Bootstrap 95% CI (10K iterations)
- [ ] Multiple testing correction (Bonferroni)

**Decision Tree:**

```
if r < 0.1:
    → KILL immediately (очень слабо)
    → Write negative result paper
elif r < 0.3:
    → KILL gracefully
    → Publish in PLOS Comp Bio
elif r > 0.4 and p < 0.01:
    → PASS → proceed to Month 4
else:
    → Borderline → need more data or wet-lab
```

**Deliverable:** `results/h0_stats.json`, `results/fig2_correlation.png`

---

## Phase 3: ATP Proxy (Month 4, if H0 passed)

- [ ] Compute ATP proxy from RNA-seq (OXPHOS genes)
- [ ] Correlate with mutation rate
- [ ] Validate against published ATP measurements

**Decision:**

- If r < -0.2 → ATP proxy failed, mechanism unclear
- If r < -0.3 → ATP proxy works, supports Bilinsky framework

**Deliverable:** `results/fig3_atp_proxy.png`

---

## Phase 4: Manuscript Draft (Month 5)

**Scenarios:**

### Scenario A: Null Result

**Title:** "No Evidence for Correlation Between Cell Cycle Duration and Somatic Mutation Rate"

**Sections:**

1. Introduction (Bilinsky framework, hypothesis)
2. Methods (TCGA data, Spearman test)
3. Results (r = 0.15, p = 0.23)
4. Discussion (why hypothesis failed, what we learned)

**Submit to:** PLOS Computational Biology, F1000Research

---

### Scenario B: Weak Positive

**Title:** "Cell Proliferation Rate Weakly Predicts Mutation Burden: A Computational Framework"

**Sections:**

1. Introduction
2. Methods
3. Results (r = 0.38, p = 0.003)
4. Discussion (theoretical implications, need wet-lab)

**Submit to:** Bioessays, Genome Biology (correspondence)

---

### Scenario C: Strong Positive

**Title:** "ATP Availability Determines Somatic Mutation Rate via Nuclear Envelope Stability"

**Sections:**

1. Introduction
2. Methods (computational + wet-lab, if Experiment 3 done)
3. Results (r = 0.62, p < 1e-10)
4. Discussion (mechanistic model)

**Submit to:** Nature Cell Biology, Nature Genetics

---

## Phase 5: Collaboration Outreach (Month 6)

### Email Bilinsky

**Timing:** После получения результатов Experiment 1

**Content:**

> Dear Dr. Bilinsky,
>
> I read your Biomath 2025 paper on radiosensitivity and ATP states. I tested whether your R/Q framework applies to endogenous mutagenesis. Results: [INSERT H0 RESULT].
>
> I'm RIIS Fellow [STATUS], computational genomics background. Would you be interested in discussing this? I believe your wet-lab expertise + my computational pipeline could lead to a strong collaboration.
>
> Attached: preliminary results, hypothesis doc.
>
> Best,  
> [Your Name]

---

### Alternative Collaborators (if Bilinsky declines)

- RIIS Fellows in cell biology (search RIIS directory)
- Authors of ATP measurement papers (PubMed: "ATP live-cell imaging")
- Radiobiology labs (already familiar with stress biology)

---

## Phase 6: Wet-Lab Validation (Month 7-12, optional)

**Only if:** H0 + H3 both passed

**Design:**

1. Cell culture (HEK293, fibroblasts)
2. ATP manipulation (oligomycin, pyruvate)
3. WGS after 10 passages
4. Count de novo mutations

**Funding needed:** $5K-10K (cell culture, WGS)

**Funding sources:**

- RIIS micro-grants
- Crowdfunding (Experiment.com)
- Collaborator's grant

---

## Milestones & Checkpoints

| Month | Milestone | Go/No-Go Decision |
|-------|-----------|-------------------|
| 1 | Data collected (n > 1000) | If n < 500 → reassess |
| 2 | H1 tested | If p > 0.05 → warning sign |
| 3 | **H0 CHECKPOINT** | **r < 0.3 → KILL** |
| 4 | H3 tested | If failed → wet-lab needed |
| 5 | Manuscript drafted | — |
| 6 | Bilinsky contacted | — |

---

## Risks & Contingency Plans

### Risk 1: TCGA data unavailable

**Probability:** 20%  
**Mitigation:** Pre-test API access in Week 1  
**Contingency:** Use ICGC data instead

---

### Risk 2: Doubling time data sparse

**Probability:** 40%  
**Mitigation:** Focus on well-studied tissues (colon, skin, blood)  
**Contingency:** Use proliferation markers (Ki-67) as proxy

---

### Risk 3: Null result (r < 0.3)

**Probability:** 60%  
**Mitigation:** This is EXPECTED — negative result is publishable  
**Contingency:** Write honest negative result paper, apply ARCHCODE lessons

---

### Risk 4: No wet-lab collaborator

**Probability:** 70%  
**Mitigation:** Computational paper still valuable  
**Contingency:** Publish theoretical framework, wait for wet-lab interest

---

## Success Criteria (6 months)

### Minimal Success ✅

- [ ] H0 tested with n > 1000 samples
- [ ] Clear result (positive or negative)
- [ ] Manuscript submitted to peer-reviewed journal

### Medium Success ✅✅

- [ ] H0 + H3 both tested
- [ ] Weak positive result (r > 0.3)
- [ ] Bilinsky contacted, interested in collaboration

### High Success ✅✅✅

- [ ] Strong positive (r > 0.5, p < 1e-10)
- [ ] ATP proxy validated
- [ ] Wet-lab collaboration secured
- [ ] Manuscript submitted to Nature Cell Biology

---

## Current Status

- [x] Branch created: `feature/stress-biology-atp-mutagenesis`
- [x] SPEC.md written
- [x] HYPOTHESIS.md written
- [x] ROADMAP.md written (this file)
- [ ] Scripts created (stubs)
- [ ] Data collection started

**Next step:** Create `scripts/download_tcga.py` stub, test API access.

---

**Last Updated:** 2026-04-25
