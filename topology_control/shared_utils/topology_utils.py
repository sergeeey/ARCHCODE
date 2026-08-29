"""
Топологические утилиты для ATR Framework

Включает:
- Linking number вычисления
- Knot/catenane detection
- Topological complexity C(G)
- Writhe/twist разложение
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TopologicalState:
    """Топологическое состояние полимерной системы"""

    num_knots: int
    num_catenanes: int
    linking_numbers: List[int]
    supercoiling: List[float]
    complexity: float


def calculate_complexity(
    num_knots: int,
    num_catenanes: int,
    linking_numbers: List[int],
    supercoiling: List[float],
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 0.5,
    delta: float = 0.3,
) -> float:
    """
    Вычислить топологическую сложность C(G)

    C(G) = α|K| + β|C| + γΣ|Lk_ij| + δΣ|σ_i|

    Parameters
    ----------
    num_knots : int
        Число узлов
    num_catenanes : int
        Число катенанов (catenanes)
    linking_numbers : List[int]
        Linking numbers между парами
    supercoiling : List[float]
        Supercoiling в каждом домене
    alpha, beta, gamma, delta : float
        Веса компонентов сложности

    Returns
    -------
    complexity : float
        Общая топологическая сложность

    Notes
    -----
    [DERIVED-INFERENCE] Веса по умолчанию: узлы и катенаны тяжелее,
    чем linking/supercoiling, так как их сложнее разрешить.

    [UNKNOWN] Оптимальные веса для живой клетки — подбираются эмпирически.
    """
    C = (
        alpha * abs(num_knots)
        + beta * abs(num_catenanes)
        + gamma * sum(abs(lk) for lk in linking_numbers)
        + delta * sum(abs(sc) for sc in supercoiling)
    )
    return C


def writhe_twist_decomposition(linking_number: int, turns: float) -> Tuple[float, float]:
    """
    Разложение Lk = Tw + Wr

    Parameters
    ----------
    linking_number : int
        Linking number (топологический инвариант)
    turns : float
        Измеренное число витков (twist)

    Returns
    -------
    twist : float
        Twist компонента
    writhe : float
        Writhe компонента (из-за суперспирализации)

    Notes
    -----
    [ESTABLISHED] Формула Călugăreanu: Lk = Tw + Wr
    где Lk сохраняется при деформации без разрыва.
    """
    twist = turns
    writhe = linking_number - twist
    return twist, writhe


def gauss_linking_integral(curve1: np.ndarray, curve2: np.ndarray) -> float:
    """
    Вычислить linking number через интеграл Гаусса (упрощённая версия)

    Parameters
    ----------
    curve1, curve2 : np.ndarray, shape (N, 3)
        Координаты двух замкнутых кривых

    Returns
    -------
    linking_number : float
        Приближённое значение Lk

    Notes
    -----
    [WEAK] Это упрощённая дискретная версия.
    Для точного вычисления нужен более сложный алгоритм.

    [VERIFIED-CODE] Формула:
    Lk = (1/4π) ∬ (r1-r2)·(dr1 × dr2) / |r1-r2|³
    """
    # Simplified discrete approximation
    # For toy model — acceptable
    # For real analysis — use specialized library (e.g., pyknotid)

    N1, N2 = len(curve1), len(curve2)
    lk_sum = 0.0

    for i in range(N1 - 1):
        for j in range(N2 - 1):
            r1 = curve1[i]
            r2 = curve2[j]
            dr1 = curve1[i + 1] - curve1[i]
            dr2 = curve2[j + 1] - curve2[j]

            diff = r1 - r2
            dist = np.linalg.norm(diff)

            if dist > 1e-6:  # избежать деления на 0
                cross = np.cross(dr1, dr2)
                lk_sum += np.dot(diff, cross) / (dist**3)

    linking_number = lk_sum / (4 * np.pi)
    return linking_number


def detect_knot_simplified(polymer_coords: np.ndarray) -> bool:
    """
    Упрощённая детекция узла (для toy model)

    Parameters
    ----------
    polymer_coords : np.ndarray, shape (N, 3)
        Координаты замкнутого полимера

    Returns
    -------
    has_knot : bool
        True если обнаружен узел

    Notes
    -----
    [WEAK] Это очень упрощённая версия. Настоящая детекция узлов требует:
    - Alexander polynomial
    - Jones polynomial
    - HOMFLY polynomial

    Для production использовать pyknotid или Topoly.

    [INFERRED] Для toy model достаточно проверить self-crossing number.
    """
    # Placeholder: считаем self-crossings
    # Реальная детекция — через polynomial invariants

    N = len(polymer_coords)
    crossings = 0

    # Считаем пересечения (проекция на 2D)
    for i in range(N - 1):
        for j in range(i + 2, N - 1):
            # Проверка пересечения сегментов i и j в проекции xy
            p1, p2 = polymer_coords[i, :2], polymer_coords[i + 1, :2]
            p3, p4 = polymer_coords[j, :2], polymer_coords[j + 1, :2]

            if segments_intersect_2d(p1, p2, p3, p4):
                crossings += 1

    # Если crossings > threshold, возможно есть узел
    # [WEAK] Это не точная детекция, только heuristic
    has_knot = crossings > N // 4
    return has_knot


def segments_intersect_2d(p1, p2, p3, p4) -> bool:
    """Проверка пересечения двух отрезков в 2D"""

    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def calculate_catenation_simple(rings: List[np.ndarray]) -> int:
    """
    Упрощённое вычисление числа катенанов между кольцами

    Parameters
    ----------
    rings : List[np.ndarray]
        Список координат колец, каждое shape (N, 3)

    Returns
    -------
    num_catenanes : int
        Число пар колец, которые топологически сцеплены

    Notes
    -----
    [INFERRED] Два кольца сцеплены, если Lk ≠ 0
    """
    num_catenanes = 0

    for i in range(len(rings)):
        for j in range(i + 1, len(rings)):
            lk = gauss_linking_integral(rings[i], rings[j])
            if abs(lk) > 0.5:  # threshold для discrete approximation
                num_catenanes += 1

    return num_catenanes


# ============================================================
# Для T2: TOP2 strand passage events
# ============================================================


def strand_passage_random(ring1: np.ndarray, ring2: np.ndarray) -> float:
    """
    Baseline: случайная вероятность strand passage

    Returns
    -------
    probability : float
        Вероятность прохождения одного кольца через другое
    """
    return 0.5  # полностью случайно


def strand_passage_angle_bias(ring1: np.ndarray, ring2: np.ndarray, crossing_point: int) -> float:
    """
    Модель 2: bias по углу пересечения

    Parameters
    ----------
    ring1, ring2 : np.ndarray
        Координаты колец
    crossing_point : int
        Индекс точки пересечения

    Returns
    -------
    probability : float
        Вероятность passage, зависящая от угла

    Notes
    -----
    [HYPOTHESIS-T2] TOP2 предпочитает острые углы пересечения,
    где passage даёт большее упрощение.
    """
    # Вычислить угол между сегментами в точке пересечения
    # Упрощённо: берём локальные тангенты

    i = crossing_point
    if i >= len(ring1) - 1 or i >= len(ring2) - 1:
        return 0.5

    tangent1 = ring1[i + 1] - ring1[i]
    tangent2 = ring2[i + 1] - ring2[i]

    # Нормализуем
    tangent1 = tangent1 / (np.linalg.norm(tangent1) + 1e-8)
    tangent2 = tangent2 / (np.linalg.norm(tangent2) + 1e-8)

    # Угол между векторами
    cos_angle = np.dot(tangent1, tangent2)
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))

    # Bias: предпочитаем перпендикулярные пересечения (90°)
    # где упрощение максимально
    optimal_angle = np.pi / 2
    deviation = abs(angle - optimal_angle)

    # Probability выше, если угол близок к 90°
    probability = np.exp(-deviation / 0.5)  # β_angle = 0.5
    return probability


def strand_passage_curvature_bias(
    ring1: np.ndarray, ring2: np.ndarray, crossing_point: int
) -> float:
    """
    Модель 3: bias по углу + локальной кривизне

    Notes
    -----
    [HYPOTHESIS-T2] TOP2 может также учитывать локальную кривизну,
    избегая сильно изогнутых участков (энергетически невыгодны).
    """
    # Сначала угловой bias
    p_angle = strand_passage_angle_bias(ring1, ring2, crossing_point)

    # Добавляем кривизну
    i = crossing_point
    if i < 2 or i >= len(ring1) - 2:
        return p_angle

    # Локальная кривизна ≈ изменение направления
    v1 = ring1[i] - ring1[i - 1]
    v2 = ring1[i + 1] - ring1[i]
    v3 = ring1[i + 2] - ring1[i + 1]

    # Изменение направления
    d1 = v2 - v1
    d2 = v3 - v2
    curvature = np.linalg.norm(d1) + np.linalg.norm(d2)

    # Penalty за высокую кривизну
    p_curvature = np.exp(-curvature / 2.0)  # β_curv = 2.0

    # Комбинируем
    probability = p_angle * p_curvature
    return probability


# ============================================================
# Convenience функции
# ============================================================


def create_simple_ring(radius: float = 1.0, num_points: int = 100) -> np.ndarray:
    """Создать простое кольцо (окружность)"""
    theta = np.linspace(0, 2 * np.pi, num_points)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = np.zeros(num_points)
    return np.column_stack([x, y, z])


def create_linked_rings(
    radius: float = 1.0, separation: float = 1.0, num_points: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Создать два сцепленных кольца (Hopf link)

    Parameters
    ----------
    radius : float
        Радиус обоих колец.
    separation : float
        Смещение центра второго кольца вдоль x. Зацепление возникает при
        ``0 < separation < 2 * radius``; на границе ``2 * radius`` кольца касаются
        (вырожденный случай, Lk ≈ -0.5), дальше расцеплены.

    Returns
    -------
    (ring1, ring2)
        ring1 в плоскости xy, ring2 в плоскости xz со смещённым центром.

    Notes
    -----
    [VERIFIED 2026-08-29, замер] Lk = -1.00 (−0.9987 при num_points=100) на всём
    диапазоне separation ∈ (0, 2·radius). Проверяется
    ``test_passage_ops.py::test_hopf_link_has_linking_number_one``.

    ИСПРАВЛЕНО 2026-08-29 (см. ``AMENDMENTS.md`` A-002).
    Прежняя версия поворачивала ring2 в плоскость **yz** (перпендикулярно радиальному
    направлению) и смещала на ``separation`` по x. Тогда ring2 пересекал плоскость
    ring1 в точках ``(s, ±1, 0)``, где ``x² + y² = s² + 1 > 1`` — оба пересечения
    ВСЕГДА снаружи диска ring1. Кольца не были зацеплены **ни при каком** значении
    separation: замер давал Lk ≈ −0.01 для s = 0.3 … 1.3, тогда как докстринг
    утверждал ``[VERIFIED-CODE] Lk = 1``.

    Последствие: ``RingSystem.initialize_rings(mode="entangled")`` строил «частично
    сцепленные» пары через эту функцию — то есть эксперимент T2 стартовал с нулевой
    топологией, и упрощать было нечего.

    WHY плоскость xz: чтобы кольца зацепились, ring2 обязано лежать в плоскости,
    содержащей радиальное направление ring1, и пересекать его диск — одно пересечение
    внутри, одно снаружи.
    """
    ring1 = create_simple_ring(radius, num_points)

    ring2 = create_simple_ring(radius, num_points)
    # Поворот вокруг оси x: плоскость xy -> xz
    rotation = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
    ring2 = ring2 @ rotation.T
    ring2[:, 0] += separation

    return ring1, ring2


if __name__ == "__main__":
    # Smoke test
    print("Topology utils loaded successfully")

    # Test 1: простое кольцо
    ring = create_simple_ring()
    print(f"Created ring with {len(ring)} points")

    # Test 2: Hopf link
    ring1, ring2 = create_linked_rings()
    lk = gauss_linking_integral(ring1, ring2)
    print(f"Hopf link Lk ≈ {lk:.2f} (expected ≈ 1)")

    # Test 3: complexity
    state = TopologicalState(
        num_knots=0,
        num_catenanes=1,
        linking_numbers=[1],
        supercoiling=[0.05, -0.03],
        complexity=0.0,
    )
    C = calculate_complexity(
        state.num_knots, state.num_catenanes, state.linking_numbers, state.supercoiling
    )
    print(f"Topological complexity C = {C:.3f}")
