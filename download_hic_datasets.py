"""ARCHCODE Hi-C Datasets Downloader.

Автоматическая загрузка эталонных Hi-C датасетов с поддержкой докачки и прогресс-бара.
"""

import os
import sys
import math
import requests
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # если нет tqdm, будет просто без прогресса


# === 1. НАСТРОЙКИ ПОД ТЕБЯ ======================================

# Корневая папка проекта
BASE_DIR = Path(r"D:\ДНК КУРСОР")
DATA_DIR = BASE_DIR / "data" / "real"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Прямые рабочие ссылки на эталонные Hi-C датасеты
# Проверены и работают без авторизации
DATASETS = [
    {
        "name": "WT_GM12878.mcool",
        # Пробуем альтернативные URL (S3 может работать лучше)
        "urls": [
            "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/4d9136c8-54b1-4eb7-a536-231a5477dc76/4DNFI1UEG1O1.mcool",
            "https://data.4dnucleome.org/files-processed/4DNFI1UEG1O1/@@download/4DNFI1UEG1O1.mcool",
        ],
        "path": DATA_DIR / "WT_GM12878.mcool",
        "description": "WT (GM12878) - Rao et al., 2014",
    },
    {
        "name": "CdLS_Like_HCT116.mcool",
        # Пробуем альтернативные URL
        "urls": [
            "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/06a0431d-2446-4fcb-8d8e-d2ae691d786b/4DNFI2TK7L2F.mcool",
            "https://data.4dnucleome.org/files-processed/4DNFI9GMP2J8/@@download/4DNFI9GMP2J8.mcool",
        ],
        "path": DATA_DIR / "CdLS_Like_HCT116.mcool",
        "description": "CdLS-like (HCT116 RAD21-AID auxin) - Rao et al., 2017",
    },
    {
        "name": "WAPL_KO_HAP1.hic",
        # Пробуем альтернативные URL
        "urls": [
            "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM2496nnn/GSM2496645/suppl/GSM2496645_HAP1_WAPL_KO_inter_30.hic",
            "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM2496nnn/GSM2496645/suppl/GSM2496645_HAP1_WAPL-KO.hic",
        ],
        "path": DATA_DIR / "WAPL_KO_HAP1.hic",
        "description": "WAPL-KO (HAP1) - Haarhuis et al., 2017",
    },
    # GSE185608: sci-Hi-C на мышиных ESC (для RS-12: bookmarking/mitosis)
    {
        "name": "GSE185608_4DNFIZ8TEE2M.tar.gz",
        "url": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE185nnn/GSE185608/suppl/GSE185608_4DNFIZ8TEE2M.tar.gz",
        "path": DATA_DIR / "GSE185608_4DNFIZ8TEE2M.tar.gz",
        "description": "sci-Hi-C processed data (ESC differentiation, X-inactivation) - GSE185608",
    },
    {
        "name": "GSE185608_4DNFI7QQWLOV.txt.gz",
        "url": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE185nnn/GSE185608/suppl/GSE185608_4DNFI7QQWLOV.txt.gz",
        "path": DATA_DIR / "GSE185608_4DNFI7QQWLOV.txt.gz",
        "description": "GSE185608 supplementary file 1",
    },
    {
        "name": "GSE185608_4DNFICOPS6ER.txt.gz",
        "url": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE185nnn/GSE185608/suppl/GSE185608_4DNFICOPS6ER.txt.gz",
        "path": DATA_DIR / "GSE185608_4DNFICOPS6ER.txt.gz",
        "description": "GSE185608 supplementary file 2",
    },
]


# === 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =================================

def format_size(num_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид."""
    if num_bytes is None:
        return "UNKNOWN"
    if num_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(num_bytes, 1024)))
    value = num_bytes / (1024 ** i)
    return f"{value:.2f} {units[i]}"


def download_with_resume(url: str, target_path: Path, chunk_size: int = 1024 * 1024):
    """
    Скачивание файла с поддержкой докачки (HTTP Range).

    Если файл уже частично существует — продолжает, а не перезатирает.
    """

    # Сколько уже скачано
    existing_size = target_path.stat().st_size if target_path.exists() else 0

    # Пытаемся узнать общий размер
    headers = {}
    if existing_size > 0:
        headers["Range"] = f"bytes={existing_size}-"

    # HEAD-запрос для размера (если сервер разрешает)
    # Используем заголовки браузера
    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
    }
    
    total_size = None
    try:
        head = requests.head(url, allow_redirects=True, timeout=15, headers=browser_headers)
        if "Content-Length" in head.headers:
            total_size = int(head.headers["Content-Length"])
            if "Content-Range" in head.headers:
                # иногда размер в Content-Range
                # формата "bytes start-end/total"
                try:
                    total_size = int(head.headers["Content-Range"].split("/")[-1])
                except Exception:
                    pass
    except Exception:
        # Если HEAD не работает, попробуем GET для получения размера
        try:
            get_head = requests.get(url, stream=True, headers=browser_headers, timeout=15, allow_redirects=True)
            if "Content-Length" in get_head.headers:
                total_size = int(get_head.headers["Content-Length"])
            get_head.close()
        except Exception:
            pass

    if existing_size > 0:
        print(f"[{target_path.name}] Найден существующий файл: {format_size(existing_size)}")
        if total_size and existing_size >= total_size:
            print(f"[{target_path.name}] Уже полностью скачан, пропускаю.")
            return
        else:
            print(f"[{target_path.name}] Продолжаю докачку...")

    # Используем заголовки браузера для лучшей совместимости
    download_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    download_headers.update(headers)
    
    # Открываем поток на скачивание
    with requests.get(url, stream=True, headers=download_headers, timeout=60, allow_redirects=True) as r:
        r.raise_for_status()

        mode = "ab" if existing_size > 0 else "wb"
        download_size = None

        # Пытаемся получить длину именно этого запроса
        if "Content-Length" in r.headers:
            download_size = int(r.headers["Content-Length"])

        desc = f"Downloading {target_path.name}"
        if tqdm is not None:
            pbar = tqdm(
                total=download_size,
                unit="B",
                unit_scale=True,
                desc=desc,
                initial=0,
                leave=True,
            )
        else:
            pbar = None
            print(desc)

        with open(target_path, mode) as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                f.write(chunk)
                if pbar is not None:
                    pbar.update(len(chunk))

        if pbar is not None:
            pbar.close()

    final_size = target_path.stat().st_size
    print(f"[{target_path.name}] Готово, размер файла: {format_size(final_size)}")
    if total_size is not None:
        if final_size == total_size:
            print(f"[{target_path.name}] Размер совпадает с ожидаемым.")
        else:
            print(
                f"[{target_path.name}] ВНИМАНИЕ: ожидаемый размер {format_size(total_size)}, "
                f"получено {format_size(final_size)}"
            )


# === 3. ОСНОВНОЙ ЗАПУСК =========================================

def main():
    """Основная функция загрузки."""
    print("=== ARCHCODE Hi-C downloader ===")
    print(f"Целевая папка: {DATA_DIR}")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for ds in DATASETS:
        name = ds["name"]
        path = ds["path"]
        
        # Поддержка как старого формата (один URL), так и нового (список URLs)
        if "urls" in ds:
            urls = ds["urls"]
        elif "url" in ds:
            urls = [ds["url"]]
        else:
            print(f"[{name}] URL не указан. Пропускаю этот датасет.")
            continue

        print("\n-------------------------------------")
        print(f"Обработка датасета: {name}")
        if "description" in ds:
            print(f"Описание: {ds['description']}")
        print(f"Файл: {path}")

        # Пробуем каждый URL по очереди
        success = False
        for idx, url in enumerate(urls, 1):
            print(f"\nПопытка {idx}/{len(urls)}: {url[:80]}...")
            try:
                download_with_resume(url, path)
                success = True
                break  # Успешно скачали, переходим к следующему датасету
            except KeyboardInterrupt:
                print(f"\nЗагрузка {name} прервана пользователем.")
                sys.exit(1)
            except Exception as e:
                print(f"[{name}] Ошибка с URL {idx}: {e}")
                if idx < len(urls):
                    print(f"[{name}] Пробую следующий URL...")
                else:
                    print(f"[{name}] Все URL не сработали. Попробуйте ручную загрузку.")
        
        if not success:
            print(f"[{name}] ⚠️  Не удалось скачать. Используйте ручную загрузку (см. ИНСТРУКЦИЯ_ЗАГРУЗКА_ДАННЫХ.md)")

    print("\n=== Все задачи завершены ===")


if __name__ == "__main__":
    main()

