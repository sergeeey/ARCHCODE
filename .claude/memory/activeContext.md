# Active Context — ARCHCODE

**Last Updated:** 2026-03-02 (session 23: Publication figures + manuscript restructuring)
**Branch:** main
**Last Commit:** d85aed3 (docs(manuscript): position-only control section + Typst bioRxiv preprint)
**GitHub:** https://github.com/sergeeev/ARCHCODE
**bioRxiv ID:** BIORXIV/2026/708672 — awaiting screening
**Status:** 6 publication figures generated, integrated into Typst, abstract shortened. Ready for commit + push.

---

## Текущий статус проекта

**Фаза:** v2.11 — publication figures + manuscript polish

### Session 23: Publication Figures + Manuscript Restructuring

**Key changes:**

1. **6 publication-quality figures** generated via `scripts/generate_publication_figures.py`:
   - Fig 1: SSIM violin plot by category (184mm, seaborn)
   - Fig 2: ROC curves — categorical vs position-only + within-category inset
   - Fig 3: Pearl variant quadrant plot (VEP vs LSSIM, 4 quadrants)
   - Fig 4: Hi-C validation bar chart across 8 locus×cell-type combinations
   - Fig 5: Multi-locus summary table (7 loci, color-coded)
   - Fig 6: Contact map triptych (WT / Cd39 mutant / differential)

2. **Typst integration:** All 6 figures inserted in body_content.typ with figure captions and labels

3. **Formulas converted to Typst math:** Kramers, contact matrix, SSIM

4. **Text fixes:** Abstract ~250 words, "March 2026", no internal labels

5. **Final PDF:** 53 pages with 6 embedded figures

---

## Для следующей сессии

1. **Commit + push** session 23 changes
2. **bioRxiv v2 preprint** — resubmit with figures
3. Consider: Figure quality review (inset overlap in Fig 2)
4. Consider: Supplementary figures (per-locus SSIM distributions)
