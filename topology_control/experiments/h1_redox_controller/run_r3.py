"""
H1 R3 — факториальная абляция. Исполняет `claim_r3.md`, заморожённый `5a9e6e6`
ДО написания этого файла.

Объясняем остаточные 14.2% разброса отношения `noise_breakeven / CV_pop`.
Исходный кандидат R3 (тяжесть хвоста при конечном N) опровергнут ДО запуска: даёт
0.25-0.53% при нужных 14.2%. Здесь проверяются три конкурента, каждый из которых
измерен пробой роя как двигающий цель СИЛЬНЕЕ объясняемого остатка.

  M0 count_events (порог+шаги)   vs  M1 детерминированный дефицит Σ max(0, λ−cap)
  C0 обрезка на 1e-6             vs  C1 пересэмплирование отрицательных
  F0 логнормаль                  vs  F1 гамма (тот же mean, тот же CV)

Фактор = причина, если его снятие роняет разброс < 5% (УЖЕ объясняемых 14.2%
и уже допуска R2 10%). «Ни один не роняет» — валидный исход, KILL всей тройки.

Запуск: python run_r3.py --out result_r3.json
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
from run_r1 import CV_GRID, MEAN_LOAD, NOISE_GRID, STEPS, THRESHOLD, N
from specificity_model import count_events

CAUSE_THRESHOLD = 0.05
BASELINE_TOL = 0.02
HALVES = {"A": range(30), "B": range(30, 60)}


def make_loads_family(cv: float, rng: np.random.Generator, family: str) -> np.ndarray:
    """
    Нагрузки с ЗАДАННЫМИ средним и CV, из указанного семейства.

    WHY гамма как альтернатива: при одних и тех же mean и CV она отличается от
    логнормали только тяжестью хвоста. Если целевая статистика к этому не инвариантна,
    вопрос «почему отношение != 1» некорректен как поставлен.
    """
    if cv <= 0:
        return np.full(N, MEAN_LOAD)
    if family == "lognormal":
        s = np.sqrt(np.log(1 + cv**2))
        x = rng.lognormal(np.log(MEAN_LOAD) - s**2 / 2, s, N)
    elif family == "gamma":
        k = 1.0 / cv**2  # форма задаёт CV; масштаб — среднее
        x = rng.gamma(k, MEAN_LOAD / k, N)
    else:
        raise ValueError(family)
    return x * (MEAN_LOAD * N / x.sum())  # суммарная нагрузка фиксирована точно


def sense_additive(loads, noise, rng, clip_mode: str) -> np.ndarray:
    """Аддитивный шум оценки + обработка отрицательных значений (фактор C)."""
    if noise <= 0:
        return loads.copy()
    scale = noise * MEAN_LOAD
    sensed = loads + rng.normal(0.0, scale, N)
    if clip_mode == "clip":
        return np.maximum(sensed, 1e-6)
    # C1: пересэмплировать, а не срезать -- убирает одностороннее усечение
    for _ in range(50):
        bad = sensed <= 0
        if not bad.any():
            break
        sensed[bad] = loads[bad] + rng.normal(0.0, scale, int(bad.sum()))
    return np.maximum(sensed, 1e-6)  # страховка после 50 попыток


def advantage(cv, seed, noise, M, C, F, ratio=1.0) -> float:
    rng = np.random.default_rng(seed)
    loads = make_loads_family(cv, rng, F)
    budget = ratio * loads.sum()
    sensed = sense_additive(loads, noise, rng, C)
    cap_l = budget * sensed / sensed.sum()
    cap_n = np.full(N, budget / N)
    assert abs(cap_l.sum() - cap_n.sum()) < 1e-9

    if M == "events":
        el = count_events(loads, cap_l, STEPS, THRESHOLD, np.random.default_rng(seed))
        en = count_events(loads, cap_n, STEPS, THRESHOLD, np.random.default_rng(seed))
    else:  # M1: детерминированный дефицит, без порога и шагов
        el = float(np.maximum(0.0, loads - cap_l).sum())
        en = float(np.maximum(0.0, loads - cap_n).sum())
    return float(en / el) if el else float("nan")


def breakeven(cv, seeds, M, C, F):
    curve = [
        (float(nz), float(np.median([advantage(cv, s, nz, M, C, F) for s in seeds])))
        for nz in NOISE_GRID
    ]
    for (n1, a1), (n2, a2) in zip(curve[:-1], curve[1:], strict=False):
        if a1 >= 1.0 > a2:
            f = (a1 - 1.0) / (a1 - a2)
            return float(np.exp(np.log(n1) + f * (np.log(n2) - np.log(n1)))), curve
    return None, curve


def spread_of(ratios) -> float:
    """Разброс отношения относительно значения при CV=0.25, как в R1/R2."""
    base = ratios[0]
    if base is None or not np.isfinite(base):
        return float("nan")
    vals = [r for r in ratios if r is not None and np.isfinite(r)]
    return float(max(abs(r - base) / base for r in vals)) if len(vals) == len(ratios) else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="result_r3.json")
    a = ap.parse_args()
    out: dict = {"prereg_commit": "5a9e6e6", "configs": {}, "curves": {}}

    print("=" * 76)
    print("H1 R3 — факториальная абляция, prereg claim_r3.md @ 5a9e6e6")
    print("=" * 76)
    print(f"{'M':>7} {'C':>10} {'F':>10} | {'разброс A':>10} {'разброс B':>10} | отношения (CV 0.25/0.5/1/2)")

    for M, C, F in itertools.product(("events", "deficit"), ("clip", "resample"),
                                     ("lognormal", "gamma")):
        key = f"{M}|{C}|{F}"
        row, spreads = {}, {}
        for half, seeds in HALVES.items():
            ratios = []
            for cv in CV_GRID:
                be, curve = breakeven(cv, seeds, M, C, F)
                ratios.append(be / cv if be else None)
                out["curves"][f"{key}|{half}|CV{cv}"] = curve
            spreads[half] = spread_of(ratios)
            row[half] = {"ratios": ratios, "spread": spreads[half]}
        out["configs"][key] = row
        r = row["A"]["ratios"]
        fmt = " / ".join(f"{x:.3f}" if x else "  —  " for x in r)
        print(f"{M:>7} {C:>10} {F:>10} | {spreads['A']:>10.1%} {spreads['B']:>10.1%} | {fmt}")

    base = out["configs"]["events|clip|lognormal"]["A"]["spread"]
    print("-" * 76)
    print(f"  ПОЗИТИВНЫЙ КОНТРОЛЬ: базовая конфигурация даёт {base:.1%} "
          f"(R2 дал 14.2%, допуск ±2 п.п.)  {'PASS' if abs(base-0.142) <= BASELINE_TOL else 'FAIL'}")
    out["positive_control"] = {"spread": base, "pass": bool(abs(base - 0.142) <= BASELINE_TOL)}

    print("\n  ЭФФЕКТ СНЯТИЯ КАЖДОГО ФАКТОРА (половина A):")
    verdicts = {}
    for name, key in (("M снят (дефицит)", "deficit|clip|lognormal"),
                      ("C снят (пересэмпл.)", "events|resample|lognormal"),
                      ("F сменён (гамма)", "events|clip|gamma")):
        s = out["configs"][key]["A"]["spread"]
        v = ("ПРИЧИНА" if s < CAUSE_THRESHOLD else
             "частичный вклад" if s < base - 0.02 else "не при чём")
        verdicts[key] = {"spread": s, "verdict": v}
        print(f"    {name:22s} разброс {s:>7.1%}  (было {base:.1%})  -> {v}")
    out["factor_verdicts"] = verdicts

    causes = [k for k, v in verdicts.items() if v["verdict"] == "ПРИЧИНА"]
    out["verdict"] = ("KILL всей тройки — ни один фактор не роняет ниже 5%" if not causes
                      else f"ПРИЧИНА: {', '.join(causes)}")
    print(f"\n  ВЕРДИКТ: {out['verdict']}")

    # вторичный: воспроизводится ли немонотонность в ОБЕИХ половинах
    b = out["configs"]["events|clip|lognormal"]
    up = [h for h in ("A", "B")
          if all(x is not None for x in b[h]["ratios"]) and b[h]["ratios"][2] > b[h]["ratios"][1]]
    print(f"  вторичный — возврат при CV=1.0 воспроизводится в половинах: {up or 'НИ В ОДНОЙ'}")
    out["nonmonotonic_halves"] = up

    Path(a.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nsaved: {a.out}  (кривые персистированы: {len(out['curves'])} шт.)")


if __name__ == "__main__":
    main()
