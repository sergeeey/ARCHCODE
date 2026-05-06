"""
Simple WRN Test — No Proxies
Post-hoc from G4-3 failure

Direct test: WRN expression → WRN CRISPR dependency

Kill criteria: |ρ| < 0.15 OR p > 0.01
"""

import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path("../results")
OUTPUT_DIR = Path("../results")

# Load merged data from G4-3
df = pd.read_csv(DATA_DIR / "lambda_crispr_merged.csv", index_col=0)

print("=" * 60)
print("Simple WRN Test (No Proxies)")
print("=" * 60)
print()

# Direct test
wrn_expr = df["WRN_expr"].values
wrn_crispr = df["WRN"].values

rho, pval = spearmanr(wrn_expr, wrn_crispr)

print(f"n = {len(wrn_expr)} cell lines")
print(f"WRN expression range: {wrn_expr.min():.2f} - {wrn_expr.max():.2f}")
print(f"WRN CRISPR range: {wrn_crispr.min():.2f} - {wrn_crispr.max():.2f}")
print()
print(f"Spearman ρ(WRN_expr, WRN_dependency) = {rho:.3f}")
print(f"p-value = {pval:.2e}")
print()

# Kill criteria
if abs(rho) > 0.15 and pval < 0.01:
    print("✓ WEAK SIGNAL DETECTED")
    print(f"  Effect size adequate (|ρ|={abs(rho):.3f} > 0.15)")
    print(f"  Significance OK (p={pval:.2e} < 0.01)")
    verdict = "EXPLORE"
else:
    print("✗ NO SIGNAL")
    if abs(rho) <= 0.15:
        print(f"  Effect size too weak (|ρ|={abs(rho):.3f} ≤ 0.15)")
    if pval >= 0.01:
        print(f"  Not significant (p={pval:.2e} ≥ 0.01)")
    verdict = "KILL"

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(wrn_expr, wrn_crispr, alpha=0.3, s=10)
ax.set_xlabel("WRN Expression (TPM log1p)")
ax.set_ylabel("WRN CRISPR Dependency (gene effect)")
ax.set_title(f"WRN Expression vs Dependency\nρ={rho:.3f}, p={pval:.2e}")
ax.grid(alpha=0.3)

# Add trend line
z = pd.DataFrame({"x": wrn_expr, "y": wrn_crispr}).dropna()
if len(z) > 10:
    coeffs = pd.DataFrame({"x": z.x, "y": z.y}).corr().iloc[0, 1]
    fit = pd.Series(wrn_expr).rank().corr(pd.Series(wrn_crispr).rank())

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "wrn_simple_test.png", dpi=150)
print(f"\nPlot saved: {OUTPUT_DIR / 'wrn_simple_test.png'}")

print()
print("=" * 60)
print(f"VERDICT: {verdict}")
print("=" * 60)

if verdict == "EXPLORE":
    print("Recommendation: Try refined G4-helicase hypothesis (WRN-focused)")
else:
    print("Recommendation: Computational route exhausted, need wet-lab data")
