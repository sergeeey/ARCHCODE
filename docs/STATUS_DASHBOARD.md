---
**UPDATED:** 2026-05-18 — Consilience assessment complete, bioRxiv submission ready
**See:** docs/SUBMISSION_STATUS_2026-05-18.md for current submission details
---

# ARCHCODE Status Dashboard

**Canon Tier:** Public Canonical — Reframed
**Release-facing:** Yes
**Last Updated:** 2026-05-03

## Current Release Identity

| Field | Current |
|-------|---------|
| Public research release | `v2.17` (public canonical) |
| Internal package version | `2.0.0` |
| Positioning | **Analytical structural perturbation framework + falsification-first validation suite** |
| Scope | `30,318` ClinVar variants across `9` loci; `30` validation tests |
| Primary contribution | Validation suite (6 modules, 30 tests, <30s runtime) |
| Surviving signal | TP53 splice_region: AUC=0.69, d=-0.78, FDR-corrected |

## Validation Suite Results

| Test | PASS | WARNING | FAIL | SKIPPED |
|------|------|---------|------|---------|
| CTCF Shuffle | 8 | 0 | 1 (HBB) | 0 |
| Simple Baseline | 0 | 7 | 1 (GJB2) | 1 (HBB) |
| Within-Category | 1 (TP53) | 0 | 7 | 1 (HBB) |
| Ablation | — | 1 (TP53) | — | — |
| Cross-Locus Transfer | 0 | 0 | 1 | — |
| Robustness | 0 | 1 | 0 | — |
| **Total** | **9 (30%)** | **9 (30%)** | **12 (40%)** | **2** |

## Key Findings (Reframed)

| Claim | Old Status | New Status |
|-------|-----------|------------|
| AUC = 0.977 on HBB = pathogenicity discovery | ~~Confirmed~~ | **Category-driven** (position-only AUC = 0.551) |
| 25/27 pearl variants = hidden pathogenicity | ~~Confirmed~~ | **Candidates for experimental prioritization** (not independent discovery) |
| Cross-locus generalization | ~~Supported~~ | **Transfer fails** (0% sensitivity on 8/9 loci with HBB threshold) |
| Simple baselines beaten | ~~Claimed~~ | **Baselines match/beat SSIM on 8/9 loci** |
| Within-category signal | ~~Null in 2/3, power effect in 2~~ | **Null in 7/8, TP53 exception confirmed** |
| Hi-C correlation r = 0.28–0.59 | Confirmed | **Confirmed** — architecture-driven, not kinetics-driven |
| Validation suite | Did not exist | **Primary contribution** — reusable benchmark |

## Release Gates

| Gate | Status |
|------|--------|
| Project canon validator | Green (reframed 2026-04-06) |
| Results contract validator | Green |
| Manuscript verification | **Updated** — Abstract, Discussion, Limitations, README reframed |
| Red-flag scan | Green |
| Secret scan | Green |
| Unit tests | `44/44` passing |

## Publication State (Updated 2026-05-21)

| Surface | Status | Details |
|---------|--------|---------|
| **Research Square** | ✅ **LIVE** | DOI: 10.21203/rs.3.rs-9090074/v1 (May 18, 2026) — **PRIMARY PREPRINT** |
| **bioRxiv** | ❌ **REJECTED** | May 21 — Institutional affiliation requirement (Ronin Institute not recognized) — **Appeal pending** |
| **arXiv** | 🔴 **BLOCKED** | 4/4 endorsers failed (Fudenberg bounced, Paulsen refused, Polovnikov/Imakaev can't), 3/3 MIT ghosted >50 days |
| **Next** | Appeal bioRxiv (P0) → if rejected, use Research Square primary + prepare journal submission (Bioinformatics Advances) |

**Current strategy:** Research Square DOI active and citable. bioRxiv appeal in progress (3-7 days response). arXiv endorsement paused (low probability).

## Active Caveats

- ARCHCODE AUC is category-driven, not within-category prediction
- Simple baselines (distance + severity) match or beat SSIM on 8/9 loci
- Cross-locus threshold transfer fails entirely
- Pearl variants are computational hypotheses only — no experimental validation
- TP53 splice_region (AUC=0.69) is the only surviving within-category signal
- Validation suite is the primary scientific contribution
- No clinical utility demonstrated

## Canon Routing

| Layer | Role |
|-------|------|
| Public Canonical | Reframed: analytical framework + validation suite |
| Technical Full-Scope | Exploratory loci, VUS work, legacy analyses |
| Legacy | Historical v2.17 materials (old framing preserved for provenance) |

## Immediate Next Milestone

1. Keep Research Square and local public surfaces aligned to v2.17 canonical framing
2. Update arXiv submission only if version labels and public narrative are reconciled
3. Publish validation suite as standalone tool
