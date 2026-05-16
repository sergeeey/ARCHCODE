#!/usr/bin/env python3
"""Generate publication-ready figures for VT Detector paper."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set publication style
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 9
plt.rcParams["axes.linewidth"] = 0.5


def generate_figure1_decision_tree():
    """Figure 1: VT Detector decision tree (3-stage pipeline)."""

    fig, ax = plt.subplots(figsize=(8, 10), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis("off")

    # Stage 1: Pattern Detection
    stage1_box = FancyBboxPatch(
        (0.5, 12),
        9,
        1.2,
        boxstyle="round,pad=0.1",
        facecolor="#E8F4F8",
        edgecolor="#2C5F77",
        linewidth=2,
    )
    ax.add_patch(stage1_box)
    ax.text(
        5,
        12.6,
        "STAGE 1: Pattern Detection (AST + Regex)",
        ha="center",
        va="center",
        fontsize=11,
        weight="bold",
    )

    # Pattern boxes
    patterns = [
        ("Synthetic\nMarkers", 1.5, 10.5, ["np.random", "mock_*", "synthetic_*"]),
        ("Perfect\nMetrics", 3.5, 10.5, ["F1=1.000", "100%", "AUC=1.0"]),
        ("Zero\nFailures", 5.5, 10.5, ["all passed", "zero fail", "no errors"]),
        ("Embedded\nTest Data", 7.5, 10.5, ["inline arrays", "no URL", "no API"]),
    ]

    for label, x, y, examples in patterns:
        box = FancyBboxPatch(
            (x - 0.6, y),
            1.2,
            1.0,
            boxstyle="round,pad=0.05",
            facecolor="#FFF9E6",
            edgecolor="#8B7355",
            linewidth=1,
        )
        ax.add_patch(box)
        ax.text(x, y + 0.7, label, ha="center", va="center", fontsize=8, weight="bold")
        ax.text(x, y + 0.3, "\n".join(examples[:2]), ha="center", va="center", fontsize=6)

        # Arrow down
        arrow = FancyArrowPatch(
            (x, y), (x, 9.5), arrowstyle="->", mutation_scale=15, linewidth=1, color="#666"
        )
        ax.add_patch(arrow)

    # Stage 2: Confidence Scoring
    stage2_box = FancyBboxPatch(
        (0.5, 8),
        9,
        1.2,
        boxstyle="round,pad=0.1",
        facecolor="#FFF4E6",
        edgecolor="#8B5A00",
        linewidth=2,
    )
    ax.add_patch(stage2_box)
    ax.text(
        5, 8.6, "STAGE 2: Confidence Scoring", ha="center", va="center", fontsize=11, weight="bold"
    )
    ax.text(
        5,
        8.25,
        "Base weights + Synergies + Modifiers",
        ha="center",
        va="center",
        fontsize=8,
        style="italic",
    )

    # Scoring components
    scoring = [
        ("Base\nWeights", 1.5, 6.5, "0.2–0.5\nper pattern"),
        ("Synergy\nBoost", 3.5, 6.5, "+0.25\nsynthetic+\nperfect"),
        ("Evidence\nModifier", 5.5, 6.5, "-0.30\nexternal\nsource"),
        ("Unit Test\nSuppress", 7.5, 6.5, "-0.25\ndef test_"),
    ]

    for label, x, y, detail in scoring:
        box = FancyBboxPatch(
            (x - 0.6, y),
            1.2,
            1.0,
            boxstyle="round,pad=0.05",
            facecolor="#FFE6CC",
            edgecolor="#CC7722",
            linewidth=1,
        )
        ax.add_patch(box)
        ax.text(x, y + 0.7, label, ha="center", va="center", fontsize=7, weight="bold")
        ax.text(x, y + 0.25, detail, ha="center", va="center", fontsize=6)

        # Arrow down
        arrow = FancyArrowPatch(
            (x, y), (x, 5.5), arrowstyle="->", mutation_scale=15, linewidth=1, color="#666"
        )
        ax.add_patch(arrow)

    # Confidence range
    conf_box = FancyBboxPatch(
        (3.5, 5),
        3,
        0.4,
        boxstyle="round,pad=0.05",
        facecolor="#F0F0F0",
        edgecolor="#555",
        linewidth=1,
    )
    ax.add_patch(conf_box)
    ax.text(5, 5.2, "confidence ∈ [0.0, 1.0]", ha="center", va="center", fontsize=8, style="italic")

    # Arrow to Stage 3
    arrow = FancyArrowPatch(
        (5, 5), (5, 4), arrowstyle="->", mutation_scale=20, linewidth=2, color="#333"
    )
    ax.add_patch(arrow)

    # Stage 3: Severity Mapping
    stage3_box = FancyBboxPatch(
        (0.5, 2.5),
        9,
        1.2,
        boxstyle="round,pad=0.1",
        facecolor="#FFE6E6",
        edgecolor="#8B0000",
        linewidth=2,
    )
    ax.add_patch(stage3_box)
    ax.text(
        5, 3.1, "STAGE 3: Severity Mapping", ha="center", va="center", fontsize=11, weight="bold"
    )
    ax.text(
        5,
        2.75,
        "Threshold + Context-Aware Escalation",
        ha="center",
        va="center",
        fontsize=8,
        style="italic",
    )

    # Severity levels
    severities = [
        ("HIGH", 1.5, 1, "≥0.70", "#DC3545", "theater\ndetected"),
        ("MEDIUM", 3.5, 1, "0.40–0.70", "#FFC107", "suspicious\npatterns"),
        ("LOW", 5.5, 1, "<0.40", "#28A745", "info"),
        ("Validation\nContext", 7.5, 1, "escalate\n+1 level", "#6C757D", "keywords:\nvalidation"),
    ]

    for label, x, y, threshold, color, desc in severities:
        box = FancyBboxPatch(
            (x - 0.6, y),
            1.2,
            0.8,
            boxstyle="round,pad=0.05",
            facecolor=color,
            edgecolor="#333",
            linewidth=1,
            alpha=0.7,
        )
        ax.add_patch(box)
        ax.text(
            x, y + 0.6, label, ha="center", va="center", fontsize=7, weight="bold", color="white"
        )
        ax.text(x, y + 0.3, threshold, ha="center", va="center", fontsize=6, color="white")

    # Output
    output_box = FancyBboxPatch(
        (3.5, 0.1),
        3,
        0.6,
        boxstyle="round,pad=0.1",
        facecolor="#E8E8E8",
        edgecolor="#333",
        linewidth=2,
    )
    ax.add_patch(output_box)
    ax.text(
        5, 0.5, "TheaterFinding (structured)", ha="center", va="center", fontsize=9, weight="bold"
    )
    ax.text(
        5,
        0.2,
        "file:line:column | severity | confidence | message",
        ha="center",
        va="center",
        fontsize=6,
        style="italic",
    )

    # Arrow to output
    arrow = FancyArrowPatch(
        (5, 1), (5, 0.7), arrowstyle="->", mutation_scale=20, linewidth=2, color="#333"
    )
    ax.add_patch(arrow)

    plt.tight_layout()
    plt.savefig(
        "D:/ДНК/docs/papers/figures/figure1_decision_tree.png",
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    print("✓ Figure 1 saved: figure1_decision_tree.png")
    plt.close()


def generate_figure2_cli_output():
    """Figure 2: Example CLI output (simplified for publication)."""

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(
        5,
        9.5,
        "VT Detector CLI Output Example",
        ha="center",
        va="top",
        fontsize=12,
        weight="bold",
        family="monospace",
    )

    # Summary box
    summary_box = FancyBboxPatch(
        (0.5, 8),
        9,
        1.2,
        boxstyle="round,pad=0.1",
        facecolor="#F8F9FA",
        edgecolor="#333",
        linewidth=1,
    )
    ax.add_patch(summary_box)

    summary_text = """VALIDATION THEATER DETECTOR — 15 findings

🔴 HIGH: 4    🟡 MEDIUM: 11    🔵 LOW: 0"""

    ax.text(5, 8.6, summary_text, ha="center", va="center", fontsize=9, family="monospace")

    # HIGH findings (2 examples)
    high_y = 7.2
    ax.text(
        0.8,
        high_y,
        "🔴 HIGH SEVERITY",
        ha="left",
        va="top",
        fontsize=10,
        weight="bold",
        color="#DC3545",
    )

    high_findings = [
        {
            "file": "test_core.py:23:8",
            "pattern": "embedded_test_data",
            "message": "Embedded test data without external source",
            "confidence": 0.85,
            "suggestion": "Replace with real API call",
        },
        {
            "file": "test_core.py:45:15",
            "pattern": "f1_perfect + synthetic_marker",
            "message": "Perfect F1=1.000 with synthetic generation",
            "confidence": 0.80,
            "suggestion": "Verify on real data, mark [VERIFIED-SYNTHETIC]",
        },
    ]

    y = high_y - 0.3
    for finding in high_findings:
        box = FancyBboxPatch(
            (1, y - 0.8),
            8.5,
            0.7,
            boxstyle="round,pad=0.05",
            facecolor="#FFE6E6",
            edgecolor="#DC3545",
            linewidth=1,
        )
        ax.add_patch(box)

        text = f"""  {finding['file']}
  Pattern: {finding['pattern']}  |  Confidence: {finding['confidence']:.2f}
  Message: {finding['message']}"""

        ax.text(1.2, y - 0.45, text, ha="left", va="center", fontsize=6.5, family="monospace")
        y -= 1.0

    # MEDIUM findings (2 examples)
    medium_y = y - 0.3
    ax.text(
        0.8,
        medium_y,
        "🟡 MEDIUM SEVERITY",
        ha="left",
        va="top",
        fontsize=10,
        weight="bold",
        color="#FFC107",
    )

    medium_findings = [
        {
            "file": "test_core.py:12:4",
            "pattern": "numpy_random_seed",
            "confidence": 0.55,
            "message": "np.random.seed() — synthetic data marker",
        },
        {
            "file": "test_core.py:67:8",
            "pattern": "hundred_percent_success",
            "confidence": 0.50,
            "message": "100% success rate claim",
        },
    ]

    y = medium_y - 0.3
    for finding in medium_findings:
        box = FancyBboxPatch(
            (1, y - 0.6),
            8.5,
            0.5,
            boxstyle="round,pad=0.05",
            facecolor="#FFF9E6",
            edgecolor="#FFC107",
            linewidth=1,
        )
        ax.add_patch(box)

        text = f"""  {finding['file']}  |  {finding['pattern']}  |  conf: {finding['confidence']:.2f}
  {finding['message']}"""

        ax.text(1.2, y - 0.3, text, ha="left", va="center", fontsize=6.5, family="monospace")
        y -= 0.8

    # Summary recommendation
    rec_box = FancyBboxPatch(
        (1, 0.5),
        8,
        0.6,
        boxstyle="round,pad=0.05",
        facecolor="#E8F4F8",
        edgecolor="#2C5F77",
        linewidth=1,
    )
    ax.add_patch(rec_box)

    ax.text(
        5,
        0.8,
        "✓ Recommendation: 4 HIGH findings require review",
        ha="center",
        va="center",
        fontsize=8,
        weight="bold",
        family="monospace",
    )
    ax.text(
        5,
        0.5,
        "Replace embedded test data with external sources | Add [VERIFIED-SYNTHETIC] markers",
        ha="center",
        va="center",
        fontsize=6.5,
        family="monospace",
        style="italic",
    )

    plt.tight_layout()
    plt.savefig(
        "D:/ДНК/docs/papers/figures/figure2_cli_output.png",
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    print("✓ Figure 2 saved: figure2_cli_output.png")
    plt.close()


if __name__ == "__main__":
    print("Generating VT Detector publication figures...")
    generate_figure1_decision_tree()
    generate_figure2_cli_output()
    print("\n✓ All figures generated successfully")
    print("  - figure1_decision_tree.png (8×10 inches, 300 DPI)")
    print("  - figure2_cli_output.png (8×6 inches, 300 DPI)")
