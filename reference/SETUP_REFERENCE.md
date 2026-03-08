# 🧬 Reference Genome Setup for RNA-seq

## Required Files

For STAR alignment, you need:

1. **Human reference genome (hg38/GRCh38)**
2. **Gene annotation (GTF)**
3. **STAR index**

---

## Option 1: Download from GENCODE (Recommended)

### Step 1: Create directory structure

```bash
mkdir D:\ДНК\reference\hg38
cd D:\ДНК\reference\hg38
```

### Step 2: Download reference genome

**FASTA (genome sequence):**
```bash
# Download from GENCODE
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.primary_assembly.genome.fa.gz

# Or use Ensembl
wget ftp://ftp.ensembl.org/pub/release-107/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
```

### Step 3: Download gene annotation

**GTF (gene models):**
```bash
# GENCODE GTF
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.primary_assembly.annotation.gtf.gz

# Or Ensembl GTF
wget ftp://ftp.ensembl.org/pub/release-107/gtf/homo_sapiens/Homo_sapiens.GRCh38.107.gtf.gz
```

### Step 4: Generate STAR index

```bash
# Decompress files
gunzip GRCh38.primary_assembly.genome.fa.gz
gunzip gencode.v44.primary_assembly.annotation.gtf.gz

# Create STAR index directory
mkdir star_index

# Generate index (takes ~30-60 min, requires ~30 GB RAM)
STAR --runThreadN 8 \
     --runMode genomeGenerate \
     --genomeDir star_index \
     --genomeFastaFiles GRCh38.primary_assembly.genome.fa \
     --sjdbGTFfile gencode.v44.primary_assembly.annotation.gtf \
     --sjdbOverhang 149 \
     --limitGenomeGenerateRAM 31000000000
```

---

## Option 2: Use Existing Reference (If Available)

If you already have hg38 reference from another project:

```bash
# Copy existing reference
cp /path/to/existing/hg38.fa D:\ДНК\reference\hg38\
cp /path/to/existing/hg38.gtf D:\ДНК\reference\hg38\

# Generate STAR index
STAR --runThreadN 8 \
     --runMode genomeGenerate \
     --genomeDir D:\ДНК\reference\hg38\star_index \
     --genomeFastaFiles D:\ДНК\reference\hg38\hg38.fa \
     --sjdbGTFfile D:\ДНК\reference\hg38\hg38.gtf \
     --sjdbOverhang 149
```

---

## Option 3: Quick Test (No Reference)

For testing the pipeline without full alignment:

**Use pseudo-alignment (Kallisto/Salmon)** — faster, less disk space:

```bash
# Install Kallisto
conda install -c bioconda kallisto

# Build index (much faster than STAR)
kallisto index -i hg38_kallisto.idx GRCh38.primary_assembly.genome.fa

# Run quantification
kallisto quant -i hg38_kallisto.idx -o output/ \
    -b 100 \
    fastq_data/raw/SRR12935486_1.fastq.gz \
    fastq_data/raw/SRR12935486_2.fastq.gz
```

**Note:** Kallisto doesn't produce splice junctions, so use STAR for full analysis.

---

## File Sizes (Expected)

| File | Size |
|------|------|
| FASTA (genome) | ~3 GB |
| GTF (annotation) | ~1 GB |
| STAR index | ~30 GB |
| Total | ~34 GB |

---

## Download Scripts

Automated download script: `scripts/download_reference.sh` (coming soon)

---

## Verification

After setup, verify:

```bash
# Check files exist
ls -lh D:\ДНК\reference\hg38\*.fa
ls -lh D:\ДНК\reference\hg38\*.gtf
ls -lh D:\ДНК\reference\hg38\star_index\SA
```

If all files exist → **Ready for alignment!**

---

## Quick Start (Copy-Paste)

```bash
# 1. Create directory
mkdir D:\ДНК\reference\hg38
cd D:\ДНК\reference\hg38

# 2. Download (using wget or browser)
# Download FASTA and GTF from GENCODE or Ensembl

# 3. Generate STAR index
STAR --runThreadN 8 \
     --runMode genomeGenerate \
     --genomeDir star_index \
     --genomeFastaFiles Homo_sapiens.GRCh38.dna.primary_assembly.fa \
     --sjdbGTFfile Homo_sapiens.GRCh38.107.gtf \
     --sjdbOverhang 149

# 4. Run pipeline
cd D:\ДНК
python scripts\rnaseq_pipeline.py
```
