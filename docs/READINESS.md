# Readiness Assessment (ARCHCODE)

**Canon Tier:** Public Canonical  
**Release-facing:** Yes  
**Last Updated:** 2026-04-04  
**Public Research Release:** v2.17  
**Internal Package Version:** 2.0.0

## Goal

Provide an evidence-backed release-readiness score for the current public ARCHCODE surface.

This score is about **release confidence**, not proof that the scientific interpretation is complete.

## Scoring Rubric

Each dimension is scored `0-10`, then averaged.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Code and engine | 8.0 | Core engine is tested and stable; unit and regression tests are green. |
| Data and provenance | 7.0 | Public core data are real and provenance-labeled, but technical/full-scope assets remain broader than the public layer. |
| Scientific integrity | 9.0 | Manuscript verification, results contracts, red-flag scans, and explicit caveats are in place. |
| Evidence strength | 6.0 | HBB evidence is strong; broader biological generalization remains exploratory. |
| Reproducibility | 7.0 | Build/test/integrity gates exist and tracked artifacts are reproducible. |
| Manuscript and public coherence | 5.0 | Canonical Core work is reducing drift, but technical/full-scope surfaces still need discipline. |
| Multi-locus maturity | 3.0 | HBB is the only confirmed public core case; non-HBB findings are not promoted as validated. |
| Publication path | 5.0 | Research Square is live; arXiv remains pending endorsement and bioRxiv was rejected. |
| Infrastructure and gating | 8.0 | Security, publication-integrity, and results-contract gates are implemented. |
| Platform potential | 6.0 | Expansion paths exist, but should follow after Canonical Core stabilization. |

**Current Score:** **6.4 / 10**

## Evidence Links

- `PROJECT_CANON.md`
- `docs/VALIDATION.md`
- `docs/FAILURE_MODES.md`
- `docs/PR_GATE.md`
- `docs/RESULTS_CONTRACT.md`
- `results/publication_claim_matrix_2026-03-30.json`
- `.github/workflows/publication-integrity.yml`
- `.github/workflows/security-gates.yml`

## Current Caveats

- Public canonical claims are intentionally narrower than the full technical repo scope.
- HBB is the confirmed public core case; non-HBB Class B findings remain exploratory.
- No wet-lab confirmation has yet converted the computational HBB structural class into experimentally proven pathogenicity.
- Broader technical layers remain useful, but they are not the default release identity.

## Verdict

`WORKS WITH RISKS`

ARCHCODE is credible as a release-facing discovery engine with strong integrity infrastructure and a defendable HBB core. It is not yet a mature cross-locus validation platform or a clinical predictor.
