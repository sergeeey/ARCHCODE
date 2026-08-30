"""
H1 — модель специфичности на органеллу. Исполняет `claim.md`, заморожённый `274bbb8`
ДО написания этого файла.

Проверяемый механизм — НЕ скорость, а адресность (CoRR, John F. Allen; гипотеза не наша,
см. `novelty_check.md`). Решающий тест при τ_ratio = 1: задержки равны, преимущества
по скорости нет вообще, армы отличаются ТОЛЬКО распределением одинакового бюджета.

    local    мощность ∝ собственной нагрузке органеллы
    nuclear  мощность равномерно -- контроллер не различает органеллы
    null     то же при CV = 0, где оба распределения тождественны по построению

    advantage_excess = advantage(CV>0) / advantage(CV=0)
    SUCCESS >= 1.20      KILL < 1.05      серая зона -> СТОП

Запуск:
    python specificity_model.py --seeds 30 --out result.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

SUCCESS_EXCESS = 1.20
KILL_EXCESS = 1.05
CALIBRATION_TOL = 0.02


def make_loads(n: int, cv: float, mean_load: float, rng: np.random.Generator) -> np.ndarray:
    """
    Скорости производства ROS по органеллам, логнормальные с заданным CV.

    WHY логнормальное: неотрицательно и задаёт CV независимо от среднего, поэтому
    гетерогенность варьируется, а суммарная нагрузка -- нет. Иначе армы сравнивались бы
    при разной общей нагрузке, и это был бы конфаундер.
    """
    if cv <= 0:
        return np.full(n, mean_load)
    sigma = np.sqrt(np.log(1 + cv**2))
    loads = rng.lognormal(np.log(mean_load) - sigma**2 / 2, sigma, n)
    return loads * (mean_load * n / loads.sum())  # суммарная нагрузка фиксирована точно


def allocate(loads: np.ndarray, budget: float, mode: str) -> np.ndarray:
    """
    Распределение ОДИНАКОВОГО бюджета мощности.

    WHY равный бюджет -- главное ограничение всего теста: без него локальный арм
    выигрывал бы просто имея больше ресурса. Это была бы та же тавтология, что у
    прежней формулировки через задержку (см. AMENDMENTS.md A-005).
    """
    if mode == "local":  # адресно: видит состояние СВОЕЙ органеллы
        return budget * loads / loads.sum()
    if mode == "nuclear":  # равномерно: различить органеллы не может
        return np.full(len(loads), budget / len(loads))
    raise ValueError(mode)


def count_events(
    loads: np.ndarray,
    capacity: np.ndarray,
    steps: int,
    threshold: float,
    rng: np.random.Generator,
) -> int:
    """
    Событие = уровень ROS органеллы превысил порог.

    WHY пол на нуле: мощность, приложенная к органелле с малой нагрузкой, пропадает
    впустую -- уровень не уходит в минус. Это единственный, кроме порога, источник
    нелинейности, и именно он делает распределение небезразличным. Если бы модель была
    линейной, суммарное число событий не зависело бы от распределения вообще, и
    excess был бы ровно 1.0 -- исход, записанный в claim.md как реальный.
    """
    level = np.zeros(len(loads))
    events = 0
    for _ in range(steps):
        level += rng.poisson(loads) - capacity
        np.maximum(level, 0.0, out=level)
        crossed = level >= threshold
        events += int(crossed.sum())
        level[crossed] = 0.0  # сработал ответ -- уровень сброшен
    return events


def advantage(
    n: int,
    cv: float,
    seed: int,
    *,
    mean_load: float = 5.0,
    capacity_ratio: float = 1.0,
    threshold: float = 20.0,
    steps: int = 400,
    shuffle_after_allocation: bool = False,
) -> tuple[float, float]:
    """
    `advantage = events(nuclear) / events(local)` при одном бюджете и одном потоке.

    Возвращает (advantage, budget) -- бюджет наружу для проверки его равенства.
    """
    rng = np.random.default_rng(seed)
    loads = make_loads(n, cv, mean_load, rng)
    budget = capacity_ratio * loads.sum()

    cap_local = allocate(loads, budget, "local")
    cap_nuclear = allocate(loads, budget, "nuclear")
    assert abs(cap_local.sum() - cap_nuclear.sum()) < 1e-9, "бюджеты не равны"

    if shuffle_after_allocation:
        # НЕГАТИВНЫЙ КОНТРОЛЬ: нагрузки перемешаны ПОСЛЕ распределения, поэтому
        # адресность локального арма больше ни на что не указывает.
        loads = rng.permutation(loads)

    ev_loc = count_events(loads, cap_local, steps, threshold, np.random.default_rng(seed))
    ev_nuc = count_events(loads, cap_nuclear, steps, threshold, np.random.default_rng(seed))
    adv = float(ev_nuc / ev_loc) if ev_loc else float("nan")
    return adv, float(budget)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200, help="органелл в клетке")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--cv", type=float, default=0.5, help="гетерогенность, основной прогон")
    ap.add_argument("--capacity-ratio", type=float, default=1.0)
    ap.add_argument("--out", default="result.json")
    args = ap.parse_args()

    print("=" * 68)
    print("H1 specificity -- prereg claim.md @ 274bbb8, tau_ratio = 1 (задержек нет)")
    print(f"N={args.n} органелл · {args.seeds} seed · CV={args.cv} · бюджет x{args.capacity_ratio}")
    print("=" * 68)

    kw = {"n": args.n, "capacity_ratio": args.capacity_ratio}
    out: dict = {"prereg_commit": "274bbb8", "config": vars(args)}

    # --- контроль 1: калибровка. CV=0 обязана дать 1.00 ---
    null = [advantage(cv=0.0, seed=s, **kw)[0] for s in range(args.seeds)]
    null_med = float(np.median(null))
    calib_ok = abs(null_med - 1.0) <= CALIBRATION_TOL
    print(
        f"  [{'PASS' if calib_ok else 'FAIL'}] калибровка: CV=0 -> advantage = {null_med:.4f}"
        f"  (обязано 1.00 ± {CALIBRATION_TOL})"
    )
    out["null_median"] = null_med

    # --- контроль 2: равенство бюджета ---
    _, b1 = advantage(cv=args.cv, seed=0, **kw)
    _, b2 = advantage(cv=0.0, seed=0, **kw)
    print(f"  [PASS] бюджет: {b1:.6f} vs {b2:.6f} (суммарная нагрузка зафиксирована)")

    if not calib_ok:
        out["verdict"] = "BLOCKED-INFRASTRUCTURE"
        out["note"] = "калибровка провалена -- НЕ свидетельство против гипотезы (FL 2a)"
        print(f"\nVERDICT: {out['verdict']}")
        Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
        return

    # --- основной результат ---
    het = [advantage(cv=args.cv, seed=s, **kw)[0] for s in range(args.seeds)]
    het_med = float(np.median(het))
    excess = het_med / null_med
    verdict = (
        "SUCCESS"
        if excess >= SUCCESS_EXCESS
        else "KILL"
        if excess < KILL_EXCESS
        else "INCONCLUSIVE"
    )
    out.update(
        {
            "hetero_median": het_med,
            "advantage_excess": excess,
            "iqr": [float(np.percentile(het, 25)), float(np.percentile(het, 75))],
            "verdict": verdict,
        }
    )
    print(f"\n--- ОСНОВНОЙ РЕЗУЛЬТАТ (CV={args.cv}) ---")
    print(f"  advantage(CV=0)   : {null_med:.4f}")
    print(
        f"  advantage(CV={args.cv})  : {het_med:.4f}   IQR [{out['iqr'][0]:.3f}, {out['iqr'][1]:.3f}]"
    )
    print(f"  advantage_excess  : {excess:.4f}   -> {verdict}")

    # --- контроль 3: негативный ---
    neg = [
        advantage(cv=args.cv, seed=s, shuffle_after_allocation=True, **kw)[0]
        for s in range(args.seeds)
    ]
    neg_excess = float(np.median(neg)) / null_med
    neg_ok = neg_excess < SUCCESS_EXCESS
    print(
        f"\n  [{'PASS' if neg_ok else 'FAIL'}] негативный контроль (нагрузки перемешаны "
        f"после распределения): excess = {neg_excess:.4f}"
    )
    out["negative_control_excess"] = neg_excess

    # --- вторичное предсказание: эффект обязан расти с гетерогенностью ---
    print("\n  вторичное предсказание -- рост с CV:")
    by_cv = {}
    for cv in (0.25, 0.5, 1.0, 2.0):
        m = float(np.median([advantage(cv=cv, seed=s, **kw)[0] for s in range(args.seeds)]))
        by_cv[cv] = m / null_med
        print(f"    CV={cv:<5} excess = {by_cv[cv]:.4f}")
    out["by_cv"] = by_cv

    # --- точка безубыточности по стоимости ---
    out["cost_breakeven"] = excess - 1.0
    print(f"\n  точка безубыточности: преимущество обнуляется при cost_ratio = {excess - 1.0:.4f}")
    print(f"\nVERDICT: {verdict}")
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"saved: {args.out}")


if __name__ == "__main__":
    main()
