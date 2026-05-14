"""
Cross-Omics Orthogonality Detector

Классифицирует пары методов измерения как:
- CONCORDANT: методы согласны (ρ > 0.5), измеряют одно и то же
- ORTHOGONAL: методы независимы (ρ ≈ 0), измеряют разные механизмы
- CONFLICTING: методы противоречат (ρ < -0.3), один ошибочен

Применение: геномика (CAGE vs ATAC-seq), ML (ensemble disagreement),
             медицина (независимые биомаркеры)

Автор: Sergey Boyko (ARCHCODE Project)
Дата: 2026-05-14
Лицензия: MIT
"""

import numpy as np
from scipy.stats import spearmanr, mannwhitneyu
from typing import Dict, List, Tuple, Optional
import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap


def classify_orthogonality(
    A: np.ndarray,
    B: np.ndarray,
    labels: np.ndarray,
    rho_concordant: float = 0.5,
    rho_orthogonal_min: float = -0.3,
    rho_orthogonal_max: float = 0.3,
    alpha: float = 0.05,
    min_n: int = 15,
    min_cv: float = 5.0,
    return_details: bool = True,
) -> Dict:
    """
    Классифицирует отношение между двумя методами измерения.

    Параметры:
    ----------
    A : np.ndarray
        Предсказания метода A (continuous values)
    B : np.ndarray
        Предсказания метода B (continuous values)
    labels : np.ndarray
        Бинарные метки (0 = negative, 1 = positive)
        Например: 0 = benign, 1 = pathogenic
    rho_concordant : float, default=0.5
        Порог корреляции для CONCORDANT (если ρ > порог)
    rho_orthogonal_min : float, default=-0.3
        Нижняя граница ортогональности
    rho_orthogonal_max : float, default=0.3
        Верхняя граница ортогональности
    alpha : float, default=0.05
        Уровень значимости для Mann-Whitney U test
    min_n : int, default=15
        Минимальный размер выборки (предупреждение если меньше)
    min_cv : float, default=5.0
        Минимальный коэффициент вариации % (предупреждение если меньше)
    return_details : bool, default=True
        Вернуть полные детали анализа

    Возвращает:
    -----------
    dict с полями:
        - classification : str
            "CONCORDANT" | "ORTHOGONAL" | "CONFLICTING" | "AMBIGUOUS"
        - rho : float
            Корреляция Спирмена между A и B
        - p_correlation : float
            p-value корреляции
        - group_0_mean_A, group_1_mean_A : float
            Средние значения A для двух групп
        - group_0_mean_B, group_1_mean_B : float
            Средние значения B для двух групп
        - p_diff_A : float
            p-value Mann-Whitney U для метода A
        - p_diff_B : float
            p-value Mann-Whitney U для метода B
        - n : int
            Размер выборки
        - cv_A, cv_B : float
            Коэффициент вариации (%) для A и B
        - warnings : List[str]
            Предупреждения о качестве данных
        - interpretation : str
            Человекочитаемая интерпретация

    Примеры:
    --------
    >>> # ORTHOGONAL case (ARCHCODE × AlphaGenome)
    >>> A = np.array([0.85, 0.90, 0.95, ...])  # ARCHCODE LSSIM
    >>> B = np.array([-0.15, -0.08, -0.20, ...])  # AlphaGenome CAGE delta
    >>> labels = np.array([1, 1, 1, 0, 0, 0, ...])  # pathogenic/benign
    >>> result = classify_orthogonality(A, B, labels)
    >>> print(result['classification'])
    'ORTHOGONAL'

    >>> # CONCORDANT case (synthetic)
    >>> A = np.array([1, 2, 3, 4, 5])
    >>> B = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    >>> labels = np.array([0, 0, 1, 1, 1])
    >>> result = classify_orthogonality(A, B, labels)
    >>> print(result['classification'])
    'CONCORDANT'
    """

    # Валидация входных данных
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    labels = np.asarray(labels, dtype=int)

    if len(A) != len(B) or len(A) != len(labels):
        raise ValueError(f"Размеры не совпадают: A={len(A)}, B={len(B)}, labels={len(labels)}")

    if len(np.unique(labels)) != 2:
        raise ValueError(
            f"labels должен быть бинарным (0/1), найдено {len(np.unique(labels))} уникальных значений"
        )

    n = len(A)
    warnings_list = []

    # Проверка размера выборки
    if n < min_n:
        warnings_list.append(f"Малая выборка (N={n} < {min_n}), результаты могут быть ненадёжными")

    # Проверка NaN/Inf
    if np.any(~np.isfinite(A)) or np.any(~np.isfinite(B)):
        raise ValueError("A или B содержат NaN/Inf значения")

    # 1. Корреляция Спирмена (ранговая, устойчива к выбросам)
    rho, p_corr = spearmanr(A, B)

    # 2. Коэффициент вариации (CV) — проверка разброса данных
    cv_A = (np.std(A) / np.abs(np.mean(A))) * 100 if np.mean(A) != 0 else 0
    cv_B = (np.std(B) / np.abs(np.mean(B))) * 100 if np.mean(B) != 0 else 0

    if cv_A < min_cv:
        warnings_list.append(
            f"Низкая вариация A (CV={cv_A:.1f}% < {min_cv}%), корреляция может быть ненадёжной"
        )
    if cv_B < min_cv:
        warnings_list.append(
            f"Низкая вариация B (CV={cv_B:.1f}% < {min_cv}%), корреляция может быть ненадёжной"
        )

    # 3. Разделение групп (Mann-Whitney U test)
    group_0_A = A[labels == 0]
    group_1_A = A[labels == 1]
    group_0_B = B[labels == 0]
    group_1_B = B[labels == 1]

    # Проверка размеров групп
    if len(group_0_A) < 3 or len(group_1_A) < 3:
        warnings_list.append(
            f"Малые группы (group_0={len(group_0_A)}, group_1={len(group_1_A)}), тест может быть ненадёжным"
        )

    # Mann-Whitney U (two-sided, no assumption of direction)
    stat_A, p_diff_A = mannwhitneyu(group_0_A, group_1_A, alternative="two-sided")
    stat_B, p_diff_B = mannwhitneyu(group_0_B, group_1_B, alternative="two-sided")

    # 4. Классификация
    both_separate = (p_diff_A < alpha) and (p_diff_B < alpha)
    one_separates = (p_diff_A < alpha) or (p_diff_B < alpha)
    a_separates = p_diff_A < alpha
    b_separates = p_diff_B < alpha

    if rho > rho_concordant:
        classification = "CONCORDANT"
        interpretation = (
            f"Методы СОГЛАСНЫ (ρ={rho:.3f} > {rho_concordant}): измеряют одно и то же явление. "
            f"Можно выбрать один метод или усреднить."
        )
    elif rho_orthogonal_min <= rho <= rho_orthogonal_max:
        if both_separate:
            classification = "ORTHOGONAL"
            interpretation = (
                f"Методы ОРТОГОНАЛЬНЫ (ρ={rho:.3f} ≈ 0, оба p<{alpha}): измеряют РАЗНЫЕ механизмы. "
                f"Оба метода информативны, РЕКОМЕНДУЕТСЯ КОМБИНИРОВАТЬ для полного покрытия."
            )
        elif one_separates:
            # НОВАЯ КАТЕГОРИЯ: односторонняя ортогональность
            stronger_method = "A" if a_separates else "B"
            classification = "WEAK-ORTHOGONAL"
            interpretation = (
                f"СЛАБАЯ ОРТОГОНАЛЬНОСТЬ (ρ={rho:.3f} ≈ 0, только метод {stronger_method} значим): "
                f"методы измеряют разные механизмы, но один сильнее на ЭТОМ датасете. "
                f"Возможно малая вариация слабого метода (проверьте CV) или неудачный выбор контролей. "
                f"Рекомендация: используйте сильный метод ({stronger_method}), слабый может улучшить при других данных."
            )
        else:
            classification = "AMBIGUOUS"
            interpretation = (
                f"НЕОДНОЗНАЧНЫЙ случай (ρ={rho:.3f} ≈ 0, оба p>{alpha}): "
                f"ни один метод не разделяет группы значимо. Проблема с данными или метки неверны."
            )
    elif rho < rho_orthogonal_min:
        classification = "CONFLICTING"
        interpretation = (
            f"Методы КОНФЛИКТУЮТ (ρ={rho:.3f} < {rho_orthogonal_min}): отрицательная корреляция. "
            f"Один метод может быть ошибочным, или метки перепутаны, или механизмы антагонистичны."
        )
    else:
        # rho между orthogonal_max и concordant (например, 0.3 < ρ < 0.5)
        classification = "AMBIGUOUS"
        interpretation = (
            f"УМЕРЕННАЯ корреляция (ρ={rho:.3f}): частично согласны, частично независимы. "
            f"Может быть полезно комбинировать, но эффект слабее чем при чистой ортогональности."
        )

    # 5. Результат
    result = {
        "classification": classification,
        "rho": float(rho),
        "p_correlation": float(p_corr),
        "group_0_mean_A": float(np.mean(group_0_A)),
        "group_1_mean_A": float(np.mean(group_1_A)),
        "group_0_mean_B": float(np.mean(group_0_B)),
        "group_1_mean_B": float(np.mean(group_1_B)),
        "p_diff_A": float(p_diff_A),
        "p_diff_B": float(p_diff_B),
        "n": int(n),
        "n_group_0": int(len(group_0_A)),
        "n_group_1": int(len(group_1_A)),
        "cv_A": float(cv_A),
        "cv_B": float(cv_B),
        "warnings": warnings_list,
        "interpretation": interpretation,
    }

    if not return_details:
        # Минимальный вывод
        return {
            "classification": classification,
            "rho": float(rho),
            "interpretation": interpretation,
        }

    return result


def print_result(result: Dict) -> None:
    """
    Печатает результат classify_orthogonality в человекочитаемом виде.

    Параметры:
    ----------
    result : dict
        Результат от classify_orthogonality()
    """
    print("=" * 70)
    print(f"CLASSIFICATION: {result['classification']}")
    print("=" * 70)
    print(f"\nКорреляция: ρ = {result['rho']:.3f} (p = {result['p_correlation']:.4f})")
    print(
        f"Размер выборки: N = {result['n']} (группы: {result['n_group_0']} / {result['n_group_1']})"
    )
    print(f"\nМетод A:")
    print(f"  Group 0 mean: {result['group_0_mean_A']:.4f}")
    print(f"  Group 1 mean: {result['group_1_mean_A']:.4f}")
    print(f"  p-value (Mann-Whitney): {result['p_diff_A']:.4f}")
    print(f"  CV: {result['cv_A']:.1f}%")
    print(f"\nМетод B:")
    print(f"  Group 0 mean: {result['group_0_mean_B']:.4f}")
    print(f"  Group 1 mean: {result['group_1_mean_B']:.4f}")
    print(f"  p-value (Mann-Whitney): {result['p_diff_B']:.4f}")
    print(f"  CV: {result['cv_B']:.1f}%")

    if result["warnings"]:
        print(f"\n⚠️  WARNINGS:")
        for w in result["warnings"]:
            print(f"  - {w}")

    print(f"\n📊 INTERPRETATION:")
    print(f"  {result['interpretation']}")
    print("=" * 70)


def batch_classify(
    datasets: List[Tuple[str, np.ndarray, np.ndarray, np.ndarray]], **kwargs
) -> Dict[str, Dict]:
    """
    Классифицирует несколько пар методов за один вызов.

    Параметры:
    ----------
    datasets : List[Tuple[str, np.ndarray, np.ndarray, np.ndarray]]
        Список кортежей (name, A, B, labels)
    **kwargs :
        Параметры для classify_orthogonality()

    Возвращает:
    -----------
    Dict[str, Dict]
        Словарь {name: result}

    Пример:
    -------
    >>> datasets = [
    ...     ("ARCHCODE_x_AlphaGenome", A1, B1, labels1),
    ...     ("CAGE_x_ATAC", A2, B2, labels2),
    ... ]
    >>> results = batch_classify(datasets)
    >>> for name, res in results.items():
    ...     print(f"{name}: {res['classification']}")
    """
    results = {}
    for name, A, B, labels in datasets:
        try:
            results[name] = classify_orthogonality(A, B, labels, **kwargs)
        except Exception as e:
            results[name] = {"classification": "ERROR", "error": str(e)}
    return results


# Пример использования
if __name__ == "__main__":
    print("Cross-Omics Orthogonality Detector - Demo\n")

    # Test 1: ORTHOGONAL (inspired by ARCHCODE × AlphaGenome)
    print("Test 1: ORTHOGONAL (симуляция ARCHCODE × AlphaGenome)")
    np.random.seed(42)

    # ARCHCODE: pathogenic имеют низкий LSSIM (structural disruption)
    archcode_pathogenic = np.random.normal(0.85, 0.03, 15)  # lower LSSIM
    archcode_benign = np.random.normal(0.95, 0.02, 15)  # higher LSSIM

    # AlphaGenome: pathogenic имеют negative CAGE delta (loss of transcription)
    alphag_pathogenic = np.random.normal(-0.12, 0.04, 15)  # negative delta
    alphag_benign = np.random.normal(-0.03, 0.03, 15)  # near zero

    A_test1 = np.concatenate([archcode_pathogenic, archcode_benign])
    B_test1 = np.concatenate([alphag_pathogenic, alphag_benign])
    labels_test1 = np.array([1] * 15 + [0] * 15)

    result1 = classify_orthogonality(A_test1, B_test1, labels_test1)
    print_result(result1)

    # Test 2: CONCORDANT
    print("\n\nTest 2: CONCORDANT (synthetic)")
    A_test2 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    B_test2 = A_test2 * 1.2 + np.random.normal(0, 0.3, 10)  # high correlation
    labels_test2 = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])

    result2 = classify_orthogonality(A_test2, B_test2, labels_test2)
    print_result(result2)

    # Test 3: CONFLICTING
    print("\n\nTest 3: CONFLICTING (synthetic)")
    A_test3 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    B_test3 = -A_test3 + np.random.normal(0, 0.5, 10)  # negative correlation
    labels_test3 = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])

    result3 = classify_orthogonality(A_test3, B_test3, labels_test3)
    print_result(result3)

    print("\n✅ Demo complete!")
