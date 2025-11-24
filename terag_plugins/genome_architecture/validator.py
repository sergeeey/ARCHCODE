"""
Bio-physical domain validator for ARCHCODE results.

Validates ARCHCODE experiment results against theoretical predictions
and biological constraints.
"""

from typing import Any


def validate_archcode_result(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Принимает JSON от ArchcodeAdapter.run_mission(...)

    Args:
        payload: Dictionary from ArchcodeAdapter.run_mission() with:
            - status: "success" | "error"
            - mission_type: mission type
            - data: experiment results (if success)
            - error: error message (if error)

    Returns:
        Dictionary with:
            - valid: bool
            - issues: list of issue strings
            - derived_metrics: metrics for T.R.A.C. reasoning
    """
    status = payload.get("status")
    if status != "success":
        return {
            "valid": False,
            "issues": [f"ARCHCODE returned error: {payload.get('error')}"],
            "derived_metrics": {},
        }

    data = payload.get("data", {})
    mission_type = payload.get("mission_type")

    issues = []
    derived = {}

    if mission_type == "rs09_processivity_phase":
        # Проверка фазовой структуры, порогов, гладкости поверхности
        phase_diagram = data.get("phase_diagram", {})
        crit_points = data.get("critical_points", {})
        stable_fraction = data.get("stable_fraction", 0.0)

        # Derived метрики
        derived["stable_phase_fraction"] = float(stable_fraction)
        derived["collapse_threshold"] = crit_points.get("collapse_threshold")
        derived["stable_threshold"] = crit_points.get("stable_threshold")

        # Валидация
        if stable_fraction < 0.2:
            issues.append("Too small stable phase fraction, check processivity scaling.")

        if derived["collapse_threshold"] is None:
            issues.append("Collapse threshold not detected, may need finer grid.")

        if derived["stable_threshold"] is None:
            issues.append("Stable threshold not detected, may need finer grid.")

        # Проверка теоретических предсказаний
        if derived["collapse_threshold"] is not None:
            if not (0.3 <= derived["collapse_threshold"] <= 0.7):
                issues.append(
                    f"Collapse threshold ({derived['collapse_threshold']}) "
                    f"out of expected range (0.3-0.7)."
                )

    elif mission_type == "rs10_bookmarking_threshold":
        threshold = data.get("estimated_threshold")
        bookmarking_grid = data.get("bookmarking_grid", {})

        derived["bookmark_threshold"] = float(threshold) if threshold is not None else None

        # Проверка наличия порога
        if threshold is None:
            issues.append("Bookmarking threshold not detected.")
        elif not (0.2 <= threshold <= 0.5):
            issues.append(
                f"Bookmarking threshold ({threshold}) "
                f"out of expected theoretical range (0.3–0.4)."
            )

        # Проверка тренда
        if bookmarking_grid:
            # Extract jaccard values
            jaccard_values = [
                v.get("final_jaccard", 0.0) for v in bookmarking_grid.values()
            ]
            if len(jaccard_values) > 1:
                # Check monotonicity (should increase with bookmarking)
                is_monotonic = all(
                    jaccard_values[i] <= jaccard_values[i + 1]
                    for i in range(len(jaccard_values) - 1)
                )
                if not is_monotonic:
                    issues.append(
                        "Jaccard not monotonically increasing with bookmarking fraction."
                    )

                derived["jaccard_at_0.3"] = bookmarking_grid.get("0.3", {}).get(
                    "final_jaccard", None
                )
                derived["jaccard_at_0.5"] = bookmarking_grid.get("0.5", {}).get(
                    "final_jaccard", None
                )

    elif mission_type == "rs11_multichannel_memory":
        critical_surface = data.get("critical_surface", {})
        phase_regimes = data.get("phase_regimes", {})
        critical_line = data.get("critical_line", [])

        # Derived метрики
        derived["critical_surface_points"] = len(critical_surface)
        derived["stable_memory_count"] = phase_regimes.get("stable_memory", 0)
        derived["partial_memory_count"] = phase_regimes.get("partial_memory", 0)
        derived["drift_count"] = phase_regimes.get("drift", 0)

        # Проверка наличия критической поверхности
        if len(critical_surface) == 0 and len(critical_line) == 0:
            issues.append("Critical surface/line not detected, may need finer grid.")

        # Проверка распределения режимов
        total_points = (
            derived["stable_memory_count"]
            + derived["partial_memory_count"]
            + derived["drift_count"]
        )
        if total_points > 0:
            stable_fraction = derived["stable_memory_count"] / total_points
            if stable_fraction < 0.1:
                issues.append("Too few stable memory points, check parameters.")

            # Extract example threshold
            if critical_surface:
                example_key = list(critical_surface.keys())[0]
                derived["example_threshold"] = critical_surface[example_key]

    elif mission_type == "real_hic_benchmark":
        corr_ins = data.get("insulation_correlation", 0.0)
        corr_ps = data.get("ps_correlation", 0.0)
        pass_fail = data.get("pass_fail", {})

        derived["insulation_correlation"] = float(corr_ins)
        derived["ps_correlation"] = float(corr_ps)
        derived["overall_pass"] = pass_fail.get("overall_pass", False)

        # Валидация корреляций
        if corr_ps < 0.9:
            issues.append(
                f"P(s) correlation ({corr_ps:.3f}) too low, "
                f"model does not capture polymer scaling well."
            )
        if corr_ins < 0.7:
            issues.append(
                f"Insulation correlation ({corr_ins:.3f}) too low, "
                f"TAD boundaries not well captured."
            )

        # Проверка pass/fail флагов
        if not pass_fail.get("insulation_pass", False):
            issues.append("Insulation validation failed (correlation < 0.7).")
        if not pass_fail.get("ps_pass", False):
            issues.append("P(s) validation failed (correlation < 0.9).")

    else:
        issues.append(f"Unknown mission_type: {mission_type}")

    valid = len(issues) == 0

    return {
        "valid": valid,
        "issues": issues,
        "derived_metrics": derived,
    }

