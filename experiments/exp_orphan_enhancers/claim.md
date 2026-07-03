---
experiment: exp_orphan_enhancers
date: 2026-07-01
ladder_tier: Standard
question_type: Descriptive
status: IN PROGRESS
---

# Claim: Orphan enhancers are enriched for ClinVar VUS relative to nearest-gene-matched enhancers

## EstimandOps L0

**Question type:** Descriptive
→ "Do ClinVar VUS cluster near 'orphan' enhancers (ABC-predicted target gene ≠ nearest gene)
more than near 'regular' enhancers (ABC-predicted target gene = nearest gene)?"

This is explicitly NOT a causal claim. We are not testing "does the orphan enhancer cause
the VUS's phenotype" — only whether a descriptive enrichment exists that would justify a
later, separate causal follow-up (CRISPRi-FlowFISH).

## L1 Estimand

- **Population:** Enhancer elements (ABC model class = intergenic/genic, non-promoter,
  ABC.Score >= 0.015) from Nasser et al. 2021 genome-wide predictions, 131 biosamples.
- **Exposure:** "Orphan" status — ABC-predicted TargetGene != nearest protein-coding gene
  by genomic distance (GENCODE v47 TSS).
- **Comparator:** "Regular" enhancers — ABC TargetGene == nearest gene.
- **Endpoint:** Presence of >=1 ClinVar variant with ClinicalSignificance == "Uncertain
  significance" within the enhancer interval (chr:start-end).
- **Summary measure:** Odds ratio (VUS presence, orphan vs regular), permutation-test p-value
  (10,000 shuffles of orphan/regular label, stratified by CellType/biosample).
- **MCID:** OR >= 2.0 AND permutation p < 0.01 on a HELD-OUT set of chromosomes not used to
  pick any analysis parameters — required before considering wet-lab follow-up.

## Natural Language Statement

We estimate the odds ratio of ClinVar VUS presence within orphan enhancers (ABC target !=
nearest gene) versus regular enhancers (ABC target == nearest gene), across all ABC-model
biosamples, using a stratified permutation test to control for biosample composition.

## What This Does NOT Mean

1. Does NOT establish that any specific VUS is pathogenic via its orphan enhancer.
2. Does NOT establish causality between enhancer disruption and target gene expression —
   that requires the separate CRISPRi-FlowFISH follow-up on specific loci.
3. Does NOT control for general variant-density confounds (well-sequenced/well-studied genes
   have more submitted ClinVar variants regardless of enhancer status) unless the matched
   control (below) is applied.

## Known Confound to Control (learned from prior sessions in this repo)

VUS submission density in ClinVar is NOT uniform across the genome — it correlates with how
much a gene/region has been clinically sequenced. A naive "VUS near orphan enhancer" count
would be confounded by this. Control: compare orphan vs regular enhancers MATCHED on
(a) nearest-gene ClinVar submission volume (proxy for sequencing/study intensity) and
(b) distance-to-TSS bucket. This mirrors the category-matched-control lesson from the
LSSIM/Class-B null result earlier in this project (see null_results/20260605-...).

## Pre-registered analysis split (before touching results)

- **Calibration set:** chr1-chr11 (parameter/threshold exploration allowed here only)
- **Held-out confirmatory set:** chr12-chr22, chrX (NO threshold changes after seeing this)

## Go/No-Go Criterion

- PROMOTE (justify wet-lab follow-up design): OR>=2.0 AND p<0.01 on held-out set
- REPEAT (refine matched control, try different confound adjustment): 1.3<=OR<2.0 or 0.01<=p<0.05
- REJECT: OR<1.3 or p>=0.05 on held-out set → file to null_results/
