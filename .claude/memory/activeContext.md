# Active Context — ARCHCODE

**Last Updated:** 2026-03-24
**Branch:** feature/mechanistic-taxonomy (taxonomy paper track)
**Last Commit:** `c212f2d` — FOXP3 in silico mutagenesis, 2 structural hotspots
**GitHub:** https://github.com/sergeeey/ARCHCODE — NOT pushed yet

## Submission Status

| Platform | Status | Next Action |
|----------|--------|-------------|
| Research Square | rs-9090074, DOI: 10.21203/rs.3.rs-9090074/v1 | Wait review feedback |
| arXiv | Waiting endorsement (code B9P837) | Follow-up Nora (UCSF) ~Apr 1 |
| Ronin Institute | Application submitted 2026-03-12 | Decision ~May 2026 |
| bioRxiv | Rejected (no affiliation) | Resubmit after Ronin |
| Zenodo | v2.16 DOI locked | Done |
| ORCID | 0009-0009-2178-5701 | Done |

## Current State

- **Manuscript:** taxonomy paper, 9 sections + 6 supplementary sections (S1-S6), compiles clean
- **Data:** 30,554 ClinVar variants, 15 loci (incl. FOXP3), 27 HBB pearls, 641 VUS candidates
- **FOXP3:** 4 configs + in silico mutagenesis (486 SYNTHETIC SNVs). ClinVar: 0 pearls (all coding). Mutagenesis: 8 synthetic pearls in 2 Treg enhancer hotspots (LSSIM=0.9364 at chrX:49276056). ARCHCODE → predictive mode
- **V1 Module:** ML ablation complete — structural features = 64% importance for pearl detection
- **Orthogonal methods:** 10 independent methods confirm Class B blind spot
- **Core branch:** feature/v4-prioritization-framework (frozen at e9435f9)

## Key Numbers (canonical)

- 27 HBB pearls, robust across thresholds 0.88-0.95
- VEP catches 0/27 pearls, SIFT 0/27, CADD 15/27 (56%)
- Structural features: 64% importance (HBB), 0.6% (BRCA1) — tissue-specificity confirmed
- Hi-C validation: r=0.28-0.59 across loci
- Cross-species: r=0.82 (human vs mouse LSSIM)

## Backlog

1. **P0:** Wait RS/Ronin/Nora — nothing to do until responses
2. **P1:** Add FOXP3 mutagenesis results to taxonomy paper (Discussion + new figure)
3. **P1:** V1 cross-locus transfer (HBA1, BCL11A) — after publication
4. **P2:** VUS reclassification pipeline (641 candidates) — needs clinical partner
5. **P2:** CRISPR collaboration — after preprint is live
6. **P3:** MYBPC3 cardiac, gene therapy, CRISPR off-target — post-ARCHCODE

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
- [2026-03-24 09:58] `c212f2d`: feat(foxp3): in silico saturation mutagenesis — 2 structural hotspots identified
- [2026-03-24 09:53] `7374b78`: feat(foxp3): 60kb focused window — IPEX-like paradox established
- [2026-03-24 09:31] `a2a6d6d`: feat: add FOXP3 as 15th ARCHCODE locus — immunology track (Nobel 2025 FOXP3/Treg)
