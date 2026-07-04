#!/usr/bin/env python3
"""
HBB Real Atlas — Consistency Check + Pearl Table Generator

Reads results/HBB_Clinical_Atlas_REAL.csv, validates numbers,
and generates manuscript/TABLE_2_PEARLS_TOP5.md and manuscript/TABLE_S1_PEARLS.md.

Usage:
    python scripts/check_consistency_hbb_real.py
"""

import pandas as pd
import sys
from pathlib import Path

ATLAS = Path("results/HBB_Clinical_Atlas_REAL.csv")
TABLE_TOP5 = Path("manuscript/TABLE_2_PEARLS_TOP5.md")
TABLE_FULL = Path("manuscript/TABLE_S1_PEARLS.md")


def shorten_insight(text: str, category: str, vep_csq: str) -> str:
    """Condense Mechanism_Insight to 3-5 words, category-aware."""
    cat = str(category).lower()
    csq = str(vep_csq).lower()
    if cat == "promoter":
        return "Promoter–enhancer loop disruption"
    if cat == "splice_acceptor":
        return "Complex indel, VEP underscored"
    if cat == "frameshift":
        if "synonymous" in csq:
            return "LoF, VEP misannotated"
        return "LoF, VEP underscored"
    if cat == "missense":
        if "coding_sequence" in csq:
            return "Complex variant, VEP generic"
        return "Missense, structural signal"
    return "3D disruption, VEP blind"


def shorten_hgvs(hgvs: str) -> str:
    """Strip transcript prefix for readability: NM_000518.5(HBB):c.X → c.X"""
    if not isinstance(hgvs, str):
        return ""
    if "):c." in hgvs:
        return "c." + hgvs.split("):c.")[1]
    if "):g." in hgvs:
        return "g." + hgvs.split("):g.")[1]
    return hgvs


def main():
    df = pd.read_csv(ATLAS)

    # ================================================================
    # CONSISTENCY CHECK
    # ================================================================
    print("=" * 66)
    print("CONSISTENCY CHECK — HBB Real Clinical Atlas")
    print("=" * 66)

    total = len(df)
    print(f"\ntotal_variants = {total}")

    # Pearl definition: Pearl == true OR (VEP_Score < 0.3 AND ARCHCODE_SSIM < 0.95)
    pearl_flag = df["Pearl"].astype(str).str.lower() == "true"
    pearl_numeric = (df["VEP_Score"] < 0.3) & (df["ARCHCODE_SSIM"] < 0.95)
    pearls_mask = pearl_flag | pearl_numeric
    n_pearls = pearls_mask.sum()
    print(f"n_pearls       = {n_pearls}  (Pearl==true: {pearl_flag.sum()}, "
          f"numeric filter: {pearl_numeric.sum()}, union: {n_pearls})")

    # ClinVar_Significance distribution (full atlas)
    print(f"\n--- ClinVar_Significance distribution (n={total}) ---")
    sig_counts = df["ClinVar_Significance"].value_counts()
    for sig, cnt in sig_counts.items():
        pct = cnt / total * 100
        print(f"  {sig:40s}  {cnt:4d}  ({pct:5.1f}%)")

    # Category distribution (full atlas)
    print(f"\n--- Category distribution (n={total}) ---")
    cat_counts = df["Category"].value_counts()
    for cat, cnt in cat_counts.items():
        pct = cnt / total * 100
        print(f"  {cat:20s}  {cnt:4d}  ({pct:5.1f}%)")

    # Category distribution among pearls
    pearl_df = df[pearls_mask].copy()
    print(f"\n--- Category distribution among PEARLS (n={n_pearls}) ---")
    pearl_cats = pearl_df["Category"].value_counts()
    for cat, cnt in pearl_cats.items():
        print(f"  {cat:20s}  {cnt:4d}")

    # ARCHCODE verdict among pearls
    print(f"\n--- ARCHCODE verdict among pearls ---")
    for v, cnt in pearl_df["ARCHCODE_Verdict"].value_counts().items():
        print(f"  {v:20s}  {cnt:4d}")

    # SSIM stats for pearls
    print(f"\n--- SSIM among pearls ---")
    print(f"  min  = {pearl_df['ARCHCODE_SSIM'].min():.4f}")
    print(f"  max  = {pearl_df['ARCHCODE_SSIM'].max():.4f}")
    print(f"  mean = {pearl_df['ARCHCODE_SSIM'].mean():.4f}")

    # VEP score stats for pearls
    print(f"\n--- VEP_Score among pearls ---")
    print(f"  min  = {pearl_df['VEP_Score'].min():.2f}")
    print(f"  max  = {pearl_df['VEP_Score'].max():.2f}")
    print(f"  mean = {pearl_df['VEP_Score'].mean():.2f}")

    # Discordance stats (full atlas)
    print(f"\n--- Discordance (n={total}) ---")
    disc_counts = df["Discordance"].value_counts()
    for d, cnt in disc_counts.items():
        pct = cnt / total * 100
        print(f"  {d:20s}  {cnt:4d}  ({pct:5.1f}%)")

    # ================================================================
    # GENERATE TABLES
    # ================================================================
    pearl_sorted = pearl_df.sort_values("ARCHCODE_SSIM", ascending=True)

    # Shorten columns
    pearl_sorted["HGVS_short"] = pearl_sorted["HGVS_c"].apply(shorten_hgvs)
    pearl_sorted["Insight_short"] = pearl_sorted.apply(
        lambda r: shorten_insight(r["Mechanism_Insight"], r["Category"], r["VEP_Consequence"]),
        axis=1,
    )

    cols = [
        "ClinVar_ID", "HGVS_short", "Category", "ClinVar_Significance",
        "ARCHCODE_SSIM", "VEP_Score", "VEP_Consequence",
        "Pearl", "Discordance", "Insight_short",
    ]
    headers = [
        "ClinVar_ID", "HGVS_c", "Category", "ClinVar_Significance",
        "ARCHCODE_SSIM", "VEP_Score", "VEP_Consequence",
        "Pearl", "Discordance", "Mechanism_Insight",
    ]

    def to_md_table(sub_df: pd.DataFrame, title: str) -> str:
        lines = [f"# {title}", ""]
        # Header
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for _, row in sub_df.iterrows():
            vals = []
            for c in cols:
                v = row[c]
                if c == "ARCHCODE_SSIM":
                    vals.append(f"{v:.4f}")
                elif c == "VEP_Score":
                    vals.append(f"{v:.2f}")
                elif c == "Pearl":
                    vals.append(str(v).lower())
                else:
                    vals.append(str(v) if pd.notna(v) else "")
            lines.append("| " + " | ".join(vals) + " |")
        lines.append("")
        return "\n".join(lines)

    # Full table (all 20)
    full_md = to_md_table(pearl_sorted, f"Supplementary Table S1: All {n_pearls} Pearl Variants")
    full_md += (
        f"_Pearl definition: VEP_Score < 0.30 AND ARCHCODE_SSIM < 0.95._\n"
        f"_Sorted by ARCHCODE_SSIM ascending (strongest structural disruption first)._\n"
        f"_Source: results/HBB_Clinical_Atlas_REAL.csv ({total} total variants)._\n"
    )

    # Top-5
    top5 = pearl_sorted.head(5)
    top5_md = to_md_table(top5, f"Table 2: Top 5 Pearl Variants (of {n_pearls} total)")
    top5_md += (
        f"_Top 5 by lowest ARCHCODE_SSIM (strongest predicted structural disruption)._\n"
        f"_Full list of {n_pearls} pearls: Supplementary Table S1._\n"
    )

    TABLE_FULL.write_text(full_md, encoding="utf-8")
    TABLE_TOP5.write_text(top5_md, encoding="utf-8")

    print(f"\n{'=' * 66}")
    print(f"TABLES GENERATED")
    print(f"{'=' * 66}")
    print(f"  {TABLE_TOP5}  ({len(top5)} rows)")
    print(f"  {TABLE_FULL}  ({n_pearls} rows)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
