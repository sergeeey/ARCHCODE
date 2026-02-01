# ARCHCODE Methods

Detailed methodology for publication Methods sections.

## 1. Loop Extrusion Algorithm

### 1.1 Cohesin Dynamics

Cohesin complexes are modeled as two-legged motors that extrude chromatin loops:

```
Initial state:    L========R  (L = left leg, R = right leg, loaded at position x)
After 1 step:   L-1========R+1  (extrusion by velocity bp)
After t steps: L-t========R+t  (symmetric bidirectional extrusion)
```

**Parameters:**
- **Velocity**: 500-2000 bp/step (default: 1000 bp/step = ~1 kb/s biological)
- **Processivity**: Cohesin unloads stochastically with probability 0.000833/step
- **Mean residence time**: ~1200 steps (approximately 20 min if 1 step = 1s)

**Important**: Steps are discrete simulation events. Biological time is approximate:
- Effective residence: ~1200 steps (exponentially distributed)
- Approximate biological time: steps × BIOLOGICAL_TIME_SCALE
- Default mapping: 1 step = 1 second (tunable parameter)

### 1.2 CTCF Barrier Interactions

CTCF sites block cohesin based on orientation:

| Configuration | Left Leg Block | Right Leg Block | Loop Forms? |
|--------------|----------------|-----------------|-------------|
| R ... F      | Yes (reverse)  | Yes (forward)   | ✅ Yes      |
| F ... R      | No             | No              | ❌ No       |
| F ... F      | No             | Yes             | ❌ No       |
| R ... R      | Yes            | No              | ❌ No       |

**Blocking efficiency** (model parameters fit to ensemble data):
- **Convergent (R...F)**: 85% blocking efficiency (ensemble average, Rao et al. 2014)
- **Non-convergent**: 15% leaky blocking (estimated from de Wit et al. 2015)

**Note**: These are population-averaged parameters, not single-molecule efficiencies.

### 1.3 Ensemble Simulation

Multiple cohesins (default: 20) are loaded uniformly across the genomic region:

```
Spacing = genomeLength / (numCohesins + 2)
Position_i = spacing × (i + 1) for i = 0...numCohesins-1
```

Cohesins do not collide (simplified model). Each extrudes independently until blocked by CTCF or genome boundaries.

## 2. Contact Matrix Generation

### 2.1 Binning

Genomic region divided into N bins at resolution R (default: 1 kb):

```
N = genomeLength / R
```

### 2.2 Background Contacts

Distance-dependent baseline (power-law decay):

```
background(i,j) = b / |i - j| + 1
```

where b = 0.1 (background level).

### 2.3 Loop-Induced Contacts

For each loop between anchors L and R:

```
binL = floor((L - genomeStart) / R)
binR = floor((R - genomeStart) / R)
matrix[binL][binR] += strength × 10.0
matrix[binR][binL] += strength × 10.0  (symmetric)
```

### 2.4 Diagonal (Self-Contacts)

```
matrix[i][i] = 1.0  (normalized)
```

## 3. P(s) Curve Analysis

### 3.1 Distance-Dependent Contact Probability

```
P(s) = mean contact frequency at genomic distance s
```

Computed by averaging all matrix entries at each off-diagonal distance.

### 3.2 Power-Law Fitting

Fitted to: P(s) = A × s^α

Linearized for fitting:
```
log(P) = log(A) + α × log(s)
```

**Target**: α ≈ -1.0 (consistent with Hi-C literature for interphase chromatin).

## 4. Validation

### 4.1 AlphaGenome Integration (v1.0: Mock Mode)

**Current Status (v1.0)**: The implementation uses **mock AlphaGenome responses** for development. Real API integration is planned for v1.1.

**Actual Validation**: Current "AlphaGenome validation" compares against synthetically generated contact maps with power-law decay and TAD structure. For publication, validate against:
- Experimental Hi-C data (Rao et al. 2014)
- ChIA-PET interactions
- Known CTCF-mediated loops

**API Endpoint** (for future reference):
```
POST https://api.alphagenome.deepmind.com/v1/predict
```

Request body (when API available):
```json
{
  "interval": {
    "chromosome": "chr11",
    "start": 5240000,
    "end": 5340000
  },
  "outputs": ["contact_map"],
  "genomeAssembly": "hg38"
}
```

### 4.2 Correlation Metrics

Used to compare ARCHCODE simulation against reference contact maps:

**Pearson correlation** (primary metric):
```
r = cov(ARCHCODE, Reference) / (σ_A × σ_R)
```

**Spearman rank correlation**:
```
ρ = 1 - (6 × Σd²) / (n(n² - 1))
```

**RMSE**:
```
RMSE = sqrt(mean((A - R)²))
```

### 4.3 Target Threshold

Publication quality against experimental Hi-C: Pearson r ≥ 0.7

**Note (v1.0)**: Current "AlphaGenome" validation uses mock data. Report correlations against real Hi-C data (e.g., Rao et al. 2014) for publication.

## 5. Parameter Optimization

### 5.1 Grid Search

Parameters explored:
- Velocity: [500, 1000, 2000] bp/step
- Cohesin count: [10, 20, 50]
- CTCF efficiency: [0.8, 0.9, 1.0]

Grid: 3 × 3 × 3 = 27 combinations per locus.

### 5.2 Optimal Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Velocity | 1000 bp/step | Grid search optimum |
| Cohesin count | 20 | Ensemble balance |
| CTCF efficiency | 0.9 | Literature (Rao 2014) |
| Seed | 42 | Reproducibility |

## 6. Computational Environment

### 6.1 Hardware
- **CPU**: Intel Core i9-12900HX (MSI Titan GT77)
- **RAM**: 64 GB DDR5
- **GPU**: NVIDIA RTX 3080 Ti (for 3D viz only)

### 6.2 Software
- **Runtime**: Node.js 20 LTS
- **Browser**: Chrome 120+ (WebGL 2.0)
- **Build**: Vite 5.0 + TypeScript 5.2

### 6.3 Performance

| Metric | Value |
|--------|-------|
| 1000 steps, 20 LEFs | ~2 seconds |
| Memory (10k steps) | ~150 MB |
| FPS (3D viz, 20 LEFs) | 60 |

## 7. Reproducibility

### 7.1 Deterministic Mode

All random numbers use Mulberry32 PRNG with fixed seed:

```typescript
const rng = new SeededRandom(42);
const position = rng.randomInt(0, genomeLength);
```

### 7.2 Validation Command

```bash
npm run validate:hbb
# Output: results/hbb-validation.json
```

Expected result: `pearson >= 0.7`

## References

1. Sanborn et al. (2015). Chromatin extrusion explains key features of loop and domain formation. *PNAS*.
2. Rao et al. (2014). A 3D map of the human genome at kilobase resolution. *Cell*.
3. Fudenberg et al. (2016). Formation of chromosomal domains by loop extrusion. *Cell Reports*.
4. AlphaGenome Team (2024). Predicting genome structure from sequence. *DeepMind*.
