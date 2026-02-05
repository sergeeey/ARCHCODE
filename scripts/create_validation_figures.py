#!/usr/bin/env python3
"""
Generate publication-quality figures for Hi-C validation results

Creates:
1. Side-by-side heatmaps (experimental vs simulation)
2. Scatter plot (experimental vs simulation contacts)
3. Correlation comparison (raw vs normalized)

For bioRxiv / PLoS Computational Biology submission
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from scipy.stats import pearsonr

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
FIG_DIR = PROJECT_ROOT / 'figures'
FIG_DIR.mkdir(exist_ok=True)

# Load data
exp_raw = np.load(DATA_DIR / 'hudep2_wt_hic_hbb_locus.npy')
exp_norm = np.load(DATA_DIR / 'hudep2_wt_hic_hbb_locus_normalized.npy')
sim_v1_norm = np.load(DATA_DIR / 'archcode_hbb_simulation_normalized.npy')
sim_v2_norm = np.load(DATA_DIR / 'archcode_hbb_literature_ctcf_normalized.npy')

with open(DATA_DIR / 'archcode_hbb_simulation_matrix.json') as f:
    sim_v1_data = json.load(f)
    sim_v1_raw = np.array(sim_v1_data['matrix'])

with open(DATA_DIR / 'archcode_hbb_literature_ctcf_matrix.json') as f:
    sim_v2_data = json.load(f)
    sim_v2_raw = np.array(sim_v2_data['matrix'])

# Correlation results
with open(DATA_DIR / 'correlation_results_v1_normalized.json') as f:
    corr_v1_norm = json.load(f)

with open(DATA_DIR / 'correlation_results_v2_normalized.json') as f:
    corr_v2_norm = json.load(f)

with open(DATA_DIR / 'correlation_results.json') as f:
    data = json.load(f)
    # Handle nested format (old) vs flat format (new)
    corr_v1_raw = data['correlation'] if 'correlation' in data else data

with open(DATA_DIR / 'correlation_results_v2_literature_ctcf.json') as f:
    data = json.load(f)
    corr_v2_raw = data['correlation'] if 'correlation' in data else data

# Figure style
plt.style.use('seaborn-v0_8-paper')
sns.set_context("paper", font_scale=1.2)
sns.set_palette("colorblind")

##############################################################################
# Figure 1: Side-by-side heatmaps (Experimental vs Simulation V1 - normalized)
##############################################################################

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Genomic coordinates
start_mb = 5.2
end_mb = 5.25
ticks = np.linspace(0, 9, 5)
tick_labels = [f'{start_mb + (end_mb - start_mb) * t / 9:.2f}' for t in ticks]

# A) Experimental (KR normalized)
im1 = axes[0].imshow(exp_norm, cmap='Reds', aspect='auto', vmin=0)
axes[0].set_title('A) Experimental Hi-C\n(KR normalized)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Genomic position (Mb)', fontsize=10)
axes[0].set_ylabel('Genomic position (Mb)', fontsize=10)
axes[0].set_xticks(ticks)
axes[0].set_xticklabels(tick_labels)
axes[0].set_yticks(ticks)
axes[0].set_yticklabels(tick_labels)
plt.colorbar(im1, ax=axes[0], label='Contact frequency', fraction=0.046, pad=0.04)

# Add metadata
axes[0].text(0.02, 0.98, 'GSM4873116\nWT-HUDEP2\nchr11:5.2-5.25 Mb\n5kb resolution',
             transform=axes[0].transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# B) ARCHCODE Simulation V1 (normalized)
im2 = axes[1].imshow(sim_v1_norm, cmap='Blues', aspect='auto', vmin=0)
axes[1].set_title('B) ARCHCODE Simulation\n(hypothetical CTCF)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Genomic position (Mb)', fontsize=10)
axes[1].set_xticks(ticks)
axes[1].set_xticklabels(tick_labels)
axes[1].set_yticks(ticks)
axes[1].set_yticklabels(tick_labels)
plt.colorbar(im2, ax=axes[1], label='Contact frequency', fraction=0.046, pad=0.04)

# Add simulation parameters
axes[1].text(0.02, 0.98, f'6 CTCF sites\n20 cohesins\nv=1kb/s\nseed=42',
             transform=axes[1].transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

# C) Scatter plot: Experimental vs Simulation
# Upper triangle only (exclude diagonal)
n = exp_norm.shape[0]
triu_indices = np.triu_indices(n, k=1)
exp_triu = exp_norm[triu_indices]
sim_triu = sim_v1_norm[triu_indices]

# Remove NaN pairs
mask = ~(np.isnan(exp_triu) | np.isnan(sim_triu))
exp_valid = exp_triu[mask]
sim_valid = sim_triu[mask]

axes[2].scatter(exp_valid, sim_valid, alpha=0.6, s=30, edgecolors='k', linewidths=0.5)
axes[2].set_title(f'C) Correlation\nr = {corr_v1_norm["pearson_r"]:.3f} (p={corr_v1_norm["pearson_p"]:.3f})',
                  fontsize=12, fontweight='bold')
axes[2].set_xlabel('Experimental contact frequency', fontsize=10)
axes[2].set_ylabel('Simulated contact frequency', fontsize=10)
axes[2].grid(True, alpha=0.3)

# Add diagonal reference line
lims = [
    np.min([axes[2].get_xlim(), axes[2].get_ylim()]),
    np.max([axes[2].get_xlim(), axes[2].get_ylim()]),
]
axes[2].plot(lims, lims, 'k--', alpha=0.5, zorder=0, label='y=x')
axes[2].legend(loc='upper left', fontsize=8)

# Add statistical box
stats_text = f'n = {corr_v1_norm["sample_size"]} pairs\nSpearman ρ = {corr_v1_norm["spearman_rho"]:.3f}'
axes[2].text(0.98, 0.02, stats_text, transform=axes[2].transAxes, fontsize=8,
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(FIG_DIR / 'figure1_hic_validation_v1.png', dpi=300, bbox_inches='tight')
plt.savefig(FIG_DIR / 'figure1_hic_validation_v1.pdf', bbox_inches='tight')
print(f'✅ Figure 1 saved: {FIG_DIR}/figure1_hic_validation_v1.png (and .pdf)')
plt.close()

##############################################################################
# Figure 2: Comparison V1 vs V2 (hypothetical vs literature CTCF)
##############################################################################

fig, axes = plt.subplots(2, 2, figsize=(12, 12))

# Top row: V1 (hypothetical CTCF)
im1 = axes[0, 0].imshow(exp_norm, cmap='Reds', aspect='auto', vmin=0)
axes[0, 0].set_title('A) Experimental Hi-C', fontsize=11, fontweight='bold')
axes[0, 0].set_ylabel('Genomic position (Mb)', fontsize=9)
axes[0, 0].set_xticks(ticks)
axes[0, 0].set_xticklabels(tick_labels, fontsize=8)
axes[0, 0].set_yticks(ticks)
axes[0, 0].set_yticklabels(tick_labels, fontsize=8)
plt.colorbar(im1, ax=axes[0, 0], fraction=0.046, pad=0.04)

im2 = axes[0, 1].imshow(sim_v1_norm, cmap='Blues', aspect='auto', vmin=0)
axes[0, 1].set_title(f'B) V1: Hypothetical CTCF\nr={corr_v1_norm["pearson_r"]:.3f} (p={corr_v1_norm["pearson_p"]:.3f})',
                     fontsize=11, fontweight='bold')
axes[0, 1].set_xticks(ticks)
axes[0, 1].set_xticklabels(tick_labels, fontsize=8)
axes[0, 1].set_yticks(ticks)
axes[0, 1].set_yticklabels(tick_labels, fontsize=8)
plt.colorbar(im2, ax=axes[0, 1], fraction=0.046, pad=0.04)

# Bottom row: V2 (literature CTCF)
im3 = axes[1, 0].imshow(exp_norm, cmap='Reds', aspect='auto', vmin=0)
axes[1, 0].set_title('C) Experimental Hi-C (repeated)', fontsize=11, fontweight='bold')
axes[1, 0].set_xlabel('Genomic position (Mb)', fontsize=9)
axes[1, 0].set_ylabel('Genomic position (Mb)', fontsize=9)
axes[1, 0].set_xticks(ticks)
axes[1, 0].set_xticklabels(tick_labels, fontsize=8)
axes[1, 0].set_yticks(ticks)
axes[1, 0].set_yticklabels(tick_labels, fontsize=8)
plt.colorbar(im3, ax=axes[1, 0], fraction=0.046, pad=0.04)

im4 = axes[1, 1].imshow(sim_v2_norm, cmap='Greens', aspect='auto', vmin=0)
axes[1, 1].set_title(f'D) V2: Literature CTCF\nr={corr_v2_norm["pearson_r"]:.3f} (p={corr_v2_norm["pearson_p"]:.3f})',
                     fontsize=11, fontweight='bold')
axes[1, 1].set_xlabel('Genomic position (Mb)', fontsize=9)
axes[1, 1].set_xticks(ticks)
axes[1, 1].set_xticklabels(tick_labels, fontsize=8)
axes[1, 1].set_yticks(ticks)
axes[1, 1].set_yticklabels(tick_labels, fontsize=8)
plt.colorbar(im4, ax=axes[1, 1], fraction=0.046, pad=0.04)

plt.tight_layout()
plt.savefig(FIG_DIR / 'figure2_v1_vs_v2_comparison.png', dpi=300, bbox_inches='tight')
plt.savefig(FIG_DIR / 'figure2_v1_vs_v2_comparison.pdf', bbox_inches='tight')
print(f'✅ Figure 2 saved: {FIG_DIR}/figure2_v1_vs_v2_comparison.png (and .pdf)')
plt.close()

##############################################################################
# Figure 3: Correlation comparison (Raw vs KR Normalized)
##############################################################################

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Data for bar plot
conditions = ['V1\nHypothetical\nCTCF', 'V2\nLiterature\nCTCF']
raw_r = [corr_v1_raw['pearson_r'], corr_v2_raw['pearson_r']]
norm_r = [corr_v1_norm['pearson_r'], corr_v2_norm['pearson_r']]

x = np.arange(len(conditions))
width = 0.35

# A) Pearson r comparison
bars1 = axes[0].bar(x - width/2, raw_r, width, label='Raw counts', color='coral', alpha=0.8)
bars2 = axes[0].bar(x + width/2, norm_r, width, label='KR normalized', color='steelblue', alpha=0.8)

axes[0].set_ylabel('Pearson correlation (r)', fontsize=11)
axes[0].set_title('A) Effect of KR Normalization', fontsize=12, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(conditions, fontsize=9)
axes[0].legend(fontsize=9)
axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.8)
axes[0].axhline(y=0.7, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Target (r≥0.7)')
axes[0].grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)
for bar in bars2:
    height = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)

# B) P-value significance
raw_p = [corr_v1_raw['pearson_p'], corr_v2_raw['pearson_p']]
norm_p = [corr_v1_norm['pearson_p'], corr_v2_norm['pearson_p']]

bars3 = axes[1].bar(x - width/2, raw_p, width, label='Raw counts', color='coral', alpha=0.8)
bars4 = axes[1].bar(x + width/2, norm_p, width, label='KR normalized', color='steelblue', alpha=0.8)

axes[1].set_ylabel('p-value', fontsize=11)
axes[1].set_title('B) Statistical Significance', fontsize=12, fontweight='bold')
axes[1].set_xticks(x)
axes[1].set_xticklabels(conditions, fontsize=9)
axes[1].legend(fontsize=9)
axes[1].axhline(y=0.05, color='red', linestyle='--', linewidth=1, alpha=0.5, label='α=0.05')
axes[1].set_ylim([0, 1.0])
axes[1].grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars3:
    height = bar.get_height()
    axes[1].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=8)
for bar in bars4:
    height = bar.get_height()
    axes[1].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=8)

# Significance annotation
axes[1].text(0.5, 0.95, 'None significant (all p>0.05)',
             transform=axes[1].transAxes, fontsize=10, ha='center',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

plt.tight_layout()
plt.savefig(FIG_DIR / 'figure3_normalization_effect.png', dpi=300, bbox_inches='tight')
plt.savefig(FIG_DIR / 'figure3_normalization_effect.pdf', bbox_inches='tight')
print(f'✅ Figure 3 saved: {FIG_DIR}/figure3_normalization_effect.png (and .pdf)')
plt.close()

##############################################################################
# Figure 4: Contact distribution comparison
##############################################################################

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# A) Histogram comparison (normalized data)
exp_flat_norm = exp_norm[np.triu_indices(n, k=1)]
sim_v1_flat_norm = sim_v1_norm[np.triu_indices(n, k=1)]

# Remove NaNs
exp_valid_hist = exp_flat_norm[~np.isnan(exp_flat_norm)]
sim_valid_hist = sim_v1_flat_norm[~np.isnan(sim_v1_flat_norm)]

axes[0].hist(exp_valid_hist, bins=30, alpha=0.6, color='red', label='Experimental', density=True)
axes[0].hist(sim_valid_hist, bins=30, alpha=0.6, color='blue', label='Simulation V1', density=True)
axes[0].set_xlabel('Contact frequency (KR normalized)', fontsize=10)
axes[0].set_ylabel('Density', fontsize=10)
axes[0].set_title('A) Contact Distribution', fontsize=12, fontweight='bold')
axes[0].legend(fontsize=9)
axes[0].grid(alpha=0.3)

# Add statistics
stats_text = (f'Experimental:\nMean={np.mean(exp_valid_hist):.4f}\n'
              f'Std={np.std(exp_valid_hist):.4f}\n\n'
              f'Simulation:\nMean={np.mean(sim_valid_hist):.4f}\n'
              f'Std={np.std(sim_valid_hist):.4f}')
axes[0].text(0.98, 0.98, stats_text, transform=axes[0].transAxes, fontsize=8,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# B) Q-Q plot
from scipy import stats as scipy_stats
scipy_stats.probplot(sim_valid_hist, dist=scipy_stats.norm, plot=axes[1])
axes[1].get_lines()[0].set_markerfacecolor('blue')
axes[1].get_lines()[0].set_markeredgecolor('blue')
axes[1].get_lines()[0].set_alpha(0.6)
axes[1].set_title('B) Q-Q Plot (Simulation vs Normal)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Theoretical quantiles', fontsize=10)
axes[1].set_ylabel('Sample quantiles', fontsize=10)
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(FIG_DIR / 'figure4_contact_distributions.png', dpi=300, bbox_inches='tight')
plt.savefig(FIG_DIR / 'figure4_contact_distributions.pdf', bbox_inches='tight')
print(f'✅ Figure 4 saved: {FIG_DIR}/figure4_contact_distributions.png (and .pdf)')
plt.close()

##############################################################################
# Summary
##############################################################################

print('\n═══════════════════════════════════════════')
print('  Figure Generation Complete')
print('═══════════════════════════════════════════\n')

print('📊 Figures created:')
print(f'   1. {FIG_DIR}/figure1_hic_validation_v1.png (and .pdf)')
print(f'      - Experimental vs Simulation heatmaps + scatter plot')
print(f'   2. {FIG_DIR}/figure2_v1_vs_v2_comparison.png (and .pdf)')
print(f'      - V1 (hypothetical) vs V2 (literature) CTCF comparison')
print(f'   3. {FIG_DIR}/figure3_normalization_effect.png (and .pdf)')
print(f'      - Raw vs KR normalized correlation comparison')
print(f'   4. {FIG_DIR}/figure4_contact_distributions.png (and .pdf)')
print(f'      - Contact frequency distributions and Q-Q plot\n')

print('✅ All figures ready for manuscript inclusion\n')
print('📝 Figure captions and legends should be added to manuscript\n')
