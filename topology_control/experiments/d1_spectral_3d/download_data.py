"""
T1 — загрузка данных для D1 (переформулированного, см. `scope_test.md` → REDIRECT).

Все источники публичные, без ключей и без оплаты.

| Источник | Что | Зачем |
|---|---|---|
| 4DN 4DNFINPH7UOD | Hi-C GM12878, in situ MboI, .mcool | контактная матрица: и baseline (сила контакта), и предиктор (Δλ) |
| GTEx v8 LCL | signif_variant_gene_pairs | endpoint: eQTL. Ткань `Cells_EBV-transformed_lymphocytes` = LCL = **тот же тип клеток, что GM12878** |
| GENCODE v26 | gene GTF | TSS генов для baseline «расстояние» |
| SCREEN v4 | GRCh38 cCRE BED | baseline «перекрытие с энхансером» |

WHY именно GM12878 + LCL: D1 в `KILL_CRITERIA.md` требует, чтобы эффект выживал при
cell-type matching. Здесь совпадение по типу клеток есть ПО ПОСТРОЕНИЮ, а не проверяется
задним числом.

WHY Hi-C не скачивается: файл 2.1 ГБ (а в ENCODE версии того же эксперимента — 78-235 ГБ),
интересующие регионы — мегабазы. Читается по HTTP range через `shared_utils/remote_hdf5.py`.
Канонический для этого `hic-straw` НЕ собирается на Windows (провал сборки wheel).

Запуск:
    python download_data.py
"""

from __future__ import annotations

import hashlib
import json
import tarfile
import time
from pathlib import Path

import requests

DATA = Path(__file__).parent / "data"

HIC_URL = (
    "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/"
    "077a1498-e1ad-429a-b976-8f71625ebdb6/4DNFINPH7UOD.mcool"
)
GTEX_TAR = (
    "https://storage.googleapis.com/adult-gtex/bulk-qtl/v8/"
    "single-tissue-cis-qtl/GTEx_Analysis_v8_eQTL.tar"
)
GTEX_MEMBER = (
    "GTEx_Analysis_v8_eQTL/Cells_EBV-transformed_lymphocytes.v8.signif_variant_gene_pairs.txt.gz"
)
DIRECT = {
    "gencode.v26.GRCh38.genes.gtf": (
        "https://storage.googleapis.com/adult-gtex/references/v8/"
        "reference-tables/gencode.v26.GRCh38.genes.gtf"
    ),
    "GRCh38-cCREs.bed": "https://downloads.wenglab.org/Registry-V4/GRCh38-cCREs.bed",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(2**20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"  уже есть: {dest.name} ({dest.stat().st_size / 1e6:.1f} МБ)")
        return
    t = time.time()
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in r.iter_content(2**20):
                fh.write(chunk)
    print(f"  скачано: {dest.name} {dest.stat().st_size / 1e6:.1f} МБ за {time.time() - t:.0f}s")


def fetch_gtex_member(dest: Path) -> None:
    """
    WHY именно так: архив 1.56 ГБ содержит 98 тканей, нужна одна. Архив НЕ сжат,
    поэтому tarfile умеет seek между членами поверх seekable file-like -- скачивается
    только нужный член плюс заголовки, а не весь архив.
    """
    if dest.exists():
        print(f"  уже есть: {dest.name} ({dest.stat().st_size / 1e6:.1f} МБ)")
        return
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared_utils"))
    from remote_hdf5 import HTTPRangeFile

    t = time.time()
    f = HTTPRangeFile(GTEX_TAR, block_size=2**20)
    with tarfile.open(fileobj=f, mode="r:") as tf:
        src = tf.extractfile(tf.getmember(GTEX_MEMBER))
        dest.write_bytes(src.read())
    print(
        f"  извлечено: {dest.name} {dest.stat().st_size / 1e6:.1f} МБ "
        f"(из архива скачано {f.bytes_fetched / 1e6:.0f} МБ, не 1563) за {time.time() - t:.0f}s"
    )


def main() -> None:
    DATA.mkdir(exist_ok=True)
    print("=" * 68)
    print("T1 — загрузка данных D1. Источники публичные, ключи не нужны.")
    print("=" * 68)

    for name, url in DIRECT.items():
        fetch(url, DATA / name)
    fetch_gtex_member(DATA / "LCL.v8.signif_variant_gene_pairs.txt.gz")

    manifest = {
        "hic_remote_url": HIC_URL,
        "hic_note": "не скачивается -- читается по HTTP range (remote_hdf5.py)",
        "gtex_tissue": "Cells_EBV-transformed_lymphocytes (LCL) -- соответствует GM12878",
        "files": {
            p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)}
            for p in sorted(DATA.glob("*"))
            if p.is_file() and p.suffix != ".json"
        },
    }
    (DATA / "download_checksums.json").write_text(json.dumps(manifest, indent=2))
    print("-" * 68)
    for n, v in manifest["files"].items():
        print(f"  {n:44s} {v['bytes'] / 1e6:8.1f} МБ  {v['sha256'][:16]}…")
    print(f"saved: {DATA / 'download_checksums.json'}")


if __name__ == "__main__":
    main()
