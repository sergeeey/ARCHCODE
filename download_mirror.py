import os
import requests
from tqdm import tqdm

# Список зеркал (Mirrors) от наиболее вероятного к запасному
MIRRORS = [
    # Mirror 1: Репозиторий автора Higlass/Cooler (Peter Kerpedjiev)
    "https://s3.amazonaws.com/pkerp/public/coolers/Rao2014-GM12878-MboI-allreps-filtered.1000kb.cool",
    
    # Mirror 2: Github Raw (используется в туториалах Open2C)
    "https://github.com/open2c/cooler-binder/raw/master/data/Rao2014-GM12878-MboI-allreps-filtered.1000kb.cool",
    
    # Mirror 3: Внешний тестовый бакет
    "https://raw.githubusercontent.com/mirnylab/cooler-binder/master/data/Rao2014-GM12878-MboI-allreps-filtered.1000kb.cool"
]

TARGET_FOLDER = "data/real_hic/WT"
TARGET_FILENAME = "Rao2014_GM12878_1000kb.cool"


def download_with_mirrors():
    filepath = os.path.join(TARGET_FOLDER, TARGET_FILENAME)
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    
    print(f"🎯 Цель: {TARGET_FILENAME}")
    
    for i, url in enumerate(MIRRORS):
        print(f"\n🔄 Попытка {i+1}/{len(MIRRORS)}: {url}")
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                print("✅ Связь установлена! Начало загрузки...")
                total_size = int(response.headers.get('content-length', 0))
                
                with open(filepath, 'wb') as file, tqdm(
                    total=total_size, unit='iB', unit_scale=True
                ) as progress_bar:
                    for data in response.iter_content(1024 * 1024):
                        progress_bar.update(len(data))
                        file.write(data)
                
                print(f"\n🎉 УСПЕХ! Файл сохранен: {filepath}")
                return filepath # Выход при успехе
            else:
                print(f"❌ Ошибка сервера: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка соединения: {e}")
            
    print("\n💀 Все зеркала недоступны. Это проблема сети или глобальный сбой S3.")


if __name__ == "__main__":
    download_with_mirrors()


