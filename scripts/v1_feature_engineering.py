"""
V1 Module: 3D-aware variant scoring — Step 1: Feature Engineering

Enriches HBB_Unified_Atlas_95kb.csv with structural-distance features
for downstream ML scoring (XGBoost / LogReg).

Input:  results/HBB_Unified_Atlas_95kb.csv
Output: analysis/v1_hbb_features.csv  (ML-ready feature matrix)
        analysis/v1_feature_summary.json (feature statistics)
"""

import json
import csv
import math
from pathlib import Path

# === Paths ===
ROOT = Path("D:/ДНК")
ATLAS_PATH = ROOT / "results" / "HBB_Unified_Atlas_95kb.csv"
CONFIG_PATH = ROOT / "config" / "locus" / "hbb_95kb_subTAD.json"
OUTPUT_CSV = ROOT / "analysis" / "v1_hbb_features.csv"
OUTPUT_JSON = ROOT / "analysis" / "v1_feature_summary.json"

# === Load locus config for regulatory element positions ===
with open(CONFIG_PATH) as f:
    config = json.load(f)

# WHY: features are nested under config["features"] in the locus config
features = config.get("features", config)

# Extract enhancer positions
enhancer_positions = []
enhancer_names = []
for e in features.get("enhancers", []):
    pos = e.get("position") or e.get("pos")
    if pos:
        enhancer_positions.append(int(pos))
        enhancer_names.append(e.get("name", "unknown"))

# Extract CTCF positions
ctcf_positions = []
for c in features.get("ctcf_sites", []):
    pos = c.get("position") or c.get("pos")
    if pos:
        ctcf_positions.append(int(pos))

# LCR hypersensitive sites (from config enhancers)
lcr_positions = [p for p, n in zip(enhancer_positions, enhancer_names) if "LCR" in n or "HS" in n]

# HBB promoter/TSS
hbb_tss = 5226268  # from config
hbb_gene_start = 5225464
hbb_gene_end = 5227079

# Gene positions for distance features
gene_positions = {g["name"]: (g["start"], g["end"]) for g in config.get("genes", [])}

print(f"Enhancers: {len(enhancer_positions)} — {list(zip(enhancer_names, enhancer_positions))}")
print(f"CTCF sites: {len(ctcf_positions)} — {ctcf_positions}")
print(f"LCR sites: {len(lcr_positions)} — {lcr_positions}")


# === Helper functions ===
def min_distance(pos: int, targets: list[int]) -> int:
    """Minimum absolute distance from pos to any target."""
    if not targets:
        return -1
    return min(abs(pos - t) for t in targets)


def is_in_gene(pos: int, start: int, end: int) -> bool:
    return start <= pos <= end


def safe_float(val: str, default: float = -1.0) -> float:
    try:
        v = float(val)
        return v if not math.isnan(v) else default
    except (ValueError, TypeError):
        return default


# === Category encoding ===
CATEGORIES = [
    "missense",
    "nonsense",
    "splice",
    "frameshift",
    "synonymous",
    "3_prime_UTR",
    "5_prime_UTR",
    "promoter",
    "other",
    "non_coding",
]


def encode_category(cat: str) -> dict[str, int]:
    """One-hot encode variant category."""
    cat_lower = cat.lower().strip()
    result = {}
    for c in CATEGORIES:
        key = f"cat_{c}"
        result[key] = 1 if c in cat_lower else 0
    # WHY: ensure at least one category is set; fallback to "other"
    if sum(result.values()) == 0:
        result["cat_other"] = 1
    return result


# === Process atlas ===
print(f"\nReading atlas: {ATLAS_PATH}")

rows_out = []
stats = {
    "total_variants": 0,
    "pathogenic": 0,
    "benign": 0,
    "pearls": 0,
    "features_added": [],
    "category_distribution": {},
}

with open(ATLAS_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        pos = int(row["Position_GRCh38"])
        category = row.get("Category", "other")
        label = row.get("Label", "")
        is_pathogenic = "Pathogenic" in label

        # === Original features (clean) ===
        ssim = safe_float(row.get("ARCHCODE_SSIM", ""))
        lssim = safe_float(row.get("ARCHCODE_LSSIM", ""))
        delta_ins = safe_float(row.get("ARCHCODE_DeltaInsulation", ""))
        loop_int = safe_float(row.get("ARCHCODE_LoopIntegrity", ""))
        vep_score = safe_float(row.get("VEP_Score", ""))
        sift_score = safe_float(row.get("SIFT_Score", ""))
        cadd_phred = safe_float(row.get("CADD_Phred", ""))
        is_pearl = row.get("Pearl", "false").lower() == "true"

        # === New distance features ===
        dist_to_lcr = min_distance(pos, lcr_positions)
        dist_to_nearest_enhancer = min_distance(pos, enhancer_positions)
        dist_to_nearest_ctcf = min_distance(pos, ctcf_positions)
        dist_to_tss = abs(pos - hbb_tss)
        in_hbb_gene = 1 if is_in_gene(pos, hbb_gene_start, hbb_gene_end) else 0

        # Log-scaled distances (more informative for ML)
        log_dist_lcr = math.log10(dist_to_lcr + 1)
        log_dist_enhancer = math.log10(dist_to_nearest_enhancer + 1)
        log_dist_ctcf = math.log10(dist_to_nearest_ctcf + 1)
        log_dist_tss = math.log10(dist_to_tss + 1)

        # === Derived structural features ===
        # Delta from WT baseline (1.0 = no change)
        delta_ssim = 1.0 - ssim if ssim >= 0 else -1.0
        delta_lssim = 1.0 - lssim if lssim >= 0 else -1.0

        # Structural disruption ratio
        struct_disruption = delta_lssim / (delta_ssim + 1e-8) if delta_ssim > 0 else 0.0

        # === Category encoding ===
        cat_encoded = encode_category(category)

        # === Build output row ===
        out = {
            "ClinVar_ID": row["ClinVar_ID"],
            "Position_GRCh38": pos,
            "Category": category,
            # Target
            "label": 1 if is_pathogenic else 0,
            "is_pearl": 1 if is_pearl else 0,
            # Original structural features
            "ssim": round(ssim, 6),
            "lssim": round(lssim, 6),
            "delta_ssim": round(delta_ssim, 6),
            "delta_lssim": round(delta_lssim, 6),
            "delta_insulation": round(delta_ins, 6),
            "loop_integrity": round(loop_int, 6),
            "struct_disruption_ratio": round(struct_disruption, 4),
            # Sequence-based scores
            "vep_score": round(vep_score, 4),
            "sift_score": round(sift_score, 4),
            "cadd_phred": round(cadd_phred, 2),
            # Distance features
            "dist_to_lcr": dist_to_lcr,
            "dist_to_nearest_enhancer": dist_to_nearest_enhancer,
            "dist_to_nearest_ctcf": dist_to_nearest_ctcf,
            "dist_to_tss": dist_to_tss,
            "in_hbb_gene": in_hbb_gene,
            # Log distances
            "log_dist_lcr": round(log_dist_lcr, 4),
            "log_dist_enhancer": round(log_dist_enhancer, 4),
            "log_dist_ctcf": round(log_dist_ctcf, 4),
            "log_dist_tss": round(log_dist_tss, 4),
        }
        # Add category one-hot
        out.update(cat_encoded)

        rows_out.append(out)

        # Stats
        stats["total_variants"] += 1
        if is_pathogenic:
            stats["pathogenic"] += 1
        else:
            stats["benign"] += 1
        if is_pearl:
            stats["pearls"] += 1
        stats["category_distribution"][category] = (
            stats["category_distribution"].get(category, 0) + 1
        )

# === Write output CSV ===
if rows_out:
    fieldnames = list(rows_out[0].keys())
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"\nWrote {len(rows_out)} rows to {OUTPUT_CSV}")
    print(f"  Columns: {len(fieldnames)}")

# === Feature statistics ===
# Compute min/max/mean for numeric features
numeric_features = [
    "ssim",
    "lssim",
    "delta_ssim",
    "delta_lssim",
    "delta_insulation",
    "loop_integrity",
    "struct_disruption_ratio",
    "vep_score",
    "sift_score",
    "cadd_phred",
    "dist_to_lcr",
    "dist_to_nearest_enhancer",
    "dist_to_nearest_ctcf",
    "dist_to_tss",
    "log_dist_lcr",
    "log_dist_enhancer",
    "log_dist_ctcf",
    "log_dist_tss",
]

feature_stats = {}
for feat in numeric_features:
    vals = [r[feat] for r in rows_out if r[feat] != -1.0]
    if vals:
        feature_stats[feat] = {
            "min": round(min(vals), 6),
            "max": round(max(vals), 6),
            "mean": round(sum(vals) / len(vals), 6),
            "n_valid": len(vals),
            "n_missing": len(rows_out) - len(vals),
        }

stats["features_added"] = [
    "dist_to_lcr",
    "dist_to_nearest_enhancer",
    "dist_to_nearest_ctcf",
    "dist_to_tss",
    "in_hbb_gene",
    "log_dist_lcr",
    "log_dist_enhancer",
    "log_dist_ctcf",
    "log_dist_tss",
    "delta_ssim",
    "delta_lssim",
    "struct_disruption_ratio",
] + [f"cat_{c}" for c in CATEGORIES]
stats["feature_statistics"] = feature_stats
stats["total_features"] = len(fieldnames) - 3  # minus ID, Position, Category

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)
print(f"Wrote summary to {OUTPUT_JSON}")

# === Quick report ===
print(f"\n{'=' * 60}")
print(f"V1 Feature Engineering — Summary")
print(f"{'=' * 60}")
print(f"Total variants:  {stats['total_variants']}")
print(f"Pathogenic:      {stats['pathogenic']}")
print(f"Benign:          {stats['benign']}")
print(f"Pearls:          {stats['pearls']}")
print(f"Total features:  {stats['total_features']}")
print(f"Categories:      {stats['category_distribution']}")
print(f"\nKey distance stats:")
for feat in ["dist_to_lcr", "dist_to_nearest_enhancer", "dist_to_nearest_ctcf", "dist_to_tss"]:
    s = feature_stats.get(feat, {})
    print(f"  {feat}: min={s.get('min')}, max={s.get('max')}, mean={s.get('mean', 0):.0f}")
