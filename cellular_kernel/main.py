"""Точка входа симуляции - главный цикл."""

import yaml
from src.agents import KinetochoreAgent
from src.bus import AnalogBus
from src.kernel import APCC_Controller
from src.mutant_agents import (
    HyperstabilizedKinetochore,
    MerotelicDrift,
    MutantMAD2,
    WeakCTCF,
)
from src.verifier import LTLVerifier


def load_config() -> dict:
    """Загрузка конфигурации из YAML файла."""
    with open("config/vizier_protocol.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_simulation() -> None:
    """Главный цикл симуляции митоза."""
    cfg = load_config()
    sys_params = cfg["system_parameters"]
    bus_params = cfg["bus_parameters"]

    # 1. Инициализация Hardware (Агенты)
    agents: list[KinetochoreAgent] = []
    total_k = sys_params["total_chromosomes"] * sys_params["kinetochores_per_chr"]

    # Параметры мутантов (можно настроить в конфиге)
    mutant_config = cfg.get("mutant_config", {})
    use_mutants = mutant_config.get("enabled", False)
    mutant_types = mutant_config.get("types", {})

    for i in range(0, total_k, 2):
        # Пары сестринских кинетохоров
        pair_id = i // 2

        # Определяем тип агента (нормальный или мутант)
        if use_mutants:
            # Проверяем, должен ли этот агент быть мутантом
            if pair_id in mutant_types.get("mad2", []):
                k1 = MutantMAD2(
                    i,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
                k2 = MutantMAD2(
                    i + 1,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
            elif pair_id in mutant_types.get("weak_ctcf", []):
                k1 = WeakCTCF(
                    i,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
                k2 = WeakCTCF(
                    i + 1,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
            elif pair_id in mutant_types.get("hyperstabilized", []):
                k1 = HyperstabilizedKinetochore(
                    i,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
                k2 = HyperstabilizedKinetochore(
                    i + 1,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
            elif pair_id in mutant_types.get("merotelic_drift", []):
                k1 = MerotelicDrift(
                    i,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
                k2 = MerotelicDrift(
                    i + 1,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
            else:
                # Нормальный агент
                k1 = KinetochoreAgent(
                    i,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
                k2 = KinetochoreAgent(
                    i + 1,
                    pair_id,
                    sys_params["physics"]["tension_threshold"],
                    sys_params["physics"]["noise_level"],
                )
        else:
            # Все агенты нормальные
            k1 = KinetochoreAgent(
                i,
                pair_id,
                sys_params["physics"]["tension_threshold"],
                sys_params["physics"]["noise_level"],
            )
            k2 = KinetochoreAgent(
                i + 1,
                pair_id,
                sys_params["physics"]["tension_threshold"],
                sys_params["physics"]["noise_level"],
            )
        agents.extend([k1, k2])

    # 2. Инициализация шины и ядра
    cytoplasm_bus = AnalogBus(bus_params["mcc_degradation_rate"])
    apcc = APCC_Controller(bus_params["apc_activation_threshold"])
    verifier = LTLVerifier()

    print("--- CELLULAR KERNEL SIMULATION START ---")
    print(f"Nodes: {len(agents)}, Threshold: {bus_params['apc_activation_threshold']}")
    if use_mutants:
        print("[MUTANTS] ⚠️  Mutant agents enabled:")
        for mutant_type, pairs in mutant_types.items():
            if pairs:
                print(f"  - {mutant_type}: {len(pairs)} chromosome pairs")

    # 3. Главный цикл (Main Loop)
    system_limits = cfg.get("system_limits", {})
    max_mitosis_time = system_limits.get("max_mitosis_time", 200)
    apoptosis_threshold = system_limits.get("apoptosis_threshold", 250)
    max_ticks = max(max_mitosis_time, apoptosis_threshold)

    mitosis_arrested = False
    apoptosis_triggered = False
    for tick in range(max_ticks):
        # A. Обновление агентов
        total_mcc_flux = 0.0
        ready_count = 0
        misattached_count = 0

        for i in range(0, len(agents), 2):
            k1 = agents[i]
            k2 = agents[i + 1]

            # Обмен состоянием (физическая связь через центромеру)
            k1.update(k2, sys_params["physics"])
            k2.update(k1, sys_params["physics"])

            # Сбор сигналов
            flux = k1.emit_mcc_signal() + k2.emit_mcc_signal()
            total_mcc_flux += flux * bus_params["mcc_production_rate"]

            # Подсчет готовых и меротелических кинетохоров
            if k1.is_ready():
                ready_count += 1
            if k2.is_ready():
                ready_count += 1

            if k1.is_misattached():
                misattached_count += 1
                verifier.log_misattachment(tick, k1.uid)
            if k2.is_misattached():
                misattached_count += 1
                verifier.log_misattachment(tick, k2.uid)

        # B. Обновление шины
        cytoplasm_bus.update(total_mcc_flux)

        # C. Решение ядра
        is_anaphase = apcc.evaluate(cytoplasm_bus.mcc_concentration)

        # D. LTL Verification (Runtime)
        all_ready = ready_count == len(agents)
        verifier.check_safety(tick, all_ready, is_anaphase, misattached_count)

        # E. Global time-outs (митотический арест и апоптоз)
        if tick >= max_mitosis_time and not mitosis_arrested:
            mitosis_arrested = True
            print(f"\n[MITOTIC ARREST] ⚠️  Mitosis arrested at tick {tick} (p53 activation)")
            print(f"[MITOTIC ARREST] System stuck: Ready {ready_count}/{len(agents)}, MCC: {cytoplasm_bus.mcc_concentration:.2f}")

        if tick >= apoptosis_threshold and not apoptosis_triggered:
            apoptosis_triggered = True
            print(f"\n[APOPTOSIS] 💀 Apoptosis triggered at tick {tick} (cell death)")
            print("[APOPTOSIS] Mitosis exceeded maximum safe duration")
            break

        # Логирование
        if tick % 10 == 0 or is_anaphase or misattached_count > 0 or mitosis_arrested:
            misattach_str = f" | Misattached: {misattached_count}" if misattached_count > 0 else ""
            arrest_str = " | ARRESTED" if mitosis_arrested else ""
            print(
                f"T={tick:03d} | MCC: {cytoplasm_bus.mcc_concentration:.2f} | "
                f"Ready: {ready_count}/{len(agents)}{misattach_str}{arrest_str} | Anaphase: {is_anaphase}"
            )
        if is_anaphase:
            print(f"--- ANAPHASE TRIGGERED AT TICK {tick} ---")
            break

    # 4. Итоги
    verifier.report()

    if mitosis_arrested and not is_anaphase:
        print("\n[FINAL STATE] ⚠️  Mitosis arrested - cell cycle checkpoint activated")
    if apoptosis_triggered:
        print("\n[FINAL STATE] 💀 Apoptosis - cell death due to excessive mitosis duration")
    elif is_anaphase:
        print("\n[FINAL STATE] ✅ Anaphase completed successfully")


if __name__ == "__main__":
    run_simulation()

