# Project Plan: Option B (REAL) — Experimental Data Validation

## ARCHCODE vs Ground Truth: Hi-C + RNA-seq Integration

**Decision Date:** 2026-02-04 19:45 (CORRECTED)
**Timeline:** 3-5 days (fast track)
**Approach:** **Model vs Reality** (not Model vs Model)
**Status:** READY TO EXECUTE

---

## 🎯 Critical Difference from Wrong Approach

### ❌ WRONG (ClinVar-only):

```
ClinVar variants → ARCHCODE simulation → SpliceAI prediction
                         ↓                        ↓
                   (predicted)              (predicted)
                         └─────── compare ─────────┘
                              (no ground truth)
```

**Problem:** Model comparison, not validation

### ✅ CORRECT (Hi-C + RNA-seq):

```
Real Hi-C contacts (HUDEP2) → Ground truth structure
         ↓
ARCHCODE simulation → Compare → Validation (R² correlation)
         ↓
Real RNA-seq (GSE131055) → Ground truth splicing defects
         ↓
Hypothesis test: Stable loops correlate with trapped transcripts?
```

**Advantage:** Experimental validation, real discovery

---

## 📁 Available Experimental Data

### Priority 1: Hi-C (Structure Ground Truth)

**Files Found:**

- `GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic` (6.7 GB) — Genome-wide
- `GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic` (2.3 GB) — **Targeted, use this**
- `GSM4873114_B6-HUDEP2-HiC` (6.7 GB) — B6 mutant
- `GSM4873115_A2-HUDEP2-HiC` (6.5 GB) — A2 mutant

**Source:** GEO GSE160422 (Published Hi-C on HUDEP2 cells)

### Priority 2: RNA-seq (Function Ground Truth)

**File:**

- `GSE131055_RAW.tar` (4.4 GB) — RNA-seq data

**Task:** Detect aberrant splicing in HBB locus

### Priority 3: ChIP-seq (Validation)

**Files:** In GSE160422 archives

- GATA1 ChIP-seq — Transcription factor binding
- CTCF ChIP-seq — TAD boundary validation

---

## 📅 FAST TRACK TIMELINE (3-5 Days)

### Day 1: Hi-C Extraction & Validation (TODAY)

**Morning:**

- [ ] Install juicer_tools (for .hic processing)
- [ ] Extract HBB locus: chr11:5,200,000-5,250,000
- [ ] Convert to contact matrix (50 KB bins)

**Afternoon:**

- [ ] Run ARCHCODE WT simulation for same locus
- [ ] Compare matrices: Pearson R², Spearman ρ
- [ ] **Decision point:** R² > 0.7 → model validated, proceed

**Evening:**

- [ ] Visualize: Side-by-side heatmaps (Real vs Simulated)
- [ ] Document correlation metrics

---

### Day 2: RNA-seq Aberrant Splicing Detection

**Morning:**

- [ ] Extract `GSE131055_RAW.tar`
- [ ] Identify FASTQ files for HBB region
- [ ] Run STAR alignment (or use pre-aligned BAM)

**Afternoon:**

- [ ] Splice junction analysis with rMATS or LeafCutter
- [ ] Detect: Intron retention, cryptic splice sites
- [ ] Quantify: PSI (Percent Spliced In) for HBB exons

**Evening:**

- [ ] Cross-reference with Hi-C: Do stable loops correlate with splicing defects?
- [ ] Statistical test: χ² or Fisher's exact

---

### Day 3: Integration & Discovery

**Morning:**

- [ ] Overlay Hi-C contact strength with RNA-seq splicing efficiency
- [ ] Identify regions: High contact + Low splicing → "Loop trap" candidates

**Afternoon:**

- [ ] Check ClinVar: Are these positions known pathogenic variants?
- [ ] Literature search: Any case reports for discovered variants?

**Evening:**

- [ ] Manuscript draft: Results section with real data
- [ ] Create Figure 3: Hi-C validation (Real vs ARCHCODE)
- [ ] Create Figure 4: Splicing defects map

---

### Day 4-5: Manuscript Finalization

- [ ] Update Methods with real data processing
- [ ] Results: Validation (R²) + Discovery (splicing-structure correlation)
- [ ] Discussion: Experimental evidence for "Loop That Stayed"
- [ ] Submit to bioRxiv

---

## 🔧 Technical Implementation

### Task 1.1: Extract HBB Locus from Hi-C

**Install juicer_tools:**

```bash
# Download juicer_tools.jar
wget https://s3.amazonaws.com/hicfiles.tc4ga.com/public/juicer/juicer_tools.jar

# Or use hictools Python package
pip install hic-straw
```

**Extract contact matrix:**

```python
# Using hic-straw (Python)
import hicstraw

# Load .hic file
hic = hicstraw.HiCFile("GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic")

# Extract HBB locus: chr11:5,200,000-5,250,000
# Resolution: 5 KB (or 10 KB for faster)
matrix = hic.getMatrixZoomData('chr11', 'chr11', "observed", "KR", "BP", 5000)
contacts = matrix.getRecordsAsMatrix(5200000, 5250000, 5200000, 5250000)

# Save as numpy array
import numpy as np
np.save('data/hudep2_wt_hic_hbb_locus.npy', contacts)
```

**Alternative: juicer_tools CLI:**

```bash
java -jar juicer_tools.jar dump observed KR \
  GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic \
  chr11:5200000:5250000 chr11:5200000:5250000 BP 5000 \
  data/hudep2_wt_contacts.txt
```

---

### Task 1.2: ARCHCODE WT Simulation

**Run simulation:**

```typescript
// scripts/simulate_wt_hbb_for_validation.ts
import { LoopExtrusionEngine } from "../src/engines/LoopExtrusionEngine";

const config = {
  locus: {
    chromosome: "chr11",
    start: 5200000,
    end: 5250000,
  },
  resolution: 5000, // Match Hi-C resolution
  simulation_time: 10000, // 10k steps
  output: "data/archcode_wt_hbb_contacts.npy",
};

const engine = new LoopExtrusionEngine(config);
const contacts = engine.simulate();
engine.saveContactMatrix(contacts, config.output);
```

---

### Task 1.3: Correlation Analysis

**Compare matrices:**

```python
import numpy as np
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt

# Load matrices
real = np.load('data/hudep2_wt_hic_hbb_locus.npy')
simulated = np.load('data/archcode_wt_hbb_contacts.npy')

# Normalize (Hi-C bias correction already applied via KR)
real_norm = real / np.max(real)
sim_norm = simulated / np.max(simulated)

# Correlation (flatten to 1D)
r_pearson, p_pearson = pearsonr(real_norm.flatten(), sim_norm.flatten())
r_spearman, p_spearman = spearmanr(real_norm.flatten(), sim_norm.flatten())

print(f"Pearson R² = {r_pearson**2:.3f} (p={p_pearson:.2e})")
print(f"Spearman ρ = {r_spearman:.3f} (p={p_spearman:.2e})")

# Visualize
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].imshow(real_norm, cmap='Reds')
axes[0].set_title('Real Hi-C (HUDEP2)')
axes[1].imshow(sim_norm, cmap='Reds')
axes[1].set_title('ARCHCODE Simulation')
axes[2].scatter(real_norm.flatten(), sim_norm.flatten(), alpha=0.1)
axes[2].set_title(f'Correlation (R²={r_pearson**2:.3f})')
plt.savefig('results/hic_validation.png', dpi=300)
```

**Success Criteria:**

- R² > 0.7 → Excellent validation
- R² 0.5-0.7 → Good validation
- R² < 0.5 → Model needs calibration

---

### Task 2.1: RNA-seq Splicing Analysis

**Extract tar:**

```bash
cd "C:\Users\serge\Desktop\ДНК\ДНК Образцы СКАЧЕННЫЙ"
tar -xf GSE131055_RAW.tar
ls GSE131055_RAW/*.fastq.gz
```

**Run splice junction detection:**

```bash
# Using rMATS (best for differential splicing)
rmats.py \
  --b1 wt_samples.txt \
  --b2 mutant_samples.txt \
  --gtf gencode.v38.annotation.gtf \
  --readLength 150 \
  --od output/rmats \
  --tmp tmp

# Extract HBB splicing events
grep "HBB\|chr11:522" output/rmats/SE.MATS.JC.txt
```

**Alternative: STAR alignment + junction counts:**

```bash
STAR --genomeDir hg38_star_index \
  --readFilesIn sample_R1.fastq.gz sample_R2.fastq.gz \
  --readFilesCommand zcat \
  --outSAMtype BAM SortedByCoordinate \
  --quantMode GeneCounts \
  --outFilterMultimapNmax 1 \
  --sjdbGTFfile gencode.v38.gtf

# Extract HBB junctions
samtools view -b Aligned.sortedByCoord.out.bam chr11:5225464-5227079 > hbb_reads.bam
```

---

### Task 2.2: Intron Retention Analysis

**Detect retained introns:**

```python
import pysam

bam = pysam.AlignmentFile('hbb_reads.bam', 'rb')

# HBB introns (GRCh38 coordinates)
introns = [
    (5226776, 5226926),  # Intron 1
    (5226032, 5226493),  # Intron 2
]

for intron_start, intron_end in introns:
    # Count reads spanning intron (should be spliced)
    spliced = 0
    retained = 0

    for read in bam.fetch('chr11', intron_start, intron_end):
        if 'N' in read.cigarstring:  # Has splice junction
            spliced += 1
        else:  # Continuous read (intron retention)
            retained += 1

    psi = retained / (retained + spliced) if (retained + spliced) > 0 else 0
    print(f"Intron {intron_start}-{intron_end}: PSI={psi:.2%} (retained/total)")
```

**Expected for "Loop That Stayed":**

- WT: PSI < 5% (normal splicing)
- Mutant with stable loop + disrupted enhancer: PSI > 20% (aberrant)

---

## 📊 Validation Metrics

### Hi-C Validation Success Criteria

| Metric         | Threshold | Interpretation                                   |
| -------------- | --------- | ------------------------------------------------ |
| **Pearson R²** | > 0.7     | ARCHCODE accurately predicts contact frequencies |
| **Spearman ρ** | > 0.65    | Rank-order correlation (topology correct)        |
| **SSIM**       | > 0.85    | Structural similarity (loop positions match)     |

### RNA-seq Discovery Criteria

| Feature              | Evidence                         | Hypothesis Support               |
| -------------------- | -------------------------------- | -------------------------------- |
| **Intron retention** | PSI > 15% in stable loop regions | ✅ Supports "trapped transcript" |
| **Cryptic splice**   | Novel junctions within loop      | ✅ Supports enhancer disruption  |
| **Exon skipping**    | Low inclusion (PSI < 50%)        | ⚠️ Alternative mechanism         |

---

## 🎯 Possible Outcomes

### 🟢 Best Case: Validation + Discovery

- **Hi-C:** R² > 0.7 (model validated)
- **RNA-seq:** Aberrant splicing detected in predicted regions
- **Integration:** Correlation between loop stability and splicing defects
- **Manuscript:** "Experimental Validation of Loop-Constrained Pathogenicity"
- **Target:** Nature Genetics / Cell

### 🟡 Validation Only

- **Hi-C:** R² > 0.7 (model works)
- **RNA-seq:** No clear splicing pattern
- **Manuscript:** "ARCHCODE: Validated Framework for 3D Chromatin Simulation"
- **Target:** Nature Methods / Genome Biology

### 🔴 Validation Fails

- **Hi-C:** R² < 0.5 (model needs work)
- **Action:** Calibrate parameters, improve physics
- **Manuscript:** Delayed (fix model first)

---

## 📝 Scripts to Create (Priority Order)

### 1. `extract_hic_hbb_locus.py` (TODAY)

Extract HBB region from .hic file using hicstraw

### 2. `simulate_wt_hbb_validation.ts` (TODAY)

Run ARCHCODE WT simulation matching Hi-C resolution

### 3. `compare_hic_archcode.py` (TODAY)

Calculate correlation, generate validation plots

### 4. `process_rnaseq_splicing.sh` (TOMORROW)

STAR alignment + rMATS splice detection

### 5. `integrate_structure_function.py` (DAY 3)

Overlay Hi-C contacts with RNA-seq splicing efficiency

---

## 🛡️ CLAUDE.md Compliance

All work follows scientific integrity protocol:

✅ **Real experimental data** — HUDEP2 Hi-C (GEO GSE160422)
✅ **Ground truth validation** — Model vs Reality (not Model vs Model)
✅ **Reproducible** — Public datasets, code in GitHub
✅ **Transparent** — Document if validation fails

---

## 🚀 EXECUTE NOW (Day 1 Checklist)

### Morning Tasks:

- [ ] Install hicstraw: `pip install hic-straw`
- [ ] Create `scripts/extract_hic_hbb_locus.py`
- [ ] Extract WT-HUDEP2 contacts for chr11:5.2-5.25 Mb
- [ ] Verify matrix shape and resolution

### Afternoon Tasks:

- [ ] Create `scripts/simulate_wt_hbb_validation.ts`
- [ ] Run ARCHCODE WT simulation (matching resolution)
- [ ] Save contact matrix as .npy

### Evening Tasks:

- [ ] Create `scripts/compare_hic_archcode.py`
- [ ] Calculate R², Spearman ρ, SSIM
- [ ] Generate side-by-side heatmaps
- [ ] **Decision:** If R² > 0.5 → proceed to RNA-seq

---

## 💬 Communication

**Daily stand-up in this file:**

```markdown
### Day 1 Progress (2026-02-05)

- Completed: Hi-C extraction (R²=0.72)
- Next: RNA-seq splicing analysis
- Blockers: None
```

**Git commits:**

```bash
git commit -m "data: extract HUDEP2 Hi-C HBB locus (real ground truth)"
git commit -m "validate: ARCHCODE vs Hi-C correlation R²=0.72"
```

---

## 📚 References (Real Data Sources)

**Hi-C Data:**

- GEO Accession: GSE160422
- Paper: "3D genome organization of erythroid cells" (cite if published)
- Cells: HUDEP2 (human erythroid progenitors)

**RNA-seq Data:**

- GEO Accession: GSE131055
- Paper: "Transcriptome profiling in HBB variants"

**Validation Approach:**

- Hi-C validation: Compare simulated vs experimental contact matrices
- RNA-seq validation: Detect aberrant splicing in stable loop regions

---

**Project Lead:** Sergey Boyko
**AI Assistant:** Claude Sonnet 4.5 (CLAUDE.md compliant)
**Start:** 2026-02-05 (TODAY)
**Target:** bioRxiv submission 2026-02-08 (Day 3-4)

---

_"A model validated against reality beats a thousand model comparisons."_
— Adaptation of George Box: "All models are wrong, some are useful"
