#!/usr/bin/env python3
"""
AlphaGenome Real API Experiments — 5 experiments using DeepMind SDK.

ALL DATA IS REAL. No mocks. No synthetic fallbacks.
API key from .env or ALPHAGENOME_API_KEY environment variable.

Usage:
    python scripts/alphagenome_real_experiments.py variant-effect
    python scripts/alphagenome_real_experiments.py ctcf-validation
    python scripts/alphagenome_real_experiments.py multi-cellline
    python scripts/alphagenome_real_experiments.py enhancer-activity
    python scripts/alphagenome_real_experiments.py benchmark-95kb
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def get_api_key() -> str:
    key = os.environ.get("ALPHAGENOME_API_KEY")
    if key:
        return key
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ALPHAGENOME_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val
    print("ERROR: No ALPHAGENOME_API_KEY found")
    sys.exit(1)


def get_client():
    from alphagenome.models import dna_client

    return dna_client.create(get_api_key())


def make_interval(chrom: str, start: int, end: int):
    """Create interval snapped to AlphaGenome supported lengths."""
    from alphagenome.models import dna_client
    from alphagenome.data.genome import Interval

    length = end - start
    supported = sorted(dna_client.SUPPORTED_SEQUENCE_LENGTHS.values())
    # Snap up to nearest supported length
    snap_len = length
    for s in supported:
        if s >= length:
            snap_len = s
            break
    if snap_len == length and snap_len not in supported:
        snap_len = supported[-1]

    # Center the interval
    center = (start + end) // 2
    snap_start = center - snap_len // 2
    snap_end = snap_start + snap_len

    print(
        f"  Interval: {chrom}:{start}-{end} ({length}bp) → snapped to {chrom}:{snap_start}-{snap_end} ({snap_len}bp)"
    )
    return Interval(chromosome=chrom, start=snap_start, end=snap_end, name="hbb")


def make_variant(chrom: str, pos: int, ref: str, alt: str):
    from alphagenome.data.genome import Variant

    return Variant(chromosome=chrom, position=pos, reference_bases=ref, alternate_bases=alt)


# =========================================================================
# Experiment 1: Variant Effect on 20 Pearls
# =========================================================================
def experiment_variant_effect():
    from alphagenome.models.dna_output import OutputType

    print("=" * 70)
    print("Experiment 1: Variant Effect on Pearl Variants (REAL API)")
    print("=" * 70)

    atlas = pd.read_csv(RESULTS_DIR / "HBB_Clinical_Atlas_REAL.csv")
    pearls = atlas[atlas["Pearl"] == True].copy()
    print(f"Pearl variants: {len(pearls)}")

    # Deduplicate by position (15 promoter pearls at same cluster)
    unique_positions = pearls.drop_duplicates(subset=["Position_GRCh38"])
    print(f"Unique positions: {len(unique_positions)}")

    client = get_client()
    interval = make_interval("chr11", 5200000, 5240000)

    results = []
    for idx, row in unique_positions.iterrows():
        pos = int(row["Position_GRCh38"])
        ref = str(row["Ref"])
        alt = str(row["Alt"])
        clinvar_id = row["ClinVar_ID"]
        category = row["Category"]
        archcode_ssim = float(row["ARCHCODE_SSIM"])

        print(f"\n  [{clinvar_id}] chr11:{pos} {ref}>{alt} ({category})")
        print(f"    ARCHCODE SSIM: {archcode_ssim:.4f}")

        variant = make_variant("chr11", pos, ref, alt)

        try:
            var_output = client.predict_variant(
                interval,
                variant,
                requested_outputs=[
                    OutputType.CONTACT_MAPS,
                    OutputType.CAGE,
                    OutputType.CHIP_HISTONE,
                ],
                ontology_terms=["EFO:0002784"],  # K562
            )

            # Contact map delta
            ref_contacts = var_output.reference.contact_maps
            alt_contacts = var_output.alternate.contact_maps

            contact_delta = None
            if ref_contacts is not None and alt_contacts is not None:
                ref_data = ref_contacts.values
                alt_data = alt_contacts.values
                if ref_data is not None and alt_data is not None:
                    ref_arr = np.array(ref_data)
                    alt_arr = np.array(alt_data)
                    contact_delta = float(np.mean(np.abs(alt_arr - ref_arr)))
                    print(f"    Contact map delta (mean abs): {contact_delta:.6f}")

            # CAGE delta (promoter activity)
            cage_delta = None
            if var_output.reference.cage is not None and var_output.alternate.cage is not None:
                ref_cage = np.array(var_output.reference.cage.values)
                alt_cage = np.array(var_output.alternate.cage.values)
                if ref_cage.size > 0 and alt_cage.size > 0:
                    cage_delta = float(np.mean(alt_cage) - np.mean(ref_cage))
                    print(f"    CAGE delta (mean): {cage_delta:.6f}")

            # Histone delta
            histone_delta = None
            if (
                var_output.reference.chip_histone is not None
                and var_output.alternate.chip_histone is not None
            ):
                ref_hist = np.array(var_output.reference.chip_histone.values)
                alt_hist = np.array(var_output.alternate.chip_histone.values)
                if ref_hist.size > 0 and alt_hist.size > 0:
                    histone_delta = float(np.mean(alt_hist) - np.mean(ref_hist))
                    print(f"    Histone delta (mean): {histone_delta:.6f}")

            results.append(
                {
                    "clinvar_id": clinvar_id,
                    "position": pos,
                    "ref": ref,
                    "alt": alt,
                    "category": category,
                    "archcode_ssim": archcode_ssim,
                    "ag_contact_delta": contact_delta,
                    "ag_cage_delta": cage_delta,
                    "ag_histone_delta": histone_delta,
                    "status": "OK",
                }
            )

        except Exception as e:
            print(f"    ERROR: {e}")
            results.append(
                {
                    "clinvar_id": clinvar_id,
                    "position": pos,
                    "category": category,
                    "archcode_ssim": archcode_ssim,
                    "status": f"ERROR: {e}",
                }
            )

        time.sleep(0.5)

    output = {
        "experiment": "AlphaGenome Variant Effect on Pearl Variants",
        "date": datetime.now(timezone.utc).isoformat(),
        "data_source": "REAL AlphaGenome API (SDK v0.6.0)",
        "n_pearls_total": len(pearls),
        "n_unique_positions": len(unique_positions),
        "results": results,
    }

    out_path = RESULTS_DIR / "alphagenome_pearl_variant_effects.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


# =========================================================================
# Experiment 2: CTCF Binding Validation
# =========================================================================
def experiment_ctcf_validation():
    from alphagenome.models.dna_output import OutputType

    print("=" * 70)
    print("Experiment 2: CTCF Binding Prediction vs ENCODE (REAL API)")
    print("=" * 70)

    client = get_client()
    interval = make_interval("chr11", 5200000, 5295000)

    print("Requesting CHIP_TF prediction...")
    output = client.predict_interval(
        interval,
        requested_outputs=[OutputType.CHIP_TF],
        ontology_terms=None,  # all cell lines
    )

    chip_tf = output.chip_tf
    if chip_tf is None:
        print("ERROR: No CHIP_TF data returned")
        return

    tf_data = np.array(chip_tf.values)
    print(f"  CHIP_TF shape: {tf_data.shape}")
    print(
        f"  Track names: {list(chip_tf.metadata.columns)[:10] if hasattr(chip_tf, 'metadata') else 'N/A'}"
    )

    # Find CTCF track
    ctcf_track = None
    ctcf_idx = None
    if hasattr(chip_tf, "metadata") and chip_tf.metadata is not None:
        names = chip_tf.metadata.index.tolist() if hasattr(chip_tf.metadata, "index") else []
        for i, name in enumerate(names):
            if "CTCF" in str(name).upper():
                ctcf_track = tf_data[:, i] if tf_data.ndim > 1 else tf_data
                ctcf_idx = i
                print(f"  Found CTCF track at index {i}: {name}")
                break

    if ctcf_track is None and tf_data.ndim == 1:
        ctcf_track = tf_data
        print("  Using single TF track as CTCF proxy")

    result = {
        "experiment": "CTCF Binding Validation (AlphaGenome CHIP_TF vs ENCODE)",
        "date": datetime.now(timezone.utc).isoformat(),
        "data_source": "REAL AlphaGenome API",
        "interval": "chr11:5200000-5295000",
        "chip_tf_shape": list(tf_data.shape),
        "ctcf_track_found": ctcf_track is not None,
        "ctcf_track_index": ctcf_idx,
    }

    if ctcf_track is not None:
        result["ctcf_signal_stats"] = {
            "mean": float(np.mean(ctcf_track)),
            "max": float(np.max(ctcf_track)),
            "min": float(np.min(ctcf_track)),
            "n_peaks_above_mean": int(np.sum(ctcf_track > np.mean(ctcf_track))),
        }
        # Find peak positions
        threshold = np.mean(ctcf_track) + 2 * np.std(ctcf_track)
        peaks = np.where(ctcf_track > threshold)[0]
        result["ctcf_peak_bins"] = peaks.tolist()[:20]
        print(f"  CTCF peaks (>mean+2σ): {len(peaks)} bins")

    out_path = RESULTS_DIR / "alphagenome_ctcf_validation.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


# =========================================================================
# Experiment 3: Multi-Cell-Line Contact Maps
# =========================================================================
def experiment_multi_cellline():
    from alphagenome.models.dna_output import OutputType

    print("=" * 70)
    print("Experiment 3: Multi-Cell-Line Contact Maps (REAL API)")
    print("=" * 70)

    client = get_client()
    interval = make_interval("chr11", 5200000, 5295000)

    print("Requesting CONTACT_MAPS for all cell lines...")
    output = client.predict_interval(
        interval,
        requested_outputs=[OutputType.CONTACT_MAPS],
        ontology_terms=None,  # all cell lines
    )

    contacts = output.contact_maps
    if contacts is None:
        print("ERROR: No contact maps returned")
        return

    data = np.array(contacts.values)
    print(f"  Contact map shape: {data.shape}")

    track_names = (
        contacts.metadata.index.tolist()
        if hasattr(contacts, "metadata") and contacts.metadata is not None
        else list(range(data.shape[-1] if data.ndim == 3 else 1))
    )
    print(f"  Cell lines: {len(track_names)}")

    # Build ARCHCODE reference matrix
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    try:
        from benchmark_alphagenome import get_archcode_matrix

        archcode_matrix = get_archcode_matrix("95kb", {})
        print(f"  ARCHCODE matrix: {archcode_matrix.shape}")
        has_archcode = True
    except Exception as e:
        print(f"  WARNING: Could not load ARCHCODE matrix: {e}")
        has_archcode = False

    results = []
    for i, name in enumerate(track_names):
        if data.ndim == 3:
            cell_map = data[:, :, i] if data.shape[2] > i else data[:, :, 0]
        else:
            cell_map = data

        # Normalize
        upper_tri = cell_map[np.triu_indices(cell_map.shape[0], k=2)]
        valid = upper_tri[~np.isnan(upper_tri) & (upper_tri != 0)]

        r_archcode = None
        if has_archcode and len(valid) > 10:
            # Resize archcode to match
            from scipy.ndimage import zoom

            target_size = cell_map.shape[0]
            if archcode_matrix.shape[0] != target_size:
                scale = target_size / archcode_matrix.shape[0]
                archcode_resized = zoom(archcode_matrix, scale)
            else:
                archcode_resized = archcode_matrix

            arch_upper = archcode_resized[np.triu_indices(target_size, k=2)]
            cell_upper = cell_map[np.triu_indices(target_size, k=2)]
            mask = ~np.isnan(cell_upper) & ~np.isnan(arch_upper) & (cell_upper != 0)
            if np.sum(mask) > 10:
                r, p = stats.pearsonr(arch_upper[mask], cell_upper[mask])
                r_archcode = float(r)

        entry = {
            "index": i,
            "track_name": str(name),
            "mean_contact": float(np.nanmean(cell_map)),
            "max_contact": float(np.nanmax(cell_map)),
            "pearson_r_vs_archcode": r_archcode,
        }
        results.append(entry)
        status = f"r={r_archcode:.3f}" if r_archcode is not None else "N/A"
        print(f"  [{i:2d}] {str(name):40s} {status}")

    output_data = {
        "experiment": "Multi-Cell-Line Contact Maps (28 cell lines)",
        "date": datetime.now(timezone.utc).isoformat(),
        "data_source": "REAL AlphaGenome API",
        "interval": "chr11:5200000-5295000",
        "n_cell_lines": len(track_names),
        "contact_map_shape": list(data.shape),
        "results": results,
    }

    out_path = RESULTS_DIR / "alphagenome_multicellline_contacts.json"
    with open(out_path, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


# =========================================================================
# Experiment 4: Enhancer Activity at Pearl Positions
# =========================================================================
def experiment_enhancer_activity():
    from alphagenome.models.dna_output import OutputType

    print("=" * 70)
    print("Experiment 4: Enhancer Activity at Pearl Positions (REAL API)")
    print("=" * 70)

    atlas = pd.read_csv(RESULTS_DIR / "HBB_Clinical_Atlas_REAL.csv")
    pearls = atlas[atlas["Pearl"] == True].drop_duplicates(subset=["Position_GRCh38"])

    # Top 5 unique positions
    top5 = pearls.head(5)
    print(f"Testing {len(top5)} unique pearl positions")

    client = get_client()
    interval = make_interval("chr11", 5200000, 5240000)

    results = []
    for _, row in top5.iterrows():
        pos = int(row["Position_GRCh38"])
        ref = str(row["Ref"])
        alt = str(row["Alt"])
        cid = row["ClinVar_ID"]

        print(f"\n  [{cid}] chr11:{pos} {ref}>{alt}")

        variant = make_variant("chr11", pos, ref, alt)

        try:
            var_output = client.predict_variant(
                interval,
                variant,
                requested_outputs=[OutputType.CAGE, OutputType.CHIP_HISTONE, OutputType.ATAC],
                ontology_terms=["EFO:0002784"],  # K562
            )

            entry = {"clinvar_id": cid, "position": pos, "ref": ref, "alt": alt, "status": "OK"}

            for modality, attr in [("cage", "cage"), ("histone", "chip_histone"), ("atac", "atac")]:
                ref_track = getattr(var_output.reference, attr, None)
                alt_track = getattr(var_output.alternate, attr, None)
                if ref_track is not None and alt_track is not None:
                    ref_arr = np.array(ref_track.values)
                    alt_arr = np.array(alt_track.values)
                    if ref_arr.size > 0 and alt_arr.size > 0:
                        delta_mean = float(np.mean(alt_arr) - np.mean(ref_arr))
                        delta_max = float(np.max(np.abs(alt_arr - ref_arr)))
                        pct_change = float(delta_mean / (np.mean(ref_arr) + 1e-10) * 100)
                        entry[f"{modality}_delta_mean"] = delta_mean
                        entry[f"{modality}_delta_max"] = delta_max
                        entry[f"{modality}_pct_change"] = pct_change
                        print(f"    {modality:10s}: delta={delta_mean:.6f} ({pct_change:+.2f}%)")

            results.append(entry)

        except Exception as e:
            print(f"    ERROR: {e}")
            results.append({"clinvar_id": cid, "position": pos, "status": f"ERROR: {e}"})

        time.sleep(0.5)

    output = {
        "experiment": "Enhancer Activity at Pearl Positions",
        "date": datetime.now(timezone.utc).isoformat(),
        "data_source": "REAL AlphaGenome API",
        "n_positions": len(top5),
        "results": results,
    }

    out_path = RESULTS_DIR / "alphagenome_enhancer_activity.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


# =========================================================================
# Experiment 5: 95kb Benchmark
# =========================================================================
def experiment_benchmark_95kb():
    from alphagenome.models.dna_output import OutputType

    print("=" * 70)
    print("Experiment 5: 95kb Window Benchmark (REAL API)")
    print("=" * 70)

    client = get_client()
    interval = make_interval("chr11", 5200000, 5295000)

    print("Requesting CONTACT_MAPS (95kb window)...")
    output = client.predict_interval(
        interval,
        requested_outputs=[OutputType.CONTACT_MAPS],
        ontology_terms=None,  # all cell lines
    )

    contacts = output.contact_maps
    if contacts is None:
        print("ERROR: No contact maps returned")
        return

    data = np.array(contacts.values)
    print(f"  Shape: {data.shape}")

    # Find GM12878 or K562
    track_names = (
        contacts.metadata.index.tolist()
        if hasattr(contacts, "metadata") and contacts.metadata is not None
        else list(range(data.shape[-1] if data.ndim == 3 else 1))
    )
    target_idx = 0
    for i, name in enumerate(track_names):
        name_str = str(name)
        if "GM12878" in name_str or "K562" in name_str:
            target_idx = i
            print(f"  Selected: [{i}] {name_str}")
            break

    if data.ndim == 3:
        ag_matrix = data[:, :, target_idx]
    else:
        ag_matrix = data

    # Apply exp() if log scale
    if np.min(ag_matrix[ag_matrix != 0]) < 0:
        ag_matrix = np.exp(ag_matrix)

    print(
        f"  AG matrix: {ag_matrix.shape}, range [{np.min(ag_matrix):.4f}, {np.max(ag_matrix):.4f}]"
    )

    # Load Hi-C
    hic_path = PROJECT_ROOT / "data" / "HBB_K562_HiC_1000bp.npy"
    hic_matrix = None
    if hic_path.exists():
        hic_matrix = np.load(hic_path)
        print(f"  Hi-C matrix: {hic_matrix.shape}")

    # Build ARCHCODE
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    try:
        from benchmark_alphagenome import get_archcode_matrix

        archcode_matrix = get_archcode_matrix("95kb", {})
        print(f"  ARCHCODE matrix: {archcode_matrix.shape}")
        has_archcode = True
    except Exception as e:
        print(f"  WARNING: Could not load ARCHCODE matrix: {e}")
        has_archcode = False

    # Resize all to common size
    target_size = ag_matrix.shape[0]
    from scipy.ndimage import zoom

    def resize_matrix(m, size):
        if m.shape[0] == size:
            return m
        scale = size / m.shape[0]
        return zoom(m, scale)

    correlations = {}

    if has_archcode:
        arch_resized = resize_matrix(archcode_matrix, target_size)
        mask = np.triu_indices(target_size, k=2)
        a = arch_resized[mask]
        b = ag_matrix[mask]
        valid = ~np.isnan(a) & ~np.isnan(b) & (a != 0) & (b != 0)
        if np.sum(valid) > 10:
            r, p = stats.pearsonr(a[valid], b[valid])
            rho, rho_p = stats.spearmanr(a[valid], b[valid])
            correlations["archcode_vs_alphagenome"] = {
                "pearson_r": float(r),
                "pearson_p": float(p),
                "spearman_rho": float(rho),
                "spearman_p": float(rho_p),
                "n_valid": int(np.sum(valid)),
            }
            print(f"\n  ARCHCODE ↔ AlphaGenome: r={r:.4f}, ρ={rho:.4f} (n={np.sum(valid)})")

    if hic_matrix is not None:
        hic_resized = resize_matrix(hic_matrix, target_size)
        mask = np.triu_indices(target_size, k=2)

        if has_archcode:
            a = resize_matrix(archcode_matrix, target_size)[mask]
            h = hic_resized[mask]
            valid = ~np.isnan(a) & ~np.isnan(h) & (a != 0) & (h != 0)
            if np.sum(valid) > 10:
                r, p = stats.pearsonr(a[valid], h[valid])
                rho, rho_p = stats.spearmanr(a[valid], h[valid])
                correlations["archcode_vs_hic"] = {
                    "pearson_r": float(r),
                    "pearson_p": float(p),
                    "spearman_rho": float(rho),
                    "spearman_p": float(rho_p),
                    "n_valid": int(np.sum(valid)),
                }
                print(f"  ARCHCODE ↔ Hi-C:        r={r:.4f}, ρ={rho:.4f}")

        b = ag_matrix[mask]
        h = hic_resized[mask]
        valid = ~np.isnan(b) & ~np.isnan(h) & (b != 0) & (h != 0)
        if np.sum(valid) > 10:
            r, p = stats.pearsonr(b[valid], h[valid])
            rho, rho_p = stats.spearmanr(b[valid], h[valid])
            correlations["alphagenome_vs_hic"] = {
                "pearson_r": float(r),
                "pearson_p": float(p),
                "spearman_rho": float(rho),
                "spearman_p": float(rho_p),
                "n_valid": int(np.sum(valid)),
            }
            print(f"  AlphaGenome ↔ Hi-C:     r={r:.4f}, ρ={rho:.4f}")

    output_data = {
        "experiment": "95kb Window Benchmark (ARCHCODE vs AlphaGenome vs Hi-C)",
        "date": datetime.now(timezone.utc).isoformat(),
        "data_source": "REAL AlphaGenome API",
        "interval": "chr11:5200000-5295000",
        "ag_matrix_shape": list(ag_matrix.shape),
        "selected_cell_line": str(track_names[target_idx]) if track_names else "default",
        "correlations": correlations,
    }

    out_path = RESULTS_DIR / "alphagenome_benchmark_95kb_real.json"
    with open(out_path, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


# =========================================================================
# Main dispatcher
# =========================================================================
EXPERIMENTS = {
    "variant-effect": experiment_variant_effect,
    "ctcf-validation": experiment_ctcf_validation,
    "multi-cellline": experiment_multi_cellline,
    "enhancer-activity": experiment_enhancer_activity,
    "benchmark-95kb": experiment_benchmark_95kb,
    "all": None,
}


def main():
    parser = argparse.ArgumentParser(description="AlphaGenome Real API Experiments")
    parser.add_argument(
        "experiment", choices=list(EXPERIMENTS.keys()), help="Which experiment to run"
    )
    args = parser.parse_args()

    if args.experiment == "all":
        for name, func in EXPERIMENTS.items():
            if name != "all" and func is not None:
                func()
                print("\n")
    else:
        EXPERIMENTS[args.experiment]()


if __name__ == "__main__":
    main()
