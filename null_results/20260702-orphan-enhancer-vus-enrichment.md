# REJECT — Orphan enhancers are NOT enriched for ClinVar VUS

**Experiment ID:** 20260702-orphan-enhancer-vus-enrichment
**Claim date:** 2026-07-01
**Falsification date:** 2026-07-02

## Claim being rejected

> ClinVar VUS cluster near "orphan" enhancers (ABC-model target gene != nearest gene by TSS)
> more than near "regular" enhancers (ABC target == nearest gene), at OR>=2.0.

## Result (pre-registered calibration/held-out split, `claim.md`)

| | Calibration (chr1-11) | Held-out (chr12-22,X) |
|---|---|---|
| n orphan / n regular | 430,628 / 595,439 | 285,959 / 375,335 |
| Cochran-Mantel-Haenszel OR | 0.999 | 1.221 |
| p-value | 0.93 | ~0 (large-n artifact) |

**Pre-registered go/no-go (claim.md): PROMOTE requires OR>=2.0 AND p<0.01 on held-out.
Actual: OR=1.221 — far below threshold. REJECT.**

The held-out p-value being ~0 despite a small OR (1.22) is exactly the "statistically
significant but practically meaningless" pattern the MCID (OR>=2.0, not just p<0.05) was
pre-registered specifically to filter out — with n=661,294, even trivial effect sizes reach
significance. This is a textbook example of why effect size, not just p-value, must be the
go/no-go criterion.

## Two real bugs caught and fixed before trusting this result [VERIFIED-bash]

1. **Genome build mismatch**: the ABC model predictions file (Nasser et al. 2021) uses
   hg19/GRCh37 coordinates; GENCODE and ClinVar were initially pulled in hg38. Confirmed
   empirically (NOC2L TSS in ABC file=894679 matches hg19=894689; hg38=959309, ~65kb off).
   This alone produced an implausible 85-91% "orphan" rate (published range ~30-40%) in two
   earlier runs. Fixed by re-fetching GENCODE + ClinVar VUS on GRCh37/hg19
   (`scripts/fetch_gencode_hg19_stranded.py`, `scripts/fetch_clinvar_vus_hg19.py`).

2. **Interval-overlap bug**: `has_vus_overlap()` used a fixed +/-5-record window around a
   bisect insertion point, which silently misses wide-spanning VUS (large CNVs/indels)
   sitting behind a dense cluster of narrower variants -- a one-directional false-negative
   bug in the primary outcome variable. Caught by `Agent(reviewer)` with a concrete
   reproducing case, fixed with an exact O(log n) running-max-end interval check (see
   `scripts/orphan_enhancer_analysis.py:load_vus_index`/`has_vus_overlap`, 2026-07-02).
   Confirmed fixed with a unit test reproducing the reviewer's exact failing case.

After both fixes, the orphan rate (43%) is finally in a biologically plausible range,
and the result (OR~1, no enrichment) is stable and consistent between calibration and
held-out sets -- this is a genuine null, not an artifact.

## What this does NOT mean

1. Does NOT mean orphan-enhancer / distal-regulatory-target biology is false in general —
   only that this specific operationalization (ABC-model target != nearest-TSS gene, VUS
   overlap of the enhancer interval, genome-wide, unweighted by locus/tissue relevance)
   shows no enrichment.
2. Does NOT rule out a signal restricted to tissue-matched biosamples for a specific disease
   area (this analysis pooled all 131 ABC biosamples indiscriminately) — a locus-specific,
   tissue-matched version of this test was not run.
3. Does NOT mean CRISPRi-FlowFISH validation of any individual orphan-enhancer/VUS pair
   would be uninformative — this was a genome-wide descriptive screen, not a claim about
   any specific locus.

## Do not retry without

Either (a) restricting to tissue-matched biosamples for a specific disease locus (the
original narrower framing before this session's "genome-wide, multiple loci" choice), or
(b) a different exposure definition — e.g., ABC score magnitude or contact-frequency
percentile rather than a binary orphan/regular split, which discards graded information.
