# BCL11A 14-Day Sprint

**Canon Tier:** Technical Full-Scope  
**Release-facing:** No  
**Status:** Sprint Setup  
**Created:** 2026-04-04

## Sprint Goal

Complete the BCL11A / Casgevy bridge as an evidence-backed technical extension without changing
the public canonical layer.

This sprint does **not**:

- edit the public README framing
- promote BCL11A into the public canonical layer
- open FOXP3 or broad oncology as parallel pillars

This sprint **does**:

- create three missing tracked BCL11A artifacts
- update the BCL11A bridge only from tracked artifacts
- assemble one collaborator-ready external validation pack

## Deliverables

1. `results/bcl11a_uniform_occupancy_summary.json`
2. `results/bcl11a_gwas_hbf_overlay_summary.json`
3. `results/bcl11a_gata1_motif_summary.json`
4. Updated `docs/BCL11A_CASGEVY_BRIDGE.md`
5. `docs/BCL11A_external_validation_pack.md`

## Hard Rules

- Do not change `README.md`
- Do not change `submission_metadata.json`
- Do not change `manuscript/taxonomy_paper/abstract_content.typ`
- Do not promote BCL11A as a second validated public-canonical Class B locus
- Any new strong statement must be backed by a tracked artifact

## Day 1-2 Source-of-Truth Inventory

### Existing BCL11A configs

- `config/locus/bcl11a_300kb.json`
- `config/locus/bcl11a_erythroid_95kb.json`
- `config/locus/bcl11a_uniform_control.json`

### Existing BCL11A inputs

- `data/bcl11a_variants.csv`
- `data/clinvar_bcl11a_variants.csv`
- `data/bcl11a_mutagenesis_variants.csv`
- `data/bcl11a_gwas_variants.csv`
- `data/SYNTHETIC_bcl11a_erythroid_mutagenesis.csv`

### Existing BCL11A outputs

- `results/BCL11A_Unified_Atlas_300kb.csv`
- `results/BCL11A_Unified_Atlas_bcl11a_erythroid.csv`
- `results/BCL11A_Unified_Atlas_bcl11a_mutagenesis.csv`
- `results/UNIFIED_ATLAS_SUMMARY_BCL11A_300kb.json`
- `results/UNIFIED_ATLAS_SUMMARY_bcl11a_erythroid.json`
- `results/UNIFIED_ATLAS_SUMMARY_bcl11a_mutagenesis.json`
- `results/bcl11a_casgevy_bridge_summary.json`

### Existing BCL11A code/docs

- `scripts/bcl11a_in_silico_mutagenesis.py`
- `docs/BCL11A_CASGEVY_BRIDGE.md`
- `manuscript/taxonomy_paper/body_content.typ`

## Execution Checklist

### Phase A — Structured Artifacts

- [ ] `bcl11a_uniform_occupancy_summary.json`
- [ ] `bcl11a_gwas_hbf_overlay_summary.json`
- [ ] `bcl11a_gata1_motif_summary.json`

### Phase B — Bridge Update

- [ ] Update `docs/BCL11A_CASGEVY_BRIDGE.md` only from structured artifacts
- [ ] Keep explicit non-claims
- [ ] Keep promoter caveat

### Phase C — External Pack

- [ ] Create `docs/BCL11A_external_validation_pack.md`
- [ ] State what is shown vs not shown
- [ ] Define minimum wet-lab ask
- [ ] Explain why BCL11A is next

### Phase D — Verification

- [ ] `python scripts/validate_project_canon.py`
- [ ] `python scripts/verify_manuscript.py`
- [ ] `python check_redflags.py`
- [ ] `python scripts/secret_scan.py`
- [ ] `npm test`
- [ ] `npm run build`

## Definition of Done

- Three new BCL11A tracked artifacts exist and are valid JSON
- `docs/BCL11A_CASGEVY_BRIDGE.md` can be derived from those artifacts plus the existing bridge
  summary
- Public canonical surfaces remain unchanged
- The validator still passes
- One collaborator-facing validation pack exists

## Current Positioning

BCL11A is a **technical bridge / translational showcase**, not a new public pillar.

Promotion is allowed only after a non-circular evidence pack exists.
