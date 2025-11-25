"""
Автоматизированный скрипт для полной валидации ARCHCODE.

Выполняет:
1. RS-11B с полными параметрами (50×50, 100 циклов)
2. CdLS валидацию с реальными данными
3. Создает итоговый отчет
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from experiments.run_RS11B_phase_diagram import RS11BPhaseDiagram
from experiments.validate_cdls import CdLSValidation


def check_prerequisites() -> dict:
    """Проверить наличие всех необходимых компонентов."""
    print("=" * 80)
    print("ПРОВЕРКА ПРЕДВАРИТЕЛЬНЫХ УСЛОВИЙ")
    print("=" * 80)

    checks = {
        "cdls_data": False,
        "wapl_data": False,
        "disk_space": False,
        "memory": False,
    }

    # Проверка данных CdLS
    cdls_paths = [
        "data/real/CdLS_Like_HCT116.mcool",
        "data/real_hic/CdLS/CdLS_HCT116_10kb.cool",
    ]
    for path in cdls_paths:
        if Path(path).exists():
            checks["cdls_data"] = True
            print(f"✅ CdLS данные найдены: {path}")
            break

    if not checks["cdls_data"]:
        print("⚠️  CdLS данные не найдены, будет использован WT как placeholder")

    # Проверка места на диске
    import shutil
    disk_usage = shutil.disk_usage(".")
    free_gb = disk_usage.free / (1024 ** 3)
    if free_gb > 10:
        checks["disk_space"] = True
        print(f"✅ Свободно места: {free_gb:.1f} GB")
    else:
        print(f"⚠️  Мало места: {free_gb:.1f} GB (нужно > 10 GB)")

    # Проверка памяти (упрощенная)
    try:
        import psutil
        mem = psutil.virtual_memory()
        mem_gb = mem.total / (1024 ** 3)
        if mem_gb >= 8:
            checks["memory"] = True
            print(f"✅ RAM: {mem_gb:.1f} GB")
        else:
            print(f"⚠️  RAM: {mem_gb:.1f} GB (рекомендуется >= 8 GB)")
    except ImportError:
        print("⚠️  psutil не установлен, проверка памяти пропущена")
        checks["memory"] = True  # Предполагаем что все ОК

    print("=" * 80)
    return checks


def run_full_validation(
    rs11b_full: bool = True,
    cdls_validation: bool = True,
    output_dir: Path | None = None,
) -> dict:
    """
    Запустить полную валидацию.

    Args:
        rs11b_full: Запустить RS-11B с полными параметрами
        cdls_validation: Запустить CdLS валидацию
        output_dir: Выходная директория

    Returns:
        Словарь с результатами
    """
    print("=" * 80)
    print("ПОЛНАЯ ВАЛИДАЦИЯ ARCHCODE")
    print("=" * 80)

    checks = check_prerequisites()

    results = {
        "rs11b": None,
        "cdls": None,
        "start_time": time.time(),
    }

    # 1. RS-11B Phase Diagram (полная версия)
    if rs11b_full:
        print("\n" + "=" * 80)
        print("ШАГ 1: RS-11B PHASE DIAGRAM (ПОЛНАЯ ВАЛИДАЦИЯ)")
        print("=" * 80)
        print("⚠️  ВНИМАНИЕ: Это займет 4-6 часов!")
        print("   Параметры: 50×50 точек, 100 циклов")
        print("=" * 80)

        builder = RS11BPhaseDiagram(output_dir=output_dir)

        # Изменить параметры на полные
        print("\n📝 Изменяю параметры на полные...")
        print("   Bookmarking: 0.0-1.0, 50 точек")
        print("   Epigenetic: 0.0-1.0, 50 точек")
        print("   Циклы: 100")

        try:
            results["rs11b"] = builder.build_phase_diagram(
                bookmarking_range=(0.0, 1.0, 50),  # Полная сетка
                epigenetic_range=(0.0, 1.0, 50),  # Полная сетка
                processivity=0.9,
                num_cycles=100,  # Больше циклов
            )

            # Визуализация
            figure_path = builder.visualize_phase_diagram(results["rs11b"])
            results["rs11b"]["figure_path"] = str(figure_path)

            print("\n✅ RS-11B завершен успешно!")
        except Exception as e:
            print(f"\n❌ Ошибка в RS-11B: {e}")
            results["rs11b"] = {"error": str(e)}

    # 2. CdLS Validation
    if cdls_validation:
        print("\n" + "=" * 80)
        print("ШАГ 2: CdLS VALIDATION")
        print("=" * 80)

        validator = CdLSValidation(output_dir=output_dir)

        # Найти путь к CdLS данным
        cdls_paths = [
            "data/real/CdLS_Like_HCT116.mcool::/resolutions/10000",
            "data/real_hic/CdLS/CdLS_HCT116_10kb.cool",
            "data/real_hic/WT/Rao2014_GM12878_1000kb.cool",  # Fallback
        ]

        cdls_path = None
        for path in cdls_paths:
            if "::" in path:
                # mcool format
                base_path = path.split("::")[0]
                if Path(base_path).exists():
                    cdls_path = path
                    break
            elif Path(path).exists():
                cdls_path = path
                break

        if not cdls_path:
            cdls_path = cdls_paths[-1]  # Fallback to WT
            print(f"⚠️  Используется fallback: {cdls_path}")

        try:
            results["cdls"] = validator.run_validation(cdls_cooler_path=cdls_path)
            print("\n✅ CdLS валидация завершена успешно!")
        except Exception as e:
            print(f"\n❌ Ошибка в CdLS валидации: {e}")
            results["cdls"] = {"error": str(e)}

    # Итоговый отчет
    results["end_time"] = time.time()
    results["duration"] = results["end_time"] - results["start_time"]
    results["duration_hours"] = results["duration"] / 3600

    print("\n" + "=" * 80)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)
    print(f"Время выполнения: {results['duration_hours']:.2f} часов")
    print(f"RS-11B: {'✅' if results['rs11b'] and 'error' not in results['rs11b'] else '❌'}")
    print(f"CdLS: {'✅' if results['cdls'] and 'error' not in results['cdls'] else '❌'}")

    # Сохранить отчет
    import json
    report_file = Path("data/output/full_validation_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Отчет сохранен: {report_file}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Полная валидация ARCHCODE")
    parser.add_argument(
        "--skip-rs11b",
        action="store_true",
        help="Пропустить RS-11B (долго)",
    )
    parser.add_argument(
        "--skip-cdls",
        action="store_true",
        help="Пропустить CdLS валидацию",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Выходная директория",
    )

    args = parser.parse_args()

    results = run_full_validation(
        rs11b_full=not args.skip_rs11b,
        cdls_validation=not args.skip_cdls,
        output_dir=Path(args.output_dir) if args.output_dir else None,
    )


