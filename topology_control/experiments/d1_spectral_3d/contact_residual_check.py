"""
Проверка числа, попавшего в pearl-реестр МИНУЯ закоммиченный артефакт.

История: 2026-08-30 при разборе D1 было посчитано инлайн, что остаток контакта Hi-C
после вычета геномного расстояния даёт AUC 0.5063 — "канал пуст". Число ушло в
pearl-реестр с impact 8. Закоммиченного скрипта за ним не стояло.

2026-08-31 его независимо оспорили ДВЕ стороны: проба роя (пересчёт дал 0.4326/0.4536)
и другая сессия (`nonlinear_residual_check_2026-08-31.md`, не смогла найти исходный
скрипт и получила 0.43-0.48).

Этот файл воспроизводит исходное вычисление ДОСЛОВНО и фиксирует результат в git,
чтобы спор закрылся артефактом, а не памятью.

Запуск: python contact_residual_check.py                    # исходный набор (GTEx v8)
        python contact_residual_check.py --features X.parquet --out Y.json

WHY параметризация добавлена 2026-09-01, а дефолты НЕ тронуты: репликация на GTEx v10
должна пройти тем же кодом, но команда из строки выше обязана воспроизводить исходные
числа дословно — иначе артефакт перестаёт закрывать спор, ради которого написан.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

_ap = argparse.ArgumentParser()
_ap.add_argument("--features", default="features_all.parquet")
_ap.add_argument("--out", default="contact_residual_check.json")
_args = _ap.parse_args()

df = pd.read_parquet(Path(__file__).parent / _args.features)
out: dict = {}

# Популяция ровно та, что была в исходном инлайн-вычислении 2026-08-30
d = df[(df.bin_ok == 1) & (df.contact > 0)].copy()
out["n_pairs"] = len(d)

rho, _ = spearmanr(d.contact, d.log10_dist)
fit = sm.OLS(np.log10(d.contact.to_numpy()), sm.add_constant(d.log10_dist.to_numpy())).fit()
resid = fit.resid
auc = roc_auc_score(d.label, resid)

out.update(
    {
        "spearman_contact_vs_dist": float(rho),
        "r2_log_contact_on_log_dist": float(fit.rsquared),
        "slope": float(fit.params[1]),
        "auc_of_residual": float(auc),
        # WHY обе стороны: AUC остатка ниже 0.5 означает АНТИ-корреляцию, а не
        # отсутствие сигнала. Симметричная величина |AUC-0.5| честнее для вывода
        # "канал пуст", чем сырое число.
        "auc_symmetric": float(max(auc, 1 - auc)),
        "distance_from_chance": float(abs(auc - 0.5)),
    }
)

print("=" * 62)
print("Пересчёт числа из pearl-реестра, впервые с артефактом в git")
print("=" * 62)
for k, v in out.items():
    print(f"  {k:32s} {v}")
print()
print("  исходно записано в реестр: AUC остатка = 0.5063")
print(f"  получено сейчас          : AUC остатка = {auc:.4f}")
print(f"  {'ВОСПРОИЗВЕЛОСЬ' if abs(auc - 0.5063) < 0.002 else 'НЕ ВОСПРОИЗВЕЛОСЬ'}")

Path(__file__).with_name(_args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
