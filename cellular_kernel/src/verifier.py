"""LTL Runtime Verification Engine - проверка инвариантов безопасности."""


class LTLVerifier:
    """Runtime верификатор LTL свойств для проверки безопасности системы."""

    def __init__(self) -> None:
        """Инициализация верификатора."""
        self.violations: list[str] = []
        self.misattachment_events: list[tuple[int, int]] = []  # (tick, agent_id)

    def check_safety(
        self,
        tick: int,
        all_agents_ready: bool,
        anaphase_triggered: bool,
        misattached_count: int = 0,
    ) -> bool:
        """
        Проверка формулы: G ( !ALL_READY -> !ANAPHASE )

        Если не все готовы, но анафаза запущена -> FATAL ERROR (Рак).
        Меротелия также считается нарушением безопасности.

        Args:
            tick: Текущий тик симуляции
            all_agents_ready: Все ли агенты в состоянии READY
            anaphase_triggered: Запущена ли анафаза
            misattached_count: Количество кинетохоров в состоянии меротелии

        Returns:
            True если проверка пройдена, False если нарушение
        """
        if anaphase_triggered and not all_agents_ready:
            msg = (
                f"[LTL VIOLATION] Tick {tick}: "
                f"Anaphase Triggered while system NOT ready!"
            )
            self.violations.append(msg)
            return False

        # Меротелия - критическая ошибка
        if misattached_count > 0:
            if anaphase_triggered:
                msg = (
                    f"[LTL VIOLATION] Tick {tick}: "
                    f"Anaphase Triggered with {misattached_count} MISATTACHED kinetochores!"
                )
                self.violations.append(msg)
                return False

        return True

    def log_misattachment(self, tick: int, agent_id: int) -> None:
        """Логирование события меротелии."""
        self.misattachment_events.append((tick, agent_id))

    def report(self) -> None:
        """Вывод отчета о результатах верификации."""
        if not self.violations:
            print("\n[VERIFIER] ✅ SAFETY CHECK PASSED. System is robust.")
        else:
            print(f"\n[VERIFIER] ❌ SAFETY VIOLATIONS FOUND ({len(self.violations)}):")
            for v in self.violations:
                print(v)

        if self.misattachment_events:
            print(f"\n[MISATTACHMENT] ⚠️  Total misattachment events: {len(self.misattachment_events)}")
            unique_agents = len({agent_id for _, agent_id in self.misattachment_events})
            print(f"[MISATTACHMENT] Affected agents: {unique_agents}")


