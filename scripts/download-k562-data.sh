#!/bin/bash
# Download K562 BigWig files from ENCODE for Cross-Cell Validation
#
# Usage: ./scripts/download-k562-data.sh

set -e

DATA_DIR="data/inputs"
MED1_DIR="$DATA_DIR/med1"
HISTONE_DIR="$DATA_DIR/histone"

# Create directories
mkdir -p "$MED1_DIR" "$HISTONE_DIR"

echo "=========================================="
echo "  ARCHCODE: Downloading K562 Data"
echo "=========================================="
echo ""

# H3K27ac K562 (hg38) - ENCSR000AKP
# Signal p-value bigWig file
H3K27AC_URL="https://www.encodeproject.org/files/ENCFF038HNR/@@download/ENCFF038HNR.bigWig"
H3K27AC_FILE="$HISTONE_DIR/H3K27ac_K562.bw"

if [ -f "$H3K27AC_FILE" ]; then
    echo "[OK] H3K27ac_K562.bw already exists"
else
    echo "Downloading H3K27ac K562..."
    echo "  Source: ENCSR000AKP (Bradley Bernstein, Broad)"
    wget -q --show-progress "$H3K27AC_URL" -O "$H3K27AC_FILE" || \
    curl -L "$H3K27AC_URL" -o "$H3K27AC_FILE"
    echo "  Saved: $H3K27AC_FILE"
fi

# MED1 K562 (hg38) - ENCSR269BSA
# Note: Check the experiment page for the correct file accession
# https://www.encodeproject.org/experiments/ENCSR269BSA/
MED1_URL="https://www.encodeproject.org/files/ENCFF341MYG/@@download/ENCFF341MYG.bigWig"
MED1_FILE="$MED1_DIR/MED1_K562.bw"

if [ -f "$MED1_FILE" ]; then
    echo "[OK] MED1_K562.bw already exists"
else
    echo "Downloading MED1 K562..."
    echo "  Source: ENCSR269BSA (Richard Myers, HAIB)"
    wget -q --show-progress "$MED1_URL" -O "$MED1_FILE" || \
    curl -L "$MED1_URL" -o "$MED1_FILE"
    echo "  Saved: $MED1_FILE"
fi

echo ""
echo "=========================================="
echo "  Download complete!"
echo "=========================================="
echo ""
echo "Files:"
ls -lh "$HISTONE_DIR"/*.bw 2>/dev/null || echo "  (no histone files)"
ls -lh "$MED1_DIR"/*.bw 2>/dev/null || echo "  (no MED1 files)"
echo ""
echo "Run validation:"
echo "  npx tsx scripts/run-cross-cell-k562.ts"
