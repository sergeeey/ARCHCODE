"""
T2: TOP2 as Topological Annealing -- оптимизированный прогон.

Функционально идентичен `toy_model.py`. Отличие только в том, КАК считается C(G):
матрица linking numbers с инкрементальным обновлением вместо полного пересчёта.

Kill criteria (pre-registered, НЕ менялись -- см. AMENDMENTS.md A-001):
    advantage_score = C_final(biased) / C_final(random)   -- меньше = лучше
    KILL:    advantage_score > 0.8   ИЛИ num_params > 5   ИЛИ effect_size < 0.05
    SUCCESS: advantage_score < 0.7   И   num_params <= 3  И  effect_size > 0.3

Эквивалентность ядра доказана `shared_utils/test_fast_equivalence.py` (9 тестов).
Эквивалентность траектории -- `test_trajectory_equivalence.py`.

Запуск:
    python toy_model_fast.py --rings 30 --steps 500     # proof-of-concept
    python toy_model_fast.py --rings 200 --steps 500    # полный масштаб
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared_utils"))

from topology_utils import (  # noqa: E402
    create_linked_rings,
    create_simple_ring,
    strand_passage_angle_bias,
    strand_passage_curvature_bias,
    strand_passage_random,
)
from topology_utils_fast import LinkingMatrix  # noqa: E402

KILL_ADVANTAGE = 0.8
SUCCESS_ADVANTAGE = 0.7
KILL_NUM_PARAMS = 5
SUCCESS_NUM_PARAMS = 3
KILL_EFFECT_SIZE = 0.05
SUCCESS_EFFECT_SIZE = 0.3


@dataclass
class ExperimentConfig:
    num_rings: int = 200
    num_steps: int = 500
    random_seed: int = 42
    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 0.5
    delta: float = 0.3


class FastRingSystem:
    """
    Система колец, поддерживающая матрицу linking numbers.

    WHY: оригинал вызывал calculate_current_complexity() на каждом шаге, а та обходила
    все пары ДВАЖДЫ (катенаны + linking-сумма). При этом strand passage сдвигает ровно
    одно кольцо -- меняются только пары с ним. Здесь матрица строится один раз и
    обновляется построчно.
    """

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.rings: list[np.ndarray] = []
        self.matrix: LinkingMatrix | None = None
        self.complexity_history: list[float] = []
        # WHY: тот же вызов и в том же месте, что в оригинале -- последовательность
        # обращений к ГПСЧ должна совпадать, иначе траектория разойдётся при том же seed.
        np.random.seed(config.random_seed)

    def initialize_rings(self, mode: str = "entangled") -> None:
        """Порядок случайных вызовов дословно повторяет toy_model.py:62-111."""
        self.rings = []

        if mode == "random":
            for _ in range(self.config.num_rings):
                ring = create_simple_ring(radius=1.0, num_points=50)
                shift = np.random.randn(3) * 2.0
                ring = ring + shift
                _angle = np.random.rand() * 2 * np.pi  # noqa: F841  (оригинал тоже не использует)
                axis = np.random.randn(3)
                axis /= np.linalg.norm(axis) + 1e-8
                theta = np.random.rand() * 2 * np.pi
                cos_t, sin_t = np.cos(theta), np.sin(theta)
                rot_z = np.array([[cos_t, -sin_t, 0], [sin_t, cos_t, 0], [0, 0, 1]])
                self.rings.append(ring @ rot_z.T)

        elif mode == "entangled":
            num_pairs = self.config.num_rings // 4
            for _ in range(num_pairs):
                ring1, ring2 = create_linked_rings(radius=1.0, separation=0.3)
                shift = np.random.randn(3) * 3.0
                self.rings.append(ring1 + shift)
                self.rings.append(ring2 + shift)

            remaining = self.config.num_rings - 2 * num_pairs
            for _ in range(remaining):
                ring = create_simple_ring(radius=1.0)
                shift = np.random.randn(3) * 2.0
                self.rings.append(ring + shift)

        self.matrix = LinkingMatrix(self.rings)

    def current_complexity(self) -> float:
        assert self.matrix is not None, "initialize_rings() не вызван"
        return self.matrix.complexity(
            alpha=self.config.alpha,
            beta=self.config.beta,
            gamma=self.config.gamma,
            delta=self.config.delta,
        )

    def simulate(self, strand_passage_model: str, num_steps: int | None = None) -> list[float]:
        """Порядок обращений к ГПСЧ дословно повторяет toy_model.py:176-213."""
        if num_steps is None:
            num_steps = self.config.num_steps

        self.complexity_history = []

        for _ in range(num_steps):
            self.complexity_history.append(self.current_complexity())

            i = np.random.randint(0, len(self.rings))
            j = np.random.randint(0, len(self.rings))
            if i == j:
                continue

            ring1, ring2 = self.rings[i], self.rings[j]

            if strand_passage_model == "random":
                p_passage = strand_passage_random(ring1, ring2)
            elif strand_passage_model == "angle":
                p_passage = strand_passage_angle_bias(ring1, ring2, 0)
            elif strand_passage_model == "angle_curvature":
                p_passage = strand_passage_curvature_bias(ring1, ring2, 0)
            else:
                raise ValueError(f"Unknown model: {strand_passage_model}")

            if np.random.rand() < p_passage:
                shift = np.random.randn(3) * 0.2
                self.rings[j] = self.rings[j] + shift
                self.matrix.update_ring(self.rings, j)

        self.complexity_history.append(self.current_complexity())
        return self.complexity_history


def run_experiment(config: ExperimentConfig, verbose: bool = True) -> dict:
    results: dict = {}
    models = [
        ("random", "RANDOM (baseline)"),
        ("angle", "ANGLE-BIASED"),
        ("angle_curvature", "ANGLE+CURVATURE"),
    ]

    for idx, (key, label) in enumerate(models, start=1):
        t0 = time.perf_counter()
        system = FastRingSystem(config)
        system.initialize_rings(mode="entangled")

        if key == "random":
            results["initial"] = system.current_complexity()
            if verbose:
                print(f"  Initial complexity: C = {results['initial']:.2f}")

        history = system.simulate(strand_passage_model=key)
        results[key] = history[-1]
        results[f"history_{key}"] = history
        elapsed = time.perf_counter() - t0

        if verbose:
            reduction = (1 - history[-1] / results["initial"]) * 100
            print(f"[{idx}/3] {label}: C = {history[-1]:.2f}  ({reduction:+.1f}%)  {elapsed:.1f}s")

    return results


def analyze(results: dict) -> dict:
    """Проверка pre-registered критериев. Формулы -- как в toy_model.py:297-411."""
    c_initial = results["initial"]
    c_random = results["random"]
    c_angle = results["angle"]
    c_curv = results["angle_curvature"]

    # WHY: деление на ноль реально достижимо -- если baseline полностью развязал систему,
    # C_random = 0. Оригинал этого не проверял и упал бы с ZeroDivisionError/inf.
    if c_random == 0.0:
        return {
            "advantage_score": float("nan"),
            "num_params": 0,
            "effect_size": float("nan"),
            "kill": False,
            "success": False,
            "verdict": "UNDEFINED",
            "reason": "C_random = 0 -- advantage_score не определён, метрика неприменима",
        }

    adv_angle = c_angle / c_random
    adv_curv = c_curv / c_random
    best_advantage = min(adv_angle, adv_curv)
    best_model = "Angle" if adv_angle < adv_curv else "Angle+Curvature"
    num_params = 2 if best_model == "Angle+Curvature" else 1

    reduction_random = (c_initial - c_random) / c_initial
    reduction_best = (c_initial - min(c_angle, c_curv)) / c_initial
    effect_size = abs(reduction_best - reduction_random)

    reasons = []
    if best_advantage > KILL_ADVANTAGE:
        reasons.append(f"advantage_score = {best_advantage:.3f} > {KILL_ADVANTAGE}")
    if num_params > KILL_NUM_PARAMS:
        reasons.append(f"num_params = {num_params} > {KILL_NUM_PARAMS}")
    if effect_size < KILL_EFFECT_SIZE:
        reasons.append(f"effect_size = {effect_size:.3f} < {KILL_EFFECT_SIZE}")

    kill = bool(reasons)
    success = (
        best_advantage < SUCCESS_ADVANTAGE
        and num_params <= SUCCESS_NUM_PARAMS
        and effect_size > SUCCESS_EFFECT_SIZE
    )
    verdict = "SUCCESS" if success else ("KILL" if kill else "MARGINAL")

    return {
        "advantage_angle": adv_angle,
        "advantage_curvature": adv_curv,
        "advantage_score": best_advantage,
        "best_model": best_model,
        "num_params": num_params,
        "effect_size": effect_size,
        "kill": kill,
        "success": success,
        "verdict": verdict,
        "reason": "; ".join(reasons) if reasons else "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="T2 TOP2 annealing (optimized)")
    parser.add_argument("--rings", type=int, default=30, help="число колец (POSTPONED.md: 20-30)")
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="result_fast.json")
    args = parser.parse_args()

    config = ExperimentConfig(num_rings=args.rings, num_steps=args.steps, random_seed=args.seed)

    print("=" * 62)
    print(f"T2 TOP2 annealing -- rings={args.rings}, steps={args.steps}, seed={args.seed}")
    print("=" * 62)

    t0 = time.perf_counter()
    results = run_experiment(config)
    metrics = analyze(results)
    total = time.perf_counter() - t0

    print("-" * 62)
    print(f"advantage_score : {metrics['advantage_score']:.4f}   (KILL > {KILL_ADVANTAGE})")
    print(f"effect_size     : {metrics['effect_size']:.4f}   (KILL < {KILL_EFFECT_SIZE})")
    print(f"num_params      : {metrics['num_params']}")
    print(f"VERDICT         : {metrics['verdict']}")
    if metrics["reason"]:
        print(f"  reason: {metrics['reason']}")
    print(f"wall clock      : {total:.1f}s")
    print("=" * 62)

    payload = {
        "config": asdict(config),
        "metrics": metrics,
        "complexity": {
            "initial": results["initial"],
            "random": results["random"],
            "angle": results["angle"],
            "angle_curvature": results["angle_curvature"],
        },
        "wall_clock_sec": total,
        "criteria_source": "KILL_CRITERIA.md T2 (amended A-001: direction only, thresholds unchanged)",
    }
    Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"saved: {args.out}")


if __name__ == "__main__":
    main()
