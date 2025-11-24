import os
import requests
from tqdm import tqdm

# --- НОВАЯ ЦЕЛЬ (STABLE S3 BUCKET) ---
# Это официальный бакет примеров от разработчиков cooler.
# Файл: Rao 2014, GM12878, разрешение 1000kb.

# Попробуем несколько вариантов URL
TARGET_URL = "https://s3.amazonaws.com/cool-examples/Rao2014-GM12878-MboI-allreps-filtered.1000kb.cool"

# Альтернативные варианты (на случай если имя файла отличается)
ALTERNATIVE_URLS = [
    "https://s3.amazonaws.com/cool-examples/Rao2014-GM12878-MboI-allreps-filtered.1000kb.cool",
    "https://s3.amazonaws.com/cool-examples/rao2014-gm12878-mboi-allreps-filtered.1000kb.cool",  # lowercase
    "https://cooler.readthedocs.io/en/latest/examples/Rao2014-GM12878-MboI-allreps-filtered.1000kb.cool",
]

TARGET_FOLDER = "data/real_hic/WT"

TARGET_FILENAME = "Rao2014_GM12878_1000kb.cool"


def download_file(url, folder, filename, alternative_urls=None):
    filepath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    
    print(f"🚀 Начинаю загрузку: {filename}")
    print(f"🔗 Источник: Stable Open2C S3 Bucket")
    print(f"📂 Папка: {folder}")
    
    urls_to_try = [url]
    if alternative_urls:
        urls_to_try.extend(alternative_urls)
    
    for attempt, current_url in enumerate(urls_to_try, 1):
        try:
            print(f"\nПопытка {attempt}/{len(urls_to_try)}: {current_url[:80]}...")
            response = requests.get(current_url, stream=True, timeout=30)
            response.raise_for_status() 
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024 # 1 MB
        
        if os.path.exists(filepath):
            if total_size > 0 and os.path.getsize(filepath) == total_size:
                print(f"✅ Файл уже скачан и проверен по размеру: {filepath}")
                return filepath
            else:
                print(f"⚠️ Файл существует, но размер отличается. Перезаписываю...")

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
                print(f"\n❌ Все URL не сработали.")
                print(f"💡 Рекомендация: Проверьте документацию cooler или используйте ручную загрузку.")
                return None
    
    return None


if __name__ == "__main__":
    download_file(TARGET_URL, TARGET_FOLDER, TARGET_FILENAME, alternative_urls=ALTERNATIVE_URLS)

