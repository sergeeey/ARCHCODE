# FASTQ Download Plan — Вечер после 19:00

**Дата:** 2026-02-05
**Статус:** ⏰ ЗАПЛАНИРОВАНО на вечер (после 19:00)
**Интернет:** Дома (быстрый) ✅
**Время:** 4-6 часов download (можно оставить на ночь)

---

## 🎯 Цель

Скачать RNA-seq FASTQ файлы для splice junction анализа HBB locus:

- WT rep1 (baseline)
- D3 (-36% HBB) — ожидаем высокий aberrant splicing
- A2 (+28% HBB) — ожидаем нормальный сплайсинг

**Гипотеза:** Loop disruption (D3) → aberrant splicing 15-30%

---

## 📋 Pre-Flight Checklist

### 1. Проверить Dependencies

```bash
# Check if sra-toolkit installed
fastq-dump --version
# Если нет: conda install -c bioconda sra-toolkit

# Check disk space (need ~35 GB free)
df -h D:\

# Check Python/conda environment
python --version
which star  # STAR aligner (установим если нет)
```

### 2. Создать Рабочую Директорию

```bash
cd D:\ДНК
mkdir -p fastq_data/raw
mkdir -p fastq_data/aligned
mkdir -p fastq_data/junctions
```

---

## 🚀 Step 1: Download FASTQ Files (4-6 hours)

### SRA Accessions

| Sample  | SRA ID          | Clone          | HBB CPM       | Expected Aberrant % |
| ------- | --------------- | -------------- | ------------- | ------------------- |
| WT rep1 | **SRR12837671** | WT             | 10,886        | <5% (baseline)      |
| D3      | **SRR12837674** | 3'HS1 deleted  | 6,947 (-36%)  | 15-30% (high) ⚠️    |
| A2      | **SRR12837675** | 3'HS1 inverted | 13,978 (+28%) | <10% (low)          |

### Commands (Copy-Paste Ready)

```bash
# Navigate to working directory
cd D:\ДНК\fastq_data\raw

# Download WT rep1 (baseline)
echo "Downloading WT rep1 (SRR12837671)..."
fastq-dump --split-files --gzip SRR12837671

# Download D3 (biggest reduction)
echo "Downloading D3 (SRR12837674)..."
fastq-dump --split-files --gzip SRR12837674

# Download A2 (biggest elevation)
echo "Downloading A2 (SRR12837675)..."
fastq-dump --split-files --gzip SRR12837675

echo "Download complete! Check file sizes:"
ls -lh
```

**Expected output:**

```
SRR12837671_1.fastq.gz  (~5 GB)
SRR12837671_2.fastq.gz  (~5 GB)
SRR12837674_1.fastq.gz  (~5 GB)
SRR12837674_2.fastq.gz  (~5 GB)
SRR12837675_1.fastq.gz  (~5 GB)
SRR12837675_2.fastq.gz  (~5 GB)
Total: ~30 GB
```

### Alternative: Faster Download with prefetch

```bash
# If fastq-dump is slow, use prefetch first
prefetch SRR12837671 SRR12837674 SRR12837675

# Then convert to FASTQ
fastq-dump --split-files --gzip SRR12837671
fastq-dump --split-files --gzip SRR12837674
fastq-dump --split-files --gzip SRR12837675
```

### Monitor Progress

```bash
# In another terminal, watch disk usage
watch -n 60 'du -sh D:\ДНК\fastq_data\raw'

# Check download speed
du -sh D:\ДНК\fastq_data\raw  # Run every 5 minutes
```

---

## 🧬 Step 2: Quick QC (Optional, 15 min)

```bash
# Check number of reads
zcat SRR12837671_1.fastq.gz | wc -l
# Divide by 4 to get read count (expect ~30-50 million)

# Check read length
zcat SRR12837671_1.fastq.gz | head -2 | tail -1
# Expect: 100-150 bp paired-end reads
```

---

## 🔬 Step 3: STAR Alignment (12 hours, run overnight)

### Install STAR (if needed)

```bash
conda install -c bioconda star
# OR download from: https://github.com/alexdobin/STAR/releases
```

### Get Reference Genome Index

```bash
# Check if hg38 STAR index exists
ls D:\ДНК\reference\hg38_star_index/

# If NOT exist, download pre-built index (25 GB)
cd D:\ДНК\reference
wget https://ftp.ensembl.org/pub/release-110/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz

# OR use existing chr11.fa.gz and build index (1 hour)
STAR --runMode genomeGenerate \
     --genomeDir hg38_star_index \
     --genomeFastaFiles chr11.fa.gz \
     --runThreadN 8
```

### Alignment Commands (Run Overnight)

```bash
cd D:\ДНК\fastq_data

# Align WT rep1
STAR --genomeDir ../reference/hg38_star_index \
     --readFilesIn raw/SRR12837671_1.fastq.gz raw/SRR12837671_2.fastq.gz \
     --readFilesCommand zcat \
     --outFileNamePrefix aligned/WT_rep1_ \
     --outSAMtype BAM SortedByCoordinate \
     --runThreadN 8 \
     --outFilterMultimapNmax 1 \
     --outSJfilterReads Unique

# Align D3
STAR --genomeDir ../reference/hg38_star_index \
     --readFilesIn raw/SRR12837674_1.fastq.gz raw/SRR12837674_2.fastq.gz \
     --readFilesCommand zcat \
     --outFileNamePrefix aligned/D3_ \
     --outSAMtype BAM SortedByCoordinate \
     --runThreadN 8 \
     --outFilterMultimapNmax 1 \
     --outSJfilterReads Unique

# Align A2
STAR --genomeDir ../reference/hg38_star_index \
     --readFilesIn raw/SRR12837675_1.fastq.gz raw/SRR12837675_2.fastq.gz \
     --readFilesCommand zcat \
     --outFileNamePrefix aligned/A2_ \
     --outSAMtype BAM SortedByCoordinate \
     --runThreadN 8 \
     --outFilterMultimapNmax 1 \
     --outSJfilterReads Unique

echo "Alignment complete! Check output:"
ls -lh aligned/
```

**Expected output files:**

```
aligned/WT_rep1_Aligned.sortedByCoord.out.bam  (~3 GB)
aligned/WT_rep1_SJ.out.tab                      (~5 MB) ← SPLICE JUNCTIONS
aligned/WT_rep1_Log.final.out                   (stats)

aligned/D3_Aligned.sortedByCoord.out.bam
aligned/D3_SJ.out.tab                           ← KEY FILE for D3
aligned/D3_Log.final.out

aligned/A2_Aligned.sortedByCoord.out.bam
aligned/A2_SJ.out.tab                           ← KEY FILE for A2
aligned/A2_Log.final.out
```

---

## 📊 Step 4: Extract HBB Splice Junctions (Tomorrow Morning)

### Filter SJ.out.tab for HBB Locus

**HBB gene:** chr11:5,225,464-5,227,079 (GRCh38)

**Canonical junctions:**

- Exon 1→2: chr11:5,225,726 → 5,226,405
- Exon 2→3: chr11:5,226,626 → 5,227,079

```bash
cd D:\ДНК\fastq_data\junctions

# Extract HBB junctions from WT
awk '$1=="11" && $2>=5225000 && $3<=5228000' ../aligned/WT_rep1_SJ.out.tab > WT_rep1_HBB_junctions.txt

# Extract HBB junctions from D3
awk '$1=="11" && $2>=5225000 && $3<=5228000' ../aligned/D3_SJ.out.tab > D3_HBB_junctions.txt

# Extract HBB junctions from A2
awk '$1=="11" && $2>=5225000 && $3<=5228000' ../aligned/A2_SJ.out.tab > A2_HBB_junctions.txt

echo "HBB junctions extracted. Top 10:"
head -10 WT_rep1_HBB_junctions.txt
```

### Python Analysis Script (Copy-Paste Ready)

```python
# analyze_hbb_junctions.py
import pandas as pd

# Canonical junction coordinates (GRCh38)
CANONICAL_JUNCTIONS = {
    'exon1_2': (5225726, 5226405),
    'exon2_3': (5226626, 5227079)
}

def load_junctions(file):
    """Load STAR SJ.out.tab file"""
    cols = ['chr', 'start', 'end', 'strand', 'motif', 'annotated',
            'unique_reads', 'multimap_reads', 'max_overhang']
    df = pd.read_csv(file, sep='\t', names=cols)
    return df

def classify_junction(row):
    """Classify as canonical or aberrant"""
    start, end = row['start'], row['end']

    # Check if matches canonical junctions
    if (start, end) in CANONICAL_JUNCTIONS.values():
        return 'canonical'
    else:
        return 'aberrant'

def analyze_sample(name, file):
    """Analyze splice junctions for one sample"""
    df = load_junctions(file)
    df['type'] = df.apply(classify_junction, axis=1)

    canonical_reads = df[df['type']=='canonical']['unique_reads'].sum()
    aberrant_reads = df[df['type']=='aberrant']['unique_reads'].sum()
    total_reads = canonical_reads + aberrant_reads

    aberrant_pct = (aberrant_reads / total_reads * 100) if total_reads > 0 else 0

    print(f"\n{name}:")
    print(f"  Canonical reads: {canonical_reads:,}")
    print(f"  Aberrant reads:  {aberrant_reads:,}")
    print(f"  Aberrant %:      {aberrant_pct:.2f}%")

    return {
        'sample': name,
        'canonical': canonical_reads,
        'aberrant': aberrant_reads,
        'aberrant_pct': aberrant_pct
    }

# Analyze all samples
results = []
results.append(analyze_sample('WT rep1', 'WT_rep1_HBB_junctions.txt'))
results.append(analyze_sample('D3', 'D3_HBB_junctions.txt'))
results.append(analyze_sample('A2', 'A2_HBB_junctions.txt'))

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv('HBB_aberrant_splicing_results.csv', index=False)
print("\nResults saved to HBB_aberrant_splicing_results.csv")
```

**Run:**

```bash
cd D:\ДНК\fastq_data\junctions
python analyze_hbb_junctions.py
```

---

## ✅ Expected Results

### Hypothesis Predictions

| Sample      | HBB Expression    | Aberrant Splicing %                 | Interpretation                |
| ----------- | ----------------- | ----------------------------------- | ----------------------------- |
| **WT rep1** | 10,886 CPM        | <5%                                 | Normal baseline               |
| **D3**      | 6,947 CPM (-36%)  | **15-30%** if hypothesis correct ✅ | Loop trap → aberrant splicing |
| **A2**      | 13,978 CPM (+28%) | <10%                                | Transcriptional upregulation  |

### Success Criteria

✅ **If D3 shows >15% aberrant splicing:**

- Validates "Loop That Stayed" hypothesis
- Functional validation STRONG (compensates for weak Hi-C r=0.16)
- Manuscript upgrade: Pilot study → Validated mechanism

❌ **If D3 shows <5% aberrant splicing:**

- Rejects "Loop That Stayed" (alternative mechanism)
- Expression change is transcriptional, not splicing-related
- Still valuable negative result (honest reporting)

---

## 📝 Documentation (Tomorrow)

### Create Results Document

```bash
cd D:\ДНК
# Create SPLICE_JUNCTION_RESULTS.md with findings
```

**Include:**

1. Aberrant splicing % for WT, D3, A2
2. Top 5 aberrant junctions in D3 (coordinates, read counts)
3. Correlation: HBB expression change vs aberrant splicing %
4. Figure: Bar plot (aberrant % by sample)
5. Interpretation: Validates or rejects hypothesis

---

## ⏰ Timeline

**Tonight (19:00-23:00):**

- ✅ Download FASTQ (4-6 hours) — **можно оставить на ночь**
- ✅ Start STAR alignment (runs overnight)

**Tomorrow morning:**

- ✅ Check alignment logs
- ✅ Extract HBB junctions (30 min)
- ✅ Run Python analysis (10 min)
- ✅ Create results document (1 hour)

**Total:** 1-2 days from start to final results

---

## 🚨 Troubleshooting

### If fastq-dump is slow:

```bash
# Use parallel-fastq-dump (faster)
conda install -c bioconda parallel-fastq-dump
parallel-fastq-dump --split-files --gzip --threads 4 --sra-id SRR12837671
```

### If STAR fails (not enough RAM):

```bash
# Use --limitBAMsortRAM parameter
STAR --genomeDir hg38_star_index \
     --readFilesIn raw/SRR12837671_1.fastq.gz raw/SRR12837671_2.fastq.gz \
     --limitBAMsortRAM 10000000000  # 10 GB
```

### If no STAR index:

```bash
# Use chr11 only (faster, smaller)
STAR --runMode genomeGenerate \
     --genomeDir chr11_star_index \
     --genomeFastaFiles ../reference/chr11.fa.gz \
     --genomeSAindexNbases 12 \
     --runThreadN 8
```

---

## 📌 Files to Check Tomorrow

**Key output files:**

1. `fastq_data/aligned/D3_SJ.out.tab` — D3 splice junctions (most important)
2. `fastq_data/aligned/WT_rep1_SJ.out.tab` — Baseline
3. `fastq_data/aligned/A2_SJ.out.tab` — Comparison
4. `fastq_data/junctions/HBB_aberrant_splicing_results.csv` — Final results

**Success check:**

```bash
# Check if alignment finished
tail fastq_data/aligned/D3_Log.final.out

# Look for:
# "Uniquely mapped reads number" — should be >20 million
# "% of reads mapped to multiple loci" — should be <10%
```

---

## 🎯 Next Session (Tomorrow)

**If aberrant splicing analysis complete:**

1. Correlate Hi-C loop disruption vs aberrant splicing %
2. Create Figure 5 (4-panel: Hi-C + Expression + Splicing + Correlation)
3. Update manuscript Discussion section
4. Commit results with timestamp

**Commands for tomorrow:**

```bash
cd D:\ДНК
claude "Review FASTQ alignment results and create splice junction analysis summary"
```

---

**Status:** ⏰ READY TO START после 19:00 (дома, быстрый интернет)

**First command to run tonight:**

```bash
cd D:\ДНК\fastq_data\raw
fastq-dump --split-files --gzip SRR12837671 SRR12837674 SRR12837675
```

Оставить на ночь. Утром проверить размер файлов (~30 GB total).

---

_FASTQ Download Plan_
_Created: 2026-02-05_
_Scheduled: Evening after 19:00_
_Expected completion: Tomorrow morning_
