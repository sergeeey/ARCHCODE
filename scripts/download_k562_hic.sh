#!/bin/bash
# Download K562 Hi-C/Micro-C data + ChIP-seq peaks for ARCHCODE validation
#
# ПОЧЕМУ K562: HBB expressed in erythroid cells. K562 = erythroleukemia cell line
# with active HBB locus. GM12878 (lymphoblastoid) gave r=0.16 — expected low
# because HBB is not expressed in B-cells.
#
# Sources:
#   1. 4DN K562 Hi-C mcool — multi-resolution, ready to use with cooler
#   2. GSE206131 K562 Micro-C pairs (Barshad 2024, eLife) — highest resolution
#   3. ENCODE CTCF K562 peaks (ENCFF660GHM) — for parameter calibration
#   4. ENCODE MED1 K562 peaks (ENCFF882ZEN) — for enhancer validation
#
# Usage: bash scripts/download_k562_hic.sh [--all|--hic|--chipseq|--microc]

set -euo pipefail

DATA_DIR="data/reference"
mkdir -p "$DATA_DIR"

MODE="${1:---all}"

echo "=========================================="
echo "  ARCHCODE: K562 Hi-C Data Download"
echo "=========================================="
echo ""

# --- 1. 4DN K562 Hi-C mcool (7.92 GB, multi-resolution) ---
download_hic() {
    local FILE="$DATA_DIR/4DNFI18UHVRO.mcool"
    local URL="https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/230ad652-0232-47f2-97ef-296c7a040bd9/4DNFI18UHVRO.mcool"

    if [ -f "$FILE" ]; then
        local SIZE=$(stat -c%s "$FILE" 2>/dev/null || stat -f%z "$FILE" 2>/dev/null || echo 0)
        echo "[OK] 4DNFI18UHVRO.mcool already exists ($(numfmt --to=iec $SIZE 2>/dev/null || echo "${SIZE} bytes"))"
    else
        echo "Downloading 4DN K562 Hi-C mcool (~7.92 GB)..."
        echo "  Source: 4DN Data Portal (Experiment 4DNEX9UZVLI1)"
        echo "  Cell line: K562 (human erythroleukemia)"
        echo "  This will take 10-30 minutes depending on connection speed."
        echo ""
        wget -c -O "$FILE" "$URL" || curl -L -C - -o "$FILE" "$URL"
        echo "  Saved: $FILE"
    fi
}

# --- 2. GSE206131 K562 Micro-C pairs (Barshad 2024, eLife) ---
download_microc() {
    local FILE="$DATA_DIR/GSE206131_K562_cis_mapq30_pairs.txt.gz"
    local URL="https://ftp.ncbi.nlm.nih.gov/geo/series/GSE206nnn/GSE206131/suppl/GSE206131_K562_cis_mapq30_pairs.txt.gz"

    if [ -f "$FILE" ]; then
        echo "[OK] GSE206131 Micro-C pairs already exists"
    else
        echo "Downloading GSE206131 K562 Micro-C pairs (~10-20 GB)..."
        echo "  Source: Barshad et al. 2024, eLife (GSE206131)"
        echo "  Resolution: nucleosome-level (~150bp)"
        echo ""
        wget -c -O "$FILE" "$URL" || curl -L -C - -o "$FILE" "$URL"
        echo "  Saved: $FILE"
    fi
}

# --- 3. CTCF K562 peaks (ENCODE, IDR narrowPeak, hg38) ---
download_chipseq() {
    local CTCF_FILE="$DATA_DIR/K562_CTCF_peaks.bed.gz"
    local CTCF_URL="https://www.encodeproject.org/files/ENCFF660GHM/@@download/ENCFF660GHM.bed.gz"

    local MED1_FILE="$DATA_DIR/K562_MED1_peaks.bed.gz"
    local MED1_URL="https://www.encodeproject.org/files/ENCFF882ZEN/@@download/ENCFF882ZEN.bed.gz"

    if [ -f "$CTCF_FILE" ]; then
        echo "[OK] K562_CTCF_peaks.bed.gz already exists"
    else
        echo "Downloading CTCF K562 peaks (ENCFF660GHM)..."
        wget -q -O "$CTCF_FILE" "$CTCF_URL" || curl -sL -o "$CTCF_FILE" "$CTCF_URL"
        echo "  Saved: $CTCF_FILE"
    fi

    if [ -f "$MED1_FILE" ]; then
        echo "[OK] K562_MED1_peaks.bed.gz already exists"
    else
        echo "Downloading MED1 K562 peaks (ENCFF882ZEN)..."
        wget -q -O "$MED1_FILE" "$MED1_URL" || curl -sL -o "$MED1_FILE" "$MED1_URL"
        echo "  Saved: $MED1_FILE"
    fi
}

# Dispatch
case "$MODE" in
    --all)
        download_chipseq
        download_hic
        download_microc
        ;;
    --hic)
        download_hic
        ;;
    --microc)
        download_microc
        ;;
    --chipseq)
        download_chipseq
        ;;
    *)
        echo "Usage: $0 [--all|--hic|--chipseq|--microc]"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  Download complete!"
echo "=========================================="
echo ""
echo "Files in $DATA_DIR:"
ls -lh "$DATA_DIR"/ 2>/dev/null
echo ""
echo "Next steps:"
echo "  python scripts/extract_k562_hbb.py    # Extract HBB region from mcool"
echo "  python scripts/correlate_hic_archcode.py  # Compare with ARCHCODE simulation"
