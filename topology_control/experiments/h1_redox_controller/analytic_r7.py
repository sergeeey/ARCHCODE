"""
R7 — замкнутая форма отношения `noise_breakeven / CV` при N → ∞.

ВЫВОД (аддитивный шум, детерминированный дефицит, N = ∞):

  Ядерный арм раздаёт μ каждому  ->  дефицит = E[max(0, λ−μ)]
    Поскольку E[λ−μ] = 0, положительная и отрицательная части равны, значит
    E[max(0, λ−μ)] = E|λ−μ|/2 = μ·H,  где H — ИНДЕКС ГУВЕРА.
    Для логнормали:  H(s) = 2Φ(s/2) − 1,  s = √(ln(1+CV²)).

  Локальный арм с аддитивным шумом: sensed = λ + δ, E[δ] = 0, поэтому нормировка
    даёт ровно c = λ + δ  ->  дефицит = E[max(0, −δ)] = σ_δ/√(2π).

  Безубыточность:  μ·H = σ_δ/√(2π),  а σ_δ = noise·μ  =>

      noise_breakeven = √(2π) · H(s)
      отношение       = √(2π) · H(s) / CV          <- ЗАМКНУТАЯ ФОРМА

Симуляции здесь нет вообще. Проверка — сверка формулы с прямым Монте-Карло тех же
величин, а не с прогонами проекта.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import norm

CV_GRID = (0.25, 0.5, 1.0, 2.0)
SQRT_2PI = np.sqrt(2 * np.pi)


def hoover_lognormal(cv: float) -> float:
    """H(s) = 2Φ(s/2) − 1, s = √(ln(1+CV²)). Индекс Гувера логнормали."""
    s = np.sqrt(np.log(1 + cv**2))
    return float(2 * norm.cdf(s / 2) - 1)


def ratio_analytic(cv: float) -> float:
    return SQRT_2PI * hoover_lognormal(cv) / cv


def hoover_mc(cv: float, n: int = 4_000_000, seed: int = 0) -> float:
    """Прямой Монте-Карло того же H — контроль правильности формулы."""
    rng = np.random.default_rng(seed)
    s = np.sqrt(np.log(1 + cv**2))
    x = rng.lognormal(-(s**2) / 2, s, n)  # среднее = 1
    return float(np.maximum(0.0, x - 1.0).mean())


out: dict = {"formula": "ratio = sqrt(2*pi) * (2*Phi(s/2) - 1) / CV, s = sqrt(ln(1+CV^2))"}
print("=" * 70)
print("R7 — замкнутая форма при N = ∞, без единой симуляции модели")
print("=" * 70)
print(f"{'CV':>6} {'H (формула)':>13} {'H (Монте-Карло)':>17} {'отношение':>11}")
rows = []
for cv in CV_GRID:
    h, hm, r = hoover_lognormal(cv), hoover_mc(cv), ratio_analytic(cv)
    rows.append({"cv": cv, "hoover": h, "hoover_mc": hm, "ratio": r})
    print(f"{cv:>6} {h:>13.6f} {hm:>17.6f} {r:>11.4f}")
out["rows"] = rows

base = rows[0]["ratio"]
spread = max(abs(r["ratio"] - base) / base for r in rows)
out["spread_analytic"] = float(spread)
print("-" * 70)
print(f"  разброс отношения ПРИ N = ∞ : {spread:.1%}")
print("  разброс в симуляции R3      : 14.2%  (базовая конфигурация)")
print(f"  максимальное расхождение H формула/МК: "
      f"{max(abs(r['hoover']-r['hoover_mc']) for r in rows):.2e}")

print("\n  ВЫВОД: отклонение от 1 существует УЖЕ при N = ∞ и БЕЗ всякой симуляции,")
print(f"  и оно БОЛЬШЕ ({spread:.1%}), чем наблюдаемое в модели (14.2%).")
print("  Причина: делим величину типа L1 (индекс Гувера) на меру типа L2 (CV).")
print("  Для нормального/равномерного/Пуассона это отношение — константа √(2/π)≈0.798,")
print("  для логнормали пропорциональность ломается тем сильнее, чем тяжелее хвост.")

Path("analytic_r7.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("\nsaved: analytic_r7.json")
