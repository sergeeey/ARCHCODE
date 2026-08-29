"""
Доказательство, что быстрая модель воспроизводит траекторию оригинала.

Тест ядра (`shared_utils/test_fast_equivalence.py`) доказывает, что C(G) считается
одинаково. Здесь проверяется более сильное утверждение: при одном seed обе реализации
проходят ОДНУ И ТУ ЖЕ последовательность состояний.

Это не педантизм. Если порядок обращений к np.random разойдётся хоть на один вызов,
траектории разъедутся, и «ускоренный» прогон будет измерять другой эксперимент при
внешне правдоподобных числах -- ровно тот режим отказа, который в этом проекте уже
стоил восьми карантинных файлов (gnomAD, 2026-04-28).

Запуск:
    python -m pytest test_trajectory_equivalence.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent.parent / "shared_utils"))

import toy_model as slow_mod  # noqa: E402
import toy_model_fast as fast_mod  # noqa: E402

TOL = 1e-9


def _run_slow(num_rings: int, num_steps: int, seed: int, model: str) -> list[float]:
    config = slow_mod.ExperimentConfig(num_rings=num_rings, num_steps=num_steps, random_seed=seed)
    system = slow_mod.RingSystem(config)
    system.initialize_rings(mode="entangled")
    return system.simulate_top2_events(strand_passage_model=model)


def _run_fast(num_rings: int, num_steps: int, seed: int, model: str) -> list[float]:
    config = fast_mod.ExperimentConfig(num_rings=num_rings, num_steps=num_steps, random_seed=seed)
    system = fast_mod.FastRingSystem(config)
    system.initialize_rings(mode="entangled")
    return system.simulate(strand_passage_model=model)


# WHY: 8 колец / 12 шагов -- медленная версия O(n^2) на каждом шаге, больше не поднять
# за разумное время. Этого достаточно: расхождение в порядке ГПСЧ проявляется на первом
# же несовпавшем вызове, а не накапливается медленно.
@pytest.mark.parametrize("model", ["random", "angle", "angle_curvature"])
def test_trajectory_identical(model: str):
    slow = _run_slow(num_rings=8, num_steps=12, seed=42, model=model)
    fast = _run_fast(num_rings=8, num_steps=12, seed=42, model=model)

    assert len(slow) == len(fast), f"{model}: разная длина истории {len(slow)} vs {len(fast)}"
    assert np.allclose(slow, fast, atol=TOL), (
        f"{model}: траектории разошлись\n"
        f"  первое расхождение на шаге "
        f"{int(np.argmax(~np.isclose(slow, fast, atol=TOL)))}\n"
        f"  slow={slow[:5]}\n  fast={fast[:5]}"
    )


def test_initial_state_identical():
    """Инициализация тоже потребляет ГПСЧ -- если разойдётся она, разойдётся всё."""
    cfg_s = slow_mod.ExperimentConfig(num_rings=8, num_steps=1, random_seed=42)
    sys_s = slow_mod.RingSystem(cfg_s)
    sys_s.initialize_rings(mode="entangled")

    cfg_f = fast_mod.ExperimentConfig(num_rings=8, num_steps=1, random_seed=42)
    sys_f = fast_mod.FastRingSystem(cfg_f)
    sys_f.initialize_rings(mode="entangled")

    assert len(sys_s.rings) == len(sys_f.rings)
    for k, (a, b) in enumerate(zip(sys_s.rings, sys_f.rings)):
        assert np.allclose(a, b, atol=TOL), f"кольцо {k} отличается после инициализации"

    assert abs(sys_s.calculate_current_complexity() - sys_f.current_complexity()) < TOL


def test_analyze_verdict_matches_original_logic():
    """Пороги не сдвинуты: те же входы дают тот же вердикт, что в toy_model.analyze_results."""
    results = {"initial": 100.0, "random": 50.0, "angle": 30.0, "angle_curvature": 35.0}
    metrics = fast_mod.analyze(results)

    # advantage = 30/50 = 0.6 < 0.7; effect = |0.70 - 0.50| = 0.20
    assert abs(metrics["advantage_score"] - 0.6) < TOL
    assert metrics["num_params"] == 1
    assert abs(metrics["effect_size"] - 0.2) < TOL
    # 0.6 < 0.8 -> не kill; но effect 0.2 < 0.3 -> не success => MARGINAL
    assert metrics["verdict"] == "MARGINAL"
    assert not metrics["kill"]


def test_analyze_kill_branch():
    """advantage выше порога -> KILL, с названной причиной."""
    results = {"initial": 100.0, "random": 50.0, "angle": 45.0, "angle_curvature": 48.0}
    metrics = fast_mod.analyze(results)
    assert metrics["advantage_score"] > fast_mod.KILL_ADVANTAGE
    assert metrics["verdict"] == "KILL"
    assert "advantage_score" in metrics["reason"]


def test_analyze_handles_zero_baseline():
    """C_random = 0 -> UNDEFINED, а не ZeroDivisionError и не молчаливый inf."""
    results = {"initial": 100.0, "random": 0.0, "angle": 0.0, "angle_curvature": 0.0}
    metrics = fast_mod.analyze(results)
    assert metrics["verdict"] == "UNDEFINED"
    assert not metrics["kill"] and not metrics["success"]
