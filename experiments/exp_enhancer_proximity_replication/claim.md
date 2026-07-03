---
experiment: exp_enhancer_proximity_replication
date: 2026-07-02
ladder_tier: Standard
question_type: Predictive
status: IN PROGRESS
---

# Claim: Enhancer proximity discriminates pathogenic/benign ClinVar variants at erythroid loci beyond HBB

## EstimandOps L0

**Question type:** Predictive.
"Does distance to the nearest tissue-matched (erythroid/K562) H3K27ac enhancer peak
discriminate ClinVar Pathogenic from Benign variants at BCL11A, KLF1, GATA1 -- the same
pattern found at HBB (OR=34.05, permutation p<0.0001, in `manuscript/taxonomy_paper`)?"

Not a full replication of the original methodology: the original HBB finding was computed
on ARCHCODE's LSSIM-derived "Class B" (Q2b) variant subset (requires running the full
TypeScript loop-extrusion simulation engine). This experiment tests the simpler, more
tractable CORE geometric claim directly -- enhancer proximity vs pathogenicity label --
without the LSSIM/simulation layer. This is an honest simplification, not a hidden scope
change: if this simpler test fails, it does NOT falsify the original HBB finding (different
methodology); if it succeeds, it is independent, complementary evidence, not proof the full
methodology generalizes.

## L1 Estimand

- **Population:** ClinVar SNV/indel variants at BCL11A (chr2), KLF1 (chr19), GATA1 (chrX),
  strict ClinicalSignificance == "Pathogenic"/"Likely pathogenic" OR "Benign"/"Likely benign"
  (excludes VUS/conflicting), GRCh37/hg19 (matches today's ABC/GENCODE build).
- **Exposure:** Distance (bp) from variant to nearest ENCODE K562 H3K27ac ChIP-seq peak
  (tissue-matched, same cell line used throughout this project's erythroid analyses).
- **Comparator:** Benign variant distances vs Pathogenic variant distances, WITHIN the same
  VEP consequence category (category-matched control -- this is the control that correctly
  falsified the earlier "Class B VUS" overclaim; applying it here from the start, not
  retrofitted after a positive result).
- **Endpoint:** Pathogenic vs Benign classification.
- **Summary measure:** (a) Mann-Whitney U on raw distance (continuous, no arbitrary
  threshold), reported per locus separately; (b) odds ratio at a pre-specified 1kb threshold
  (matches HBB's published proximity analysis), category-stratified CMH test.
- **MCID:** Given HBB's effect was very large (OR=34), and this is a lower-powered
  multi-locus replication, MCID is set conservatively: OR>=3 AND FDR-corrected p<0.05
  (Benjamini-Hochberg across the 3 loci) on the category-matched test. Anything weaker is
  REPEAT/REJECT, not PROMOTE.
- **ICE:** None (complete-case classification, no dropouts).

## Natural Language Statement

We estimate the odds ratio (at 1kb) and Mann-Whitney U (continuous) of ClinVar Pathogenic
vs Benign variant proximity to K562 H3K27ac enhancer peaks, separately at BCL11A, KLF1, and
GATA1, controlling for VEP consequence category, with FDR correction across the 3 loci.

## What This Does NOT Mean

1. A positive result does NOT prove the full ARCHCODE LSSIM methodology generalizes --
   only that the simpler geometric feature (raw enhancer proximity) does.
2. A negative result does NOT falsify the original HBB finding -- different methodology,
   different loci, not a like-for-like replication.
3. Does NOT establish causality -- descriptive/predictive association only.

## Pre-registered analysis plan (before touching data)

1. Fetch ClinVar P/B variants for BCL11A, KLF1, GATA1 (hg19) -- NEW query, not yet run.
2. Fetch ENCODE K562 H3K27ac peaks (hg19) -- NEW download, not yet run.
3. Compute per-variant distance to nearest peak.
4. Run category-matched Mann-Whitney U + CMH-OR-at-1kb per locus, independently.
5. Apply Benjamini-Hochberg FDR correction across the 3 loci's p-values.
6. Report ALL three loci's results regardless of outcome (no cherry-picking which locus to
   report) -- if 0/3, 1/3, 2/3, or 3/3 loci show a positive result, all get documented.

## Go/No-Go Criterion

- PROMOTE: >=2/3 loci individually meet MCID (OR>=3, FDR-p<0.05)
- REPEAT: 1/3 loci meets MCID, or effect sizes trend correctly but underpowered
- REJECT: 0/3 loci show effect in the predicted direction -> null_results/
