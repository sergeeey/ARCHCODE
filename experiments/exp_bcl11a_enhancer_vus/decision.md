---
experiment: exp_bcl11a_enhancer_vus
date: 2026-07-02
verdict: CANDIDATE FLAGGED (via gnomAD follow-up) — 2 rare, unstudied variants near the known functional motif; not a finding, a lead
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

## gnomAD follow-up (2026-07-02, same day)

Queried gnomAD v2.1.1 (GRCh37) GraphQL API for the same window
(chr2:60,710,000-60,732,000). **Sanity check:** rs1427407 recovered at exactly
chr2:60,718,043 with AF=0.811 (matches its known status as a common, high-frequency variant)
-- confirms the window and query are correct. **1,810 total variants** found in this 22kb
window (vs 0 in ClinVar) -- directly confirms the "wrong database" diagnosis above: rare
variation is abundant here, ClinVar simply never captured any of it.

**Candidate search:** restricted to variants within +-15bp of rs1427407's exact position
(the approximate footprint of the GATA1/TAL1 composite motif it disrupts, per Bauer et al.
2013 Science). Found 3 variants in this tight window: rs1427407 itself (AF=0.81, already
characterized), and two RARE variants:

| Variant | Position | Distance from motif | Allele count | Literature status |
|---|---|---|---|---|
| rs369310985 | chr2:60,718,048 | 5bp | AC=6 (rare, not singleton) | **Not found in any publication** (WebSearch, 2026-07-02) |
| rs1196343157 | chr2:60,718,028 | 15bp | AC=1 (singleton) | **Not found in any publication** |

Confirmed via WebSearch that neither variant appears in any BCL11A-enhancer/HbF literature,
unlike the 4 well-characterized SNPs also present in this window (rs1427407, rs6706648,
rs6738440, rs7606173, all from Bauer 2013 Science / subsequent fine-mapping).

### What this is and is NOT

This IS a legitimate, systematic, defensible candidate-flagging result -- exactly what
claim.md pre-registered as the goal ("flag candidate variants for follow-up, not test an
enrichment"). rs369310985 in particular (AC=6, not a singleton, 5bp from a functionally
characterized motif) is a genuinely novel, unstudied candidate worth a literature/functional
follow-up.

This is NOT a discovery, NOT proof of pathogenicity, and NOT proof of HbF effect. It is a
computationally-generated hypothesis for a specific, named variant, at the appropriate
confidence level for this kind of descriptive search: "here is one lead a wet-lab
collaborator or literature search might want to check next," not "we found something."

### Recommended next step (not yet done, requires resources beyond this session)

1. Check rs369310985 against any available functional genomics track (ATAC-seq footprint,
   TF ChIP-seq at this exact position) to see if it falls within an actual bound TF peak,
   not just the general DHS region.
2. If pursued further, this is now at the point where either (a) a literature/database
   specialist confirms it's genuinely unstudied, or (b) a functional assay (luciferase
   reporter, EMSA for GATA1/TAL1 binding) would be the actual test -- both outside this
   session's scope (no wet lab, no paid literature-mining tools beyond WebSearch).

## Recommendation

The ClinVar-only framing of this experiment is exhausted (0 hits, reason understood). The
gnomAD follow-up produced one concrete, checkable, previously-unflagged candidate
(rs369310985) -- small, honest, and exactly the kind of output this project's methodology is
suited to producing: a specific lead for someone with wet-lab or deep-literature-access
resources to pick up, not a self-contained discovery.
