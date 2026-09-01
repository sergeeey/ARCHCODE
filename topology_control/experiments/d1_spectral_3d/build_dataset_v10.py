"""
Сборка признаков D1 на GTEx **v10** — репликация с бо́льшим объёмом данных.

WHY отдельный файл, а не флаг в build_dataset.py: тот привязан к замороженной
пре-регистрации `0f8cbb4` и должен остаться исполнимым дословно. Здесь меняется
ТОЛЬКО источник eQTL, вся геометрия (Hi-C GM12878, окно ±500 кб, разрешение 10 кб,
признаки) наследуется импортом.

Отличия v10 от v8, замеренные до прогона:
  * 1,841,906 значимых пар против 458,161 — в 4.02 раза больше
  * 12,428 уникальных eGenes
  * формат parquet вместо txt.gz; колонка `af` вместо `maf`
  * ⚠️ GENCODE: TSS берутся из v26 (версия под v8), покрытие eGenes v10 — 95.7%,
    теряется 531 ген. Сопоставление по ENSG БЕЗ суффикса версии.

ПРЕДСКАЗАНИЕ, зафиксированное до прогона: вердикт не изменится, ΔAUC < 0.02,
и разложение baseline сохранится (контакт добавляет ~0 над расстоянием).

Запуск: python -u build_dataset_v10.py --out features_v10.parquet
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
    """
    WHY ассерт: снятие суффикса версии — единственное место, где ДВА разных гена могли бы
    слиться в один ключ и молча испортить метку `label`. На фактических данных коллизий
    ноль (проверено 2026-09-01: GTEx v10 12 428 ↔ 12 428, GENCODE 26 724 ↔ 26 724), но это
    свойство ЭТИХ файлов, а не кода. Другая сборка аннотации обязана падать здесь, а не
    отдавать неверные метки.
    """
    out = s.str.replace(r"\.\d+$", "", regex=True)
    assert s.nunique() == out.nunique(), (
        f"коллизия при снятии версии ENSG: {s.nunique()} уникальных id -> "
        f"{out.nunique()} уникальных базовых — метки были бы неверны"
    )
    return out


def load_lead_v10():
    df = pd.read_parquet(DATA / V10, columns=["variant_id", "gene_id", "pval_nominal"])
    df["gene_base"] = strip_ver(df.gene_id)
    lead = df.loc[df.groupby("gene_base").pval_nominal.idxmin()].copy()
    v = lead.variant_id.str.split("_", expand=True)
    lead["chrom"], lead["pos"] = v[0], v[1].astype(int)
    return lead.reset_index(drop=True), set(zip(df.variant_id, df.gene_base, strict=True))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chroms", nargs="+", default=[f"chr{i}" for i in range(1, 23)])
    ap.add_argument("--out", default="features_v10.parquet")
    args = ap.parse_args()

    print("загрузка аннотаций…", flush=True)
    genes = load_gene_tss()
    genes["gene_base"] = strip_ver(genes.gene_id)
    lead, signif = load_lead_v10()
    ccre = load_ccre()
    print(
        f"  генов {len(genes):,} · лид-вариантов {len(lead):,} · значимых пар {len(signif):,}",
        flush=True,
    )

    # WHY блок 1 МБ вместо DEFAULT_BLOCK=4 МБ: доступ здесь точечный (200x200 подматрица
    # на вариант), и 4-мегабайтный блок тянет лишнее на каждый промах кэша. Плата —
    # больше range-запросов, то есть больше шансов поймать обрыв keep-alive; это
    # компенсировано ретраями в HTTPRangeFile._block, добавленными в том же коммите.
    hfile = HTTPRangeFile(HIC_URL, block_size=2**20)
    clr = cooler.Cooler(h5py.File(hfile, "r")[f"resolutions/{RESOLUTION}"])

    # WHY почанковое сохранение: первый прогон умер на chr1 от RemoteDisconnected,
    # потеряв всё. Чекпойнт по хромосоме делает обрыв транспорта стоимостью в одну
    # хромосому, а не в весь прогон.
    #
    # WHY запись через .tmp + os.replace: `if part.exists(): skip` — корректная проверка
    # возобновления ТОЛЬКО если создание файла атомарно. Иначе процесс, убитый посреди
    # to_parquet, оставляет обрезанный файл, который следующий запуск примет за готовый.
    # os.replace атомарен и на POSIX, и на Windows, поэтому exists() видит либо целое,
    # либо ничего. "Существует" и "дописан" — два разных утверждения.
    part_dir = Path("v10_parts")
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
                rows.append(
                    {
                        "chrom": chrom,
                        "variant_id": r.variant_id,
                        "gene_id": g.gene_base,
                        "label": int((r.variant_id, g.gene_base) in signif),
                        "log10_dist": float(np.log10(1 + abs(r.pos - g.tss))),
                        "in_ccre": in_ccre,
                        "contact": 0.0 if np.isnan(contact) else float(contact),
                        "spec_resist": effective_resistance(mat, int(vbin), int(gbin)),
                        "bin_ok": int(marg[int(vbin)] > 0 and marg[int(gbin)] > 0),
                    }
                )
            if n % 100 == 0:
                print(
                    f"    {n}/{len(sub)}  пар {len(rows):,}  "
                    f"{hfile.bytes_fetched / 1e6:.0f} МБ  {time.perf_counter() - t0:.0f}s",
                    flush=True,
                )
        tmp = part.with_suffix(".tmp")
        pd.DataFrame(rows).to_parquet(tmp)
        os.replace(tmp, part)
        print(f"  -> {part.name}: {len(rows):,} пар", flush=True)

    df = pd.concat(
        [pd.read_parquet(part_dir / f"{c}.parquet") for c in args.chroms], ignore_index=True
    )
    df.to_parquet(args.out)
    print("-" * 60, flush=True)
    print(
        f"пар {len(df):,} · позитивов {df.label.sum():,} ({df.label.mean():.2%}) · "
        f"вариантов {df.variant_id.nunique():,}",
        flush=True,
    )
    print(f"saved: {args.out}  ({time.perf_counter() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
