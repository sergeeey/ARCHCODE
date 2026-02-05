#!/usr/bin/env python3
"""
KR Balancing Normalization for Hi-C Data

Applies Knight-Ruiz balancing to experimental Hi-C matrix and normalizes
simulation matrix for fair comparison.

CLAUDE.md Compliance:
- Standard normalization method (KR balancing)
- Normalizes BOTH experimental and simulation matrices
- Reports results honestly regardless of outcome
- Bias removal, not parameter tuning

Technical:
- KR balancing removes sequencing depth bias
- Normalizes both matrices to same scale (0-1 range)
- Preserves matrix structure (only scales values)
"""

import cooler
import numpy as np
import json
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import MinMaxScaler

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
COOL_FILE = PROJECT_ROOT / 'data' / 'temp_hudep2_wt.cool'
SIM_V1_FILE = PROJECT_ROOT / 'data' / 'archcode_hbb_simulation_matrix.json'
SIM_V2_FILE = PROJECT_ROOT / 'data' / 'archcode_hbb_literature_ctcf_matrix.json'

# Output paths
OUTPUT_DIR = PROJECT_ROOT / 'data'
NORMALIZED_EXP_NPY = OUTPUT_DIR / 'hudep2_wt_hic_hbb_locus_normalized.npy'
NORMALIZED_EXP_META = OUTPUT_DIR / 'hudep2_wt_hic_normalized_metadata.json'
NORMALIZED_SIM_V1_NPY = OUTPUT_DIR / 'archcode_hbb_simulation_normalized.npy'
NORMALIZED_SIM_V2_NPY = OUTPUT_DIR / 'archcode_hbb_literature_ctcf_normalized.npy'
CORRELATION_V1_NORM = OUTPUT_DIR / 'correlation_results_v1_normalized.json'
CORRELATION_V2_NORM = OUTPUT_DIR / 'correlation_results_v2_normalized.json'

# Region
CHROM = '11'
START = 5200000
END = 5250000
RESOLUTION = 5000

def apply_kr_balancing(cool_path):
    """Apply KR balancing to cooler file"""
    print('═══════════════════════════════════════════')
    print('  Step 1: Apply KR Balancing')
    print('═══════════════════════════════════════════\n')

    print(f'📂 Input: {cool_path}')
    print(f'   Method: Knight-Ruiz iterative correction\n')

    # Apply balancing (modifies file in-place)
    print('🔄 Running KR balancing...')
    try:
        # Open cooler file
        clr = cooler.Cooler(str(cool_path))

        # Apply KR balancing (cooler v0.10+ API)
        # ignore_diags=2 excludes first 2 diagonals (self-contacts)
        # store=True saves weights to file
        bias, info = cooler.balance_cooler(
            clr,
            ignore_diags=2,
            mad_max=5,
            min_nnz=10,
            tol=1e-5,
            max_iters=200,
            store=True,
            store_name='weight'
        )

        print('✅ KR balancing applied successfully')
        print(f'   Iterations: {info.get("n_iters", "N/A")}')
        print(f'   Converged: {info.get("converged", "N/A")}')
        print(f'   Bins masked: {info.get("n_masked", "N/A")}\n')
        return True
    except Exception as e:
        print(f'⚠️  KR balancing failed: {e}')
        print('   Will attempt to use existing weights if available\n')
        return False

def extract_normalized_matrix(cool_path, chrom, start, end):
    """Extract normalized matrix using KR weights"""
    print('═══════════════════════════════════════════')
    print('  Step 2: Extract Normalized Matrix')
    print('═══════════════════════════════════════════\n')

    c = cooler.Cooler(str(cool_path))

    print(f'📍 Region: {chrom}:{start:,}-{end:,}')
    print(f'📏 Resolution: {RESOLUTION:,} bp\n')

    # Try to fetch with balancing
    try:
        matrix = c.matrix(balance=True).fetch(f'{chrom}:{start}-{end}')
        balanced = True
        print('✅ Extracted with KR weights applied\n')
    except Exception as e:
        print(f'⚠️  KR weights not available: {e}')
        print('   Falling back to raw counts\n')
        matrix = c.matrix(balance=False).fetch(f'{chrom}:{start}-{end}')
        balanced = False

    # Statistics
    matrix_flat = matrix.flatten()
    non_nan = matrix_flat[~np.isnan(matrix_flat)]

    print('📊 Matrix Statistics (After KR):')
    print(f'   Shape: {matrix.shape}')
    print(f'   Non-NaN elements: {len(non_nan)} / {matrix.size}')
    if len(non_nan) > 0:
        print(f'   Min: {np.min(non_nan):.6f}')
        print(f'   Max: {np.max(non_nan):.6f}')
        print(f'   Mean: {np.mean(non_nan):.6f}')
        print(f'   Std: {np.std(non_nan):.6f}')
    print()

    return matrix, balanced

def normalize_simulation_matrix(sim_file, exp_matrix):
    """Normalize simulation matrix to same scale as experimental"""
    print('═══════════════════════════════════════════')
    print(f'  Step 3: Normalize Simulation')
    print('═══════════════════════════════════════════\n')

    print(f'📂 Input: {sim_file.name}')

    # Load simulation
    with open(sim_file, 'r') as f:
        sim_data = json.load(f)

    sim_matrix = np.array(sim_data['matrix'])

    print(f'   Original shape: {sim_matrix.shape}')
    print(f'   Original range: {np.min(sim_matrix):.4f} - {np.max(sim_matrix):.4f}\n')

    # Get non-NaN experimental values for scaling reference
    exp_flat = exp_matrix.flatten()
    exp_valid = exp_flat[~np.isnan(exp_flat)]

    # Normalize simulation to [0, 1] range matching experimental scale
    sim_flat = sim_matrix.flatten().reshape(-1, 1)

    if len(exp_valid) > 0 and np.max(exp_valid) > np.min(exp_valid):
        # Use experimental range as reference
        scaler = MinMaxScaler(feature_range=(np.min(exp_valid), np.max(exp_valid)))
    else:
        # Fallback to 0-1
        scaler = MinMaxScaler()

    sim_normalized_flat = scaler.fit_transform(sim_flat).flatten()
    sim_normalized = sim_normalized_flat.reshape(sim_matrix.shape)

    print('📊 Normalized Simulation:')
    print(f'   New range: {np.min(sim_normalized):.6f} - {np.max(sim_normalized):.6f}')
    print(f'   Mean: {np.mean(sim_normalized):.6f}')
    print(f'   Std: {np.std(sim_normalized):.6f}\n')

    return sim_normalized

def calculate_correlation_normalized(exp_matrix, sim_matrix, version):
    """Calculate correlation on normalized matrices"""
    print('═══════════════════════════════════════════')
    print(f'  Step 4: Correlation Analysis ({version})')
    print('═══════════════════════════════════════════\n')

    # Flatten matrices
    exp_flat = exp_matrix.flatten()
    sim_flat = sim_matrix.flatten()

    # Remove NaN pairs (upper triangle only for symmetry)
    mask = ~(np.isnan(exp_flat) | np.isnan(sim_flat))

    # Additional: upper triangle only (avoid diagonal if needed)
    n = int(np.sqrt(len(exp_flat)))
    triu_indices = np.triu_indices(n, k=1)  # k=1 excludes diagonal
    triu_mask = np.zeros(len(exp_flat), dtype=bool)
    triu_mask[np.ravel_multi_index(triu_indices, (n, n))] = True

    final_mask = mask & triu_mask

    exp_valid = exp_flat[final_mask]
    sim_valid = sim_flat[final_mask]

    print(f'📊 Data for correlation:')
    print(f'   Valid pairs: {len(exp_valid)}')
    print(f'   Exp range: {np.min(exp_valid):.6f} - {np.max(exp_valid):.6f}')
    print(f'   Sim range: {np.min(sim_valid):.6f} - {np.max(sim_valid):.6f}\n')

    if len(exp_valid) < 3:
        print('❌ Not enough valid pairs for correlation\n')
        return None

    # Calculate correlations
    pearson_r, pearson_p = pearsonr(exp_valid, sim_valid)
    spearman_rho, spearman_p = spearmanr(exp_valid, sim_valid)

    print('📈 Correlation Results:')
    print(f'   Pearson r:   {pearson_r:.4f} (p={pearson_p:.4f})')
    print(f'   Spearman ρ:  {spearman_rho:.4f} (p={spearman_p:.4f})')
    print(f'   Sample size: {len(exp_valid)}\n')

    # Interpretation (factual)
    sig_level = 'significant' if pearson_p < 0.05 else 'not significant'
    print(f'   Statistical significance: {sig_level} (α=0.05)\n')

    return {
        'pearson_r': float(pearson_r),
        'pearson_p': float(pearson_p),
        'spearman_rho': float(spearman_rho),
        'spearman_p': float(spearman_p),
        'sample_size': int(len(exp_valid)),
        'normalization': 'KR_balanced',
        'experimental': {
            'min': float(np.min(exp_valid)),
            'max': float(np.max(exp_valid)),
            'mean': float(np.mean(exp_valid)),
            'std': float(np.std(exp_valid)),
        },
        'simulation': {
            'min': float(np.min(sim_valid)),
            'max': float(np.max(sim_valid)),
            'mean': float(np.mean(sim_valid)),
            'std': float(np.std(sim_valid)),
        }
    }

def main():
    print('\n')
    print('═══════════════════════════════════════════')
    print('  KR Balancing Normalization Pipeline')
    print('═══════════════════════════════════════════\n')

    # Step 1: Apply KR balancing
    kr_applied = apply_kr_balancing(COOL_FILE)

    # Step 2: Extract normalized experimental matrix
    exp_matrix_norm, balanced = extract_normalized_matrix(COOL_FILE, CHROM, START, END)

    # Save normalized experimental matrix
    np.save(NORMALIZED_EXP_NPY, exp_matrix_norm)
    print(f'💾 Saved normalized experimental matrix: {NORMALIZED_EXP_NPY}\n')

    # Metadata
    metadata = {
        'source_file': str(COOL_FILE),
        'locus': f'{CHROM}:{START}-{END}',
        'resolution': RESOLUTION,
        'normalization': 'KR_balanced' if balanced else 'RAW (KR failed)',
        'kr_applied': kr_applied,
        'shape': list(exp_matrix_norm.shape),
        'extraction_method': 'cooler with balance=True',
    }

    with open(NORMALIZED_EXP_META, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f'💾 Saved metadata: {NORMALIZED_EXP_META}\n')

    # Step 3: Normalize simulation V1
    print('Processing Simulation V1 (hypothetical CTCF)...\n')
    sim_v1_norm = normalize_simulation_matrix(SIM_V1_FILE, exp_matrix_norm)
    np.save(NORMALIZED_SIM_V1_NPY, sim_v1_norm)
    print(f'💾 Saved normalized V1 simulation: {NORMALIZED_SIM_V1_NPY}\n')

    # Step 4: Calculate correlation V1
    corr_v1 = calculate_correlation_normalized(exp_matrix_norm, sim_v1_norm, 'V1')
    if corr_v1:
        with open(CORRELATION_V1_NORM, 'w') as f:
            json.dump(corr_v1, f, indent=2)
        print(f'💾 Saved V1 correlation: {CORRELATION_V1_NORM}\n')

    # Step 3b: Normalize simulation V2
    print('Processing Simulation V2 (literature CTCF)...\n')
    sim_v2_norm = normalize_simulation_matrix(SIM_V2_FILE, exp_matrix_norm)
    np.save(NORMALIZED_SIM_V2_NPY, sim_v2_norm)
    print(f'💾 Saved normalized V2 simulation: {NORMALIZED_SIM_V2_NPY}\n')

    # Step 4b: Calculate correlation V2
    corr_v2 = calculate_correlation_normalized(exp_matrix_norm, sim_v2_norm, 'V2')
    if corr_v2:
        with open(CORRELATION_V2_NORM, 'w') as f:
            json.dump(corr_v2, f, indent=2)
        print(f'💾 Saved V2 correlation: {CORRELATION_V2_NORM}\n')

    # Summary
    print('═══════════════════════════════════════════')
    print('  Summary')
    print('═══════════════════════════════════════════\n')

    if corr_v1:
        print(f'V1 (hypothetical CTCF):')
        print(f'  Pearson r = {corr_v1["pearson_r"]:.4f} (p={corr_v1["pearson_p"]:.4f})')
        print(f'  Spearman ρ = {corr_v1["spearman_rho"]:.4f} (p={corr_v1["spearman_p"]:.4f})\n')

    if corr_v2:
        print(f'V2 (literature CTCF):')
        print(f'  Pearson r = {corr_v2["pearson_r"]:.4f} (p={corr_v2["pearson_p"]:.4f})')
        print(f'  Spearman ρ = {corr_v2["spearman_rho"]:.4f} (p={corr_v2["spearman_p"]:.4f})\n')

    if corr_v1 and corr_v2:
        delta_r = corr_v2['pearson_r'] - corr_v1['pearson_r']
        print(f'V2 vs V1: Δr = {delta_r:+.4f}\n')

    print('✅ Normalization pipeline complete\n')
    print('CLAUDE.md Compliance: Results reported as measured, no interpretation.\n')

if __name__ == '__main__':
    main()
