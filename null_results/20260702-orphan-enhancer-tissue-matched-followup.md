# REJECT — Tissue-matching does NOT rescue the orphan-enhancer VUS-enrichment null

**Experiment ID:** 20260702-orphan-enhancer-tissue-matched-followup
**Status:** EXPLORATORY (post-hoc), documented to prevent re-litigating the same idea blind

## Background

After the original `exp_orphan_enhancers` REJECT (OR=1.22, genome-wide, all 131 ABC
biosamples pooled), three independently-launched audit agents with no visibility into each
other's work all converged on the same recommendation: restrict the test to tissue-matched
(erythroid) biosamples, mirroring the ONE condition under which this project's strongest
surviving signal (enhancer proximity, OR=34.05 at HBB) was found.

## What was tested

`scripts/orphan_enhancer_tissue_matched_exploratory.py` reran the same CMH-stratified
orphan/regular vs VUS-overlap test, restricted to 4 erythroid-lineage ABC CellTypes
(K562-Roadmap, CD34-positive_mobilized-Roadmap, erythroblast-Corces2016,
megakaryocyte-erythroid_progenitor-Corces2016), both genome-wide and restricted further to
the HBB locus (chr11:5,100,000-5,350,000, hg19).

## Result

| Scope | n orphan / n regular | OR | p |
|---|---|---|---|
| Original (all 131 tissues, genome-wide) | 285,959 / 375,335 | 1.221 | ~0 |
| Erythroid-only, genome-wide | 23,935 / 34,799 | **1.158** (weaker, not stronger) | 0.018 |
| Erythroid-only, HBB locus | 24 / 12 | undefined (n too small) | undefined |

**Tissue-restriction did not recover a stronger signal — if anything the OR moved slightly
closer to null.** The HBB-locus-restricted test is uninformative (n=36 total intervals,
degenerate variance in the CMH statistic).

## Interpretation

The mechanism that makes tissue-matching essential for the SNV pipeline's enhancer-proximity
signal (HBB, K562, LCR/promoter architecture) does not transfer to the ABC-model
orphan/regular enhancer classification tested here. These are different operationalizations
of "enhancer relevance" (spatial proximity to a variant vs. ABC-model target-gene assignment
mismatch) and evidently do not share the same tissue-dependence. This is a useful negative
result: it prevents future sessions from re-trying "just restrict to the right tissue" on
this specific hypothesis without knowing it was already checked and did not pan out.

## What this does NOT mean

1. Does NOT mean tissue-matching is unimportant in general -- it remains essential and
   confirmed for the SNV/LSSIM pipeline's enhancer-proximity finding.
2. Does NOT rule out a signal at a DIFFERENT, single, well-characterized disease locus with
   its own dedicated Hi-C/ABC data (this test used ABC's public genome-wide K562/erythroid
   biosamples, not a purpose-built HBB Hi-C dataset) -- but that is a materially different,
   heavier undertaking than this quick exploratory check.
3. Does NOT mean the three agents' reasoning was invalid -- restricting to tissue-matched
   biosamples was the single most defensible, cheapest, most convergent next step to check,
   and checking it (rather than assuming it would work) is exactly the falsification-first
   discipline this project is built on.
