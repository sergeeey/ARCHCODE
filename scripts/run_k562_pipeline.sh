#!/bin/bash
# Run complete K562 Hi-C pipeline: extract + correlate
#
# Prerequisite: 4DNFI18UHVRO.mcool must be fully downloaded.
# Check: ls -lh data/reference/4DNFI18UHVRO.mcool  (should be ~7.9 GB)
#
# Usage: bash scripts/run_k562_pipeline.sh

set -euo pipefail

MCOOL="data/reference/4DNFI18UHVRO.mcool"
EXPECTED_SIZE=7900000000  # ~7.9 GB

echo "=========================================="
echo "  ARCHCODE: K562 Hi-C Pipeline"
echo "=========================================="

# Check mcool exists and is complete
if [ ! -f "$MCOOL" ]; then
    echo "ERROR: $MCOOL not found."
    echo "Run: bash scripts/download_k562_hic.sh --hic"
    exit 1
fi

ACTUAL_SIZE=$(stat -c%s "$MCOOL" 2>/dev/null || stat -f%z "$MCOOL" 2>/dev/null || echo 0)
if [ "$ACTUAL_SIZE" -lt "$EXPECTED_SIZE" ]; then
    echo "WARNING: $MCOOL appears incomplete"
    echo "  Expected: ~7.9 GB"
    echo "  Actual:   $(numfmt --to=iec $ACTUAL_SIZE 2>/dev/null || echo "$ACTUAL_SIZE bytes")"
    echo "  Download may still be in progress."
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "--- Step 1: Extract HBB region from mcool ---"
python scripts/extract_k562_hbb.py

echo ""
echo "--- Step 2: Correlate with ARCHCODE simulation ---"
python scripts/correlate_hic_archcode.py

echo ""
echo "=========================================="
echo "  Pipeline complete!"
echo "=========================================="
echo "  Results: results/hic_correlation_k562.json"
