#!/usr/bin/env python3
"""
Extract mouse beta-globin Hi-C contact matrix from G1E-ER4 mcool file.

Source: 4DN 4DNFIB3Y8ECJ (G1E-ER4 in situ Hi-C, DpnII, mm10/GRCm38)
Experiment set: 4DNESWNF3Y23
Region: chr7:103,788,000-103,918,000 (130kb mouse Hbb sub-TAD)

Outputs:
  - results/mouse_hic_beta_globin.json (contact matrix + metadata)
  - figures/fig13_mouse_hic_validation.pdf/png (comparison figure)
"""

import json
import sys
from pathlib import Path

import cooler
import numpy as np

PROJECT = Path(__file__).parent.parent
MCOOL = PROJECT / "data" / "mouse" / "4DNFIB3Y8ECJ_G1E-ER4_HiC_mm10.mcool"
CONFIG = PROJECT / "config" / "locus" / "mouse_hbb_130kb.json"
OUT_JSON = PROJECT / "results" / "mouse_hic_beta_globin.json"

# Load mouse config
with open(CONFIG) as f:
    cfg = json.load(f)

chrom = cfg["window"]["chromosome"]
start = cfg["window"]["start"]
end = cfg["window"]["end"]
n_bins = cfg["window"]["n_bins"]
resolution_bp = cfg["window"]["resolution_bp"]

region = f"{chrom}:{start}-{end}"
print(f"Region: {region} ({(end-start)//1000}kb)")
print(f"Config resolution: {resolution_bp}bp, n_bins: {n_bins}")

# Find best resolution in mcool
print(f"\nLoading mcool: {MCOOL}")
print(f"File size: {MCOOL.stat().st_size / 1e9:.2f} GB")

# List available resolutions
resolutions = cooler.fileops.list_coolers(str(MCOOL))
print(f"Available resolutions: {resolutions}")

# Pick resolution closest to 600bp (our config resolution)
# Typical Hi-C resolutions: 1000, 2000, 5000, 10000, ...
# We'll use the finest available
res_values = []
for r in resolutions:
    try:
        val = int(r.split("/")[-1])
        res_values.append(val)
    except ValueError:
        pass

if not res_values:
    print("ERROR: No valid resolutions found in mcool")
    sys.exit(1)

res_values.sort()
print(f"Numeric resolutions: {res_values}")

# Use finest resolution available (but not finer than 1kb for reasonable matrix size)
best_res = None
for r in res_values:
    if r >= 1000:
        best_res = r
        break
if best_res is None:
    best_res = res_values[0]

print(f"\nUsing resolution: {best_res}bp")

# Load cooler at chosen resolution
clr = cooler.Cooler(f"{MCOOL}::resolutions/{best_res}")
print(f"Cooler info: {clr.info}")
print(f"Chromosomes: {list(clr.chromnames)[:5]}...")

# Extract matrix for beta-globin region
matrix = clr.matrix(balance=True).fetch(region)
print(f"\nRaw matrix shape: {matrix.shape}")
print(f"NaN fraction: {np.isnan(matrix).sum() / matrix.size:.3f}")

# Also get unbalanced (raw) matrix
matrix_raw = clr.matrix(balance=False).fetch(region)
print(f"Raw counts range: {np.nanmin(matrix_raw):.0f} - {np.nanmax(matrix_raw):.0f}")
print(f"Total contacts in region: {np.nansum(matrix_raw):.0f}")

# Replace NaN with 0 for balanced matrix
matrix_balanced = np.nan_to_num(matrix, nan=0.0)

# Normalize to [0, 1] range
max_val = np.nanmax(matrix_balanced)
if max_val > 0:
    matrix_norm = matrix_balanced / max_val
else:
    matrix_norm = matrix_balanced

print(f"Balanced matrix range: {matrix_norm.min():.4f} - {matrix_norm.max():.4f}")

# Bin coordinates
bins_start = np.arange(start, end, best_res)
bins_end = bins_start + best_res
actual_n_bins = matrix.shape[0]

# Resample to match config n_bins (217) if needed
if actual_n_bins != n_bins:
    print(f"\nResampling: {actual_n_bins} bins → {n_bins} bins")
    from scipy.ndimage import zoom
    zoom_factor = n_bins / actual_n_bins
    matrix_resampled = zoom(matrix_norm, zoom_factor, order=1)
    # Ensure symmetric
    matrix_resampled = (matrix_resampled + matrix_resampled.T) / 2
    np.fill_diagonal(matrix_resampled, np.diag(matrix_resampled))
    print(f"Resampled shape: {matrix_resampled.shape}")
else:
    matrix_resampled = matrix_norm

# Save results
result = {
    "source": "4DN 4DNFIB3Y8ECJ (G1E-ER4 in situ Hi-C, DpnII, mm10)",
    "experiment_set": "4DNESWNF3Y23",
    "cell_line": "G1E-ER4 (GATA1-restored mouse erythroleukemia)",
    "genome_assembly": "GRCm38/mm10",
    "region": region,
    "region_size_kb": (end - start) // 1000,
    "hic_resolution_bp": best_res,
    "config_resolution_bp": resolution_bp,
    "config_n_bins": n_bins,
    "actual_n_bins": actual_n_bins,
    "resampled_n_bins": matrix_resampled.shape[0],
    "total_contacts_raw": int(np.nansum(matrix_raw)),
    "nan_fraction": float(np.isnan(matrix).sum() / matrix.size),
    "matrix": matrix_resampled.tolist(),
    "matrix_raw_counts": matrix_raw.tolist() if actual_n_bins <= 300 else "too_large",
}

with open(OUT_JSON, "w") as f:
    json.dump(result, f, indent=2)
print(f"\nSaved: {OUT_JSON}")
print(f"Matrix dimensions: {matrix_resampled.shape[0]}x{matrix_resampled.shape[1]}")
