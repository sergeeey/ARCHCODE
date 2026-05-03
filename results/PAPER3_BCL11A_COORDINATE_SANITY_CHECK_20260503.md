# Paper 3 BCL11A Coordinate / Query Sanity Check

Date: 2026-05-03

This note closes the current BCL11A sanity-check gate for Paper 3.
It is a blocker note, not a claim of locus validation.

## Inputs

- Primary BCL11A pilot:
  - `results/paper3_bcl11a_primary_regulatory_not_observed_20260503.csv`
  - `results/paper3_bcl11a_primary_regulatory_not_observed_20260503.json`
- Position-matched controls:
  - `results/paper3_bcl11a_position_controls_not_observed_20260503.csv`
  - `results/paper3_bcl11a_position_controls_not_observed_20260503.json`
- Source audit:
  - `results/PAPER3_BCL11A_SOURCE_AUDIT_20260503.md`
  - `results/PAPER3_BCL11A_BASELINE_AUDIT_20260503.md`

## Primary pilot rows

- Retained primary rows: 3
- All 3 returned `gnomAD_v4_not_observed_graphql`
- Positions:
  - `60553215` (`VCV000985925`, `VCV000973119`)
  - `60553283` (`VCV001698614`)

## Position-matched controls

- Position-matched controls: 6
- All 6 returned `gnomAD_v4_not_observed_graphql`
- Positions:
  - `60553212`
  - `60553236`
  - `60553253`
  - `60553261`
  - `60553268`
  - `60553271`

## Sanity-check interpretation

- The primary BCL11A pilot does not separate cleanly from the position-matched controls.
- The shared `not_observed` pattern means the current pilot cannot distinguish LSSIM signal from position/query behavior.
- This is consistent with the baseline audit: BCL11A remains a useful cautionary pilot, not a second positive regulatory locus.

## Decision

- Do not promote BCL11A to manuscript-grade evidence.
- Do not use the current BCL11A pilot as proof of locus generalization.
- Keep Paper 3 in feasibility mode until a second locus survives a position-matched control check.
