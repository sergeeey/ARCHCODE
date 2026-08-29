"""
Настоящая операция strand passage: локальная геометрия, меняющая linking number.

ЗАЧЕМ ЭТОТ МОДУЛЬ СУЩЕСТВУЕТ
----------------------------
В `toy_model.py` «passage» был случайной трансляцией кольца на 0.2 (строка 211).
Такая операция не меняет топологию -- она только перемешивает конфигурацию. Из-за этого
метрика `advantage_score` вознаграждала модели, которые двигаются РЕЖЕ, а не те, которые
упрощают топологию (диагноз: `experiments/t2_top2_annealing/ORACLE_INADEQUACY.md`,
принято passages 29/500 против 233/500 при одинаково нулевом упрощении).

Здесь passage выполняется физически: дуга одного кольца протаскивается сквозь другое
в точке ближайшего сближения. Изменение Lk -- СЛЕДСТВИЕ этой операции, а не постулат.
Поэтому оно поддаётся проверке: `verify_passage` сравнивает Lk до и после и сообщает,
получилось ли ±1. Операция, которая не сработала, обязана быть видимой, а не молча
засчитанной.

ФИЗИКА
------
Два сегмента разных колец в точке сближения образуют перекрёсток. Его знак:

    s = sign( d . (t1 x t2) ),   d = b - a  -- вектор сближения, t1,t2 -- касательные

Это тот же знак, что стоит под интегралом Гаусса. Протаскивание дуги на другую сторону
меняет знак перекрёстка, то есть меняет Lk на ±1.

ОГРАНИЧЕНИЕ (честно)
--------------------
[WEAK] Дискретные кольца из 50 точек -- грубое приближение. Для части конфигураций
операция даст dLk = 0 или |dLk| > 1 (дуга задела соседние сегменты). Это НЕ прячется:
`apply_passage` возвращает фактическое dLk, вызывающий обязан проверить. Доля неудач --
отдельная выходная метрика, а не скрытый шум.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from topology_utils_fast import gauss_linking_integral_vec

_EPS = 1e-12


@dataclass(frozen=True)
class Crossing:
    """Точка ближайшего сближения двух колец -- кандидат на strand passage."""

    idx1: int  # индекс сегмента на кольце 1
    idx2: int  # индекс сегмента на кольце 2
    distance: float
    sign: int  # +1 / -1 -- знак перекрёстка
    angle: float  # угол между касательными, радианы [0, pi]
    separation: np.ndarray  # вектор от кольца 1 к кольцу 2, shape (3,)


def find_closest_crossing(ring1: np.ndarray, ring2: np.ndarray) -> Crossing:
    """
    Найти точку ближайшего сближения между кольцами.

    WHY: оригинал жёстко брал `crossing_point = 0` (`toy_model.py:195,198`) -- всегда
    нулевую точку, независимо от геометрии. Из-за этого ветка кривизны в
    `strand_passage_curvature_bias` попадала под guard `if i < 2: return p_angle`
    и модель "angle+curvature" была побитовым дубликатом "angle".
    """
    p1 = ring1[:-1]
    p2 = ring2[:-1]

    diff = p1[:, None, :] - p2[None, :, :]  # (N1-1, N2-1, 3)
    dist = np.sqrt(np.einsum("ijk,ijk->ij", diff, diff))

    i, j = np.unravel_index(int(np.argmin(dist)), dist.shape)

    t1 = ring1[i + 1] - ring1[i]
    t2 = ring2[j + 1] - ring2[j]
    sep = ring2[j] - ring1[i]  # направление СМЕЩЕНИЯ: от ring1 к ring2

    # WHY: знак перекрёстка обязан следовать конвенции интеграла Гаусса, где
    # подынтегральное выражение использует (r1 - r2) -- см. gauss_linking_integral_vec,
    # `diff = p1 - p2`. Вектор смещения `sep` направлен наоборот (r2 - r1), поэтому для
    # знака берётся -sep. Без этого знак систематически инвертирован относительно Lk.
    #
    # Найдено гейтом G3 (2026-08-29): оракул принимал 0 из 381 passage, потому что для
    # каждой зацепленной пары Lk = -1.00, а sign выдавал +1 -- условие sign == sign(Lk)
    # не выполнялось никогда. Пинится тестом test_crossing_sign_matches_linking_sign.
    triple = float(np.dot(-sep, np.cross(t1, t2)))
    sign = 1 if triple >= 0 else -1

    n1 = np.linalg.norm(t1) + _EPS
    n2 = np.linalg.norm(t2) + _EPS
    cos_angle = float(np.dot(t1, t2) / (n1 * n2))
    angle = float(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    return Crossing(
        idx1=int(i),
        idx2=int(j),
        distance=float(dist[i, j]),
        sign=sign,
        angle=angle,
        separation=sep,
    )


def apply_passage(
    ring1: np.ndarray,
    ring2: np.ndarray,
    crossing: Crossing,
    arc_half_width: int = 4,
) -> tuple[np.ndarray, int]:
    """
    Протащить дугу ring2 сквозь ring1 в точке перекрёстка.

    Дуга ring2 вокруг `crossing.idx2` сдвигается на другую сторону ring1 вдоль вектора
    сближения. Сдвиг спадает косинусом к краям дуги, чтобы кольцо осталось замкнутым и
    гладким -- резкий сдвиг создал бы разрыв, который интеграл Гаусса посчитает как
    ложное зацепление.

    Returns
    -------
    (new_ring2, delta_lk)
        delta_lk -- ФАКТИЧЕСКОЕ изменение округлённого Lk. Ожидается ±1;
        0 или |delta| > 1 означают, что операция не удалась на этой конфигурации.
        Вызывающий обязан это проверить -- см. докстринг модуля.
    """
    lk_before = gauss_linking_integral_vec(ring1, ring2)

    n_pts = len(ring2)
    sep = crossing.separation
    sep_norm = np.linalg.norm(sep)
    if sep_norm < _EPS:
        return ring2.copy(), 0

    # WHY: 2.05x, а не ровно 2x -- нужно гарантированно оказаться ЗА нитью, а не
    # ровно на ней. Точное попадание на нить даёт вырожденную геометрию, где знак
    # перекрёстка не определён.
    direction = sep / sep_norm
    displacement = -direction * (2.05 * sep_norm)

    new_ring2 = ring2.copy()
    center = crossing.idx2

    for offset in range(-arc_half_width, arc_half_width + 1):
        # WHY: кольцо замкнуто -- последняя точка дублирует первую, поэтому индексы
        # берутся по модулю (n_pts - 1), иначе шов разъедется.
        k = (center + offset) % (n_pts - 1)
        taper = float(np.cos(0.5 * np.pi * offset / (arc_half_width + 1)))
        new_ring2[k] = ring2[k] + displacement * taper

    new_ring2[-1] = new_ring2[0]  # сохранить замкнутость

    lk_after = gauss_linking_integral_vec(ring1, new_ring2)
    delta_lk = int(np.round(lk_after) - np.round(lk_before))

    return new_ring2, delta_lk


# WHY: при почти (анти)параллельных касательных t1 x t2 -> 0, перекрёсток вырожден и
# strand passage геометрически не определён. Замер 2026-08-30 (n=286): ВСЕ случаи
# dLk = 0 имели медианный угол 176.9 град (sin ~= 0.05), тогда как успешные ±1 --
# 54.9 и 89.8 град. Порог 0.2 по |sin| отсекает конус ~11.5 град у обоих концов.
MIN_TRANSVERSALITY = 0.2

# Лестница ширин дуги: если passage не дал чистого ±1, пробуем другую ширину, прежде
# чем отказаться. Это поднимает долю применённых passage, не ослабляя требование |dLk|=1.
_ARC_WIDTH_LADDER = (4, 6, 8, 3, 10)


def is_degenerate_crossing(crossing: Crossing) -> bool:
    """Перекрёсток непригоден для passage: касательные почти (анти)параллельны."""
    return abs(np.sin(crossing.angle)) < MIN_TRANSVERSALITY


def attempt_passage(
    ring1: np.ndarray,
    ring2: np.ndarray,
    crossing: Crossing,
) -> tuple[np.ndarray, int, str]:
    """
    Passage с гарантией |dLk| = 1 — «проверь или откати».

    Инвариант: если статус ``applied``, то ``abs(delta_lk) == 1``. Всегда, без оговорок.
    При любом другом исходе возвращается ИСХОДНОЕ кольцо — система никогда не попадает
    в состояние, произведённое сбойной операцией.

    WHY это важнее, чем кажется: в прогоне T2 v2 доля сбоев различалась между армами
    втрое (random 8.00 против angle 2.90 на арм), и именно она, а не выбор правила,
    двигала метрику ``advantage_score``. Пока сбои возможны, сравнение армов измеряет
    частоту поломок, а не топологию (см. ``decision_v2.md``).

    Returns
    -------
    (ring2_out, delta_lk, status)
        status: ``applied`` | ``rejected_degenerate`` | ``rejected_no_clean_passage``
    """
    if is_degenerate_crossing(crossing):
        return ring2, 0, "rejected_degenerate"

    for width in _ARC_WIDTH_LADDER:
        candidate, delta_lk = apply_passage(ring1, ring2, crossing, arc_half_width=width)
        if abs(delta_lk) == 1:
            return candidate, delta_lk, "applied"

    # Ни одна ширина не дала чистого passage -- откат, состояние не меняется.
    return ring2, 0, "rejected_no_clean_passage"


def passage_reduces_linking(crossing: Crossing, current_lk: float) -> bool:
    """
    ЛОКАЛЬНОЕ правило: стоит ли выполнять этот passage.

    Это и есть проверяемое ядро гипотезы T2. Правило использует ТОЛЬКО знак перекрёстка
    (локальная величина) и знак текущего Lk этой пары. Глобальная топология системы
    правилу недоступна -- в этом весь смысл: могут ли локальные правила давать
    глобальное упрощение.

    Убирая перекрёсток, чей знак совпадает со знаком Lk, мы уменьшаем |Lk|.
    """
    if abs(current_lk) < 0.5:
        return False  # нечего упрощать
    return crossing.sign == (1 if current_lk > 0 else -1)


def angle_gate(crossing: Crossing, beta: float = 0.5) -> float:
    """
    Вероятность принятия по углу перекрёстка (модель 2 оригинала, сохранена).

    [HYPOTHESIS-T2] TOP2 предпочитает околоперпендикулярные пересечения.
    Формула и β=0.5 -- как в `topology_utils.strand_passage_angle_bias`.
    """
    deviation = abs(crossing.angle - np.pi / 2)
    return float(np.exp(-deviation / beta))
