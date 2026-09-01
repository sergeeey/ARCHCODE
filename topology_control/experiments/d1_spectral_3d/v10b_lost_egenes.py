"""
V10-B — чем отличаются 531 eGene, потерянные при сопоставлении GTEx v10 с GENCODE v26.

WHY: `decision_v10_replication.md` назвал это единственной честной оговоркой
репликации — TSS взяты из аннотации под v8, eGenes из v10, пересечение 95.7%.
Оговорка бесполезна, пока не сказано НАПРАВЛЕНИЕ смещения: потерянные гены
случайны или систематически иные?

Это НЕ проверка гипотезы, а характеризация пропущенных данных. Вердикта не выносит.
Запуск: python v10b_lost_egenes.py
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from build_dataset import DATA, load_gene_tss

V10 = "LCL.v10.Cells_EBV-transformed_lymphocytes.v10.eQTLs.signif_pairs.parquet"


def strip_ver(s: pd.Series) -> pd.Series:
    return s.str.replace(r"\.\d+$", "", regex=True)


def main() -> None:
    df = pd.read_parquet(DATA / V10, columns=["variant_id", "gene_id", "pval_nominal"])
    df["gene_base"] = strip_ver(df.gene_id)

    genes = load_gene_tss()
    known = set(strip_ver(genes.gene_id))

    per_gene = df.groupby("gene_base").agg(
        n_pairs=("variant_id", "size"), best_p=("pval_nominal", "min")
    )
    per_gene["matched"] = per_gene.index.isin(known)

    lost, kept = per_gene[~per_gene.matched], per_gene[per_gene.matched]
    out: dict = {"n_lost": len(lost), "n_kept": len(kept)}

    print("=" * 68)
    print("V10-B — характеризация eGenes, потерянных при v10 x GENCODE v26")
    print("=" * 68)
    print(f"потеряно {len(lost):,} · сопоставлено {len(kept):,} "
          f"({len(kept) / len(per_gene):.1%})\n")

    # 1. Сила сигнала: слабее ли они?
    for name, sub in (("потерянные", lost), ("сопоставленные", kept)):
        out[f"median_pairs_{name}"] = float(sub.n_pairs.median())
        out[f"median_logp_{name}"] = float(np.log10(sub.best_p.clip(lower=1e-300)).median())
        print(f"  {name:16s} медиана пар/ген {sub.n_pairs.median():7.1f} · "
              f"медиана log10(best p) {np.log10(sub.best_p.clip(lower=1e-300)).median():7.2f}")

    # 2. Возраст аннотации: номер ENSG растёт со временем добавления гена
    def ensg_num(idx: pd.Index) -> pd.Series:
        return pd.to_numeric(pd.Series(idx).str.extract(r"ENSG(\d+)", expand=False), errors="coerce")

    n_lost, n_kept = ensg_num(lost.index), ensg_num(kept.index)
    out["median_ensg_lost"] = float(n_lost.median())
    out["median_ensg_kept"] = float(n_kept.median())
    print(f"\n  медиана номера ENSG: потерянные {n_lost.median():,.0f} · "
          f"сопоставленные {n_kept.median():,.0f}")
    hi = 260_000  # WHY: гены с ENSG00000260000+ добавлены в аннотацию поздно
    out["frac_lost_high_ensg"] = float((n_lost > hi).mean())
    out["frac_kept_high_ensg"] = float((n_kept > hi).mean())
    print(f"  доля с ENSG > {hi:,}: потерянные {(n_lost > hi).mean():.1%} · "
          f"сопоставленные {(n_kept > hi).mean():.1%}")

    # 3. Где они лежат
    chrom = df.drop_duplicates("gene_base").set_index("gene_base").variant_id.str.split("_").str[0]
    lost_chr = chrom.reindex(lost.index).value_counts(normalize=True).head(4)
    print("\n  топ-хромосомы потерянных:",
          ", ".join(f"{c} {v:.1%}" for c, v in lost_chr.items()))
    out["top_chrom_lost"] = {str(c): float(v) for c, v in lost_chr.items()}

    # 4. Сколько ПАР теряется, а не генов — это и есть цена для датасета
    lost_pairs = int(lost.n_pairs.sum())
    out["lost_pairs"] = lost_pairs
    out["lost_pairs_frac"] = float(lost_pairs / per_gene.n_pairs.sum())
    print(f"\n  потеряно значимых ПАР: {lost_pairs:,} из {per_gene.n_pairs.sum():,} "
          f"({lost_pairs / per_gene.n_pairs.sum():.2%})")
    print(f"  для сравнения, потеряно ГЕНОВ: {len(lost) / len(per_gene):.2%}")

    with open("v10b_lost_egenes.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("\nsaved: v10b_lost_egenes.json")


if __name__ == "__main__":
    main()
