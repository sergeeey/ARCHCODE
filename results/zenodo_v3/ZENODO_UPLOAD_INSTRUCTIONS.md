# Zenodo v3 Upload Instructions

**Record:** https://doi.org/10.5281/zenodo.18867448
**Action:** Create new version (v3) of existing record
**Files:** in `results/zenodo_v3/`

---

## Step-by-step (Zenodo web UI)

### 1. Open the record
Go to https://doi.org/10.5281/zenodo.18867448 → click **Edit** (top right) → **New version**.

### 2. Upload files
Remove the old PDF/HTML and upload:
- `ARCHCODE_v3_corrected.html` — the corrected preprint (primary file)
- `CORRECTION_NOTE.md` — full correction details (supplementary)

### 3. Update metadata

**Title (change to):**
```
ARCHCODE: A Falsification-First Framework for Evaluating 3D Chromatin Structural Scores in Variant Interpretation — A β-Thalassemia Case Study (v3 Corrected)
```

**Description (replace with):**
```
VERSION 3 CORRECTION (2026-06-05): This version corrects errors in v1–v2 (deposited Feb–Mar 2026).

CORRECTIONS:
1. Phantom reference removed: "Sabaté et al., Nature Genetics 2025" (DOI 404) → corrected to Sabaté et al. bioRxiv 2024 (DOI: 10.1101/2024.08.09.605990)
2. Clinical reclassification claim removed: "we propose reclassifying 3 HBB variants from VUS to Likely Pathogenic" had no ACMG PS3 evidence
3. AUC 0.977 overclaim corrected: a matched-control audit showed this is a category-distribution artifact (within-category AUC ≈ 0.52, chance level)
4. AlphaGenome exclusion: all AlphaGenome claims used mock/synthetic data and are excluded

CURRENT FRAMING: ARCHCODE does not demonstrate independent 3D chromatin pathogenicity signal in the five tested configurations. The contribution is a systematic falsification framework for auditing chromatin-based variant scores.

Code and audit artifacts: https://github.com/sergeeey/ARCHCODE
```

**Keywords (update to):**
```
β-thalassemia, HBB, chromatin loops, loop extrusion, cohesin, SSIM, falsification framework,
matched controls, negative result, variant interpretation, mean-field simulation, 3D genome
```

**Version:** `v3-corrected`

### 4. Add note to v1/v2 (if Zenodo allows editing old version description)
If possible, add to the older version's description:
```
⚠ SUPERSEDED: A corrected version (v3) is available at [new DOI]. 
This version contains a phantom reference and an unsupported clinical reclassification claim. 
Please use v3.
```

### 5. Publish
Click **Publish**. Zenodo will assign a new version DOI while keeping the parent DOI (10.5281/zenodo.18867448) pointing to the latest version.

### 6. Update repo
After publishing, update `submission_metadata.json`:
- `data_availability.zenodo_v3`: set to new version DOI
- Remove `data_availability.zenodo_v2.9` key

---

## Files checklist

| File | Status | Action |
|---|---|---|
| `ARCHCODE_v3_corrected.html` | ✅ ready | Upload as primary file |
| `CORRECTION_NOTE.md` | ✅ ready | Upload as supplementary |
| Old `ARCHCODE_Preprint_EN.pdf` (v1/v2) | ❌ contains phantom ref + clinical claim | Remove from record |

---

## What to fix before re-submitting to bioRxiv (separate from Zenodo)

- Author name: canonicalize `Boyko` vs `Boiko` everywhere
- ORCID: register and fill in (currently empty)
- Article type: set explicitly for target venue
- AI-use disclosure: add to Methods section
- arXiv badge in README: remove (no arXiv record exists)
