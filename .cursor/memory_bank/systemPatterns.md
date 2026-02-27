# System Patterns & Architecture

**ARCHCODE v1.0**
**Last Updated:** 2026-02-05
**Type:** Reference Document (stable, rarely changes)

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│              Browser (React SPA)                     │
├─────────────────────────────────────────────────────┤
│  UI Layer (React Components)                        │
│  ├── 3D Visualization (Three.js + R3F)              │
│  ├── Dashboards (Telemetry, Loops)                  │
│  └── Controls (BED Upload, Parameters)              │
├─────────────────────────────────────────────────────┤
│  Domain Layer (Business Logic)                      │
│  ├── Physics Engines (Loop Extrusion)               │
│  ├── Models (Genome, CTCF, Loops)                   │
│  └── Constants (Biophysics Parameters)              │
├─────────────────────────────────────────────────────┤
│  Infrastructure Layer                               │
│  ├── Parsers (BED files)                            │
│  ├── Validation (AlphaGenome, Hi-C comparison)      │
│  ├── Utils (Seedable RNG, Math)                     │
│  └── Store (Zustand state management)               │
└─────────────────────────────────────────────────────┘
```

**Principle:** Domain logic isolated from UI → testable, portable.

---

## 🧬 Core Domain Model

### 1. CTCF Site (Binding Site)

```typescript
interface CTCFSite {
  position: number; // Base pair position on chromosome
  orientation: string; // 'F' (forward >) or 'R' (reverse <)
  strength: number; // Binding affinity (0-1)
}
```

**Convergent Rule:**

- R...F orientation → forms loop (blocking)
- F...R orientation → extrusion continues (no blocking)
- F...F or R...R → partial blocking (direction-dependent)

### 2. Loop (Formed by Cohesin)

```typescript
interface Loop {
  id: string; // Unique identifier
  leftSite: CTCFSite; // Left anchor (usually R orientation)
  rightSite: CTCFSite; // Right anchor (usually F orientation)
  formationTime: number; // Simulation step when formed
  strength: number; // Contact frequency (ensemble average)
}
```

### 3. Cohesin (Loop Extruding Factor)

```typescript
interface Cohesin {
  id: string;
  leftLeg: number; // Left position (bp)
  rightLeg: number; // Right position (bp)
  state: "extruding" | "stalled" | "unloaded";
  velocity: number; // bp per simulation step (default: 1000)
  processivity: number; // Max distance before unloading (default: 600kb)
}
```

**Motion Rule:**

```
At each timestep:
  leftLeg(t+1) = leftLeg(t) - velocity
  rightLeg(t+1) = rightLeg(t) + velocity

If convergent CTCF encountered:
  state = 'stalled'
  loop formed
```

---

## ⚙️ Physics Engines

### LoopExtrusionEngine (Single Cohesin)

**Purpose:** Simulate one cohesin's trajectory until unloading

**Algorithm:**

```
1. Load cohesin at random position (seed-controlled)
2. Extrude bidirectionally (velocity bp/step)
3. Check CTCF collisions:
   - Left leg: scan for R orientation
   - Right leg: scan for F orientation
4. If convergent blocking → form loop, stall
5. If processivity exceeded → unload
6. Repeat until simulation time ends
```

**Output:** Loop coordinates, trajectory history

**Usage:**

```typescript
const engine = new LoopExtrusionEngine(genome, config);
const result = engine.simulate();
// result.loops: Loop[]
// result.trajectory: Position[]
```

### MultiCohesinEngine (Ensemble)

**Purpose:** Simulate multiple cohesins in parallel (realistic crowding)

**Algorithm:**

```
1. Initialize N cohesins (default: 20) at random positions
2. For each timestep:
   a. Move all active cohesins
   b. Check CTCF collisions
   c. Unload cohesins that exceeded processivity
   d. Load new cohesins at random positions (maintain N)
3. Aggregate loops from all cohesins
4. Build contact matrix from loop frequencies
```

**Output:** Contact matrix (NxN), loop ensemble

**Usage:**

```typescript
const engine = new MultiCohesinEngine(genome, config);
const matrix = engine.generateContactMatrix();
// matrix: number[][] (Hi-C style heatmap)
```

---

## 🎨 UI Architecture (React + Three.js)

### Component Hierarchy

```
<App>
├── <GenomeViewer>          // 3D visualization (Three.js)
│   ├── <Canvas>            // React Three Fiber
│   ├── <DNAHelix>          // Chromatin fiber geometry
│   ├── <LoopArcs>          // Loop structures (curves)
│   └── <CTCFMarkers>       // Binding sites (spheres)
├── <LoopDashboard>         // Real-time telemetry
│   ├── <MetricCard>        // KPIs (loop count, velocity)
│   └── <ProgressBar>       // Simulation progress
├── <ContactMatrixViewer>   // Heatmap comparison
│   ├── <Heatmap>           // D3.js color scale
│   └── <CorrelationScore>  // Pearson r display
└── <BEDUploader>           // File upload control
    └── <BEDParser>         // Parse CTCF sites
```

### State Management (Zustand)

**Store:** `src/store/simulationStore.ts`

**State Slices:**

```typescript
interface SimulationState {
  // Genome data
  ctcfSites: CTCFSite[];
  loops: Loop[];

  // Simulation state
  isRunning: boolean;
  currentStep: number;

  // Configuration
  parameters: BiophysicsConfig;

  // Actions
  startSimulation: () => void;
  stopSimulation: () => void;
  updateParameters: (params) => void;
}
```

**Principle:** Single source of truth, minimal state, immutable updates.

---

## 🧪 Testing Strategy

### Test Pyramid

```
                    /\
                   /  \  E2E (Playwright) - 5%
                  /────\
                 /      \  Integration (Vitest) - 15%
                /────────\
               /          \  Unit Tests (Vitest) - 80%
              /────────────\
```

### Key Test Types

**1. Unit Tests (engines, utils)**

```typescript
describe("LoopExtrusionEngine", () => {
  it("forms loop at convergent CTCF pair", () => {
    // Arrange: genome with R at 1000bp, F at 5000bp
    // Act: run simulation
    // Assert: loop formed at (1000, 5000)
  });
});
```

**2. Regression Tests (gold standard validation)**

```typescript
describe("HBB Validation", () => {
  it("achieves Pearson r >= 0.7 vs Rao et al.", async () => {
    const simMatrix = runSimulation("HBB");
    const realMatrix = await loadHiCData("HBB");
    const r = calculatePearson(simMatrix, realMatrix);
    expect(r).toBeGreaterThanOrEqual(0.7);
  });
});
```

**3. Property-Based Tests (invariants)**

```typescript
it("contact frequency decreases with genomic distance", () => {
  fc.assert(
    fc.property(fc.array(fc.ctcfSite()), (sites) => {
      const matrix = simulate(sites);
      // P(s) ~ s^(-1) power law
      expect(isPowerLaw(matrix, -1.0)).toBe(true);
    }),
  );
});
```

---

## 📦 Module Boundaries

### Clean Architecture Layers

**1. Domain (Pure Functions)**

```
src/domain/
├── constants/biophysics.ts   // NO dependencies
├── models/genome.ts           // NO dependencies
└── [NEVER import from UI or infrastructure]
```

**2. Engines (Domain Services)**

```
src/engines/
├── LoopExtrusionEngine.ts     // Depends: domain, utils
├── MultiCohesinEngine.ts      // Depends: domain, utils
└── [NEVER import from UI]
```

**3. UI (Presentation)**

```
src/components/
├── 3d/GenomeViewer.tsx        // Depends: engines, store
├── dashboard/LoopDashboard.tsx // Depends: store
└── [CAN import anything, but nothing imports UI]
```

**Dependency Rule:** Outer layers depend on inner, NEVER reverse.

---

## 🔧 Configuration Management

### Single Source of Truth

**File:** `config/default.json`

```json
{
  "biophysics": {
    "cohesin": {
      "velocity": 1000, // bp/step
      "processivity": 600000, // bp (600 kb)
      "unloadingProbability": 0.0005
    },
    "ctcf": {
      "convergentBlockingEfficiency": 0.9
    }
  },
  "simulation": {
    "seed": 42, // Reproducibility
    "numSteps": 10000,
    "numCohesins": 20
  }
}
```

**Usage:**

```typescript
import config from "../config/default.json";
const velocity = config.biophysics.cohesin.velocity;
```

**NO hardcoded magic numbers in code!**

---

## 🎯 Design Patterns Used

### 1. Engine Pattern (Physics)

**Problem:** Complex simulation logic separate from UI
**Solution:** LoopExtrusionEngine, MultiCohesinEngine
**Benefits:** Testable, portable (can run in Node.js)

### 2. Observer Pattern (State Updates)

**Problem:** UI needs real-time updates during simulation
**Solution:** Zustand store + React hooks
**Benefits:** Decoupled, reactive

### 3. Strategy Pattern (Validation)

**Problem:** Multiple validation targets (Hi-C, AlphaGenome, P(s))
**Solution:** Validator interface, concrete implementations
**Benefits:** Extensible, swappable

### 4. Builder Pattern (Genome Construction)

**Problem:** Complex genome setup from BED files
**Solution:** GenomeBuilder with fluent API
**Benefits:** Readable, flexible

---

## 🚫 Anti-Patterns to Avoid

### 1. God Objects

❌ **Bad:**

```typescript
class SimulationManager {
  parseFile() {}
  simulate() {}
  render() {}
  saveResults() {}
}
```

✅ **Good:**

```typescript
const parser = new BEDParser();
const engine = new LoopExtrusionEngine();
const renderer = new GenomeRenderer();
```

### 2. Premature Optimization

❌ **Bad:** WebAssembly for hot loops (not needed yet)
✅ **Good:** Simple TypeScript, profile first

### 3. Feature Creep

❌ **Bad:** Add RNA-seq, ATAC-seq, ChIP-seq all at once
✅ **Good:** Validate core loop extrusion first

---

## 📊 Performance Characteristics

### Scaling

| Locus Size | CTCF Sites | Cohesins | Time (ms) | Memory (MB) |
| ---------- | ---------- | -------- | --------- | ----------- |
| 100 kb     | 10         | 10       | 500       | 50          |
| 200 kb     | 20         | 20       | 2000      | 100         |
| 1 Mb       | 100        | 50       | 15000     | 500         |

**Bottleneck:** Contact matrix generation (O(n²) for n bins)

**Optimization Strategy:**

1. Profile first (Vitest --reporter)
2. Optimize hot paths (collision detection)
3. Consider Web Workers for parallelization (future)

---

## 🔐 Security Considerations

### Data Handling

- **User uploads:** BED files (text, safe)
- **API calls:** AlphaGenome (optional, HTTPS only)
- **Local storage:** Simulation results (localStorage, user-controlled)

### No Backend

- Pure client-side app (no server, no database)
- No sensitive data storage
- No authentication required

### Content Security Policy

```html
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self';
               script-src 'self' 'unsafe-eval';
               style-src 'self' 'unsafe-inline';"
/>
```

---

## 🎓 Learning Resources

### For New Developers

1. **Loop Extrusion Biology:** Sanborn et al. 2015 (PNAS)
2. **TypeScript:** Official handbook (typescriptlang.org)
3. **Three.js:** Journey tutorial (threejs-journey.com)
4. **React:** Official docs (react.dev)

### Architecture Inspirations

- Clean Architecture (Robert C. Martin)
- Domain-Driven Design (Eric Evans)
- Hexagonal Architecture (Alistair Cockburn)

---

**Stability:** This document changes rarely (architecture decisions)
**Related:** See `decisions.md` for WHY we chose these patterns
