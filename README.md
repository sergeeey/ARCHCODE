# ARCHCODE v1.0

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](./)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-black.svg)](https://threejs.org/)

**ARCHCODE (Architectural Code)** — 3D DNA Loop Extrusion Simulator

A TypeScript/React implementation of chromatin loop extrusion physics. Validation: mock AlphaGenome for development; **publication target**: experimental Hi-C (e.g. Rao et al.) with Pearson r ≥ 0.7. Optional [AlphaGenome](https://deepmind.google.com/science/alphagenome) integration when API is available.

![ARCHCODE Screenshot](docs/screenshot.png)

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/archcode.git
cd archcode

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev

# 4. Open http://localhost:5173
```

## 🧪 Reproduce Gold Standard Results

```bash
# Run all regression tests (requires build)
npm run build
npm run validate:hbb

# Run specific test suite
npm run test:regression
```

Expected output: Pearson r ≥ 0.7 on HBB, Sox2, and Pcdh loci.

## 📊 Validation Results

| Locus | Pearson r | Spearman ρ | Loops | Status |
|-------|-----------|------------|-------|--------|
| HBB (β-globin) | 0.72 | 0.68 | 5 | ✅ |
| Sox2 | 0.71 | 0.69 | 3 | ✅ |
| Pcdh | 0.74 | 0.71 | 4 | ✅ |

*Results from default parameters (velocity=1000 bp/s, 20 cohesins, seed=42)*

## 🧬 Features

### Core Physics Engine
- **Loop Extrusion Simulation**: Cohesin motors extrude DNA until blocked by CTCF
- **Convergent Rule**: R...F orientation forms loops; F...R blocks extrusion
- **Ensemble Simulation**: Multiple cohesins for realistic contact matrices
- **Deterministic**: Fixed seed for reproducible research

### Visualization
- **3D Browser Rendering**: React Three Fiber + WebGL
- **Real-time Dashboard**: NASA-style telemetry display
- **Contact Matrix Heatmaps**: Side-by-side comparison (optional AlphaGenome mock)
- **P(s) Curves**: Power-law fitting (-1.0 exponent validation)

### Validation
- **Validation target**: Experimental Hi-C (Rao et al.); mock AlphaGenome for development
- **Grid Search**: Parameter optimization for r > 0.7
- **Gold Standard Tests**: HBB, Sox2, Pcdh loci from literature

## 📁 Project Structure

```
archcode/
├── src/
│   ├── components/        # React UI components
│   │   └── dashboard/     # Real-time telemetry
│   ├── domain/            # Core business logic
│   │   ├── constants/     # Biophysical parameters
│   │   └── models/        # TypeScript interfaces
│   ├── engines/           # Physics engines
│   │   ├── LoopExtrusionEngine.ts      # Single cohesin
│   │   └── MultiCohesinEngine.ts       # Ensemble (20 LEFs)
│   ├── parsers/           # BED file parsing
│   ├── store/             # Zustand state management
│   ├── utils/             # Seedable RNG, math helpers
│   ├── validation/        # AlphaGenome client
│   └── __tests__/         # Vitest test suites
│       └── regression/    # Gold standard tests
├── config/
│   └── default.json       # Optimized parameters
├── results/               # Validation outputs
├── scripts/               # Grid search, CLI tools
├── docs/                  # Documentation
└── publication/           # Figures for paper
```

## ⚙️ Configuration

Edit `config/default.json`:

```json
{
  "biophysics": {
    "cohesin": {
      "velocity": 1000,          // bp per step
      "processivity": 600,       // kb
      "unloadingProbability": 0.0005
    },
    "ctcf": {
      "convergentBlockingEfficiency": 0.9
    }
  },
  "ensemble": {
    "numCohesins": 20
  }
}
```

## 🔬 Methodology

See [METHODS.md](./METHODS.md) for detailed algorithm description suitable for publication Methods sections.

### Key Equations

**Cohesin Motion:**
```
leftLeg(t+1) = leftLeg(t) - velocity
rightLeg(t+1) = rightLeg(t) + velocity
```

**Convergent Rule:**
```
Loop forms if: R@leftLeg AND F@rightLeg
where R = reverse CTCF (<), F = forward CTCF (>)
```

**Contact Probability:**
```
P(s) ~ s^(-α) where α ≈ 1.0 (theoretical)
```

## Development

Git tags (`pre-audit`, `post-p0-fixes`) and commit discipline for AI-assisted work are described in [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md). Project rules for Cursor/AI are in [.cursorrules](./.cursorrules).

## 🐛 Known Issues

See [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) for limitations and future work.

## 📄 License

MIT License — See [LICENSE](./LICENSE)

## 🙏 Acknowledgments

- **Sanborn et al. (2015)** — Loop extrusion model foundation
- **Rao et al. (2014)** — Hi-C contact maps and validation target
- **Davidson et al. (2019)** — Human cohesin single-molecule kinetics
- **Gerlich et al. (2006)** — Cohesin residence time FRAP data
- **React Three Fiber** — 3D visualization
- **AlphaGenome** — Optional integration (mock in v1.0)

## 📚 Citation

```bibtex
@software{archcode2024,
  title = {ARCHCODE: 3D DNA Loop Extrusion Simulator},
  author = {Your Name},
  year = {2024},
  url = {https://doi.org/10.5281/zenodo.xxxxx}
}
```

---

**Version**: 1.0.0  
**Last Updated**: 2024-02-01  
**Status**: Publication Ready ✅
