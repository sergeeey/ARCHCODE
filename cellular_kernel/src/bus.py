"""Цитоплазма/MCC (Shared Analog Bus) - аналоговая шина данных."""


class AnalogBus:
    """
    Моделирует цитоплазму как общую шину данных.

    MCC (Mitotic Checkpoint Complex) - это аналоговая величина.
    """

    def __init__(self, degradation_rate: float) -> None:
        """Инициализация шины с начальной концентрацией MCC."""
        self.mcc_concentration = 100.0  # Start high
        self.degradation_rate = degradation_rate
        self.history: list[float] = []

    def update(self, input_flux: float) -> None:
        """
        Обновление концентрации MCC в шине.

        Args:
            input_flux: Входящий поток ингибитора от кинетохоров
        """
        # Распад старого сигнала
        self.mcc_concentration *= 1.0 - self.degradation_rate

        # Добавление нового сигнала от кинетохоров
        self.mcc_concentration += input_flux

        # Физическое ограничение (не может быть < 0)
        self.mcc_concentration = max(0.0, self.mcc_concentration)

        self.history.append(self.mcc_concentration)











