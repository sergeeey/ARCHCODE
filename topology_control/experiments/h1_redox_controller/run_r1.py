"""
H1 R1 — исполняет `claim_r1.md`, заморожённый `98b95cc` ДО написания этого файла.

Первичный вопрос: точка безубыточности по шуму сенсора совпадает с гетерогенностью
популяции? `|log2(noise_be / CV_pop)| <= 1` для CV ∈ {0.25, 0.5, 1.0, 2.0}.
SUCCESS >= 3 из 4 · KILL >= 2 нарушений · ровно 2 -> INCONCLUSIVE.

Вторичный: держится ли `advantage_excess >= 1.20` в КОНСЕРВАТИВНОЙ точке
(ρ = 0.80, шум = 0.10) — не в той, что дала лучшее число в первом прогоне.

WHY безубыточность ищется по АБСОЛЮТНОМУ advantage, а не по excess: нормировка на
нулевую модель, которую тот же шум портит, скрыла деградацию в первом прогоне
(см. decision.md § Ошибка в моей собственной проверке).

Запуск:
    python run_r1.py --seeds 30 --out result_r1.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from specificity_model import count_events, make_loads

N = 200
THRESHOLD = 20.0
MEAN_LOAD = 5.0
STEPS = 400
NOISE_GRID = np.logspace(np.log10(0.02), np.log10(4.0), 25)  # зафиксировано в claim_r1
CV_GRID = (0.25, 0.5, 1.0, 2.0)
CONSERVATIVE_RATIO = 0.80
CONSERVATIVE_NOISE = 0.10
SUCCESS_EXCESS = 1.20
KILL_EXCESS = 1.05
LOG2_TOLERANCE = 1.0  # фактор 2


def advantage_abs(cv: float, seed: int, noise: float, ratio: float) -> float:
    """
    Абсолютное `events(nuclear) / events(local)`. > 1 -- адресность выигрывает.

    Шум применяется к оценке ЛОКАЛЬНЫМ контроллером своей собственной нагрузки.
    Ядерный арм от него не зависит: он и так не различает органеллы.
    """
    rng = np.random.default_rng(seed)
    loads = make_loads(N, cv, MEAN_LOAD, rng)
    budget = ratio * loads.sum()

    if noise > 0:
        s = np.sqrt(np.log(1 + noise**2))
        sensed = loads * rng.lognormal(-(s**2) / 2, s, N)
    else:
        sensed = loads

    cap_local = budget * sensed / sensed.sum()
    cap_nuclear = np.full(N, budget / N)
    assert abs(cap_local.sum() - cap_nuclear.sum()) < 1e-9

    ev_l = count_events(loads, cap_local, STEPS, THRESHOLD, np.random.default_rng(seed))
    ev_n = count_events(loads, cap_nuclear, STEPS, THRESHOLD, np.random.default_rng(seed))
    return float(ev_n / ev_l) if ev_l else float("nan")


def breakeven_noise(cv: float, seeds: int, ratio: float) -> tuple[float | None, list]:
    """
    Уровень шума, при котором адресность перестаёт выигрывать (advantage = 1.0).

    Ищется линейной интерполяцией в log-пространстве по зафиксированной сетке.
    Возвращает (уровень или None, кривая) — None означает, что перехода нет.
    """
    curve = [
        (float(nz), float(np.median([advantage_abs(cv, s, nz, ratio) for s in range(seeds)])))
        for nz in NOISE_GRID
    ]
    for (n1, a1), (n2, a2) in zip(curve[:-1], curve[1:], strict=False):
        if a1 >= 1.0 > a2:  # пересечение сверху вниз
            f = (a1 - 1.0) / (a1 - a2)
            return float(np.exp(np.log(n1) + f * (np.log(n2) - np.log(n1)))), curve
    return None, curve


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--out", default="result_r1.json")
    args = ap.parse_args()
    out: dict = {"prereg_commit": "98b95cc"}

    print("=" * 72)
    print("H1 R1 -- prereg claim_r1.md @ 98b95cc")
    print("=" * 72)

    # ---------- контроли ----------
    calib = float(np.median([advantage_abs(0.0, s, 0.0, 1.0) for s in range(args.seeds)]))
    calib_ok = abs(calib - 1.0) <= 0.02
    print(f"  [{'PASS' if calib_ok else 'FAIL'}] калибровка (CV=0, шум=0): advantage = {calib:.4f}")
    out["calibration"] = calib
    if not calib_ok:
        out["verdict"] = "BLOCKED-INFRASTRUCTURE"
        Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"\nVERDICT: {out['verdict']}")
        return

    # ---------- ПЕРВИЧНЫЙ: закон безубыточности ----------
    print("\n--- ПЕРВИЧНЫЙ: совпадает ли точка безубыточности с CV популяции? ---")
    print(
        f"{'CV популяции':>13} {'шум безубыт.':>14} {'отношение':>11} {'log2':>7}  в пределах x2?"
    )
    rows, hits = [], 0
    for cv in CV_GRID:
        be, curve = breakeven_noise(cv, args.seeds, ratio=1.0)
        if be is None:
            print(f"{cv:>13} {'НЕ НАЙДЕНА':>14} {'—':>11} {'—':>7}  ✗ (перехода нет)")
            rows.append({"cv": cv, "breakeven": None, "within": False, "curve": curve})
            continue
        ratio_ = be / cv
        lg = float(np.log2(ratio_))
        ok = abs(lg) <= LOG2_TOLERANCE
        hits += ok
        print(f"{cv:>13} {be:>14.3f} {ratio_:>11.3f} {lg:>+7.2f}  {'✓' if ok else '✗'}")
        rows.append(
            {"cv": cv, "breakeven": be, "ratio": ratio_, "log2": lg, "within": ok, "curve": curve}
        )
    out["primary"] = rows
    out["hits"] = hits
    primary = "SUCCESS" if hits >= 3 else ("INCONCLUSIVE" if hits == 2 else "KILL")
    print(f"\n  выполнено {hits} из 4  ->  ПЕРВИЧНЫЙ ВЕРДИКТ: {primary}")
    out["primary_verdict"] = primary

    # ---------- ВТОРИЧНЫЙ: консервативная точка ----------
    print(
        f"\n--- ВТОРИЧНЫЙ: ρ={CONSERVATIVE_RATIO}, шум={CONSERVATIVE_NOISE} (не лучшая точка) ---"
    )
    het = float(
        np.median(
            [
                advantage_abs(0.5, s, CONSERVATIVE_NOISE, CONSERVATIVE_RATIO)
                for s in range(args.seeds)
            ]
        )
    )
    null = float(
        np.median(
            [
                advantage_abs(0.0, s, CONSERVATIVE_NOISE, CONSERVATIVE_RATIO)
                for s in range(args.seeds)
            ]
        )
    )
    excess = het / null
    sec = (
        "SUCCESS"
        if excess >= SUCCESS_EXCESS
        else "KILL"
        if excess < KILL_EXCESS
        else "INCONCLUSIVE"
    )
    print(
        f"  advantage абсолютный (CV=0.5) : {het:.4f}   ({'адресность лучше' if het > 1 else 'адресность ХУЖЕ'})"
    )
    print(f"  advantage нулевой    (CV=0)   : {null:.4f}")
    print(f"  advantage_excess              : {excess:.4f}  (порог {SUCCESS_EXCESS})  -> {sec}")
    out["secondary"] = {"hetero": het, "null": null, "excess": excess, "verdict": sec}
    if (het > 1) != (excess >= 1):
        print("  ⚠️ абсолютная и нормированная величины РАСХОДЯТСЯ — сообщается явно")

    # ---------- негативный контроль ----------
    negs = []
    rng = np.random.default_rng(0)
    for s in range(args.seeds):
        r = np.random.default_rng(s)
        loads = make_loads(N, 0.5, MEAN_LOAD, r)
        budget = CONSERVATIVE_RATIO * loads.sum()
        cap = budget * loads / loads.sum()
        shuffled = rng.permutation(loads)
        el = count_events(shuffled, cap, STEPS, THRESHOLD, np.random.default_rng(s))
        en = count_events(
            shuffled, np.full(N, budget / N), STEPS, THRESHOLD, np.random.default_rng(s)
        )
        negs.append(en / el if el else np.nan)
    neg = float(np.median(negs))
    print(
        f"\n  [{'PASS' if neg < SUCCESS_EXCESS else 'FAIL'}] негативный контроль "
        f"(нагрузки перемешаны после распределения): advantage = {neg:.4f}"
    )
    out["negative_control"] = neg

    print(f"\nВЕРДИКТ первичный: {primary} · вторичный: {sec}")
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"saved: {args.out}")


if __name__ == "__main__":
    main()
