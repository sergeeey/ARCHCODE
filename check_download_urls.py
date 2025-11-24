"""Проверка доступности URL для загрузки датасетов.

Выполняет HEAD-запросы к каждому URL и проверяет их доступность.
"""

import requests
from pathlib import Path

# Те же URL, что и в download_hic_datasets.py
DATASETS = [
    {
        "name": "WT_GM12878.mcool",
        "url": "https://data.4dnucleome.org/files-processed/4DNFI1UEG1O1/@@download/4DNFI1UEG1O1.mcool",
        "description": "WT (GM12878) - Rao et al., 2014",
    },
    {
        "name": "CdLS_Like_HCT116.mcool",
        "url": "https://data.4dnucleome.org/files-processed/4DNFI9GMP2J8/@@download/4DNFI9GMP2J8.mcool",
        "description": "CdLS-like (HCT116 RAD21-AID auxin) - Rao et al., 2017",
    },
    {
        "name": "WAPL_KO_HAP1.hic",
        "url": "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM2496nnn/GSM2496645/suppl/GSM2496645_HAP1_WAPL-KO.hic",
        "description": "WAPL-KO (HAP1) - Haarhuis et al., 2017",
    },
]


def check_url(url: str, timeout: int = 15) -> tuple[bool, str, int | None]:
    """
    Проверяет доступность URL.

    Returns:
        (is_available, status_message, content_length)
    """
    # Используем правильные заголовки для имитации браузера
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
    }
    
    try:
        # Сначала пробуем HEAD
        try:
            response = requests.head(url, allow_redirects=True, timeout=timeout, headers=headers)
            if response.status_code == 200:
                content_length = response.headers.get("Content-Length")
                size = int(content_length) if content_length else None
                return True, f"✅ Доступен (HTTP {response.status_code})", size
        except Exception:
            pass
        
        # Если HEAD не работает, пробуем GET с ограничением размера
        try:
            get_response = requests.get(
                url, 
                stream=True, 
                timeout=timeout, 
                headers=headers,
                allow_redirects=True
            )
            
            # Проверяем статус
            if get_response.status_code == 200:
                content_length = get_response.headers.get("Content-Length")
                size = int(content_length) if content_length else None
                # Закрываем соединение, так как мы только проверяем
                get_response.close()
                return True, f"✅ Доступен (HTTP {get_response.status_code}, GET)", size
            elif get_response.status_code in [301, 302, 303, 307, 308]:
                location = get_response.headers.get("Location")
                return False, f"⚠️  Редирект (HTTP {get_response.status_code}) → {location}", None
            else:
                get_response.close()
                return False, f"❌ HTTP {get_response.status_code}", None
        except requests.exceptions.Timeout:
            return False, "❌ Таймаут при GET", None
        except requests.exceptions.ConnectionError:
            return False, "❌ Ошибка подключения", None
        except Exception as e:
            return False, f"❌ Ошибка GET: {e}", None
            
    except requests.exceptions.Timeout:
        return False, "❌ Таймаут", None
    except requests.exceptions.ConnectionError:
        return False, "❌ Ошибка подключения", None
    except Exception as e:
        return False, f"❌ Ошибка: {e}", None


def format_size(bytes: int | None) -> str:
    """Форматирует размер в читаемый вид."""
    if bytes is None:
        return "неизвестен"
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 ** 2:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 ** 3:
        return f"{bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes / (1024 ** 3):.2f} GB"


def main():
    """Проверяет все URL."""
    print("=" * 70)
    print("🔍 Проверка доступности URL для загрузки датасетов")
    print("=" * 70)
    print()

    all_available = True

    for i, ds in enumerate(DATASETS, 1):
        name = ds["name"]
        url = ds["url"]
        description = ds.get("description", "")

        print(f"[{i}/{len(DATASETS)}] {name}")
        if description:
            print(f"     {description}")
        print(f"     URL: {url}")
        print("     Проверка...", end=" ", flush=True)

        is_available, message, size = check_url(url)

        print(message)
        if size:
            print(f"     Размер: {format_size(size)}")
        
        if not is_available:
            all_available = False

        print()

    print("=" * 70)
    if all_available:
        print("✅ Все URL доступны! Можно запускать download_hic_datasets.py")
    else:
        print("⚠️  Некоторые URL недоступны. Проверьте ссылки.")
    print("=" * 70)


if __name__ == "__main__":
    main()

