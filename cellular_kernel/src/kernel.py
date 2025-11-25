"""APC/C (System Controller) - глобальный переключатель состояний."""


class APCC_Controller:
    """
    Anaphase Promoting Complex / Cyclosome.

    Глобальный переключатель состояний.
    """

    def __init__(self, activation_threshold: float) -> None:
        """
        Инициализация контроллера APC/C.

        Args:
            activation_threshold: Порог концентрации MCC для активации анафазы
        """
        self.threshold = activation_threshold
        self.anaphase_triggered = False

    def evaluate(self, bus_level: float) -> bool:
        """
        Оценка состояния системы и принятие решения о запуске анафазы.

        Args:
            bus_level: Текущая концентрация MCC в шине

        Returns:
            True если анафаза запущена, False иначе
        """
        # Если уровень ингибитора упал ниже порога -> ЗАПУСК
        if bus_level < self.threshold:
            self.anaphase_triggered = True
        return self.anaphase_triggered









