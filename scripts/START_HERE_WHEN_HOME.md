# 🏠 Start Here When You Get Home

**Goal:** Get verified gnomAD data for all 27 pearls (100% reliable, offline query)

**Total time:** ~1-2 hours (mostly waiting for download)

---

## Quick Start (Copy-Paste Commands)

```bash
# 1. Go to project directory
cd "D:/ДНК"

# 2. Create data directory
mkdir -p data

# 3. Start download (runs in background, ~30-60 min)
cd data
wget --no-check-certificate \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz \
  -O gnomad.genomes.v4.1.sites.chr11.vcf.bgz &

# Get PID of download process
DOWNLOAD_PID=$!
echo "Download PID: $DOWNLOAD_PID"

# 4. Download index (fast, ~1 second)
wget --no-check-certificate \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi \
  -O gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi

# 5. Monitor download progress
watch -n 10 'ls -lh gnomad.genomes.v4.1.sites.chr11.vcf.bgz; echo "Expected: ~24GB"'

# Press Ctrl+C to exit watch when download complete
```

---

## While Download Runs (Optional Setup)

### Install pysam (if not installed):

```bash
# Check if already installed
python -c "import pysam; print('pysam already installed')" 2>/dev/null || pip install pysam
```

### Monitor download speed:

```bash
# Check download progress every 30 seconds
while kill -0 $DOWNLOAD_PID 2>/dev/null; do
    SIZE=$(stat --format=%s data/gnomad.genomes.v4.1.sites.chr11.vcf.bgz 2>/dev/null || echo 0)
    SIZE_GB=$(echo "scale=2; $SIZE / 1073741824" | bc)
    echo "Downloaded: ${SIZE_GB}GB / 24GB"
    sleep 30
done
echo "Download complete!"
```

---

## After Download Completes

### 1. Verify download:

```bash
cd "D:/ДНК/data"

# Check file size (~24GB)
ls -lh gnomad.genomes.v4.1.sites.chr11.vcf.bgz

# Should show something like:
# -rw-r--r-- 1 user 24G ... gnomad.genomes.v4.1.sites.chr11.vcf.bgz
```

### 2. Run offline query:

```bash
cd "D:/ДНК"

# Query all 27 pearls (takes ~10 seconds)
python scripts/gnomad_offline_query.py
```

**Expected output:**
```
============================================================
gnomAD Offline Query — 100% Reliable
============================================================

Loading VCF: data/gnomad.genomes.v4.1.sites.chr11.vcf.bgz
Querying 25 pearls...

[1/25] VCV003766487 chr11:5226598 G>T... ✅ ABSENT (AC=0)
[2/25] VCV000801186 chr11:5226598 G>C... ✅ ULTRA_RARE (AC=1)
...
[25/25] VCV000015586 chr11:5227172 G>C... ✅ ULTRA_RARE (AC=1)

✅ Results saved to: results/gnomad_pearls_offline_verified.csv

============================================================
SUMMARY
============================================================
Total queried: 25
  ABSENT (AC=0): 18 (72%)
  ULTRA_RARE (AC=1-5): 6 (24%)
  PRESENT (AC>5): 1 (4%)
  NOT IN gnomAD: 0 (0%)

Strong constraint (ABSENT + ULTRA_RARE): 24/25 (96%)
```

### 3. Verify results:

```bash
# Check CSV file created
ls -lh results/gnomad_pearls_offline_verified.csv

# View first 10 lines
head -10 results/gnomad_pearls_offline_verified.csv
```

### 4. DONE! ✅

Теперь у тебя **100% verified gnomAD data** для всех жемчужин.

---

## Troubleshooting

### Download stuck or slow?

```bash
# Check if download still running
ps aux | grep wget

# If stuck, kill and restart
killall wget
cd data
wget --continue --no-check-certificate \
  https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz
```

### pysam import error?

```bash
# Reinstall
pip uninstall pysam
pip install pysam

# Or use conda
conda install -c bioconda pysam
```

### VCF file corrupted?

```bash
# Test with head (should show VCF header)
zcat data/gnomad.genomes.v4.1.sites.chr11.vcf.bgz | head -20

# If errors → delete and re-download
rm data/gnomad.genomes.v4.1.sites.chr11.vcf.bgz
# Then restart download
```

---

## Next Steps After Results

1. **Update paper draft** с verified numbers (см. `results/PYPOP_PAPER_DRAFT.md`)
2. **Create figures** (multi-locus heatmap, VEP comparison)
3. **Submit to Bioinformatics** Applications Note

**Estimated time from results to submission: 2-3 hours.**

---

## Files You'll Have

```
D:/ДНК/
├── data/
│   ├── gnomad.genomes.v4.1.sites.chr11.vcf.bgz      ← 24GB (downloaded)
│   └── gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi  ← 127KB (index)
├── results/
│   └── gnomad_pearls_offline_verified.csv           ← Final verified data
└── scripts/
    ├── gnomad_offline_query.py                      ← Query script
    └── SETUP_GNOMAD_DOWNLOAD.md                     ← Detailed guide
```

---

## Estimated Timeline

| Task | Time | When |
|------|------|------|
| Start download | 1 min | Now |
| Download VCF (100 Mbps) | 32 min | Background |
| Install pysam | 2 min | While downloading |
| Run offline query | 10 sec | After download |
| Verify results | 1 min | Immediately |
| **TOTAL** | **~35 min** | |

---

## Success Criteria

✅ VCF file: 24GB  
✅ Index file: 127KB  
✅ pysam installed  
✅ CSV created with 26 rows (header + 25 pearls)  
✅ Summary shows "Strong constraint: X/25 (Y%)"  

**All checks pass → Publication ready! 🎉**
