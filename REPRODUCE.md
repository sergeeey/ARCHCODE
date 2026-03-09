# ARCHCODE — Reproducibility Guide

**Manuscript:** "Enhancer-Proximal ClinVar Variants Show Tissue-Dependent Structural Disruption
Across Nine Genomic Loci"
**bioRxiv ID:** BIORXIV/2026/710343
**Last verified:** 2026-03-09

All paths below are relative to the project root (wherever you cloned the repository).
On Windows the root is `D:\ДНК`; on Linux/macOS it will be wherever you `git clone` to.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | Tested on 3.11.x |
| Node.js | 20+ | Required for the physics simulator |
| npm | bundled with Node.js | |
| git | any modern | |

---

## 1. Python Dependencies

Install all analysis dependencies into a virtual environment:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements-analysis.txt
```

The packages installed and why each is needed:

| Package | Used by |
|---------|---------|
| `numpy` | array operations, distance calculations |
| `scipy` | Mann-Whitney U tests (`scipy.stats.mannwhitneyu`, `spearmanr`) |
| `pandas` | CSV I/O, DataFrame operations |
| `matplotlib` | figure generation (Analyses 1 and 3) |
| `scikit-learn` | `normalized_mutual_info_score` (Analyses 1 and 3) |
| `requests` | data-fetch helper scripts (not the five analyses below) |

---

## 2. Node.js Build (Physics Simulator)

The ARCHCODE loop-extrusion simulator is a TypeScript/React application. The Python analysis
scripts consume its pre-computed CSV outputs; you do not need to rebuild it to reproduce the
five analyses. However, to verify the simulator from source:

```bash
npm install
npm run build   # runs: tsc && vite build
npm test        # runs: vitest run (unit + regression suite)
```

Coverage gate (enforced in CI):

```bash
npm run test:coverage
# lines >= 60%, functions >= 60%, statements >= 60%, branches >= 55%
```

Docker alternative (no local Node.js needed):

```bash
docker build -t archcode .
docker run archcode npm test
```

---

## 3. Input Data

All nine locus atlas files must exist before running any analysis script.

### CSV Atlas Files (simulator outputs)

Location: `results/`

| File | Locus | Window |
|------|-------|--------|
| `HBB_Unified_Atlas_95kb.csv` | HBB | 95 kb sub-TAD |
| `BRCA1_Unified_Atlas_400kb.csv` | BRCA1 | 400 kb |
| `TP53_Unified_Atlas_300kb.csv` | TP53 | 300 kb |
| `CFTR_Unified_Atlas_317kb.csv` | CFTR | 317 kb |
| `MLH1_Unified_Atlas_300kb.csv` | MLH1 | 300 kb |
| `LDLR_Unified_Atlas_300kb.csv` | LDLR | 300 kb |
| `SCN5A_Unified_Atlas_400kb.csv` | SCN5A | 400 kb |
| `TERT_Unified_Atlas_300kb.csv` | TERT | 300 kb |
| `GJB2_Unified_Atlas_300kb.csv` | GJB2 | 300 kb |

Each file has columns including: `ClinVar_ID`, `Position_GRCh38`, `Ref`, `Alt`, `HGVS_c`,
`HGVS_p`, `Category`, `ClinVar_Significance`, `ARCHCODE_LSSIM`, `VEP_Score`, `CADD_Phred`,
`VEP_Consequence`.

### CADD Supplement for TERT

Location: `results/cadd_scores_TERT.csv`
Columns: `ClinVar_ID`, `CADD_Phred`
Source: CADD v1.7 — https://cadd.gs.washington.edu/ (GRCh38)
Accession: download via `scripts/fetch_cadd_scores.py` using CADD REST API.

### Locus Config Files (JSON)

Location: `config/locus/`

| File | Locus |
|------|-------|
| `hbb_95kb_subTAD.json` | HBB |
| `brca1_400kb.json` | BRCA1 |
| `tp53_300kb.json` | TP53 |
| `cftr_317kb.json` | CFTR |
| `mlh1_300kb.json` | MLH1 |
| `ldlr_300kb.json` | LDLR |
| `scn5a_400kb.json` | SCN5A |
| `tert_300kb.json` | TERT |
| `gjb2_300kb.json` | GJB2 |

Each JSON encodes genomic features:
```json
{
  "features": {
    "enhancers": [{"position": 5246696, ...}],
    "ctcf_sites": [{"position": 5248029, ...}]
  }
}
```

### External Data Sources

| Dataset | Source | Accession / URL |
|---------|--------|-----------------|
| ClinVar variants | NCBI ClinVar | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/ |
| VEP scores | Ensembl VEP REST API | https://rest.ensembl.org/vep/human/hgvs |
| CADD scores | CADD v1.7 | https://cadd.gs.washington.edu/score |
| Hi-C (K562, GM12878) | GEO | GSE63525 |
| ABC model predictions | Engreitz Lab | https://www.engreitzlab.org/resources/ |
| ChIP-seq CTCF (K562) | ENCODE | ENCSR000DFA |

---

## 4. Output Directory

All five analyses write to `analysis/`. Create it if absent:

```bash
mkdir -p analysis
```

---

## Analysis 1 — Q2a/Q2b Split (Discordance Taxonomy)

**What it does:** Loads all nine locus atlas CSVs, assigns each variant to Q1–Q4 (2×2 matrix
of ARCHCODE_HIGH vs SEQ_HIGH), then splits Q2 into:
- Q2a: VEP coverage gap (VEP_Score == -1, tool could not score)
- Q2b: True structural blind spots (VEP scored 0–0.5, ARCHCODE sees disruption)

Also computes per-locus Normalized Mutual Information (NMI) between ARCHCODE and VEP/CADD.

**Command:**
```bash
python scripts/discordance_v2_split.py
```

**Inputs:**
- `results/*_Unified_Atlas_*.csv` (9 files)
- `config/locus/*.json` (9 files)

**Outputs:**

| File | Description |
|------|-------------|
| `analysis/Q2b_true_blindspots.csv` | All Q2b variants with annotations, sorted by LSSIM ascending |
| `analysis/Q2b_top20_manuscript.csv` | Top-20 most disrupted Q2b variants (manuscript Table 2) |
| `analysis/nmi_per_locus.csv` | Per-locus NMI between ARCHCODE, VEP, and CADD |
| `analysis/DISCORDANCE_REPORT_v2.md` | Full statistical narrative with GO/NO-GO table |

**Verification:**

```bash
python - <<'EOF'
import pandas as pd
q2b = pd.read_csv("analysis/Q2b_true_blindspots.csv")
nmi  = pd.read_csv("analysis/nmi_per_locus.csv")
print(f"Q2b variants: {len(q2b)}")           # expect 54
hbb_nmi = nmi.loc[nmi['Locus'] == 'HBB', 'NMI_ARCH_VEP_valid'].values[0]
print(f"HBB NMI (valid VEP): {hbb_nmi}")    # expect ~0.49
EOF
```

Expected counts: Q2b = 54 variants, Q2a = 207 variants (printed to stdout during run).
HBB NMI should be the highest across all loci (~0.49); all others should be < 0.05.

---

## Analysis 2 — TERT Validation (Second Locus GO/NO-GO)

**What it does:** Reproduces the Q1–Q4 framework on TERT alone, merging the supplementary
CADD file for higher coverage. Applies three GO criteria and outputs a verdict JSON.

**Command:**
```bash
python scripts/tert_validation.py
```

**Inputs:**
- `results/TERT_Unified_Atlas_300kb.csv`
- `results/cadd_scores_TERT.csv`
- `config/locus/tert_300kb.json`

**Outputs:**

| File | Description |
|------|-------------|
| `analysis/TERT_validation.csv` | Full TERT variant table with Q assignments and distances |
| `analysis/TERT_validation_summary.json` | Key metrics + GO/NO-GO verdict |

**Verification:**

```bash
python - <<'EOF'
import json
with open("analysis/TERT_validation_summary.json") as f:
    s = json.load(f)
print(f"N_Q2:      {s['n_q2']}")                          # expect 35
print(f"p-value:   {s['p_mannwhitney_q2_lt_q3']}")        # expect < 0.01
print(f"Verdict:   {s['verdict']}")                        # expect GO or CONDITIONAL GO
EOF
```

Expected: N_Q2 = 35, Mann-Whitney p < 0.01, verdict contains "GO".

---

## Analysis 3 — Enhancer Distance Test (2x2 Matrix + Figures)

**What it does:** Builds the full cross-locus 2×2 discordance matrix, tests whether Q2 variants
are significantly closer to enhancers than Q3 variants (Mann-Whitney, one-sided), computes
tissue-specificity Spearman correlation, and generates all manuscript figures (fig1–fig4).

**Command:**
```bash
python scripts/discordance_analysis.py
```

**Inputs:**
- `results/*_Unified_Atlas_*.csv` (9 files, same as Analysis 1)
- `config/locus/*.json` (9 files)

**Outputs:**

| File | Description |
|------|-------------|
| `analysis/discordance_2x2_matrix.csv` | Q1–Q4 counts and precision per locus |
| `analysis/discordance_by_locus.csv` | Per-locus Q distribution with enhancer distances |
| `analysis/fig1-fig4/` | PDF/PNG figures for manuscript |

**Verification:**

```bash
python - <<'EOF'
import pandas as pd, scipy.stats as st
mat = pd.read_csv("analysis/discordance_by_locus.csv")
q2_dist = mat.loc[mat['Q'] == 'Q2', 'Mean_Enhancer_Dist_bp']
q3_dist = mat.loc[mat['Q'] == 'Q3', 'Mean_Enhancer_Dist_bp']
_, p = st.mannwhitneyu(q2_dist, q3_dist, alternative='less')
print(f"Q2 mean: {q2_dist.mean():.0f} bp")
print(f"Q3 mean: {q3_dist.mean():.0f} bp")
print(f"p-value: {p:.2e}")   # expect < 0.01
EOF
```

Expected: Q2 mean enhancer distance < Q3 mean enhancer distance, p < 0.01.

---

## Analysis 4 — Per-Locus NMI (Orthogonality)

**What it does:** Demonstrates that ARCHCODE and VEP/CADD capture orthogonal axes of
pathogenicity. Computed as part of Analysis 1 (no separate script needed).

**Command:** see Analysis 1 above — `nmi_per_locus.csv` is produced in the same run.

**Output:** `analysis/nmi_per_locus.csv`

**Verification:**

```bash
python - <<'EOF'
import pandas as pd
nmi = pd.read_csv("analysis/nmi_per_locus.csv")
print(nmi[['Locus', 'NMI_ARCH_VEP_all', 'NMI_ARCH_VEP_valid']].to_string(index=False))
# HBB should have the highest NMI_ARCH_VEP_valid (~0.49)
# All other loci should be < 0.05 (low NMI = orthogonal signals)
EOF
```

Expected: HBB NMI_ARCH_VEP_valid ~0.49 (highest), all others < 0.05.
This confirms that the two tools do not overlap in what they detect.

---

## Analysis 5 — External Validation Overlays (ABC, PCHi-C, CRISPRi)

**What it does:** Cross-references Q2b variants with three public functional genomics datasets
to assess overlap with experimentally characterized regulatory elements.

### 5a. ABC/rE2G Enhancer Overlay

**Command:**
```bash
python scripts/abc_model_overlay.py
```

**Data source:** ENCODE rE2G enhancer–gene predictions (ENCSR627ANP, K562 DNase-seq).
File: `ENCFF976OKL.bed.gz` (auto-downloaded from ENCODE portal).

**Outputs:**
- `analysis/abc_q2b_overlap.csv` — per-variant enhancer overlap
- `analysis/abc_q2b_summary.json` — Fisher exact test (Q2b vs Q3 enrichment)

**Expected result:** 68% Q2b overlap vs 61% Q3 (Fisher p = 0.36, NS). Both groups are in
enhancer-rich regions; no differential Q2b enrichment. 20 HBB-linked enhancer regions identified.

### 5b. Promoter Capture Hi-C (Erythroblast)

**Data source:** Javierre et al. 2016 (Cell), E-MTAB-2323.
File: `PCHiC_peak_matrix_cutoff5.txt.gz` from https://osf.io/download/63hh4/ (~100 MB).

**Outputs:**
- `analysis/pchic_hbb_all_celltypes.tsv` — filtered HBB interactions across 17 cell types
- `analysis/pchic_q2b_overlap.json` — Q2b overlap analysis

**Expected result:** 25/46 HBB interactions significant in erythroblasts (CHiCAGO > 5).
Q2b positions (5,226,596–5,227,172) fall upstream of capture bait (5,243,047–5,268,365).
Erythroblast-specific HBB–LCR loop confirmed (CHiCAGO up to 10.5).

### 5c. CRISPRi K562 Screen

**Data source:** Gasperini et al. 2019 (Cell), GSE120861.

**Outputs:**
- `analysis/crispri_k562_hbb.json` — CRISPRi elements near HBB
- `analysis/crispri_q2b_overlap.json` — overlap analysis

**Expected result:** 65 CRISPRi elements tested near HBB; zero overlap with Q2b positions
within 500 bp. Q2b variants remain experimentally unvalidated.

---

## Quick Sanity Check (All Analyses)

After running all analyses, verify key output files exist:

```bash
python - <<'EOF'
from pathlib import Path
expected = [
    "analysis/Q2b_true_blindspots.csv",
    "analysis/Q2b_top20_manuscript.csv",
    "analysis/nmi_per_locus.csv",
    "analysis/DISCORDANCE_REPORT_v2.md",
    "analysis/TERT_validation.csv",
    "analysis/TERT_validation_summary.json",
    "analysis/discordance_2x2_matrix.csv",
    "analysis/discordance_by_locus.csv",
    "analysis/per_locus_verdict.csv",
    "analysis/abc_q2b_summary.json",
    "analysis/pchic_q2b_overlap.json",
    "analysis/crispri_q2b_overlap.json",
]
for p in expected:
    status = "OK" if Path(p).exists() else "MISSING"
    print(f"  [{status}] {p}")
EOF
```

**Checksums:** verify data integrity against `checksums.sha256`:
```bash
sha256sum -c checksums.sha256
```

---

## Integrity Notes

All data in `results/` is real ClinVar+VEP+CADD data, not synthetic.
Synthetic/mock files (if any) carry the prefix `MOCK_` or `SYNTHETIC_` per project policy
(see `CLAUDE.md`).

Parameters in analysis scripts are labeled in comments as MANUALLY CALIBRATED (e.g.,
`LSSIM_THRESHOLD = 0.95`, `CADD_THRESHOLD = 20`) rather than "fitted", because no automated
fitting procedure was run on these thresholds — they were set from published literature ranges.
