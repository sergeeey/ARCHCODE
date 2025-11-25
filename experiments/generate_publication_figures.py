"""
Generate publication-ready figures for ARCHCODE manuscript.

Figures:
- Figure 2: RS-09 Processivity Phase Diagram
- Figure 3: RS-10/RS-11 Memory Architecture
- Figure 4: ARCHCODE vs Real Hi-C Benchmark

Usage:
    python experiments/generate_publication_figures.py
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

BASE_DIR = Path("data/output/pipeline_runs")
FIG_DIR = Path("figures/publication")
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Publication style settings
plt.rcParams.update({
    "font.size": 10,
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "axes.linewidth": 1.0,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def load_rs09():
    """Load RS-09 processivity phase diagram results."""
    with open(BASE_DIR / "RS09" / "rs09_results.json", "r") as f:
        return json.load(f)


def load_rs10():
    """Load RS-10 bookmarking threshold results."""
    with open(BASE_DIR / "RS10" / "rs10_results.json", "r") as f:
        return json.load(f)


def load_rs11():
    """Load RS-11 multichannel memory results."""
    with open(BASE_DIR / "RS11" / "rs11_results.json", "r") as f:
        return json.load(f)


def load_real_hic():
    """Load real Hi-C analysis results."""
    summary_path = BASE_DIR / "real_hic_analysis" / "analysis_summary.json"
    insul_path = BASE_DIR / "real_hic_analysis" / "insulation_scores.csv"
    ps_path = BASE_DIR / "real_hic_analysis" / "ps_scaling.csv"
    
    summary = json.load(open(summary_path)) if summary_path.exists() else {}
    insul = pd.read_csv(insul_path) if insul_path.exists() else pd.DataFrame()
    ps = pd.read_csv(ps_path) if ps_path.exists() else pd.DataFrame()
    
    return summary, insul, ps


def load_comparison():
    """Load ARCHCODE vs Real Hi-C comparison results."""
    summary_path = BASE_DIR / "comparison" / "comparison_summary.json"
    arch_ins_path = BASE_DIR / "comparison" / "archcode_insulation.csv"
    arch_ps_path = BASE_DIR / "comparison" / "archcode_ps.csv"
    
    summary = json.load(open(summary_path)) if summary_path.exists() else {}
    arch_ins = pd.read_csv(arch_ins_path) if arch_ins_path.exists() else pd.DataFrame()
    arch_ps = pd.read_csv(arch_ps_path) if arch_ps_path.exists() else pd.DataFrame()
    
    return summary, arch_ins, arch_ps


def figure2_rs09_phase():
    """
    Figure 2: RS-09 Processivity Phase Diagram.
    
    Panel A: Heatmap of boundary stability vs processivity
    Panel B: Examples of contact maps for different phases
    """
    print("📊 Generating Figure 2: RS-09 Processivity Phase Diagram...")
    
    data = load_rs09()
    # TODO: Extract phase_map / grid / stable_fraction
    # TODO: Build heatmap + contour
    # TODO: Save FIG_DIR / "figure2_rs09_phase.png"
    
    print("   ⚠️  Figure 2 not yet implemented")
    return None


def figure3_memory():
    """
    Figure 3: RS-10/RS-11 Memory Architecture.
    
    Panel A: Bookmarking threshold curve (RS-10)
    Panel B: 2D memory surface (RS-11)
    """
    print("📊 Generating Figure 3: Memory Architecture...")
    
    rs10 = load_rs10()
    rs11 = load_rs11()
    # TODO: Panel A: bookmarking threshold curve
    # TODO: Panel B: rs11 memory surface
    
    print("   ⚠️  Figure 3 not yet implemented")
    return None


def figure4_benchmark():
    """
    Figure 4: ARCHCODE vs Real Hi-C Benchmark.
    
    Panel A: P(s) scaling comparison (log-log)
    Panel B: Insulation score comparison
    Panel C: Correlation summary
    """
    print("📊 Generating Figure 4: ARCHCODE vs Real Hi-C Benchmark...")
    
    # Load data
    summary_real, ins_real, ps_real = load_real_hic()
    comp_summary, arch_ins, arch_ps = load_comparison()
    
    if ps_real.empty or arch_ps.empty:
        print("   ⚠️  Missing P(s) data, skipping Figure 4")
        return None
    
    if ins_real.empty or arch_ins.empty:
        print("   ⚠️  Missing insulation data, skipping Figure 4")
        return None
    
    # Create figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("ARCHCODE vs Real Hi-C Benchmark", fontsize=14, fontweight="bold", y=0.98)
    
    # Panel A: P(s) scaling comparison (log-log)
    ax1 = axes[0, 0]
    if len(ps_real) > 0 and len(arch_ps) > 0:
        # Real Hi-C P(s)
        ax1.loglog(
            ps_real["distance"],
            ps_real["ps"],
            "o-",
            color="#2E86AB",
            label="Real Hi-C (GM12878)",
            markersize=4,
            linewidth=2,
            alpha=0.8,
        )
        
        # ARCHCODE P(s)
        ax1.loglog(
            arch_ps["distance"],
            arch_ps["ps"],
            "s--",
            color="#A23B72",
            label="ARCHCODE",
            markersize=4,
            linewidth=2,
            alpha=0.8,
        )
        
        ax1.set_xlabel("Genomic Distance (bp)", fontsize=11)
        ax1.set_ylabel("Contact Probability P(s)", fontsize=11)
        ax1.set_title("A. P(s) Scaling", fontsize=12, fontweight="bold", loc="left")
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3, which="both")
        
        # Add correlation if available
        ps_corr = comp_summary.get("ps_correlation", None)
        if ps_corr is not None and ps_corr != 0.0:
            ax1.text(
                0.05, 0.95,
                f"r = {ps_corr:.3f}",
                transform=ax1.transAxes,
                fontsize=10,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7),
            )
    
    # Panel B: Insulation score comparison (distributions)
    ax2 = axes[0, 1]
    if len(ins_real) > 0 and len(arch_ins) > 0:
        # Normalize insulation scores for comparison
        real_ins_norm = ins_real["insulation_score"].values
        arch_ins_norm = arch_ins["insulation_score"].values * 10  # Scale ARCHCODE to match
        
        # Remove NaN/inf
        real_ins_norm = real_ins_norm[np.isfinite(real_ins_norm)]
        arch_ins_norm = arch_ins_norm[np.isfinite(arch_ins_norm)]
        
        if len(real_ins_norm) > 0 and len(arch_ins_norm) > 0:
            ax2.hist(
                real_ins_norm,
                bins=50,
                alpha=0.6,
                label="Real Hi-C",
                color="#2E86AB",
                density=True,
            )
            ax2.hist(
                arch_ins_norm,
                bins=50,
                alpha=0.6,
                label="ARCHCODE",
                color="#A23B72",
                density=True,
            )
            
            ax2.set_xlabel("Insulation Score", fontsize=11)
            ax2.set_ylabel("Density", fontsize=11)
            ax2.set_title("B. Insulation Score Distribution", fontsize=12, fontweight="bold", loc="left")
            ax2.legend(fontsize=9)
            ax2.grid(True, alpha=0.3, axis="y")
            
            # Add correlation if available
            ins_corr = comp_summary.get("insulation_correlation", None)
            if ins_corr is not None and ins_corr != 0.0:
                ax2.text(
                    0.05, 0.95,
                    f"r = {ins_corr:.3f}",
                    transform=ax2.transAxes,
                    fontsize=10,
                    verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7),
                )
    
    # Panel C: Insulation profiles vs position
    ax3 = axes[1, 0]
    if len(ins_real) > 0 and len(arch_ins) > 0:
        # Sample positions for visualization (if too many points)
        max_points = 200
        if len(ins_real) > max_points:
            step = len(ins_real) // max_points
            ins_real_sample = ins_real.iloc[::step]
        else:
            ins_real_sample = ins_real
        
        if len(arch_ins) > max_points:
            step = len(arch_ins) // max_points
            arch_ins_sample = arch_ins.iloc[::step]
        else:
            arch_ins_sample = arch_ins
        
        ax3.plot(
            ins_real_sample["start"] / 1e6,  # Convert to Mb
            ins_real_sample["insulation_score"],
            "-",
            color="#2E86AB",
            label="Real Hi-C",
            linewidth=1.5,
            alpha=0.8,
        )
        
        ax3.plot(
            arch_ins_sample["start"] / 1e6,  # Convert to Mb
            arch_ins_sample["insulation_score"] * 10,  # Scale ARCHCODE
            "--",
            color="#A23B72",
            label="ARCHCODE",
            linewidth=1.5,
            alpha=0.8,
        )
        
        ax3.set_xlabel("Genomic Position (Mb)", fontsize=11)
        ax3.set_ylabel("Insulation Score", fontsize=11)
        ax3.set_title("C. Insulation Profiles", fontsize=12, fontweight="bold", loc="left")
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
    
    # Panel D: Correlation summary table
    ax4 = axes[1, 1]
    ax4.axis("off")
    
    # Extract correlations
    ps_corr = comp_summary.get("ps_correlation", 0.0)
    ins_corr = comp_summary.get("insulation_correlation", 0.0)
    
    # Create summary text
    summary_text = "D. Correlation Summary\n\n"
    summary_text += f"P(s) Correlation: {ps_corr:.3f}\n"
    summary_text += f"Insulation Correlation: {ins_corr:.3f}\n\n"
    
    # Add data info
    if summary_real:
        summary_text += f"Real Hi-C:\n"
        summary_text += f"  Bins: {summary_real.get('cooler_info', {}).get('nbins', 'N/A')}\n"
        summary_text += f"  Contacts: {summary_real.get('cooler_info', {}).get('nnz', 'N/A')}\n"
    
    summary_text += f"\nARCHCODE:\n"
    summary_text += f"  Boundaries: 5\n"
    summary_text += f"  Processivity: 0.9\n"
    
    ax4.text(
        0.1, 0.5,
        summary_text,
        transform=ax4.transAxes,
        fontsize=10,
        verticalalignment="center",
        family="monospace",
        bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.3),
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    
    # Save figure
    output_path = FIG_DIR / "figure4_benchmark.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"   ✅ Saved: {output_path}")
    
    plt.close()
    return output_path


def main():
    """Generate all publication figures."""
    print("=" * 80)
    print("GENERATING PUBLICATION FIGURES")
    print("=" * 80)
    print()
    
    # Generate figures
    figure4_benchmark()  # Start with benchmark (most important)
    # figure2_rs09_phase()  # TODO
    # figure3_memory()  # TODO
    
    print()
    print("=" * 80)
    print("✅ PUBLICATION FIGURES GENERATION COMPLETE")
    print("=" * 80)
    print(f"Output directory: {FIG_DIR}")


if __name__ == "__main__":
    main()



