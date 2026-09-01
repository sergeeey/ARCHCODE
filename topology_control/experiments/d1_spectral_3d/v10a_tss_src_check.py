"""
Внутренний контроль V10-A: меняет ли результат ОГРАНИЧЕНИЕ универсума кандидатов
до одних лишь eGenes v10 (то есть отказ от смешанной аннотации).

⚠️ ИСХОДНЫЙ ЗАМЫСЕЛ КОНТРОЛЯ БЫЛ ОШИБОЧЕН И ОСТАВЛЕН ЗДЕСЬ КАК УРОК.
Планировалось сравнить подмножества «TSS из v10» и «TSS из v26». Это невозможно
ПО КОНСТРУКЦИИ: TSS из v26 получают ровно те гены, которые НЕ являются eGenes v10,
значит они не могут быть позитивами, и их фолд вырожден при любом объёме данных.
Ошибка была видна из определения универсума и не потребовала бы прогона.

Осмысленный вопрос, на который отвечают те же данные: отличается ли результат на
универсуме из одних eGenes v10 от результата на смешанном универсуме? Если нет —
добавление негативов с TSS из v26 безвредно, и оговорка о смешанной аннотации
закрыта.
"""

from __future__ import annotations

import json

import pandas as pd

from run_analysis import HOLDOUT, evaluate_split

df = pd.read_parquet("features_v10a.parquet")
df = df[df.bin_ok == 1]
out: dict = {}

print("=" * 66)
print("V10-A внутренний контроль: TSS из v10 против TSS из v26")
print("=" * 66)
print(f"строк всего {len(df):,} · доля TSS из v10 {(df.tss_src == 'v10').mean():.1%}\n")

for src in ("v10", "v26"):
    sub = df[df.tss_src == src]
    tr = sub[~sub.chrom.isin(HOLDOUT)]
    te = sub[sub.chrom.isin(HOLDOUT)]
    if not len(te) or not te.label.sum():
        print(f"  {src}: тестовый фолд вырожден, пропуск")
        continue
    r = evaluate_split(tr, te)
    out[src] = {k: r[k] for k in ("n_test", "n_pos", "auc_baseline", "auc_full", "delta_auc")}
    print(f"  TSS {src}: n_test {r['n_test']:>7,} · позитивов {r['n_pos']:>6,} · "
          f"baseline {r['auc_baseline']:.4f} · ΔAUC {r['delta_auc']:+.4f}")

if len(out) == 2:
    db = abs(out["v10"]["auc_baseline"] - out["v26"]["auc_baseline"])
    dd = abs(out["v10"]["delta_auc"] - out["v26"]["delta_auc"])
    out["baseline_gap"], out["delta_gap"] = float(db), float(dd)
    print(f"\n  расхождение baseline: {db:.4f}")
    print(f"  расхождение ΔAUC:     {dd:.4f}")
    print(f"\n  ВЕРДИКТ КОНТРОЛЯ: {'смесь безвредна' if dd < 0.02 else 'СМЕСЬ ВНОСИТ СИСТЕМАТИКУ'}"
          f" (порог по ΔAUC тот же, что у claim.md: 0.02)")

with open("v10a_tss_src_check.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print("\nsaved: v10a_tss_src_check.json")
