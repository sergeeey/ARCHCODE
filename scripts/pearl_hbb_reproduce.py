"""
Pearl variant detection reproduction for HBB locus.

Pearl definition (from dataset): ClinVar-pathogenic variants that are
structurally disrupted (low LSSIM) but missed by sequence-based tools
(low VEP score). These are "hidden pathogenic" variants -- invisible
to VEP/CADD but caught by ARCHCODE structural analysis.

Criteria:
  - LSSIM < 0.95 (structural disruption detected by ARCHCODE)
  - VEP_Score < 0.5 (sequence tools fail to flag)
  - ClinVar = Pathogenic (ground truth: actually pathogenic)
"""

import pandas as pd

CSV_PATH = "D:/ДНК/results/HBB_Unified_Atlas_95kb.csv"

df = pd.read_csv(CSV_PATH)
print(f"Total variants: {len(df)}")
print(f"Columns: {list(df.columns)}")
print()

# --- 1. Reproduce pearl count at LSSIM < 0.95 ---
LSSIM_THRESHOLD = 0.95
VEP_THRESHOLD = 0.5

# Pearl = structurally disrupted + VEP-invisible + actually pathogenic
pathogenic_labels = df["Label"] == "Pathogenic"
low_lssim = df["ARCHCODE_LSSIM"] < LSSIM_THRESHOLD
low_vep = df["VEP_Score"] < VEP_THRESHOLD

pearls = df[low_lssim & low_vep & pathogenic_labels]
print(f"=== Pearl Detection (LSSIM < {LSSIM_THRESHOLD}, VEP < {VEP_THRESHOLD}) ===")
print(f"Pearls found: {len(pearls)}")
print(f"Dataset Pearl column True count: {(df['Pearl'] == True).sum()}")
match = len(pearls) == (df["Pearl"] == True).sum()
print(f"Matches dataset Pearl column: {match}")
print()

# --- 2. Check: how many pearls have VEP >= 0.5? (should be 0) ---
pearls_high_vep = pearls[pearls["VEP_Score"] >= 0.5]
print(f"Pearls with VEP >= 0.5: {len(pearls_high_vep)} (expected: 0)")
print()

# --- 3. Check: how many pearls have CADD Phred >= 15? ---
# Exclude CADD=-1 (missing)
pearls_valid_cadd = pearls[pearls["CADD_Phred"] >= 0]
pearls_high_cadd = pearls_valid_cadd[pearls_valid_cadd["CADD_Phred"] >= 15]
print(f"Pearls with valid CADD (>=0): {len(pearls_valid_cadd)}")
print(f"Pearls with CADD Phred >= 15: {len(pearls_high_cadd)} / {len(pearls_valid_cadd)}")
print(
    f"Pearls with CADD Phred < 15 (truly invisible): {len(pearls_valid_cadd) - len(pearls_high_cadd)}"
)
print()

# --- 4. Threshold stability analysis ---
print("=== Threshold Stability ===")
print(f"{'LSSIM threshold':<18} {'Pearl count':<14} {'% of pathogenic'}")
print("-" * 50)

total_pathogenic = pathogenic_labels.sum()
for threshold in [0.88, 0.90, 0.92, 0.95]:
    mask = (df["ARCHCODE_LSSIM"] < threshold) & low_vep & pathogenic_labels
    count = mask.sum()
    pct = 100.0 * count / total_pathogenic if total_pathogenic > 0 else 0
    print(f"< {threshold:<16} {count:<14} {pct:.1f}%")

print()

# --- 5. Summary table of all 27 pearls ---
print("=== All Pearl Variants ===")
cols = [
    "ClinVar_ID",
    "Position_GRCh38",
    "ARCHCODE_LSSIM",
    "VEP_Score",
    "CADD_Phred",
    "ClinVar_Significance",
    "VEP_Consequence",
]
print(pearls[cols].to_string(index=False))
print()

# --- 6. LSSIM distribution of pearls ---
print("=== Pearl LSSIM Statistics ===")
print(f"Min:    {pearls['ARCHCODE_LSSIM'].min():.4f}")
print(f"Max:    {pearls['ARCHCODE_LSSIM'].max():.4f}")
print(f"Mean:   {pearls['ARCHCODE_LSSIM'].mean():.4f}")
print(f"Median: {pearls['ARCHCODE_LSSIM'].median():.4f}")
