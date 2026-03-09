# [CHECK] Markers — Resolved

**Date:** 2026-03-09
**Files scanned:**
- `manuscript/taxonomy_paper/sections_1_3.md`
- `manuscript/taxonomy_paper/sections_4_6.md`
- `manuscript/taxonomy_paper/sections_7_9.md`
- `docs/taxonomy_paper_draft_abstract.md`

---

## Marker 1: Cross-reference to Section 3

**File:** `manuscript/taxonomy_paper/sections_4_6.md`, line 98
**Text:** `[CHECK: cross-reference to Section 3]`
**Context:** "...establishing that CTCF boundary deletions alone are sufficient for oncogene activation through 3D contact rewiring (see also the external casebook, Section 3.6 [CHECK: cross-reference to Section 3])."

**Resolution:** The cross-reference should point to **Section 3.2** (Class B: Architecture-Driven), not Section 3.6. Section 3.6 is "Decision Rules for Class Assignment" which does not cover the external casebook. The Hnisz et al. 2016 case validates Class B, so the correct parenthetical is:

> `(see also Section 3.2, Class B)`

**Source:** `manuscript/taxonomy_paper/sections_1_3.md` — Section 3.2 (lines 61-71) covers architecture-driven pathogenicity and references insulated neighborhood disruption directly.

---

## Marker 2: EXP-004 threshold robustness reference

**File:** `manuscript/taxonomy_paper/sections_4_6.md`, line 134
**Text:** `[CHECK: reference if completed]`
**Context:** "The EXP-004 threshold robustness analysis [CHECK: reference if completed] showed that the Q2b count is sensitive to the LSSIM threshold..."

**Resolution:** EXP-004 **is completed**. The bracket should be replaced with a concrete reference to the results.

Verified data from `analysis/threshold_robustness_summary.json`:
- Bootstrap CI at threshold 0.95: observed = 286 disrupted variants, 95% CI [271, 300]
- HBB stability zone: LSSIM 0.930–0.965 (width 0.035)
- BRCA1 stability zone: LSSIM 0.890–0.960 (width 0.070)
- TP53 stability zone: LSSIM 0.950–0.955 (width 0.005 — very narrow)
- Perturbation analysis: mean = 288.69, SD = 2.54, CI [284, 294]

**Corrected text:**

> "The EXP-004 threshold robustness analysis (bootstrap 95% CI: 271–300 disrupted variants at threshold 0.95; perturbation SD = 2.54) showed that..."

**Source:** `analysis/threshold_robustness_summary.json`

---

## Marker 3: Figure specification reference

**File:** `manuscript/taxonomy_paper/sections_4_6.md`, line 144
**Text:** `[CHECK: figure specification in docs/taxonomy_paper_outline.md]`
**Context:** "Figure 2 reference: schematic of ARCHCODE pipeline with per-class examples..."

**Resolution:** The figure specification **exists** in `docs/taxonomy_paper_outline.md`. Per the outline (line 96):

> Section 4 maps to **Figure 2** — "ARCHCODE examples by class"

The examples listed in the manuscript text (HBB Q2b for Class B, TERT Q2a for Class D, SCN5A null for Class E) are consistent with the outline's specification. The bracket can be removed and replaced with a note confirming alignment:

> *Figure 2: ARCHCODE pipeline schematic with per-class examples (HBB Q2b for Class B, TERT Q2a for Class D, SCN5A null for Class E). See Section 4 outline specification.*

**Source:** `docs/taxonomy_paper_outline.md`, line 96

---

## Marker 4: Abstract word count

**File:** `docs/taxonomy_paper_draft_abstract.md`, line 16
**Text:** `[CHECK: trim to ~250 if targeting journals with strict limits; current length appropriate for bioRxiv/Genome Research]`

**Resolution:** This is an **editorial note**, not a data verification issue. The abstract as written is ~310 words (per the note itself). Per the target journal plan in `docs/taxonomy_paper_outline.md` (lines 222-231):

- **bioRxiv (first target):** No strict word limit. ~310 words is appropriate.
- **Nature Genetics Perspective:** Abstract limit ~150 words — would require major trimming.
- **Genome Research / AJHG:** ~250 words typical — needs minor trimming.

**Action:** Keep at ~310 for bioRxiv preprint. Mark for trimming when targeting a specific journal. Replace bracket with:

> **Word count:** ~310 (appropriate for bioRxiv; trim to ~250 for Genome Research/AJHG, ~150 for Nature Genetics Perspective)

**Source:** `docs/taxonomy_paper_outline.md` (target journals section)

---

## Marker 5: Significance Statement word count

**File:** `docs/taxonomy_paper_draft_abstract.md`, line 24
**Text:** `[CHECK: trim to ~100 if journal requires]`

**Resolution:** Editorial note. The Significance Statement is ~120 words. Relevant limits:

- **PNAS** (which uses Significance Statements): 120 words max — current length is at the limit.
- **Most other journals** do not require a Significance Statement.

**Action:** Current length (~120 words) is within PNAS limits. No trimming needed unless a stricter journal is targeted. Replace bracket with:

> **Word count:** ~120 (within PNAS 120-word limit; no action needed)

**Source:** PNAS author guidelines [MEMORY — standard journal format knowledge]

---

## Marker 6: One-Paragraph Summary word count

**File:** `docs/taxonomy_paper_draft_abstract.md`, line 38
**Text:** `[CHECK: trim to ~80 if needed]`

**Resolution:** Editorial note. The One-Paragraph Summary is ~110 words. This section is labeled "for collaborators and talks" — it is not a journal submission element and has no formal word limit.

**Action:** No trimming needed. This is an internal communication tool. Replace bracket with:

> **Word count:** ~110 (internal use; no formal limit)

**Source:** Internal document purpose (line 34: "for collaborators and talks")

---

## Summary Table

| # | File | Line | Marker | Type | Resolved Value | Source |
|---|------|------|--------|------|----------------|--------|
| 1 | sections_4_6.md | 98 | Cross-reference to Section 3 | Cross-ref error | Change to "Section 3.2, Class B" | sections_1_3.md |
| 2 | sections_4_6.md | 134 | EXP-004 reference if completed | Data reference | EXP-004 completed: bootstrap CI [271, 300], perturbation SD = 2.54 | threshold_robustness_summary.json |
| 3 | sections_4_6.md | 144 | Figure specification | Figure cross-ref | Confirmed: Figure 2 = ARCHCODE examples by class (matches outline) | taxonomy_paper_outline.md |
| 4 | abstract.md | 16 | Abstract word count | Editorial | ~310 words; appropriate for bioRxiv, trim for journals | taxonomy_paper_outline.md |
| 5 | abstract.md | 24 | Significance word count | Editorial | ~120 words; within PNAS limit | Journal guidelines |
| 6 | abstract.md | 38 | Summary word count | Editorial | ~110 words; internal use, no limit | Document purpose |
