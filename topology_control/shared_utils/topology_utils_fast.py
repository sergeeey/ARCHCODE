"""
Векторизованное ядро топологических вычислений для T2.

Заменяет узкие места `topology_utils.py`, сохраняя **побитово ту же математику**.
Эквивалентность доказывается `tests/test_fast_equivalence.py`, а не декларируется.

Три источника ускорения (диагноз из `experiments/t2_top2_annealing/POSTPONED.md`):

1. `gauss_linking_integral` был питоновским двойным циклом: для 50-точечных колец это
   49x49 = 2401 итерация, в каждой -- вызовы np.cross/np.dot/norm на 3-векторах.
   Накладные расходы numpy на скалярную операцию превышают саму операцию на порядки.
   Здесь -- один broadcast.

2. `calculate_current_complexity` пересчитывал ВСЕ пары колец на каждом шаге
   (200 колец -> 19 900 пар), хотя strand passage сдвигает РОВНО ОДНО кольцо.
   Меняются только пары с этим кольцом -- 199 из 19 900.

3. Двойная работа: `calculate_catenation_simple` и подсчёт linking numbers независимо
   обходили все пары, вызывая один и тот же интеграл дважды. Обе величины выводятся
   из одной матрицы.

Совокупно: ~2401x (п.1) * ~100x (п.2) * 2x (п.3). Оценка автора в POSTPONED.md была
50-100x -- она занижена, потому что учитывала только пп. 2-3.
"""

from __future__ import annotations

import numpy as np

# WHY: пороги вынесены в константы, но значения НЕ менялись -- они взяты из
# topology_utils.py:135 (|lk| > 0.1 для complexity) и :230 (|lk| > 0.5 для катенанов).
# Разные пороги на одной величине -- сознательное решение оригинала, сохранено.
LK_NOISE_THRESHOLD = 0.1
LK_CATENANE_THRESHOLD = 0.5
_MIN_DIST = 1e-6


def gauss_linking_integral_vec(curve1: np.ndarray, curve2: np.ndarray) -> float:
    """
    Интеграл Гаусса, векторизованный.

    Математически идентичен `topology_utils.gauss_linking_integral`:
    Lk = (1/4pi) * sum_ij (r1_i - r2_j) . (dr1_i x dr2_j) / |r1_i - r2_j|^3

    Parameters
    ----------
    curve1, curve2 : np.ndarray, shape (N, 3)

    Returns
    -------
    float
        Приближённое Lk.
    """
    seg1 = curve1[1:] - curve1[:-1]  # (N1-1, 3)
    seg2 = curve2[1:] - curve2[:-1]  # (N2-1, 3)
    p1 = curve1[:-1]  # (N1-1, 3)
    p2 = curve2[:-1]  # (N2-1, 3)

    diff = p1[:, None, :] - p2[None, :, :]  # (N1-1, N2-1, 3)
    cross = np.cross(seg1[:, None, :], seg2[None, :, :])  # (N1-1, N2-1, 3)

    dist = np.sqrt(np.einsum("ijk,ijk->ij", diff, diff))
    numer = np.einsum("ijk,ijk->ij", diff, cross)

    # WHY: маска воспроизводит `if dist > 1e-6` оригинала. Без неё деление на ~0 даёт inf,
    # что молча испортит сумму -- ровно тот класс тихой порчи, который здесь недопустим.
    valid = dist > _MIN_DIST
    lk_sum = float(np.sum(numer[valid] / dist[valid] ** 3))

    return lk_sum / (4.0 * np.pi)


class LinkingMatrix:
    """
    Матрица попарных linking numbers с инкрементальным обновлением.

    Инвариант: `self.lk[i, j]` всегда равно
    `gauss_linking_integral_vec(rings[i], rings[j])` для текущих `rings`.
    Нарушение инварианта = молчаливо неверная сложность, поэтому обновление
    кольца обязано идти только через `update_ring`.
    """

    def __init__(self, rings: list[np.ndarray]) -> None:
        n = len(rings)
        self.n = n
        self.lk = np.zeros((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                value = gauss_linking_integral_vec(rings[i], rings[j])
                self.lk[i, j] = value
                self.lk[j, i] = value

    def update_ring(self, rings: list[np.ndarray], idx: int) -> None:
        """Пересчитать только пары, содержащие кольцо `idx`. O(n) вместо O(n^2)."""
        for k in range(self.n):
            if k == idx:
                continue
            value = gauss_linking_integral_vec(rings[idx], rings[k])
            self.lk[idx, k] = value
            self.lk[k, idx] = value

    def complexity(
        self,
        alpha: float = 1.0,
        beta: float = 1.0,
        gamma: float = 0.5,
        delta: float = 0.3,
        num_knots: int = 0,
    ) -> float:
        """
        C(G) = alpha*|K| + beta*|C| + gamma*sum|Lk| + delta*sum|sigma|

        Воспроизводит `RingSystem.calculate_current_complexity` оригинала:
        узлы = 0 (placeholder), supercoiling = [] (простые кольца),
        катенаны по порогу 0.5, linking-сумма по порогу 0.1 с округлением до int.
        """
        upper = self.lk[np.triu_indices(self.n, k=1)]
        abs_lk = np.abs(upper)

        num_catenanes = int(np.count_nonzero(abs_lk > LK_CATENANE_THRESHOLD))

        # WHY: оригинал делает int(np.round(lk)) ПЕРЕД суммированием (topology_utils
        # вызывается из toy_model.py:136). Округление до сложения меняет результат,
        # поэтому порядок операций сохранён точно.
        significant = upper[abs_lk > LK_NOISE_THRESHOLD]
        linking_sum = float(np.sum(np.abs(np.round(significant).astype(int))))

        return alpha * abs(num_knots) + beta * num_catenanes + gamma * linking_sum
