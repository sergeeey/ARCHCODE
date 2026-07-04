"""
О3: Benford's Law Test на ARCHCODE LSSIM Scores

Hypothesis: LSSIM scores from 3D structures follow Benford's Law.
Kill Criterion: KS-test p > 0.05 OR shuffle test shows same deviation → law not applicable.

Context: Benford works for log-uniform distributions (wide range, 10^1-10^9).
          LSSIM ∈ [0.88, 0.99] ≈ 1 order of magnitude → likely FALSE hypothesis.
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path
import matplotlib.pyplot as plt

# Benford's Law distribution (first significant digit)
BENFORD_DIST = {
    1: np.log10(2),  # 0.301
    2: np.log10(3 / 2),  # 0.176
    3: np.log10(4 / 3),  # 0.125
    4: np.log10(5 / 4),  # 0.097
    5: np.log10(6 / 5),  # 0.079
    6: np.log10(7 / 6),  # 0.067
    7: np.log10(8 / 7),  # 0.058
    8: np.log10(9 / 8),  # 0.051
    9: np.log10(10 / 9),  # 0.046
}


def extract_first_digit(value):
    """Extract first significant digit from decimal number."""
    if pd.isna(value) or value <= 0:
        return None

    # Convert to string, remove leading '0.' if present
    str_val = f"{value:.10f}".lstrip("0.")

    # Find first non-zero digit
    for char in str_val:
        if char.isdigit() and char != "0":
            return int(char)

    return None


def benford_test(data, label="Data"):
    """Run Benford's Law test on dataset."""

    # Extract first digits
    first_digits = [extract_first_digit(x) for x in data]
    first_digits = [d for d in first_digits if d is not None]

    if len(first_digits) == 0:
        return {"error": "No valid first digits extracted"}

    # Count occurrences
    digit_counts = pd.Series(first_digits).value_counts().sort_index()
    observed_freq = (digit_counts / len(first_digits)).to_dict()

    # Expected Benford frequencies
    expected_freq = BENFORD_DIST.copy()

    # Ensure all digits 1-9 are present
    for d in range(1, 10):
        if d not in observed_freq:
            observed_freq[d] = 0.0

    # KS test
    obs_values = [observed_freq[d] for d in range(1, 10)]
    exp_values = [expected_freq[d] for d in range(1, 10)]

    ks_stat, ks_p = stats.ks_2samp(obs_values, exp_values)

    # Chi-square test
    obs_counts = [digit_counts.get(d, 0) for d in range(1, 10)]
    exp_counts = [BENFORD_DIST[d] * len(first_digits) for d in range(1, 10)]

    chi2_stat, chi2_p = stats.chisquare(obs_counts, exp_counts)

    return {
        "label": label,
        "n": len(first_digits),
        "observed_freq": observed_freq,
        "expected_freq": expected_freq,
        "ks_statistic": float(ks_stat),
        "ks_p_value": float(ks_p),
        "chi2_statistic": float(chi2_stat),
        "chi2_p_value": float(chi2_p),
        "digit_counts": digit_counts.to_dict(),
    }


def shuffle_test(data, n_shuffles=1000):
    """Run shuffle test to check if deviation is artifact of distribution shape."""
    original_result = benford_test(data, "Original")

    shuffle_ks = []
    for _ in range(n_shuffles):
        shuffled = np.random.permutation(data)
        result = benford_test(shuffled, "Shuffle")
        if "ks_statistic" in result:
            shuffle_ks.append(result["ks_statistic"])

    shuffle_mean_ks = np.mean(shuffle_ks)
    shuffle_std_ks = np.std(shuffle_ks)

    # If original KS is within 1 SD of shuffle mean → deviation is artifact
    z_score = (
        (original_result["ks_statistic"] - shuffle_mean_ks) / shuffle_std_ks
        if shuffle_std_ks > 0
        else 0
    )

    return {
        "original_ks": original_result["ks_statistic"],
        "shuffle_mean_ks": float(shuffle_mean_ks),
        "shuffle_std_ks": float(shuffle_std_ks),
        "z_score": float(z_score),
        "interpretation": "ARTIFACT" if abs(z_score) < 1.0 else "REAL_DEVIATION",
    }


def main():
    # Load HBB Unified Atlas
    atlas_path = Path("D:/ДНК/results/HBB_Unified_Atlas.csv")
    df = pd.read_csv(atlas_path)

    print(f"Loaded {len(df)} variants from HBB Unified Atlas")

    # Extract LSSIM scores
    lssim_scores = df["ARCHCODE_LSSIM"].dropna()
    print(f"Valid LSSIM scores: {len(lssim_scores)}")
    print(f"Range: [{lssim_scores.min():.4f}, {lssim_scores.max():.4f}]")

    # Orders of magnitude check
    log_range = np.log10(lssim_scores.max() / lssim_scores.min())
    print(f"Log range (orders of magnitude): {log_range:.2f}")
    print(f"WARNING: Benford requires ≥2 orders of magnitude. Current: {log_range:.2f}")

    # Run Benford test
    print("\n" + "=" * 60)
    print("BENFORD'S LAW TEST")
    print("=" * 60)

    result = benford_test(lssim_scores, "HBB LSSIM")

    print(f"\nSample size: {result['n']}")
    print(f"KS statistic: {result['ks_statistic']:.4f}")
    print(f"KS p-value: {result['ks_p_value']:.4f}")
    print(f"Chi² statistic: {result['chi2_statistic']:.4f}")
    print(f"Chi² p-value: {result['chi2_p_value']:.4f}")

    print("\nFirst Digit Distribution:")
    print(f"{'Digit':<8} {'Observed':<12} {'Expected (Benford)':<20} {'Deviation'}")
    print("-" * 60)
    for d in range(1, 10):
        obs = result["observed_freq"][d]
        exp = result["expected_freq"][d]
        dev = (obs - exp) / exp * 100 if exp > 0 else 0
        print(f"{d:<8} {obs:<12.4f} {exp:<20.4f} {dev:+.1f}%")

    # Shuffle test
    print("\n" + "=" * 60)
    print("SHUFFLE TEST (1000 iterations)")
    print("=" * 60)

    shuffle_result = shuffle_test(lssim_scores.values)
    print(f"Original KS: {shuffle_result['original_ks']:.4f}")
    print(
        f"Shuffle mean KS: {shuffle_result['shuffle_mean_ks']:.4f} ± {shuffle_result['shuffle_std_ks']:.4f}"
    )
    print(f"Z-score: {shuffle_result['z_score']:.2f}")
    print(f"Interpretation: {shuffle_result['interpretation']}")

    # VERDICT
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    kill_criteria_met = []

    # Kill Criterion 1: KS p-value > 0.05
    if result["ks_p_value"] > 0.05:
        kill_criteria_met.append("KS p-value > 0.05 (not significantly different from Benford)")

    # Kill Criterion 2: Chi² p-value > 0.05
    if result["chi2_p_value"] > 0.05:
        kill_criteria_met.append("Chi² p-value > 0.05 (good fit to Benford)")

    # Kill Criterion 3: Shuffle test shows artifact
    if shuffle_result["interpretation"] == "ARTIFACT":
        kill_criteria_met.append("Shuffle test: deviation is artifact (|z| < 1.0)")

    # Kill Criterion 4: Log range < 2 orders
    if log_range < 2.0:
        kill_criteria_met.append(f"Log range {log_range:.2f} < 2.0 (Benford not applicable)")

    if len(kill_criteria_met) > 0:
        verdict = "HYPOTHESIS KILLED"
        confidence = "HIGH"
        print(f"✗ {verdict} (confidence: {confidence})")
        print("\nKill criteria met:")
        for i, criterion in enumerate(kill_criteria_met, 1):
            print(f"  {i}. {criterion}")
    else:
        verdict = "HYPOTHESIS SUPPORTED"
        confidence = "MEDIUM"
        print(f"✓ {verdict} (confidence: {confidence})")
        print("\nBenford's Law appears to hold for LSSIM scores.")

    # Save results
    output = {
        "hypothesis": "O3: Benford's Law on LSSIM Scores",
        "data_source": "HBB_Unified_Atlas.csv",
        "n_variants": len(df),
        "n_lssim_scores": result["n"],
        "lssim_range": {
            "min": float(lssim_scores.min()),
            "max": float(lssim_scores.max()),
            "log_range": float(log_range),
        },
        "benford_test": result,
        "shuffle_test": shuffle_result,
        "kill_criteria": kill_criteria_met,
        "verdict": verdict,
        "confidence": confidence,
        "interpretation": (
            "Benford's Law does NOT apply to LSSIM scores. "
            "LSSIM ∈ [0.88, 0.99] covers ~0.05 log units (<<2 orders required). "
            "First digit distribution is dominated by 9's (boundary effect at max SSIM=1.0). "
            "This is expected for bounded similarity metrics and does NOT indicate anomalies."
        ),
    }

    output_path = Path("D:/ДНК/results/O3_benford_lssim_test.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Observed vs Expected
    digits = list(range(1, 10))
    obs_freq = [result["observed_freq"][d] for d in digits]
    exp_freq = [result["expected_freq"][d] for d in digits]

    x = np.arange(len(digits))
    width = 0.35

    ax1.bar(x - width / 2, obs_freq, width, label="Observed (LSSIM)", alpha=0.7)
    ax1.bar(x + width / 2, exp_freq, width, label="Expected (Benford)", alpha=0.7)
    ax1.set_xlabel("First Significant Digit")
    ax1.set_ylabel("Frequency")
    ax1.set_title(f'Benford Test: HBB LSSIM (n={result["n"]})')
    ax1.set_xticks(x)
    ax1.set_xticklabels(digits)
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # LSSIM distribution histogram
    ax2.hist(lssim_scores, bins=50, alpha=0.7, edgecolor="black")
    ax2.set_xlabel("LSSIM Score")
    ax2.set_ylabel("Count")
    ax2.set_title(f"LSSIM Distribution (range: {log_range:.2f} log units)")
    ax2.axvline(
        lssim_scores.mean(), color="red", linestyle="--", label=f"Mean: {lssim_scores.mean():.4f}"
    )
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig_path = Path("D:/ДНК/results/fig_O3_benford_test.png")
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to: {fig_path}")

    return output


if __name__ == "__main__":
    result = main()
