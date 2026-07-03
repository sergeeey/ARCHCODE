# REJECT (partial) — "The Loop That Stayed" splice-junction hypothesis

**Experiment ID:** 20260702-loop-that-stayed-splice-junction
**Original hypothesis date:** ~2026-02-05 (`manuscript/LOOP_THAT_STAYED_HYPOTHESIS.md`)
**Formalized into null_results/:** 2026-07-02 (retroactive — this is a process-gap fix, not new analysis)

## Claim being (partially) rejected

> Deletion of the 3'HS1 CTCF binding site disrupts the HBB promoter <-> 3'HS1 loop (22 kb),
> causing HBB to exit its "active compartment" and undergo aberrant splicing. Predicted:
> **15-30% aberrant splicing** in 3'HS1-deletion clones, vs **<5-10%** in WT/inversion clones.
> Testable via splice-junction analysis of published RNA-seq (GSE160420, Himadewi et al. 2021).

## What was actually tested [VERIFIED via Read of results/hbb_splice_analysis.json]

| Clone | Modification | Canonical splicing | Novel/aberrant | Total reads |
|---|---|---|---|---|
| WT | intact 3'HS1 | 99.9% | 0.1% | 423,722 |
| B6 | 3'HS1 **deletion** | 99.9% | 0.1% | 734,735 |
| A2 | 3'HS1 **inversion** | 99.9% | 0.1% | 1,275,983 |

All three samples show ~0.1% aberrant splicing -- indistinguishable from WT, far below the
predicted 15-30% for a deletion clone.

## Why this is a PARTIAL reject, not a decisive one

The hypothesis document (`manuscript/LOOP_THAT_STAYED_HYPOTHESIS.md:146-154`) identifies **two**
independent 3'HS1-deletion clones from the original Himadewi et al. 2021 dataset, with very
different HBB expression phenotypes:

| Clone | HBB expression change vs WT | Notes |
|---|---|---|
| **B6** (tested here) | **-4%** | Weak/borderline phenotype |
| **D3** (never tested) | **-36%** | The dramatic phenotype the hypothesis was built to explain |

**B6 is the weaker of the two deletion clones for the very phenotype (HBB reduction) the
splicing hypothesis is meant to explain.** A null splice-junction result on B6 is real evidence
against the hypothesis, but it is not decisive: D3 -- the clone with the actual -36% HBB
reduction that motivated the hypothesis -- was never run through splice-junction analysis.
`scripts/analyze_splice_junctions.py` (deprecated 2026-03-06) points to a machine-local path
(`D:/ДНК/fastq_data/junctions`) not available in this environment; D3 FASTQ/junction data was
apparently never processed at all, on any machine, for this specific analysis.

**Verdict: REPEAT (targeted), not full REJECT.** The hypothesis is disfavored by the B6 null
result but remains formally untested on its own strongest predicted case (D3). See companion
task: fetch D3 RNA-seq from GSE160420 and complete the splice-junction analysis before treating
this hypothesis as fully closed.

## What this does NOT mean

1. Does NOT mean the 3'HS1 loop has no functional role -- Himadewi et al. 2021's own published
   finding (fetal globin HBG1/2 reactivation, 37-53% HbF+ cells in B6/D3 vs 4.3% WT) is real and
   independently confirmed; only the SPLICING mechanism proposed here (as opposed to the
   published transcriptional-switching mechanism) lacks support from the tested clone.
2. Does NOT mean D3's dramatic -36% HBB expression change is unexplained -- it may be explained
   by the published fetal-globin-competition mechanism (LCR redirected to HBG1/2) rather than by
   aberrant HBB splicing. These are not mutually exclusive with the null splicing result on B6.
3. Does NOT close the door on the "Loop That Stayed" hypothesis until D3 is tested directly.

## Do not retry without

D3 RNA-seq data from GSE160420, run through the same corrected splice-junction pipeline used
for WT/B6/A2 (see `results/hbb_splice_analysis.json` methodology, NOT the deprecated
`scripts/analyze_splice_junctions.py` which had a BED12 parsing bug already fixed once).
