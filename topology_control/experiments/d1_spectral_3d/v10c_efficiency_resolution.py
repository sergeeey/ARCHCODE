"""
Разрешение вопроса "efficiency вырождена при observed < floor" (V10-C, FL Step 4a).

ДИАГНОЗ, поставленный до пересчёта:
  1. ПОЛ был ОДНОЙ реализацией перестановки (seed=0) -- не распределением. Заявление
     "observed ниже пола" неотличимо от шума одной выборки без CI.
  2. ПОТОЛОК считался ДВУМЯ разными классами моделей: пол/наблюдаемое -- логистическая,
     один вариант потолка -- бустинг. Это сравнение мощности модели, а не пола и
     потолка ОДНОЙ конструкции. Триплет обязан быть по одному классу модели.

РЕШЕНИЕ:
  A. Пол по ЛОГИСТИЧЕСКОЙ -- N=30 перестановок вместо одной, дать медиану + 90% CI.
  B. Потолок по ЛОГИСТИЧЕСКОЙ (train=test, реальные метки) -- согласован по классу
     модели с полом и наблюдаемым. Триплет (пол_lr, observed_lr, потолок_lr) --
     единственный методологически чистый.
  C. Потолок БУСТИНГОМ -- отдельная величина, отвечающая на ДРУГОЙ вопрос ("есть ли
     вообще извлекаемая нелинейная структура"), не на исходный вопрос D1. Ему нужен
     СВОЙ пол той же мощности: бустинг in-sample на перемешанных метках, N=10 прогонов.

Запуск: python -u v10c_efficiency_resolution.py
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from run_analysis import BASELINE, HOLDOUT, TEST_FEATURE, fit_predict


def shuffled_delta_lr(tr: pd.DataFrame, te: pd.DataFrame, seed: int) -> float:
    rng = np.random.default_rng(seed)
    sh = te.copy()
    sh["label"] = sh.groupby("variant_id", sort=False).label.transform(
        lambda v: rng.permutation(v.to_numpy())
    )
    y = sh.label.to_numpy()
    s0 = fit_predict(tr, sh, BASELINE)
    s1 = fit_predict(tr, sh, [*BASELINE, TEST_FEATURE])
    return roc_auc_score(y, s1) - roc_auc_score(y, s0)


def shuffled_delta_gb(te: pd.DataFrame, seed: int) -> float:
    """WHY in-sample: сопоставимо с ceiling_gb, который тоже train=test."""
    rng = np.random.default_rng(seed)
    sh = te.copy()
    sh["label"] = sh.groupby("variant_id", sort=False).label.transform(
        lambda v: rng.permutation(v.to_numpy())
    )
    y = sh.label.to_numpy()
    out = []
    for feats in (BASELINE, [*BASELINE, TEST_FEATURE]):
        m = HistGradientBoostingClassifier(max_iter=300, random_state=0)
        m.fit(sh[feats].to_numpy(), y)
        out.append(roc_auc_score(y, m.predict_proba(sh[feats].to_numpy())[:, 1]))
    return out[1] - out[0]


def summarize(vals: list[float]) -> dict:
    a = np.array(vals)
    return {
        "n": len(a),
        "median": float(np.median(a)),
        "ci90_lo": float(np.percentile(a, 5)),
        "ci90_hi": float(np.percentile(a, 95)),
        "min": float(a.min()),
        "max": float(a.max()),
    }


def main() -> None:
    df = pd.read_parquet("features_v10a.parquet")
    df = df[df.bin_ok == 1]
    tr = df[~df.chrom.isin(HOLDOUT)]
    te = df[df.chrom.isin(HOLDOUT)]

    print("=" * 70)
    print("V10-C -- разрешение efficiency: распределение пола + согласование классов")
    print("=" * 70)

    # --- наблюдаемое и потолок_lr: детерминированы при реальных метках ---
    y = te.label.to_numpy()
    s0 = fit_predict(tr, te, BASELINE)
    s1 = fit_predict(tr, te, [*BASELINE, TEST_FEATURE])
    observed_lr = roc_auc_score(y, s1) - roc_auc_score(y, s0)

    s0c = fit_predict(te, te, BASELINE)
    s1c = fit_predict(te, te, [*BASELINE, TEST_FEATURE])
    ceiling_lr = roc_auc_score(y, s1c) - roc_auc_score(y, s0c)

    print(f"\nнаблюдаемое (логистическая, честная подгонка)      dAUC = {observed_lr:+.4f}")
    print(f"потолок     (логистическая, train=test)             dAUC = {ceiling_lr:+.4f}")

    # --- пол_lr: N=30 перестановок ---
    print("\nпол (логистическая): 30 независимых перестановок...", flush=True)
    floor_draws = [shuffled_delta_lr(tr, te, s) for s in range(30)]
    floor_lr = summarize(floor_draws)
    print(
        f"  медиана {floor_lr['median']:+.4f}  ·  90% CI [{floor_lr['ci90_lo']:+.4f}, "
        f"{floor_lr['ci90_hi']:+.4f}]  ·  диапазон [{floor_lr['min']:+.4f}, {floor_lr['max']:+.4f}]"
    )

    obs_in_floor_ci = floor_lr["ci90_lo"] <= observed_lr <= floor_lr["ci90_hi"]
    ceil_in_floor_ci = floor_lr["ci90_lo"] <= ceiling_lr <= floor_lr["ci90_hi"]
    print(f"\n  наблюдаемое внутри 90% CI пола? {obs_in_floor_ci}")
    print(f"  потолок_lr внутри 90% CI пола?   {ceil_in_floor_ci}")

    # --- ceiling_gb и его СОБСТВЕННЫЙ пол той же мощности ---
    m0 = HistGradientBoostingClassifier(max_iter=300, random_state=0)
    m0.fit(te[BASELINE].to_numpy(), y)
    m1 = HistGradientBoostingClassifier(max_iter=300, random_state=0)
    m1.fit(te[[*BASELINE, TEST_FEATURE]].to_numpy(), y)
    ceiling_gb = roc_auc_score(
        y, m1.predict_proba(te[[*BASELINE, TEST_FEATURE]].to_numpy())[:, 1]
    ) - roc_auc_score(y, m0.predict_proba(te[BASELINE].to_numpy())[:, 1])

    print(f"\nпотолок (бустинг, train=test, согласованные метки)  dAUC = {ceiling_gb:+.4f}")
    print("пол для бустинга (in-sample, 10 перестановок)...", flush=True)
    gb_floor_draws = [shuffled_delta_gb(te, s) for s in range(10)]
    gb_floor = summarize(gb_floor_draws)
    print(
        f"  медиана {gb_floor['median']:+.4f}  ·  90% CI [{gb_floor['ci90_lo']:+.4f}, "
        f"{gb_floor['ci90_hi']:+.4f}]"
    )
    ceil_gb_above_own_floor = ceiling_gb > gb_floor["ci90_hi"]
    print(f"  потолок_gb ({ceiling_gb:+.4f}) выше СВОЕГО 90% CI пола? {ceil_gb_above_own_floor}")

    # --- efficiency по чистому (согласованному по классу модели) триплету ---
    print("\n" + "-" * 70)
    denom = ceiling_lr - floor_lr["median"]
    eff_lr = (observed_lr - floor_lr["median"]) / denom if abs(denom) > 1e-9 else None
    if eff_lr is not None:
        print(
            f"efficiency (логистическая, медианный пол) = "
            f"({observed_lr:+.4f} - {floor_lr['median']:+.4f}) / "
            f"({ceiling_lr:+.4f} - {floor_lr['median']:+.4f}) = "
            f"{eff_lr:.3f}"
        )
    else:
        print("efficiency неопределена -- потолок совпал с полом")

    out = {
        "observed_lr": observed_lr,
        "ceiling_lr": ceiling_lr,
        "floor_lr": floor_lr,
        "floor_lr_draws": floor_draws,
        "observed_in_floor_ci": obs_in_floor_ci,
        "ceiling_lr_in_floor_ci": ceil_in_floor_ci,
        "ceiling_gb": ceiling_gb,
        "gb_floor": gb_floor,
        "gb_floor_draws": gb_floor_draws,
        "ceiling_gb_above_own_floor": ceil_gb_above_own_floor,
        "efficiency_lr_matched_class": eff_lr,
    }

    print("\n" + "=" * 70)
    print("ВЕРДИКТ")
    print("=" * 70)
    if ceil_in_floor_ci or ceiling_lr <= floor_lr["ci90_hi"]:
        verdict = (
            "CEILING_AT_OR_BELOW_FLOOR (согласованный класс модели) -- даже "
            "привилегированный доступ логистической моделью не отличим от шума. "
            "Не свидетельство против гипотезы: логистическая слишком негибкая, "
            "чтобы дать честный потолок для этого признака."
        )
    elif obs_in_floor_ci:
        verdict = "OBSERVED_AT_FLOOR -- наблюдаемое статистически неотличимо от пола."
    else:
        verdict = "интервал разрешим, efficiency интерпретируема"
    out["verdict"] = verdict
    print(verdict)

    if ceil_gb_above_own_floor:
        print(
            f"\nОТДЕЛЬНО: бустинг находит структуру ВЫШЕ своего собственного пола "
            f"({ceiling_gb:+.4f} > CI [{gb_floor['ci90_lo']:+.4f}, {gb_floor['ci90_hi']:+.4f}])."
            f'\nЭто ответ на ДРУГОЙ вопрос -- "есть ли вообще нелинейная структура", не на'
            f'\nвопрос D1 "добавляет ли spec_resist поверх baseline в честной постановке".'
        )
    else:
        print("\nОТДЕЛЬНО: бустинг НЕ находит структуры выше своего пола -- потолок_gb тоже шум.")

    with open("v10c_efficiency_resolution.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("\nsaved: v10c_efficiency_resolution.json")


if __name__ == "__main__":
    main()
