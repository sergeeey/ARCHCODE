"""
H1 R2 — исполняет `claim_r2.md`, заморожённый `3374774` ДО написания этого файла.

Объясняем: почему `noise_breakeven / CV_pop` систематически < 1 и падает с CV
(1.003 / 0.980 / 0.884 / 0.732), тогда как структура даёт 1.0 везде.

H_A: ошибка локального арма МУЛЬТИПЛИКАТИВНА, то есть сцеплена с нагрузкой органеллы,
а ошибка ядерного -- нет. При тяжёлом хвосте это бьёт по локальному сильнее.
Тест: аддитивный шум расцепляет ошибку с нагрузкой и обязан убрать эффект.

    SUCCESS  аддитивный разброс <= 10% И мультипликативный > 10%
    KILL     аддитивный тоже > 10%
    серая    оба <= 10% -> стоп и доклад

Запуск: python run_r2.py --seeds 30 --out result_r2.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from run_r1 import CV_GRID, MEAN_LOAD, NOISE_GRID, STEPS, THRESHOLD, N
from specificity_model import count_events, make_loads

TOLERANCE = 0.10


def advantage(cv: float, seed: int, noise: float, model: str, ratio: float = 1.0) -> float:
    """`events(nuclear)/events(local)`. `model` -- как шумит сенсор локального арма."""
    rng = np.random.default_rng(seed)
    loads = make_loads(N, cv, MEAN_LOAD, rng)
    budget = ratio * loads.sum()

    if noise <= 0:
        sensed = loads.copy()
    elif model == "mult":
        s = np.sqrt(np.log(1 + noise**2))
        sensed = loads * rng.lognormal(-(s**2) / 2, s, N)
    elif model == "add":
        # WHY аддитивный: ошибка НЕ масштабируется с нагрузкой -- ровно то сцепление,
        # которое H_A называет причиной. Масштаб задан средней нагрузкой, чтобы
        # относительный разброс оценки в среднем по популяции совпадал с mult.
        sensed = loads + rng.normal(0.0, noise * MEAN_LOAD, N)
        sensed = np.maximum(sensed, 1e-6)
    else:
        raise ValueError(model)

    cap_l = budget * sensed / sensed.sum()
    cap_n = np.full(N, budget / N)
    assert abs(cap_l.sum() - cap_n.sum()) < 1e-9
    el = count_events(loads, cap_l, STEPS, THRESHOLD, np.random.default_rng(seed))
    en = count_events(loads, cap_n, STEPS, THRESHOLD, np.random.default_rng(seed))
    return float(en / el) if el else float("nan")


def breakeven(cv: float, seeds: int, model: str) -> float | None:
    curve = [
        (float(nz), float(np.median([advantage(cv, s, nz, model) for s in range(seeds)])))
        for nz in NOISE_GRID
    ]
    for (n1, a1), (n2, a2) in zip(curve[:-1], curve[1:], strict=False):
        if a1 >= 1.0 > a2:
            f = (a1 - 1.0) / (a1 - a2)
            return float(np.exp(np.log(n1) + f * (np.log(n2) - np.log(n1))))
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--out", default="result_r2.json")
    a = ap.parse_args()
    out: dict = {"prereg_commit": "3374774"}

    print("=" * 70)
    print("H1 R2 -- prereg claim_r2.md @ 3374774")
    print("=" * 70)
    calib = float(np.median([advantage(0.0, s, 0.0, "mult") for s in range(a.seeds)]))
    print(f"  [{'PASS' if abs(calib-1) <= 0.02 else 'FAIL'}] калибровка: {calib:.4f}")
    out["calibration"] = calib

    print(f"\n{'CV':>6} {'мультипл. отн.':>16} {'аддитивн. отн.':>16}")
    res: dict[str, dict] = {"mult": {}, "add": {}}
    for cv in CV_GRID:
        row = []
        for m in ("mult", "add"):
            be = breakeven(cv, a.seeds, m)
            r = be / cv if be else float("nan")
            res[m][str(cv)] = {"breakeven": be, "ratio": r}
            row.append(r)
        print(f"{cv:>6} {row[0]:>16.3f} {row[1]:>16.3f}")

    print()
    verdicts = {}
    for m, label in (("mult", "мультипликативный"), ("add", "аддитивный")):
        rs = [res[m][str(cv)]["ratio"] for cv in CV_GRID]
        base = rs[0]  # значение при CV = 0.25, как задано в claim_r2
        spread = float(max(abs(r - base) / base for r in rs))
        verdicts[m] = spread
        flag = "≤10% (эффект отсутствует)" if spread <= TOLERANCE else ">10% (эффект ЕСТЬ)"
        print(f"  {label:>18}: разброс отношения = {spread:6.1%}  {flag}")
    out["spread"] = verdicts

    ok_add = verdicts["add"] <= TOLERANCE
    ok_mult = verdicts["mult"] > TOLERANCE
    verdict = ("SUCCESS" if ok_add and ok_mult
               else "INCONCLUSIVE" if ok_add and not ok_mult else "KILL")
    out["verdict"] = verdict
    print(f"\n  H_A (сцепление ошибки с нагрузкой): {verdict}")
    Path(a.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"saved: {a.out}")


if __name__ == "__main__":
    main()
