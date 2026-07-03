---
experiment: exp_bcl11a_enhancer_vus
date: 2026-07-02
ladder_tier: Standard
question_type: Descriptive
status: CANDIDATE FLAGGED -- gnomAD follow-up found rs369310985 (5bp from known functional motif, AC=6, unstudied in literature); see decision.md
---

# Claim: ClinVar VUS exist within the known BCL11A erythroid enhancer (candidate flagging)

## EstimandOps L0

**Question type:** Descriptive.
"How many ClinVar variants of Uncertain Significance (VUS) fall within the well-characterized
BCL11A erythroid enhancer (DHS +55/+58/+62, Canver et al. 2015 Nature), and do any of them
sit near the known functional motif (GATA1/TAL1 composite, disrupted by rs1427407)?"

This is explicitly NOT a hypothesis test with a p-value or MCID -- it is a systematic search
and flagging exercise. Zero VUS found is a valid, fully reportable outcome (not a failed
experiment). A positive count does NOT itself establish pathogenicity or HbF-modifying effect
-- it only identifies candidates that would need functional validation (e.g., luciferase
reporter, CRISPR base-editing, or comparison against published GWAS/functional fine-mapping
data) before any causal or clinical claim could be made.

## Novelty check (per falsification-ladder.md Step -3, mandatory for AI-generated hypotheses)

The BROADER connection (BCL11A enhancer variants modulate HbF) is NOT novel -- it is
foundational, ~2008-2015 literature (Uda 2008, Menzel 2007, Bauer et al. 2013 Science, Canver
et al. 2015 Nature) that directly motivated the FDA-approved Casgevy/exa-cel therapy. Verified
via WebSearch before any data work began (see conversation record, 2026-07-02). The narrower
question here -- are there RARE ClinVar VUS at this locus, distinct from the well-studied
COMMON GWAS SNPs -- is the piece not already covered by GWAS (which is structurally powered
only to detect common variants).

## L1 Estimand

- **Population:** All ClinVar entries (any ClinicalSignificance, any variant type) within
  chr2:60,710,000-60,732,000 (hg19/GRCh37), anchored on rs1427407 (VEP-confirmed
  chr2:60,718,043) with margin to cover all 3 published DHS sites (+55/+58/+62).
- **Exposure/Intervention:** N/A (descriptive, not comparative).
- **Endpoint:** Presence and annotation (ClinicalSignificance, distance from rs1427407,
  GeneSymbol) of each variant found.
- **Summary measure:** Count and list of variants, stratified by ClinicalSignificance
  (especially "Uncertain significance").
- **MCID:** N/A (descriptive).
- **ICE:** None.

## Natural Language Statement

We enumerate all ClinVar-reported variants within the genomic window spanning the published
BCL11A erythroid enhancer DHS sites, reporting counts by clinical significance category, to
identify Uncertain Significance variants that may be candidates for the same regulatory
mechanism as the well-established common GWAS variants at this locus.

## What This Does NOT Mean

1. A found VUS does NOT mean it is pathogenic, benign, or HbF-modifying -- only that it is
   physically located in a functionally-characterized regulatory element and warrants
   downstream investigation.
2. This does NOT constitute novel discovery of the BCL11A-enhancer-HbF connection itself
   (established 2008-2015) -- only a systematic inventory of understudied rare variants there.
3. Does NOT establish causality for any individual variant without functional validation.
