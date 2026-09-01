"""
V10-A — пересборка D1 на TSS, СОГЛАСОВАННЫХ с GTEx v10.

Метод оказался лучше исходного плана. Вместо скачивания GENCODE v39 (версия
установлена одним источником, то есть догадка) TSS восстанавливается ТОЧНО из
самого файла GTEx: `TSS = variant_pos - tss_distance`.

ПОЗИТИВНЫЙ КОНТРОЛЬ МЕТОДА: та же формула на v8 воспроизводит GENCODE v26
на 135 887 парах с совпадением 100.00% и медианой отклонения 0 п.о.
Это не предположение, а измерение.

Что даёт: аннотацию, которой пользовался сам GTEx v10, включая 3 103 гена,
отсутствующих в v26 — то есть закрывает дефект, найденный V10-B (30.45%
потерянных значимых пар).

Универсум кандидатов:
  * eGenes v10 (12 428) — TSS восстановлен из v10, точный
  * остальные гены v26 (protein_coding + lincRNA), не являющиеся eGenes v10 —
    TSS из v26. Это чистые негативы, их погрешность та же, что была в v8-прогоне.
  ⚠️ Аннотация смешанная. Названо явно, не спрятано.

Запуск: python -u build_dataset_v10a.py --out features_v10a.parquet
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import cooler
import h5py
import numpy as np
import pandas as pd

from build_dataset import (
    DATA,
    HALF_WINDOW,
    HIC_URL,
    RESOLUTION,
    HTTPRangeFile,
    _adjacency,
    effective_resistance,
    load_ccre,
    load_gene_tss,
)

V10 = "LCL.v10.Cells_EBV-transformed_lymphocytes.v10.eQTLs.signif_pairs.parquet"


def strip_ver(s: pd.Series) -> pd.Series:
    return s.str.replace(r"\.\d+$", "", regex=True)


def build_universe(df: pd.DataFrame) -> pd.DataFrame:
    """TSS: точные из v10 для eGenes, из v26 для прочих кандидатов."""
    v10 = df.drop_duplicates("gene_base")[["gene_base", "chrom", "tss"]].copy()
    v10["src"] = "v10"

    g = load_gene_tss()
    g["gene_base"] = strip_ver(g.gene_id)
    extra = g[~g.gene_base.isin(set(v10.gene_base))][["gene_base", "chrom", "tss"]].copy()
    extra["src"] = "v26"

    uni = pd.concat([v10, extra], ignore_index=True)
    print(f"  универсум: {len(uni):,} генов = {len(v10):,} (TSS из v10) "
          f"+ {len(extra):,} (TSS из v26)", flush=True)
    return uni


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chroms", nargs="+", default=[f"chr{i}" for i in range(1, 23)])
    ap.add_argument("--out", default="features_v10a.parquet")
    args = ap.parse_args()

    print("загрузка v10 + восстановление TSS…", flush=True)
    df = pd.read_parquet(DATA / V10, columns=["variant_id", "gene_id", "pval_nominal", "tss_distance"])
    df["gene_base"] = strip_ver(df.gene_id)
    v = df.variant_id.str.split("_", expand=True)
    df["chrom"], df["pos"] = v[0], v[1].astype(int)
    df["tss"] = df.pos - df.tss_distance

    signif = set(zip(df.variant_id, df.gene_base, strict=True))
    lead = df.loc[df.groupby("gene_base").pval_nominal.idxmin()].reset_index(drop=True)
    genes = build_universe(df)
    ccre = load_ccre()
    print(f"  лид-вариантов {len(lead):,} · значимых пар {len(signif):,}", flush=True)

    hfile = HTTPRangeFile(HIC_URL, block_size=2**20)
    clr = cooler.Cooler(h5py.File(hfile, "r")[f"resolutions/{RESOLUTION}"])

    part_dir = Path("v10a_parts")
    part_dir.mkdir(exist_ok=True)
    t0 = time.perf_counter()

    for chrom in args.chroms:
        part = part_dir / f"{chrom}.parquet"
        if part.exists():
            print(f"{chrom}: уже собрана, пропуск", flush=True)
            continue
        rows: list[dict] = []
        sub = lead[lead.chrom == chrom].sort_values("pos")
        gsub = genes[genes.chrom == chrom]
        creg = ccre.get(chrom, np.empty((0, 2)))
        print(f"{chrom}: {len(sub)} лид-вариантов, {len(gsub)} генов", flush=True)

        for n, (_, r) in enumerate(sub.iterrows(), 1):
            lo, hi = max(0, r.pos - HALF_WINDOW), r.pos + HALF_WINDOW
            cand = gsub[(gsub.tss >= lo) & (gsub.tss < hi)]
            if len(cand) < 2:
                continue
            try:
                mat = clr.matrix(balance=True).fetch(f"{chrom}:{lo}-{hi}")
            except (ValueError, KeyError):
                continue
            vbin = (r.pos - lo) // RESOLUTION
            if vbin >= mat.shape[0]:
                continue
            in_ccre = int(((creg[:, 0] <= r.pos) & (creg[:, 1] > r.pos)).any()) if len(creg) else 0
            marg = _adjacency(mat).sum(axis=1)

            for _, g in cand.iterrows():
                gbin = (g.tss - lo) // RESOLUTION
                if gbin >= mat.shape[0]:
                    continue
                contact = mat[vbin, gbin]
                rows.append({
                    "chrom": chrom, "variant_id": r.variant_id, "gene_id": g.gene_base,
                    "label": int((r.variant_id, g.gene_base) in signif),
                    "log10_dist": float(np.log10(1 + abs(r.pos - g.tss))),
                    "in_ccre": in_ccre,
                    "contact": 0.0 if np.isnan(contact) else float(contact),
                    "spec_resist": effective_resistance(mat, int(vbin), int(gbin)),
                    "bin_ok": int(marg[int(vbin)] > 0 and marg[int(gbin)] > 0),
                    "tss_src": g.src,
                })
            if n % 100 == 0:
                print(f"    {n}/{len(sub)}  пар {len(rows):,}  "
                      f"{hfile.bytes_fetched / 1e6:.0f} МБ  {time.perf_counter() - t0:.0f}s", flush=True)

        tmp = part.with_suffix(".tmp")
        pd.DataFrame(rows).to_parquet(tmp)
        os.replace(tmp, part)
        print(f"  -> {part.name}: {len(rows):,} пар", flush=True)

    out = pd.concat([pd.read_parquet(part_dir / f"{c}.parquet") for c in args.chroms],
                    ignore_index=True)
    out.to_parquet(args.out)
    print("-" * 60, flush=True)
    print(f"пар {len(out):,} · позитивов {out.label.sum():,} ({out.label.mean():.2%}) · "
          f"вариантов {out.variant_id.nunique():,}", flush=True)
    print(f"TSS из v10: {(out.tss_src == 'v10').mean():.1%} строк", flush=True)
    print(f"saved: {args.out}  ({time.perf_counter() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
