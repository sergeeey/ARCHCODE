# ARCHCODE Status Dashboard

**Canon Tier:** Public Canonical  
**Release-facing:** Yes  
**Last Updated:** 2026-04-04

## Current Release Identity

| Field | Current |
|-------|---------|
| Public research release | `v2.17` |
| Internal package version | `2.0.0` |
| Positioning | Discovery engine for structural mechanism discovery |
| Public core scope | `30,318` ClinVar variants across `9` primary loci |
| Confirmed public core | `25` high-confidence HBB Class B variants |
| Exploratory extension | `29` candidate non-HBB Class B variants |

## Release Gates

| Gate | Status |
|------|--------|
| Project canon validator | Green on 2026-04-04 current working tree |
| Results contract validator | Green on 2026-04-04 current working tree |
| Manuscript verification | Green on 2026-04-04 current working tree |
| Red-flag scan | Green on 2026-04-04 current working tree |
| Secret scan | Green on 2026-04-04 current working tree |
| Unit tests | `44/44` passing on 2026-04-04 current working tree |

## Publication State

| Surface | Status |
|---------|--------|
| Research Square | Live — DOI `10.21203/rs.3.rs-9090074/v1` |
| arXiv | Pending endorsement |
| bioRxiv | Rejected |

## Canon Routing

| Layer | Role |
|-------|------|
| Public Canonical | Default release identity for reviewers, README, metadata, and short collateral |
| Technical Full-Scope | Broader repo-backed analyses, exploratory loci, VUS work, and supplementary narratives |
| Legacy | Historical snapshots and superseded public surfaces under `archive/legacy/` |

## Active Caveats

- HBB remains the only confirmed public core case.
- Non-HBB findings are retained, but only as exploratory/technical material.
- AlphaGenome and Hi-C support strengthen the HBB hotspot narrative, but do not replace wet-lab confirmation.
- Public-facing materials must not use wider historical counts as the default project identity.

## Immediate Next Milestone

Use the stabilized Canonical Core as the release-facing baseline, then add new scope only through explicitly labeled technical or exploratory surfaces.
