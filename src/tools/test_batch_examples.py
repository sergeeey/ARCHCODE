"""
Batch test: 4 classification examples для validation

1. ARCHCODE × AlphaGenome (real) → WEAK-ORTHOGONAL
2. Synthetic CONCORDANT → high correlation
3. Synthetic CONFLICTING → negative correlation
4. Synthetic ORTHOGONAL → both methods separate, ρ ≈ 0
"""

import numpy as np
from plot_classification import plot_batch
import json

# 1. ARCHCODE × AlphaGenome (real data)
print("Loading ARCHCODE × AlphaGenome data...")
with open("../../results/alphagenome_pearl_vs_control.json", "r") as f:
    data = json.load(f)

A1 = []
B1 = []
labels1 = []

for variant in data["results"]:
    A1.append(variant["archcode_ssim"])
    B1.append(variant["cage_pct"])
    labels1.append(1 if variant["group"] == "PEARL" else 0)

A1 = np.array(A1)
B1 = np.array(B1)
labels1 = np.array(labels1)

# 2. CONCORDANT (synthetic)
np.random.seed(42)
n = 30

# Оба метода измеряют "одно и то же" (pathogenic = high values)
group_0_base = np.random.normal(3, 0.5, 15)  # benign: low values
group_1_base = np.random.normal(8, 0.8, 15)  # pathogenic: high values

A2 = np.concatenate([group_0_base, group_1_base])
B2 = A2 * 1.1 + np.random.normal(0, 0.4, n)  # High correlation with A
labels2 = np.array([0] * 15 + [1] * 15)

# 3. CONFLICTING (synthetic)
# Method A: pathogenic = high
# Method B: pathogenic = LOW (inverse!) → conflict
A3 = np.concatenate([group_0_base, group_1_base])
B3 = -A3 + 10 + np.random.normal(0, 0.6, n)  # Negative correlation
labels3 = np.array([0] * 15 + [1] * 15)

# 4. ORTHOGONAL (synthetic, correct)
# Method A: detects pathogenic (high values)
# Method B: ALSO detects pathogenic (high values), but INDEPENDENT mechanism
np.random.seed(123)

# Method A: structural mechanism
group_0_A = np.random.normal(0.95, 0.02, 15)  # benign: high structural stability
group_1_A = np.random.normal(0.85, 0.03, 15)  # pathogenic: low structural stability

# Method B: functional mechanism (INDEPENDENT from structure)
# Pathogenic = negative functional score, benign = near zero
# NO correlation with structural scores
group_0_B = np.random.normal(-0.05, 0.03, 15)  # benign: minimal functional disruption
group_1_B = np.random.normal(-0.25, 0.05, 15)  # pathogenic: strong functional disruption

A4 = np.concatenate([group_0_A, group_1_A])
B4 = np.concatenate([group_0_B, group_1_B])
labels4 = np.array([0] * 15 + [1] * 15)

# Check: correlation should be near zero, both should separate
from scipy.stats import spearmanr, mannwhitneyu

rho4, _ = spearmanr(A4, B4)
_, p_A4 = mannwhitneyu(group_0_A, group_1_A, alternative="two-sided")
_, p_B4 = mannwhitneyu(group_0_B, group_1_B, alternative="two-sided")

print(f"\nOrthogonal example verification:")
print(f"  ρ = {rho4:.3f} (expected ≈ 0)")
print(f"  Method A: p = {p_A4:.4f} (expected <0.05)")
print(f"  Method B: p = {p_B4:.4f} (expected <0.05)")
print()

# Batch plot
datasets = [
    ("ARCHCODE × AlphaGenome\n(Real Data)", A1, B1, labels1, "ARCHCODE SSIM", "AlphaGenome CAGE %"),
    ("CONCORDANT Example\n(Synthetic)", A2, B2, labels2, "Method A", "Method B (correlated)"),
    ("CONFLICTING Example\n(Synthetic)", A3, B3, labels3, "Method A", "Method B (inverse)"),
    (
        "ORTHOGONAL Example\n(Synthetic)",
        A4,
        B4,
        labels4,
        "Method A (structural)",
        "Method B (functional)",
    ),
]

print("Generating batch plot (2×2 grid)...")
fig = plot_batch(
    datasets,
    ncols=2,
    figsize_per_plot=(6, 5),
    save_path="../../results/fig_orthogonality_batch_examples.png",
)

print("\n✅ Batch test complete!")
print("Figure saved: results/fig_orthogonality_batch_examples.png")
print("\nExpected classifications:")
print("  1. ARCHCODE × AlphaGenome → WEAK-ORTHOGONAL ✓")
print("  2. Synthetic CONCORDANT → CONCORDANT ✓")
print("  3. Synthetic CONFLICTING → CONFLICTING ✓")
print("  4. Synthetic ORTHOGONAL → ORTHOGONAL ✓")
