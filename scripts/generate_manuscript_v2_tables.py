#!/usr/bin/env python3
"""
ARCHCODE Manuscript v2 Tables — Pure Falsification Paper.

Generates 4 publication-quality tables for the falsification manuscript:
- Table 1: Category-specific pathogenicity rates
- Table 2: Locus-specific AUC comparison
- Table 3: AlphaGenome mechanism-specific validation
- Table 4: Hypothesis kill summary

Output: manuscript/tables/table{N}_{name}.csv + .tex

Usage:
    python scripts/generate_manuscript_v2_tables.py
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
TABLES = ROOT / "manuscript" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def load_atlas_data():
    """Load all 13 loci atlas data and merge."""
    atlas_files = [
        "HBB_Unified_Atlas.csv",
        "TP53_Unified_Atlas_300kb.csv",
        "BRCA1_Unified_Atlas_brca1.csv",
        "CFTR_Unified_Atlas_317kb.csv",
        "MLH1_Unified_Atlas_300kb.csv",
        "TERT_Unified_Atlas_300kb.csv",
        "GJB2_Unified_Atlas_300kb.csv",
        "GATA1_Unified_Atlas_300kb.csv",
        "PTEN_Unified_Atlas_300kb.csv",
        "HBA1_Unified_Atlas_300kb.csv",
        "BCL11A_Unified_Atlas_300kb.csv",
        "LDLR_Unified_Atlas_300kb.csv",
        "SCN5A_Unified_Atlas_400kb.csv",
    ]

    dfs = []
    for fname in atlas_files:
        path = RESULTS / fname
        if path.exists():
            df = pd.read_csv(path)
            df["Locus"] = fname.split("_")[0]
            dfs.append(df)
        else:
            print(f"  Warning: {fname} not found, skipping")

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════
# Table 1: Category-specific pathogenicity rates
# ══════════════════════════════════════════════════════════════════════
def table1_category_rates():
    print("\n[Table 1] Category-specific pathogenicity rates...")
    df = load_atlas_data()

    if df.empty:
        print("  ERROR: No atlas data found")
        return

    df = df[df["Label"].isin(["Pathogenic", "Benign"])].copy()

    # Group by category
    categories = [
        "splice_donor",
        "nonsense",
        "frameshift",
        "splice_acceptor",
        "splice",
        "promoter",
        "missense",
        "inframe_deletion",
        "inframe_indel",
        "splice_region",
        "5_prime_UTR",
        "3_prime_UTR",
        "intronic",
        "synonymous",
        "other",
    ]

    rows = []
    for cat in categories:
        df_cat = df[df["Category"] == cat]
        if len(df_cat) == 0:
            continue

        n_total = len(df_cat)
        n_path = len(df_cat[df_cat["Label"] == "Pathogenic"])
        n_ben = len(df_cat[df_cat["Label"] == "Benign"])
        path_rate = n_path / n_total if n_total > 0 else 0

        rows.append(
            {
                "Category": cat.replace("_", " "),
                "Pathogenic": n_path,
                "Benign": n_ben,
                "Total": n_total,
                "Pathogenic_Rate": f"{path_rate:.1%}",
            }
        )

    table1 = pd.DataFrame(rows)

    # Save
    table1.to_csv(TABLES / "table1_category_rates.csv", index=False)

    # LaTeX format
    latex = table1.to_latex(
        index=False,
        escape=False,
        caption="Category-specific pathogenicity rates (13 loci, n=32,201)",
        label="tab:category_rates",
    )
    (TABLES / "table1_category_rates.tex").write_text(latex)

    print(f"  Saved: table1_category_rates.csv + .tex")
    print(f"  Categories: {len(rows)}, Total variants: {table1['Total'].sum()}")


# ══════════════════════════════════════════════════════════════════════
# Table 2: Locus-specific AUC comparison
# ══════════════════════════════════════════════════════════════════════
def table2_locus_auc():
    print("\n[Table 2] Locus-specific AUC comparison...")
    df = load_atlas_data()

    if df.empty:
        print("  ERROR: No atlas data found")
        return

    df = df[df["Label"].isin(["Pathogenic", "Benign"])].copy()

    from sklearn.metrics import roc_auc_score
    from sklearn.linear_model import LogisticRegression

    loci = df["Locus"].unique()
    rows = []

    for locus in loci:
        df_locus = df[df["Locus"] == locus].copy()
        if len(df_locus) < 10:
            continue

        y = (df_locus["Label"] == "Pathogenic").astype(int)
        if y.nunique() < 2:
            continue

        # Category-only
        cat_dummies = pd.get_dummies(df_locus["Category"], prefix="cat")
        lr_cat = LogisticRegression(max_iter=1000, random_state=42)
        lr_cat.fit(cat_dummies, y)
        y_pred_cat = lr_cat.predict_proba(cat_dummies)[:, 1]
        auc_cat = roc_auc_score(y, y_pred_cat)

        # Category + LSSIM
        X_comb = cat_dummies.copy()
        X_comb["LSSIM"] = df_locus["ARCHCODE_LSSIM"].fillna(df_locus["ARCHCODE_LSSIM"].median())
        lr_comb = LogisticRegression(max_iter=1000, random_state=42)
        lr_comb.fit(X_comb, y)
        y_pred_comb = lr_comb.predict_proba(X_comb)[:, 1]
        auc_comb = roc_auc_score(y, y_pred_comb)

        delta_auc = auc_comb - auc_cat

        rows.append(
            {
                "Locus": locus,
                "n_variants": len(df_locus),
                "Category_only_AUC": f"{auc_cat:.3f}",
                "Category_LSSIM_AUC": f"{auc_comb:.3f}",
                "ΔAUC": f"{delta_auc:+.4f}",
            }
        )

    table2 = pd.DataFrame(rows)
    table2 = table2.sort_values("n_variants", ascending=False).reset_index(drop=True)

    # Save
    table2.to_csv(TABLES / "table2_locus_auc.csv", index=False)

    latex = table2.to_latex(
        index=False,
        escape=False,
        caption="Locus-specific AUC comparison: category vs category+LSSIM",
        label="tab:locus_auc",
    )
    (TABLES / "table2_locus_auc.tex").write_text(latex)

    print(f"  Saved: table2_locus_auc.csv + .tex")
    print(f"  Loci: {len(rows)}")


# ══════════════════════════════════════════════════════════════════════
# Table 3: AlphaGenome mechanism-specific validation
# ══════════════════════════════════════════════════════════════════════
def table3_alphagenome_validation():
    print("\n[Table 3] AlphaGenome mechanism-specific validation...")

    # Data from ADR-029, ADR-030 (manually entered for now)
    rows = [
        {
            "Locus": "HBB",
            "Mechanism": "Regulatory",
            "Mean_ΔCAGE_Path": -0.18,
            "Mean_ΔCAGE_Ben": -0.032,
            "p_value": 4.0e-6,
            "Cohen_d": -1.53,
        },
        {
            "Locus": "MLH1",
            "Mechanism": "Regulatory",
            "Mean_ΔCAGE_Path": -0.15,
            "Mean_ΔCAGE_Ben": -0.041,
            "p_value": 0.022,
            "Cohen_d": -0.89,
        },
        {
            "Locus": "TERT",
            "Mechanism": "Regulatory (GOF)",
            "Mean_ΔCAGE_Path": +0.33,
            "Mean_ΔCAGE_Ben": +0.001,
            "p_value": 0.001,
            "Cohen_d": +2.15,
        },
        {
            "Locus": "TP53",
            "Mechanism": "Coding",
            "Mean_ΔCAGE_Path": -0.009,
            "Mean_ΔCAGE_Ben": -0.011,
            "p_value": 0.84,
            "Cohen_d": 0.02,
        },
        {
            "Locus": "BRCA1",
            "Mechanism": "Coding",
            "Mean_ΔCAGE_Path": +0.002,
            "Mean_ΔCAGE_Ben": +0.001,
            "p_value": 0.67,
            "Cohen_d": 0.05,
        },
        {
            "Locus": "CFTR",
            "Mechanism": "Coding",
            "Mean_ΔCAGE_Path": -0.011,
            "Mean_ΔCAGE_Ben": -0.010,
            "p_value": 0.92,
            "Cohen_d": -0.01,
        },
        {
            "Locus": "GJB2",
            "Mechanism": "Coding",
            "Mean_ΔCAGE_Path": +0.005,
            "Mean_ΔCAGE_Ben": +0.003,
            "p_value": 0.78,
            "Cohen_d": 0.03,
        },
    ]

    table3 = pd.DataFrame(rows)

    # Format for display
    table3["Mean_ΔCAGE_Path_fmt"] = table3["Mean_ΔCAGE_Path"].apply(lambda x: f"{x:+.3f}")
    table3["Mean_ΔCAGE_Ben_fmt"] = table3["Mean_ΔCAGE_Ben"].apply(lambda x: f"{x:+.3f}")
    table3["p_value_fmt"] = table3["p_value"].apply(
        lambda x: f"{x:.2e}" if x < 0.01 else f"{x:.3f}"
    )
    table3["Cohen_d_fmt"] = table3["Cohen_d"].apply(lambda x: f"{x:+.2f}")

    # Result column
    table3["Result"] = table3.apply(
        lambda row: "Signal detected" if row["p_value"] < 0.05 else "Null (expected)", axis=1
    )

    table3_display = table3[
        [
            "Locus",
            "Mechanism",
            "Mean_ΔCAGE_Path_fmt",
            "Mean_ΔCAGE_Ben_fmt",
            "p_value_fmt",
            "Cohen_d_fmt",
            "Result",
        ]
    ].copy()

    table3_display.columns = [
        "Locus",
        "Mechanism",
        "Mean ΔCAGE (Path)",
        "Mean ΔCAGE (Ben)",
        "p-value",
        "Cohen's d",
        "Result",
    ]

    # Save
    table3_display.to_csv(TABLES / "table3_alphagenome_validation.csv", index=False)

    latex = table3_display.to_latex(
        index=False,
        escape=False,
        caption="AlphaGenome CAGE mechanism-specific validation (7 loci)",
        label="tab:alphagenome",
    )
    (TABLES / "table3_alphagenome_validation.tex").write_text(latex)

    print(f"  Saved: table3_alphagenome_validation.csv + .tex")
    print(f"  Loci: {len(rows)}, Mechanism-specific consistency: 7/7 (100%)")


# ══════════════════════════════════════════════════════════════════════
# Table 4: Hypothesis kill summary
# ══════════════════════════════════════════════════════════════════════
def table4_hypothesis_kills():
    print("\n[Table 4] Hypothesis kill summary...")

    rows = [
        {
            "Hypothesis": "H1: Within-category AUC",
            "Kill_Criterion": "AUC > 0.55 in ≥3 categories",
            "Test_Statistic": "Missense AUC = 0.568 (post-hoc)",
            "p_value": "N/A",
            "Verdict": "KILLED",
            "Kill_Date": "2026-04-07",
        },
        {
            "Hypothesis": "H2: Category artifact",
            "Kill_Criterion": "Category AUC < 0.90 OR ΔAUC ≥ 0.02",
            "Test_Statistic": "Category AUC = 0.982, ΔAUC = 0.001",
            "p_value": "N/A",
            "Verdict": "SURVIVED",
            "Kill_Date": "—",
        },
        {
            "Hypothesis": "H3: 73bp cluster",
            "Kill_Criterion": "Fisher p < 0.05 after category matching",
            "Test_Statistic": "OR = 1.3 (matched)",
            "p_value": "0.18",
            "Verdict": "KILLED",
            "Kill_Date": "2026-05-08",
        },
        {
            "Hypothesis": "H4: AlphaGenome concordance",
            "Kill_Criterion": "Spearman ρ ≥ 0.5",
            "Test_Statistic": "ρ = 0.077",
            "p_value": "0.67",
            "Verdict": "KILLED",
            "Kill_Date": "2026-05-09",
        },
        {
            "Hypothesis": "H5: TDRA router",
            "Kill_Criterion": "OR > 1.5 vs matched controls",
            "Test_Statistic": "OR = 1.02",
            "p_value": "0.996",
            "Verdict": "KILLED",
            "Kill_Date": "2026-04-15",
        },
        {
            "Hypothesis": "H6: Gene compactness",
            "Kill_Criterion": "Spearman ρ > 0.3 across loci",
            "Test_Statistic": "ρ = −0.05",
            "p_value": "0.90",
            "Verdict": "KILLED",
            "Kill_Date": "2026-05-09",
        },
    ]

    table4 = pd.DataFrame(rows)

    # Save
    table4.to_csv(TABLES / "table4_hypothesis_kills.csv", index=False)

    latex = table4.to_latex(
        index=False,
        escape=False,
        caption="Hypothesis kill summary: pre-registered criteria and outcomes",
        label="tab:hypothesis_kills",
    )
    (TABLES / "table4_hypothesis_kills.tex").write_text(latex)

    print(f"  Saved: table4_hypothesis_kills.csv + .tex")
    print(f"  Hypotheses: 6, Killed: 5, Survived: 1 (H2 category artifact)")


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("ARCHCODE Manuscript v2 Tables — Falsification Paper")
    print("=" * 60)

    table1_category_rates()
    table2_locus_auc()
    table3_alphagenome_validation()
    table4_hypothesis_kills()

    print("\n" + "=" * 60)
    generated = list(TABLES.glob("table*.*"))
    print(f"Generated {len(generated)} files in {TABLES}/")
    for f in sorted(generated):
        print(f"  {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
