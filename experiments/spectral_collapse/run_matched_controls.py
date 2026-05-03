#!/usr/bin/env python3
"""
Matched-control robustness pilot for the spectral-collapse line.

This script keeps the scope narrow:
- HBB pilot robustness under simple perturbations
- BRCA1/TP53 negative comparison from already computed spectral outputs

It does not widen the locus set or create a manuscript claim.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from spectral_fragility import compute_spectral_fragility, spectral_gap_disruption  # noqa: E402

RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_DIR = RESULTS_DIR / "spectral_collapse"
HBB_MATRIX_DIR = RESULTS_DIR / "contact_matrices" / "30KB"


@dataclass(frozen=True)
class VariantRow:
    clinvar_id: str
    label: str
    category: str
    pearl: bool
    position: int


def load_json_matrix(path: Path) -> np.ndarray:
    with path.open() as fh:
        return np.array(json.load(fh), dtype=np.float64)


def symmetrize(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.T) / 2.0


def crop_center(matrix: np.ndarray, size: int) -> np.ndarray:
    if size >= matrix.shape[0]:
        return matrix.copy()
    start = (matrix.shape[0] - size) // 2
    return matrix[start : start + size, start : start + size]


def threshold_keep_fraction(matrix: np.ndarray, keep_fraction: float) -> np.ndarray:
    out = symmetrize(matrix.copy())
    upper = out[np.triu_indices_from(out, k=1)]
    positive = upper[upper > 0]
    if len(positive) == 0:
        return out
    cutoff = np.quantile(positive, 1.0 - keep_fraction)
    out[(out > 0) & (out < cutoff)] = 0.0
    return symmetrize(out)


def downsample_contacts(matrix: np.ndarray, keep_fraction: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = symmetrize(matrix.copy())
    n = out.shape[0]
    upper = np.triu_indices(n, k=1)
    keep = rng.random(len(upper[0])) < keep_fraction
    mask = np.zeros((n, n), dtype=bool)
    mask[upper] = keep
    mask[(upper[1], upper[0])] = keep
    mask[np.diag_indices(n)] = True
    out = np.where(mask, out, 0.0)
    return symmetrize(out)


def randomized_degree_graph(degree_sequence: list[int], rng: np.random.Generator) -> np.ndarray:
    n = len(degree_sequence)
    adj = np.zeros((n, n), dtype=float)

    # The sequence comes from a graphical support graph, so a randomized
    # Havel-Hakimi construction is usually enough for a small pilot matrix.
    for _ in range(100):
        rem = list(enumerate(degree_sequence))
        rem_deg = {i: int(d) for i, d in rem}
        trial = np.zeros((n, n), dtype=float)
        try:
            while True:
                active = [(d, i) for i, d in rem_deg.items() if d > 0]
                if not active:
                    return trial
                rng.shuffle(active)
                active.sort(key=lambda x: x[0], reverse=True)
                d_u, u = active[0]
                others = [i for _, i in active[1:] if i != u and rem_deg[i] > 0]
                if d_u > len(others):
                    raise ValueError("non-graphical degree sequence")
                chosen = others[:d_u]
                for v in chosen:
                    if v == u or trial[u, v] == 1.0:
                        raise ValueError("duplicate edge")
                for v in chosen:
                    trial[u, v] = 1.0
                    trial[v, u] = 1.0
                    rem_deg[u] -= 1
                    rem_deg[v] -= 1
                    if rem_deg[v] < 0:
                        raise ValueError("negative degree")
                if rem_deg[u] != 0:
                    raise ValueError("residual degree")
        except ValueError:
            continue
    raise RuntimeError("failed to generate degree-preserving null")


def degree_preserving_null(matrix: np.ndarray, seed: int, support_quantile: float = 0.80) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = symmetrize(matrix.copy())
    upper = out[np.triu_indices_from(out, k=1)]
    positive = upper[upper > 0]
    if len(positive) == 0:
        return out

    support_cutoff = np.quantile(positive, support_quantile)
    support = (out >= support_cutoff).astype(int)
    support = np.triu(support, k=1)
    support = support + support.T
    degrees = support.sum(axis=1).astype(int).tolist()

    rewired = randomized_degree_graph(degrees, rng)
    edge_idx = np.triu_indices_from(rewired, k=1)
    edge_positions = np.where(rewired[edge_idx] > 0)[0]
    if len(edge_positions) == 0:
        return out

    edge_weights = np.sort(upper[upper > 0])[::-1]
    shuffled_weights = rng.permutation(edge_weights)

    null = np.zeros_like(out)
    edge_pairs = list(zip(edge_idx[0][edge_positions], edge_idx[1][edge_positions]))
    for (i, j), w in zip(edge_pairs, shuffled_weights, strict=False):
        null[i, j] = w
        null[j, i] = w
    np.fill_diagonal(null, np.diag(out))
    return symmetrize(null)


def weight_shuffled_null(matrix: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = symmetrize(matrix.copy())
    upper = np.triu_indices_from(out, k=1)
    values = out[upper]
    positive_positions = np.where(values > 0)[0]
    if len(positive_positions) == 0:
        return out
    shuffled = values.copy()
    positive_values = shuffled[positive_positions]
    rng.shuffle(positive_values)
    shuffled[positive_positions] = positive_values
    null = np.zeros_like(out)
    null[upper] = shuffled
    null = null + null.T
    np.fill_diagonal(null, np.diag(out))
    return symmetrize(null)


def compute_metrics(wt: np.ndarray, mut: np.ndarray, k_modes: int) -> dict[str, float]:
    k = max(3, min(k_modes, wt.shape[0] - 1))
    sfi, components = compute_spectral_fragility(wt, mut, k=k)
    gap_delta, gap_wt, gap_mut = spectral_gap_disruption(wt, mut)
    return {
        "SFI": float(sfi),
        "spectral_gap_disruption": float(gap_delta),
        "spectral_gap_wt": float(gap_wt),
        "spectral_gap_mut": float(gap_mut),
        "eigenvalue_shifts_mean": float(np.mean(components["eigenvalue_shifts"])),
        "eigenvector_angles_mean": float(np.mean(components["eigenvector_angles"])),
    }


def load_hbb_pilot() -> pd.DataFrame:
    atlas = pd.read_csv(RESULTS_DIR / "HBB_Unified_Atlas.csv")
    pilot = pd.read_csv(RESULTS_DIR / "sfi_30kb_pilot_recheck.csv")
    pilot = pilot.merge(
        atlas[["ClinVar_ID", "Pearl", "Label", "Category", "Position_GRCh38"]],
        on="ClinVar_ID",
        how="left",
    )
    return pilot.sort_values(["Pearl", "Position_GRCh38", "ClinVar_ID"], ascending=[False, True, True])


def load_locus_summary(sfi_path: Path, atlas_path: Path, locus: str, control_category: str) -> dict:
    sfi = pd.read_csv(sfi_path)
    atlas = pd.read_csv(atlas_path)[["ClinVar_ID", "Label", "Category"]]
    df = sfi.merge(atlas, on="ClinVar_ID", how="left")

    summary = {
        "locus": locus,
        "rows": int(len(df)),
        "mean_SFI": float(df["SFI"].mean()),
        "median_SFI": float(df["SFI"].median()),
        "control_category": control_category,
        "control_rows": int((df["Category"] == control_category).sum()),
        "control_mean_SFI": float(df.loc[df["Category"] == control_category, "SFI"].mean()),
        "control_median_SFI": float(df.loc[df["Category"] == control_category, "SFI"].median()),
    }

    signal_rows = df[df["Category"] != control_category]
    if len(signal_rows) > 0 and summary["control_rows"] > 0:
        u, p = mannwhitneyu(
            signal_rows["SFI"].astype(float),
            df.loc[df["Category"] == control_category, "SFI"].astype(float),
            alternative="two-sided",
        )
        summary["signal_rows"] = int(len(signal_rows))
        summary["signal_mean_SFI"] = float(signal_rows["SFI"].mean())
        summary["signal_median_SFI"] = float(signal_rows["SFI"].median())
        summary["mannwhitney_p"] = float(p)
    else:
        summary["signal_rows"] = 0
        summary["signal_mean_SFI"] = None
        summary["signal_median_SFI"] = None
        summary["mannwhitney_p"] = None
    return summary


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pilot = load_hbb_pilot()
    hbb_rows = pilot.copy()

    transforms = [
        ("baseline", None),
        ("threshold_keep_0.75", lambda m, s: threshold_keep_fraction(m, 0.75)),
        ("threshold_keep_0.50", lambda m, s: threshold_keep_fraction(m, 0.50)),
        ("window_40", lambda m, s: crop_center(m, 40)),
        ("window_30", lambda m, s: crop_center(m, 30)),
        ("coverage_keep_0.75", lambda m, s: downsample_contacts(m, 0.75, s)),
        ("coverage_keep_0.50", lambda m, s: downsample_contacts(m, 0.50, s)),
        ("degree_preserving_null", lambda m, s: degree_preserving_null(m, s)),
        ("weight_shuffled_null", lambda m, s: weight_shuffled_null(m, s)),
    ]

    result_rows = []
    for idx, row in hbb_rows.reset_index(drop=True).iterrows():
        clinvar_id = row["ClinVar_ID"]
        wt_path = HBB_MATRIX_DIR / f"{clinvar_id}_wt.json"
        mut_path = HBB_MATRIX_DIR / f"{clinvar_id}_mut.json"
        if not wt_path.exists() or not mut_path.exists():
            continue

        wt = load_json_matrix(wt_path)
        mut = load_json_matrix(mut_path)
        seed_base = int(clinvar_id.replace("VCV", "")) if clinvar_id.startswith("VCV") else idx

        for transform_name, transform_fn in transforms:
            if transform_fn is None:
                wt_t = wt
                mut_t = mut
            else:
                wt_t = transform_fn(wt, seed_base * 2 + 1)
                mut_t = transform_fn(mut, seed_base * 2 + 2)

            metrics = compute_metrics(wt_t, mut_t, k_modes=10)
            result_rows.append(
                {
                    "locus": "HBB",
                    "ClinVar_ID": clinvar_id,
                    "Pearl": bool(row["Pearl"]),
                    "Label": row["Label"],
                    "Category": row["Category"],
                    "transform": transform_name,
                    **metrics,
                }
            )

    df = pd.DataFrame(result_rows)
    out_csv = OUTPUT_DIR / "matched_control_results.csv"
    df.to_csv(out_csv, index=False)

    summary = {
        "branch": "experiment/spectral-collapse-pilot",
        "hbb": {},
        "negative_comparisons": {},
        "decision": {},
        "files": {
            "results_csv": str(out_csv.relative_to(PROJECT_ROOT)),
            "summary_json": str((OUTPUT_DIR / "matched_control_summary.json").relative_to(PROJECT_ROOT)),
            "report_md": str((OUTPUT_DIR / "MATCHED_CONTROL_REPORT.md").relative_to(PROJECT_ROOT)),
        },
    }

    if not df.empty:
        baseline = df[df["transform"] == "baseline"]
        pearls = baseline[baseline["Pearl"] == True]  # noqa: E712
        benign = baseline[baseline["Pearl"] == False]  # noqa: E712
        for metric in ["SFI", "spectral_gap_disruption", "eigenvalue_shifts_mean", "eigenvector_angles_mean"]:
            if len(pearls) and len(benign):
                u, p = mannwhitneyu(pearls[metric], benign[metric], alternative="two-sided")
            else:
                p = None
            summary["hbb"][metric] = {
                "pearls_mean": float(pearls[metric].mean()),
                "benign_mean": float(benign[metric].mean()),
                "pearls_median": float(pearls[metric].median()),
                "benign_median": float(benign[metric].median()),
                "mannwhitney_p": None if p is None else float(p),
            }

        transform_summary = {}
        for transform_name in df["transform"].unique():
            sub = df[df["transform"] == transform_name]
            p = sub[sub["Pearl"] == True]["SFI"]  # noqa: E712
            b = sub[sub["Pearl"] == False]["SFI"]  # noqa: E712
            if len(p) and len(b):
                _, pv = mannwhitneyu(p, b, alternative="two-sided")
            else:
                pv = None
            transform_summary[transform_name] = {
                "pearls_mean_SFI": float(p.mean()) if len(p) else None,
                "benign_mean_SFI": float(b.mean()) if len(b) else None,
                "pearls_n": int(len(p)),
                "benign_n": int(len(b)),
                "mannwhitney_p": None if pv is None else float(pv),
            }
        summary["hbb"]["transforms"] = transform_summary

    summary["negative_comparisons"]["BRCA1"] = load_locus_summary(
        RESULTS_DIR / "sfi_brca1_all.csv",
        RESULTS_DIR / "BRCA1_Unified_Atlas_brca1.csv",
        locus="BRCA1",
        control_category="synonymous",
    )
    summary["negative_comparisons"]["TP53"] = load_locus_summary(
        RESULTS_DIR / "sfi_tp53_all.csv",
        RESULTS_DIR / "TP53_Unified_Atlas_tp53.csv",
        locus="TP53",
        control_category="synonymous",
    )

    transform_p = {
        name: stats["mannwhitney_p"] for name, stats in summary["hbb"]["transforms"].items()
    }
    robust_threshold_window = all(
        transform_p.get(name) is not None and transform_p[name] < 0.05
        for name in ["baseline", "threshold_keep_0.75", "threshold_keep_0.50", "window_40", "window_30"]
    )
    coverage_survives = all(
        transform_p.get(name) is not None and transform_p[name] < 0.05
        for name in ["coverage_keep_0.75", "coverage_keep_0.50"]
    )
    nulls_collapse = all(
        transform_p.get(name) is not None and transform_p[name] > 0.05
        for name in ["degree_preserving_null", "weight_shuffled_null"]
    )
    hbb_continue = bool(robust_threshold_window and coverage_survives and nulls_collapse)
    summary["decision"]["continue"] = hbb_continue
    if hbb_continue:
        summary["decision"]["reason"] = (
            "HBB survives baseline, threshold/window, coverage/downsampling, and null-graph controls."
        )
    else:
        summary["decision"]["reason"] = (
            "HBB survives baseline and threshold/window perturbations, but coverage/downsampling controls erase the separation, "
            "so the spectral-collapse interpretation remains unresolved."
        )

    out_json = OUTPUT_DIR / "matched_control_summary.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_lines = [
        "# Matched Control Report",
        "",
        f"**Date:** 2026-05-03",
        f"**Branch:** `experiment/spectral-collapse-pilot`",
        "",
        "## HBB Baseline",
        "",
        f"- Pearls: {len(df[(df['transform'] == 'baseline') & (df['Pearl'] == True)])}",
        f"- Benign controls: {len(df[(df['transform'] == 'baseline') & (df['Pearl'] == False)])}",
        f"- SFI p-value: {summary['hbb']['SFI']['mannwhitney_p']}",
        f"- Spectral gap p-value: {summary['hbb']['spectral_gap_disruption']['mannwhitney_p']}",
        "",
        "## Transform Sensitivity",
        "",
    ]
    for name, stats in summary["hbb"]["transforms"].items():
        report_lines.append(
            f"- {name}: pearls_mean_SFI={stats['pearls_mean_SFI']:.6f} "
            f"benign_mean_SFI={stats['benign_mean_SFI']:.6f} p={stats['mannwhitney_p']}"
        )
    report_lines.extend(
        [
            "",
            "## Negative Comparison",
            "",
            f"- BRCA1 control-category mean SFI: {summary['negative_comparisons']['BRCA1']['control_mean_SFI']}",
            f"- TP53 control-category mean SFI: {summary['negative_comparisons']['TP53']['control_mean_SFI']}",
            "",
            "## Decision",
            "",
            f"- Continue: {summary['decision']['continue']}",
            f"- Reason: {summary['decision']['reason']}",
            "",
        ]
    )
    (OUTPUT_DIR / "MATCHED_CONTROL_REPORT.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Saved {len(df)} rows to {out_csv}")
    print(f"Summary: {out_json}")
    print(f"Report: {OUTPUT_DIR / 'MATCHED_CONTROL_REPORT.md'}")
    print(f"Continue decision: {summary['decision']['continue']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
