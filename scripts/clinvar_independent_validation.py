#!/usr/bin/env python3
"""
Independent external validation of ARCHCODE-SV Step +2.

Uses ClinVar SVs on chromosomes NEVER seen during parameter calibration:
  Calibration set: chr2, chr7, chr17
  Validation set:  chr1, chr3-6, chr8-16, chr18-22, chrX

Parameters are FROZEN (not tuned on this data):
  LOEUF_BODY=0.80, WINDOW_STEP2=200kb, CTCF_BARRIER_SCORE=50

If FPR remains <=20% on unseen chromosomes -> genuine external validation.
"""

import gzip
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)

from archcode_sv import (
    CTCF_BED,
    StructuralVariant,
    find_hi_genes_step2,
    load_ctcf_strong,
    load_gene_constraint,
    score_sv,
)

# ── Config ──────────────────────────────────────────────────────────────────
CALIBRATION_CHROMS = {"chr2", "chr7", "chr17"}
VALID_CHROMS = {f"chr{i}" for i in list(range(1, 23)) + ["X"]} - CALIBRATION_CHROMS
SV_MIN_KB, SV_MAX_KB = 50_000, 400_000
GENCODE_ALL_JSON = ROOT / "data/input/gencode_genes_all_chroms.json"
CLINVAR_JSON = ROOT / "experiments/exp_archcode_sv/clinvar_valid_chroms.json"
RESULTS_JSON = ROOT / "experiments/exp_archcode_sv/clinvar_independent_results.json"

CLINVAR_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
GENCODE_URL = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_47/gencode.v47.basic.annotation.gtf.gz"


# ── Data download helpers ────────────────────────────────────────────────────


def download_gencode_all(out_path: Path) -> list[dict]:
    """Download GENCODE v47 and extract protein-coding genes for validation chroms."""
    if out_path.exists():
        print(f"GENCODE already cached: {out_path}")
        with open(out_path) as f:
            return json.load(f)

    print(f"Downloading GENCODE v47 from EBI FTP (~500MB)...")
    genes = []
    with urllib.request.urlopen(GENCODE_URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  Downloaded {len(raw) // 1_000_000}MB, parsing...")

    with gzip.open(io.BytesIO(raw)) as gz:
        for line in gz:
            line = line.decode("utf-8", errors="ignore")
            if line.startswith("#"):
                continue
            cols = line.strip().split("\t")
            if len(cols) < 9:
                continue
            chrom, ftype = cols[0], cols[2]
            if ftype != "gene":
                continue
            attrs = cols[8]
            if 'gene_type "protein_coding"' not in attrs:
                continue
            # Extract gene name
            gene_name = None
            for part in attrs.split(";"):
                part = part.strip()
                if part.startswith("gene_name"):
                    gene_name = part.split('"')[1]
                    break
            if not gene_name:
                continue
            genes.append(
                {
                    "chrom": chrom,
                    "start": int(cols[3]),
                    "end": int(cols[4]),
                    "gene": gene_name,
                }
            )

    print(f"  Total protein-coding genes: {len(genes)}")
    with open(out_path, "w") as f:
        json.dump(genes, f)
    print(f"  Saved: {out_path}")
    return genes


def download_clinvar_svs(out_path: Path) -> dict:
    """Download ClinVar variant_summary.txt.gz and extract SVs for validation chroms."""
    if out_path.exists():
        print(f"ClinVar SVs already cached: {out_path}")
        with open(out_path) as f:
            return json.load(f)

    print("Downloading ClinVar variant_summary.txt.gz (~80MB)...")
    with urllib.request.urlopen(CLINVAR_URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  Downloaded {len(raw) // 1_000_000}MB, parsing...")

    pathogenic_svs, benign_svs = [], []
    seen = set()
    target_types = {"deletion", "inversion"}
    path_sigs = {"Pathogenic", "Likely pathogenic"}
    benign_sigs = {"Benign", "Likely benign"}

    with gzip.open(io.BytesIO(raw)) as gz:
        header = gz.readline().decode().strip().split("\t")
        col = {h: i for i, h in enumerate(header)}
        for line in gz:
            row = line.decode("utf-8", errors="ignore").strip().split("\t")
            if len(row) <= max(col.values()):
                continue
            assembly = row[col.get("Assembly", 16)] if "Assembly" in col else ""
            if assembly != "GRCh38":
                continue
            chrom = (
                "chr" + row[col["Chromosome"]]
                if not row[col["Chromosome"]].startswith("chr")
                else row[col["Chromosome"]]
            )
            if chrom not in VALID_CHROMS:
                continue
            vtype = row[col.get("Type", 1)].lower() if "Type" in col else ""
            if not any(t in vtype for t in target_types):
                continue
            try:
                start = int(row[col["Start"]])
                end = int(row[col["Stop"]])
            except (ValueError, KeyError):
                continue
            size = end - start
            if not (SV_MIN_KB <= size <= SV_MAX_KB):
                continue
            sig = row[col.get("ClinicalSignificance", 6)] if "ClinicalSignificance" in col else ""
            # Strict: must be ONLY P/LP or ONLY B/LB (no conflicting)
            words = {w.strip() for w in sig.split("/")}
            is_path = bool(words & path_sigs) and not (words & benign_sigs)
            is_benign = bool(words & benign_sigs) and not (words & path_sigs)
            if not (is_path or is_benign):
                continue
            key = (chrom, start, end)
            if key in seen:
                continue
            seen.add(key)
            sv = {
                "type": "deletion" if "deletion" in vtype else "inversion",
                "chrom": chrom,
                "start": start,
                "end": end,
                "size": size,
                "sig": sig,
                "pathogenic": is_path,
                "name": row[col.get("Name", 2)] if "Name" in col else f"{chrom}:{start}-{end}",
            }
            if is_path:
                pathogenic_svs.append(sv)
            else:
                benign_svs.append(sv)

    print(f"  Pathogenic SVs: {len(pathogenic_svs)}")
    print(f"  Benign SVs: {len(benign_svs)}")

    result = {
        "source": "ClinVar variant_summary.txt.gz (NCBI FTP)",
        "filter": f"{sorted(VALID_CHROMS)}, 50-400kb, deletion+inversion, strict P/B only",
        "pathogenic_svs": pathogenic_svs,
        "benign_svs": benign_svs,
    }
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved: {out_path}")
    return result


# ── Scoring ──────────────────────────────────────────────────────────────────


def score_all_svs(
    svs: list[dict], strong_ctcf: dict, constraint: dict, genes: list[dict]
) -> list[dict]:
    """Run Step 0 + Step +2 on all SVs."""
    results = []
    for i, sv in enumerate(svs):
        if i % 20 == 0:
            print(f"  {i}/{len(svs)}...")
        sv_obj = StructuralVariant(
            chrom=sv["chrom"],
            sv_start=sv["start"],
            sv_end=sv["end"],
            sv_type=sv["type"],
        )
        try:
            scored = score_sv(sv_obj)
        except Exception as e:
            scored = {"verdict": "ERROR", "ratio": 0.0, "ctcf_rm": 0, "error": str(e)}

        verdict0 = scored.get("verdict", "ERROR")
        if verdict0 == "DISRUPTED":
            hi = find_hi_genes_step2(
                sv["chrom"], sv["start"], sv["end"], constraint, genes, strong_ctcf
            )
            verdict2 = "DISRUPTED_WITH_HI_GENE" if hi else "DISRUPTED_NO_HI_GENE"
        else:
            hi = []
            verdict2 = verdict0  # INTACT or ERROR

        results.append(
            {
                **sv,
                "ratio": scored.get("ratio", 0.0),
                "ctcf_rm": scored.get("ctcf_rm", 0),
                "verdict": verdict0,
                "step2_verdict": verdict2,
                "hi_genes": hi[:5],
            }
        )
    return results


def compute_metrics(svs: list[dict]) -> dict:
    tp = fn = fp = tn = err = 0
    for sv in svs:
        if sv["step2_verdict"] == "ERROR":
            err += 1
            continue
        pred = sv["step2_verdict"] == "DISRUPTED_WITH_HI_GENE"
        if sv["pathogenic"] and pred:
            tp += 1
        elif sv["pathogenic"] and not pred:
            fn += 1
        elif not sv["pathogenic"] and pred:
            fp += 1
        else:
            tn += 1
    n = tp + fn + fp + tn
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    return {
        "n": n,
        "TP": tp,
        "FN": fn,
        "FP": fp,
        "TN": tn,
        "errors": err,
        "recall": round(recall, 3),
        "precision": round(precision, 3),
        "FPR": round(fpr, 3),
    }


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    print("=" * 60)
    print("ARCHCODE-SV Independent Validation")
    print(f"Calibration set: {sorted(CALIBRATION_CHROMS)}")
    print(f"Validation set: {len(VALID_CHROMS)} chromosomes (never seen during tuning)")
    print("Parameters: FROZEN (LOEUF_BODY=0.80, window=200kb, CTCF>=50)")
    print("=" * 60)

    # 1. Load/download GENCODE for all chroms
    print("\n[1/5] GENCODE v47 genes (all chromosomes)...")
    all_genes = download_gencode_all(GENCODE_ALL_JSON)
    valid_genes = [g for g in all_genes if g["chrom"] in VALID_CHROMS]
    print(f"  Validation chrom genes: {len(valid_genes)}")

    # 2. Load gnomAD constraint
    print("\n[2/5] gnomAD constraint...")
    constraint, _ = load_gene_constraint()
    print(f"  {len(constraint)} genes with pLI/LOEUF")

    # 3. Load strong CTCF (all chroms, already genome-wide)
    print("\n[3/5] Strong CTCF sites (genome-wide)...")
    strong_ctcf = load_ctcf_strong()
    n_ctcf = sum(len(v) for v in strong_ctcf.values())
    print(f"  {n_ctcf} strong CTCF sites")

    # 4. Download/load ClinVar SVs for validation chroms
    print("\n[4/5] ClinVar SVs (validation chromosomes)...")
    clinvar_data = download_clinvar_svs(CLINVAR_JSON)
    path_svs = clinvar_data["pathogenic_svs"]
    benign_svs = clinvar_data["benign_svs"]
    print(f"  Pathogenic: {len(path_svs)} | Benign: {len(benign_svs)}")

    # Balance dataset (equal P/B for fair FPR measurement)
    n_each = min(len(path_svs), len(benign_svs), 100)
    all_svs = path_svs[:n_each] + benign_svs[:n_each]
    print(f"  Using balanced n={len(all_svs)} ({n_each} P + {n_each} B)")

    # 5. Score all SVs
    print(f"\n[5/5] Scoring {len(all_svs)} SVs (Step 0 + Step +2)...")
    print("  (may take several minutes — CTCF lookup per SV)")
    scored = score_all_svs(all_svs, strong_ctcf, constraint, valid_genes)

    m = compute_metrics(scored)
    print(f"\n{'=' * 60}")
    print("RESULTS — Independent validation (frozen parameters)")
    print(f"  n={m['n']} (errors={m['errors']})")
    print(f"  TP={m['TP']}  FN={m['FN']}  FP={m['FP']}  TN={m['TN']}")
    print(f"  Recall={m['recall']:.3f}  Precision={m['precision']:.3f}  FPR={m['FPR']:.3f}")
    print()

    # Compare to calibration
    print("Calibration (chr2/7/17, in-sample):  Recall=0.680  FPR=0.080  Precision=0.895")
    print(
        f"Validation  (other chroms, external): Recall={m['recall']:.3f}  FPR={m['FPR']:.3f}  Precision={m['precision']:.3f}"
    )
    print()
    if m["FPR"] <= 0.20 and m["recall"] >= 0.50:
        print("VERDICT: [VERIFIED-REAL] External validation PASSED")
        print("  FPR<=20% on unseen chromosomes -> parameters generalize")
    elif m["FPR"] <= 0.35:
        print("VERDICT: [HYPOTHESIS] Partial generalization — FPR degraded but tolerable")
        print("  Recommend: report as in-sample only, label external as preliminary")
    else:
        print("VERDICT: [NEEDS-INVESTIGATION] FPR>35% on unseen chromosomes -> overfitting")
        print("  Parameters do not generalize. Cannot claim external validation.")

    # Save
    out = {
        "evidence": "[VERIFIED-REAL] ClinVar 2026-06-26 + ENCODE CTCF K562 hg38 + gnomAD v2.1.1 + GENCODE v47",
        "validation_type": "external (chromosomes not used in calibration)",
        "calibration_chroms": sorted(CALIBRATION_CHROMS),
        "validation_chroms": sorted(VALID_CHROMS),
        "frozen_parameters": {
            "LOEUF_BODY": 0.80,
            "LOEUF_WINDOW": 0.35,
            "WINDOW_STEP2_KB": 200,
            "CTCF_BARRIER_SCORE": 50,
        },
        "metrics": m,
        "calibration_metrics": {"recall": 0.680, "FPR": 0.080, "precision": 0.895, "n": 50},
        "svs": scored,
    }
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {RESULTS_JSON}")


if __name__ == "__main__":
    main()
