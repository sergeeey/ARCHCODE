---
experiment: exp_bcl11a_enhancer_vus
date: 2026-07-02
verdict: INCONCLUSIVE — wrong data source (0 VUS found; ClinVar structurally underpowered for this question type)
---

# Decision — BCL11A Enhancer VUS Search

## Result

Searched chr2:60,710,000-60,732,000 (hg19, spans all 3 published DHS sites +55/+58/+62,
anchored on VEP-confirmed rs1427407 at chr2:60,718,043). Found **2 ClinVar entries, 0 VUS**:

1. chr2:60,720,246 — Benign SNV, ~2.2kb from rs1427407.
2. chr2:60,719,185 — "Likely pathogenic", but this is a 549kb multi-gene deletion
   (chr2:60,719,185-61,268,266) spanning BCL11A, PAPOLG, PEX13, PUS10, REL. Its pathogenicity
   almost certainly reflects loss of one or more of the OTHER genes (REL is a proto-oncogene)
   -- not specific disruption of the BCL11A erythroid enhancer mechanism. Its start coordinate
   happens to fall in the search window; this is not "a variant in the enhancer" in any
   mechanistically meaningful sense (same class of coordinate-window artifact already found
   and fixed in `exp_enhancer_proximity_replication`, but correctly EXCLUDED here since this
   experiment does not claim it as a hit).

## Interpretation

Zero VUS is not a failed experiment (pre-registered as a valid outcome in claim.md) -- it is
informative about **why** this locus's famous biology never showed up as a ClinVar finding:
ClinVar is populated by clinical diagnostic labs testing patients for Mendelian disease.
Common regulatory SNPs that modulate a quantitative trait (HbF level) -- like rs1427407 and
its neighbors -- were discovered by population-genetics GWAS (Bauer 2013, Uda 2008), not by
clinical diagnostic sequencing, and this class of finding is not the kind of result that gets
submitted to ClinVar at all. ClinVar is structurally the wrong database for this question.

## What this does NOT mean

1. Does NOT mean no rare/undiscovered variants exist at this locus with clinical relevance --
   only that ClinVar specifically has none on record as of 2026-07-02.
2. Does NOT mean the BCL11A-enhancer-HbF connection is unimportant -- it is extremely well
   established (see claim.md novelty-check section) via non-ClinVar sources.
3. Does NOT close the door on a "rare variant at a known functional element" search --
   only redirects it to a more appropriate data source (see below).

## Correct data sources for this question (not yet queried)

1. **gnomAD** -- population allele frequencies at this exact locus would show whether any
   rare variants exist there at all, independent of clinical classification.
2. **The original GWAS/fine-mapping papers' supplementary data** (Bauer et al. 2013 Science,
   Canver et al. 2015 Nature) -- these directly report the functionally-tested variant set at
   this locus, which is the actual authoritative source, not ClinVar.
3. **UK Biobank / other large biobank GWAS summary statistics** for HbF or related red-cell
   traits, if available, would show the full common-variant association landscape here.

## Recommendation

This specific ClinVar-VUS-search framing for Hypothesis B is exhausted -- 0 hits, and the
reason why is now understood (wrong database class for this question type). Re-attempting
this exact search will not yield different results. If this locus is worth pursuing further,
the next step is gnomAD population-frequency lookup at this coordinate window, not another
ClinVar query.
