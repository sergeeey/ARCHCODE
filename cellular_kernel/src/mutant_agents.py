"""Мутантные агенты для хаос-инжиниринга - моделирование патологических состояний."""

from src.agents import KinetochoreAgent, KinetochoreState


class MutantMAD2(KinetochoreAgent):
    """
    Мутант MAD2 - игнорирует отсутствие натяжения.

    Всегда генерирует сигнал READY, даже без правильного прикрепления.
    Это катастрофическая мутация, приводящая к анеуплоидии.
    """

    def emit_mcc_signal(self) -> float:
        """
        Мутант всегда сигнализирует READY.

        Это нарушает checkpoint и может привести к преждевременной анафазе.
        """
        return 0.0  # Всегда READY → катастрофа

    def is_ready(self) -> bool:
        """Мутант всегда считает себя готовым."""
        return True


class WeakCTCF(KinetochoreAgent):
    """
    Слабый CTCF - нестабильные границы → нестабильное натяжение.

    Моделирует клетки с нарушенной архитектурой хроматина.
    """

    def update(self, sister_state: "KinetochoreAgent", physics_params: dict) -> None:
        """
        Увеличенная нестабильность натяжения из-за слабых границ.
        """
        # Вызываем базовую логику
        super().update(sister_state, physics_params)

        # Дополнительная нестабильность: случайные сбросы натяжения
        if self.state == KinetochoreState.ATTACHED_TENSIONED:
            instability_chance = physics_params.get("ctcf_instability", 0.1)
            if self._random() < instability_chance:
                self.state = KinetochoreState.ATTACHED_RELAXED
                self.tension_stability_counter = 0

    def _random(self) -> float:
        """Вспомогательный метод для случайных чисел."""
        import random

        return random.random()


class HyperstabilizedKinetochore(KinetochoreAgent):
    """
    Гиперстабилизированный кинетохор - имитирует раковые клетки.

    Очень сильные прикрепления, которые трудно разрушить.
    Это может привести к застреванию в митозе.
    """

    def update(self, sister_state: "KinetochoreAgent", physics_params: dict) -> None:
        """
        Уменьшенная вероятность отрыва - гиперстабильность.
        """
        # Сохраняем оригинальную вероятность отрыва
        original_detach_prob = physics_params["detach_probability"]

        # Уменьшаем вероятность отрыва для гиперстабилизированного агента
        stabilization_factor = physics_params.get("hyperstabilization_factor", 0.1)
        physics_params["detach_probability"] = original_detach_prob * stabilization_factor

        # Вызываем базовую логику
        super().update(sister_state, physics_params)

        # Восстанавливаем оригинальную вероятность
        physics_params["detach_probability"] = original_detach_prob


class MerotelicDrift(KinetochoreAgent):
    """
    Меротелический дрифт - склонность к меротелии.

    Агент с повышенной вероятностью меротелии при прикреплении.
    """

    def update(self, sister_state: "KinetochoreAgent", physics_params: dict) -> None:
        """
        Увеличенная вероятность меротелии.
        """
        # Увеличиваем вероятность меротелии
        original_misattach_prob = physics_params.get("misattach_probability", 0.02)
        drift_multiplier = physics_params.get("merotelic_drift_multiplier", 5.0)
        physics_params["misattach_probability"] = original_misattach_prob * drift_multiplier

        # Вызываем базовую логику
        super().update(sister_state, physics_params)

        # Восстанавливаем оригинальную вероятность
        physics_params["misattach_probability"] = original_misattach_prob










