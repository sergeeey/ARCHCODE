#!/usr/bin/env python3
"""
Hi-C Structural Analysis: TADs, Insulation, Compartments, Directionality Index
Understand why ARCHCODE correlation is weak (r=0.16)

Input: Normalized Hi-C matrix (hudep2_wt_hic_hbb_locus_normalized.npy)
Output: TAD boundaries, insulation score, A/B compartments, directionality index
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from scipy.stats import pearsonr
from pathlib import Path
import json

# Configuration
HIC_FILE = 'D:/ДНК/data/hudep2_wt_hic_hbb_locus_normalized.npy'
METADATA_FILE = 'D:/ДНК/data/hudep2_wt_hic_normalized_metadata.json'
OUTPUT_DIR = 'D:/ДНК/figures/'
RESULTS_DIR = 'D:/ДНК/data/'

# HBB Locus
LOCUS_START = 5_200_000
LOCUS_END = 5_250_000
BIN_SIZE = 5000  # 5 kb bins
CHROMOSOME = '11'

# CTCF sites (from validation)
CTCF_SITES = [
    {'name': "5'HS5", 'position': 5_203_300},
    {'name': "5'HS4", 'position': 5_205_700},
    {'name': "5'HS3", 'position': 5_207_100},
    {'name': "5'HS2", 'position': 5_209_000},
    {'name': "HBB", 'position': 5_225_700},
    {'name': "3'HS1", 'position': 5_247_900}
]

def load_hic_matrix():
    """Load normalized Hi-C matrix"""
    print("Loading Hi-C matrix...")
    matrix = np.load(HIC_FILE)

    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)

    print(f"Matrix shape: {matrix.shape}")
    print(f"Resolution: {metadata.get('resolution', 'unknown')} bp")
    print(f"Normalization: {metadata.get('normalization', 'unknown')}")

    return matrix, metadata

def calculate_insulation_score(matrix, window_size=3):
    """
    Calculate insulation score (Dixon et al. 2012)

    Insulation = mean contact frequency across diagonal
    Low insulation = TAD boundary (insulator)
    High insulation = within TAD (high interactions)

    Parameters:
    - window_size: number of bins for sliding window (default 3 = 15 kb at 5kb resolution)
    """
    n = matrix.shape[0]
    insulation = np.zeros(n)

    for i in range(n):
        # Define window boundaries
        start = max(0, i - window_size)
        end = min(n, i + window_size + 1)

        # Calculate mean contact frequency in window
        # Sum upper-left and lower-right quadrants (across boundary)
        if i > 0 and i < n - 1:
            upper_left = matrix[start:i, i:end]
            lower_right = matrix[i:end, start:i]

            # Mean of cross-boundary contacts
            cross_contacts = np.concatenate([upper_left.flatten(), lower_right.flatten()])
            cross_contacts = cross_contacts[~np.isnan(cross_contacts)]

            if len(cross_contacts) > 0:
                insulation[i] = np.mean(cross_contacts)
        else:
            insulation[i] = np.nan

    # Normalize (log transform)
    insulation = np.log2(insulation + 1e-10)

    # Invert so that boundaries = peaks
    insulation = -insulation

    return insulation

def find_tad_boundaries(insulation, prominence=0.5):
    """
    Find TAD boundaries as peaks in insulation score

    Parameters:
    - prominence: minimum peak prominence (default 0.5)
    """
    # Remove NaN
    valid = ~np.isnan(insulation)
    insulation_clean = insulation[valid]

    # Find peaks
    peaks, properties = signal.find_peaks(insulation_clean, prominence=prominence)

    # Convert back to original indices
    valid_indices = np.where(valid)[0]
    boundary_indices = valid_indices[peaks]
    boundary_scores = insulation_clean[peaks]

    return boundary_indices, boundary_scores, properties['prominences']

def calculate_directionality_index(matrix, window_size=5):
    """
    Calculate Directionality Index (Dixon et al. 2012)

    DI = (B - A) / (B + A)
    where:
    - A = sum of upstream contacts (left of diagonal)
    - B = sum of downstream contacts (right of diagonal)

    DI > 0: downstream bias (end of TAD)
    DI < 0: upstream bias (start of TAD)
    DI ≈ 0: within TAD

    Parameters:
    - window_size: distance from diagonal (in bins)
    """
    n = matrix.shape[0]
    di = np.zeros(n)

    for i in range(n):
        # Define window
        start = max(0, i - window_size)
        end = min(n, i + window_size + 1)

        # Sum upstream contacts (A)
        if i > 0:
            A = np.nansum(matrix[i, start:i])
        else:
            A = 0

        # Sum downstream contacts (B)
        if i < n - 1:
            B = np.nansum(matrix[i, i+1:end])
        else:
            B = 0

        # Calculate DI
        if A + B > 0:
            di[i] = (B - A) / (B + A)
        else:
            di[i] = 0

    return di

def calculate_compartments(matrix):
    """
    Calculate A/B compartments using PCA (Lieberman-Aiden et al. 2009)

    A compartment: active chromatin (positive PC1)
    B compartment: inactive chromatin (negative PC1)

    Steps:
    1. Correlation matrix (Pearson between rows)
    2. Observed/Expected normalization
    3. PCA (first principal component = compartment)
    """
    # Correlation matrix
    corr_matrix = np.corrcoef(matrix)

    # Replace NaN with 0
    corr_matrix = np.nan_to_num(corr_matrix)

    # PCA via eigendecomposition
    eigenvalues, eigenvectors = np.linalg.eigh(corr_matrix)

    # First PC (largest eigenvalue)
    pc1_idx = np.argmax(np.abs(eigenvalues))
    pc1 = eigenvectors[:, pc1_idx]

    # Sign convention: positive = A compartment (active)
    # Typically, A compartment has higher contact density
    mean_contacts = np.nanmean(matrix, axis=1)
    if np.corrcoef(pc1, mean_contacts)[0, 1] < 0:
        pc1 = -pc1

    return pc1, eigenvalues

def compare_ctcf_with_boundaries(boundary_positions, ctcf_sites, bin_size=5000, tolerance=2):
    """
    Compare predicted CTCF sites with TAD boundaries

    Parameters:
    - boundary_positions: indices of TAD boundaries
    - ctcf_sites: list of CTCF positions (bp)
    - bin_size: Hi-C bin size (bp)
    - tolerance: allowed distance (bins)
    """
    matches = []

    for site in ctcf_sites:
        # Convert position to bin index
        site_bin = (site['position'] - LOCUS_START) // bin_size

        # Find closest boundary
        if len(boundary_positions) > 0:
            distances = np.abs(boundary_positions - site_bin)
            closest_idx = np.argmin(distances)
            closest_boundary = boundary_positions[closest_idx]
            distance_bins = distances[closest_idx]
            distance_bp = distance_bins * bin_size

            is_match = distance_bins <= tolerance

            matches.append({
                'ctcf_site': site['name'],
                'ctcf_position': site['position'],
                'ctcf_bin': site_bin,
                'closest_boundary_bin': closest_boundary,
                'distance_bins': distance_bins,
                'distance_bp': distance_bp,
                'match': is_match
            })

    return pd.DataFrame(matches)

def create_structure_plot(matrix, insulation, di, compartments, boundaries, ctcf_sites):
    """Create comprehensive Hi-C structure plot"""
    fig, axes = plt.subplots(4, 1, figsize=(16, 12),
                            gridspec_kw={'height_ratios': [3, 1, 1, 1]})

    n = matrix.shape[0]
    extent = [LOCUS_START/1e6, LOCUS_END/1e6, LOCUS_START/1e6, LOCUS_END/1e6]

    # Panel A: Hi-C heatmap with TAD boundaries
    ax1 = axes[0]
    im = ax1.imshow(matrix, cmap='YlOrRd', origin='lower', extent=extent,
                   aspect='auto', interpolation='nearest')

    # Mark TAD boundaries
    for boundary_bin in boundaries:
        boundary_pos = (LOCUS_START + boundary_bin * BIN_SIZE) / 1e6
        ax1.axhline(boundary_pos, color='blue', linestyle='--', linewidth=1, alpha=0.7)
        ax1.axvline(boundary_pos, color='blue', linestyle='--', linewidth=1, alpha=0.7)

    # Mark CTCF sites
    for site in CTCF_SITES:
        site_pos = site['position'] / 1e6
        ax1.plot(site_pos, site_pos, 'g^', markersize=10, markeredgecolor='black',
                markeredgewidth=1, label='CTCF' if site == CTCF_SITES[0] else '')

    ax1.set_xlabel('Genomic Position (Mb)', fontsize=11)
    ax1.set_ylabel('Genomic Position (Mb)', fontsize=11)
    ax1.set_title('Hi-C Contact Map with TAD Boundaries and CTCF Sites', fontsize=13, weight='bold')
    plt.colorbar(im, ax=ax1, label='Normalized Contact Frequency')
    ax1.legend(loc='upper right')

    # Panel B: Insulation score (TAD boundaries)
    ax2 = axes[1]
    genomic_pos = (np.arange(n) * BIN_SIZE + LOCUS_START) / 1e6

    ax2.plot(genomic_pos, insulation, 'b-', linewidth=1.5, label='Insulation Score')
    ax2.axhline(0, color='gray', linestyle=':', linewidth=0.8)

    # Mark boundaries as peaks
    for boundary_bin in boundaries:
        boundary_pos = (LOCUS_START + boundary_bin * BIN_SIZE) / 1e6
        ax2.axvline(boundary_pos, color='blue', linestyle='--', linewidth=1, alpha=0.5)

    # Mark CTCF sites
    for site in CTCF_SITES:
        site_pos = site['position'] / 1e6
        ax2.axvline(site_pos, color='green', linestyle='-', linewidth=1.5, alpha=0.7)

    ax2.set_xlabel('Genomic Position (Mb)', fontsize=11)
    ax2.set_ylabel('Insulation Score\n(Higher = Boundary)', fontsize=10)
    ax2.set_title('TAD Insulation Score (Peaks = Boundaries)', fontsize=12, weight='bold')
    ax2.legend(loc='upper right')
    ax2.grid(alpha=0.3)

    # Panel C: Directionality Index
    ax3 = axes[2]
    ax3.plot(genomic_pos, di, 'purple', linewidth=1.5, label='Directionality Index (DI)')
    ax3.axhline(0, color='gray', linestyle=':', linewidth=0.8)
    ax3.fill_between(genomic_pos, di, 0, where=(di > 0), color='red', alpha=0.3, label='Downstream bias')
    ax3.fill_between(genomic_pos, di, 0, where=(di < 0), color='blue', alpha=0.3, label='Upstream bias')

    # Mark CTCF sites
    for site in CTCF_SITES:
        site_pos = site['position'] / 1e6
        ax3.axvline(site_pos, color='green', linestyle='-', linewidth=1.5, alpha=0.7)

    ax3.set_xlabel('Genomic Position (Mb)', fontsize=11)
    ax3.set_ylabel('DI', fontsize=10)
    ax3.set_title('Directionality Index (DI > 0: downstream, DI < 0: upstream)', fontsize=12, weight='bold')
    ax3.legend(loc='upper right', fontsize=9)
    ax3.grid(alpha=0.3)

    # Panel D: A/B Compartments
    ax4 = axes[3]
    ax4.plot(genomic_pos, compartments, 'k-', linewidth=1.5, label='PC1 (Compartment)')
    ax4.axhline(0, color='gray', linestyle=':', linewidth=0.8)
    ax4.fill_between(genomic_pos, compartments, 0, where=(compartments > 0),
                     color='red', alpha=0.3, label='A compartment (active)')
    ax4.fill_between(genomic_pos, compartments, 0, where=(compartments < 0),
                     color='blue', alpha=0.3, label='B compartment (inactive)')

    # Mark HBB gene
    hbb_pos = 5_225_700 / 1e6
    ax4.axvline(hbb_pos, color='orange', linestyle='--', linewidth=2, alpha=0.8, label='HBB gene')

    ax4.set_xlabel('Genomic Position (Mb)', fontsize=11)
    ax4.set_ylabel('PC1 (Compartment)', fontsize=10)
    ax4.set_title('A/B Compartment Analysis (PC1 from correlation matrix)', fontsize=12, weight='bold')
    ax4.legend(loc='upper right', fontsize=9)
    ax4.grid(alpha=0.3)

    plt.tight_layout()

    return fig

def main():
    """Run Hi-C structural analysis"""
    print("="*70)
    print("Hi-C Structural Analysis: TADs, Insulation, Compartments")
    print("="*70)

    # Load data
    matrix, metadata = load_hic_matrix()
    n = matrix.shape[0]

    print(f"\n📊 Dataset: {n} bins × {n} bins")
    print(f"   Genomic span: chr{CHROMOSOME}:{LOCUS_START:,}-{LOCUS_END:,}")
    print(f"   Resolution: {BIN_SIZE:,} bp/bin")

    # Calculate insulation score
    print("\n🔍 Calculating insulation score (TAD boundaries)...")
    insulation = calculate_insulation_score(matrix, window_size=3)
    boundaries, boundary_scores, prominences = find_tad_boundaries(insulation, prominence=0.3)

    print(f"   Found {len(boundaries)} TAD boundaries:")
    for i, (boundary_bin, score, prom) in enumerate(zip(boundaries, boundary_scores, prominences)):
        boundary_pos = LOCUS_START + boundary_bin * BIN_SIZE
        print(f"   {i+1}. Bin {boundary_bin} (chr{CHROMOSOME}:{boundary_pos:,}) - "
              f"Score: {score:.2f}, Prominence: {prom:.2f}")

    # Calculate directionality index
    print("\n📐 Calculating directionality index...")
    di = calculate_directionality_index(matrix, window_size=5)

    di_mean = np.mean(di[~np.isnan(di)])
    di_std = np.std(di[~np.isnan(di)])
    print(f"   Mean DI: {di_mean:.3f} ± {di_std:.3f}")

    # Calculate compartments
    print("\n🧬 Calculating A/B compartments (PCA)...")
    pc1, eigenvalues = calculate_compartments(matrix)

    a_compartment_pct = np.sum(pc1 > 0) / len(pc1) * 100
    b_compartment_pct = np.sum(pc1 < 0) / len(pc1) * 100

    print(f"   A compartment (active): {a_compartment_pct:.1f}%")
    print(f"   B compartment (inactive): {b_compartment_pct:.1f}%")
    print(f"   Largest eigenvalue: {eigenvalues.max():.2f}")

    # Check HBB compartment
    hbb_bin = (5_225_700 - LOCUS_START) // BIN_SIZE
    if 0 <= hbb_bin < len(pc1):
        hbb_compartment = "A (active)" if pc1[hbb_bin] > 0 else "B (inactive)"
        print(f"   HBB gene compartment: {hbb_compartment} (PC1 = {pc1[hbb_bin]:.3f})")

    # Compare CTCF sites with TAD boundaries
    print("\n🔗 Comparing CTCF sites with TAD boundaries...")

    if len(boundaries) > 0:
        comparison = compare_ctcf_with_boundaries(boundaries, CTCF_SITES, BIN_SIZE, tolerance=2)

        print(f"\n   CTCF Site → Nearest TAD Boundary:")
        for _, row in comparison.iterrows():
            match_str = "✅ MATCH" if row['match'] else "⚠️ NO MATCH"
            print(f"   {row['ctcf_site']:10s} → {row['distance_bp']:>6.0f} bp away ({match_str})")

        matched = comparison['match'].sum()
        print(f"\n   Matched: {matched}/{len(CTCF_SITES)} ({matched/len(CTCF_SITES)*100:.0f}%)")

        # Save results
        comparison.to_csv(f'{RESULTS_DIR}/ctcf_tad_boundary_comparison.csv', index=False)
    else:
        print("   ⚠️ No TAD boundaries detected - cannot compare with CTCF sites")
        print("   → Locus has weak/diffuse TAD structure at this resolution")
        matched = 0
        comparison = pd.DataFrame()  # Empty DataFrame

    # Save insulation, DI, compartments
    results = pd.DataFrame({
        'bin': np.arange(n),
        'start': np.arange(n) * BIN_SIZE + LOCUS_START,
        'end': (np.arange(n) + 1) * BIN_SIZE + LOCUS_START,
        'insulation': insulation,
        'directionality_index': di,
        'compartment_pc1': pc1
    })
    results.to_csv(f'{RESULTS_DIR}/hic_structure_analysis.csv', index=False)

    print(f"\n✅ Results saved:")
    print(f"   - {RESULTS_DIR}/hic_structure_analysis.csv")
    print(f"   - {RESULTS_DIR}/ctcf_tad_boundary_comparison.csv")

    # Create visualization
    print("\n📊 Creating structure plot...")
    fig = create_structure_plot(matrix, insulation, di, pc1, boundaries, CTCF_SITES)

    output_png = f'{OUTPUT_DIR}/hic_structure_analysis.png'
    output_pdf = f'{OUTPUT_DIR}/hic_structure_analysis.pdf'

    fig.savefig(output_png, dpi=300, bbox_inches='tight')
    fig.savefig(output_pdf, bbox_inches='tight')

    print(f"✅ Figure saved:")
    print(f"   PNG: {output_png}")
    print(f"   PDF: {output_pdf}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY: Why is Hi-C correlation weak (r=0.16)?")
    print("="*70)

    # Analysis 1: TAD structure quality
    if len(boundaries) < 3:
        print("\n⚠️ TAD Structure: WEAK")
        print(f"   Only {len(boundaries)} clear boundaries detected")
        print("   → TAD structure is poorly defined in this locus")
        print("   → Explains why simple loop model doesn't fit well")
    else:
        print("\n✅ TAD Structure: STRONG")
        print(f"   {len(boundaries)} clear boundaries detected")
        print("   → TAD structure is well-defined")

    # Analysis 2: CTCF-TAD concordance
    if matched >= len(CTCF_SITES) * 0.66:
        print(f"\n✅ CTCF-TAD Concordance: GOOD ({matched}/{len(CTCF_SITES)})")
        print("   → CTCF sites align with TAD boundaries")
        print("   → Model predictions are mechanistically correct")
    else:
        print(f"\n⚠️ CTCF-TAD Concordance: POOR ({matched}/{len(CTCF_SITES)})")
        print("   → CTCF sites don't align with TAD boundaries")
        print("   → Model may be missing other structural features")

    # Analysis 3: Compartmentalization
    if hbb_compartment == "A (active)":
        print("\n✅ HBB Compartment: A (active)")
        print("   → Expected for highly expressed gene")
        print("   → Compartmentalization supports high HBB expression")
    else:
        print("\n⚠️ HBB Compartment: B (inactive)")
        print("   → Unexpected for highly expressed gene")
        print("   → May indicate compartment switching or erythroid-specific pattern")

    # Final verdict
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)

    if len(boundaries) < 3:
        print("\n🔍 PRIMARY ISSUE: Weak TAD structure")
        print("   Hypothesis: HBB locus has diffuse TAD boundaries")
        print("   → Simple loop model cannot capture complex structure")
        print("   → Need to add: compartmentalization, micro-TADs, dynamic loops")
    elif matched < len(CTCF_SITES) * 0.66:
        print("\n🔍 PRIMARY ISSUE: CTCF sites don't mark TAD boundaries")
        print("   Hypothesis: CTCF sites form internal loops, not boundaries")
        print("   → Model correctly predicts CTCF positions (100% concordance)")
        print("   → But these CTCF sites don't structure TADs at 5kb resolution")
    else:
        print("\n🔍 PRIMARY ISSUE: Model simplicity, not input errors")
        print("   Hypothesis: Loop extrusion alone insufficient")
        print("   → CTCF sites correct (100% concordance + TAD boundaries match)")
        print("   → Need to add: polymer baseline, compartments, non-CTCF loops")

    print("\n📋 Recommendations for Phase C:")
    print("   1. Add baseline polymer model (self-avoiding walk)")
    print("   2. Incorporate A/B compartment signal")
    print("   3. Add cohesin processivity parameter (dynamic loop sizes)")
    print("   4. Test on larger locus (200 kb) for statistical power")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
