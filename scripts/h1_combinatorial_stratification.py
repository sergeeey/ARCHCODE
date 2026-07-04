#!/usr/bin/env python3
"""
H1: Комбинаторная стратификация HBB
====================================

Проверка гипотезы: комбинаторная матрица клинических и геномных признаков
предсказывает pathogenicity HBB-вариантов точнее, чем аддитивные
скоринговые системы.

Author: ARCHCODE Project
Date: 2026-05-21
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    roc_curve,
    precision_recall_curve,
    brier_score_loss,
    f1_score,
    matthews_corrcoef,
    confusion_matrix,
)
from scipy import stats
from sklearn.calibration import calibration_curve
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# 1. ЗАГРУЗКА ДАННЫХ
# ============================================================

print("=" * 70)
print("H1: КОМБИНАТОРНАЯ СТРАТИФИКАЦИЯ HBB")
print("=" * 70)

df = pd.read_csv("D:/ДНК/results/HBB_Unified_Atlas.csv")
print(f"\n✓ Loaded: {len(df)} HBB variants")
print(f"  Columns: {list(df.columns)[:10]}...")

# ============================================================
# 2. ПРЕДОБРАБОТКА
# ============================================================

print("\n" + "=" * 70)
print("PREPROCESSING")
print("=" * 70)

# Фильтрация: только уверенные метки
df_confident = df[df["Label"].isin(["Pathogenic", "Benign"])].copy()
print(f"\n✓ Filtered to confident labels: {len(df_confident)}")

# Бинарная целевая переменная
df_confident["y"] = (df_confident["Label"] == "Pathogenic").astype(int)
print(
    f"  Pathogenic: {df_confident['y'].sum()} ({df_confident['y'].sum()/len(df_confident)*100:.1f}%)"
)
print(
    f"  Benign: {len(df_confident) - df_confident['y'].sum()} ({(1-df_confident['y'].mean())*100:.1f}%)"
)

# Обработка признаков
df_confident["Category_encoded"] = (
    df_confident["Category"].fillna("unknown").astype("category").cat.codes
)

# CADD_Phred: заменяем -1 (missing) на медиану
cadd_median = df_confident[df_confident["CADD_Phred"] != -1]["CADD_Phred"].median()
df_confident["CADD_Phred"] = df_confident["CADD_Phred"].replace(-1, cadd_median)

# VEP_Score: заменяем -1 на 0.1 (минимальный impact)
df_confident["VEP_Score"] = df_confident["VEP_Score"].replace(-1, 0.1)

# ARCHCODE_LSSIM: уже чистый (0.88-0.99)
print(f"\n✓ Feature statistics:")
print(
    f"  CADD_Phred: {df_confident['CADD_Phred'].min():.1f} - {df_confident['CADD_Phred'].max():.1f}"
)
print(f"  VEP_Score: {df_confident['VEP_Score'].min():.2f} - {df_confident['VEP_Score'].max():.2f}")
print(
    f"  LSSIM: {df_confident['ARCHCODE_LSSIM'].min():.3f} - {df_confident['ARCHCODE_LSSIM'].max():.3f}"
)
print(f"  Categories: {df_confident['Category'].nunique()} unique")

# Признаки
feature_cols = ["CADD_Phred", "VEP_Score", "ARCHCODE_LSSIM", "Category_encoded"]
X = df_confident[feature_cols].copy()
y = df_confident["y"]

# Train/test split (stratified по Label)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
print(f"\n✓ Train/test split:")
print(f"  Train: {len(X_train)} ({y_train.sum()} pathogenic)")
print(f"  Test:  {len(X_test)} ({y_test.sum()} pathogenic)")

# ============================================================
# 3. BASELINE МОДЕЛИ
# ============================================================

print("\n" + "=" * 70)
print("BASELINE MODELS")
print("=" * 70)

# B1: Logistic Regression (без interactions)
baseline_lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
baseline_lr.fit(X_train, y_train)
y_pred_proba_lr = baseline_lr.predict_proba(X_test)[:, 1]
print("\n✓ Baseline LogReg trained")

# B2: Random Forest
baseline_rf = RandomForestClassifier(
    n_estimators=100, random_state=42, class_weight="balanced", max_depth=5
)
baseline_rf.fit(X_train, y_train)
y_pred_proba_rf = baseline_rf.predict_proba(X_test)[:, 1]
print("✓ Baseline RandomForest trained")

# B3: LogReg с interaction terms
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)
baseline_lr_inter = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
baseline_lr_inter.fit(X_train_poly, y_train)
y_pred_proba_lr_inter = baseline_lr_inter.predict_proba(X_test_poly)[:, 1]
print("✓ Baseline LogReg + Interactions trained")

# ============================================================
# 4. КОМБИНАТОРНАЯ МОДЕЛЬ
# ============================================================

print("\n" + "=" * 70)
print("COMBINATORIAL MODEL")
print("=" * 70)


def create_combinatorial_matrix(X_train_df, y_train_series, n_bins=3):
    """
    Создаёт комбинаторную матрицу: биннинг каждого признака по квантилям.
    """
    binned = X_train_df.copy()
    bin_edges = {}

    for col in X_train_df.columns:
        if col == "Category_encoded":
            binned[col] = X_train_df[col].astype(int)
        else:
            # qcut с обработкой дубликатов
            try:
                binned[col], edges = pd.qcut(
                    X_train_df[col], q=n_bins, labels=False, retbins=True, duplicates="drop"
                )
                bin_edges[col] = edges
            except ValueError:
                # Если слишком мало уникальных значений
                binned[col] = pd.cut(X_train_df[col], bins=n_bins, labels=False)
                bin_edges[col] = None

    # Создаём клетки
    matrix = {}
    for idx in binned.index:
        cell_key = tuple(binned.loc[idx].values)
        if cell_key not in matrix:
            matrix[cell_key] = {"pathogenic_count": 0, "total_count": 0}
        matrix[cell_key]["total_count"] += 1
        matrix[cell_key]["pathogenic_count"] += y_train_series.loc[idx]

    # Сглаживание Лапласа
    for key in matrix:
        matrix[key]["smoothed_rate"] = (matrix[key]["pathogenic_count"] + 1) / (
            matrix[key]["total_count"] + 2
        )

    return matrix, bin_edges


def predict_combinatorial(X_test_df, matrix, bin_edges, n_bins=3):
    """
    Предсказывает probability для тестовой выборки.
    """
    binned = X_test_df.copy().reset_index(drop=True)

    for col in X_test_df.columns:
        if col == "Category_encoded":
            binned[col] = X_test_df[col].astype(int).values
        else:
            # Используем edges из трейна
            if bin_edges[col] is not None:
                binned[col] = pd.cut(
                    X_test_df[col], bins=bin_edges[col], labels=False, include_lowest=True
                )
            else:
                binned[col] = pd.cut(X_test_df[col], bins=n_bins, labels=False)

    predictions = []
    for idx in range(len(binned)):
        cell_key = tuple(binned.iloc[idx].values)
        if cell_key in matrix:
            predictions.append(matrix[cell_key]["smoothed_rate"])
        else:
            # Для неизвестных клеток — априорная вероятность
            predictions.append(y_train.mean())

    return np.array(predictions)


# Создание модели
comb_matrix, bin_edges = create_combinatorial_matrix(X_train, y_train, n_bins=3)
y_pred_proba_comb = predict_combinatorial(X_test, comb_matrix, bin_edges, n_bins=3)

print(f"\n✓ Combinatorial matrix created:")
print(f"  Cells: {len(comb_matrix)}")
print(f"  Avg variants per cell: {len(X_train) / len(comb_matrix):.1f}")

# ============================================================
# 5. МЕТРИКИ
# ============================================================

print("\n" + "=" * 70)
print("EVALUATION")
print("=" * 70)


def evaluate_model(y_true, y_pred_proba, model_name):
    """Полная оценка модели."""
    auc = roc_auc_score(y_true, y_pred_proba)
    pr_auc = average_precision_score(y_true, y_pred_proba)
    brier = brier_score_loss(y_true, y_pred_proba)

    # F1 при оптимальном threshold (Youden's J)
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[optimal_idx]
    y_pred = (y_pred_proba >= optimal_threshold).astype(int)
    f1 = f1_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)

    print(
        f"\n{model_name:30s} | AUC: {auc:.3f} | PR-AUC: {pr_auc:.3f} | F1: {f1:.3f} | MCC: {mcc:.3f}"
    )

    return {
        "model": model_name,
        "auc": auc,
        "pr_auc": pr_auc,
        "brier": brier,
        "f1": f1,
        "mcc": mcc,
        "y_pred_proba": y_pred_proba,
    }


results = []
results.append(evaluate_model(y_test, y_pred_proba_lr, "Baseline: LogReg"))
results.append(evaluate_model(y_test, y_pred_proba_lr_inter, "Baseline: LogReg + Interactions"))
results.append(evaluate_model(y_test, y_pred_proba_rf, "Baseline: RandomForest"))
results.append(evaluate_model(y_test, y_pred_proba_comb, "Combinatorial Matrix"))

# ============================================================
# 6. СТАТИСТИЧЕСКАЯ ПРОВЕРКА
# ============================================================

print("\n" + "=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)


def delong_test_bootstrap(y_true, pred1, pred2, n_bootstrap=1000):
    """Bootstrap DeLong test для сравнения AUC."""
    diffs = []
    n = len(y_true)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, size=n, replace=True)
        try:
            auc1 = roc_auc_score(y_true.iloc[idx], pred1[idx])
            auc2 = roc_auc_score(y_true.iloc[idx], pred2[idx])
            diffs.append(auc1 - auc2)
        except:
            continue

    diffs = np.array(diffs)
    ci_lower = np.percentile(diffs, 2.5)
    ci_upper = np.percentile(diffs, 97.5)
    p_value = 2 * min(np.mean(diffs > 0), np.mean(diffs < 0))

    return p_value, ci_lower, ci_upper, np.mean(diffs)


# Сравнение: Combinatorial vs Baseline LogReg
p_val, ci_lo, ci_hi, delta_mean = delong_test_bootstrap(y_test, y_pred_proba_comb, y_pred_proba_lr)
print(f"\nCombinatorial vs Baseline LogReg:")
print(f"  ΔAUC: {delta_mean:.4f}")
print(f"  95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"  p-value: {p_val:.4f}")
verdict = "✅ SIGNIFICANT" if (p_val < 0.01 and ci_lo > 0.05) else "❌ NOT SIGNIFICANT"
print(f"  Verdict: {verdict}")

# Сравнение: Combinatorial vs LogReg + Interactions
p_val2, ci_lo2, ci_hi2, delta_mean2 = delong_test_bootstrap(
    y_test, y_pred_proba_comb, y_pred_proba_lr_inter
)
print(f"\nCombinatorial vs LogReg + Interactions:")
print(f"  ΔAUC: {delta_mean2:.4f}")
print(f"  95% CI: [{ci_lo2:.4f}, {ci_hi2:.4f}]")
print(f"  p-value: {p_val2:.4f}")

# ============================================================
# 7. ABLATION STUDY (1D → 2D → 3D → 4D)
# ============================================================

print("\n" + "=" * 70)
print("ABLATION STUDY: Dimensionality Impact")
print("=" * 70)

ablation_results = []

# 1D: CADD alone
X_train_1d = X_train[["CADD_Phred"]]
X_test_1d = X_test[["CADD_Phred"]]
lr_1d = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
lr_1d.fit(X_train_1d, y_train)
y_pred_1d = lr_1d.predict_proba(X_test_1d)[:, 1]
auc_1d = roc_auc_score(y_test, y_pred_1d)
ablation_results.append({"dims": 1, "features": "CADD", "auc": auc_1d})
print(f"1D (CADD):                      AUC = {auc_1d:.3f}")

# 2D: CADD + Category
X_train_2d = X_train[["CADD_Phred", "Category_encoded"]]
X_test_2d = X_test[["CADD_Phred", "Category_encoded"]]
comb_matrix_2d, bin_edges_2d = create_combinatorial_matrix(X_train_2d, y_train, n_bins=3)
y_pred_2d = predict_combinatorial(X_test_2d, comb_matrix_2d, bin_edges_2d, n_bins=3)
auc_2d = roc_auc_score(y_test, y_pred_2d)
ablation_results.append({"dims": 2, "features": "CADD + Category", "auc": auc_2d})
print(f"2D (CADD + Category):           AUC = {auc_2d:.3f}  (Δ = {auc_2d - auc_1d:+.3f})")

# 3D: CADD + Category + VEP
X_train_3d = X_train[["CADD_Phred", "Category_encoded", "VEP_Score"]]
X_test_3d = X_test[["CADD_Phred", "Category_encoded", "VEP_Score"]]
comb_matrix_3d, bin_edges_3d = create_combinatorial_matrix(X_train_3d, y_train, n_bins=3)
y_pred_3d = predict_combinatorial(X_test_3d, comb_matrix_3d, bin_edges_3d, n_bins=3)
auc_3d = roc_auc_score(y_test, y_pred_3d)
ablation_results.append({"dims": 3, "features": "CADD + Category + VEP", "auc": auc_3d})
print(f"3D (CADD + Category + VEP):     AUC = {auc_3d:.3f}  (Δ = {auc_3d - auc_2d:+.3f})")

# 4D: Full (CADD + Category + VEP + LSSIM)
auc_4d = results[3]["auc"]
ablation_results.append({"dims": 4, "features": "Full (4D)", "auc": auc_4d})
print(f"4D (Full):                      AUC = {auc_4d:.3f}  (Δ = {auc_4d - auc_3d:+.3f})")

# ============================================================
# 8. ВИЗУАЛИЗАЦИЯ
# ============================================================

print("\n" + "=" * 70)
print("GENERATING FIGURES")
print("=" * 70)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# ---- Panel 1: ROC Curves ----
ax1 = axes[0, 0]
for res in results:
    fpr, tpr, _ = roc_curve(y_test, res["y_pred_proba"])
    ax1.plot(fpr, tpr, label=f"{res['model']} ({res['auc']:.3f})", linewidth=2)
ax1.plot([0, 1], [0, 1], "k--", label="Random", linewidth=1)
ax1.set_xlabel("False Positive Rate", fontsize=11)
ax1.set_ylabel("True Positive Rate", fontsize=11)
ax1.set_title("ROC Curves", fontsize=12, fontweight="bold")
ax1.legend(loc="lower right", fontsize=9)
ax1.grid(True, alpha=0.3)

# ---- Panel 2: PR Curves ----
ax2 = axes[0, 1]
for res in results:
    precision, recall, _ = precision_recall_curve(y_test, res["y_pred_proba"])
    ax2.plot(recall, precision, label=f"{res['model']} ({res['pr_auc']:.3f})", linewidth=2)
ax2.set_xlabel("Recall", fontsize=11)
ax2.set_ylabel("Precision", fontsize=11)
ax2.set_title("Precision-Recall Curves", fontsize=12, fontweight="bold")
ax2.legend(loc="lower left", fontsize=9)
ax2.grid(True, alpha=0.3)

# ---- Panel 3: Calibration Plot ----
ax3 = axes[0, 2]
for res in results:
    try:
        prob_true, prob_pred = calibration_curve(y_test, res["y_pred_proba"], n_bins=10)
        ax3.plot(prob_pred, prob_true, marker="o", label=res["model"], linewidth=2, markersize=6)
    except:
        pass
ax3.plot([0, 1], [0, 1], "k--", label="Perfect", linewidth=1)
ax3.set_xlabel("Mean Predicted Probability", fontsize=11)
ax3.set_ylabel("Fraction of Positives", fontsize=11)
ax3.set_title("Calibration Plot", fontsize=12, fontweight="bold")
ax3.legend(loc="upper left", fontsize=9)
ax3.grid(True, alpha=0.3)

# ---- Panel 4: Ablation Study (Dimensionality) ----
ax4 = axes[1, 0]
dims = [r["dims"] for r in ablation_results]
aucs = [r["auc"] for r in ablation_results]
labels = [r["features"] for r in ablation_results]
bars = ax4.bar(range(len(dims)), aucs, color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"])
ax4.set_xticks(range(len(dims)))
ax4.set_xticklabels([f"{d}D" for d in dims], fontsize=11)
ax4.set_ylabel("AUC-ROC", fontsize=11)
ax4.set_title("Ablation Study: Dimensionality Impact", fontsize=12, fontweight="bold")
ax4.set_ylim([min(aucs) - 0.05, max(aucs) + 0.05])
ax4.grid(True, alpha=0.3, axis="y")
# Аннотации
for i, (bar, auc) in enumerate(zip(bars, aucs)):
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{auc:.3f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

# ---- Panel 5: Heatmap комбинаторной матрицы (CADD vs Category) ----
ax5 = axes[1, 1]
# 2D срез: CADD bins vs Category bins
heatmap_data = np.zeros((3, 5))  # 3 CADD bins × ~5 category bins
for key, val in comb_matrix_2d.items():
    i, j = key  # (cadd_bin, category_bin)
    if i < 3 and j < 5:
        heatmap_data[i, j] = val["smoothed_rate"]

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".2f",
    cmap="RdYlBu_r",
    xticklabels=[f"Cat{i}" for i in range(5)],
    yticklabels=["CADD_low", "CADD_med", "CADD_high"],
    ax=ax5,
    cbar_kws={"label": "Pathogenic Rate"},
    vmin=0,
    vmax=1,
)
ax5.set_title("Combinatorial Matrix (2D Slice)\nCADD × Category", fontsize=12, fontweight="bold")
ax5.set_xlabel("Category Bin", fontsize=11)
ax5.set_ylabel("CADD Bin", fontsize=11)

# ---- Panel 6: Feature Importance (RandomForest) ----
ax6 = axes[1, 2]
feature_names_short = ["CADD", "VEP", "LSSIM", "Category"]
importances = baseline_rf.feature_importances_
indices = np.argsort(importances)[::-1]
bars = ax6.barh(range(len(importances)), importances[indices], color="#FF6B6B")
ax6.set_yticks(range(len(importances)))
ax6.set_yticklabels([feature_names_short[i] for i in indices], fontsize=11)
ax6.set_xlabel("Importance", fontsize=11)
ax6.set_title("RandomForest Feature Importance", fontsize=12, fontweight="bold")
ax6.invert_yaxis()
ax6.grid(True, alpha=0.3, axis="x")

plt.tight_layout()
plt.savefig("D:/ДНК/results/h1_combinatorial_validation.png", dpi=300, bbox_inches="tight")
print("\n✓ Figure saved: results/h1_combinatorial_validation.png")

# ============================================================
# 9. ИНТЕРПРЕТАЦИЯ
# ============================================================

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

comb_auc = results[3]["auc"]
baseline_auc = results[0]["auc"]
delta = comb_auc - baseline_auc

print(f"\nΔAUC (Combinatorial - Baseline): {delta:.4f}")
print(f"95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"p-value: {p_val:.4f}")

if delta >= 0.15 and p_val < 0.01:
    verdict = "✅ HYPOTHESIS CONFIRMED"
    interpretation = """
Комбинаторная стратификация значимо превосходит линейный baseline (ΔAUC ≥ 0.15, p < 0.01).
Регуляторная функция определяется синергией признаков, не аддитивной суммой.
    """
elif delta >= 0.05 and p_val < 0.05:
    verdict = "⚠️ PARTIAL CONFIRMATION"
    interpretation = """
Эффект обнаружен, но ниже порога практической значимости (ΔAUC < 0.15).
Возможные причины: недостаточный размер выборки, overfitting, недостаточно признаков.
    """
else:
    verdict = "❌ HYPOTHESIS REJECTED"
    interpretation = """
Комбинаторная модель НЕ превосходит baseline.
Регуляторная функция может быть аддитивной, или комбинаторика избыточна.
LogReg + Interactions уже захватывает нелинейные эффекты.
    """

print(f"\nVERDICT: {verdict}")
print(interpretation)

# Ablation interpretation
print("\nABLATION INSIGHT:")
delta_2d_1d = ablation_results[1]["auc"] - ablation_results[0]["auc"]
delta_3d_2d = ablation_results[2]["auc"] - ablation_results[1]["auc"]
delta_4d_3d = ablation_results[3]["auc"] - ablation_results[2]["auc"]

print(f"  1D → 2D: +{delta_2d_1d:.3f}  (adding Category)")
print(f"  2D → 3D: +{delta_3d_2d:.3f}  (adding VEP)")
print(f"  3D → 4D: +{delta_4d_3d:.3f}  (adding LSSIM)")

if delta_3d_2d < 0.02 and delta_4d_3d < 0.02:
    print("\n  💡 Diminishing returns after 2D → most signal in CADD + Category.")
else:
    print("\n  💡 Each dimension adds value → true combinatorial effect.")

# Negative control
print("\n" + "=" * 70)
print("NEGATIVE CONTROL (Random Features)")
print("=" * 70)

X_random_train = pd.DataFrame(np.random.randn(len(X_train), 4), columns=feature_cols)
X_random_test = pd.DataFrame(np.random.randn(len(X_test), 4), columns=feature_cols)
lr_random = LogisticRegression(max_iter=1000, random_state=42)
lr_random.fit(X_random_train, y_train)
y_random_proba = lr_random.predict_proba(X_random_test)[:, 1]
auc_random = roc_auc_score(y_test, y_random_proba)
print(f"Random features AUC: {auc_random:.3f} (expected ≈ 0.50)")

if auc_random > 0.55:
    print("⚠️ WARNING: Random features show non-trivial AUC → possible data leakage or overfitting")
else:
    print("✅ Negative control passed")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
