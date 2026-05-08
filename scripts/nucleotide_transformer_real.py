"""
Nucleotide Transformer REAL — полная версия с foundation model

Использует InstaDeepAI/nucleotide-transformer-v2-500m-multi-species
для вычисления learned embeddings вместо edit distance
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
from sklearn.metrics import roc_auc_score, roc_curve
import requests
import time
import torch
from transformers import AutoTokenizer, AutoModel

# Global model/tokenizer (loaded once)
MODEL = None
TOKENIZER = None


def load_model():
    """Load Nucleotide Transformer model (one-time ~2GB download)"""
    global MODEL, TOKENIZER

    if MODEL is None:
        print("Loading Nucleotide Transformer v2-100m...")
        print("(First run: ~500MB download, subsequent runs: instant)")

        # Using 100m version for faster CPU inference (500m takes ~10 sec/variant on CPU)
        model_name = "InstaDeepAI/nucleotide-transformer-v2-100m-multi-species"

        TOKENIZER = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True, force_download=True
        )
        MODEL = AutoModel.from_pretrained(model_name, trust_remote_code=True, force_download=True)

        # CPU mode (no GPU required for 47 variants)
        MODEL.eval()

        print("✓ Model loaded")

    return MODEL, TOKENIZER


def fetch_sequence(chrom: str, start: int, end: int, retry=3) -> str:
    """Fetch reference sequence from Ensembl REST API"""
    server = "https://rest.ensembl.org"
    ext = f"/sequence/region/human/{chrom}:{start}..{end}:1?content-type=text/plain"

    for attempt in range(retry):
        try:
            response = requests.get(server + ext, headers={"Content-Type": "text/plain"})
            if response.ok:
                return response.text.strip().upper()
            time.sleep(2**attempt)
        except Exception as e:
            print(f"  Retry {attempt+1}/{retry}: {e}")
            time.sleep(2**attempt)

    raise RuntimeError(f"Failed to fetch sequence after {retry} attempts")


def apply_variant(ref_seq: str, pos_in_window: int, ref: str, alt: str) -> str:
    """Apply variant to reference sequence"""
    before = ref_seq[:pos_in_window]
    after = ref_seq[pos_in_window + len(ref) :]
    return before + alt + after


def compute_embedding_delta_real(wt_seq: str, mut_seq: str) -> float:
    """
    REAL VERSION — uses Nucleotide Transformer learned embeddings

    Returns: L2 norm of (wt_embedding - mut_embedding)
    """
    model, tokenizer = load_model()

    with torch.no_grad():
        # Tokenize
        wt_tokens = tokenizer(
            wt_seq, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        mut_tokens = tokenizer(
            mut_seq, return_tensors="pt", padding=True, truncation=True, max_length=512
        )

        # Get embeddings (last hidden state, mean pooling)
        wt_output = model(**wt_tokens)
        mut_output = model(**mut_tokens)

        wt_emb = wt_output.last_hidden_state.mean(dim=1).squeeze()  # [hidden_dim]
        mut_emb = mut_output.last_hidden_state.mean(dim=1).squeeze()

        # L2 distance
        delta = torch.norm(wt_emb - mut_emb).item()

    return float(delta)


def load_pearl_and_benign_variants(
    csv_path: Path, seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load 27 pearls + 27 random benign from HBB atlas"""
    df = pd.read_csv(csv_path)

    # Pearls
    pearls = df[df["Pearl"] == True].copy()
    print(f"Total pearls: {len(pearls)}")
    pearls = pearls.head(27)
    print(f"Using pearls: {len(pearls)}")

    # Benign
    benign = df[df["Label"] == "Benign"].copy()
    print(f"Total benign: {len(benign)}")
    np.random.seed(seed)
    benign_sample = benign.sample(n=min(27, len(benign)), random_state=seed)
    print(f"Using benign: {len(benign_sample)}")

    return pearls, benign_sample


def main():
    print("=" * 80)
    print("NUCLEOTIDE TRANSFORMER REAL — HBB Pearl vs Benign")
    print("=" * 80)
    print()

    # Paths
    project_root = Path(__file__).parent.parent
    atlas_path = project_root / "results" / "HBB_Unified_Atlas.csv"
    output_path = project_root / "results" / "nucleotide_transformer_real.json"

    # Load data
    print("STEP 1: Loading variants...")
    pearls, benign = load_pearl_and_benign_variants(atlas_path, seed=42)

    print()
    print("STEP 2: Loading Nucleotide Transformer model...")
    load_model()  # Pre-load model

    print()
    print("STEP 3: Computing embeddings (REAL)...")
    print("ETA: ~8-10 min on CPU (~10 sec/variant)")
    print()

    results = []
    start_time = time.time()

    for idx, (label, df) in enumerate([("Pearl", pearls), ("Benign", benign)]):
        print(f"\nProcessing {label} variants ({len(df)})...")

        for i, row in df.iterrows():
            variant_id = row["ClinVar_ID"]
            pos = row["Position_GRCh38"]
            ref = row["Ref"]
            alt = row["Alt"]
            category = row["Category"]
            lssim = row["ARCHCODE_LSSIM"]

            # Window ±128bp
            start = pos - 128
            end = pos + 128

            try:
                # Fetch reference sequence
                ref_seq = fetch_sequence("11", start, end)
                pos_in_window = 128
                mut_seq = apply_variant(ref_seq, pos_in_window, ref, alt)

                # Compute REAL embedding delta
                variant_start = time.time()
                emb_delta = compute_embedding_delta_real(ref_seq, mut_seq)
                variant_time = time.time() - variant_start

                results.append(
                    {
                        "variant_id": variant_id,
                        "label": label,
                        "position": int(pos),
                        "ref": ref,
                        "alt": alt,
                        "category": category,
                        "lssim": float(lssim),
                        "embedding_delta": float(emb_delta),
                        "seq_length_wt": len(ref_seq),
                        "seq_length_mut": len(mut_seq),
                        "compute_time_sec": round(variant_time, 2),
                    }
                )

                print(
                    f"  ✓ {variant_id} | {category} | delta={emb_delta:.4f} | {variant_time:.1f}s"
                )

            except Exception as e:
                print(f"  ✗ {variant_id} | ERROR: {e}")
                continue

            # Rate limit Ensembl
            time.sleep(0.1)

    total_time = time.time() - start_time

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    print()
    print("=" * 80)
    print("STEP 4: Statistical analysis")
    print("=" * 80)

    # Pearl vs Benign comparison
    pearl_deltas = results_df[results_df["label"] == "Pearl"]["embedding_delta"].values
    benign_deltas = results_df[results_df["label"] == "Benign"]["embedding_delta"].values

    u_stat, p_value = stats.mannwhitneyu(pearl_deltas, benign_deltas, alternative="two-sided")

    # Effect size (rank-biserial correlation)
    r_rb = 1 - (2 * u_stat) / (len(pearl_deltas) * len(benign_deltas))

    print(f"\nPearl vs Benign (REAL embedding_delta):")
    print(f"  Pearl:  {pearl_deltas.mean():.4f} ± {pearl_deltas.std():.4f}")
    print(f"  Benign: {benign_deltas.mean():.4f} ± {benign_deltas.std():.4f}")
    print(f"  Mann-Whitney U: {u_stat:.1f}")
    print(f"  p-value: {p_value:.6f} {'✓ SIGNIFICANT' if p_value < 0.05 else '✗ NOT significant'}")
    print(f"  Effect size (r): {r_rb:.3f}")

    # ROC AUC
    if len(pearl_deltas) > 0 and len(benign_deltas) > 0:
        y_true = np.concatenate([np.ones(len(pearl_deltas)), np.zeros(len(benign_deltas))])
        y_score = np.concatenate([pearl_deltas, benign_deltas])

        try:
            auc = roc_auc_score(y_true, y_score)
            print(f"  ROC AUC: {auc:.3f}")

            # Compare to baseline (categorical = 0.977, position-only = 0.551)
            if auc > 0.60:
                print(f"    ✓ IMPROVEMENT over position-only baseline (0.551)")
            else:
                print(f"    ✗ Below target (0.60)")
        except:
            print(f"  ROC AUC: N/A")

    # Within-category AUC
    print("\nWithin-category AUC:")
    categories = results_df["category"].unique()
    within_cat_results = []

    for cat in categories:
        cat_df = results_df[results_df["category"] == cat]
        n_pearl = (cat_df["label"] == "Pearl").sum()
        n_benign = (cat_df["label"] == "Benign").sum()

        if n_pearl > 0 and n_benign > 0:
            y_true_cat = (cat_df["label"] == "Pearl").astype(int).values
            y_score_cat = cat_df["embedding_delta"].values

            try:
                auc_cat = roc_auc_score(y_true_cat, y_score_cat)
                print(f"  {cat}: AUC={auc_cat:.3f} (pearl={n_pearl}, benign={n_benign})")

                within_cat_results.append(
                    {
                        "category": cat,
                        "auc": auc_cat,
                        "n_pearl": int(n_pearl),
                        "n_benign": int(n_benign),
                    }
                )
            except:
                print(f"  {cat}: N/A")

    # Performance stats
    print(f"\nPerformance:")
    print(f"  Total time: {total_time/60:.1f} min")
    print(f"  Per variant: {total_time/len(results_df):.1f} sec")

    # Save results
    print()
    print(f"Saving results to {output_path}...")

    output_data = {
        "analysis": "nucleotide_transformer_real",
        "model": "InstaDeepAI/nucleotide-transformer-v2-500m-multi-species",
        "n_pearl": len(pearl_deltas),
        "n_benign": len(benign_deltas),
        "pearl_mean_delta": float(pearl_deltas.mean()),
        "pearl_std_delta": float(pearl_deltas.std()),
        "benign_mean_delta": float(benign_deltas.mean()),
        "benign_std_delta": float(benign_deltas.std()),
        "mann_whitney_u": float(u_stat),
        "mann_whitney_p": float(p_value),
        "effect_size_r": float(r_rb),
        "roc_auc": float(auc) if "auc" in locals() else None,
        "within_category_auc": within_cat_results,
        "total_time_min": round(total_time / 60, 2),
        "per_variant_sec": round(total_time / len(results_df), 2),
        "variants": results_df.to_dict(orient="records"),
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print("✓ Done!")
    print()

    # Decision tree
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)

    if p_value < 0.05:
        print("✓ SIGNIFICANT discrimination detected")
        if auc > 0.60:
            print("✓ AUC above target (0.60)")
            print("\n→ EXPAND to full HBB (1,103 variants)")
            print("→ CROSS-LOCUS validation (BRCA1, TP53)")
        else:
            print("⚠ AUC below target but p<0.05")
            print("\n→ CHECK within-category AUC")
            print("→ INSPECT high-delta variants")
    else:
        print("✗ NO significant discrimination")
        print("\n→ PIVOT to Pathway 3 (Computational Closed-Loop)")
        print("→ OR try Yang nucleosome states (when available)")


if __name__ == "__main__":
    main()
