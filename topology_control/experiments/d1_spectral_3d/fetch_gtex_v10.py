"""
Извлечение ткани LCL из GTEx v10 потоковым чтением.

WHY потоком: файл GTEx_Analysis_v10_eQTL.tar на деле GZIP (сигнатура \x1f\x8b),
несмотря на расширение. Gzip не поддерживает seek, поэтому приём с range-запросами,
работавший для v8 (там честный несжатый tar), здесь неприменим. Читаем поток и
останавливаемся, как только нужный член извлечён -- качать все 2.56 ГБ незачем.
"""

from __future__ import annotations

import tarfile
import time
from pathlib import Path

import requests

URL = ("https://storage.googleapis.com/adult-gtex/bulk-qtl/v10/"
       "single-tissue-cis-qtl/GTEx_Analysis_v10_eQTL.tar")
WANT = "lymphocyte"  # Cells_EBV-transformed_lymphocytes == LCL == GM12878
DEST = Path(__file__).parent / "data"

t0 = time.time()
print(f"поток открыт: {URL.split('/')[-1]}", flush=True)
with requests.get(URL, stream=True, timeout=300) as r:
    r.raise_for_status()
    with tarfile.open(fileobj=r.raw, mode="r|gz") as tf:
        n, saved = 0, []
        for m in tf:
            n += 1
            if n % 20 == 0:
                print(f"  просмотрено членов: {n}  ({time.time()-t0:.0f}s)", flush=True)
            if WANT in m.name.lower() and "signif" in m.name.lower():
                out = DEST / f"LCL.v10.{Path(m.name).name}"
                out.write_bytes(tf.extractfile(m).read())
                saved.append(out)
                print(f"  ИЗВЛЕЧЕНО: {out.name}  {out.stat().st_size/1e6:.1f} МБ", flush=True)
                break
print(f"\nчленов просмотрено: {n} · время {time.time()-t0:.0f}s", flush=True)
print("сохранено:", [p.name for p in saved] or "НИЧЕГО НЕ НАЙДЕНО", flush=True)
