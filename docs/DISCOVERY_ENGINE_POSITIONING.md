# Discovery Engine Positioning

**Canon Tier:** Technical Full-Scope  
**Release-facing:** No  
**Last Updated:** 2026-04-04  
**Public Research Release:** v2.17

## Core Positioning

ARCHCODE should be presented as a **discovery engine for structural mechanism discovery**, not as a general-purpose pathogenicity predictor.

This document is the current technical positioning memo. The default public release identity is defined in [PROJECT_CANON.md](D:/ДНК/PROJECT_CANON.md).

## Layer Guidance

### Public Canonical

Use when writing:
- README
- submission metadata
- readiness/release dashboard
- endorsement packet
- release-facing abstracts

Default framing:
- discovery engine
- HBB-confirmed core
- non-HBB exploratory

Default public numbers:
- `30,318` variants
- `9` primary loci
- `25` high-confidence HBB Class B variants
- `29` exploratory non-HBB candidates

### Technical Full-Scope

Use when writing:
- technical notes
- broader manuscript body text
- exploratory result summaries
- VUS/full-scope analyses
- FOXP3/BCL11A extension documents

Allowed with scope/provenance labels:
- `32,201`
- `30,952`
- `63,153`
- `641 pearl-like`
- `27 pearls`
- `54 Class B`

## Language Rules

Prefer:
- `discovery engine`
- `structural mechanism discovery`
- `structural prioritization`
- `confirmed HBB core`
- `exploratory non-HBB candidates`

Avoid on public surfaces:
- `variant pathogenicity prediction`
- `better predictor`
- `five tools fail` when the broader technical evidence is more nuanced
- broad-scope counts as the default project identity

## Count Semantics

- `25 high-confidence HBB Class B variants` = current public canonical core
- `27 pearls` = broader technical HBB definition
- `54 Class B` = `25` confirmed HBB core + `29` exploratory non-HBB candidates
- `32,201 / 30,952 / 63,153 / 641 pearl-like` = technical full-scope only unless explicitly promoted in a future release

## Decision Rule

When a public and technical interpretation diverge, choose the **narrower defensible public claim** and route the broader statement into the technical full-scope layer.
