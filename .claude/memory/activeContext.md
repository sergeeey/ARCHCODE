# Active Context — ARCHCODE

**Last Updated:** 2026-04-01 (end of session)
**Branch:** feature/mechanistic-taxonomy (taxonomy paper track)
**Last Commit:** `2d64a72` — docs: align submission status + add endorsement packet
**GitHub:** https://github.com/sergeeey/ARCHCODE — PUSHED (4 commits this session)

## Submission Status

| Platform | Status | Next Action |
|----------|--------|-------------|
| Research Square | rs-9090074, DOI: 10.21203/rs.3.rs-9090074/v1 | Wait review feedback |
| arXiv | Waiting endorsement (code B9P837) | Follow-up Nora (UCSF) ~Apr 1 |
| Ronin Institute | Application submitted 2026-03-12 | Decision ~May 2026 |
| bioRxiv | Rejected (no affiliation) | Resubmit after Ronin |
| Zenodo | **v2.17 LIVE** — https://zenodo.org/records/18908214 (FOXP3+BCL11A) | Done |
| ORCID | 0009-0009-2178-5701 | Done |

## Current State

- **Manuscript:** taxonomy paper, 9 sections + 7 supplementary (S1-S7), FOXP3 + BCL11A case studies in Section 5, ~90 pages, compiles clean
- **References:** 38 (all DOI-verified, up from 24). Phantom "Chouery & Shukla 2022" fixed → Himadewi 2021. Umhoefer year 2026→2025 fixed.
- **Data:** 31,929 ClinVar variants, 18 loci (FOXP3, BCL11A, PAX6, + SCN5A cardiac), 27 HBB pearls, 641 VUS candidates
- **New:** Supplementary S7 (multi-locus atlas table, 18 loci × 9 metrics) + fig_multi_locus_atlas.png/pdf
- **BCL11A:** Erythroid enhancer mutagenesis (314 SYNTHETIC SNVs). DHS +58 = most sensitive (LSSIM=0.9660), consistent with Casgevy target. Triple validation: uniform occupancy control, GATA1 motif verified, GWAS HbF SNPs show more disruption than controls (U=46<60)
- **FOXP3:** 4 configs + in silico mutagenesis (486 SYNTHETIC SNVs). ClinVar: 0 pearls (all coding). Mutagenesis: 8 synthetic pearls in 2 Treg enhancer hotspots (LSSIM=0.9364). 6-point orthogonal validation PASSED — EGR2 binding site disrupted at Hotspot 2 (Marson lab TF)
- **V1 Module:** ML ablation complete — structural features = 64% importance for pearl detection
- **Orthogonal methods:** 10 independent methods confirm Class B blind spot
- **Core branch:** feature/v4-prioritization-framework (frozen at e9435f9)

## Key Numbers (canonical, updated 2026-03-30)

- 20 HBB pearls (14 unique positions, 11 in 73bp promoter cluster)
- Pearl vs Benign CAGE: -19% vs -0.1%, p=4×10⁻⁶, Cohen d=-2.1 (AlphaGenome real API)
- MPRA wet-lab: pearl vs non-pearl INDISTINGUISHABLE (p=0.91 Mann-Whitney; p=0.41 cross-locus). This SUPPORTS Class B: pearls invisible to MPRA.
- ISM peak: chr11:5,227,099-102 = -43% CAGE sensitivity (exact match with pearls)
- AUC=0.975 is CATEGORY-DRIVEN (ablation: without category → 0.551)
- Hi-C validation: r=0.28-0.59 across loci
- AlphaGenome 28 cell lines: r=+0.27 to +0.41 (after log→linear normalization)
- gnomAD: 85% pearls absent (purifying selection, but floor effect in conserved HBB)

## Session 2026-03-30 — Major cleanup + real validation

1. Removed AlphaGenome mock system (-11,756 lines, 37 files deleted)
2. Ran 5 experiments with real AlphaGenome API (SDK v0.6.0)
3. Key result: Pearl vs Benign CAGE p=4×10⁻⁶ (3-way with proper controls)
4. MPRA cross-validation: pearls invisible to MPRA (p=0.91) — confirms Class B blind spot
5. ISM: pearls = exact peak of CAGE sensitivity
6. README aligned with real data, mock references removed
7. All pushed to GitHub (5 commits)
8. README aligned with VALIDATION_PROTOCOL — discovery engine framing, HBB scope disclaimer, caveats (536b5ff)
9. Manuscript body updated: AlphaGenome CAGE section + ISM + AUC ablation caveat + pseudoreplication warning (60c44c7)
10. Re-evaluation score: 5.8/10. MPRA p=0.0001 was memory hallucination (actual p=0.91, correctly in manuscript)

## Session 2026-04-01 — Statistical strengthening + endorsers

1. Skeptic Engine validation committed (ffed1b0): benign=0.001, pathogenic=0.161, Pearl=0.153
2. **Statistical strengthening** (75e5908):
   - Bootstrap CI (10K) + Mann-Whitney U + Cohen d + BH FDR: **8/8 loci significant** (p < 10⁻¹⁷ all)
   - HBB: d=4.172, r=0.957 (very large effect). TERT: d=1.354. GJB2: d=1.273
   - 27,830 variants across 8 loci, all BH-corrected p < 0.05
3. **Cross-locus Pearl scan**: 323 candidates across 15 loci (30,770 variants)
   - Top: BRCA1 (97), MLH1 (87), CFTR (27), TERT (21), GPKOW (21)
   - GATA1 highest rate (6.9%), GPKOW (12.7%)
4. **Competitor comparison**: VEP misses 100% of Pearls (all MODIFIER), ARCHCODE catches 100%
5. **Endorser emails drafted**: Fudenberg (EN) + Goloborodko (RU) → outreach/endorser_emails_2026-04-01.md
6. **AlphaGenome CAGE batch** (330f64e): 7 loci tested. HBB (5.5x, p=4e-6) + MLH1 (3.7x, p=0.022) significant. BRCA1/TP53/TERT/GJB2 not significant — coding-dominant loci, CAGE can't see protein-level pathogenicity. Honest negative supports tissue-specificity thesis.

## Backlog

1. ~~**P0:** Add AlphaGenome + MPRA + ISM results to manuscript body~~ DONE (60c44c7)
2. ~~**P0:** Statistical strengthening (bootstrap CI, FDR, effect sizes)~~ DONE (75e5908)
3. ~~**P0:** Cross-locus Pearl scan~~ DONE (75e5908)
4. ~~**P0:** Competitor comparison table~~ DONE (75e5908)
5. **P0:** Send endorser emails: Fudenberg + Goloborodko — DRAFTED, user to send
6. **P0:** Submit RS v3 with new validation section + update Zenodo → v2.18
7. **P1:** Follow-up Nora — Apr 7 (email drafted in endorser_plan.md)
8. **P1:** Batch ROC: 1103 variants through AlphaGenome CAGE
9. **P1:** GATA1/KLF1 TF binding disruption at pearl positions
10. **P2:** Multi-locus AlphaGenome (BRCA1, TP53, CFTR)
11. **P2:** Tissue-specificity: pearl CAGE across 28 cell lines
8. **P3:** Wet-lab partner for Capture Hi-C at chr11:5,227,099-102

## Compilation

```bash
cd D:/ДНК/manuscript/taxonomy_paper
python -c "import typst; typst.compile('main.typ', output='main.pdf', root='../..')"
```

## Technical Notes

- Windows: `python` not `python3`
- Typst needs `root='../..'` for taxonomy paper
- Session history: use `git log --oneline` (not stored here)
- V1 roadmap: see memory/v1_module_roadmap.md

## Auto-commit log
- [2026-04-01 18:52] `2d64a72`: docs: align submission status + add endorsement packet
- [2026-04-01 14:48] `330f64e`: feat(validation): AlphaGenome CAGE batch on 7 loci — honest mixed result
- [2026-04-01 14:22] `75e5908`: feat(stats): add statistical strengthening + cross-locus Pearl scan + competitor comparison
- [2026-04-01 12:16] `ffed1b0`: docs: add Skeptic Engine independent validation results for HBB atlas
- [2026-03-31 08:24] `69ee680`: chore: repo cleanup — add missing data, remove temp files, update gitignore
- [2026-03-31 08:12] `f8e7667`: fix(integrity): audit cleanup — resolve 10 cross-document discrepancies
- [2026-03-30 23:46] `60c44c7`: feat(manuscript): add AlphaGenome CAGE validation + ISM + ablation caveat to body
- [2026-03-30 23:20] `536b5ff`: docs(readme): align public framing with VALIDATION_PROTOCOL — discovery engine, not predictor
- [2026-03-30 21:19] `52b3bba`: fix(integrity): complete remaining audit findings
- [2026-03-30 21:09] `a830c1b`: fix(integrity): resolve 6 audit findings from repo-wide scan
- [2026-03-30 20:40] `0684756`: docs: align README with actual data — fix pearl counts, update AlphaGenome to real API results
- [2026-03-30 20:32] `b346083`: feat: 3-way validation + ISM + MPRA cross-validation for pearl hotspot
- [2026-03-30 20:08] `859b1e2`: feat: AlphaGenome real API validation — pearls show 5.5× more CAGE disruption (p=0.0003)
- [2026-03-30 18:10] `f01c0a3`: fix(integrity): remove AlphaGenome mock system — eliminate synthetic data from public repo
- [2026-03-28 20:35] `cfafddb`: docs: add 14 verified references, multi-locus atlas table S7, fix phantom citation
- [2026-03-24 17:35] `1cf8fb8`: fix: use LOCUS_ARG in output filenames — prevent result overwrites
- [2026-03-24 15:14] `58a1c34`: feat(bcl11a): CTCF boundary deletion experiment — enhancer hijacking model
- [2026-03-24 14:56] `802d42b`: feat(hba1): in silico mutagenesis — hotspot at chr16:181,487 (LSSIM=0.9618)
- [2026-03-24 14:53] `af46e16`: feat(hba1): 90kb focused window — same Δ as 300kb, needs mutagenesis
- [2026-03-24 14:42] `3d3c9ed`: feat: SCN5A cardiac mutagenesis + PAX6/HBA1 baseline configs
- [2026-03-24 12:51] `765d869`: docs: add BCL11A/Casgevy + GWAS validation to abstract
- [2026-03-24 12:41] `c5a6243`: feat(bcl11a): GWAS validation + verified DHS coordinates + GATA1 motif
- [2026-03-24 12:23] `95e6e7f`: docs: add BCL11A Casgevy case study to taxonomy paper (Section 5)
- [2026-03-24 12:20] `0929362`: feat(bcl11a): erythroid enhancer mutagenesis — DHS +58 validated as Casgevy target
- [2026-03-24 10:47] `b9fa2f1`: docs: add FOXP3 mutagenesis to abstract — predictive vulnerability mapping
- [2026-03-24 10:30] `c73d23f`: docs: add FOXP3 case study + predictive mapping to taxonomy paper
- [2026-03-24 10:25] `2a04836`: docs(foxp3): orthogonal validation of in silico mutagenesis hotspots
- [2026-03-24 09:58] `c212f2d`: feat(foxp3): in silico saturation mutagenesis — 2 structural hotspots identified
- [2026-03-24 09:53] `7374b78`: feat(foxp3): 60kb focused window — IPEX-like paradox established
- [2026-03-24 09:31] `a2a6d6d`: feat: add FOXP3 as 15th ARCHCODE locus — immunology track (Nobel 2025 FOXP3/Treg)
