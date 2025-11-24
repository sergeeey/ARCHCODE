"""Конвертация .hic файла в .cool формат.

Использует hic2cool для конвертации WAPL_KO_HAP1.hic в WAPL_KO_HAP1_10kb.cool
"""

import sys
from pathlib import Path

try:
    import hic2cool
except ImportError:
    print("❌ Ошибка: hic2cool не установлен!")
    print("   Установите: pip install hic2cool")
    sys.exit(1)


BASE_DIR = Path(r"D:\ДНК КУРСОР")
DATA_DIR = BASE_DIR / "data" / "real"

INPUT_FILE = DATA_DIR / "WAPL_KO_HAP1.hic"
OUTPUT_FILE = DATA_DIR / "WAPL_KO_HAP1_10kb.cool"
RESOLUTION = 10000  # 10kb


def main():
    """Конвертация .hic в .cool."""
    print("=== Конвертация .hic → .cool ===")
    print(f"Входной файл: {INPUT_FILE}")
    print(f"Выходной файл: {OUTPUT_FILE}")
    print(f"Разрешение: {RESOLUTION} bp")
    print()

    # Проверка входного файла
    if not INPUT_FILE.exists():
        print(f"❌ Ошибка: файл {INPUT_FILE} не найден!")
        print("   Сначала загрузите файл через download_hic_datasets.py")
        sys.exit(1)

    input_size = INPUT_FILE.stat().st_size / (1024 ** 3)  # GB
    print(f"✅ Входной файл найден: {input_size:.2f} GB")
    print()

    # Проверка выходного файла
    if OUTPUT_FILE.exists():
        print(f"⚠️  Выходной файл уже существует: {OUTPUT_FILE}")
        response = input("Перезаписать? (y/n): ")
        if response.lower() != "y":
            print("Отменено.")
            return
        OUTPUT_FILE.unlink()

    # Конвертация
    print("🔄 Начинаю конвертацию...")
    print("   (это может занять 10-30 минут в зависимости от размера файла)")
    print()

    try:
        hic2cool.convert(
            str(INPUT_FILE),
            str(OUTPUT_FILE),
            RESOLUTION,
        )
        print()
        print("✅ Конвертация завершена успешно!")

        output_size = OUTPUT_FILE.stat().st_size / (1024 ** 3)  # GB
        print(f"📁 Выходной файл: {OUTPUT_FILE}")
        print(f"📊 Размер: {output_size:.2f} GB")

    except Exception as e:
        print()
        print(f"❌ Ошибка при конвертации: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()



