"""
R6 — переопределение метрики в инвариантных единицах.

R7 показал: `noise_breakeven / CV` не равно 1, потому что делит величину типа L1
(индекс Гувера) на меру типа L2 (CV). Замкнутая форма: noise_be = √(2π)·H(s).

Отсюда правильный знаменатель — не CV, а сама предсказанная величина:

    R6_ratio = noise_breakeven / (√(2π) · H(s))

При N = ∞ это тождественно 1 ПО ПОСТРОЕНИЮ. Вопрос — что останется в симуляции.
Остаток и есть чистый вклад конечного N, порога и шагов, без наложенного артефакта
нормировки.

НОВЫХ ПРОГОНОВ НЕТ: считается на 64 кривых, персистированных R3.
Это и есть польза от того, что R3 их сохранил, а run_r2.py выбрасывал.

Запуск: python run_r6.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from analytic_r7 import SQRT_2PI, hoover_lognormal

CV_GRID = (0.25, 0.5, 1.0, 2.0)


def breakeven_from_curve(curve) -> float | None:
    for (n1, a1), (n2, a2) in zip(curve[:-1], curve[1:], strict=False):
        if a1 >= 1.0 > a2:
            f = (a1 - 1.0) / (a1 - a2)
            return float(np.exp(np.log(n1) + f * (np.log(n2) - np.log(n1))))
    return None


def spread(vals) -> float:
    v = [x for x in vals if x is not None and np.isfinite(x)]
    if len(v) != len(vals):
        return float("nan")
    return float(max(abs(x - v[0]) / v[0] for x in v))


r3 = json.loads(Path("result_r3.json").read_text(encoding="utf-8"))
print("=" * 78)
print("R6 — та же величина в единицах Гувера вместо CV. Новых прогонов НЕТ.")
print("=" * 78)
print(f"{'конфигурация':>34} {'разброс /CV':>12} {'разброс /√(2π)H':>17}  изменение")

out: dict = {"denominator": "sqrt(2*pi) * H(s)", "source": "result_r3.json curves"}
rows = {}
for key in r3["configs"]:
    for half in ("A", "B"):
        old_r, new_r = [], []
        for cv in CV_GRID:
            c = r3["curves"].get(f"{key}|{half}|CV{cv}")
            be = breakeven_from_curve(c) if c else None
            old_r.append(be / cv if be else None)
            new_r.append(be / (SQRT_2PI * hoover_lognormal(cv)) if be else None)
        rows[f"{key}|{half}"] = {
            "old_spread": spread(old_r), "new_spread": spread(new_r),
            "new_ratios": new_r,
        }
    a = rows[f"{key}|A"]
    o, n = a["old_spread"], a["new_spread"]
    delta = "—" if not (np.isfinite(o) and np.isfinite(n)) else (
        f"{'-' if n < o else '+'}{abs(n-o):.1%}")
    print(f"{key:>34} {o:>11.1%} {n:>16.1%}  {delta}")
out["rows"] = rows

base = rows["events|clip|lognormal|A"]
print("-" * 78)
print("  БАЗОВАЯ конфигурация:")
print(f"    в единицах CV      : разброс {base['old_spread']:.1%}")
print(f"    в единицах Гувера  : разброс {base['new_spread']:.1%}")
print("    новые отношения    : " + " / ".join(
    f"{x:.3f}" if x else "  —  " for x in base["new_ratios"]))
imp = base["old_spread"] - base["new_spread"]
print(f"\n  {'МЕТРИКА СТАЛА УСТОЙЧИВЕЕ' if imp > 0 else 'МЕТРИКА НЕ УЛУЧШИЛАСЬ'}: "
      f"{base['old_spread']:.1%} -> {base['new_spread']:.1%}")
out["baseline_improvement"] = float(imp)

Path("result_r6.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("\nsaved: result_r6.json")
