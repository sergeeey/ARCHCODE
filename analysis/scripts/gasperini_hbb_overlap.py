"""
Gasperini et al. 2019 CRISPRi overlap analysis with ARCHCODE Q2b variants.

Source: GSE120861 (GEO)
Paper: Gasperini et al. 2019 (Cell) - "A Genome-wide Framework for Mapping
       Gene Regulation via Cellular Genetic Screens"
Cell line: K562
Data URL: https://ftp.ncbi.nlm.nih.gov/geo/series/GSE120nnn/GSE120861/suppl/
"""

import pandas as pd
import json
import os

ANALYSIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ANALYSIS_DIR, "gasperini2019")

HBB_CHR = "chr11"
HBB_START = 5_150_000
HBB_END = 5_350_000
GLOBIN_GENES = ["HBB", "HBD", "HBG1", "HBG2", "HBE1"]
CRISPRI_WINDOW = 500  # +/- bp from gRNA site center


def load_deg_results():
    """Load all differential expression results from at-scale screen."""
    path = os.path.join(DATA_DIR, "GSE120861_all_deg_results.at_scale.txt.gz")
    deg = pd.read_csv(path, sep="\t", compression="gzip", low_memory=False)
    deg["ts_start"] = pd.to_numeric(deg["target_site.start"], errors="coerce")
    deg["ts_stop"] = pd.to_numeric(deg["target_site.stop"], errors="coerce")
    return deg


def load_pair_table():
    """Load gene-gRNAgroup pair table."""
    path = os.path.join(DATA_DIR, "GSE120861_gene_gRNAgroup_pair_table.at_scale.txt.gz")
    pairs = pd.read_csv(path, sep="\t", compression="gzip", low_memory=False)
    pairs["gs_start"] = pd.to_numeric(pairs["gRNAgroup.start"], errors="coerce")
    pairs["gs_stop"] = pd.to_numeric(pairs["gRNAgroup.stop"], errors="coerce")
    return pairs


def filter_hbb_region(deg):
    """Filter DEG results for HBB region by gRNA site or target gene."""
    # By gRNA target site location
    by_site = deg[
        (deg["target_site.chr"] == HBB_CHR)
        & (deg["ts_start"] >= HBB_START)
        & (deg["ts_stop"] <= HBB_END)
    ]

    # By target gene name
    by_gene = deg[deg["gene_short_name"].isin(GLOBIN_GENES)]

    combined = pd.concat([by_site, by_gene]).drop_duplicates(subset="pairs4merge")
    return combined


def filter_hbb_pairs(pairs):
    """Filter pair table for HBB region."""
    return pairs[
        (
            (pairs["gRNAgroup.chr"] == HBB_CHR)
            & (pairs["gs_start"] >= HBB_START)
            & (pairs["gs_stop"] <= HBB_END)
        )
        | (pairs["targetgene_short_name"].isin(GLOBIN_GENES))
    ]


def check_q2b_overlap(q2b_hbb, grna_sites):
    """Check if Q2b variant positions overlap with CRISPRi gRNA target sites."""
    overlaps = []
    for _, var in q2b_hbb.iterrows():
        pos = var["Position"]
        for _, site in grna_sites.iterrows():
            center = (site["ts_start"] + site["ts_stop"]) / 2
            dist = abs(pos - center)
            if dist <= CRISPRI_WINDOW:
                overlaps.append(
                    {
                        "ClinVar_ID": var["ClinVar_ID"],
                        "Position": int(pos),
                        "Category": var["Category"],
                        "VEP_Consequence": var["VEP_Consequence"],
                        "gRNA_group": site["gRNA_group"],
                        "gRNA_center": int(center),
                        "distance_bp": int(dist),
                        "site_type": site["site_type"],
                    }
                )
    return overlaps


def main():
    # 1. Load DEG results
    print("=== Loading DEG results ===")
    deg = load_deg_results()
    print(f"Total enhancer-gene pairs tested: {len(deg):,}")

    # 2. Filter for HBB region
    hbb_all = filter_hbb_region(deg)
    print(f"HBB region pairs (by site or gene): {len(hbb_all)}")

    if len(hbb_all) > 0:
        cols = [
            "gRNA_group",
            "gene_short_name",
            "target_site.chr",
            "ts_start",
            "ts_stop",
            "site_type",
            "beta",
            "fold_change.transcript_remaining",
            "pvalue.empirical.adjusted",
            "quality_rank_grna",
        ]
        print("\n--- HBB region CRISPRi results ---")
        print(hbb_all[cols].sort_values("ts_start").to_string(index=False))

    # 3. Load pair table
    print("\n=== Loading pair table ===")
    pairs = load_pair_table()
    hbb_pairs = filter_hbb_pairs(pairs)
    print(f"Pair table entries in HBB region: {len(hbb_pairs)}")

    if len(hbb_pairs) > 0:
        unique_grna = hbb_pairs[
            [
                "gRNAgroup",
                "gRNAgroup.chr",
                "gs_start",
                "gs_stop",
                "targetgene_short_name",
                "general_group",
            ]
        ].drop_duplicates()
        print(unique_grna.to_string())

    # 4. Load Q2b variants
    print("\n=== Q2b Overlap Analysis ===")
    q2b = pd.read_csv(os.path.join(ANALYSIS_DIR, "Q2b_true_blindspots.csv"))
    q2b_hbb = q2b[q2b["Locus"] == "HBB"].copy()
    print(f"HBB Q2b variants: {len(q2b_hbb)}")
    print(f"Position range: {q2b_hbb['Position'].min()} - {q2b_hbb['Position'].max()}")

    # 5. Check overlap
    if len(hbb_all) > 0:
        grna_sites = hbb_all[
            ["gRNA_group", "target_site.chr", "ts_start", "ts_stop", "site_type"]
        ].drop_duplicates()
        overlaps = check_q2b_overlap(q2b_hbb, grna_sites)
    else:
        grna_sites = pd.DataFrame()
        overlaps = []

    print(f"Q2b-CRISPRi overlaps: {len(overlaps)}")
    for o in overlaps:
        print(
            f"  {o['ClinVar_ID']} (pos={o['Position']}, {o['Category']}) "
            f"<-> {o['gRNA_group']} (dist={o['distance_bp']}bp)"
        )

    # 6. Build interpretation
    if len(hbb_all) == 0:
        interpretation = (
            "NO CRISPRi elements were tested in the HBB region in Gasperini 2019. "
            "This is consistent with the screen design: Gasperini 2019 used K562 cells "
            "and tested enhancer-gene pairs for genes expressed in K562. Adult beta-globin "
            "(HBB) is NOT expressed in K562 cells (which express embryonic/fetal globins "
            "epsilon and gamma). Since the CRISPRi readout was transcriptional change of "
            "target genes, HBB would not be detectable. This confirms that Q2b variants "
            "in the HBB regulatory region represent a genuine experimental validation gap -- "
            "no large-scale CRISPRi screen has tested these regulatory elements for HBB "
            "effects, because the appropriate cell type (adult erythroid progenitors) was "
            "not used."
        )
    elif len(overlaps) == 0:
        interpretation = (
            f"CRISPRi elements were tested near HBB ({len(hbb_all)} pairs), but none "
            f"overlap with Q2b variant positions within a {CRISPRI_WINDOW}bp window. "
            "Q2b variants remain experimentally unvalidated."
        )
    else:
        interpretation = (
            f"{len(overlaps)} Q2b variants overlap with CRISPRi-tested elements. "
            "See overlapping_variants for experimental effect sizes."
        )

    # 7. Save JSON outputs
    crispri_data = {
        "source": "Gasperini et al. 2019 (Cell)",
        "DOI": "10.1016/j.cell.2018.11.029",
        "GEO_accession": "GSE120861",
        "data_url": (
            "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE120nnn/GSE120861/suppl/"
            "GSE120861_all_deg_results.at_scale.txt.gz"
        ),
        "cell_line": "K562",
        "region_queried": f"{HBB_CHR}:{HBB_START}-{HBB_END}",
        "total_pairs_tested": int(len(deg)),
        "hbb_region_pairs": int(len(hbb_all)),
        "globin_genes_searched": GLOBIN_GENES,
        "results": hbb_all.to_dict(orient="records") if len(hbb_all) > 0 else [],
        "unique_grna_sites": (grna_sites.to_dict(orient="records") if len(grna_sites) > 0 else []),
    }

    crispri_path = os.path.join(ANALYSIS_DIR, "crispri_k562_hbb.json")
    with open(crispri_path, "w") as f:
        json.dump(crispri_data, f, indent=2, default=str)
    print(f"\nSaved: {crispri_path}")

    overlap_data = {
        "source": "Gasperini et al. 2019 CRISPRi x ARCHCODE Q2b",
        "analysis_date": "2026-03-09",
        "q2b_hbb_variants": int(len(q2b_hbb)),
        "q2b_position_range": (
            f"chr11:{int(q2b_hbb['Position'].min())}-{int(q2b_hbb['Position'].max())}"
        ),
        "crispri_sites_in_region": (int(len(grna_sites)) if len(grna_sites) > 0 else 0),
        "crispri_window_bp": CRISPRI_WINDOW,
        "overlapping_variants": overlaps,
        "interpretation": interpretation,
    }

    overlap_path = os.path.join(ANALYSIS_DIR, "crispri_q2b_overlap.json")
    with open(overlap_path, "w") as f:
        json.dump(overlap_data, f, indent=2, default=str)
    print(f"Saved: {overlap_path}")

    print(f"\n=== SUMMARY ===")
    print(f"Gasperini 2019: {len(deg):,} enhancer-gene pairs tested in K562")
    print(f"HBB region pairs: {len(hbb_all)}")
    print(f"Q2b-CRISPRi overlaps: {len(overlaps)}")
    print(f"Interpretation: {interpretation}")


if __name__ == "__main__":
    main()
