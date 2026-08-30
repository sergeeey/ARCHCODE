"""
D1 — прогон. Исполняет `claim.md`, заморожённый коммитом 0f8cbb4 ДО этого файла.

Ничего не выбирается здесь: схема валидации, пороги, популяция, обе метрики и оба
контроля заданы в claim.md заранее.

    SUCCESS  ΔAUC ≥ 0.05      KILL  ΔAUC < 0.02      серая зона [0.02, 0.05) → СТОП

Запуск:
    python run_analysis.py --features features_all.parquet --out result.json
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import QuantileTransformer

BASELINE = ["log10_dist", "in_ccre", "contact"]
TEST_FEATURE = "spec_resist"
HOLDOUT = ["chr20", "chr21", "chr22"]
SUCCESS_DAUC = 0.05
KILL_DAUC = 0.02
POSITIVE_CONTROL_MIN_AUC = 0.60


def fit_predict(tr: pd.DataFrame, te: pd.DataFrame, feats: list[str]) -> np.ndarray:
    """
    WHY QuantileTransformer обучается ТОЛЬКО на train: ранг-нормировка по всему набору
    протащила бы распределение теста в обучение. Утечка слабая, но это ровно тот класс
    ошибки, который делает результат невоспроизводимым.
    """
    qt = QuantileTransformer(output_distribution="normal", random_state=0, n_quantiles=1000)
    xtr = qt.fit_transform(tr[feats].to_numpy())
    xte = qt.transform(te[feats].to_numpy())
    model = LogisticRegression(max_iter=2000)
    model.fit(xtr, tr.label.to_numpy())
    return model.predict_proba(xte)[:, 1]


def precision_at_1(te: pd.DataFrame, score: np.ndarray) -> float:
    """
    Доля вариантов, у которых истинный eGene оказался первым СРЕДИ КАНДИДАТОВ ЭТОГО ЖЕ
    варианта.

    WHY именно внутри варианта: ранжирование идёт внутри одной группы, поэтому любой
    по-вариантный признак (in_ccre, любой скалярный Δλ) сокращается тождественно.
    Это блокирует механизм утечки категории, который scope_test.md признал переносимым.
    """
    d = te.assign(_s=score)
    hits = d.groupby("variant_id", sort=False).apply(
        lambda g: bool(g.loc[g._s.idxmax(), "label"]), include_groups=False
    )
    return float(hits.mean()) if len(hits) else float("nan")


def evaluate_split(tr: pd.DataFrame, te: pd.DataFrame) -> dict:
    y = te.label.to_numpy()
    if y.sum() == 0 or y.sum() == len(y):
        return {"error": "вырожденный фолд: один класс"}
    s_base = fit_predict(tr, te, BASELINE)
    s_full = fit_predict(tr, te, [*BASELINE, TEST_FEATURE])
    auc_b, auc_f = roc_auc_score(y, s_base), roc_auc_score(y, s_full)
    p_b, p_f = precision_at_1(te, s_base), precision_at_1(te, s_full)
    return {
        "n_test": len(te),
        "n_pos": int(y.sum()),
        "n_variants": int(te.variant_id.nunique()),
        "auc_baseline": auc_b,
        "auc_full": auc_f,
        "delta_auc": auc_f - auc_b,
        "prec1_baseline": p_b,
        "prec1_full": p_f,
        "delta_prec1": p_f - p_b,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="features_all.parquet")
    ap.add_argument("--out", default="result.json")
    args = ap.parse_args()

    raw = pd.read_parquet(args.features)
    print("=" * 70)
    print("D1 spectral -- prereg claim.md @ 0f8cbb4 (заморожен до этого файла)")
    print("=" * 70)
    print(
        f"загружено пар {len(raw):,} · вариантов {raw.variant_id.nunique():,} · "
        f"позитивов {raw.label.sum():,} ({raw.label.mean():.2%})"
    )

    # Популяция первичного анализа задана в claim.md § ICE
    df = raw[raw.bin_ok == 1].copy()
    print(
        f"первичная популяция (bin_ok=1): {len(df):,} пар ({len(df) / len(raw):.1%}), "
        f"позитивов {df.label.sum():,}"
    )

    out: dict = {"prereg_commit": "0f8cbb4", "n_all": len(raw), "n_primary": len(df)}

    # ---- контроли ДО основного результата (claim.md § Контроли) ----
    tr = df[~df.chrom.isin(HOLDOUT)]
    te = df[df.chrom.isin(HOLDOUT)]
    print(f"\ntrain {len(tr):,} пар / test {len(te):,} пар (chr20-22)")

    assert len(tr) and len(te), "пустой фолд -- проверка непустоты из claim.md"
    assert tr.label.sum() and te.label.sum(), "нет позитивов в фолде"

    auc_dist = roc_auc_score(te.label, -te.log10_dist)
    pc_ok = auc_dist > POSITIVE_CONTROL_MIN_AUC
    print(
        f"  [{'PASS' if pc_ok else 'FAIL'}] позитивный контроль: расстояние одно AUC = {auc_dist:.4f}"
        f"  (порог > {POSITIVE_CONTROL_MIN_AUC})"
    )
    out["positive_control_auc"] = auc_dist

    rng = np.random.default_rng(0)
    sh = te.copy()
    sh["label"] = sh.groupby("variant_id", sort=False).label.transform(
        lambda v: rng.permutation(v.to_numpy())
    )
    neg = evaluate_split(tr, sh)
    nc_ok = abs(neg.get("delta_auc", 1)) < KILL_DAUC
    print(
        f"  [{'PASS' if nc_ok else 'FAIL'}] негативный контроль: ΔAUC на перемешанных "
        f"метках = {neg.get('delta_auc', float('nan')):+.4f}  (должен быть ~0)"
    )
    out["negative_control"] = neg

    if not pc_ok:
        out["verdict"] = "BLOCKED-INFRASTRUCTURE"
        out["note"] = "позитивный контроль провален -- НЕ свидетельство против гипотезы"
        print(f"\nVERDICT: {out['verdict']}")
        json.dump(out, open(args.out, "w"), indent=2)
        return
    if not nc_ok:
        out["verdict"] = "STOP-FALSE-POSITIVE-PIPELINE"
        print(f"\nVERDICT: {out['verdict']} -- пайплайн даёт сигнал на шуме")
        json.dump(out, open(args.out, "w"), indent=2)
        return

    # ---- первичный результат ----
    primary = evaluate_split(tr, te)
    out["primary"] = primary
    d = primary["delta_auc"]
    verdict = "SUCCESS" if d >= SUCCESS_DAUC else "KILL" if d < KILL_DAUC else "INCONCLUSIVE"
    out["verdict"] = verdict

    print("\n--- ПЕРВИЧНЫЙ РЕЗУЛЬТАТ (chr20-22, bin_ok=1) ---")
    print(f"  AUC baseline (dist+cCRE+contact) : {primary['auc_baseline']:.4f}")
    print(f"  AUC + spectral                   : {primary['auc_full']:.4f}")
    print(f"  ΔAUC                             : {d:+.4f}   -> {verdict}")
    print(
        f"  precision@1 baseline / +spectral : {primary['prec1_baseline']:.4f} / "
        f"{primary['prec1_full']:.4f}   Δ = {primary['delta_prec1']:+.4f}"
    )

    # ---- вторичные, все пре-регистрированы ----
    locv = []
    for c in sorted(df.chrom.unique()):
        r = evaluate_split(df[df.chrom != c], df[df.chrom == c])
        if "delta_auc" in r:
            locv.append(r["delta_auc"])
    out["locv_mean_delta_auc"] = float(np.mean(locv))
    print(f"\n  LOCV средний ΔAUC ({len(locv)} хромосом)      : {np.mean(locv):+.4f}")

    allp = evaluate_split(raw[~raw.chrom.isin(HOLDOUT)], raw[raw.chrom.isin(HOLDOUT)])
    out["all_pairs"] = allp
    print(f"  ΔAUC на ВСЕХ парах (bin_ok игнор.) : {allp['delta_auc']:+.4f}")

    # вторичное предсказание claim.md: эффект должен расти с расстоянием
    terc = te.log10_dist.quantile([1 / 3, 2 / 3]).to_numpy()
    by_t = {}
    for name, mask in [
        ("нижний терциль", te.log10_dist <= terc[0]),
        ("верхний терциль", te.log10_dist > terc[1]),
    ]:
        r = evaluate_split(tr, te[mask])
        by_t[name] = r.get("delta_auc")
        print(f"  ΔAUC {name:16s}            : {r.get('delta_auc', float('nan')):+.4f}")
    out["by_distance_tercile"] = by_t

    print(f"\nVERDICT: {verdict}")
    json.dump(out, open(args.out, "w"), indent=2)
    print(f"saved: {args.out}")


if __name__ == "__main__":
    main()
