# ARCHCODE Canonical Core

Canonical routing and claim policy for ARCHCODE release-facing material.

## Positioning

ARCHCODE is a **physics-based 3D chromatin loop extrusion simulator for structural mechanism discovery**.

It is:
- a discovery engine
- a structural prioritization framework
- a hypothesis-generation system for follow-up validation

It is not:
- a clinical pathogenicity predictor
- a cross-locus validated replacement for VEP, CADD, or AlphaGenome
- experimental proof of pathogenicity

## Version Mapping

- **Public research release:** `v2.17`
- **Internal package/app version:** `package.json` `2.0.0`

Public release surfaces must use `v2.17` when a research-release version is shown. `2.0.0` is allowed only where implementation/package versioning is being discussed explicitly.

## Layer Model

### Public Canonical Layer

Audience:
- reviewers
- landing-page readers
- endorsers
- collaborators evaluating the current release

Purpose:
- the narrowest, most defensible current ARCHCODE narrative

Allowed default framing:
- discovery engine
- HBB-confirmed core
- non-HBB findings labeled exploratory

Primary public claims:
1. `30,318` ClinVar variants across `9` primary loci define the current public atlas.
2. `25` high-confidence HBB Class B variants form the current public core result.
3. `29` candidate non-HBB Class B variants are exploratory and require tissue-matched follow-up before promotion to confirmed findings.

Active surfaces:
- `README.md`
- `submission_metadata.json`
- `docs/ENDORSEMENT_PACKET.md`
- `docs/READINESS.md`
- `docs/STATUS_DASHBOARD.md`
- `manuscript/taxonomy_paper/abstract_content.typ`

### Technical Full-Scope Layer

Audience:
- technical readers
- internal collaborators
- research collaborators working beyond the public landing narrative

Purpose:
- preserve broader current repo scope without overselling it as the default release identity

Allowed content:
- broader locus counts
- VUS and pearl-like analyses
- exploratory competitor comparisons
- FOXP3 and BCL11A extensions
- broader manuscript/body discussions

Rules:
- must be explicitly labeled `TECHNICAL`, `SUPPLEMENTAL`, or `EXPLORATORY`
- must not read like the default project identity
- broader numbers must be accompanied by scope and provenance

Active surfaces:
- `docs/DISCOVERY_ENGINE_POSITIONING.md`
- `docs/BCL11A_CASGEVY_BRIDGE.md`
- `docs/VALIDATION.md`
- `docs/VALIDATION_PROTOCOL.md`
- `docs/FAILURE_MODES.md`
- `docs/PR_GATE.md`
- `manuscript/taxonomy_paper/body_content.typ`
- `results/bcl11a_casgevy_bridge_summary.json`
- `results/competitor_comparison.json`
- `results/statistical_strengthening.json`
- `results/cross_locus_pearl_scan.json`
- `results/alphagenome_batch_cage_9loci.json`

### Legacy Layer

Audience:
- provenance and history only

Purpose:
- preserve superseded public snapshots and historical artifacts

Rule:
- legacy files must live under `archive/legacy/` and be treated as non-current by default

## Context Rules

- `54 Class B` is allowed on public surfaces only when decomposed into `25 confirmed HBB + 29 exploratory non-HBB candidates`.
- `27 pearls` is allowed on public surfaces only when explicitly labeled as a broader technical HBB definition.
- `32,201`, `30,952`, `63,153`, and `641 pearl-like` are not part of the default public identity. They belong in technical full-scope or legacy material only.
- `variant pathogenicity prediction` is not valid public positioning for the current release.

## Validation and Evidence Routing

Current release-facing evidence should resolve through:
- `docs/VALIDATION.md`
- `docs/READINESS.md`
- `docs/FAILURE_MODES.md`
- `docs/RESULTS_CONTRACT.md`
- `results/publication_claim_matrix_2026-03-30.json`
- `results/publication_canonical_index_2026-03-30.json`

Files not listed above as active public or active technical surfaces are non-canonical by default and must not be used as release truth without explicit promotion.
