---
experiment: exp_enhancer_proximity_replication
date: 2026-07-02
verdict: REJECT (0/3 loci meet pre-registered MCID, after a real bug fix removed the one apparent signal)
---

# Decision — Enhancer Proximity Replication (BCL11A / KLF1 / GATA1)

## Timeline (both runs shown -- this is the point)

### Run 1 (initial, window-filtered only)

| Locus | n path/benign | CMH OR | FDR-p | MCID met? |
|---|---|---|---|---|
| BCL11A | 91 / 48 | undefined (degenerate) | 0.0193 | Inconclusive (data-quality gap, see below) |
| KLF1 | 314 / 825 | 0.338 (wrong direction) | 0.0630 | No |
| GATA1 | 72 / 194 | **10.83** | **0.0003** | **Yes** |

Verdict at this point: REPEAT, with GATA1 flagged as a promising "pearl" -- BUT flagged as
needing independent replication before being trusted (n=14 pathogenic missense is small).

### Bug found while trying to strengthen the GATA1 result

The user asked to "docrutit'" (harden/replicate) the GATA1 finding before moving to a new
hypothesis. Inspecting the 14 pathogenic missense variants individually found one
(`NM_006044.4(HDAC6):c.1894C>T`, chrX:48,675,835) that VEP correctly attributes to **HDAC6**,
not GATA1 -- it was included only because `fetch_clinvar_erythroid_loci_hg19.py` selected
variants by genomic coordinate window (gene body +-50kb) WITHOUT checking ClinVar's own
`GeneSymbol` field. In a gene-dense region, a coordinate window pulls in neighboring genes'
variants under the wrong locus label.

**Fix:** added a `GeneSymbol` match filter (`scripts/fetch_clinvar_erythroid_loci_hg19.py`).

### Run 2 (after GeneSymbol fix)

| Locus | n path/benign (before -> after fix) | CMH OR | FDR-p | MCID met? |
|---|---|---|---|---|
| BCL11A | 91/48 -> 91/48 (unchanged -- large gene, window ~ body) | undefined | 0.0386 | No |
| KLF1 | 314/825 -> **22/67** (huge drop -- chr19 is gene-dense, most "KLF1 variants" were neighbors) | undefined | 1.0000 | No |
| GATA1 | 72/194 -> **69/131** (lost the HDAC6 variant + ~63 neighbor-gene "benign" variants) | **undefined (signal gone)** | 0.7389 | **No** |

**GATA1's OR=10.83 signal did not survive the fix.** With only genuinely GATA1-annotated
variants, CMH-OR is degenerate (no computable signal) and Mann-Whitney p=0.49 (not close to
significant). The apparent "pearl" was substantially or entirely an artifact of neighboring
chrX genes' variants being mislabeled as GATA1 variants by coordinate-only filtering.

## FINAL VERDICT: REJECT (0/3 loci meet MCID)

This is the correct, final, honest reading. The one positive signal in this experiment did
not survive an increase in data quality -- it decreased, not increased, in specificity. This
is exactly the outcome the pre-registration was designed to catch, and it worked.

## Caveat: reduced power, not necessarily "no true effect exists"

KLF1 and GATA1's post-fix sample sizes are much smaller than the original (window-based)
run. `CMH-OR=None` for KLF1/GATA1 reflects a degenerate/underpowered statistic at the 1kb
threshold (many strata now have too few observations for a computable variance), not
necessarily strong evidence of a true null. This experiment cannot distinguish "no effect"
from "underpowered to detect an effect" at KLF1/GATA1's current sample sizes. BCL11A remains
separately flagged as untested (H3K27ac data-quality gap, unresolved).

## What this does NOT mean

1. Does NOT confirm the enhancer-proximity mechanism generalizes across erythroid loci --
   0/3 properly-filtered loci show it.
2. Does NOT prove the mechanism is false at these loci either -- KLF1/GATA1 are now
   underpowered after correct gene filtering; BCL11A's H3K27ac data-quality gap is still
   unresolved. This is "not demonstrated," not "disproven."
3. Does NOT invalidate the original HBB finding (different methodology, different data,
   already independently supported by AlphaGenome CAGE convergence per the taxonomy paper).
4. Does NOT mean the GeneSymbol-filtering bug affected earlier work in this project --
   this specific coordinate-window-without-gene-filter pattern is unique to this script;
   `exp_orphan_enhancers` and `exp_archcode_sv` used different (correct) filtering logic.

## Do not retry without

1. A properly-powered variant set (larger n) at KLF1/GATA1, or a wider significance/effect
   threshold acknowledging the power limitation.
2. Resolving the BCL11A H3K27ac data-quality gap with a non-archived ENCODE replicate before
   treating that locus as tested at all.
3. If re-attempting: validate that ClinVar `GeneSymbol` matches the intended locus for EVERY
   variant before analysis, not just coordinate-window membership -- this should be a
   standard check in this project's ClinVar-fetching scripts going forward.
