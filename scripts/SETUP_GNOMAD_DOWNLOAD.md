# gnomAD VCF Local Download — Complete Setup Guide

**Цель:** Скачать gnomAD v4.1 chr11 VCF локально для offline query (100% надёжность, 0% API timeouts)

**Estimated time:** 30-60 минут (зависит от скорости интернета)

---

## Шаг 0: Pre-flight Check (перед началом)

### Проверь disk space:

```bash
cd "D:/ДНК"
df -h .
```

**Требуется:**
- Full chr11 VCF: ~24GB compressed
- Extracted HBB region: ~500MB
- **Total needed: 25GB свободного места**

Если мало места → освободи или скачай на другой диск.

---

## Шаг 1: Download gnomAD chr11 VCF + Index

### Вариант A (рекомендован): Full download (24GB, ~32 мин на 100 Mbps)

```bash
cd "D:/ДНК/data"

# Download VCF (24GB compressed)
wget --no-check-certificate \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz \
  -O gnomad.genomes.v4.1.sites.chr11.vcf.bgz

# Download index (.tbi, ~127KB)
wget --no-check-certificate \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi \
  -O gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi
```

**Progress monitoring:**
```bash
# В другом терминале (пока качается):
watch -n 5 'ls -lh gnomad.genomes.v4.1.sites.chr11.vcf.bgz'
```

### Вариант B (альтернатива): Если wget нет

```bash
# Используй curl
curl -L -o gnomad.genomes.v4.1.sites.chr11.vcf.bgz \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz

curl -L -o gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi
```

---

## Шаг 2: Verify Download Integrity

```bash
# Check file size (должно быть ~24GB)
ls -lh gnomad.genomes.v4.1.sites.chr11.vcf.bgz

# Expected output:
# -rw-r--r-- 1 user 24G ... gnomad.genomes.v4.1.sites.chr11.vcf.bgz

# Check index size (должно быть ~127KB)
ls -lh gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi

# Expected output:
# -rw-r--r-- 1 user 127K ... gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi
```

Если размеры не совпадают → download corrupted, повтори.

---

## Шаг 3: Install Required Tools

### Option A: Install pysam (Python VCF parser)

```bash
# Activate conda environment (если есть)
conda activate ape311

# Install pysam
pip install pysam

# Verify installation
python -c "import pysam; print(f'pysam {pysam.__version__} installed')"
```

**Expected output:**
```
pysam 0.22.0 installed
```

### Option B: Если pysam install fails (Windows build issues)

```bash
# Install pre-compiled wheel
pip install pysam --only-binary :all:

# OR install conda version
conda install -c bioconda pysam
```

### Option C: Если всё ещё fails

Используй `bcftools` (alternative):

```bash
# Download bcftools for Windows
# https://github.com/samtools/bcftools/releases
# Extract to C:/bcftools/

# Add to PATH or use full path
C:/bcftools/bcftools.exe --version
```

---

## Шаг 4: Extract HBB Region (optional, для скорости)

Если хочешь работать только с HBB region (500MB вместо 24GB):

```bash
# Требует tabix (из htslib)
tabix gnomad.genomes.v4.1.sites.chr11.vcf.bgz 11:5225000-5230000 > gnomad_hbb_region.vcf

# Check extracted size
ls -lh gnomad_hbb_region.vcf
# Expected: ~500MB uncompressed
```

**Если tabix нет:**

Установи htslib:
```bash
conda install -c bioconda htslib

# OR download Windows binary:
# http://www.htslib.org/download/
```

---

## Шаг 5: Run Offline Query Script

```bash
cd "D:/ДНК"

# Run prepared query script (см. следующий файл)
python scripts/gnomad_offline_query.py
```

**Expected output:**
```
Loading VCF: gnomad.genomes.v4.1.sites.chr11.vcf.bgz
Querying 27 pearls...
[1/27] chr11:5226598 G>T: AC=0 (ABSENT)
[2/27] chr11:5226598 G>C: AC=1 (ULTRA_RARE)
...
✅ Results saved to: results/gnomad_pearls_offline_verified.csv

SUMMARY:
  ABSENT (AC=0): 18/27 (67%)
  ULTRA_RARE (AC=1-5): 7/27 (26%)
  PRESENT (AC>5): 2/27 (7%)
```

---

## Troubleshooting

### Download interrupted?

Resume download с wget:
```bash
wget --continue \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz
```

Resume с curl:
```bash
curl -C - -o gnomad.genomes.v4.1.sites.chr11.vcf.bgz \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz
```

### pysam import error?

```bash
# Check Python version (должно быть 3.8+)
python --version

# Reinstall with specific version
pip install pysam==0.21.0
```

### VCF corrupted?

```bash
# Test with bcftools
bcftools view -H gnomad.genomes.v4.1.sites.chr11.vcf.bgz | head -10

# If errors → re-download
```

---

## Estimated Times

| Internet Speed | Full Download | HBB Extract | Query Time |
|----------------|---------------|-------------|------------|
| 100 Mbps | 32 min | 2 min | 10 sec |
| 50 Mbps | 64 min | 2 min | 10 sec |
| 25 Mbps | 128 min | 2 min | 10 sec |
| 10 Mbps | 320 min (5.3 hrs) | 2 min | 10 sec |

**Рекомендация:** Запускай download вечером, пусть качается ночью.

---

## Next Steps After Download

1. ✅ VCF downloaded → Run `gnomad_offline_query.py`
2. ✅ CSV generated → Verify with `wc -l results/gnomad_pearls_offline_verified.csv`
3. ✅ Results verified → Update paper draft with real numbers
4. ✅ Paper updated → Submit to Bioinformatics

**Estimated total time from download start to paper submission: 2-3 hours.**

---

## Files This Setup Creates

```
D:/ДНК/
├── data/
│   ├── gnomad.genomes.v4.1.sites.chr11.vcf.bgz      (24GB)
│   ├── gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi  (127KB)
│   └── gnomad_hbb_region.vcf                        (500MB, optional)
├── results/
│   └── gnomad_pearls_offline_verified.csv           (2KB)
└── scripts/
    └── gnomad_offline_query.py                      (ready to run)
```

Total disk usage: ~25GB
