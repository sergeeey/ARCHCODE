#!/usr/bin/env python3
"""
Cross-validation: ARCHCODE LSSIM vs Kircher 2019 MPRA functional scores.

MaveDB: urn:mavedb:00000018-a-1
Paper: Kircher et al., Nature Communications 2019; 10:3583
MPRA region: chr11:5,227,022-5,227,208 (GRCh38), 187 bp HBB promoter
Cell line: HEL 92.1.7 (erythroid)
"""

import re
import json
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DATA = ROOT / "data"

# ── 1. Load MPRA data ──────────────────────────────────────────────
mpra_raw = pd.read_csv(DATA / "mpra_kircher_hbb_raw.csv")
print(f"MPRA records: {len(mpra_raw)}")
print(f"Score range: {mpra_raw['score'].min():.3f} to {mpra_raw['score'].max():.3f}")
print(f"Significant (p<0.05): {(mpra_raw['p-value'] < 0.05).sum()}/{len(mpra_raw)}")

# ── 2. Parse HGVS notation ─────────────────────────────────────────
parsed = []
for _, row in mpra_raw.iterrows():
    hgvs = str(row['hgvs_nt'])
    # n.POS= (wildtype)
    m = re.match(r'n\.(\d+)=$', hgvs)
    if m:
        parsed.append({'mpra_pos': int(m.group(1)), 'ref': None, 'alt': None,
                        'wt': True, 'score': row['score'], 'pval': row['p-value']})
        continue
    # n.POSREF>ALT (substitution)
    m = re.match(r'n\.(\d+)([ACGT])>([ACGT])$', hgvs)
    if m:
        parsed.append({'mpra_pos': int(m.group(1)), 'ref': m.group(2), 'alt': m.group(3),
                        'wt': False, 'score': row['score'], 'pval': row['p-value']})
        continue
    # n.POSdel (deletion)
    m = re.match(r'n\.(\d+)del', hgvs)
    if m:
        parsed.append({'mpra_pos': int(m.group(1)), 'ref': None, 'alt': 'del',
                        'wt': False, 'score': row['score'], 'pval': row['p-value']})
        continue

mpra_df = pd.DataFrame(parsed)
print(f"\nParsed: {len(mpra_df)} variants")
print(f"MPRA position range: n.{mpra_df['mpra_pos'].min()} to n.{mpra_df['mpra_pos'].max()}")
print(f"Substitutions: {len(mpra_df[(~mpra_df['wt']) & (mpra_df['alt'] != 'del')])}")

# ── 3. Map to genomic coordinates ──────────────────────────────────
# HBB is on MINUS strand. MPRA construct covers chr11:5,227,022-5,227,208
# The Kircher construct is 187 bp. HBB TSS ~5,227,071.
#
# For minus strand gene: construct is numbered 5'→3' in mRNA sense,
# which means n.1 = highest genomic coordinate = 5,227,208
# genomic_pos = 5,227,209 - mpra_pos
#
# Complement needed: construct ref/alt are on minus strand (coding strand)
# Genomic ref/alt are on plus strand

CONSTRUCT_START_GENOMIC = 5_227_208  # n.1 position
mpra_df['genomic_pos'] = CONSTRUCT_START_GENOMIC - (mpra_df['mpra_pos'] - 1)

COMP = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
mpra_df['genomic_ref'] = mpra_df['ref'].map(lambda x: COMP.get(x, x) if x else None)
mpra_df['genomic_alt'] = mpra_df['alt'].map(lambda x: COMP.get(x, x) if x and x != 'del' else x)

print(f"Genomic range: {mpra_df['genomic_pos'].min()}-{mpra_df['genomic_pos'].max()}")

# ── 4. Load ARCHCODE atlas ─────────────────────────────────────────
atlas = pd.read_csv(RESULTS / "HBB_Unified_Atlas_95kb.csv")
print(f"\nARCHCODE atlas: {len(atlas)} total variants")

# Filter to MPRA overlap region
gmin, gmax = mpra_df['genomic_pos'].min(), mpra_df['genomic_pos'].max()
atlas_ovlp = atlas[
    (atlas['Position_GRCh38'] >= gmin) &
    (atlas['Position_GRCh38'] <= gmax)
].copy()
print(f"Atlas variants in MPRA region ({gmin}-{gmax}): {len(atlas_ovlp)}")

# ── 5. Match by position + allele ──────────────────────────────────
# Try both complemented and direct matching, pick the one with more hits

def match_variants(atlas_df, mpra_df, complement=True):
    """Match atlas variants to MPRA scores."""
    matched = []
    for _, av in atlas_df.iterrows():
        pos = av['Position_GRCh38']
        ref, alt = str(av['Ref']), str(av['Alt'])
        if len(ref) != 1 or len(alt) != 1:
            continue

        alt_col = 'genomic_alt' if complement else 'alt'
        candidates = mpra_df[(mpra_df['genomic_pos'] == pos) & (mpra_df[alt_col] == alt)]

        if len(candidates) > 0:
            mm = candidates.iloc[0]
            matched.append({
                'ClinVar_ID': av['ClinVar_ID'],
                'Position': pos,
                'Ref': ref, 'Alt': alt,
                'Category': av['Category'],
                'Label': av['Label'],
                'Pearl': av.get('Pearl', False),
                'LSSIM': av['ARCHCODE_LSSIM'],
                'VEP_Score': av['VEP_Score'],
                'CADD_Phred': av.get('CADD_Phred', -1),
                'MPRA_score': mm['score'],
                'MPRA_pval': mm['pval'],
            })
    return pd.DataFrame(matched) if matched else pd.DataFrame()


match_comp = match_variants(atlas_ovlp, mpra_df, complement=True)
match_direct = match_variants(atlas_ovlp, mpra_df, complement=False)

print(f"\nComplemented match: {len(match_comp)}")
print(f"Direct match: {len(match_direct)}")

# Also try: position-only matching (ignore allele, take mean MPRA score per position)
subs = mpra_df[(~mpra_df['wt']) & (mpra_df['alt'] != 'del')]
pos_mpra = subs.groupby('genomic_pos').agg(
    mpra_mean_score=('score', 'mean'),
    mpra_min_score=('score', 'min'),
    mpra_n=('score', 'count'),
).reset_index()

atlas_pos_match = atlas_ovlp.merge(pos_mpra, left_on='Position_GRCh38', right_on='genomic_pos', how='inner')
print(f"Position-only match (any allele): {len(atlas_pos_match)}")

# Use the best approach
if len(match_comp) >= len(match_direct) and len(match_comp) > 0:
    matched_df = match_comp
    method = "complemented"
elif len(match_direct) > 0:
    matched_df = match_direct
    method = "direct"
else:
    matched_df = None
    method = "none"

# ── 6. Correlation analysis ────────────────────────────────────────
print("\n" + "=" * 60)

# Allele-specific match
if matched_df is not None and len(matched_df) > 0:
    print(f"ALLELE-SPECIFIC MATCH ({method}): n = {len(matched_df)}")
    matched_df.to_csv(RESULTS / "mpra_archcode_crossvalidation.csv", index=False)

    r, p = stats.pearsonr(matched_df['LSSIM'], matched_df['MPRA_score'])
    rho, rho_p = stats.spearmanr(matched_df['LSSIM'], matched_df['MPRA_score'])
    print(f"  Pearson r = {r:.4f}, p = {p:.2e}")
    print(f"  Spearman rho = {rho:.4f}, p = {rho_p:.2e}")
    print(f"  Pearl variants: {(matched_df['Pearl'] == True).sum()}")
    print(f"  Pathogenic: {(matched_df['Label'] == 'Pathogenic').sum()}")
    print(f"  Benign: {(matched_df['Label'] == 'Benign').sum()}")
    print()
    print(matched_df[['ClinVar_ID', 'Position', 'Ref', 'Alt', 'Category', 'Label',
                       'Pearl', 'LSSIM', 'MPRA_score', 'MPRA_pval']].to_string(index=False))

# Position-level match (mean MPRA score per position)
position_pearson_r, position_pearson_p = None, None
position_spearman_rho, position_spearman_p = None, None
position_n = 0
if len(atlas_pos_match) > 0:
    print(f"\nPOSITION-LEVEL MATCH: n = {len(atlas_pos_match)}")
    # For SNVs only
    snv_match = atlas_pos_match[atlas_pos_match['Ref'].str.len() == 1].copy()
    snv_match = snv_match[snv_match['Alt'].str.len() == 1]
    print(f"  SNVs only: {len(snv_match)}")

    if len(snv_match) > 2:
        r2, p2 = stats.pearsonr(snv_match['ARCHCODE_LSSIM'], snv_match['mpra_mean_score'])
        rho2, rho2_p = stats.spearmanr(snv_match['ARCHCODE_LSSIM'], snv_match['mpra_mean_score'])
        position_pearson_r, position_pearson_p = r2, p2
        position_spearman_rho, position_spearman_p = rho2, rho2_p
        position_n = len(snv_match)
        print(f"  Pearson r = {r2:.4f}, p = {p2:.2e}")
        print(f"  Spearman rho = {rho2:.4f}, p = {rho2_p:.2e}")
        print(f"  Pearl: {(snv_match['Pearl'] == True).sum()}")
        print(f"  Path: {(snv_match['Label'] == 'Pathogenic').sum()}, Ben: {(snv_match['Label'] == 'Benign').sum()}")

        snv_match.to_csv(RESULTS / "mpra_archcode_position_match.csv", index=False)
        print(f"  Saved to results/mpra_archcode_position_match.csv")

# ── 6b. Position-aggregated: one row per position (min LSSIM vs mean MPRA) ──
position_aggregated_spearman_rho = None
position_aggregated_spearman_p = None
position_aggregated_n = 0
min_lssim_per_pos = atlas_ovlp.groupby("Position_GRCh38")["ARCHCODE_LSSIM"].min().reset_index()
min_lssim_per_pos.columns = ["genomic_pos", "min_lssim"]
agg_pos = pos_mpra.merge(min_lssim_per_pos, on="genomic_pos", how="inner")
if len(agg_pos) > 2:
    rho_agg, p_agg = stats.spearmanr(agg_pos["mpra_mean_score"], agg_pos["min_lssim"])
    position_aggregated_spearman_rho = float(rho_agg)
    position_aggregated_spearman_p = float(p_agg)
    position_aggregated_n = int(len(agg_pos))
    print(f"\nPOSITION-AGGREGATED (one row per position, min LSSIM): n = {position_aggregated_n}")
    print(f"  Spearman rho = {rho_agg:.4f}, p = {p_agg:.2e}")

# ── 7. Full MPRA landscape: ARCHCODE LSSIM for ALL MPRA positions ──
# For every position in the MPRA construct, calculate mean ARCHCODE LSSIM
# across all atlas variants at that position
print("\n" + "=" * 60)
print("FULL LANDSCAPE: MPRA score distribution at pearl vs non-pearl positions")

# Get unique pearl positions
pearl_positions = set(atlas_ovlp[atlas_ovlp['Pearl'] == True]['Position_GRCh38'].values)
print(f"Pearl positions in MPRA region: {sorted(pearl_positions)}")

# MPRA scores at pearl positions vs non-pearl positions
mpra_subs = mpra_df[(~mpra_df['wt']) & (mpra_df['alt'] != 'del')].copy()
mpra_subs['is_pearl_position'] = mpra_subs['genomic_pos'].isin(pearl_positions)

pearl_mpra = mpra_subs[mpra_subs['is_pearl_position']]['score']
nonpearl_mpra = mpra_subs[~mpra_subs['is_pearl_position']]['score']

if len(pearl_mpra) > 0 and len(nonpearl_mpra) > 0:
    print(f"\nMPRA scores at PEARL positions (n={len(pearl_mpra)}):")
    print(f"  Mean: {pearl_mpra.mean():.4f}, Median: {pearl_mpra.median():.4f}")
    print(f"MPRA scores at NON-PEARL positions (n={len(nonpearl_mpra)}):")
    print(f"  Mean: {nonpearl_mpra.mean():.4f}, Median: {nonpearl_mpra.median():.4f}")

    u_stat, u_p = stats.mannwhitneyu(pearl_mpra, nonpearl_mpra, alternative='two-sided')
    print(f"\nMann-Whitney U: U={u_stat:.0f}, p={u_p:.4e}")
    print(f"Effect: MPRA at pearl positions {'MORE' if pearl_mpra.mean() < nonpearl_mpra.mean() else 'LESS'} disruptive")

# ── 8. Summary JSON ────────────────────────────────────────────────
summary = {
    "analysis": "MPRA_ARCHCODE_crossvalidation",
    "mpra_source": "Kircher et al. 2019, Nat Commun 10:3583",
    "mavedb_urn": "urn:mavedb:00000018-a-1",
    "mpra_region_grch38": "chr11:5,227,022-5,227,208",
    "mpra_cell_line": "HEL 92.1.7 (erythroid)",
    "total_mpra_variants": len(mpra_raw),
    "total_mpra_substitutions": len(subs),
    "atlas_variants_in_region": len(atlas_ovlp),
    "allele_specific_matches": len(matched_df) if matched_df is not None else 0,
    "position_level_matches": len(atlas_pos_match),
    "pearl_positions_in_mpra": sorted([int(x) for x in pearl_positions]),
    "n_pearl_positions": len(pearl_positions),
}

if matched_df is not None and len(matched_df) > 0:
    summary["allele_pearson_r"] = float(r)
    summary["allele_pearson_p"] = float(p)
    summary["allele_spearman_rho"] = float(rho)
    summary["allele_spearman_p"] = float(rho_p)

if len(pearl_mpra) > 0:
    summary["mpra_pearl_mean"] = float(pearl_mpra.mean())
    summary["mpra_nonpearl_mean"] = float(nonpearl_mpra.mean())
    summary["mpra_pearl_vs_nonpearl_U"] = float(u_stat)
    summary["mpra_pearl_vs_nonpearl_p"] = float(u_p)

if position_pearson_r is not None:
    summary["position_pearson_r"] = float(position_pearson_r)
    summary["position_pearson_p"] = float(position_pearson_p)
    summary["position_spearman_rho"] = float(position_spearman_rho)
    summary["position_spearman_p"] = float(position_spearman_p)
    summary["position_n"] = int(position_n)

if position_aggregated_spearman_rho is not None:
    summary["position_aggregated_spearman_rho"] = position_aggregated_spearman_rho
    summary["position_aggregated_spearman_p"] = position_aggregated_spearman_p
    summary["position_aggregated_n"] = position_aggregated_n

with open(RESULTS / "mpra_crossvalidation_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved summary to results/mpra_crossvalidation_summary.json")

# ── 9. Scatter plot (LSSIM vs MPRA) for Fig ─────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if matched_df is not None and len(matched_df) > 0:
        fig, ax = plt.subplots()
        ax.scatter(matched_df["LSSIM"], matched_df["MPRA_score"], alpha=0.7)
        ax.set_xlabel("ARCHCODE LSSIM")
        ax.set_ylabel("MPRA functional score")
        rho_val = summary.get("allele_spearman_rho", 0)
        p_val = summary.get("allele_spearman_p", 1.0)
        ax.set_title(f"Kircher et al. 2019 HBB promoter chr11:5,227,022-5,227,208 (n={len(matched_df)}); Spearman rho={rho_val:.3f}, p={p_val:.2e}")
        fig.savefig(RESULTS / "mpra_archcode_scatter.png", dpi=150)
        plt.close()
        print(f"Saved scatter to results/mpra_archcode_scatter.png")
except Exception as e:
    print(f"Scatter plot skipped: {e}")
