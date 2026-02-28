# ARCHCODE: Physics-Based 3D Chromatin Simulator for Variant Pathogenicity

![bioRxiv pending](https://img.shields.io/badge/bioRxiv-pending-yellow)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

**ARCHCODE** (Architecture-Constrained Decoder) — an analytical mean-field loop extrusion
simulator that predicts structural pathogenicity of genomic variants by comparing wild-type
and mutant 3D chromatin contact maps via SSIM.

## Quick Start

```bash
npm install
npm run build
npx tsx scripts/generate-real-atlas.ts   # 353 variants, 20 pearls
```

## Key Results

Analysis of **353 real ClinVar HBB variants** (β-thalassemia) using ARCHCODE + Ensembl VEP v113:

- **161/353 (45.6%)** classified as structurally pathogenic by ARCHCODE
- **20 "pearl" variants** discovered (VEP < 0.30, SSIM < 0.95): 15 promoter, 3 missense, 1 splice_acceptor, 1 frameshift
- **130/353 (36.8%)** discordant between ARCHCODE and VEP — complementary, not competing tools
- Loss-of-function classes: 100% pathogenic (nonsense, frameshift); synonymous: 0% — biologically expected

### Figure 2: ARCHCODE SSIM vs VEP Score

![SSIM vs VEP scatter plot](results/figures/fig_ssim_vs_vep.png)

_353 real ClinVar HBB variants. Red = 20 pearl variants (VEP-blind, ARCHCODE-detected). Pearl zone: VEP < 0.30 AND SSIM < 0.95._

### Table 2: Top 5 Pearl Variants (of 20 total)

| ClinVar_ID   | HGVS_c              | Category        | ClinVar_Significance    | SSIM   | VEP  | VEP_Consequence         | Mechanism                         |
| ------------ | ------------------- | --------------- | ----------------------- | ------ | ---- | ----------------------- | --------------------------------- |
| VCV000869358 | c.50dup             | frameshift      | Pathogenic              | 0.8915 | 0.15 | synonymous_variant      | LoF, VEP misannotated             |
| VCV002024192 | c.93-33_96delins... | splice_acceptor | Likely pathogenic       | 0.9004 | 0.20 | coding_sequence_variant | Complex indel, VEP underscored    |
| VCV000015471 | c.-78A>G            | promoter        | Pathogenic/Likely path. | 0.9276 | 0.20 | 5_prime_UTR_variant     | Promoter–enhancer loop disruption |
| VCV000015470 | c.-78A>C            | promoter        | Pathogenic              | 0.9276 | 0.20 | 5_prime_UTR_variant     | Promoter–enhancer loop disruption |
| VCV000036284 | c.-136C>T           | promoter        | Pathogenic/Likely path. | 0.9277 | 0.20 | 5_prime_UTR_variant     | Promoter–enhancer loop disruption |

_Sorted by SSIM ascending (strongest structural disruption first). Full list: [Supplementary Table S1](manuscript/TABLE_S1_PEARLS.md)._

## Limitations

- **VEP proxy**: SpliceAI API was unreachable; Ensembl VEP used instead (different scope)
- **Mean-field approximation**: analytical model, not full stochastic Monte Carlo
- **Computational only**: Hi-C validation r = 0.16 (not significant); experimental validation required
- **Parameters manually calibrated**: α=0.92, γ=0.80 from literature ranges, not fitted to data
- **No missense sensitivity**: ARCHCODE models chromatin topology, not protein folding

## Project Structure

```
├── manuscript/                    # Publication manuscript (all sections)
│   ├── FULL_MANUSCRIPT.md         # Complete integrated manuscript
│   ├── TABLE_2_PEARLS_TOP5.md     # Top 5 pearl variants
│   └── TABLE_S1_PEARLS.md        # All 20 pearl variants
├── results/
│   ├── HBB_Clinical_Atlas_REAL.csv # 353 real variants (primary dataset)
│   ├── REAL_ATLAS_SUMMARY.json    # Summary statistics
│   └── figures/                   # Publication figures
├── scripts/
│   ├── generate-real-atlas.ts     # Atlas generator (analytical engine)
│   ├── run_vep_predictions.py     # Ensembl VEP batch predictions
│   ├── download_clinvar_hbb.ts    # ClinVar data acquisition
│   ├── plot_ssim_vs_vep.py        # Figure 2 generator
│   └── check_consistency_hbb_real.py  # Data/manuscript consistency check
├── src/                           # Core TypeScript engine + React UI
│   ├── engines/                   # Physics engines (loop extrusion)
│   ├── domain/                    # Biophysical constants and models
│   └── components/                # 3D visualization (Three.js)
└── config/                        # Simulation parameters
```

## Citation

```bibtex
@article{boyko2026archcode,
  title   = {ARCHCODE: 3D Chromatin Loop Extrusion Simulation Reveals Structural
             Pathogenicity Invisible to Sequence-Based Predictors in β-Globin Variants},
  author  = {Boyko, Sergey V.},
  year    = {2026},
  note    = {bioRxiv preprint (pending)},
  url     = {https://github.com/sergeeey/ARCHCODE}
}
```

## License

MIT License — See [LICENSE](./LICENSE)

---

**Version**: 2.0.0
**Last Updated**: 2026-02-28
**Status**: Pre-publication (consistency pass complete, experimental validation pending)
**Contact**: sergeikuch80@gmail.com
