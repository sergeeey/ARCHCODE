# ADR-036: Manuscript Reframe — "7/7 Consistency" → "HBB Pilot + Exploratory Extensions"

**Date:** 2026-05-25
**Status:** ACCEPTED
**Decision driver:** Skeptic agent verdict (isolated context red-team review)
**Manuscript:** `manuscript_v2_full.md` v2.18 (reframe), `abstract_content.typ` v1.1

---

## Problem

Prior manuscript framing claimed "7/7 loci (100%) biological consistency" while statistical robustness was only 1/4 (HBB only, after Bonferroni correction). This created internal inconsistency between:

- **Abstract / Conclusion:** "perfect biological consistency"
- **Limitations Section 4.4:** "statistical robustness is 1/4, not 7/7"

Skeptic verdict (independent red-team):
- 70% probability of peer review rejection
- "Solid HBB finding buried under overclaimed framing"
- Counter-arguments:
  1. Null in coding loci = tautology (CAGE doesn't measure protein function) — not "validation"
  2. Pilot → expand workflow = garden of forking paths (Gelman & Loken, 2013)
  3. "7/7 consistency" + 1/4 statistical = linguistic sleight of hand
- Verdict: reframe required, target shift Nature Genetics → Bioinformatics Advances

## Decision

Reframe manuscript from **"breakthrough discovery"** to **"HBB pilot + exploratory 6-locus extension"**.

**Key changes:**

| Section | Before | After |
|---------|--------|-------|
| Abstract (Orthogonal validation) | "achieved 7/7 loci (100%) biological consistency" | "HBB pilot robust (p=4×10⁻⁶); 6 exploratory loci directionally consistent" |
| Abstract (Conclusions) | "perfect biological consistency (7/7)" | "HBB pilot demonstrates feasibility; 7-locus extension exploratory, requires confirmation" |
| Section 3.4 heading | "Biological Consistency (7/7) but Weak Statistical Robustness (1/4)" | "HBB Pilot Result with Exploratory Extensions Across 6 Loci" |
| Section 3.4 body | "AlphaGenome achieved perfect biological consistency" | "Pilot-plus-extension design; HBB confirmatory, 6 loci exploratory (Gelman & Loken concern)" |
| Discussion 4.1 | "achieved perfect biological consistency (7/7 loci)" | "HBB pilot yielded robust result; exploratory 6-locus extension directionally consistent" |
| Discussion 4.3 | "7/7 biological consistency (100% matched)" | "HBB pilot result robust; multi-locus generalization requires confirmation" |
| Conclusion 4.5 | "achieved 7/7 biological consistency" | "HBB pilot robust; 7-locus extension exploratory" |
| Limitations 4.4 | "7/7 biological consistency, perfect directional agreement" | "Pilot-plus-extension; directional consistency exploratory (Gelman & Loken)" |
| Section 2 conclusion (line 81) | "7/7 biological consistency: 3 regulatory, 4 coding null" | "HBB pilot robust; 6-locus exploratory directionally consistent" |
| Section 3.3 conclusion (line 166) | "7-of-7 locus biological consistency (100%)" | "Pilot-plus-extension pattern; HBB confirmatory, 6 exploratory" |

**Reference added:** Gelman A, Loken E (2013) — garden of forking paths. Cited 4× in manuscript.

**Variant count fix:** `abstract_content.typ` 25,850 → 26,225 (consistency with `manuscript_v2_full.md:20`, P0 audit a3bbef2).

## Rationale

### Why reframe is honest, not weakening

The HBB result (p=4×10⁻⁶, Cohen's d=−1.53, Bonferroni-robust) is genuinely strong. It was buried under "7/7 consistency" framing because:
1. Coding null results are predicted trivially (CAGE doesn't measure coding) — counting them as "validation" inflates the success rate
2. MLH1 (p=0.022) and TERT (insufficient controls) failed Bonferroni — claiming "7/7" when only 1/4 robust is misleading
3. Loci were selected POST pilot — calling this "validation" is HARKing

Honest framing puts HBB front-and-center where it belongs. The 6-locus extension becomes context (regulatory-vs-coding dichotomy holds directionally), not the primary finding.

### Why this increases acceptance probability

| Venue | Pre-reframe | Post-reframe |
|-------|-------------|--------------|
| Research Square (LIVE) | 100% (already there) | 100% |
| bioRxiv (with Ronin) | 60% | 70% (less reviewer red flags) |
| Bioinformatics Advances | 25% | 40-50% (defensible pilot study) |
| NAR Genomics | 15% | 25-30% |
| Nature Genetics / AJHG | <5% | <5% (don't target) |

Skeptic estimate: reframe shifts acceptance from 25-30% → 40-50% at appropriate venue.

### What is preserved

- All numerical results (HBB p=4×10⁻⁶, MLH1 p=0.022, TERT hotspots +33/+53%, coding null p>0.40)
- All figures (Figure 3B, Table 3) — descriptive data unchanged
- All Methods sections — methodology was always sound
- The falsification-first story (6/6 hypotheses killed) — this is the actual contribution
- All limitations and caveats — already honest in Section 4.4

### What is removed

- "Perfect biological consistency" language (4 instances)
- "100% matched" / "7/7" overclaim (8 instances)
- Implicit promise that the multi-locus pattern is statistically confirmed

## Consequences

**Positive:**
- Internal consistency restored (abstract no longer contradicts limitations)
- Defensible against peer review attacks (Gelman & Loken explicitly addressed)
- Target venue shift toward realistic acceptance
- Reputation protection (no overclaim → no later scrutiny risk)

**Negative:**
- "Big findings paper" narrative weakened — this is a feature, not a bug, given the evidence
- May lose readers expecting breakthrough — but those readers would have rejected the paper anyway
- Title may need adjustment ("Systematic Falsification" still works; could add ", with HBB Pilot Validation")

**Action items:**
- [x] Reframe abstract (.md + .typ)
- [x] Reframe Section 3.4 heading + body
- [x] Reframe Discussion 4.1, 4.3, 4.5
- [x] Reframe Section 2/3.3 conclusion paragraphs
- [x] Update Limitations 4.4 to reference Gelman & Loken
- [x] Add Gelman & Loken (2013) to References
- [x] Fix variant count inconsistency (.typ: 25,850 → 26,225)
- [ ] Power analysis for MLH1 (referenced in abstract "N≥~120") — needs Methods Section 2.5 update if not present
- [ ] Update PRE_SUBMISSION_REVIEWER_DEFENSE.md (separate task, after submission decision)
- [ ] Update COVER_LETTER.txt + SUBMISSION_READY.txt if used (separate task)

## Related Documents

- `docs/CONSILIENCE_ASSESSMENT_2026-05-18.md` — original 7/7 claim source
- `docs/ADR-029_MLH1_mechanism_specificity.md` — cross-locus validation (now exploratory)
- `docs/ADR-030_TERT_sampling_bias_solved.md` — TERT hotspots
- Skeptic verdict (in conversation, 2026-05-25, agent a6c1fc0085e272c63)

## Open Questions

1. **MLH1 power analysis:** abstract claims "N≥~120 for 80% power" — needs Methods Section 2.5 update or supplementary calculation
2. **Title update:** keep "Systematic Falsification of 3D Chromatin-Based Variant Pathogenicity Prediction" or add "with HBB Pilot Validation"?
3. **Venue selection:** submit to Bioinformatics Advances after Ronin approval, or pursue arXiv endorsement first?

These are submission-time decisions, not blocking for current reframe commit.
