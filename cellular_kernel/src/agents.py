"""Кинетохоры (Hardware Agents) - локальные FSM узлы."""

import random
from dataclasses import dataclass
from enum import Enum


class KinetochoreState(Enum):
    """Состояния кинетохора в процессе митоза."""

    DETACHED = 0
    ATTACHED_RELAXED = 1
    ATTACHED_TENSIONED = 2
    MISATTACHED = 3  # Меротелия: прикреплен к двум полюсам одновременно


@dataclass
class KinetochoreAgent:
    """Агент кинетохора - моделирует поведение одного кинетохора."""

    uid: int
    pair_id: int  # ID хромосомы

    # Физические параметры
    tension_threshold: float
    noise_sigma: float

    # Текущее состояние
    state: KinetochoreState = KinetochoreState.DETACHED
    current_tension: float = 0.0
    misattachment_counter: int = 0  # Счетчик тиков в состоянии меротелии
    tension_stability_counter: int = 0  # Счетчик тиков с достаточным натяжением

    def update(self, sister_state: "KinetochoreAgent", physics_params: dict) -> None:
        """
        Симуляция физики и принятие решения.

        Кинетохор - это конечный автомат с вероятностными переходами.
        """
        # 1. Логика прикрепления/отрыва (Stochastic Physics)
        if self.state == KinetochoreState.DETACHED:
            if random.random() < physics_params["attach_probability"]:
                # Вероятность меротелии при прикреплении
                if random.random() < physics_params.get("misattach_probability", 0.02):
                    self.state = KinetochoreState.MISATTACHED
                    self.misattachment_counter = 0
                else:
                    self.state = KinetochoreState.ATTACHED_RELAXED
        elif self.state != KinetochoreState.DETACHED:
            # Вероятность отрыва зависит от состояния
            detach_prob = physics_params["detach_probability"]
            # MISATTACHED более нестабилен
            if self.state == KinetochoreState.MISATTACHED:
                detach_prob *= physics_params.get("misattach_detach_multiplier", 2.0)

            if random.random() < detach_prob:
                self.state = KinetochoreState.DETACHED
                self.current_tension = 0.0
                self.misattachment_counter = 0

        # 2. Логика натяжения (Tension Sensing)
        # Меротелия может создавать ложное натяжение
        if self.state == KinetochoreState.MISATTACHED:
            self.misattachment_counter += 1
            # Меротелия создает нестабильное натяжение (ложный сигнал)
            false_tension = 0.5 + random.gauss(0, self.noise_sigma * 2)
            self.current_tension = max(0.0, false_tension)
            # Меротелия НЕ может перейти в TENSIONED (это ошибка)
            return

        # Натяжение возникает только если ОБА (сестра и я) прикреплены правильно
        if (
            self.state != KinetochoreState.DETACHED
            and self.state != KinetochoreState.MISATTACHED
            and sister_state.state != KinetochoreState.DETACHED
            and sister_state.state != KinetochoreState.MISATTACHED
        ):
            # Идеальное натяжение + шум
            base_tension = 1.0
            noise = random.gauss(0, self.noise_sigma)
            measured_tension = base_tension + noise
            self.current_tension = measured_tension

            # Aurora B stability filter: натяжение должно держаться N тиков подряд
            stability_window = physics_params.get("tension_stability_window", 3)

            if measured_tension >= self.tension_threshold:
                # Увеличиваем счетчик стабильности
                self.tension_stability_counter += 1

                # Переход в TENSIONED только после стабильного периода
                if self.tension_stability_counter >= stability_window:
                    self.state = KinetochoreState.ATTACHED_TENSIONED
                else:
                    # Еще не стабильно, остаемся в RELAXED
                    self.state = KinetochoreState.ATTACHED_RELAXED
            else:
                # Натяжение недостаточно - сбрасываем счетчик стабильности
                self.tension_stability_counter = 0
                self.state = KinetochoreState.ATTACHED_RELAXED

                # WAPL-like unloading: при низком натяжении увеличивается вероятность отрыва
                relaxed_threshold = physics_params.get("wapl_relaxed_threshold", 0.5)
                wapl_unload_probability = physics_params.get("wapl_unload_probability", 0.005)

                if measured_tension < relaxed_threshold:
                    # Вероятность отрыва увеличивается при низком натяжении
                    unload_chance = wapl_unload_probability * (1.0 - measured_tension / relaxed_threshold)
                    if random.random() < unload_chance:
                        self.state = KinetochoreState.DETACHED
                        self.current_tension = 0.0
                        self.tension_stability_counter = 0
        else:
            self.current_tension = 0.0
            self.tension_stability_counter = 0

    def emit_mcc_signal(self) -> float:
        """
        Генерация ингибирующего сигнала (Mad2/BubR1).

        Если я не в состоянии TENSIONED, я кричу 'STOP'.
        MISATTACHED также генерирует сигнал STOP (это ошибка).
        """
        if self.state == KinetochoreState.ATTACHED_TENSIONED:
            return 0.0
        # MISATTACHED тоже должен блокировать анафазу
        return 1.0  # Unit output of inhibitor

    def is_ready(self) -> bool:
        """Проверка, готов ли кинетохор к анафазе."""
        return self.state == KinetochoreState.ATTACHED_TENSIONED

    def is_misattached(self) -> bool:
        """Проверка наличия меротелии."""
        return self.state == KinetochoreState.MISATTACHED


