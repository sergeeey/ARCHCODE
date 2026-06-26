# Paper 3 — Self-Review (A6, NeurIPS-style, 3 personas)

**Date:** 2026-06-12
**Object:** PAPER3_SKELETON.md (reframed case-study, post-skeptic, verified refs)
**Method:** 3 reviewer personas + ensemble. Ratings 1–10 (NeurIPS scale: 6=weak accept,
7=accept). This reviews the paper *as a journal referee*, not the claims' truth
(that was A5 skeptic).

---

## Reviewer 1 — Methodologist / statistician

**Summary:** A reproducible audit showing a physics-informed loop-extrusion variant
score (LSSIM) carries no signal beyond consequence category, with a sign-flip "mirror"
diagnostic demonstrated across three loci.

**Strengths:** Rigorous; source-traced; strong negative controls (ablation suite,
mirror); honest about underpowering and weighting-dependence of −0.34; conclusion rests
on robust K1/K2, not the weak within-category test.

**Weaknesses:**
- W1 (major): the audit targets a **single tool the author appears to have built**.
  Falsifying one's own niche model risks being a strawman — what is ARCHCODE's user
  base? If small, impact is limited.
- W2: the mirror is **self-admittedly near-tautological** under strong category
  separation → the headline methodological nugget is thin.
- W3: generality of the gate sequence is asserted, not demonstrated on an
  *independently-built* tool.

**Soundness:** 8/10. **Contribution:** 4/10. **Presentation:** 7/10.
**Rating: 5/10 (borderline)** — sound but impact-limited. **Confidence: 4/5.**

---

## Reviewer 2 — Genomics domain expert

**Summary:** Demonstrates that an analytical mean-field chromatin score reduces to a
category lookup; tissue-mismatch and 5 kb-resolution failures block a fair test.

**Strengths:** Biology framing correct; the tissue-mismatch (K562 for erythroid genes)
and HUDEP-2 resolution points are genuine, practically useful lessons; ClinVar
category structure handled correctly.

**Weaknesses:**
- W4 (major): for a domain expert the result is **low-surprise** — "a category-driven
  mean-field model is a category lookup" is almost expected. Novelty of *finding* is
  modest.
- W5 (major): does **not** test the tools people actually use (Akita, Orca). The
  cautionary value is confined to ARCHCODE-like models; applying the mirror to a
  widely-used predictor would multiply impact.
- W6: "what a fair test requires" is sensible but standard.

**Soundness:** 7/10. **Contribution:** 4/10. **Presentation:** 7/10.
**Rating: 5/10** — weak accept only at a reproducibility/negative-results venue.
**Confidence: 4/5.**

---

## Reviewer 3 — Broad / reproducibility / clarity

**Summary:** A transparent negative-result + diagnostic, with full code/data.

**Strengths:** Exemplary transparency; anti-overclaim section; honest limitations;
verified references; AI-use disclosed. A model of reproducible negative reporting.

**Weaknesses:**
- W7: scope feels narrow for a *full* paper — better fit as an Application Note /
  Matters-Arising / negative-results article.
- W8 (integrity/clarity): the paper does **not state that ARCHCODE is the author's own
  prior tool.** Disclosing this reframes the work as *self-correction* — a strong
  integrity signal and the natural explanation for the deep source access. Currently a
  reader could miss it.
- W9: a couple of method-dependent numbers (−0.34) — handled honestly, but flag-prone.

**Soundness:** 8/10. **Contribution:** 6/10 (as a reproducibility piece).
**Presentation:** 8/10. **Rating: 6/10 (weak accept at the right venue).**
**Confidence: 4/5.**

---

## Ensemble verdict

**Mean rating ≈ 5.3/10.** Consensus: **sound, honest, reproducible — but
impact/scope-limited.** The science is not in doubt (A5 confirmed); the gap is *reach*.

### Single highest-leverage improvement (all three reviewers converge)
**Apply the mirror diagnostic to ≥1 tool the author did NOT build** — e.g. an Akita/
Orca-derived variant score, or a published chromatin pathogenicity predictor — even on
a small variant set. This converts the paper from *"I falsified my own niche model"*
into *"here is a cheap, general diagnostic that detects category-confounding, shown on
a widely-used tool."* This directly answers W1, W3, W5, W4.

### Required quick fixes (cheap, do before submission)
1. **Disclose ARCHCODE provenance (W8):** add one sentence — "ARCHCODE is our own prior
   work; this paper is a self-correcting audit." Turns a hidden weakness into an
   integrity strength.
2. **Right-size the venue (W7):** target an Application Note / negative-results /
   reproducibility track explicitly, not a high-impact methods venue.
3. Keep the honest −0.34 weighting note (already done).

### Go / no-go
- **As-is → submittable** to a negative-results / reproducibility venue
  (F1000Research, GigaScience, PLOS ONE) at ~weak-accept. Honest and complete.
- **With the external-tool extension → materially stronger** (PLOS Comp Bio plausible).
  This is real follow-on work (apply mirror to Akita/Orca), not a quick edit.

**Recommendation:** apply fixes 1–3 now (minutes); then a fork —
(a) submit as honest negative-results note now, or
(b) invest in the external-tool extension to raise the ceiling.
This is a management decision for the author, not a blocker.
