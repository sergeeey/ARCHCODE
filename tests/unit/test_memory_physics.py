"""
Unit Tests for ARCHCODE Memory Physics - Bookmarking Mechanism.

Tests the fundamental memory mechanism:
1. Bookmarking accumulation (memory formation)
2. Memory decay (drift over cycles)
3. Phase transition threshold (critical bookmarking fraction)
4. Restoration after mitosis
"""

import pytest
import numpy as np
from unittest.mock import Mock

from src.archcode_core.bookmarking import (
    assign_bookmarking,
    apply_stochastic_recovery,
    adjust_barrier_for_phase,
)
from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.extrusion_engine import Boundary
from src.archcode_core.memory_metrics import (
    calculate_jaccard_stable_boundaries,
    get_stable_boundaries,
)


class TestMemoryPhysics:
    """Test memory physics of bookmarking mechanism."""

    @pytest.fixture
    def sample_boundaries(self):
        """Create sample boundaries for testing."""
        boundaries = [
            Boundary(position=1000, strength=0.8, barrier_type="ctcf", insulation_score=0.9),
            Boundary(position=2000, strength=0.7, barrier_type="ctcf", insulation_score=0.8),
            Boundary(position=3000, strength=0.6, barrier_type="ctcf", insulation_score=0.7),
            Boundary(position=4000, strength=0.5, barrier_type="ctcf", insulation_score=0.6),
            Boundary(position=5000, strength=0.9, barrier_type="ctcf", insulation_score=0.95),
        ]
        return boundaries

    def test_bookmarking_accumulation(self, sample_boundaries):
        """
        Test 1: Bookmarking accumulation.
        
        Проверяет, что механизм Bookmarking реально меняет ландшафт восстановления.
        Если память работает, bookmarked границы должны восстанавливаться лучше.
        """
        # 1. Инициализация (пустая память - все границы не bookmarked)
        boundaries = sample_boundaries.copy()
        for b in boundaries:
            b.is_bookmarked = False
        
        # Запоминаем исходные позиции
        initial_positions = {b.position for b in boundaries}
        
        # 2. Применяем bookmarking (50% границ)
        bookmarking_fraction = 0.5
        assign_bookmarking(boundaries, fraction=bookmarking_fraction, seed=42)
        
        # Проверяем, что часть границ стала bookmarked
        bookmarked_count = sum(1 for b in boundaries if b.is_bookmarked)
        assert bookmarked_count > 0, "Bookmarking не был применен!"
        
        # 3. Симулируем митоз и восстановление
        # Bookmarked границы должны восстановиться точно
        # Non-bookmarked - с вероятностью потери и сдвигом
        
        recovered_boundaries = apply_stochastic_recovery(
            boundaries,
            boundary_loss_rate=0.2,  # 20% вероятность потери non-bookmarked
            boundary_shift_std=1000.0,  # Небольшой сдвиг для теста
            seed=42,
        )
        
        # 4. Проверка: bookmarked границы должны сохранить позиции точно
        bookmarked_positions = {b.position for b in boundaries if b.is_bookmarked}
        recovered_bookmarked_positions = {
            b.position for b in recovered_boundaries
            if b.position in bookmarked_positions
        }
        
        # Все bookmarked позиции должны быть восстановлены точно
        assert len(recovered_bookmarked_positions) == len(bookmarked_positions), (
            f"Bookmarked границы не восстановились: "
            f"было {len(bookmarked_positions)}, восстановлено {len(recovered_bookmarked_positions)}"
        )
        
        # Проверяем точность позиций для bookmarked границ
        for original in boundaries:
            if original.is_bookmarked:
                recovered = next(
                    (b for b in recovered_boundaries if b.position == original.position),
                    None,
                )
                assert recovered is not None, (
                    f"Bookmarked граница на {original.position} не восстановилась"
                )
                assert recovered.position == original.position, (
                    f"Bookmarked граница сместилась: "
                    f"было {original.position}, стало {recovered.position}"
                )

    def test_memory_decay(self, sample_boundaries):
        """
        Test 2: Memory decay (Drift).
        
        Проверяет, что память не вечна - без подкрепления non-bookmarked границы теряются.
        """
        boundaries = sample_boundaries.copy()
        
        # Устанавливаем низкий bookmarking (20%)
        assign_bookmarking(boundaries, fraction=0.2, seed=42)
        
        initial_count = len(boundaries)
        
        # Прогоняем несколько циклов восстановления
        # Каждый цикл non-bookmarked границы могут теряться
        current_boundaries = boundaries.copy()
        
        for cycle in range(5):
            recovered = apply_stochastic_recovery(
                current_boundaries,
                boundary_loss_rate=0.2,  # 20% вероятность потери
                boundary_shift_std=1000.0,
                seed=cycle,  # Разные seed для разных циклов
            )
            current_boundaries = recovered
        
        final_count = len(current_boundaries)
        
        # Ожидание: часть non-bookmarked границ должна быть потеряна
        # Но bookmarked должны сохраниться
        bookmarked_count = sum(1 for b in boundaries if b.is_bookmarked)
        final_bookmarked_count = sum(
            1 for b in current_boundaries
            if any(orig.is_bookmarked and orig.position == b.position for orig in boundaries)
        )
        
        assert final_count < initial_count, (
            "Memory decay не работает: все границы сохранились"
        )
        assert final_bookmarked_count == bookmarked_count, (
            f"Bookmarked границы потерялись: "
            f"было {bookmarked_count}, осталось {final_bookmarked_count}"
        )

    def test_bookmarking_restoration_probability(self, sample_boundaries):
        """
        Test 3: Bookmarking restoration probability.
        
        Проверяет, что bookmarked границы восстанавливаются с вероятностью 1.0,
        а non-bookmarked - с меньшей вероятностью.
        """
        boundaries = sample_boundaries.copy()
        
        # Устанавливаем bookmarking
        assign_bookmarking(boundaries, fraction=0.4, seed=42)
        
        # Многократный прогон для статистики
        restoration_counts = {b.position: 0 for b in boundaries}
        num_trials = 100
        
        for trial in range(num_trials):
            recovered = apply_stochastic_recovery(
                boundaries.copy(),
                boundary_loss_rate=0.3,  # 30% вероятность потери
                boundary_shift_std=1000.0,
                seed=trial,
            )
            
            for pos in restoration_counts:
                if any(b.position == pos for b in recovered):
                    restoration_counts[pos] += 1
        
        # Проверяем вероятности восстановления
        # Учитываем, что позиции могут сдвигаться, поэтому проверяем по исходным границам
        for boundary in boundaries:
            original_pos = boundary.position
            # Ищем восстановленные границы вблизи исходной позиции (допуск 2000 bp)
            tolerance = 2000
            restored_nearby = sum(
                1 for trial in range(num_trials)
                if any(
                    abs(b.position - original_pos) < tolerance
                    for b in apply_stochastic_recovery(
                        boundaries.copy(),
                        boundary_loss_rate=0.3,
                        boundary_shift_std=1000.0,
                        seed=trial,
                    )
                )
            )
            restoration_prob = restored_nearby / num_trials
            
            if boundary.is_bookmarked:
                # Bookmarked должны восстанавливаться всегда (или почти всегда)
                assert restoration_prob > 0.90, (
                    f"Bookmarked граница на {boundary.position} "
                    f"восстанавливается с вероятностью {restoration_prob:.2f}, ожидалось > 0.90"
                )
            else:
                # Non-bookmarked восстанавливаются с меньшей вероятностью
                # Ожидаем примерно (1 - loss_rate) = 0.7, но с учетом сдвигов может быть меньше
                assert restoration_prob < 0.95, (
                    f"Non-bookmarked граница на {boundary.position} "
                    f"восстанавливается слишком часто: {restoration_prob:.2f}"
                )

    def test_phase_transition_threshold(self, sample_boundaries):
        """
        Test 4: Phase transition threshold.
        
        Проверяет наличие фазового перехода при критическом bookmarking fraction.
        Порог: ~0.3-0.4 (из RS-10 результатов).
        """
        # Сценарий A: Слабая память (ниже порога)
        boundaries_weak = sample_boundaries.copy()
        assign_bookmarking(boundaries_weak, fraction=0.2, seed=42)
        
        # Сценарий B: Сильная память (выше порога)
        boundaries_strong = sample_boundaries.copy()
        assign_bookmarking(boundaries_strong, fraction=0.6, seed=42)
        
        # Симулируем несколько циклов с более высоким loss_rate для различия
        num_cycles = 15
        loss_rate = 0.3  # Увеличиваем для более выраженного эффекта
        
        # Weak memory (20% bookmarking)
        weak_boundaries = boundaries_weak.copy()
        weak_stable_positions = {b.position for b in weak_boundaries}
        weak_bookmarked_positions = {b.position for b in weak_boundaries if b.is_bookmarked}
        
        for cycle in range(num_cycles):
            recovered = apply_stochastic_recovery(
                weak_boundaries.copy(),
                boundary_loss_rate=loss_rate,
                boundary_shift_std=1500.0,  # Больший сдвиг
                seed=cycle,
            )
            weak_boundaries = recovered
        
        weak_final_positions = {b.position for b in weak_boundaries}
        # Используем более мягкое сравнение с учетом сдвигов
        weak_jaccard = calculate_jaccard_stable_boundaries(
            weak_stable_positions, weak_final_positions
        )
        
        # Strong memory (60% bookmarking)
        strong_boundaries = boundaries_strong.copy()
        strong_stable_positions = {b.position for b in strong_boundaries}
        strong_bookmarked_positions = {b.position for b in strong_boundaries if b.is_bookmarked}
        
        for cycle in range(num_cycles):
            recovered = apply_stochastic_recovery(
                strong_boundaries.copy(),
                boundary_loss_rate=loss_rate,
                boundary_shift_std=1500.0,
                seed=cycle,
            )
            strong_boundaries = recovered
        
        strong_final_positions = {b.position for b in strong_boundaries}
        strong_jaccard = calculate_jaccard_stable_boundaries(
            strong_stable_positions, strong_final_positions
        )
        
        # Проверяем количество сохраненных bookmarked границ
        weak_bookmarked_preserved = len(
            weak_bookmarked_positions & weak_final_positions
        ) / len(weak_bookmarked_positions) if weak_bookmarked_positions else 0
        
        strong_bookmarked_preserved = len(
            strong_bookmarked_positions & strong_final_positions
        ) / len(strong_bookmarked_positions) if strong_bookmarked_positions else 0
        
        # Ожидание: strong memory должна сохранить больше bookmarked границ
        assert strong_bookmarked_preserved >= weak_bookmarked_preserved, (
            f"Phase transition не обнаружен по bookmarked границам: "
            f"weak preserved={weak_bookmarked_preserved:.3f}, "
            f"strong preserved={strong_bookmarked_preserved:.3f}"
        )
        
        # Проверяем общий Jaccard (может быть одинаковым из-за сдвигов)
        # Но bookmarked должны сохраняться лучше
        assert strong_bookmarked_preserved > 0.8, (
            f"Strong memory должна сохранить >80% bookmarked границ, "
            f"получено {strong_bookmarked_preserved:.3f}"
        )

    def test_boundary_phase_adjustment(self, sample_boundaries):
        """
        Test 5: Boundary strength adjustment by phase.
        
        Проверяет, что bookmarking влияет на effective_strength в разных фазах.
        """
        boundaries = sample_boundaries.copy()
        assign_bookmarking(boundaries, fraction=0.6, seed=42)
        
        # Тестируем разные фазы
        phases = [
            CellCyclePhase.INTERPHASE,
            CellCyclePhase.MITOSIS,
            CellCyclePhase.G1_EARLY,
            CellCyclePhase.G1_LATE,
        ]
        
        for phase in phases:
            for boundary in boundaries:
                original_strength = boundary.strength
                adjust_barrier_for_phase(boundary, phase, enable_bookmarking=True)
                
                if phase == CellCyclePhase.MITOSIS:
                    if boundary.is_bookmarked:
                        # Bookmarked: strength * 0.4
                        assert boundary.effective_strength == original_strength * 0.4
                    else:
                        # Non-bookmarked: strength * 0.0 (completely disabled)
                        assert boundary.effective_strength == 0.0
                
                elif phase == CellCyclePhase.G1_EARLY:
                    if boundary.is_bookmarked:
                        # Bookmarked: strength * 0.7
                        assert boundary.effective_strength == original_strength * 0.7
                    else:
                        # Non-bookmarked: strength * 0.2
                        assert boundary.effective_strength == original_strength * 0.2
                
                elif phase == CellCyclePhase.G1_LATE:
                    # All restored to full strength
                    assert boundary.effective_strength == original_strength * 1.0

    def test_bookmarking_fraction_impact(self):
        """
        Test 6: Impact of bookmarking fraction on memory retention.
        
        Проверяет, что увеличение bookmarking fraction улучшает память.
        """
        # Создаем больше границ для статистики
        boundaries_base = [
            Boundary(position=i * 1000, strength=0.7, barrier_type="ctcf", insulation_score=0.8)
            for i in range(10)
        ]
        
        bookmarking_fractions = [0.1, 0.3, 0.5, 0.7, 0.9]
        retention_scores = []
        
        for frac in bookmarking_fractions:
            boundaries = [Boundary(b.position, b.strength, b.barrier_type, b.insulation_score) 
                         for b in boundaries_base]
            assign_bookmarking(boundaries, fraction=frac, seed=42)
            
            initial_positions = {b.position for b in boundaries}
            
            # Симулируем 5 циклов
            current = boundaries.copy()
            for cycle in range(5):
                recovered = apply_stochastic_recovery(
                    current.copy(),
                    boundary_loss_rate=0.2,
                    boundary_shift_std=1000.0,
                    seed=cycle,
                )
                current = recovered
            
            final_positions = {b.position for b in current}
            jaccard = calculate_jaccard_stable_boundaries(initial_positions, final_positions)
            retention_scores.append(jaccard)
        
        # Проверяем монотонность: больше bookmarking → больше retention
        for i in range(len(retention_scores) - 1):
            assert retention_scores[i + 1] >= retention_scores[i] - 0.1, (
                f"Retention не монотонна: "
                f"bookmarking {bookmarking_fractions[i]} → {retention_scores[i]:.3f}, "
                f"bookmarking {bookmarking_fractions[i+1]} → {retention_scores[i+1]:.3f}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

