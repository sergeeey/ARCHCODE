---
experiment: exp_synonymous_codon_optimality
date: 2026-07-07
verdict: REJECT (primary Cliff's delta = -0.151, MCID required |delta| >= 0.2) -- real, correctly-signed, statistically robust, but sub-threshold effect
---

# Decision — Synonymous-Variant Codon-Usage Optimality

## Result

Full pipeline: genome-wide ClinVar (829 pathogenic / 685,044 benign synonymous SNVs, benign
subsampled to 5,000 with fixed seed=42, pre-registered in claim.md before any VEP call) ->
Ensembl VEP GRCh37 REST API (`codons` field) -> Delta codon-usage frequency (Kazusa human
table, ALT per-mille minus REF per-mille) -> Mann-Whitney U + Cliff's delta, BH-corrected
across primary + 1 pre-registered sensitivity check.

| Test | n (path/benign) | median Delta (path/benign) | Cliff's delta | p (BH) |
|---|---|---|---|---|
| Primary (all) | 825 / 4988 | -7.5 / -3.1 | **-0.151** | 7.9e-12 |
| Sensitivity (>=10bp from splice boundary) | 288 / 4513 | -5.7 / -3.1 | **-0.166** | 2.3e-6 |

MCID (pre-registered in claim.md): `abs(cliffs_delta) >= 0.2 AND p_value_bh < 0.05`.
Both tests meet the p-value bar (overwhelmingly), **neither meets the effect-size bar**.

## Interpretation

The direction is correct and consistent in both tests: ClinVar Pathogenic synonymous variants
shift toward less-optimal codons (more negative Delta usage) than Benign ones, and the
sensitivity check -- which removes variants near a splice junction, the literature's main
documented alternative mechanism for "pathogenic synonymous" (see claim.md novelty check) --
does NOT weaken the effect. If anything it's marginally larger (-0.166 vs -0.151) despite
losing 65% of the pathogenic n (825->288), which argues against "this is just a splicing
proxy in disguise."

But per this project's own recurring lesson (see `null_results/20260702-orphan-enhancer-vus-enrichment.md`,
"significant only due to enormous n, not practically meaningful"): with n in the thousands,
p<1e-6 is easy to reach for a genuinely small effect. Cliff's delta of -0.15 to -0.17 is a
small effect by the conventional Cliff's-delta scale (small: 0.11-0.28, medium: 0.28-0.43),
and does not clear the pre-registered MCID bar that was set BEFORE seeing this number.

## What this does NOT mean

1. Does NOT mean codon optimality is irrelevant to synonymous-variant pathogenicity -- the
   signal is real (correct direction, robust to the splice-proximity control), just smaller
   than this experiment's pre-registered practical-significance threshold on its own.
2. Does NOT contradict the published multi-feature ensemble predictors cited in claim.md's
   novelty check -- they combine codon-usage bias with several other features precisely
   because, as found here, no single feature is independently strong; this result is
   consistent with, not a refutation of, that literature.
3. Does NOT mean the splice-junction confound is fully controlled -- >=10bp is a crude proxy,
   not a real splice-effect predictor (e.g. SpliceAI); the sensitivity check only partially
   addresses the confound.
4. Does NOT establish causality -- descriptive/predictive association only, as pre-registered.

## Recommendation

**REJECT per the pre-registered Go/No-Go criterion** (primary test does not meet MCID) ->
filed to `null_results/`. Not a dead end for the underlying biology (well-established,
see claim.md), but the SINGLE simple feature tested here, alone, is not the project's next
lead. If revisited: this Delta-usage feature would need to be combined with other features
(structure, splicing-predictor score, conservation) to reach a useful effect size -- exactly
the ensemble-predictor approach the novelty check found already exists in the literature,
so a from-scratch rebuild of that ensemble is not a novel next step for this project either.
