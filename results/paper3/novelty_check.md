# Paper 3 — Novelty Check (FL Step −3)

**Date:** 2026-06-12
**Skill:** novelty-assessment (harsh-critic persona)
**Rounds:** 4 (WebSearch; Semantic Scholar script rate-limited → 0)
**Evidence:** [VERIFIED-web] search snippets; [WEAK] on Lu 2025 exact overlap (full PDF 403, read from abstract + snippets only — MUST confirm full text before submission)

---

## Verdict: **NOT NOVEL as a "falsification framework" methods paper — PIVOT required**

Confidence: **MEDIUM** (capped: could not read the closest prior-art full text; 403).

The original framing — *"we present a six-gate falsification framework for chromatin
variant scores"* — is **scooped**. Submit as-framed → high desk-reject risk for being
incremental over established prior art. The work survives only **reframed** as a
reproducible negative-result case study that *operationalizes* existing critiques on a
new model class.

---

## Closest prior art (per contribution)

### Contribution 3 — "category confounds the pathogenicity AUC" → NOT NOVEL
**Lu et al. 2025, bioRxiv 10.1101/2025.09.05.674459** — *"Genomic heterogeneity
inflates the performance of variant pathogenicity predictions."* (Sept 2025)
- Core claim is essentially identical: AUC is inflated by category-prevalence
  differences; canonical-splice variants are "almost always pathogenic and trivial";
  unclear whether models separate categories or distinguish patho/benign *of the same
  type*; fix = **within-type / category-stratified** evaluation + a benchmark.
- Broader than ARCHCODE (frontier AI models, all variant types).
- → ARCHCODE's d −2.67 → −0.34 decomposition is an **application instance** of an
  already-published principle, not a new method.

### Contribution 1 — "matched-control 6-gate framework" → NOT NOVEL
- Covariate-matched benign controls (population-frequency-matched, annotation-type and
  variant-type controlled) + consequence stratification are **established** in variant-
  predictor evaluation (multiple 2024–2025 works; surfaced in round 1).
- Tissue-match and resolution gates are sensible data-quality checks, not a novel
  contribution sufficient for a standalone methods paper.

### Contribution 2 — "mirror / sign-flip test" → PARTIALLY NOVEL (modest)
- Label permutation (→ collapse to AUC 0.5) is a standard negative control.
  Sign-flip ablation exists in deep-learning interpretability.
- The **specific mirror prediction** — AUC_categorical ≈ (1 − AUC_inverted), proving a
  score is a *directional category lookup* (collapse to 1−x, not to 0.5) — I found **no
  exact prior match**. It is a sharper, distinct diagnostic, demonstrated locus-general.
- Reviewer framing: "a nice, clean negative control," not a new paradigm. Narrow
  novelty; insufficient to carry a methods paper alone.

### Application novelty — GENUINE but it's a case study, not a method
- No prior work falsifies a **physics-informed mean-field loop-extrusion simulation**
  (ARCHCODE-type) for variant pathogenicity and shows it reduces to a category lookup.
  Loop-extrusion literature (Akita, Orca, dLEM, 3DPolyS-LE) targets genome-folding
  prediction, not pathogenicity falsification.

---

## Required pivot (keeps the paper alive)

| Drop (scooped) | Keep / reframe (defensible) |
|---|---|
| "We invented a falsification framework" | "We operationalize the heterogeneity-inflation critique (Lu et al. 2025) on a new model class" |
| "Novel matched-control method" | "First reproducible audit of a physics-informed loop-extrusion simulator" |
| Category-confound as our discovery | Cite Lu 2025 + matched-control lit as the framework we apply |
| Methods-paper positioning | Negative-result / cautionary case study + the **mirror diagnostic** as the one methodological nugget |

**Mandatory before submission:** read Lu et al. 2025 full text; cite prominently in
Introduction + Discussion; add a "Relation to prior work" paragraph stating explicitly
what is and isn't new. Venue: prefer one that values negative results / reproducibility
(e.g. PLOS Comp Bio negative-results-friendly, or a Matters-Arising / cautionary note),
not a "novel method" track.

---

## Gate decision
- **KILL** the "novel framework" claim.
- **PROCEED** with Chain A on the reframed case-study + mirror-diagnostic positioning.
- Chain A step 2 (academic-research) now has a **required seed citation**: Lu et al.
  2025 — and must harvest the matched-control prior-art cluster, not present it as new.

## Sources
- Lu et al. 2025, bioRxiv 10.1101/2025.09.05.674459 (closest prior art) — full text pending
- Round-1/2/3 WebSearch snippets (matched controls, within-category stratification, label-permutation/sign-flip negative controls, Akita/Orca/dLEM)
