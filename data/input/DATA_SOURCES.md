# ARCHCODE-SV Data Provenance

All files in `data/input/` are downloaded from public sources. No synthetic or mock data.

## gnomAD v2.1.1 constraint

**File:** `gnomad_constraint.json` (19,658 genes, pLI + LOEUF)

**Source URL:**
```
https://storage.googleapis.com/gcp-public-data--gnomad/release/2.1.1/constraint/gnomad.v2.1.1.lof_metrics.by_gene.txt.bgz
```

**Reference:** Karczewski et al. 2020 Nature. DOI: 10.1038/s41586-020-2308-7

**Download date:** 2026-06-26

**Format:** JSON dict keyed by gene symbol: `{"GENE": {"pLI": float, "LOEUF": float}}`

---

## GENCODE v47 protein-coding gene coordinates

**File:** `gencode_genes_chr2_7_17.json` (3,368 genes on chr2/chr7/chr17)

**Source URL:**
```
https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_47/gencode.v47.basic.annotation.gtf.gz
```

**Reference:** GENCODE Consortium. Release 47 (GRCh38/hg38).

**Download date:** 2026-06-26

**Filter:** protein_coding genes, chromosomes chr2/chr7/chr17 only

**Format:** JSON list: `[{"chrom": str, "start": int, "end": int, "gene": str}]`

---

## ENCODE K562 CTCF IDR peaks (hg38)

**File:** `ctcf/K562_CTCF_hg38.bed` (46,160 IDR peaks)

**ENCODE accession:** ENCFF736NYC

**Source URL:**
```
https://www.encodeproject.org/files/ENCFF736NYC/@@download/ENCFF736NYC.bed.gz
```

**Reference:** ENCODE Project Consortium. K562 cell line, CTCF ChIP-seq, IDR thresholded peaks, GRCh38.

**Download date:** 2026-06-24

**Format:** BED narrowPeak, column 7 = signalValue (used as CTCF occupancy score)

**Key sites verified:**
- SOX9 TAD boundary: chr17:70622593 (score=53.5)
- SHH TAD boundary: chr7:156909069 (score=314.6)
- ATG4B separator: chr2:241702758 (score=58.3) — confirmed TAD barrier
- KANSL1 separator: chr17:46254004 (score=126.0) — confirmed TAD barrier

---

## ClinVar SVs (validation dataset)

**File:** `experiments/exp_archcode_sv/clinvar_results.json` (n=50)

**Source:** ClinVar variant_summary.txt.gz (NCBI FTP)

```
https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz
```

**Downloaded:** 2026-06-26

**Filter criteria:**
- Chromosomes: chr2, chr7, chr17
- Size: 50-400 kb (deletion or inversion)
- ClinicalSignificance: "Pathogenic" or "Likely pathogenic" (25 SVs) OR "Benign" or "Likely benign" (25 SVs)
- Excluded: VUS, conflicting, risk factor, uncertain significance
- Assembly: GRCh38/hg38

**No synthetic data.** All SVs have real ClinVar accessions (RCV/VCV).

---

## Reproducibility note

All thresholds in Step +2 were **calibrated on the same n=50 ClinVar dataset** used for
performance evaluation. The reported FPR=8% / Recall=68% is in-sample performance.

External validation on an independent cohort (DECIPHER, gnomAD-SV) is required
before clinical use. See Paper 3 §3.7 for full discussion of limitations.
