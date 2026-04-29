"""
Synthetic Decorrelation Test: SFI vs LSSIM redundancy check

Tests whether Spectral Fragility Index provides information
distinct from LSSIM across different perturbation types.
"""

import numpy as np
from scipy.stats import pearsonr


def generate_synthetic_contact_matrix(n=50, blocks=3, noise=0.1):
    """Generate synthetic contact matrix with block structure"""
    C = np.random.rand(n, n) * noise
    block_size = n // blocks
    for i in range(blocks):
        start = i * block_size
        end = min((i + 1) * block_size, n)
        C[start:end, start:end] += 0.5
    C = (C + C.T) / 2
    return C


def add_uniform_noise(C, sigma=0.05):
    """Add uniform Gaussian noise"""
    noise = np.random.randn(*C.shape) * sigma
    C_mut = C + noise
    C_mut = (C_mut + C_mut.T) / 2
    return np.maximum(C_mut, 0)


def apply_block_perturbation(C, rank=2, strength=0.3):
    """Apply low-rank block disruption"""
    C_mut = C.copy()
    n = C.shape[0]
    block_start = n // 4
    block_end = 3 * n // 4
    C_mut[block_start:block_end, block_start:block_end] *= 1 - strength
    return C_mut


def add_highfreq_noise(C, k=20, sigma=0.1):
    """Add high-frequency speckle noise"""
    C_mut = C.copy()
    n = C.shape[0]
    for _ in range(k):
        i, j = np.random.randint(0, n, 2)
        C_mut[i, j] += np.random.randn() * sigma
        C_mut[j, i] = C_mut[i, j]
    return np.maximum(C_mut, 0)


def compute_lssim(C1, C2, window_size=7):
    """Compute LSSIM between two contact matrices"""
    n = C1.shape[0]
    lssim_values = []

    for i in range(n):
        for j in range(i, n):
            # Extract local windows
            i_start = max(0, i - window_size // 2)
            i_end = min(n, i + window_size // 2 + 1)
            j_start = max(0, j - window_size // 2)
            j_end = min(n, j + window_size // 2 + 1)

            w1 = C1[i_start:i_end, j_start:j_end].flatten()
            w2 = C2[i_start:i_end, j_start:j_end].flatten()

            # SSIM-like metric
            mu1, mu2 = w1.mean(), w2.mean()
            var1, var2 = w1.var(), w2.var()
            cov = np.cov(w1, w2)[0, 1]

            C1_const = 0.01
            C2_const = 0.03

            ssim = ((2 * mu1 * mu2 + C1_const) * (2 * cov + C2_const)) / (
                (mu1**2 + mu2**2 + C1_const) * (var1 + var2 + C2_const)
            )

            lssim_values.append(ssim)

    return np.mean(lssim_values)


if __name__ == "__main__":
    # Import spectral fragility
    import sys

    sys.path.append("D:/ДНК")
    from scripts.spectral_fragility import compute_spectral_fragility

    print("=== Synthetic Decorrelation Test: SFI vs LSSIM ===\n")

    results = {"uniform": [], "lowrank": [], "speckle": []}
    np.random.seed(42)

    for i in range(100):
        C_base = generate_synthetic_contact_matrix(n=50, blocks=3, noise=0.1)

        perturbations = {
            "uniform": add_uniform_noise(C_base, sigma=0.05),
            "lowrank": apply_block_perturbation(C_base, rank=2, strength=0.3),
            "speckle": add_highfreq_noise(C_base, k=20, sigma=0.1),
        }

        for ptype, C_mut in perturbations.items():
            sfi, _ = compute_spectral_fragility(C_base, C_mut, k=10)
            lssim = compute_lssim(C_base, C_mut, window_size=7)
            lssim_dissim = 1 - lssim  # Convert to dissimilarity
            results[ptype].append((sfi, lssim_dissim))

        if (i + 1) % 25 == 0:
            print(f"Progress: {i + 1}/100 iterations")

    print("\n=== Results ===\n")

    decision = "GO"
    max_r = 0.0

    for ptype in results:
        sfi_vals = [x[0] for x in results[ptype]]
        lssim_vals = [x[1] for x in results[ptype]]
        r, p = pearsonr(sfi_vals, lssim_vals)

        print(f"{ptype.upper()}:")
        print(f"  Correlation: r={r:.3f}, p={p:.4f}")
        print(f"  SFI range: [{min(sfi_vals):.3f}, {max(sfi_vals):.3f}]")
        print(f"  LSSIM_dissim range: [{min(lssim_vals):.3f}, {max(lssim_vals):.3f}]")

        max_r = max(max_r, abs(r))

        if abs(r) > 0.9:
            print(f"  ❌ REDUNDANT: SFI highly correlated with LSSIM")
            decision = "KILL"
        elif abs(r) > 0.7:
            print(f"  ⚠️  PARTIAL: Moderate correlation")
            if decision == "GO":
                decision = "MIXED"
        else:
            print(f"  ✅ COMPLEMENTARY: SFI provides distinct information")
        print()

    print(f"\n=== DECISION: {decision} ===")
    print(f"Max correlation: {max_r:.3f}\n")

    if decision == "KILL":
        print("Verdict: SFI is redundant with LSSIM (r>0.9).")
        print("Recommendation: KILL spectral track, pivot to HBA1/dosage panel.")
    elif decision == "MIXED":
        print("Verdict: SFI shows moderate correlation (0.7<r<0.9).")
        print("Recommendation: User decision needed — useful but not revolutionary.")
    else:
        print("Verdict: SFI is complementary to LSSIM (r<0.7).")
        print("Recommendation: Proceed to contact matrix validation.")
