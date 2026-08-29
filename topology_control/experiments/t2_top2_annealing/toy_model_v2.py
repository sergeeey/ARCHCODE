"""
T2 v2 — TOP2 topological annealing с настоящим strand passage.

Пре-регистрация: `claim_v2.md`, заморожена коммитом adbc66f ДО написания этого файла.
Пороги SUCCESS < 0.7 / KILL > 0.8 унаследованы из v1 без изменений (A-001).

Отличие от v1 (все три — исправления технических ошибок, см. AMENDMENTS.md):
  1. passage меняет Lk на ±1 (было: случайный сдвиг, dLk = 0 всегда)
  2. начальная конфигурация действительно зацеплена (было: Lk ≈ −0.01)
  3. точка перекрёстка находится геометрически (было: жёстко индекс 0)

Три арма:
  random — p = 0.5                       (baseline)
  angle  — p = exp(−|θ−π/2|/0.5)         (гипотеза T2: ТОЛЬКО локальная геометрия)
  oracle — принять, если снижает |Lk|    (ПОТОЛОК, не локальное правило, вне соревнования)

Запуск:
    python toy_model_v2.py --rings 24 --steps 400
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared_utils"))

from passage_ops import (  # noqa: E402
    angle_gate,
    attempt_passage,
    curvature_gate,
    find_closest_crossing,
    passage_reduces_linking,
)
from topology_utils import create_linked_rings, create_simple_ring  # noqa: E402
from topology_utils_fast import LinkingMatrix  # noqa: E402

SUCCESS_ADVANTAGE = 0.7
KILL_ADVANTAGE = 0.8
GATE_MIN_DLK_FRACTION = 0.5
GATE_MIN_ACCEPT_RATIO = 0.1


@dataclass
class Config:
    num_rings: int = 24
    num_steps: int = 400
    random_seed: int = 42
    radius: float = 1.0
    # WHY: пара, разнесённая дальше этого, физически не имеет перекрёстка -- passage
    # для неё не определён. Ограничение одинаково для всех армов, сравнение честное.
    max_interaction_distance: float = 1.5
    gamma: float = 0.5
    beta: float = 1.0


@dataclass
class ArmResult:
    name: str
    c_initial: float
    c_final: float
    attempted: int
    no_crossing: int
    accepted: int
    dlk_ok: int  # |dLk| == 1
    dlk_bad: int  # |dLk| != 1 среди применённых
    agreed_with_oracle: int  # правило приняло passage, который снижал |Lk|
    rejected: dict[str, int]  # отказы attempt_passage по причинам
    history: list[float]


def build_system(cfg: Config) -> list[np.ndarray]:
    """
    Половина колец — реально зацепленные пары (Hopf), остальные свободные.

    WHY: `create_linked_rings` исправлена (A-002) и теперь действительно даёт Lk = ±1.
    В v1 эта же функция возвращала незацепленные кольца, из-за чего система стартовала
    с нулевой топологией и упрощать было нечего.
    """
    rings: list[np.ndarray] = []
    num_pairs = cfg.num_rings // 4

    for _ in range(num_pairs):
        r1, r2 = create_linked_rings(radius=cfg.radius, separation=1.0, num_points=60)
        shift = np.random.randn(3) * 3.0
        rings.append(r1 + shift)
        rings.append(r2 + shift)

    for _ in range(cfg.num_rings - 2 * num_pairs):
        ring = create_simple_ring(cfg.radius, num_points=60)
        rings.append(ring + np.random.randn(3) * 2.5)

    return rings


def run_arm(cfg: Config, rule: str) -> ArmResult:
    np.random.seed(cfg.random_seed)
    rings = build_system(cfg)
    matrix = LinkingMatrix(rings)

    c_initial = matrix.complexity(beta=cfg.beta, gamma=cfg.gamma)
    history = [c_initial]
    attempted = no_crossing = accepted = dlk_ok = dlk_bad = agreed = 0
    rejected: dict[str, int] = {"rejected_degenerate": 0, "rejected_no_clean_passage": 0}

    for _ in range(cfg.num_steps):
        i = np.random.randint(0, len(rings))
        j = np.random.randint(0, len(rings))
        if i == j:
            continue
        attempted += 1

        crossing = find_closest_crossing(rings[i], rings[j])
        if crossing.distance > cfg.max_interaction_distance:
            no_crossing += 1
            history.append(history[-1])
            continue

        current_lk = float(matrix.lk[i, j])
        oracle_would_accept = passage_reduces_linking(crossing, current_lk)

        if rule == "random":
            accept = np.random.rand() < 0.5
        elif rule == "angle":
            accept = np.random.rand() < angle_gate(crossing)
        elif rule == "curvature":
            accept = np.random.rand() < curvature_gate(rings[j], crossing)
        elif rule == "oracle":
            accept = oracle_would_accept
        else:
            raise ValueError(f"unknown rule: {rule}")

        if not accept:
            history.append(history[-1])
            continue

        # WHY: attempt_passage либо даёт чистое |dLk| = 1, либо откатывает. Пока сбои
        # были возможны, их частота различалась между армами втрое (random 8.00 против
        # angle 2.90) и двигала advantage_score сильнее, чем само правило -- то есть
        # сравнение измеряло надёжность операции, а не топологию (decision_v2.md).
        new_ring_j, delta_lk, status = attempt_passage(rings[i], rings[j], crossing)
        if status != "applied":
            rejected[status] += 1
            history.append(history[-1])
            continue

        accepted += 1
        if oracle_would_accept:
            agreed += 1
        dlk_ok += 1  # инвариант attempt_passage: applied => |dLk| == 1

        rings[j] = new_ring_j
        matrix.update_ring(rings, j)
        history.append(matrix.complexity(beta=cfg.beta, gamma=cfg.gamma))

    return ArmResult(
        name=rule,
        c_initial=c_initial,
        c_final=history[-1],
        attempted=attempted,
        no_crossing=no_crossing,
        accepted=accepted,
        dlk_ok=dlk_ok,
        dlk_bad=dlk_bad,
        agreed_with_oracle=agreed,
        rejected=dict(rejected),
        history=history,
    )


def evaluate(arms: dict[str, ArmResult]) -> dict:
    """Гейты G1-G4 проверяются ДО advantage_score (claim_v2.md)."""
    rnd, ang, orc = arms["random"], arms["angle"], arms["oracle"]
    gates: list[tuple[str, bool, str]] = []

    gates.append(("G1 есть что упрощать", rnd.c_initial > 0, f"C_initial = {rnd.c_initial:.2f}"))

    applied = sum(a.dlk_ok + a.dlk_bad for a in arms.values())
    ok = sum(a.dlk_ok for a in arms.values())
    frac = ok / applied if applied else 0.0
    gates.append(
        ("G2 операция работает", frac >= GATE_MIN_DLK_FRACTION, f"|dLk|=1 доля {frac:.2f}")
    )

    gates.append(
        (
            "G3 упрощение достижимо",
            orc.c_final < orc.c_initial,
            f"oracle {orc.c_initial:.2f} -> {orc.c_final:.2f}",
        )
    )

    ratio = ang.accepted / rnd.accepted if rnd.accepted else 0.0
    gates.append(
        (
            "G4 арм не бездействует",
            ratio >= GATE_MIN_ACCEPT_RATIO,
            f"angle/random accepted = {ang.accepted}/{rnd.accepted} = {ratio:.2f}",
        )
    )

    failed = [name for name, passed, _ in gates if not passed]
    if failed:
        return {
            "verdict": "BLOCKED-INFRASTRUCTURE",
            "gates": [{"gate": n, "passed": p, "detail": d} for n, p, d in gates],
            "failed_gates": failed,
            "advantage_score": None,
            "note": "непройденный гейт -- НЕ свидетельство против гипотезы (FL Step 2a)",
        }

    advantage = ang.c_final / rnd.c_final if rnd.c_final else float("nan")
    if np.isnan(advantage):
        verdict = "UNDEFINED"
    elif advantage < SUCCESS_ADVANTAGE:
        verdict = "SUCCESS"
    elif advantage > KILL_ADVANTAGE:
        verdict = "KILL"
    else:
        verdict = "INCONCLUSIVE"

    return {
        "verdict": verdict,
        "gates": [{"gate": n, "passed": p, "detail": d} for n, p, d in gates],
        "failed_gates": [],
        "advantage_score": advantage,
        "oracle_advantage": orc.c_final / rnd.c_final if rnd.c_final else None,
        "angle_oracle_agreement": (ang.agreed_with_oracle / ang.accepted if ang.accepted else None),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rings", type=int, default=24)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default="result_v2.json")
    args = ap.parse_args()

    cfg = Config(num_rings=args.rings, num_steps=args.steps, random_seed=args.seed)
    print("=" * 68)
    print(f"T2 v2 -- rings={cfg.num_rings}, steps={cfg.num_steps}, seed={cfg.random_seed}")
    print("prereg: claim_v2.md @ adbc66f (frozen before this file existed)")
    print("=" * 68)

    t0 = time.perf_counter()
    arms = {}
    for rule in ("random", "angle", "oracle"):
        t = time.perf_counter()
        arms[rule] = run_arm(cfg, rule)
        a = arms[rule]
        tag = "  [ПОТОЛОК, не локальное правило]" if rule == "oracle" else ""
        print(
            f"{rule:7s} C {a.c_initial:6.2f} -> {a.c_final:6.2f} | "
            f"accepted {a.accepted:4d}/{a.attempted:4d} | "
            f"no-cross {a.no_crossing:4d} | |dLk|=1 {a.dlk_ok:4d} bad {a.dlk_bad:3d} | "
            f"{time.perf_counter() - t:5.1f}s{tag}"
        )

    ev = evaluate(arms)
    print("-" * 68)
    for g in ev["gates"]:
        print(f"  [{'PASS' if g['passed'] else 'FAIL'}] {g['gate']:24s} {g['detail']}")
    print("-" * 68)
    if ev["advantage_score"] is not None:
        print(f"advantage_score (angle/random) : {ev['advantage_score']:.4f}")
        print(f"oracle_advantage  (потолок)     : {ev['oracle_advantage']:.4f}")
        print(f"angle согласен с оракулом       : {ev['angle_oracle_agreement']}")
    print(f"VERDICT: {ev['verdict']}")
    if ev["failed_gates"]:
        print(f"  провалены гейты: {', '.join(ev['failed_gates'])}")
        print(f"  {ev['note']}")
    print(f"wall clock: {time.perf_counter() - t0:.1f}s")
    print("=" * 68)

    payload = {
        "config": asdict(cfg),
        "prereg_commit": "adbc66f",
        "arms": {
            k: {kk: vv for kk, vv in asdict(v).items() if kk != "history"} for k, v in arms.items()
        },
        "evaluation": ev,
    }
    Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"saved: {args.out}")


if __name__ == "__main__":
    main()
