"""
Phase transition утилиты для ATR Framework

Включает:
- Free energy landscapes
- Order parameters
- Phase boundary detection
- Condensate nucleation
"""

import numpy as np
from typing import Tuple, Callable, Optional
from dataclasses import dataclass


@dataclass
class PhaseState:
    """Состояние фазовой системы"""

    order_parameter: float  # φ
    free_energy: float  # F(φ)
    in_condensate: bool  # True если φ > φ_c
    basin: str  # 'low', 'high', 'transition'


def landau_free_energy(phi: float, a: float, b: float = 1.0, h: float = 0.0) -> float:
    """
    Функционал свободной энергии Ландау

    F(φ) = a φ² / 2 + b φ⁴ / 4 - h φ

    Parameters
    ----------
    phi : float
        Order parameter (концентрация, плотность)
    a : float
        Параметр, зависящий от генотипа/состояния
        a > 0: одна фаза (низкая φ)
        a < 0: две фазы (фазовый переход)
    b : float
        Стабилизирующий член (всегда > 0)
    h : float
        Внешнее поле (смещение)

    Returns
    -------
    F : float
        Свободная энергия

    Notes
    -----
    [ESTABLISHED] Модель Ландау — стандарт для фазовых переходов.

    [HYPOTHESIS-D2] Enhancer condensates описываются через φ = TF concentration,
    где a зависит от генотипа (risk vs protective).

    [HYPOTHESIS-H3] Nucleoid compaction: φ = DNA density.
    """
    F = (a / 2) * phi**2 + (b / 4) * phi**4 - h * phi
    return F


def find_phase_boundary(
    a_min: float = -2.0, a_max: float = 2.0, num_points: int = 100, b: float = 1.0
) -> float:
    """
    Найти критическое значение a, где происходит фазовый переход

    Parameters
    ----------
    a_min, a_max : float
        Диапазон сканирования
    num_points : int
        Разрешение сканирования
    b : float
        Параметр Ландау

    Returns
    -------
    a_critical : float
        Критическое значение (обычно a_c = 0 для простой модели)

    Notes
    -----
    [DERIVED-INFERENCE] При a < 0 появляется вторая фаза (condensate).
    Точка перехода: a = 0.
    """
    # Для стандартного Ландау a_c = 0
    # Но для более сложных моделей может отличаться
    return 0.0


def equilibrium_order_parameter(a: float, b: float = 1.0, h: float = 0.0) -> Tuple[float, float]:
    """
    Вычислить равновесное значение φ (минимум F)

    dF/dφ = a φ + b φ³ - h = 0

    Returns
    -------
    phi_low : float
        Минимум низкой фазы
    phi_high : float
        Минимум высокой фазы (если существует)

    Notes
    -----
    [VERIFIED-CODE] Решение кубического уравнения:
    φ (a + b φ²) = h

    Если a > 0: один минимум φ ≈ h/a
    Если a < 0: два минимума ± sqrt(-a/b) + поправка от h
    """
    if h == 0:
        # Симметричный случай
        if a > 0:
            # Один минимум в φ = 0
            return 0.0, 0.0
        else:
            # Два минимума в ± sqrt(-a/b)
            phi_high = np.sqrt(-a / b)
            phi_low = -phi_high
            return phi_low, phi_high
    else:
        # Несимметричный — нужно решать кубическое уравнение
        # Упрощённо: численно
        from scipy.optimize import minimize_scalar

        def objective(phi):
            return landau_free_energy(phi, a, b, h)

        # Ищем минимум в [0, 5]
        result = minimize_scalar(objective, bounds=(0, 5), method="bounded")
        phi_eq = result.x

        return phi_eq, phi_eq


def phase_diagram_scan(a_range: np.ndarray, h_range: np.ndarray, b: float = 1.0) -> np.ndarray:
    """
    Построить фазовую диаграмму в пространстве (a, h)

    Parameters
    ----------
    a_range : np.ndarray
        Значения параметра a
    h_range : np.ndarray
        Значения внешнего поля h
    b : float
        Параметр Ландау

    Returns
    -------
    phase_map : np.ndarray, shape (len(a_range), len(h_range))
        0 = низкая фаза, 1 = высокая фаза, 0.5 = transition

    Notes
    -----
    [INFERRED] Фазовая диаграмма показывает, где система находится
    в каждой фазе для разных генотипов (a) и условий (h).
    """
    phase_map = np.zeros((len(a_range), len(h_range)))

    for i, a in enumerate(a_range):
        for j, h in enumerate(h_range):
            phi_low, phi_high = equilibrium_order_parameter(a, b, h)

            # Классифицировать фазу
            if abs(phi_high) < 0.1:
                phase_map[i, j] = 0.0  # низкая фаза
            elif abs(phi_high) > 1.0:
                phase_map[i, j] = 1.0  # высокая фаза
            else:
                phase_map[i, j] = 0.5  # transition

    return phase_map


def nucleation_barrier(a: float, b: float = 1.0, h: float = 0.0) -> float:
    """
    Вычислить энергетический барьер нуклеации

    ΔF = F(φ_saddle) - F(φ_low)

    Returns
    -------
    barrier : float
        Высота барьера (0 если нет барьера)

    Notes
    -----
    [HYPOTHESIS-D2] Барьер определяет, насколько легко
    система переходит из low в high фазу.

    [INFERRED] Малые возмущения (SNP) могут сильно менять барьер
    вблизи фазовой границы.
    """
    # Найти saddle point: dF/dφ = 0 и d²F/dφ² < 0
    # Для Landau это φ = 0 (unstable при a < 0)

    phi_low, phi_high = equilibrium_order_parameter(a, b, h)
    phi_saddle = 0.0  # для симметричного случая

    F_low = landau_free_energy(phi_low, a, b, h)
    F_saddle = landau_free_energy(phi_saddle, a, b, h)

    barrier = F_saddle - F_low

    # Если barrier < 0, нет настоящего барьера
    return max(0.0, barrier)


def threshold_response(
    genotype_param: float, threshold: float = 0.0, steepness: float = 10.0
) -> float:
    """
    Пороговая функция отклика (sigmoidal)

    Parameters
    ----------
    genotype_param : float
        Параметр генотипа (например, a из Landau)
    threshold : float
        Критическое значение порога
    steepness : float
        Резкость перехода (больше = резче)

    Returns
    -------
    response : float
        От 0 (ниже порога) до 1 (выше порога)

    Notes
    -----
    [HYPOTHESIS-D2] Risk variants дают threshold effects:
    малое изменение генотипа → резкое изменение фенотипа
    около критического значения.
    """
    # Sigmoid function
    response = 1.0 / (1.0 + np.exp(-steepness * (genotype_param - threshold)))
    return response


def condensate_probability(
    concentration: float, critical_concentration: float, cooperativity: float = 4.0
) -> float:
    """
    Вероятность формирования конденсата

    Parameters
    ----------
    concentration : float
        Текущая концентрация (TF, coactivators)
    critical_concentration : float
        Критическая концентрация фазового перехода
    cooperativity : float
        Hill coefficient (степень кооперативности)

    Returns
    -------
    probability : float
        Вероятность конденсата (0-1)

    Notes
    -----
    [HYPOTHESIS-D2] Enhancer condensates формируются кооперативно.

    [ESTABLISHED] Hill function часто описывает такие переходы:
    P = c^n / (c_crit^n + c^n)
    """
    if concentration <= 0:
        return 0.0

    # Hill function
    probability = concentration**cooperativity / (
        critical_concentration**cooperativity + concentration**cooperativity
    )

    return probability


def snp_phase_effect(
    genotype: str, a_protective: float = 0.5, a_risk: float = -0.5, b: float = 1.0
) -> Tuple[float, float]:
    """
    Моделировать эффект SNP на фазовое состояние

    Parameters
    ----------
    genotype : str
        'protective', 'risk', или 'heterozygous'
    a_protective : float
        Параметр для protective allele
    a_risk : float
        Параметр для risk allele
    b : float
        Ландау параметр

    Returns
    -------
    phi_eq : float
        Равновесное значение order parameter
    free_energy : float
        Свободная энергия в минимуме

    Notes
    -----
    [HYPOTHESIS-D2] Risk SNP сдвигает a ниже критического,
    переводя систему в конденсатную фазу.
    """
    if genotype == "protective":
        a = a_protective
    elif genotype == "risk":
        a = a_risk
    elif genotype == "heterozygous":
        a = (a_protective + a_risk) / 2
    else:
        raise ValueError(f"Unknown genotype: {genotype}")

    phi_low, phi_high = equilibrium_order_parameter(a, b, h=0)
    phi_eq = phi_high if abs(phi_high) > abs(phi_low) else phi_low

    F_eq = landau_free_energy(phi_eq, a, b, h=0)

    return phi_eq, F_eq


# ============================================================
# Для H3: Nucleoid compaction
# ============================================================


def compaction_free_energy(
    density: float,
    damage: float = 0.0,
    marks: float = 0.0,
    a0: float = 1.0,
    gamma: float = 0.5,
    eta: float = 0.3,
) -> float:
    """
    Свободная энергия нуклеоида с учётом повреждений и меток

    F(ρ) = (a₀ + γ·D + η·M) ρ²/2 + b ρ⁴/4

    Parameters
    ----------
    density : float
        Плотность упаковки нуклеоида
    damage : float
        Уровень oxidative damage
    marks : float
        Уровень эпигенетических меток
    a0 : float
        Базовый параметр
    gamma, eta : float
        Веса для damage и marks

    Returns
    -------
    F : float
        Свободная энергия

    Notes
    -----
    [HYPOTHESIS-H3] Повреждения и метки сдвигают фазовый порог
    нуклеоидной упаковки.
    """
    a_eff = a0 + gamma * damage + eta * marks
    F = landau_free_energy(density, a=a_eff, b=1.0, h=0)
    return F


def accessibility_from_compaction(density: float, alpha: float = 2.0) -> float:
    """
    Доступность ДНК как функция плотности упаковки

    A = σ(-α ρ + θ)

    где σ — sigmoid

    Parameters
    ----------
    density : float
        Плотность нуклеоида
    alpha : float
        Чувствительность к плотности

    Returns
    -------
    accessibility : float
        0 (закрыто) до 1 (открыто)

    Notes
    -----
    [HYPOTHESIS-H3] Высокая плотность → низкая доступность для репликации.
    """
    theta = 1.0  # threshold
    logit = -alpha * density + theta
    accessibility = 1.0 / (1.0 + np.exp(-logit))
    return accessibility


if __name__ == "__main__":
    # Smoke test
    print("Phase utils loaded successfully")

    # Test 1: Landau free energy
    phi_range = np.linspace(-2, 2, 100)

    # a > 0: одна фаза
    F_single = [landau_free_energy(phi, a=1.0) for phi in phi_range]
    min_idx = np.argmin(F_single)
    print(f"Single phase minimum at φ = {phi_range[min_idx]:.2f}")

    # a < 0: две фазы
    F_double = [landau_free_energy(phi, a=-1.0) for phi in phi_range]
    phi_low, phi_high = equilibrium_order_parameter(a=-1.0)
    print(f"Double phase minima at φ = {phi_low:.2f}, {phi_high:.2f}")

    # Test 2: SNP effect
    phi_prot, F_prot = snp_phase_effect("protective", a_protective=0.5)
    phi_risk, F_risk = snp_phase_effect("risk", a_risk=-0.5)
    print(f"Protective: φ = {phi_prot:.2f}, F = {F_prot:.3f}")
    print(f"Risk: φ = {phi_risk:.2f}, F = {F_risk:.3f}")
    print(f"ΔF = {F_risk - F_prot:.3f}")

    # Test 3: Threshold response
    a_values = np.linspace(-1, 1, 50)
    responses = [threshold_response(a, threshold=0.0) for a in a_values]
    print(f"Threshold at a=0: response changes from {responses[0]:.2f} to {responses[-1]:.2f}")
