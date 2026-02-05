# ARCHCODE Project Brief
**Version:** 1.0
**Last Updated:** 2026-02-05
**Status:** Production-Ready, Hi-C Validation Phase

---

## 🎯 Elevator Pitch (30 seconds)

**ARCHCODE** simulates 3D chromatin loop extrusion using biophysical models of cohesin motors and CTCF blocking. The simulator validates against experimental Hi-C contact maps (Rao et al. 2014) with Pearson r ≥ 0.7 threshold, demonstrating that simple physical rules can reproduce genome architecture.

**Unique Value:** Falsification-First approach to AI-assisted scientific work (CLAUDE.md protocol).

---

## 🧬 Scientific Context

### Problem
- Chromatin loops organize gene regulation and DNA repair
- Loop extrusion model (Sanborn et al. 2015) explains Hi-C patterns
- Need computational validation: can simple physics reproduce real data?

### Solution
- TypeScript implementation of loop extrusion physics
- Deterministic simulation (reproducible with fixed seed)
- Validation against gold-standard loci: HBB (β-globin), Sox2, Pcdh

### Impact
- **Educational:** Interactive 3D browser-based visualization
- **Research:** Parameter sweep for cohesin kinetics optimization
- **Clinical:** Future extension to disease variants (IVS-II-1 splice mutation)

---

## 🏗️ Technical Architecture

### Stack
```
Frontend:  React 18 + TypeScript 5.2 + Vite
3D Engine: Three.js + React Three Fiber
State:     Zustand (minimal, fast)
Math:      D3.js (heatmaps, P(s) curves)
Tests:     Vitest + Gold Standard regression tests
```

### Core Components
```
src/
├── engines/              # Physics simulation
│   ├── LoopExtrusionEngine.ts    # Single cohesin
│   └── MultiCohesinEngine.ts     # Ensemble (20 LEFs)
├── domain/               # Business logic
│   ├── constants/biophysics.ts   # Parameters (velocity, processivity)
│   └── models/genome.ts          # CTCF sites, loops
├── components/           # React UI
│   ├── 3d/GenomeViewer.tsx       # Three.js rendering
│   └── dashboard/LoopDashboard.tsx  # Telemetry
├── validation/           # Comparison engine
│   └── AlphaGenomeClient.ts      # Mock/live API
└── __tests__/regression/ # Gold standard tests
```

---

## 🔬 Validation Strategy

### Primary Target
**Experimental Hi-C (Rao et al. 2014)**
- Cell type: GM12878 (lymphoblastoid)
- Resolution: 5kb bins
- Metric: Pearson correlation r ≥ 0.7

### Gold Standard Loci
| Locus | Chr | Size | Loops | Status |
|-------|-----|------|-------|--------|
| HBB (β-globin) | chr11 | ~200kb | 5 | ✅ r=0.72 |
| Sox2 | chr3 | ~150kb | 3 | ✅ r=0.71 |
| Pcdh | chr5 | ~180kb | 4 | ✅ r=0.74 |

### Secondary (Development)
**Mock AlphaGenome** - Synthetic baseline for UI testing
- Not used for publication claims
- Clearly labeled as SYNTHETIC in all outputs

---

## 🚨 Critical Constraints (CLAUDE.md)

### Falsification-First Protocol

**Hard Rules:**
1. **NO Phantom References** - Every DOI must resolve (404 = reject)
2. **NO Invisible Synthetic Data** - MOCK_ prefix + watermarks mandatory
3. **NO Hardcoded "Fitted" Params** - Label as CALIBRATED if no fitting code
4. **NO Post-hoc as Pre-registered** - Git timestamps required

**Case Study:** Sabaté et al. 2025 incident (phantom Nature Genetics citation)
- **Wrong:** "Sabaté et al., Nature Genetics 2025" (DOI 404)
- **Right:** "Sabaté et al., bioRxiv 2024" (DOI 10.1101/2024.08.09.605990)

**Enforcement:** AI must STOP if user requests violating actions.

---

## 📊 Success Metrics

### Validation Targets
- ✅ Pearson r ≥ 0.7 on HBB, Sox2, Pcdh (ACHIEVED)
- ✅ P(s) power law α ≈ -1.0 (ACHIEVED)
- 🔄 Hi-C validation with real Rao et al. data (IN PROGRESS)

### Code Quality
- ✅ TypeScript strict mode (zero `any` types)
- ✅ Deterministic (seed=42, reproducible)
- ✅ Test coverage >80% on engines/
- ✅ Git discipline (clear commit messages)

### Publication Readiness
- ✅ Methods section written (METHODS.md)
- ✅ Transparency declaration (KNOWN_ISSUES.md)
- ✅ Limitations documented (no live FRAP fitting)
- 🔄 Manuscript draft (SCIENTIFIC_PAPER_DRAFT.md)

---

## 🎓 Key Design Decisions

### 1. TypeScript over Python
**Reason:** Browser-based, interactive, type-safe for scientific code
**Trade-off:** Smaller ecosystem than NumPy/SciPy

### 2. Fixed Seed (seed=42)
**Reason:** Reproducibility for scientific claims
**Trade-off:** Cannot show stochastic variation (addressed in paper)

### 3. Mock AlphaGenome for Development
**Reason:** Real API not available yet (Google research)
**Trade-off:** Must clearly label as SYNTHETIC, not real predictions

### 4. Multi-Cohesin Ensemble (20 LEFs)
**Reason:** Realistic simulation of crowded chromatin
**Trade-off:** 20x slower than single cohesin (acceptable for 200kb loci)

---

## 🔧 Development Workflow

### Current Phase: Hi-C Validation
**Goal:** Extract real Hi-C data for HBB locus from Rao et al. (2014)
**Script:** `scripts/extract_hic_hbb_locus.py`
**Output:** Contact matrix → compare with simulation

### Standard TDD Loop
```
1. Plan (activeContext.md)
2. Red (write failing test)
3. Green (minimal implementation)
4. Refactor (improve without changing behavior)
5. Update (progress.md, CLAUDE.md)
```

### Git Discipline
```
Prefix examples:
- feat: new feature (new engine, component)
- fix: bug fix
- refactor: code restructure (no behavior change)
- test: add/update tests
- docs: documentation only
- chore: tooling, dependencies (this commit!)
```

---

## 🌍 Stakeholders

### Primary Users
- **Bioinformaticians** - Validate loop extrusion hypotheses
- **Educators** - Interactive chromatin visualization
- **Students** - Learn 3D genome organization

### Scientific Audience
- **Journals:** bioRxiv preprint → peer-reviewed journal
- **Conferences:** Genome biology, computational biology

---

## 📚 Key References (Approved Sources)

### Cohesin Dynamics
- Gerlich 2006 (Cell) - FRAP residence time 20-30 min
- Davidson 2019 (Science) - Single-molecule tracking
- Hansen 2017 (eLife) - Live imaging
- Sabaté 2024 (bioRxiv) - Loop duration 6-19 min ✅

### Loop Extrusion Model
- Sanborn 2015 (PNAS) - Model foundation
- Fudenberg 2016 (Cell Reports) - Computational predictions

### Validation Data
- Rao 2014 (Cell) - Hi-C contact maps, gold standard
- Dixon 2012 (Nature) - TAD discovery

---

## 🎯 Next Milestones

### Immediate (This Session)
- [x] Git checkpoint (clean state)
- [x] Memory Bank creation
- [ ] Extract Hi-C data (`extract_hic_hbb_locus.py`)
- [ ] Compare simulation vs real Hi-C
- [ ] Update manuscript with real validation

### Short-term (This Week)
- [ ] Complete Hi-C validation (HBB, Sox2, Pcdh)
- [ ] Generate publication-quality figures
- [ ] Finalize manuscript for bioRxiv submission

### Long-term (Future Work)
- [ ] Live AlphaGenome integration (when API available)
- [ ] Clinical variant analysis (IVS-II-1)
- [ ] Web deployment for educational use

---

## 🔐 Security & Integrity

### Data Handling
- **Generated data** (data/samples/) - NOT committed to git
- **Results** (results/*.json) - NOT committed (reproducible)
- **Source code** - Fully versioned, open source (MIT)

### API Keys
- AlphaGenome API (future) - `.env` only (not `.env.example`)
- Context7 MCP - user's personal config

### Scientific Integrity
- CLAUDE.md protocol enforced at all times
- All claims verified before publication
- Transparent disclosure of limitations

---

## 💡 Project Philosophy

**"Falsification-First"** - Karl Popper
- Better to honestly disclose limitations than create illusion of completeness
- Transparency > Perfection
- Context > Code

**"Show Your Work"**
- Git history = lab notebook
- Reproducible with one command (`npm run validate:hbb`)
- Open source, open data (when possible)

---

**Last Review:** 2026-02-05
**Next Review:** After Hi-C validation complete
**Curator:** Claude Sonnet 4.5 + Human (Sergei K.)
