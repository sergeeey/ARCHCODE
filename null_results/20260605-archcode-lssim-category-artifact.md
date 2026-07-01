# REJECT — ARCHCODE LSSIM as independent pathogenicity signal

**Experiment ID:** 20260605-archcode-lssim-category-artifact
**Original claim date:** ~2026-02 to 2026-03 (v2.8-v2.16 manuscript iterations)
**Falsification date:** 2026-06-05
**Formalized into null_results/:** 2026-07-01 (retroactive — see note below)

## Claim being rejected

> ARCHCODE's LSSIM (Structural Similarity Index between wild-type and mutant chromatin contact
> maps) is an independent structural signal of variant pathogenicity, distinct from sequence-based
> annotation (VEP/SpliceAI/CADD), achieving ROC AUC=0.977 on HBB ClinVar variants.

## Why falsified

[VERIFIED-INLINE] via `results/p2_hbb_truth/HBB_TRUTH_AUDIT.md` (2026-06-05) and
`scripts/generate-unified-atlas.ts:291-303,328-348,392-398`:

1. LSSIM's perturbation strength is a direct lookup from `CATEGORICAL_EFFECTS[VEP_category]` — a
   hardcoded table mapping VEP consequence category to effect magnitude. It is not derived from
   independent 3D structural evidence.
2. Position-only control (uniform perturbation strength, category information removed): AUC drops
   from 0.977 to 0.551 — near chance.
3. Within-category AUC (25 category-locus combinations): median = 0.52 (chance level). Only one
   combination (TP53 splice_region) survives FDR correction (AUC=0.69).
4. A trivial baseline mapping VEP category directly to a score, with no chromatin simulation at
   all, achieves AUC≈0.98 — matching the "physics" pipeline's headline number.
5. Independent Hi-C retest (HUDEP2 cell line, `results/p4_hudep2_hbb/HUDEP2_HBB_DECISION.md`,
   2026-06-05): Pearson r=0.16 (p=0.30, not significant); within-category AUC=0.5000 exact.

**Verdict:** The pooled AUC=0.977 headline is a category-composition artifact (Simpson's
Paradox) — pathogenic variants in the dataset are predominantly coding (nonsense, frameshift),
benign variants predominantly non-coding (intronic, synonymous). LSSIM reproduces this known
category split; it does not independently discriminate pathogenic from benign variants within
the same functional class.

## What this does NOT mean

1. Does NOT mean the loop-extrusion contact-matrix simulation is mathematically incorrect —
   only that its downstream LSSIM score, as currently computed (perturbation strength gated by
   VEP category), does not add discriminative information beyond the category label itself.
2. Does NOT mean all ARCHCODE findings are invalid — the "27 pearl variants" / VEP-blind-spot
   framing may still hold value as a *discovery* tool (flagging candidates for follow-up), but
   NOT as an independent pathogenicity *predictor* with AUC=0.977 as evidence.
3. Does NOT preclude a redesigned LSSIM (perturbation strength derived from position/sequence
   context rather than VEP category) from carrying real signal — untested.

## Do not retry without

A redesigned effect-strength model that does NOT take VEP consequence category as an input
(directly or via a lookup table), tested with the same position-only / within-category controls
used to falsify this version. Any resubmission of this claim must report within-category AUC as
the primary metric, not pooled AUC.

## Formalization note (process gap this file addresses)

This finding was correctly discovered and documented in `results/p2_hbb_truth/HBB_TRUTH_AUDIT.md`
and `results/p4_hudep2_hbb/HUDEP2_HBB_DECISION.md` on 2026-06-05, and disclosed honestly in the
`manuscript/taxonomy_paper/` Bioinformatics Advances submission draft (merged to main 2026-07-01,
commit 1b14805) — but was never routed through `null_results/` per this project's own
Falsification Ladder protocol (`falsification-ladder.md`), despite being a clear REJECT-grade
verdict on the original v2.8-v2.16 headline claim. This file closes that gap retroactively.
