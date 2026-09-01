"""
Чтение удалённого HDF5 (.mcool) по HTTP range-запросам, без скачивания файла целиком.

WHY он вообще существует: канонический инструмент для выборки региона из Hi-C --
`hic-straw` -- НЕ собирается на Windows (провал сборки wheel, тот же класс, что pysam).
`fsspec` открывает те же URL с FileNotFoundError, хотя прямой range-запрос к ним
возвращает 206 и валидную сигнатуру HDF5. Поэтому минимальная своя реализация:
~40 строк, никакой компиляции, поведение под контролем.

Файлы Hi-C для GM12878 в ENCODE весят 78-235 ГБ; интересующий регион -- 2 Мб.
Скачивать 80 ГБ ради 200x200 матрицы нельзя, поэтому чтение по кускам обязательно.
"""

from __future__ import annotations

import io
import time

import requests


class ShortRangeResponse(Exception):
    """Сервер вернул меньше байт, чем запрошено, но без HTTP-ошибки."""


DEFAULT_BLOCK = 2**22  # 4 МБ -- компромисс между числом запросов и лишним трафиком


class HTTPRangeFile(io.RawIOBase):
    """Минимальный seekable file-like поверх HTTP range-запросов с блочным кэшем."""

    def __init__(self, url: str, block_size: int = DEFAULT_BLOCK, timeout: int = 60):
        self.url, self.block_size, self.timeout = url, block_size, timeout
        self._pos = 0
        self._cache: dict[int, bytes] = {}
        self.session = requests.Session()
        head = self.session.head(url, timeout=timeout, allow_redirects=True)
        head.raise_for_status()
        if head.headers.get("Accept-Ranges") != "bytes":
            raise OSError(f"сервер не поддерживает range-запросы: {url}")
        self.size = int(head.headers["Content-Length"])
        self.bytes_fetched = 0  # для честного отчёта, сколько реально скачано

    def _block(self, idx: int, retries: int = 5) -> bytes:
        """
        WHY ретраи добавлены 2026-09-01: длинная сборка (GTEx v10, ~12 тыс. вариантов,
        десятки тысяч range-запросов) упала на `RemoteDisconnected` после ~5 минут —
        сервер 4DN закрывает keep-alive-соединение. Это отказ ТРАНСПОРТА, а не результат:
        по FL Substrate Gate такой обрыв не является свидетельством против гипотезы,
        поэтому его чинят, а не записывают. Пересоздаём сессию — переиспользование
        мёртвого пула соединений даёт ту же ошибку немедленно.

        WHY ChunkedEncodingError отдельно: это НЕ подкласс ConnectionError. requests
        поднимает его, когда тело обрывается на середине, тогда как ConnectionError —
        когда соединение умирает до/на заголовках. Обрыв keep-alive даёт то или другое
        в зависимости от момента, поэтому ловить надо оба, иначе ретрай покрывает
        половину случаев.

        WHY проверка длины: сервер (или прокси) может вернуть КОРОТКИЙ, но
        самосогласованный ответ — со своим Content-Length под усечённый диапазон.
        Тогда raise_for_status() молчит, и в кэш HDF5-потока лягут неверные байты.
        Это единственный путь в этом классе, дающий тихо НЕПРАВИЛЬНЫЕ данные,
        а не отсутствующие, поэтому проверяется явно.
        """
        if idx not in self._cache:
            start = idx * self.block_size
            end = min(start + self.block_size, self.size) - 1
            want = end - start + 1
            for attempt in range(retries):
                try:
                    r = self.session.get(
                        self.url, headers={"Range": f"bytes={start}-{end}"}, timeout=self.timeout
                    )
                    r.raise_for_status()
                    if len(r.content) != want:
                        raise ShortRangeResponse(
                            f"короткий range-ответ: запрошено {want} байт "
                            f"({start}-{end}), получено {len(r.content)}"
                        )
                    break
                except (
                    requests.ConnectionError,
                    requests.Timeout,
                    requests.exceptions.ChunkedEncodingError,
                    ShortRangeResponse,
                ):
                    if attempt == retries - 1:
                        raise
                    time.sleep(2**attempt)
                    self.session = requests.Session()
            self._cache[idx] = r.content
            self.bytes_fetched += len(r.content)
        return self._cache[idx]

    def read(self, n: int = -1) -> bytes:
        if n < 0 or self._pos + n > self.size:
            n = self.size - self._pos
        out, pos, left = bytearray(), self._pos, n
        while left > 0:
            idx, off = divmod(pos, self.block_size)
            chunk = self._block(idx)[off : off + left]
            if not chunk:
                break
            out += chunk
            pos += len(chunk)
            left -= len(chunk)
        self._pos = pos
        return bytes(out)

    def readinto(self, b) -> int:
        data = self.read(len(b))
        b[: len(data)] = data
        return len(data)

    def seek(self, offset: int, whence: int = 0) -> int:
        base = {0: 0, 1: self._pos, 2: self.size}[whence]
        self._pos = max(0, min(base + offset, self.size))
        return self._pos

    def tell(self) -> int:
        return self._pos

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True
