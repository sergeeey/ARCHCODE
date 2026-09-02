"""
V10-C — измерение ПОТОЛКА для D1 и вычисление efficiency (FL Step 4a).

Пол и наблюдаемое уже есть; потолка не было ни в одном вердикте D1 — это
единственный структурный пробел, оставшийся после V10-A/V10-B.

ОРАКУЛ здесь = подгонка НА САМОМ ТЕСТЕ (train = test). Исполнитель, видевший
ответы. Это корректная верхняя граница: если даже модель, которой разрешено
списывать, не извлекает из Hi-C прибавки — прибавки там нет, и вывод относится
к МИРУ, а не к методу.

Три армы на одном и том же холдауте chr20-22:
  ПОЛ        перемешанные метки внутри варианта, честная подгонка
  НАБЛЮД.    честная подгонка train/test (это и есть вердикт D1)
  ПОТОЛОК    train = test, две модели: та же логистическая и гибкий бустинг

efficiency = (наблюдаемое − пол) / (потолок − пол)

Запуск: python -u v10c_ceiling.py --features features_v10a.parquet
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from run_analysis import BASELINE, HOLDOUT, TEST_FEATURE, fit_predict


def gb_delta(tr: pd.DataFrame, te: pd.DataFrame) -> tuple[float, float, float]:
    """ΔAUC гибкой моделью. WHY бустинг: логистическая почти не переобучается на
    4 признаках и 16k строк, то есть даёт заниженный потолок. Оракулу нужна
    свобода подгонки, иначе это не потолок, а вторая копия наблюдаемого."""
    y_tr, y_te = tr.label.to_numpy(), te.label.to_numpy()
    out = []
    for feats in (BASELINE, [*BASELINE, TEST_FEATURE]):
        m = HistGradientBoostingClassifier(max_iter=300, random_state=0)
        m.fit(tr[feats].to_numpy(), y_tr)
        out.append(roc_auc_score(y_te, m.predict_proba(te[feats].to_numpy())[:, 1]))
    return out[0], out[1], out[1] - out[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="features_v10a.parquet")
    ap.add_argument("--out", default="v10c_ceiling.json")
    args = ap.parse_args()

    df = pd.read_parquet(args.features)
    df = df[df.bin_ok == 1]
    tr = df[~df.chrom.isin(HOLDOUT)]
    te = df[df.chrom.isin(HOLDOUT)]
    res: dict = {"n_train": len(tr), "n_test": len(te), "n_pos_test": int(te.label.sum())}

    print("=" * 70)
    print("V10-C — потолок и efficiency для D1 (FL Step 4a)")
    print("=" * 70)
    print(f"train {len(tr):,} · test {len(te):,} · позитивов в тесте {te.label.sum():,}\n")

    def delta(a: pd.DataFrame, b: pd.DataFrame) -> float:
        y = b.label.to_numpy()
        s0 = fit_predict(a, b, BASELINE)
        s1 = fit_predict(a, b, [*BASELINE, TEST_FEATURE])
        return roc_auc_score(y, s1) - roc_auc_score(y, s0)

    # --- ПОЛ: механизм удалён (метки перемешаны внутри варианта) ---
    rng = np.random.default_rng(0)
    sh = te.copy()
    sh["label"] = sh.groupby("variant_id", sort=False).label.transform(
        lambda v: rng.permutation(v.to_numpy())
    )
    floor = delta(tr, sh)
    res["floor_delta_auc"] = float(floor)
    print(f"  ПОЛ      (перемешанные метки, честная подгонка) ΔAUC = {floor:+.4f}")

    # --- НАБЛЮДАЕМОЕ ---
    obs = delta(tr, te)
    res["observed_delta_auc"] = float(obs)
    print(f"  НАБЛЮД.  (честная подгонка train/test)          ΔAUC = {obs:+.4f}")

    # --- ПОТОЛОК: оракул, видевший ответы ---
    ceil_lr = delta(te, te)
    res["ceiling_delta_auc_lr"] = float(ceil_lr)
    print(f"  ПОТОЛОК  логистическая, train = test            ΔAUC = {ceil_lr:+.4f}")

    b0, b1, ceil_gb = gb_delta(te, te)
    res["ceiling_delta_auc_gb"] = float(ceil_gb)
    res["ceiling_gb_auc_baseline"], res["ceiling_gb_auc_full"] = float(b0), float(b1)
    print(f"  ПОТОЛОК  бустинг, train = test                  ΔAUC = {ceil_gb:+.4f}"
          f"   (AUC {b0:.4f} -> {b1:.4f})")

    # --- сколько Hi-C знает об ответе ВООБЩЕ, при полной свободе подгонки ---
    hic = ["contact", "spec_resist"]
    m = HistGradientBoostingClassifier(max_iter=300, random_state=0)
    m.fit(te[hic].to_numpy(), te.label.to_numpy())
    auc_hic = roc_auc_score(te.label, m.predict_proba(te[hic].to_numpy())[:, 1])
    m2 = HistGradientBoostingClassifier(max_iter=300, random_state=0)
    m2.fit(te[["log10_dist"]].to_numpy(), te.label.to_numpy())
    auc_dist = roc_auc_score(te.label, m2.predict_proba(te[["log10_dist"]].to_numpy())[:, 1])
    res["insample_auc_hic_only"], res["insample_auc_dist_only"] = float(auc_hic), float(auc_dist)
    print(f"\n  только Hi-C (contact+spec), train = test:  AUC = {auc_hic:.4f}")
    print(f"  только расстояние,          train = test:  AUC = {auc_dist:.4f}")

    # --- efficiency ---
    print("\n" + "-" * 70)
    for name, ceil in (("логистическая", ceil_lr), ("бустинг", ceil_gb)):
        denom = ceil - floor
        if abs(denom) < 1e-9:
            print(f"  efficiency ({name}): НЕОПРЕДЕЛЕНА — потолок совпал с полом")
            res[f"efficiency_{name}"] = None
            continue
        eff = (obs - floor) / denom
        res[f"efficiency_{name}"] = float(eff)
        print(f"  efficiency ({name}) = ({obs:+.4f} − {floor:+.4f}) / "
              f"({ceil:+.4f} − {floor:+.4f}) = {eff:.3f}")

    headroom = max(ceil_lr, ceil_gb) - floor
    res["headroom"] = float(headroom)
    verdict = ("NO_HEADROOM — потолок неотличим от пола, метрика ничего не разделяет"
               if headroom < 0.005 else
               "интервал здоров — потолок выше пола, результат интерпретируем")
    res["step4a_verdict"] = verdict
    print(f"\n  запас (потолок − пол) = {headroom:+.4f}")
    print(f"  ВЕРДИКТ Step 4a: {verdict}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\nsaved: {args.out}")


if __name__ == "__main__":
    main()
