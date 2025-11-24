"""RS-12: Single-cell Hi-C Benchmarking.

Сравнение sci-Hi-C данных (GSE185608) с предсказаниями модели
processivity/bookmarking для проверки гипотезы о дискретных структурных переключениях.
"""

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.vizir.config_loader import VIZIRConfigLoader

# Определяем корневую директорию проекта
BASE_DIR = Path(__file__).parent.parent


class RS12SciHiCBenchmark:
    """Benchmarking sci-Hi-C данных против модели bookmarking."""

    def __init__(self) -> None:
        """Инициализация."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("figures/RS12")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = Path("data/output/RS12")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Путь к распакованным данным GSE185608
        # Автоматическое определение пути
        base_paths = [
            Path(r"D:\ДНК КУРСОР\skachenie DANNIE\GSE185608_4DNFIZ8TEE2M\sci-Hi-C"),
            Path("data/real/GSE185608_sciHiC"),
            BASE_DIR / "skachenie DANNIE" / "GSE185608_4DNFIZ8TEE2M" / "sci-Hi-C",
        ]
        
        self.sci_hic_dir = None
        for path in base_paths:
            if path.exists():
                self.sci_hic_dir = path
                break
        
        if self.sci_hic_dir is None:
            print(f"[RS-12] ⚠️  Не найдена папка sci-Hi-C данных")
            print(f"[RS-12]    Проверенные пути: {base_paths}")
            self.sci_hic_dir = base_paths[0]  # Используем первый как fallback

    def load_sci_hic_data(self, condition: str = "d0") -> dict[str, Any]:
        """
        Загружает sci-Hi-C данные для указанного условия.

        Args:
            condition: Условие ("d0", "d7", "d20", "NPC", etc.)

        Returns:
            Словарь с данными: P(s) profiles, XCI cells, metadata
        """
        import gzip
        
        print(f"[RS-12] Загрузка sci-Hi-C данных для условия: {condition}")

        data = {
            "condition": condition,
            "p_s_profiles": {},  # P(s) профили по типам
            "xci_cells": {},  # X-инактивация клеток
            "metadata": {},
        }

        # Загрузка P(s) профилей из non-allelic_contact_decay_profiles
        p_s_dir = self.sci_hic_dir / "non-allelic_contact_decay_profiles"
        
        if not p_s_dir.exists():
            print(f"[RS-12] ⚠️  Папка {p_s_dir} не найдена")
            return data

        # Ищем файлы для указанного условия
        # Паттерны: F121_d0, EBdiff_F121_d0, mES_EBdiff_D0, etc.
        pattern_files = list(p_s_dir.glob(f"*{condition}*.gz"))
        
        if not pattern_files:
            # Пробуем альтернативные форматы (D0 вместо d0)
            alt_condition = condition.replace("d", "D")
            pattern_files = list(p_s_dir.glob(f"*{alt_condition}*.gz"))

        print(f"[RS-12] Найдено {len(pattern_files)} файлов для условия {condition}")

        for file_path in pattern_files:
            try:
                # Определяем тип файла по названию
                file_name = file_path.name
                file_type = "all"
                
                if "autosomes" in file_name.lower():
                    file_type = "autosomes"
                elif "logbin" in file_name.lower():
                    file_type = "logbin"
                
                # Загружаем P(s) профиль
                with gzip.open(file_path, "rt") as f:
                    # Формат: первая колонка "bin" (расстояние), остальные - отдельные клетки
                    df = pd.read_csv(f, sep="\t")
                    
                    # Первая колонка - расстояние (bin), остальные - клетки
                    if "bin" in df.columns:
                        # Вычисляем средний P(s) профиль по всем клеткам
                        cell_columns = [col for col in df.columns if col != "bin"]
                        df["contact_frequency"] = df[cell_columns].mean(axis=1)
                        df["distance"] = df["bin"]  # Предполагаем, что bin это расстояние в бинах
                        # Конвертируем в bp (предполагаем разрешение 10kb для logbin файлов)
                        df["distance"] = df["distance"] * 10000
                        
                        # Оставляем только нужные колонки
                        p_s_df = df[["distance", "contact_frequency"]].copy()
                        p_s_df = p_s_df[p_s_df["contact_frequency"] > 0]  # Убираем нули
                        p_s_df = p_s_df.sort_values("distance")
                        
                        data["p_s_profiles"][file_type] = p_s_df
                        data["metadata"][f"{file_type}_n_cells"] = len(cell_columns)
                    else:
                        # Альтернативный формат
                        df.columns = ["distance", "contact_frequency"]
                        data["p_s_profiles"][file_type] = df
                    
                print(f"[RS-12]   Загружен: {file_name} ({len(df)} точек)")
                
            except Exception as e:
                print(f"[RS-12]   ⚠️  Ошибка загрузки {file_path.name}: {e}")

        # Загрузка данных по X-инактивации
        xci_dir = self.sci_hic_dir / "LMD_XCI_cells_countthresh50"
        
        if xci_dir.exists():
            xci_files = list(xci_dir.glob(f"*{condition}*.tsv"))
            
            for file_path in xci_files:
                file_name = file_path.name
                xci_type = None
                
                if "altXCIcells" in file_name:
                    xci_type = "altXCI"
                elif "refXCIcells" in file_name:
                    xci_type = "refXCI"
                elif "nonXCIcells" in file_name:
                    xci_type = "nonXCI"
                
                if xci_type:
                    try:
                        df = pd.read_csv(file_path, sep="\t")
                        data["xci_cells"][xci_type] = df
                        print(f"[RS-12]   Загружены XCI клетки: {xci_type} ({len(df)} клеток)")
                    except Exception as e:
                        print(f"[RS-12]   ⚠️  Ошибка загрузки XCI {file_path.name}: {e}")

        return data

    def compute_p_s_from_matrix(self, matrix: np.ndarray, resolution: int = 10000) -> pd.DataFrame:
        """
        Вычисляет P(s) профиль из контактной матрицы.

        Args:
            matrix: Контактная матрица (N x N)
            resolution: Разрешение в bp

        Returns:
            DataFrame с колонками ['distance', 'contact_frequency']
        """
        n = matrix.shape[0]
        distances = []
        frequencies = []

        for i in range(n):
            for j in range(i + 1, n):
                dist = abs(j - i) * resolution
                freq = matrix[i, j]
                if freq > 0:
                    distances.append(dist)
                    frequencies.append(freq)

        df = pd.DataFrame({"distance": distances, "contact_frequency": frequencies})
        df = df.groupby("distance")["contact_frequency"].mean().reset_index()
        df = df.sort_values("distance")

        return df

    def generate_simulation_p_s(
        self,
        processivity: float,
        bookmarking: float = 0.8,
        ctcf_occupancy: float = 0.9,
    ) -> pd.DataFrame:
        """
        Генерирует P(s) профиль из модели для сравнения.

        Args:
            processivity: Processivity factor
            bookmarking: Bookmarking fraction
            ctcf_occupancy: CTCF occupancy

        Returns:
            DataFrame с P(s) профилем
        """
        print(f"[RS-12] Генерация симуляции: P={processivity:.2f}, B={bookmarking:.2f}")

        # Используем упрощенную модель для генерации P(s)
        # В реальной реализации здесь будет полный пайплайн ARCHCODE

        distances = np.logspace(4, 7, 100)  # От 10kb до 10Mb

        # Упрощенная модель: P(s) ~ s^(-alpha)
        # alpha зависит от processivity и bookmarking
        alpha = 1.0 - 0.3 * processivity + 0.2 * (1 - bookmarking)

        frequencies = distances ** (-alpha)
        frequencies = frequencies / frequencies[0]  # Нормализация

        df = pd.DataFrame({"distance": distances, "contact_frequency": frequencies})

        return df

    def compare_p_s_profiles(
        self,
        real_p_s: pd.DataFrame,
        sim_p_s: pd.DataFrame,
        condition: str,
    ) -> dict[str, Any]:
        """
        Сравнивает реальные и симулированные P(s) профили.

        Args:
            real_p_s: Реальный P(s) профиль
            sim_p_s: Симулированный P(s) профиль
            condition: Название условия

        Returns:
            Словарь с метриками сравнения
        """
        # Интерполируем на общие расстояния
        all_distances = np.unique(
            np.concatenate([real_p_s["distance"].values, sim_p_s["distance"].values])
        )
        all_distances = np.sort(all_distances)

        real_interp = np.interp(
            all_distances, real_p_s["distance"].values, real_p_s["contact_frequency"].values
        )
        sim_interp = np.interp(
            all_distances, sim_p_s["distance"].values, sim_p_s["contact_frequency"].values
        )

        # Вычисляем метрики
        correlation = np.corrcoef(real_interp, sim_interp)[0, 1]
        mse = np.mean((real_interp - sim_interp) ** 2)
        mae = np.mean(np.abs(real_interp - sim_interp))

        metrics = {
            "condition": condition,
            "correlation": float(correlation),
            "mse": float(mse),
            "mae": float(mae),
            "n_points": len(all_distances),
        }

        return metrics

    def run_benchmark(self) -> dict[str, Any]:
        """Запускает полный бенчмарк sci-Hi-C данных."""
        print("=" * 60)
        print("RS-12: Single-cell Hi-C Benchmarking")
        print("=" * 60)
        print()

        # Условия для анализа (соответствуют названиям файлов)
        conditions = ["d0", "d7", "d20", "NPC"]  # d0=ESC, d7/d20=дифференцировка, NPC=нейральные предшественники

        results = {}

        for condition in conditions:
            print(f"\n{'=' * 60}")
            print(f"Условие: {condition}")
            print(f"{'=' * 60}")

            # Загрузка реальных данных
            real_data = self.load_sci_hic_data(condition)

            if real_data["p_s_profiles"] is None:
                print(f"[RS-12] ⚠️  Данные для {condition} не загружены, пропускаю")
                continue

            # Генерация симуляции
            # Параметры зависят от условия:
            # - d0 (ESC): высокий bookmarking, средняя processivity
            # - d7/d20 (Differentiated): снижение bookmarking
            # - NPC: особый режим
            if condition == "d0":
                processivity, bookmarking = 1.0, 0.9  # ESC: высокий bookmarking
            elif condition in ["d7", "d20"]:
                # Дифференцировка: снижение bookmarking со временем
                bookmarking_val = 0.8 if condition == "d7" else 0.7
                processivity, bookmarking = 1.0, bookmarking_val
            elif condition == "NPC":
                processivity, bookmarking = 0.9, 0.75  # NPC: промежуточное состояние
            else:
                processivity, bookmarking = 1.0, 0.8

            sim_p_s = self.generate_simulation_p_s(processivity, bookmarking)

            # Сравнение с реальными данными
            if "logbin" in real_data["p_s_profiles"] or "all" in real_data["p_s_profiles"]:
                # Используем основной профиль или logbin
                real_p_s_key = "logbin" if "logbin" in real_data["p_s_profiles"] else "all"
                real_p_s = real_data["p_s_profiles"][real_p_s_key]
                
                metrics = self.compare_p_s_profiles(real_p_s, sim_p_s, condition)
                
                results[condition] = {
                    "processivity": processivity,
                    "bookmarking": bookmarking,
                    "metrics": metrics,
                    "xci_cells_count": {
                        k: len(v) for k, v in real_data["xci_cells"].items()
                    },
                    "status": "success",
                }
            else:
                print(f"[RS-12] ⚠️  P(s) профили не найдены для {condition}")
                results[condition] = {
                    "processivity": processivity,
                    "bookmarking": bookmarking,
                    "status": "no_p_s_data",
                }

            results[condition] = {
                "processivity": processivity,
                "bookmarking": bookmarking,
                # "metrics": metrics,
                "status": "pending_data_loading",
            }

        # Сохранение результатов
        results_path = self.data_dir / "RS12_sci_hic_results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        print("\n" + "=" * 60)
        print("✅ RS-12 Benchmarking завершен")
        print("=" * 60)
        print(f"\n📊 Результаты сохранены: {results_path}")

        return results


def main() -> None:
    """Запуск RS-12 бенчмарка."""
    benchmark = RS12SciHiCBenchmark()
    results = benchmark.run_benchmark()

    print("\n💡 Следующие шаги:")
    print("   1. Изучите структуру данных в data/real/GSE185608_sciHiC/")
    print("   2. Адаптируйте load_sci_hic_data() под реальные файлы")
    print("   3. Запустите бенчмарк снова")


if __name__ == "__main__":
    main()

