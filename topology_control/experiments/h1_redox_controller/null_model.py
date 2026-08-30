"""
Нулевая модель H1 — арм-ПОТОЛОК для критерия «локальное управление лучше ядерного».

WHY этот файл существует: критерий H1 в `KILL_CRITERIA.md` (в редакции 2026-04-25)
удовлетворяется **арифметикой задержки без всякой биологии**. Замер 2026-08-30:

    порог SUCCESS (>1.5) перекрыт уже при tau_ratio = 1.5
    порог KILL   (<1.2) требует tau_ratio < 1.5
    кривая насыщается на 11.01, причём 90% насыщения -- уже при tau_ratio = 8

Поскольку сама гипотеза H1 существует только при tau_ratio >> 1, её собственная
посылка гарантирует её собственный SUCCESS, а условие KILL недостижимо. Это дефект
критерия, а не результат. См. `AMENDMENTS.md` A-005.

Модель СОЗНАТЕЛЬНО не содержит биологии: пуассоновский поток возмущений, контроллер
с задержкой tau, событие = накопление превысило порог. Всё, что реальная модель H1
добавит сверх этого, и есть проверяемое содержание гипотезы.

Использование при построении H1:

    from null_model import advantage, excess_over_null
    exc = excess_over_null(advantage_of_your_model, tau_ratio=..., ...)
    # exc = 1.0 означает: модель не добавила ничего к арифметике задержки

Запуск:
    python null_model.py            # таблица кривой + положение колена
"""

from __future__ import annotations

import numpy as np

DEFAULT_T = 400_000
DEFAULT_RATE = 1.0
DEFAULT_THRESHOLD = 3.0
DEFAULT_TAU_LOCAL = 0.5


def ros_events(
    tau: float,
    *,
    horizon: float = DEFAULT_T,
    rate: float = DEFAULT_RATE,
    threshold: float = DEFAULT_THRESHOLD,
    seed: int = 0,
) -> int:
    """
    Число ROS-событий при задержке контроллера `tau`.

    Событие = за время tau накопилось >= threshold возмущений. Биологии нет: это
    чистое следствие того, что более медленный контроллер пропускает больше.
    """
    rng = np.random.default_rng(seed)
    n = rng.poisson(rate * horizon)
    t = np.sort(rng.uniform(0, horizon, n))
    # сколько возмущений пришло в окне [t_i, t_i + tau)
    load = np.searchsorted(t, t + tau) - np.arange(len(t))
    return int((load >= threshold).sum())


def advantage(tau_ratio: float, *, tau_local: float = DEFAULT_TAU_LOCAL, **kw) -> float:
    """
    `advantage` в точности по формуле H1: ROS_events(nuclear) / ROS_events(local).

    WHY одинаковый seed для обоих армов: сравниваются два контроллера на ОДНОМ потоке
    возмущений. Разные seed добавили бы шум выборки в величину, которая должна
    отражать только разницу задержек.
    """
    local = ros_events(tau_local, **kw)
    nuclear = ros_events(tau_local * tau_ratio, **kw)
    return float(nuclear / local) if local else float("inf")


def excess_over_null(model_advantage: float, tau_ratio: float, **kw) -> float:
    """
    Во сколько раз модель превосходит чистую арифметику задержки при том же tau_ratio.

    Это и есть величина, на которой должен стоять критерий H1 после A-005:
      1.00 -- модель не добавила ничего сверх задержки (гипотезы нет)
      >1   -- есть содержание, не сводимое к «медленнее значит хуже»

    Величина безразмерна и не зависит от параметров нулевой модели, потому что
    числитель и знаменатель берутся при ОДНИХ И ТЕХ ЖЕ параметрах.
    """
    null = advantage(tau_ratio, **kw)
    return float(model_advantage / null) if null else float("nan")


def curve(ratios=(1, 1.5, 2, 3, 5, 8, 12, 20, 35, 60, 100, 200, 500, 1000), **kw):
    return [(r, advantage(r, **kw)) for r in ratios]


def knee(rows, frac: float = 0.9) -> float:
    """Наименьший tau_ratio, при котором достигнуто `frac` от насыщения."""
    xs = np.array([r for r, _ in rows])
    ys = np.array([a for _, a in rows])
    return float(xs[np.argmax(ys >= frac * ys.max())])


def main() -> None:
    rows = curve()
    print("=" * 62)
    print("H1 — НУЛЕВАЯ МОДЕЛЬ (только задержка, биологии нет)")
    print("=" * 62)
    print(f"{'tau_ratio':>10} {'advantage':>11}   вердикт по критерию H1 (редакция 2026-04-25)")
    for r, a in rows:
        v = "SUCCESS" if a > 1.5 else ("KILL" if a < 1.2 else "серая зона")
        print(f"{r:>10} {a:>11.2f}   {v}")
    ys = [a for _, a in rows]
    print("-" * 62)
    print(f"  насыщение              : {max(ys):.2f}")
    print(f"  колено (90% насыщения) : tau_ratio = {knee(rows):g}")
    print(f"  порог SUCCESS перекрыт : tau_ratio = {min(r for r, a in rows if a > 1.5):g}")
    print(f"  порог KILL достижим    : tau_ratio < {min(r for r, a in rows if a >= 1.2):g}")
    print("\n  Вывод: посылка H1 (tau_ratio >> 1) гарантирует её собственный SUCCESS.")
    print("  Критерий не может быть провален -> см. AMENDMENTS.md A-005.")


if __name__ == "__main__":
    main()
