#!/bin/bash
# ARCHCODE FASTQ Download Script
# Purpose: Download RNA-seq data for "Loop That Stayed" validation
# Date: 2026-03-06
# 
# Usage: 
#   bash scripts/download_rnaseq_fastq.sh
#
# Samples:
#   WT Rep1: SRR12837671
#   D3 Rep1: SRR12837674 (3'HS1 deletion, expected: 15-30% aberrant splicing)
#   A2 Rep1: SRR12837675 (3'HS1 inversion, expected: <10% aberrant splicing)

set -e

echo "============================================================"
echo "  ARCHCODE RNA-seq FASTQ Download"
echo "  'Loop That Stayed' Hypothesis Validation"
echo "============================================================"
echo ""

# Create output directory
OUTPUT_DIR="D:/ДНК/fastq_data/raw"
mkdir -p "$OUTPUT_DIR"

echo "📁 Output directory: $OUTPUT_DIR"
echo ""

# Check if fastq-dump is available
if ! command -v fastq-dump &> /dev/null; then
    echo "❌ Error: fastq-dump not found."
    echo ""
    echo "Install SRA Toolkit:"
    echo "  - Windows: https://github.com/ncbi/sra-tools/wiki/01.-Downloading-SRA-Toolkit"
    echo "  - Or: conda install -c bioconda sra-tools"
    echo ""
    exit 1
fi

echo "✅ fastq-dump found: $(which fastq-dump)"
echo ""

# Download samples
echo "🚀 Starting download..."
echo ""
echo "Samples:"
echo "  1. SRR12837671 (WT Rep1)"
echo "  2. SRR12837674 (D3 Rep1 - 3'HS1 deletion)"
echo "  3. SRR12837675 (A2 Rep1 - 3'HS1 inversion)"
echo ""
echo "Expected size: ~30 GB total"
echo "Estimated time: 4-6 hours"
echo ""
echo "⏱️  Starting at: $(date)"
echo ""

# Download with progress
cd "$OUTPUT_DIR"

# Download each sample
for accession in SRR12837671 SRR12837674 SRR12837675; do
    echo "📥 Downloading $accession..."
    
    # Check if already downloaded
    if [ -f "${accession}_1.fastq.gz" ] && [ -f "${accession}_2.fastq.gz" ]; then
        echo "⚠️  Already exists, skipping..."
        continue
    fi
    
    # Download with split-files and gzip
    fastq-dump \
        --split-files \
        --gzip \
        --progress \
        --outdir "$OUTPUT_DIR" \
        "$accession"
    
    echo "✅ Completed: $accession"
    echo ""
done

echo ""
echo "============================================================"
echo "  Download Complete"
echo "============================================================"
echo ""
echo "⏱️  Finished at: $(date)"
echo ""
echo "📁 Output files:"
ls -lh "$OUTPUT_DIR"/*.fastq.gz 2>/dev/null || echo "  (checking files...)"
echo ""
echo "📊 Total size:"
du -sh "$OUTPUT_DIR" 2>/dev/null || echo "  (unable to calculate)"
echo ""
echo "✅ Next step: Run RNA-seq analysis pipeline"
echo "   See: fastq_data/README.md"
echo ""
