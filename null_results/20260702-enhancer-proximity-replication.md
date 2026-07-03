# REJECT — Enhancer proximity signal does not replicate at BCL11A/KLF1/GATA1

**Experiment ID:** 20260702-enhancer-proximity-replication
**Falsification date:** 2026-07-02

## Claim being rejected

> The enhancer-proximity signal found at HBB (OR=34.05) generalizes to other well-characterized
> erythroid loci (BCL11A, KLF1, GATA1): ClinVar Pathogenic variants sit closer to K562 H3K27ac
> peaks than Benign variants, within VEP consequence category.

## Result

0/3 loci meet the pre-registered MCID (OR>=3, FDR-p<0.05). Full detail, including a real bug
found and fixed mid-experiment (coordinate-window ClinVar extraction pulled in neighboring
genes' variants, inflating an apparent GATA1 signal that vanished once filtered to true
GATA1-annotated variants), is in `experiments/exp_enhancer_proximity_replication/decision.md`.

## Why this matters as a process example

An initial run showed a promising signal at GATA1 (OR=10.83, FDR-p=0.0003). Asked to hold up
under stronger scrutiny before moving to a new hypothesis, inspection of the individual
variants found one was mislabeled (belonged to a neighboring gene, HDAC6, not GATA1) due to a
coordinate-window-only ClinVar filter. Fixing the filter (matching ClinVar's own GeneSymbol
field) removed the apparent signal entirely. This is the falsification-first process working
as intended -- a promising early result was not reported as a finding until it survived an
attempt to break it, and it did not survive.

## What this does NOT mean

1. Does NOT mean no effect exists at these loci -- post-fix sample sizes (esp. KLF1, GATA1)
   are underpowered; this is "not demonstrated," not "disproven."
2. Does NOT affect the original HBB finding (different methodology/data).
3. Does NOT mean this coordinate-window bug affected other experiments in this project --
   verified to be specific to this one fetch script.

## Do not retry without

Larger, properly gene-symbol-filtered variant sets at KLF1/GATA1, and a resolved H3K27ac
data source for BCL11A (see decision.md's data-quality caveat -- nearest peak in the archived
ENCFF252DWA replicate is 1.7Mb from the gene body, implausible for this locus).
