# Installing SRA Toolkit on Windows (For Tonight)

**Status:** ⚠️ conda installation failed (package not available for win-64)
**Solution:** Download pre-built Windows binaries from NCBI

---

## Option 1: Pre-built Binaries (Recommended, 5 minutes)

### Download

**Official link:** https://github.com/ncbi/sra-tools/wiki/01.-Downloading-SRA-Toolkit

**Direct download (Windows 64-bit):**
https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-win64.zip

**Expected size:** ~150 MB

### Installation Steps

```bash
# 1. Download (можно через браузер или wget)
cd D:\ДНК\tools
wget https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-win64.zip

# 2. Unzip
unzip sratoolkit.current-win64.zip

# 3. Add to PATH (временно, для этой сессии)
export PATH=$PATH:D:/ДНК/tools/sratoolkit.3.X.X-win64/bin

# 4. Test
fastq-dump --version
# Should output: fastq-dump : 3.X.X

# 5. Configure (one-time)
vdb-config --interactive
# Press 'X' to exit (default settings are fine)
```

### Quick Test

```bash
# Test download tiny sample (SRR000001, 1 MB)
fastq-dump --stdout -X 5 SRR000001
# Should output 5 reads in FASTQ format
```

**If successful → Ready for tonight's download!**

---

## Option 2: Use WSL (If Already Installed)

If Windows Subsystem for Linux (WSL) is available:

```bash
# Check if WSL exists
wsl --version

# If yes, use conda in WSL
wsl
conda install -y -c bioconda sra-tools
fastq-dump --version

# Download in WSL, files accessible at /mnt/d/ДНК/
```

**Check WSL:**
```bash
wsl echo "WSL available" || echo "WSL not installed"
```

---

## Option 3: Alternative Downloader (fasterq-dump)

**fasterq-dump** is newer and faster than fastq-dump.

If pre-built binaries include it:
```bash
# Use fasterq-dump instead (same syntax)
fasterq-dump --split-files SRR12837671

# Advantages:
# - 2-3× faster than fastq-dump
# - Better multi-threading
# - Same output format
```

---

## Option 4: Aspera Download (Fastest, Advanced)

If you need maximum speed (10× faster):

**Install Aspera Connect:**
https://www.ibm.com/aspera/connect/

**Download command:**
```bash
ascp -QT -l 300m -P33001 \
  -i ~/.aspera/connect/etc/asperaweb_id_dsa.openssh \
  anonftp@ftp.ncbi.nlm.nih.gov:/sra/sra-instant/reads/ByRun/sra/SRR/SRR128/SRR12837671/SRR12837671.sra \
  ./

# Convert SRA to FASTQ
fastq-dump --split-files SRR12837671.sra
```

**Speed comparison:**
- fastq-dump: 4-6 hours (HTTP)
- fasterq-dump: 2-3 hours (HTTP)
- Aspera: 30-60 minutes (UDP, high-speed)

---

## Recommended for Tonight

**Use Option 1 (Pre-built binaries):**
1. Download sratoolkit ZIP (5 min)
2. Unzip and add to PATH (2 min)
3. Test with small sample (1 min)
4. Run full download command (leave overnight)

**Total setup time:** <10 minutes

---

## Tonight's Command (Once SRA Toolkit Installed)

```bash
# Navigate to target directory
cd D:\ДНК\fastq_data\raw

# Download 3 samples (WT, D3, A2)
fastq-dump --split-files --gzip SRR12837671 &  # WT rep1
fastq-dump --split-files --gzip SRR12837674 &  # D3
fastq-dump --split-files --gzip SRR12837675 &  # A2

# Check progress
ls -lh

# Expected output (after 4-6 hours):
# SRR12837671_1.fastq.gz  (~5 GB)
# SRR12837671_2.fastq.gz  (~5 GB)
# SRR12837674_1.fastq.gz  (~5 GB)
# SRR12837674_2.fastq.gz  (~5 GB)
# SRR12837675_1.fastq.gz  (~5 GB)
# SRR12837675_2.fastq.gz  (~5 GB)
# Total: ~30 GB
```

---

## Troubleshooting

### Error: "Failed to resolve hostname"
**Solution:** Check internet connection, try again

### Error: "Path not found"
**Solution:**
```bash
cd D:\ДНК\fastq_data\raw  # Correct path
pwd  # Verify current directory
```

### Error: "Insufficient disk space"
**Check available space:**
```bash
df -h D:\ДНК
# Need: 50+ GB free
# Have: 155 GB free ✅
```

### Slow download speed
**Switch to fasterq-dump:**
```bash
fasterq-dump --split-files SRR12837671
# Then compress manually:
gzip SRR12837671_1.fastq SRR12837671_2.fastq
```

---

## Alternative: Direct Browser Download

If command-line fails, download via browser:

**SRA Run Selector:**
https://www.ncbi.nlm.nih.gov/Traces/study/?acc=SRP290306

**Steps:**
1. Select samples: SRR12837671, SRR12837674, SRR12837675
2. Click "Download" → "FASTQ files"
3. Save to D:\ДНК\fastq_data\raw\

**Note:** Browser download may be slower (no parallel downloads)

---

## Checklist for Tonight

Before starting download:
- [ ] SRA Toolkit installed (`fastq-dump --version` works)
- [ ] Directory exists: `D:\ДНК\fastq_data\raw`
- [ ] 155 GB free space confirmed
- [ ] Internet connection stable (home network)
- [ ] Command copied to clipboard

**Estimated time:** 4-6 hours (can leave overnight)

---

*Installation Guide for SRA Toolkit*
*Created: 2026-02-05*
*Status: conda failed → use pre-built binaries instead*
