# PyPop HBB Paper — Submission Checklist (May 4, 2026)

## Pre-Submission Verification ✅ COMPLETE

- [x] **Skeptic audit** — BS1 calculation fixed (commit 075d2e3)
- [x] **Coverage check** — AN_EAS >30K for both variants (reliable AF)
- [x] **Founder effect check** — distributed within EAS (ratio <2×)
- [x] **Reverse epidemiology** — confirmed (high EAS, low SAS/EUR)
- [x] **Qualitative framing** — "proof-of-concept" not "quantitative FP rate"

**Verdict:** Ready for submission

---

## Final Submission Gate

### Completed in current manuscript

1. **Methods note on data sources** — present in `manuscript/pypop_paper_FINAL.md`
2. **Future Directions baseline comparison** — present in `manuscript/pypop_paper_FINAL.md`
3. **Data Availability coverage check** — present in `manuscript/pypop_paper_FINAL.md`

### Remaining external step

The only remaining submission step is the manual Human Mutation portal check:

- verify author
- verify article type
- verify affiliation wording
- verify title
- upload the current `manuscript/taxonomy_paper/main.pdf`
- retain the current cover letter framing

If the portal metadata matches the canonical manuscript package, the submission package is ready.

---

## Human Mutation Submission Requirements

**Journal:** Human Mutation  
**Article type:** Brief Report  
**Current word count:** 3,239 words ✅ (within range)

**Required materials:**
1. **Manuscript** — pypop_paper_FINAL.md (convert to .docx)
2. **Cover letter** — draft below
3. **Graphical abstract** — optional (skip for short report)
4. **Supplementary materials** — data files (gnomad_populations_pearls.csv)

---

## Cover Letter Draft

```
Dear Editor,

I am submitting a Brief Report entitled "Population Stratification Identifies Epidemiology-Discordant Variants in the HBB Locus: A Validation Framework for Structural Predictions" for consideration in Human Mutation.

Structural variant prediction tools increasingly detect 3D chromatin disruptions in regulatory regions, but validating these predictions without functional data remains challenging. We demonstrate that population genetics, specifically cross-population allele frequency analysis, provides an orthogonal validation strategy. By adapting the PyPop population stratification framework (originally developed for HLA immunogenetics) to rare pathogenic variants, we identified two HBB promoter variants showing East Asian-specific enrichment despite beta-thalassemia being rare in this population—a reverse epidemiology pattern consistent with population-specific benign polymorphisms and potential overclassification by structural prediction.

This proof-of-concept study (n=12 variants) demonstrates that integrating disease epidemiology with cross-population allele frequency consistency can detect misclassifications invisible to sequence-based pathogenicity tools. Our approach addresses a critical gap in regulatory variant interpretation, where experimental validation (Hi-C, CRISPR) is impractical for large-scale screening.

Key findings:
- 5 (41.7%) variants not observed in gnomAD v4 queried datasets
- 2 variants showed reverse epidemiology pattern (East Asian enrichment, disease rare in East Asia)
- Allele frequency coverage validation confirmed reliable estimates (AN >30K)
- Sequence-based tools (VEP) correctly classified both as MODIFIER, demonstrating complementarity

This work is novel in applying population stratification (established in immunogenetics) to structural variant validation, and timely given increasing reliance on 3D genome-based prediction tools in clinical variant interpretation. Larger multi-locus studies are needed to quantify error rates systematically, but this study establishes population genetics as a scalable validation framework when functional data is unavailable.

The manuscript has not been submitted elsewhere and all authors have approved the submission. No conflicts of interest to declare.

Sincerely,
Sergey Boyko
Independent Researcher; Ronin Institute for Independent Scholarship 2.0 (affiliation pending confirmation)
```

---

## Submission Timeline

**May 2 (today, 23:30):** Final edits completed locally  
**May 3 (morning):** Convert to .docx, format figures (2 hours)  
**May 3 (afternoon):** Manual Human Mutation portal check / upload  
**May 4 deadline:** Local package aligned

---

## Post-Submission Actions

1. **ClinVar submission** — after SUB16160621 approval (expected May 3-4)
2. **Lancaster follow-up** — May 7 with paper submission proof
3. **Harvest deliverables** — publish Integrity Checklist + Falsification Blog (June)

---

## Backup Plan (if Human Mutation rejects)

**Alternative journals (ranked):**
1. **Genes** (MDPI) — open access, accepts short reports, ~3 week review
2. **Frontiers in Genetics** — open access, population genetics section
3. **European Journal of Human Genetics** — Springer, clinical focus

**Estimated timeline:** +4 weeks per journal cycle

---

**Status:** READY FOR PORTAL CHECK  
**Bottleneck:** External submission metadata confirmation  
**Risk:** Low for the local package; portal metadata still needs manual verification  
**Confidence:** HIGH for the canonical bundle, pending portal confirmation
