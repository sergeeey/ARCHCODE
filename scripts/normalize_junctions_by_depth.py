# normalize_junctions_by_depth.py
import pandas as pd
import json

print("=" * 70)
print("  Normalized Junction Analysis — Depth-Adjusted")
print("=" * 70)
print()

# Sequencing depth (HBB locus reads)
DEPTH = {
    "WT": 424_685,
    "B6": 736_251,
    "A2": 1_278_373,
}

# Load classified junctions
with open("D:/ДНК/results/hbb_novel_junctions_classified.json") as f:
    data = json.load(f)

# Raw counts - JSON structure is sample-first, not type-first
junction_counts = data["junction_counts"]

# Reorganize: type -> sample -> count
raw_counts = {
    'cryptic_5ss': {
        'WT': junction_counts['WT']['cryptic_5ss'],
        'B6': junction_counts['B6']['cryptic_5ss'],
        'A2': junction_counts['A2']['cryptic_5ss'],
    },
    'cryptic_3ss': {
        'WT': junction_counts['WT']['cryptic_3ss'],
        'B6': junction_counts['B6']['cryptic_3ss'],
        'A2': junction_counts['A2']['cryptic_3ss'],
    },
    'intron_retention': {
        'WT': junction_counts['WT']['intron_retention'],
        'B6': junction_counts['B6']['intron_retention'],
        'A2': junction_counts['A2']['intron_retention'],
    },
    'novel': {
        'WT': junction_counts['WT']['novel'],
        'B6': junction_counts['B6']['novel'],
        'A2': junction_counts['A2']['novel'],
    },
}

print("RAW counts (from classification):")
print(f"  cryptic_5ss: WT={raw_counts['cryptic_5ss']['WT']}, B6={raw_counts['cryptic_5ss']['B6']}, A2={raw_counts['cryptic_5ss']['A2']}")
print(f"  cryptic_3ss: WT={raw_counts['cryptic_3ss']['WT']}, B6={raw_counts['cryptic_3ss']['B6']}, A2={raw_counts['cryptic_3ss']['A2']}")
print(f"  intron_retention: WT={raw_counts['intron_retention']['WT']}, B6={raw_counts['intron_retention']['B6']}, A2={raw_counts['intron_retention']['A2']}")
print()

# Normalize to per-million reads
print("NORMALIZED (per million HBB reads):")
print()

for jtype in ['cryptic_5ss', 'cryptic_3ss', 'intron_retention', 'novel']:
    print(f"{jtype}:")
    
    for sample in ['WT', 'B6', 'A2']:
        raw = raw_counts[jtype][sample]
        depth_millions = DEPTH[sample] / 1_000_000
        normalized = raw / depth_millions
        print(f"  {sample}: {raw} raw → {normalized:.1f} per million reads")
    
    print()

# Calculate normalized ratios
print("=" * 70)
print("  Depth-Adjusted Comparison")
print("=" * 70)
print()

print(f"{'Type':<20} {'WT':>12} {'B6':>15} {'A2':>15}")
print(f"{'':20} {'(base)':>12} {'(vs WT)':>15} {'(vs WT)':>15}")
print("-" * 62)

for jtype in ['cryptic_5ss', 'cryptic_3ss', 'intron_retention', 'novel']:
    wt_norm = raw_counts[jtype]['WT'] / (DEPTH['WT'] / 1_000_000)
    b6_norm = raw_counts[jtype]['B6'] / (DEPTH['B6'] / 1_000_000)
    a2_norm = raw_counts[jtype]['A2'] / (DEPTH['A2'] / 1_000_000)
    
    b6_vs_wt = ((b6_norm / wt_norm) - 1) * 100 if wt_norm > 0 else 0
    a2_vs_wt = ((a2_norm / wt_norm) - 1) * 100 if wt_norm > 0 else 0
    
    print(f"{jtype:<20} {wt_norm:>10.1f}   {b6_norm:>8.1f} ({b6_vs_wt:+6.0f}%)   {a2_norm:>8.1f} ({a2_vs_wt:+6.0f}%)")

print()
print("=" * 70)
print("  VERDICT")
print("=" * 70)
print()

# Check if differences are still significant after normalization
cryptic5_wt = raw_counts['cryptic_5ss']['WT'] / (DEPTH['WT'] / 1_000_000)
cryptic5_b6 = raw_counts['cryptic_5ss']['B6'] / (DEPTH['B6'] / 1_000_000)
cryptic5_a2 = raw_counts['cryptic_5ss']['A2'] / (DEPTH['A2'] / 1_000_000)

b6_change = ((cryptic5_b6 / cryptic5_wt) - 1) * 100
a2_change = ((cryptic5_a2 / cryptic5_wt) - 1) * 100

if abs(b6_change) < 20 and abs(a2_change) < 20:
    print("✅ After depth normalization: NO SIGNIFICANT DIFFERENCE")
    print("   Original difference explained by sequencing depth")
    print()
    print("   Manuscript statement:")
    print('   "No significant difference in cryptic splice site usage')
    print('    was detected after normalizing for sequencing depth."')
elif b6_change > 50 or a2_change > 50:
    print("⚠️ After depth normalization: DIFFERENCE PERSISTS")
    print(f"   B6: {b6_change:+.0f}%, A2: {a2_change:+.0f}%")
    print("   Biological signal may be present")
else:
    print("⚠️ After depth normalization: MODEST DIFFERENCE")
    print(f"   B6: {b6_change:+.0f}%, A2: {a2_change:+.0f}%")
    print("   Further validation needed")
