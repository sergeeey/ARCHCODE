"""Распаковка и подготовка sci-Hi-C данных из GSE185608.

Распаковывает архив GSE185608_4DNFIZ8TEE2M.tar.gz и подготавливает данные
для анализа в RS-12 (single-cell contact decay vs processivity/bookmarking).
"""

import tarfile
import gzip
import shutil
from pathlib import Path

BASE_DIR = Path(r"D:\ДНК КУРСОР")
DATA_DIR = BASE_DIR / "data" / "real"
EXTRACT_DIR = DATA_DIR / "GSE185608_sciHiC"

# Файлы для распаковки
ARCHIVE_FILE = DATA_DIR / "GSE185608_4DNFIZ8TEE2M.tar.gz"
SUPP_FILES = [
    DATA_DIR / "GSE185608_4DNFI7QQWLOV.txt.gz",
    DATA_DIR / "GSE185608_4DNFICOPS6ER.txt.gz",
]


def extract_tar_gz(tar_path: Path, extract_to: Path):
    """Распаковывает .tar.gz архив."""
    print(f"📦 Распаковка архива: {tar_path.name}")
    print(f"   → {extract_to}")
    
    if not tar_path.exists():
        print(f"❌ Ошибка: файл {tar_path} не найден!")
        return False
    
    extract_to.mkdir(parents=True, exist_ok=True)
    
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_to)
        
        print(f"✅ Архив распакован успешно!")
        
        # Показываем содержимое
        files = list(extract_to.rglob("*"))
        print(f"\n📁 Содержимое архива ({len(files)} файлов/папок):")
        for item in sorted(files)[:20]:  # Показываем первые 20
            rel_path = item.relative_to(extract_to)
            if item.is_file():
                size_mb = item.stat().st_size / (1024 ** 2)
                print(f"   📄 {rel_path} ({size_mb:.2f} MB)")
            else:
                print(f"   📁 {rel_path}/")
        
        if len(files) > 20:
            print(f"   ... и еще {len(files) - 20} элементов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при распаковке: {e}")
        return False


def extract_gz(gz_path: Path, extract_to: Path):
    """Распаковывает .gz файл."""
    if not gz_path.exists():
        print(f"⚠️  Файл {gz_path.name} не найден, пропускаю")
        return False
    
    output_path = extract_to / gz_path.stem  # Убираем .gz
    
    print(f"📦 Распаковка: {gz_path.name}")
    print(f"   → {output_path.name}")
    
    try:
        with gzip.open(gz_path, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        size_mb = output_path.stat().st_size / (1024 ** 2)
        print(f"✅ Распакован ({size_mb:.2f} MB)")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при распаковке {gz_path.name}: {e}")
        return False


def analyze_structure(extract_dir: Path):
    """Анализирует структуру распакованных данных."""
    print("\n" + "=" * 60)
    print("📊 Анализ структуры данных")
    print("=" * 60)
    
    # Ищем файлы по типам
    cool_files = list(extract_dir.rglob("*.cool"))
    mcool_files = list(extract_dir.rglob("*.mcool"))
    txt_files = list(extract_dir.rglob("*.txt"))
    hdf5_files = list(extract_dir.rglob("*.h5*"))
    tsv_files = list(extract_dir.rglob("*.tsv"))
    
    print(f"\nНайдено файлов:")
    print(f"  .cool: {len(cool_files)}")
    print(f"  .mcool: {len(mcool_files)}")
    print(f"  .txt: {len(txt_files)}")
    print(f"  .h5/.hdf5: {len(hdf5_files)}")
    print(f"  .tsv: {len(tsv_files)}")
    
    # Ищем папки по состояниям/дням
    dirs = [d for d in extract_dir.rglob("*") if d.is_dir()]
    print(f"\nПапок: {len(dirs)}")
    
    # Ищем паттерны в названиях (дни дифференцировки, состояния)
    day_patterns = ["day", "d0", "d7", "d20", "day0", "day7", "day20"]
    state_patterns = ["esc", "differentiated", "x_inactive", "x_active"]
    
    found_patterns = []
    for item in extract_dir.rglob("*"):
        name_lower = item.name.lower()
        for pattern in day_patterns + state_patterns:
            if pattern in name_lower and pattern not in found_patterns:
                found_patterns.append(pattern)
    
    if found_patterns:
        print(f"\n🔍 Обнаружены паттерны в названиях:")
        for pattern in found_patterns:
            print(f"   - {pattern}")
    
    return {
        "cool_files": cool_files,
        "mcool_files": mcool_files,
        "txt_files": txt_files,
        "hdf5_files": hdf5_files,
        "tsv_files": tsv_files,
        "dirs": dirs,
    }


def main():
    """Основная функция распаковки."""
    print("=" * 60)
    print("🔓 Распаковка sci-Hi-C данных (GSE185608)")
    print("=" * 60)
    print()
    
    # Проверка наличия архива
    if not ARCHIVE_FILE.exists():
        print(f"❌ Ошибка: архив {ARCHIVE_FILE.name} не найден!")
        print(f"   Сначала загрузите файлы через download_hic_datasets.py")
        return
    
    # Распаковка основного архива
    success = extract_tar_gz(ARCHIVE_FILE, EXTRACT_DIR)
    
    if not success:
        print("\n❌ Не удалось распаковать основной архив")
        return
    
    # Распаковка дополнительных файлов
    print("\n" + "-" * 60)
    print("📦 Распаковка дополнительных файлов")
    print("-" * 60)
    
    for supp_file in SUPP_FILES:
        extract_gz(supp_file, EXTRACT_DIR)
    
    # Анализ структуры
    structure = analyze_structure(EXTRACT_DIR)
    
    print("\n" + "=" * 60)
    print("✅ Распаковка завершена!")
    print("=" * 60)
    print(f"\n📁 Данные находятся в: {EXTRACT_DIR}")
    print("\n💡 Следующие шаги:")
    print("   1. Изучите структуру данных выше")
    print("   2. Запустите RS-12 анализ:")
    print("      python experiments/run_RS12_sci_hic_benchmark.py")


if __name__ == "__main__":
    main()




