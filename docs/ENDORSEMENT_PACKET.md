# ARCHCODE — Endorsement Packet

**For arXiv q-bio.GN endorsers and potential collaborators**

---

## What ARCHCODE does

ARCHCODE is a physics-based 3D chromatin loop extrusion simulator that identifies ClinVar variants disrupting chromatin architecture — variants invisible to sequence-based tools (VEP, SpliceAI, CADD).

It is a **structural mechanism discovery engine**, not a clinical pathogenicity predictor.

## Three key results

1. **20 "Pearl" variants in HBB** — disrupt loop structure but classified benign/VUS by all standard tools. AlphaGenome CAGE validation: p = 4 x 10^-6, Cohen d = -2.1.

2. **Cross-locus signal in 8/8 loci** — statistically significant after Benjamini-Hochberg FDR correction (27,830 variants). Largest effect: HBB d = 4.17, TERT d = 1.35, GJB2 d = 1.27.

3. **323 Pearl candidates across 15 loci** (30,770 variants) — benign-classified variants with structural disruption at the level of known pathogenic variants.

## Three key limitations

1. **No wet-lab validation yet.** Pearl variants are computational predictions, not confirmed pathogenic. CRISPR/Hi-C on 2-3 candidates would be decisive.

2. **Deep analysis concentrated on HBB.** Other loci have atlas-level data but not the same depth of orthogonal validation.

3. **Simulator uses manually calibrated parameters** (not fitted to experimental data). Mean-field approximation of loop extrusion.

## Links

| Resource | Link |
|----------|------|
| Preprint (Research Square) | [DOI: 10.21203/rs.3.rs-9090074/v1](https://doi.org/10.21203/rs.3.rs-9090074/v1) |
| Code + data (GitHub) | [github.com/sergeeey/ARCHCODE](https://github.com/sergeeey/ARCHCODE) |
| Data archive (Zenodo) | [DOI: 10.5281/zenodo.18908214](https://zenodo.org/records/18908214) |
| ORCID | [0009-0009-2178-5701](https://orcid.org/0009-0009-2178-5701) |

## arXiv endorsement

- **Category:** q-bio.GN (Genomics)
- **Endorsement code:** B9P837
- **Endorsing requires:** one click at [arxiv.org/auth/endorse](https://arxiv.org/auth/endorse), enter code B9P837

## About the author

Sergey V. Boyko, independent researcher, Almaty, Kazakhstan.
Ronin Institute affiliation pending (application submitted March 2026).

---

*ARCHCODE identifies which variants to investigate first — not whether they are pathogenic. The project prioritizes transparency over perfection.*
