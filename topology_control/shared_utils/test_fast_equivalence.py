"""
Доказательство эквивалентности быстрого ядра оригиналу.

Смысл: ускорение, меняющее результат, -- это не оптимизация, а подмена эксперимента.
Пре-регистрация T2 привязана к конкретной математике; ускоренная версия обязана
воспроизводить её, а не «примерно то же самое».

Запуск:
    python -m pytest shared_utils/test_fast_equivalence.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from topology_utils import (  # noqa: E402
    calculate_catenation_simple,
    calculate_complexity,
    create_linked_rings,
    create_simple_ring,
    gauss_linking_integral,
)
from topology_utils_fast import LinkingMatrix, gauss_linking_integral_vec  # noqa: E402

# WHY: 1e-9 -- обе реализации суммируют одни и те же слагаемые, различие только в порядке
# накопления с плавающей точкой. Более слабый допуск скрыл бы реальное расхождение формул.
TOL = 1e-9


def _random_ring(rng: np.random.Generator, num_points: int = 50) -> np.ndarray:
    ring = create_simple_ring(radius=1.0, num_points=num_points)
    return ring + rng.standard_normal(3) * 2.0


def test_linking_integral_matches_on_hopf_link():
    """Контроль с известным ответом: Hopf link имеет Lk = 1."""
    ring1, ring2 = create_linked_rings()
    slow = gauss_linking_integral(ring1, ring2)
    fast = gauss_linking_integral_vec(ring1, ring2)
    assert abs(slow - fast) < TOL, f"расхождение на Hopf link: {slow} vs {fast}"


@pytest.mark.parametrize("seed", [0, 1, 42, 2026])
def test_linking_integral_matches_on_random_pairs(seed: int):
    """Случайные пары колец -- основная проверка формулы."""
    rng = np.random.default_rng(seed)
    for _ in range(5):
        c1, c2 = _random_ring(rng), _random_ring(rng)
        slow = gauss_linking_integral(c1, c2)
        fast = gauss_linking_integral_vec(c1, c2)
        assert abs(slow - fast) < TOL, f"seed={seed}: {slow} vs {fast}"


def test_linking_integral_handles_coincident_curves():
    """Совпадающие кривые -- ветка dist <= 1e-6, где оригинал пропускает слагаемые."""
    ring = create_simple_ring(num_points=30)
    slow = gauss_linking_integral(ring, ring)
    fast = gauss_linking_integral_vec(ring, ring)
    assert abs(slow - fast) < TOL
    assert np.isfinite(fast), "маска dist>1e-6 не сработала -- получен inf/nan"


def test_complexity_matches_original_pipeline():
    """
    Полная сложность C(G): матрица против оригинального двойного прохода.

    Оригинал (toy_model.py:128-149) считает катенаны и linking-сумму двумя
    независимыми обходами всех пар. Быстрая версия выводит обе из одной матрицы.
    """
    rng = np.random.default_rng(7)
    rings = [_random_ring(rng) for _ in range(12)]

    num_catenanes = calculate_catenation_simple(rings)
    linking_numbers = []
    for i in range(len(rings)):
        for j in range(i + 1, len(rings)):
            lk = gauss_linking_integral(rings[i], rings[j])
            if abs(lk) > 0.1:
                linking_numbers.append(int(np.round(lk)))
    slow_c = calculate_complexity(
        num_knots=0,
        num_catenanes=num_catenanes,
        linking_numbers=linking_numbers,
        supercoiling=[],
    )

    fast_c = LinkingMatrix(rings).complexity()

    assert abs(slow_c - fast_c) < TOL, f"C(G) расходится: {slow_c} vs {fast_c}"


def test_incremental_update_equals_full_recompute():
    """
    Ключевой инвариант оптимизации №2.

    После сдвига одного кольца инкрементальное обновление обязано дать ту же матрицу,
    что полный пересчёт. Если нет -- сложность поедет незаметно, и траектория
    эксперимента разойдётся с оригиналом молча.
    """
    rng = np.random.default_rng(11)
    rings = [_random_ring(rng) for _ in range(10)]

    matrix = LinkingMatrix(rings)
    idx = 4
    rings[idx] = rings[idx] + rng.standard_normal(3) * 0.2
    matrix.update_ring(rings, idx)

    full = LinkingMatrix(rings)

    assert np.allclose(matrix.lk, full.lk, atol=TOL), "инкрементальное обновление разошлось"
    assert abs(matrix.complexity() - full.complexity()) < TOL


def test_matrix_symmetry_and_zero_diagonal():
    """Структурный инвариант: Lk(i,j) = Lk(j,i), диагональ не используется."""
    rng = np.random.default_rng(3)
    rings = [_random_ring(rng) for _ in range(6)]
    matrix = LinkingMatrix(rings)

    assert np.allclose(matrix.lk, matrix.lk.T, atol=TOL)
    assert np.allclose(np.diag(matrix.lk), 0.0)
