"""
Сборка признаков для D1 (переформулированного, `scope_test.md` → REDIRECT).

Задача: **вариант → ген**. Для значимого eQTL-варианта V и гена-кандидата G в окне
предсказать, является ли пара (V, G) значимой. Это формулировка «causal genes» из
самой гипотезы D1 (`KILL_CRITERIA.md:66`).

  Позитивы  — (V, eGene), где V — лид-вариант этого eGene (минимальный pval)
  Негативы  — (V, G'), где G' — другой ген с TSS в том же окне, не eGene для V

Признаки:
  log10_dist   — baseline, парный  (расстояние вариант ↔ TSS)
  in_ccre      — baseline, ПО-ВАРИАНТНЫЙ (см. предупреждение ниже)
  contact      — baseline, парный  ← ДОБАВЛЕН REDIRECT'ом, сырая сила контакта Hi-C
  spec_resist  — ТЕСТОВЫЙ, парный  — эффективное сопротивление в лапласиане окна

⚠️ ПО-ВАРИАНТНЫЕ признаки не различают кандидатов. Для одного V все гены-кандидаты
имеют одно и то же `in_ccre` и один и тот же скалярный Δλ. Поэтому **Δλ как скаляр
на вариант физически не может решать эту задачу** — нужен ПАРНЫЙ спектральный признак.
Отсюда `spec_resist`: эффективное сопротивление строится из псевдообратного лапласиана,
то есть остаётся спектральной величиной, но определено на паре.
Записано до прогона; это не подгонка, а следствие постановки задачи.

⚠️ Окно ФИКСИРОВАННОЕ (вариант ± 500 кб). Окно «от варианта до гена с отступом» росло
бы вместе с расстоянием, и спектральный признак начал бы кодировать расстояние — то
есть тестовый признак частично стал бы baseline. Фиксированный размер это исключает.

Запуск:
    python build_dataset.py --chroms chr1 --out features_chr1.parquet
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import cooler
import h5py
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared_utils"))
from remote_hdf5 import HTTPRangeFile

DATA = Path(__file__).parent / "data"
HIC_URL = (
    "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/"
    "077a1498-e1ad-429a-b976-8f71625ebdb6/4DNFINPH7UOD.mcool"
)
RESOLUTION = 10_000
HALF_WINDOW = 500_000  # фиксировано, см. предупреждение в docstring
ELS_TYPES = ("pELS", "dELS", "PLS")


def load_gene_tss() -> pd.DataFrame:
    """TSS генов из GENCODE v26 — той же версии, на которой построен GTEx v8."""
    rows = []
    pat = re.compile(r'gene_id "([^"]+)".*?gene_type "([^"]+)"')
    with (DATA / "gencode.v26.GRCh38.genes.gtf").open() as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            p = line.split("\t")
            if p[2] != "gene":
                continue
            m = pat.search(p[8])
            if not m:
                continue
            # WHY strand: TSS -- начало гена по направлению транскрипции, не min(start,end)
            tss = int(p[3]) if p[6] == "+" else int(p[4])
            rows.append((m.group(1), p[0], tss, m.group(2)))
    df = pd.DataFrame(rows, columns=["gene_id", "chrom", "tss", "gene_type"])
    return df[df.gene_type.isin(["protein_coding", "lincRNA"])].reset_index(drop=True)


def load_lead_variants() -> pd.DataFrame:
    """
    Лид-вариант на eGene: минимальный pval_nominal.

    WHY один вариант на ген, а не все 458k значимых пар: варианты в LD дублируют друг
    друга, и AUC на полном наборе измеряла бы в основном размер LD-блоков.
    """
    df = pd.read_csv(
        DATA / "LCL.v8.signif_variant_gene_pairs.txt.gz",
        sep="\t",
        usecols=["variant_id", "gene_id", "pval_nominal"],
    )
    lead = df.loc[df.groupby("gene_id").pval_nominal.idxmin()].copy()
    v = lead.variant_id.str.split("_", expand=True)
    lead["chrom"], lead["pos"] = v[0], v[1].astype(int)
    return lead.reset_index(drop=True), set(zip(df.variant_id, df.gene_id, strict=True))


def load_ccre() -> dict[str, np.ndarray]:
    cols = ["chrom", "start", "end", "id1", "id2", "ctype"]
    df = pd.read_csv(DATA / "GRCh38-cCREs.bed", sep="\t", header=None, names=cols)
    df = df[df.ctype.str.contains("|".join(ELS_TYPES), na=False)]
    return {c: g[["start", "end"]].to_numpy() for c, g in df.groupby("chrom")}


def _adjacency(mat: np.ndarray) -> np.ndarray:
    a = np.nan_to_num(mat, nan=0.0)
    np.fill_diagonal(a, 0.0)
    return 0.5 * (a + a.T)


def effective_resistance(mat: np.ndarray, i: int, j: int) -> float:
    """
    Эффективное сопротивление между узлами i и j в графе контактов окна.

    R(i,j) = L⁺[i,i] + L⁺[j,j] − 2·L⁺[i,j],  где L = D − A, L⁺ — псевдообратная.

    WHY именно эта величина, а не сырой контакт: R строится из ПОЛНОГО спектра
    лапласиана и учитывает все пути между узлами, а не только прямое ребро. Это и есть
    «спектральная информация сверх контакта» — ровно тот вопрос, который ставит redirect.
    """
    a = _adjacency(mat)
    deg = a.sum(axis=1)
    # WHY регуляризация: изолированные бины (полностью пустые строки Hi-C) дают
    # бесконечное сопротивление. Малая добавка делает граф связным, не искажая
    # относительный порядок величин.
    lap = np.diag(deg + 1e-9) - a
    pinv = np.linalg.pinv(lap, hermitian=True)
    return float(pinv[i, i] + pinv[j, j] - 2 * pinv[i, j])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chroms", nargs="+", default=["chr1"])
    ap.add_argument("--out", default="features_chr1.parquet")
    ap.add_argument("--limit", type=int, default=0, help="0 = без ограничения")
    args = ap.parse_args()

    print("загрузка аннотаций…")
    genes = load_gene_tss()
    lead, signif_set = load_lead_variants()
    ccre = load_ccre()
    print(
        f"  генов {len(genes):,} · лид-вариантов {len(lead):,} · значимых пар {len(signif_set):,}"
    )

    hfile = HTTPRangeFile(HIC_URL, block_size=2**20)
    clr = cooler.Cooler(h5py.File(hfile, "r")[f"resolutions/{RESOLUTION}"])

    rows, t0 = [], time.perf_counter()
    for chrom in args.chroms:
        sub = lead[lead.chrom == chrom].sort_values("pos")
        if args.limit:
            sub = sub.head(args.limit)
        gsub = genes[genes.chrom == chrom]
        creg = ccre.get(chrom, np.empty((0, 2)))
        print(f"{chrom}: {len(sub)} лид-вариантов, {len(gsub)} генов")

        for n, (_, r) in enumerate(sub.iterrows(), 1):
            lo = max(0, r.pos - HALF_WINDOW)
            hi = r.pos + HALF_WINDOW
            cand = gsub[(gsub.tss >= lo) & (gsub.tss < hi)]
            if len(cand) < 2:  # нужен хотя бы один негатив
                continue
            try:
                mat = clr.matrix(balance=True).fetch(f"{chrom}:{lo}-{hi}")
            except (ValueError, KeyError):
                # WHY узкие типы: cooler бросает их на регионах вне хромосомы. Голый
                # except прятал бы и настоящие сбои чтения по сети.
                continue
            vbin = (r.pos - lo) // RESOLUTION
            if vbin >= mat.shape[0]:
                continue
            in_ccre = int(((creg[:, 0] <= r.pos) & (creg[:, 1] > r.pos)).any()) if len(creg) else 0
            # WHY маргиналы: у бина с НУЛЕВЫМ покрытием Hi-C эффективное сопротивление
            # определяется только регуляризацией 1e-9 и взлетает до ~2e9. Замер на пилоте:
            # 38.9% пар. Такая пара несёт не спектральную информацию, а сам факт "бин
            # пустой" -- то есть прокси для baseline contact. Флаг позволяет исключить их
            # по ПРЕ-РЕГИСТРИРОВАННОМУ правилу, а не задним числом.
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
                        "gene_id": g.gene_id,
                        "label": int((r.variant_id, g.gene_id) in signif_set),
                        "log10_dist": float(np.log10(1 + abs(r.pos - g.tss))),
                        "in_ccre": in_ccre,
                        "contact": 0.0 if np.isnan(contact) else float(contact),
                        "spec_resist": effective_resistance(mat, int(vbin), int(gbin)),
                        "bin_ok": int(marg[int(vbin)] > 0 and marg[int(gbin)] > 0),
                    }
                )
            if n % 50 == 0:
                print(
                    f"    {n}/{len(sub)}  пар {len(rows):,}  "
                    f"скачано {hfile.bytes_fetched / 1e6:.0f} МБ  {time.perf_counter() - t0:.0f}s"
                )

    df = pd.DataFrame(rows)
    df.to_parquet(args.out)
    print("-" * 60)
    print(f"пар всего {len(df):,} · позитивов {df.label.sum():,} ({df.label.mean():.1%})")
    print(f"вариантов {df.variant_id.nunique():,} · скачано {hfile.bytes_fetched / 1e6:.0f} МБ")
    print(f"saved: {args.out}  ({time.perf_counter() - t0:.0f}s)")


if __name__ == "__main__":
    main()
