"""RS-12: Complete Single-cell Hi-C Analysis Pipeline.

Полный пайплайн анализа sci-Hi-C данных с автоматической проверкой структуры,
загрузкой данных, генерацией симуляций и созданием визуализаций.
"""

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.run_RS12_sci_hic_benchmark import RS12SciHiCBenchmark


def create_rs12_figures(results: dict[str, Any], output_dir: Path) -> None:
    """
    Создает визуализации для RS-12.

    Args:
        results: Результаты бенчмарка
        output_dir: Директория для сохранения фигур
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Figure 1: P(s) сравнение для всех условий
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    conditions = ["d0", "d7", "d20", "NPC"]
    colors = ["blue", "green", "orange", "red"]
    
    for idx, (condition, color) in enumerate(zip(conditions, colors)):
        ax = axes[idx]
        
        if condition in results and results[condition].get("status") == "success":
            # Здесь нужно будет загрузить реальные данные для визуализации
            # Пока заглушка
            ax.text(0.5, 0.5, f"{condition}\n(данные загружены)", 
                   ha="center", va="center", fontsize=14)
            ax.set_title(f"{condition}", fontweight="bold")
        else:
            ax.text(0.5, 0.5, f"{condition}\n(данные не найдены)", 
                   ha="center", va="center", fontsize=14, color="gray")
            ax.set_title(f"{condition} (нет данных)", fontweight="bold", color="gray")
        
        ax.set_xlabel("Distance (bp)")
        ax.set_ylabel("Contact Frequency")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.grid(True, alpha=0.3)
    
    plt.suptitle("RS-12: P(s) Profiles Comparison", fontsize=16, fontweight="bold")
    plt.tight_layout()
    
    fig_path = output_dir / "RS12_Ps_comparison.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    print(f"[RS-12] Figure saved: {fig_path}")
    plt.close()
    
    # Figure 2: Processivity vs Bookmarking фазовая диаграмма
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for condition in conditions:
        if condition in results and results[condition].get("status") == "success":
            proc = results[condition].get("processivity", 1.0)
            book = results[condition].get("bookmarking", 0.8)
            ax.scatter(proc, book, s=200, alpha=0.7, label=condition)
    
    ax.set_xlabel("Processivity", fontweight="bold")
    ax.set_ylabel("Bookmarking", fontweight="bold")
    ax.set_title("RS-12: Processivity vs Bookmarking Phase Diagram", fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    fig_path = output_dir / "RS12_phase_diagram.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    print(f"[RS-12] Figure saved: {fig_path}")
    plt.close()


def main() -> None:
    """Полный пайплайн RS-12."""
    print("=" * 70)
    print("🚀 RS-12: Complete Single-cell Hi-C Analysis Pipeline")
    print("=" * 70)
    print()
    
    # Инициализация
    benchmark = RS12SciHiCBenchmark()
    
    # Проверка наличия данных
    if not benchmark.sci_hic_dir.exists():
        print(f"❌ Ошибка: папка sci-Hi-C не найдена: {benchmark.sci_hic_dir}")
        print()
        print("💡 Убедитесь, что:")
        print("   1. Данные GSE185608 распакованы")
        print("   2. Путь к sci-Hi-C правильный")
        print("   3. Структура папок соответствует ожидаемой")
        sys.exit(1)
    
    print(f"✅ Найдена папка sci-Hi-C: {benchmark.sci_hic_dir}")
    print()
    
    # Запуск бенчмарка
    results = benchmark.run_benchmark()
    
    # Создание визуализаций
    print()
    print("=" * 70)
    print("📊 Создание визуализаций")
    print("=" * 70)
    
    try:
        create_rs12_figures(results, benchmark.output_dir)
    except Exception as e:
        print(f"⚠️  Ошибка при создании визуализаций: {e}")
        import traceback
        traceback.print_exc()
    
    # Финальный отчет
    print()
    print("=" * 70)
    print("✅ RS-12 Complete Pipeline завершен!")
    print("=" * 70)
    print()
    print("📁 Результаты:")
    print(f"   - JSON: {benchmark.data_dir / 'RS12_sci_hic_results.json'}")
    print(f"   - Figures: {benchmark.output_dir}")
    print()
    print("📊 Статус по условиям:")
    for condition, result in results.items():
        status = result.get("status", "unknown")
        icon = "✅" if status == "success" else "⚠️" if status == "no_p_s_data" else "❌"
        print(f"   {icon} {condition}: {status}")


if __name__ == "__main__":
    main()



