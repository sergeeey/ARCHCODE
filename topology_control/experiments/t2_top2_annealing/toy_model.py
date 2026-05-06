"""
T2: TOP2 as Topological Annealing — Toy Model

Hypothesis: TOP2 uses local geometric rules for strand passage
           to achieve global topological simplification below equilibrium.

Kill Criteria (pre-registered):
- advantage_score > 0.8 → KILL (less than 20% simplification)
- num_params > 5 → KILL (overfitting)
- effect disappears at coarse-graining → KILL

Success: advantage_score < 0.7 AND num_params <= 3
"""

import sys
from pathlib import Path

# Add shared_utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared_utils"))

import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
import matplotlib.pyplot as plt

from topology_utils import (
    TopologicalState,
    calculate_complexity,
    gauss_linking_integral,
    calculate_catenation_simple,
    strand_passage_random,
    strand_passage_angle_bias,
    strand_passage_curvature_bias,
    create_simple_ring,
    create_linked_rings,
)


@dataclass
class ExperimentConfig:
    """Конфигурация эксперимента"""

    num_rings: int = 200  # Число колец
    num_steps: int = 1000  # Число TOP2 events
    random_seed: int = 42
    # Веса для C(G)
    alpha: float = 1.0  # knots
    beta: float = 1.0  # catenanes
    gamma: float = 0.5  # linking
    delta: float = 0.3  # supercoiling


class RingSystem:
    """Система колец с TOP2 events"""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.rings: List[np.ndarray] = []
        self.complexity_history: List[float] = []
        np.random.seed(config.random_seed)

    def initialize_rings(self, mode: str = "random"):
        """
        Создать начальную конфигурацию колец

        Parameters
        ----------
        mode : str
            'random': случайное размещение
            'entangled': частично сцепленные (более реалистично)
        """
        self.rings = []

        if mode == "random":
            # Простые кольца в случайных позициях
            for i in range(self.config.num_rings):
                ring = create_simple_ring(radius=1.0, num_points=50)

                # Случайные сдвиги
                shift = np.random.randn(3) * 2.0
                ring += shift

                # Случайный поворот
                angle = np.random.rand() * 2 * np.pi
                axis = np.random.randn(3)
                axis /= np.linalg.norm(axis) + 1e-8
                # Упрощённый поворот (только вокруг z для toy model)
                theta = np.random.rand() * 2 * np.pi
                cos_t = np.cos(theta)
                sin_t = np.sin(theta)
                rot_z = np.array([[cos_t, -sin_t, 0], [sin_t, cos_t, 0], [0, 0, 1]])
                ring = ring @ rot_z.T

                self.rings.append(ring)

        elif mode == "entangled":
            # Создать некоторые пары сцепленных колец
            num_pairs = self.config.num_rings // 4
            for _ in range(num_pairs):
                ring1, ring2 = create_linked_rings(radius=1.0, separation=0.3)
                # Случайный сдвиг пары
                shift = np.random.randn(3) * 3.0
                self.rings.append(ring1 + shift)
                self.rings.append(ring2 + shift)

            # Остальные — простые кольца
            remaining = self.config.num_rings - 2 * num_pairs
            for _ in range(remaining):
                ring = create_simple_ring(radius=1.0)
                shift = np.random.randn(3) * 2.0
                self.rings.append(ring + shift)

    def calculate_current_complexity(self) -> float:
        """
        Вычислить текущую топологическую сложность

        Returns
        -------
        C : float
            C(G) = α|K| + β|C| + γΣ|Lk| + δΣ|σ|
        """
        # [WEAK] Для toy model упрощаем:
        # - Knots не детектируем (требует сложного алгоритма)
        # - Supercoiling = 0 (кольца, не суперкоилы)
        # - Фокус на catenanes и linking numbers

        num_knots = 0  # placeholder
        num_catenanes = calculate_catenation_simple(self.rings)

        # Linking numbers между всеми парами
        linking_numbers = []
        for i in range(len(self.rings)):
            for j in range(i + 1, len(self.rings)):
                lk = gauss_linking_integral(self.rings[i], self.rings[j])
                if abs(lk) > 0.1:  # threshold для шума
                    linking_numbers.append(int(np.round(lk)))

        supercoiling = []  # нет для простых колец

        C = calculate_complexity(
            num_knots=num_knots,
            num_catenanes=num_catenanes,
            linking_numbers=linking_numbers,
            supercoiling=supercoiling,
            alpha=self.config.alpha,
            beta=self.config.beta,
            gamma=self.config.gamma,
            delta=self.config.delta,
        )

        return C

    def simulate_top2_events(
        self, strand_passage_model: str = "random", num_steps: int = None
    ) -> List[float]:
        """
        Симулировать TOP2 strand passage события

        Parameters
        ----------
        strand_passage_model : str
            'random', 'angle', 'angle_curvature'
        num_steps : int
            Число событий (если None, использует config)

        Returns
        -------
        complexity_history : List[float]
            C(G) после каждого шага
        """
        if num_steps is None:
            num_steps = self.config.num_steps

        self.complexity_history = []

        for step in range(num_steps):
            # Вычислить текущую сложность
            C_current = self.calculate_current_complexity()
            self.complexity_history.append(C_current)

            # Выбрать случайную пару колец для возможного passage
            i = np.random.randint(0, len(self.rings))
            j = np.random.randint(0, len(self.rings))
            if i == j:
                continue

            ring1 = self.rings[i]
            ring2 = self.rings[j]

            # Вычислить вероятность passage в зависимости от модели
            if strand_passage_model == "random":
                p_passage = strand_passage_random(ring1, ring2)
            elif strand_passage_model == "angle":
                # Упрощённо: используем первую точку как crossing
                crossing_point = 0
                p_passage = strand_passage_angle_bias(ring1, ring2, crossing_point)
            elif strand_passage_model == "angle_curvature":
                crossing_point = 0
                p_passage = strand_passage_curvature_bias(ring1, ring2, crossing_point)
            else:
                raise ValueError(f"Unknown model: {strand_passage_model}")

            # Решить, происходит ли passage
            if np.random.rand() < p_passage:
                # Passage: меняем linking number
                # [SIMPLIFIED] Для toy model просто немного "разделяем" кольца
                # чтобы уменьшить сцепление

                # В реальности TOP2 меняет топологию, мы эмулируем это
                # через малое изменение позиции
                shift = np.random.randn(3) * 0.2
                self.rings[j] = self.rings[j] + shift

            # Progress
            if (step + 1) % 100 == 0:
                print(
                    f"  Step {step+1}/{num_steps}, C = {C_current:.2f}",
                    end="\r",
                )

        # Финальная сложность
        C_final = self.calculate_current_complexity()
        self.complexity_history.append(C_final)

        print()  # newline after progress
        return self.complexity_history


def run_experiment(config: ExperimentConfig) -> Dict[str, float]:
    """
    Запустить полный эксперимент: 3 модели + baseline

    Returns
    -------
    results : Dict[str, float]
        Финальная сложность для каждой модели
    """
    results = {}

    print("=" * 60)
    print("T2: TOP2 Topological Annealing — Toy Model")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Rings: {config.num_rings}")
    print(f"  Steps: {config.num_steps}")
    print(f"  Seed: {config.random_seed}")
    print()

    # Модель 1: Random (baseline)
    print("[1/3] Running RANDOM (baseline)...")
    system_random = RingSystem(config)
    system_random.initialize_rings(mode="entangled")
    C_initial = system_random.calculate_current_complexity()
    print(f"  Initial complexity: C = {C_initial:.2f}")

    history_random = system_random.simulate_top2_events(strand_passage_model="random")
    C_final_random = history_random[-1]
    print(f"  Final complexity: C = {C_final_random:.2f}")
    print(f"  Reduction: {(1 - C_final_random/C_initial)*100:.1f}%")
    print()

    results["random"] = C_final_random
    results["initial"] = C_initial

    # Модель 2: Angle-biased
    print("[2/3] Running ANGLE-BIASED...")
    system_angle = RingSystem(config)
    system_angle.initialize_rings(mode="entangled")
    history_angle = system_angle.simulate_top2_events(strand_passage_model="angle")
    C_final_angle = history_angle[-1]
    print(f"  Final complexity: C = {C_final_angle:.2f}")
    print(f"  Reduction: {(1 - C_final_angle/C_initial)*100:.1f}%")
    print()

    results["angle"] = C_final_angle

    # Модель 3: Angle + Curvature
    print("[3/3] Running ANGLE+CURVATURE...")
    system_curv = RingSystem(config)
    system_curv.initialize_rings(mode="entangled")
    history_curv = system_curv.simulate_top2_events(strand_passage_model="angle_curvature")
    C_final_curv = history_curv[-1]
    print(f"  Final complexity: C = {C_final_curv:.2f}")
    print(f"  Reduction: {(1 - C_final_curv/C_initial)*100:.1f}%")
    print()

    results["angle_curvature"] = C_final_curv

    # Сохранить histories для plotting
    results["history_random"] = history_random
    results["history_angle"] = history_angle
    results["history_curv"] = history_curv

    return results


def analyze_results(results: Dict[str, float]) -> Dict[str, float]:
    """
    Анализ результатов и проверка kill criteria

    Returns
    -------
    metrics : Dict[str, float]
        advantage_score, num_params, effect_size
    """
    C_initial = results["initial"]
    C_random = results["random"]
    C_angle = results["angle"]
    C_curv = results["angle_curvature"]

    print("=" * 60)
    print("RESULTS ANALYSIS")
    print("=" * 60)
    print(f"Initial complexity: C₀ = {C_initial:.2f}")
    print(f"Random (baseline):  C_rand = {C_random:.2f}")
    print(f"Angle-biased:       C_angle = {C_angle:.2f}")
    print(f"Angle+Curvature:    C_curv = {C_curv:.2f}")
    print()

    # Advantage scores
    advantage_angle = C_angle / C_random
    advantage_curv = C_curv / C_random

    print("Advantage Scores (C_biased / C_random):")
    print(f"  Angle:            {advantage_angle:.3f}")
    print(f"  Angle+Curvature:  {advantage_curv:.3f}")
    print()

    # Best model
    best_advantage = min(advantage_angle, advantage_curv)
    best_model = "Angle" if advantage_angle < advantage_curv else "Angle+Curvature"

    print(f"Best model: {best_model} (advantage = {best_advantage:.3f})")
    print()

    # Number of parameters
    # Angle: 1 param (β_angle)
    # Angle+Curvature: 2 params (β_angle, β_curv)
    num_params_angle = 1
    num_params_curv = 2

    num_params = num_params_curv if best_model == "Angle+Curvature" else num_params_angle

    print(f"Number of parameters: {num_params}")
    print()

    # Effect size (Cohen's d for reduction)
    # [SIMPLIFIED] Используем simple reduction ratio
    reduction_random = (C_initial - C_random) / C_initial
    reduction_best = (C_initial - min(C_angle, C_curv)) / C_initial
    effect_size = abs(reduction_best - reduction_random)

    print(f"Effect size (|Δ reduction|): {effect_size:.3f}")
    print()

    # ============================================================
    # KILL CRITERIA CHECK
    # ============================================================
    print("=" * 60)
    print("KILL CRITERIA CHECK (pre-registered)")
    print("=" * 60)

    kill = False
    reasons = []

    # Criterion 1: advantage_score
    if best_advantage > 0.8:
        kill = True
        reasons.append(f"❌ advantage_score = {best_advantage:.3f} > 0.8 (< 20% improvement)")
    else:
        print(f"✓ advantage_score = {best_advantage:.3f} <= 0.8 (PASS)")

    # Criterion 2: num_params
    if num_params > 5:
        kill = True
        reasons.append(f"❌ num_params = {num_params} > 5 (overfitting)")
    else:
        print(f"✓ num_params = {num_params} <= 5 (PASS)")

    # Criterion 3: effect_size
    if effect_size < 0.05:
        kill = True
        reasons.append(f"❌ effect_size = {effect_size:.3f} < 0.05 (too weak)")
    else:
        print(f"✓ effect_size = {effect_size:.3f} >= 0.05 (PASS)")

    print()

    # SUCCESS criterion
    success = best_advantage < 0.7 and num_params <= 3 and effect_size > 0.3

    if success:
        print("🎯 SUCCESS: advantage < 0.7 AND params <= 3 AND strong effect")
    elif not kill:
        print("⚠️  MARGINAL: passes kill criteria but not strong success")
    else:
        print("🚫 KILL TRIGGERED:")
        for reason in reasons:
            print(f"   {reason}")

    print()

    metrics = {
        "advantage_score": best_advantage,
        "num_params": num_params,
        "effect_size": effect_size,
        "kill": kill,
        "success": success,
    }

    return metrics


def plot_results(results: Dict[str, float], save_path: str = "complexity_evolution.png"):
    """Построить графики"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Complexity evolution
    steps = np.arange(len(results["history_random"]))

    ax1.plot(steps, results["history_random"], label="Random (baseline)", linewidth=2, alpha=0.8)
    ax1.plot(steps, results["history_angle"], label="Angle-biased", linewidth=2, alpha=0.8)
    ax1.plot(steps, results["history_curv"], label="Angle+Curvature", linewidth=2, alpha=0.8)

    ax1.set_xlabel("TOP2 Events", fontsize=12)
    ax1.set_ylabel("Topological Complexity C(G)", fontsize=12)
    ax1.set_title("T2: TOP2 Strand Passage Models", fontsize=14, fontweight="bold")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Plot 2: Final comparison
    models = ["Random", "Angle", "Angle+Curv"]
    C_finals = [results["random"], results["angle"], results["angle_curvature"]]
    colors = ["gray", "steelblue", "darkgreen"]

    ax2.bar(models, C_finals, color=colors, alpha=0.7, edgecolor="black")
    ax2.axhline(results["random"], color="red", linestyle="--", alpha=0.5, label="Baseline")
    ax2.set_ylabel("Final Complexity C(G)", fontsize=12)
    ax2.set_title("Final Topological Complexity", fontsize=14, fontweight="bold")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved: {save_path}")
    plt.show()


if __name__ == "__main__":
    # Создать конфигурацию
    config = ExperimentConfig(
        num_rings=200,  # Начинаем с малого для быстрого теста
        num_steps=500,  # 500 TOP2 events
        random_seed=42,
    )

    # Запустить эксперимент
    results = run_experiment(config)

    # Анализ
    metrics = analyze_results(results)

    # Визуализация
    plot_results(results)

    # Вывод в файл
    print("\n" + "=" * 60)
    print("Next steps:")
    if metrics["kill"]:
        print("  1. Document negative result in NEGATIVE_RESULT.md")
        print("  2. Pivot to D1 (spectral 3D)")
        print("  3. Update UNIFIED_FRAMEWORK.md")
    elif metrics["success"]:
        print("  1. Increase num_rings to 500 for robustness check")
        print("  2. Test parameter sensitivity")
        print("  3. Proceed to Phase 2 (T1 or H1)")
        print("  4. Draft bioRxiv preprint")
    else:
        print("  1. Review why success not achieved")
        print("  2. Consider parameter tuning (but NO goalpost moving)")
        print("  3. Decide: continue or pivot")
    print("=" * 60)
