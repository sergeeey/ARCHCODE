"""Полный пайплайн: загрузка → конвертация → бенчмарк.

Этот скрипт выполняет все шаги автоматически:
1. Скачивает все три датасета
2. Конвертирует WAPL.hic в WAPL_10kb.cool
3. Запускает RS-11 multi-condition бенчмарк
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(r"D:\ДНК КУРСОР")
DATA_DIR = BASE_DIR / "data" / "real"


def check_file_exists(filename: str, min_size_gb: float = 0.1) -> bool:
    """Проверяет существование файла и его минимальный размер."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return False
    size_gb = filepath.stat().st_size / (1024 ** 3)
    return size_gb >= min_size_gb


def run_step(step_name: str, script_path: Path, check_files: list[str] | None = None):
    """Запускает шаг пайплайна с проверкой результата."""
    print("\n" + "=" * 60)
    print(f"📋 ШАГ: {step_name}")
    print("=" * 60)

    if check_files:
        all_exist = all(check_file_exists(f) for f in check_files)
        if all_exist:
            print(f"✅ Файлы уже существуют: {', '.join(check_files)}")
            print("   Пропускаю этот шаг.")
            return True

    print(f"🚀 Запускаю: {script_path.name}")
    print()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            check=False,
        )

        if result.returncode == 0:
            print()
            print(f"✅ {step_name} завершён успешно!")
            return True
        else:
            print()
            print(f"❌ {step_name} завершился с ошибкой (код: {result.returncode})")
            return False

    except KeyboardInterrupt:
        print()
        print(f"⚠️  {step_name} прерван пользователем.")
        return False
    except Exception as e:
        print()
        print(f"❌ Ошибка при выполнении {step_name}: {e}")
        return False


def main():
    """Основная функция полного пайплайна."""
    print("=" * 60)
    print("🚀 ARCHCODE: Полный пайплайн загрузки и бенчмарка")
    print("=" * 60)
    print()

    # Проверка наличия скриптов
    download_script = BASE_DIR / "download_hic_datasets.py"
    convert_script = BASE_DIR / "convert_hic_to_cool.py"
    extract_sci_hic_script = BASE_DIR / "extract_sci_hic.py"
    benchmark_script = BASE_DIR / "experiments" / "run_RS11_multi_condition.py"
    rs12_benchmark_script = BASE_DIR / "experiments" / "run_RS12_sci_hic_benchmark.py"

    missing_scripts = []
    for script, name in [
        (download_script, "download_hic_datasets.py"),
        (convert_script, "convert_hic_to_cool.py"),
        (extract_sci_hic_script, "extract_sci_hic.py"),
        (benchmark_script, "experiments/run_RS11_multi_condition.py"),
    ]:
        if not script.exists():
            missing_scripts.append(name)

    if missing_scripts:
        print("❌ Ошибка: отсутствуют необходимые скрипты:")
        for script in missing_scripts:
            print(f"   - {script}")
        sys.exit(1)

    # Шаг 1: Загрузка датасетов
    success = run_step(
        "Загрузка Hi-C датасетов",
        download_script,
        check_files=["WT_GM12878.mcool", "CdLS_Like_HCT116.mcool", "WAPL_KO_HAP1.hic"],
    )

    if not success:
        print()
        print("⚠️  Загрузка не завершена. Проверьте URL в download_hic_datasets.py")
        response = input("Продолжить с конвертацией? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)

    # Шаг 2: Конвертация WAPL файла
    if check_file_exists("WAPL_KO_HAP1.hic", min_size_gb=0.1):
        success = run_step(
            "Конвертация WAPL.hic → WAPL_10kb.cool",
            convert_script,
            check_files=["WAPL_KO_HAP1_10kb.cool"],
        )

        if not success:
            print()
            print("⚠️  Конвертация не завершена.")
            response = input("Продолжить с бенчмарком? (y/n): ")
            if response.lower() != "y":
                sys.exit(1)
    else:
        print()
        print("⚠️  WAPL_KO_HAP1.hic не найден или слишком маленький.")
        print("   Пропускаю конвертацию.")

    # Шаг 2.5: Распаковка sci-Hi-C данных (GSE185608)
    if check_file_exists("GSE185608_4DNFIZ8TEE2M.tar.gz", min_size_gb=0.01):
        extract_dir = DATA_DIR / "GSE185608_sciHiC"
        success = run_step(
            "Распаковка sci-Hi-C данных (GSE185608)",
            extract_sci_hic_script,
            check_files=[],  # Проверка структуры будет внутри скрипта
        )
        
        if not success:
            print()
            print("⚠️  Распаковка sci-Hi-C данных не завершена.")
            print("   Можно продолжить с RS-11 бенчмарком.")
    else:
        print()
        print("ℹ️  GSE185608 архив не найден.")
        print("   RS-12 (sci-Hi-C) будет пропущен.")

    # Шаг 3: Запуск бенчмарка
    print()
    print("=" * 60)
    print("📊 ФИНАЛЬНЫЙ ШАГ: Запуск RS-11 бенчмарка")
    print("=" * 60)
    print()

    # Проверка наличия необходимых файлов
    required_files = [
        "WT_GM12878.mcool",
        "CdLS_Like_HCT116.mcool",
        "WAPL_KO_HAP1_10kb.cool",
    ]

    missing_files = []
    for filename in required_files:
        if not check_file_exists(filename, min_size_gb=0.1):
            missing_files.append(filename)

    if missing_files:
        print("❌ Ошибка: отсутствуют необходимые файлы для бенчмарка:")
        for filename in missing_files:
            print(f"   - {filename}")
        print()
        print("💡 Убедитесь, что:")
        print("   1. Все датасеты загружены (download_hic_datasets.py)")
        print("   2. WAPL файл сконвертирован (convert_hic_to_cool.py)")
        sys.exit(1)

    print("✅ Все необходимые файлы найдены!")
    print()

    # Запуск бенчмарка
    try:
        result = subprocess.run(
            [sys.executable, str(benchmark_script)],
            cwd=str(BASE_DIR),
            check=False,
        )

        if result.returncode == 0:
            print()
            print("=" * 60)
            print("🎉 ВСЕ ШАГИ ЗАВЕРШЕНЫ УСПЕШНО!")
            print("=" * 60)
            print()
            print("📊 Результаты сохранены в:")
            print("   - figures/RS11/Figure_4_*.png")
            print("   - data/output/RS11/RS11_multi_condition_results.json")
        else:
            print()
            print("❌ Бенчмарк завершился с ошибкой.")
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        print("⚠️  Бенчмарк прерван пользователем.")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Ошибка при запуске бенчмарка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

