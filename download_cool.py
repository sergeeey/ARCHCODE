import os
import requests
from tqdm import tqdm

# --- КОНФИГУРАЦИЯ (ФОРМАТ .mcool) ---
# Мы берем файл Rao 2014 (GM12878) - самый качественный датасет.
# Ссылка ведет на репозиторий 4DN.

# Попробуем несколько вариантов URL для Rao 2014 GM12878
TARGET_URL = "https://data.4dnucleome.org/files-processed/4DNFI1UEG1O1/@@download/4DNFI1UEG1O1.mcool"

# Альтернативные URL для попытки
ALTERNATIVE_URLS = [
    "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/4d9136c8-54b1-4eb7-a536-231a5477dc76/4DNFI1UEG1O1.mcool",
]

TARGET_FOLDER = "data/real_hic/WT"

TARGET_FILENAME = "Rao2014_GM12878.mcool"


def download_file(url, folder, filename, alternative_urls=None):
    filepath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    
    print(f"🚀 Начинаю загрузку: {filename}")
    print(f"📂 Папка: {folder}")
    
    urls_to_try = [url]
    if alternative_urls:
        urls_to_try.extend(alternative_urls)
    
    for attempt, current_url in enumerate(urls_to_try, 1):
        try:
            print(f"\nПопытка {attempt}/{len(urls_to_try)}: {current_url[:80]}...")
            response = requests.get(current_url, stream=True, timeout=30)
            response.raise_for_status() # Проверка на ошибки сети
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024 # 1 MB
            
            # Проверка, если файл уже есть
            if os.path.exists(filepath):
                if total_size > 0 and os.path.getsize(filepath) == total_size:
                    print(f"✅ Файл уже скачан: {filepath}")
                    return filepath
                else:
                    print(f"⚠️ Файл неполный или поврежден. Перезаписываю...")

            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
            
            with open(filepath, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
                    
            progress_bar.close()
            print("✅ Загрузка завершена успешно.")
            return filepath
            
        except Exception as e:
            print(f"❌ Ошибка с URL {attempt}: {e}")
            if attempt < len(urls_to_try):
                print(f"Пробую следующий URL...")
                continue
            else:
                print(f"\n❌ Все URL не сработали. Попробуйте ручную загрузку.")
                print(f"Рекомендуется скачать файл вручную с https://data.4dnucleome.org/")
                return None
    
    return None


if __name__ == "__main__":
    print("=== ARCHCODE DATA DOWNLOADER (COOLER EDITION) ===")
    download_file(TARGET_URL, TARGET_FOLDER, TARGET_FILENAME, alternative_urls=ALTERNATIVE_URLS)
