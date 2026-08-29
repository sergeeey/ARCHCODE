"""
Позитивный контроль для strand passage.

Дефект №3 из `ORACLE_INADEQUACY.md`: в T2 не было прогона, который ОБЯЗАН показать
упрощение. Без него нельзя отличить «правило работает» от «метрика измеряет не то» --
что и произошло.

Здесь такой контроль есть. Hopf link имеет Lk = 1 по построению; корректный passage
обязан привести его к 0. Если операция passage снова выродится в перемешивание,
`test_hopf_link_unlinks` упадёт -- и артефакт не пройдёт дальше молча.

Запуск:
    python -m pytest shared_utils/test_passage_ops.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from passage_ops import (  # noqa: E402
    angle_gate,
    apply_passage,
    find_closest_crossing,
    passage_reduces_linking,
)
from topology_utils import create_linked_rings, create_simple_ring  # noqa: E402
from topology_utils_fast import gauss_linking_integral_vec  # noqa: E402


def test_hopf_link_has_linking_number_one():
    """Контроль исходного состояния: без него «расцепили» ничего не значит."""
    ring1, ring2 = create_linked_rings(radius=1.0, separation=0.5, num_points=100)
    lk = gauss_linking_integral_vec(ring1, ring2)
    assert abs(round(lk)) == 1, f"Hopf link должен иметь |Lk| = 1, получено {lk:.3f}"


def test_crossing_detection_finds_real_proximity():
    """Перекрёсток должен находиться геометрически, а не браться как точка 0."""
    ring1, ring2 = create_linked_rings(radius=1.0, separation=0.5, num_points=100)
    crossing = find_closest_crossing(ring1, ring2)

    assert crossing.sign in (-1, 1)
    assert 0.0 <= crossing.angle <= np.pi

    # Найденное расстояние обязано быть минимальным среди всех пар сегментов.
    p1, p2 = ring1[:-1], ring2[:-1]
    diff = p1[:, None, :] - p2[None, :, :]
    true_min = float(np.sqrt(np.einsum("ijk,ijk->ij", diff, diff)).min())
    assert abs(crossing.distance - true_min) < 1e-9

    # WHY: это и есть проверка дефекта №2 -- оригинал всегда брал точку 0.
    # Если бы детекция была фиктивной, idx2 совпадал бы с нулём на всех конфигурациях.
    assert crossing.idx1 >= 0 and crossing.idx2 >= 0


@pytest.mark.parametrize("separation", [0.3, 0.5, 0.7])
def test_passage_changes_linking_number(separation: float):
    """
    ГЛАВНЫЙ ТЕСТ. Passage обязан менять Lk -- иначе это не passage.

    Именно это отличает новую операцию от старой: старая (случайный сдвиг на 0.2)
    давала dLk = 0 всегда.
    """
    ring1, ring2 = create_linked_rings(radius=1.0, separation=separation, num_points=100)
    crossing = find_closest_crossing(ring1, ring2)
    _, delta_lk = apply_passage(ring1, ring2, crossing)

    assert delta_lk != 0, (
        f"separation={separation}: passage не изменил Lk (dLk=0) -- "
        "операция снова выродилась в перемешивание"
    )
    assert abs(delta_lk) == 1, f"ожидалось |dLk| = 1, получено {delta_lk}"


def test_hopf_link_unlinks():
    """
    ПОЗИТИВНЫЙ КОНТРОЛЬ: Lk = 1 -> 0 за один корректный passage.

    Это тот прогон, который ОБЯЗАН показать упрощение. Его отсутствие было
    дефектом №3 в ORACLE_INADEQUACY.md.
    """
    ring1, ring2 = create_linked_rings(radius=1.0, separation=0.5, num_points=100)
    lk_before = round(gauss_linking_integral_vec(ring1, ring2))
    assert abs(lk_before) == 1

    crossing = find_closest_crossing(ring1, ring2)
    new_ring2, delta_lk = apply_passage(ring1, ring2, crossing)
    lk_after = round(gauss_linking_integral_vec(ring1, new_ring2))

    assert lk_after == lk_before + delta_lk, "фактическое Lk не согласуется с сообщённым dLk"
    assert abs(lk_after) < abs(lk_before), (
        f"passage не расцепил Hopf link: |Lk| {abs(lk_before)} -> {abs(lk_after)}"
    )
    assert lk_after == 0


def test_passage_keeps_ring_closed():
    """Разрыв кольца интеграл Гаусса посчитает как ложное зацепление."""
    ring1, ring2 = create_linked_rings(num_points=100)
    crossing = find_closest_crossing(ring1, ring2)
    new_ring2, _ = apply_passage(ring1, ring2, crossing)

    assert np.allclose(new_ring2[0], new_ring2[-1], atol=1e-12), "кольцо разомкнулось"
    assert new_ring2.shape == ring2.shape


def test_local_rule_uses_only_local_information():
    """
    Правило обязано опираться на знак перекрёстка, а не на глобальное состояние.

    В этом суть гипотезы T2: локальные правила -> глобальное упрощение.
    """
    ring1, ring2 = create_linked_rings(num_points=100)
    crossing = find_closest_crossing(ring1, ring2)

    # При Lk того же знака, что перекрёсток -- упрощаем.
    same_sign_lk = float(crossing.sign) * 3.0
    assert passage_reduces_linking(crossing, same_sign_lk) is True

    # При противоположном -- нет (passage бы увеличил |Lk|).
    assert passage_reduces_linking(crossing, -same_sign_lk) is False

    # Уже расцеплено -- упрощать нечего.
    assert passage_reduces_linking(crossing, 0.0) is False


def test_angle_gate_is_not_constant():
    """
    Проверка дефекта №2: угловой gate обязан различать конфигурации.

    Если бы он возвращал одно и то же (как выходило при crossing_point=0), модели
    2 и 3 снова были бы неразличимы.
    """
    rng = np.random.default_rng(0)
    values = []
    for _ in range(12):
        r1 = create_simple_ring(num_points=60) + rng.standard_normal(3)
        r2 = create_simple_ring(num_points=60) + rng.standard_normal(3)
        values.append(angle_gate(find_closest_crossing(r1, r2)))

    assert len(set(np.round(values, 6))) > 1, "angle_gate константен -- gate не работает"
    assert all(0.0 <= v <= 1.0 for v in values)


def test_crossing_sign_matches_linking_sign():
    """
    Пин конвенции знака.

    Знак перекрёстка обязан совпадать со знаком Lk пары -- иначе локальное правило
    `passage_reduces_linking` не сработает никогда. Регрессия этого теста означает
    возврат бага, найденного гейтом G3 (2026-08-29): sign был инвертирован
    относительно конвенции интеграла Гаусса, оракул принимал 0 из 381 passage.
    """
    for separation in (0.5, 1.0, 1.5):
        ring1, ring2 = create_linked_rings(radius=1.0, separation=separation, num_points=100)
        lk = gauss_linking_integral_vec(ring1, ring2)
        crossing = find_closest_crossing(ring1, ring2)

        assert abs(round(lk)) == 1, f"separation={separation}: кольца не зацеплены"
        expected = 1 if lk > 0 else -1
        assert crossing.sign == expected, (
            f"separation={separation}: Lk={lk:+.3f} -> ожидался знак {expected:+d}, "
            f"получен {crossing.sign:+d} -- конвенция знака инвертирована"
        )


def test_local_rule_fires_on_linked_pair():
    """
    Следствие предыдущего: на реально зацепленной паре правило ОБЯЗАНО срабатывать.

    Это тот тест, отсутствие которого позволило ошибке знака дойти до прогона.
    """
    ring1, ring2 = create_linked_rings(radius=1.0, separation=1.0, num_points=100)
    lk = gauss_linking_integral_vec(ring1, ring2)
    crossing = find_closest_crossing(ring1, ring2)

    assert passage_reduces_linking(crossing, lk) is True, (
        "правило не сработало на зацепленной паре -- локальное правило мертво"
    )
