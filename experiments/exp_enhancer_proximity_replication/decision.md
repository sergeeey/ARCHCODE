---
experiment: exp_enhancer_proximity_replication
date: 2026-07-02
verdict: REPEAT (1/3 loci meet pre-registered MCID; 1 locus data-quality-inconclusive)
---

# Decision — Enhancer Proximity Replication (BCL11A / KLF1 / GATA1)

## Result (per pre-registered criteria in claim.md)

| Locus | n path/benign | Median dist path/benign | CMH OR | FDR-p | MCID met? |
|---|---|---|---|---|---|
| BCL11A | 91 / 48 | 293,822 / 294,365 bp | undefined (degenerate) | 0.0193 | **INCONCLUSIVE — see caveat** |
| KLF1 | 314 / 825 | 4,276 / 2,327 bp | 0.338 (wrong direction) | 0.0630 | No |
| GATA1 | 72 / 194 | 0 / 0 bp | **10.83** | **0.0003** | **Yes** |

**VERDICT: REPEAT (1/3 loci meet MCID: OR>=3 AND FDR-p<0.05).** Per pre-registered go/no-go,
this does not meet the PROMOTE bar (>=2/3) but is not a clean REJECT either (0/3) -- one
locus shows a real, category-controlled signal.

## Per-locus interpretation

### GATA1 — the pearl: real, but small and single-category

Traced the OR=10.83 to its source by inspecting the category-stratified bucket breakdown
(`results.json` -> `consequence_bucket_breakdown`). Two large single-sided buckets
(frameshift_variant: 40 pathogenic / 0 benign; synonymous_variant: 0 pathogenic / 109
benign) mathematically contribute **zero** to the CMH statistic (no comparison group within
that stratum -- confirms the category-stratification is doing its job, not just diluting a
category confound). The entire OR=10.83 comes from ONE stratum:

> **missense_variant**: 13/14 (93%) pathogenic-missense variants sit within 1kb of a K562
> H3K27ac peak, vs 30/55 (55%) benign-missense variants.

This is a real, category-matched comparison (both groups are missense, so this is not the
"pathogenic variants are more often coding" confound that killed the original SNV project).
But n=14 pathogenic missense variants is small -- treat as a promising lead, not a confirmed
finding, until replicated on an independent GATA1 variant set or validated functionally.

### KLF1 — null, wrong direction

n=1139 total, well-powered. Benign variants are actually CLOSER to H3K27ac peaks
(median 2327bp) than pathogenic ones (4276bp) -- opposite of the hypothesis. OR=0.34 (<1).
Not significant after FDR correction (p=0.063) but the direction alone argues against the
enhancer-proximity mechanism generalizing to KLF1.

### BCL11A — data-quality caveat, NOT a clean null

**[VERIFIED-bash]** The nearest H3K27ac peak to the BCL11A gene body in this specific ENCODE
file (ENCFF252DWA, archived hg19 replicate) is 1.7 Mb upstream and 202 kb downstream -- a
gap far exceeding the ~67kb average peak spacing on chr2 (3,631 peaks / ~243 Mb). BCL11A has
a well-documented erythroid-specific enhancer (the +58kb intronic element targeted by the
FDA-approved Casgevy/exa-cel therapy) -- complete absence of any H3K27ac signal within 1.7 Mb
is biologically implausible for an active erythroid locus and more likely reflects a coverage
gap or peak-calling dropout specific to this archived dataset, not a true absence of
enhancer activity.

**This locus's "does not meet MCID" result should NOT be read as a fair test of the
hypothesis** -- it is confounded by an apparent data-quality gap. Re-running with a
different/newer K562 H3K27ac replicate (or ATAC-seq/DNase as a cross-check) before drawing
any conclusion about BCL11A specifically.

## What this does NOT mean

1. Does NOT confirm the enhancer-proximity mechanism generalizes across erythroid loci --
   only 1/3 tested loci showed it, and that locus's effect rests on n=14 pathogenic variants
   in one VEP category.
2. Does NOT mean KLF1 or BCL11A definitively lack this signal -- KLF1 is a genuine null with
   reasonable power; BCL11A is inconclusive due to a likely data artifact, not tested fairly.
3. Does NOT replace or match the original HBB methodology (Q2b/LSSIM-based) -- this tested
   the simpler geometric proxy only, as pre-registered.

## Next steps (not yet done)

1. Re-fetch H3K27ac (or ATAC-seq) for K562/erythroid at BCL11A specifically from a different,
   non-archived ENCODE experiment to rule out the data-gap artifact.
2. If GATA1's missense-specific signal is real, look for an independent GATA1 variant
   cohort (e.g., a different ClinVar snapshot date, or a curated literature set) to replicate
   without re-using the same 14 pathogenic variants.
3. Given a single-category (missense-only) signal at one locus, out of 3 tested, this is NOT
   yet strong enough evidence to write up or claim externally -- needs the above replication
   first.
