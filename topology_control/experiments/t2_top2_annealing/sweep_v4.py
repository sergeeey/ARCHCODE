"""
30-seed прогон варианта V2 (плотность зацеплений). Пре-регистрация: `claim_v4.md`,
заморожена коммитом 4be9e55 ДО того, как `density_gate` был написан.

Что зафиксировано в claim_v4.md ДО запуска и здесь только исполняется:
  * n = 30, seeds range(30) -- те же, что в v3
  * решение по МЕДИАНЕ advantage_score, не по среднему и не по лучшему seed
  * пороги SUCCESS < 0.7 / KILL > 0.8 -- унаследованы из v1, не менялись
  * вторичное предсказание: эффект обязан быть виден уже в ПЕРВОЙ половине прогона
    (плотность информативна с шага 0, в отличие от кривизны)

WHY отдельный файл, а не heredoc: 30-seed прогон v3 гонялся инлайном и не оставил
артефакта, который можно перезапустить. Здесь он воспроизводим и коммитится.

Запуск:
    python sweep_v4.py --arm density --seeds 30 --out sweep_v4.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from toy_model_v2 import KILL_ADVANTAGE, SUCCESS_ADVANTAGE, Config, evaluate, run_arm


def half_advantage(test_hist: list[float], rnd_hist: list[float]) -> float | None:
    """
    advantage_score на середине прогона -- для вторичного предсказания claim_v4.md.

    WHY середина по индексу, а не по числу принятых passage: у армов разное число
    принятий, и деление по ним сравнивало бы разные моменты «модельного времени».
    Индекс шага одинаков для всех армов по построению.
    """
    ti, ri = test_hist[len(test_hist) // 2], rnd_hist[len(rnd_hist) // 2]
    return float(ti / ri) if ri else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", type=str, default="density")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--rings", type=int, default=24)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--out", type=str, default="sweep_v4.json")
    args = ap.parse_args()

    print("=" * 70)
    print(f"T2 v4 / V2 -- арм '{args.arm}', {args.seeds} seed, prereg claim_v4.md @ 4be9e55")
    print("=" * 70)

    rows: list[dict] = []
    t0 = time.perf_counter()

    for seed in range(args.seeds):
        cfg = Config(num_rings=args.rings, num_steps=args.steps, random_seed=seed)
        arms = {r: run_arm(cfg, r) for r in ("random", args.arm, "oracle")}
        ev = evaluate(arms, test_arm=args.arm)

        test, rnd = arms[args.arm], arms["random"]
        rows.append(
            {
                "seed": seed,
                "verdict": ev["verdict"],
                "failed_gates": ev["failed_gates"],
                # WHY .get(): при непройденном гейте evaluate() возвращает УКОРОЧЕННЫЙ
                # словарь (ветка BLOCKED-INFRASTRUCTURE) без oracle_*. Такой seed по
                # FL Step 2a -- НЕ свидетельство против гипотезы, он исключается из
                # медианы и считается отдельно как n_blocked.
                "advantage_score": ev["advantage_score"],
                "oracle_advantage": ev.get("oracle_advantage"),
                "oracle_agreement": ev.get("oracle_agreement"),
                "half_advantage": half_advantage(test.history, rnd.history),
                "accepted_test": test.accepted,
                "accepted_random": rnd.accepted,
                "c_initial": test.c_initial,
                "dlk_bad": sum(a.dlk_bad for a in arms.values()),
            }
        )
        adv = ev["advantage_score"]
        print(
            f"  seed {seed:2d}  adv {adv:.3f}  "
            f"half {rows[-1]['half_advantage']:.3f}  "
            f"accepted {test.accepted:3d}/{rnd.accepted:3d}  {ev['verdict']}"
            if adv is not None
            else f"  seed {seed:2d}  BLOCKED: {ev['failed_gates']}"
        )

    ok = [r for r in rows if r["advantage_score"] is not None]
    adv = np.array([r["advantage_score"] for r in ok])
    half = np.array([r["half_advantage"] for r in ok if r["half_advantage"] is not None])
    agree = np.array([r["oracle_agreement"] for r in ok if r["oracle_agreement"] is not None])
    ceiling = np.array([r["oracle_advantage"] for r in ok])

    median = float(np.median(adv))
    verdict = (
        "SUCCESS"
        if median < SUCCESS_ADVANTAGE
        else "KILL"
        if median > KILL_ADVANTAGE
        else "INCONCLUSIVE"
    )
    counts = {
        v: sum(1 for r in ok if r["verdict"] == v) for v in ("SUCCESS", "INCONCLUSIVE", "KILL")
    }

    summary = {
        "arm": args.arm,
        "prereg_commit": "4be9e55",
        "n_seeds": len(ok),
        "n_blocked": len(rows) - len(ok),
        "advantage_median": median,
        "advantage_iqr": [float(np.percentile(adv, 25)), float(np.percentile(adv, 75))],
        "verdict_counts": counts,
        "oracle_agreement_mean": float(agree.mean()) if len(agree) else None,
        "oracle_ceiling_median": float(np.median(ceiling)),
        "half_advantage_median": float(np.median(half)) if len(half) else None,
        "dlk_bad_total": sum(r["dlk_bad"] for r in rows),
        "VERDICT": verdict,
    }

    print("-" * 70)
    print(f"advantage_score МЕДИАНА : {median:.4f}   ->  {verdict}")
    print(
        f"  IQR                   : [{summary['advantage_iqr'][0]:.3f}, {summary['advantage_iqr'][1]:.3f}]"
    )
    print(
        f"  SUCCESS/INCONCL/KILL  : {counts['SUCCESS']}/{counts['INCONCLUSIVE']}/{counts['KILL']}"
    )
    print(f"  согласие с оракулом   : {summary['oracle_agreement_mean']}  (0.5 = случайно)")
    print(f"  потолок оракула       : {summary['oracle_ceiling_median']:.4f}")
    print(
        f"  half-advantage медиана: {summary['half_advantage_median']:.4f}  (вторичное предсказание)"
    )
    print(f"  сбоев |dLk| != 1      : {summary['dlk_bad_total']}")
    print(f"wall clock: {time.perf_counter() - t0:.1f}s")
    print("=" * 70)

    Path(args.out).write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2), encoding="utf-8"
    )
    print(f"saved: {args.out}")


if __name__ == "__main__":
    main()
