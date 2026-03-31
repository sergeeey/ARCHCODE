"""
Generate illustrations for the ARCHCODE project report.
4 new figures: timeline, pipeline scheme, blind spot Venn, project stats infographic.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

os.makedirs("figures/report", exist_ok=True)

# ── 1. Project Timeline ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 7))

events = [
    ("2025-11-25", "Первый коммит\nИдея: моделировать\n3D-петли хроматина", "#4CAF50"),
    ("2026-02-02", "HBB атлас: 353 варианта\nОткрытие 27 «жемчужин»", "#E53935"),
    ("2026-02-03", "Валидация Hi-C\nr = 0.53–0.59 (K562)", "#2196F3"),
    ("2026-02-04", "Integrity Protocol\nПост-аудит (Sabaté incident)", "#FF9800"),
    ("2026-02-28", "9 локусов: 30,318 вариантов\nМасштабирование pipeline", "#9C27B0"),
    ("2026-03-01", "Кросс-видовая валидация\nМышь Hbb-bs: r = 0.82", "#00BCD4"),
    ("2026-03-02", "VUS кандидаты: 641\nиз 30,952 проанализированных", "#795548"),
    ("2026-03-05", "MaveDB + gnomAD + MPRA\n9 ортогональных методов", "#607D8B"),
    ("2026-03-06", "bioRxiv v4 подготовка\nTier-система приоритизации", "#FF5722"),
    (
        "2026-03-09",
        "6 экспериментов (P0+P1)\nMetric robustness ✓\nGasperini benchmark ✓",
        "#4CAF50",
    ),
]

dates = [datetime.strptime(d, "%Y-%m-%d") for d, _, _ in events]
labels = [l for _, l, _ in events]
colors = [c for _, _, c in events]

# Alternate y positions
y_positions = [1, -1] * 5
ax.set_xlim(datetime(2025, 11, 1), datetime(2026, 3, 20))
ax.set_ylim(-2.5, 2.5)

# Draw timeline
ax.axhline(0, color="gray", linewidth=2, zorder=1)

for i, (date, label, color) in enumerate(zip(dates, labels, colors)):
    y = y_positions[i] * 1.5
    ax.scatter(date, 0, s=120, color=color, zorder=3, edgecolor="black", linewidth=0.5)
    ax.plot([date, date], [0, y * 0.6], color=color, linewidth=1.5, zorder=2)
    ax.text(
        date,
        y * 0.7,
        label,
        ha="center",
        va="bottom" if y > 0 else "top",
        fontsize=7.5,
        fontweight="bold",
        color=color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.9),
    )

ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.set_yticks([])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.set_title("Хронология проекта ARCHCODE", fontsize=16, fontweight="bold", pad=20)

plt.tight_layout()
plt.savefig("figures/report/timeline.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved: figures/report/timeline.png")


# ── 2. Pipeline Scheme ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")

# Boxes
boxes = [
    (
        0.5,
        4.5,
        2,
        1,
        "ВХОД\n• Геномные координаты\n• ClinVar варианты\n• ENCODE пики\n  (CTCF, H3K27ac)",
        "#E3F2FD",
        "#1565C0",
    ),
    (
        3.5,
        4.5,
        2.5,
        1,
        "СИМУЛЯЦИЯ\n• Экструзия петель когезином\n• Кинетика Крамера\n• CTCF-барьеры\n• MED1-ландшафт энхансеров",
        "#FFF3E0",
        "#E65100",
    ),
    (
        7,
        4.5,
        2.5,
        1,
        "КОНТАКТНЫЕ КАРТЫ\n• Wildtype (норма)\n• Mutant (мутация)\n• Сравнение SSIM",
        "#E8F5E9",
        "#2E7D32",
    ),
    (
        0.5,
        2,
        2,
        1,
        "МЕТРИКИ\n• LSSIM (локальный)\n• DeltaInsulation\n• LoopIntegrity",
        "#F3E5F5",
        "#6A1B9A",
    ),
    (
        3.5,
        2,
        2.5,
        1,
        "КЛАССИФИКАЦИЯ\n• LSSIM < 0.95 → structural\n• VEP < 0.30 → invisible\n• Оба = «жемчужина»",
        "#FFEBEE",
        "#C62828",
    ),
    (
        7,
        2,
        2.5,
        1,
        "РЕЗУЛЬТАТ\n• Атлас вариантов\n• Tier-приоритизация\n• Кандидаты для\n  экспериментов",
        "#E0F7FA",
        "#00695C",
    ),
]

for x, y, w, h, text, facecolor, edgecolor in boxes:
    rect = mpatches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.1",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=2,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8, fontweight="bold")

# Arrows (horizontal)
arrow_style = dict(arrowstyle="-|>", color="#333", lw=2, mutation_scale=20)
ax.annotate("", xy=(3.4, 5), xytext=(2.6, 5), arrowprops=arrow_style)
ax.annotate("", xy=(6.9, 5), xytext=(6.1, 5), arrowprops=arrow_style)

# Arrows (vertical)
ax.annotate("", xy=(1.5, 3.1), xytext=(1.5, 4.4), arrowprops=arrow_style)
ax.annotate("", xy=(4.75, 3.1), xytext=(4.75, 4.4), arrowprops=arrow_style)
ax.annotate("", xy=(8.25, 3.1), xytext=(8.25, 4.4), arrowprops=arrow_style)

# Horizontal arrows bottom row
ax.annotate("", xy=(3.4, 2.5), xytext=(2.6, 2.5), arrowprops=arrow_style)
ax.annotate("", xy=(6.9, 2.5), xytext=(6.1, 2.5), arrowprops=arrow_style)

ax.set_title(
    "Как работает ARCHCODE: от варианта до приоритизации", fontsize=14, fontweight="bold", y=0.98
)

plt.savefig("figures/report/pipeline_scheme.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved: figures/report/pipeline_scheme.png")


# ── 3. Blind Spot Venn Diagram ──────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(-3, 3)
ax.set_ylim(-2.5, 3)
ax.axis("off")

# Three overlapping circles
from matplotlib.patches import Circle

circle1 = Circle((-0.8, 0.3), 1.8, alpha=0.2, color="#2196F3", linewidth=2, edgecolor="#1565C0")
circle2 = Circle((0.8, 0.3), 1.8, alpha=0.2, color="#E53935", linewidth=2, edgecolor="#C62828")
circle3 = Circle((0, -1.0), 1.8, alpha=0.2, color="#4CAF50", linewidth=2, edgecolor="#2E7D32")

ax.add_patch(circle1)
ax.add_patch(circle2)
ax.add_patch(circle3)

# Labels
ax.text(
    -1.8,
    1.8,
    "VEP / SpliceAI\nПоследовательность",
    fontsize=11,
    fontweight="bold",
    ha="center",
    color="#1565C0",
)
ax.text(
    1.8,
    1.8,
    "CADD / REVEL\nМашинное обучение",
    fontsize=11,
    fontweight="bold",
    ha="center",
    color="#C62828",
)
ax.text(
    0,
    -2.3,
    "ARCHCODE\n3D-структура хроматина",
    fontsize=11,
    fontweight="bold",
    ha="center",
    color="#2E7D32",
)

# Center region
ax.text(
    0,
    0.5,
    "Все три\nвидят",
    fontsize=9,
    ha="center",
    va="center",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
)

# Unique ARCHCODE region
ax.text(
    0,
    -1.5,
    "«ЖЕМЧУЖИНЫ»\n27 вариантов\nневидимы другим",
    fontsize=10,
    fontweight="bold",
    ha="center",
    va="center",
    color="#2E7D32",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#C8E6C9", edgecolor="#2E7D32", linewidth=2),
)

# Arrow pointing to pearls
ax.annotate(
    "Структурное\nслепое пятно",
    xy=(0, -1.0),
    xytext=(2.2, -1.5),
    fontsize=9,
    fontweight="bold",
    color="#E53935",
    arrowprops=dict(arrowstyle="->", color="#E53935", lw=2),
    bbox=dict(boxstyle="round", facecolor="#FFEBEE", edgecolor="#E53935"),
)

ax.set_title("Слепое пятно: что видит каждый инструмент", fontsize=14, fontweight="bold")

plt.savefig("figures/report/blind_spot_venn.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved: figures/report/blind_spot_venn.png")


# ── 4. Project Stats Infographic ────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis("off")

# Title
ax.text(
    5,
    7.5,
    "ARCHCODE: проект в цифрах",
    fontsize=22,
    fontweight="bold",
    ha="center",
    va="center",
    color="#1A237E",
)

# Stats cards
stats = [
    (1.5, 5.5, "215", "коммитов", "#E53935"),
    (4, 5.5, "30,318", "вариантов\nклассифицировано", "#2196F3"),
    (6.5, 5.5, "9", "геномных\nлокусов", "#4CAF50"),
    (9, 5.5, "27", "«жемчужин»\nна HBB", "#FF9800"),
    (1.5, 3.5, "36", "фигур\nсгенерировано", "#9C27B0"),
    (4, 3.5, "641", "VUS кандидатов\nна реклассификацию", "#00BCD4"),
    (6.5, 3.5, "6", "экспериментов\nсамопроверки", "#795548"),
    (9, 3.5, "9", "ортогональных\nметодов валидации", "#607D8B"),
    (1.5, 1.5, "113", "Python скриптов", "#FF5722"),
    (4, 1.5, "85", "TypeScript\nмодулей", "#3F51B5"),
    (6.5, 1.5, "~60K", "строк кода\n(Python + TS + Typst)", "#009688"),
    (9, 1.5, "105", "дней\nразработки", "#8BC34A"),
]

for x, y, number, label, color in stats:
    # Card background
    rect = mpatches.FancyBboxPatch(
        (x - 1.1, y - 0.8),
        2.2,
        1.6,
        boxstyle="round,pad=0.15",
        facecolor="white",
        edgecolor=color,
        linewidth=2.5,
    )
    ax.add_patch(rect)
    # Number
    ax.text(
        x, y + 0.2, number, fontsize=24, fontweight="bold", ha="center", va="center", color=color
    )
    # Label
    ax.text(x, y - 0.4, label, fontsize=8, ha="center", va="center", color="#333")

plt.savefig("figures/report/stats_infographic.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved: figures/report/stats_infographic.png")

print("\nAll 4 report figures generated!")
