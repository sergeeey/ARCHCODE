"""Quick test of TERAG ↔ ARCHCODE integration."""

from src.integration.archcode_adapter import ArchcodeAdapter

print("=== 🧪 БЫСТРАЯ ПРОВЕРКА ИНТЕГРАЦИИ ===")
print()

# Test adapter import
print("1️⃣ Тест импорта адаптера...")
try:
    adapter = ArchcodeAdapter(mode="fast")
    print("   ✅ Адаптер импортирован успешно")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    exit(1)

# Test RS-09 mission
print("\n2️⃣ Тест RS-09 миссии...")
mission = {
    "id": "RS09-TEST",
    "mission_type": "rs09_processivity_phase",
    "parameters": {
        "processivity_min": 0.0,
        "processivity_max": 2.0,
        "processivity_steps": 5,  # Very small for quick test
    },
}

try:
    result = adapter.run_mission(mission)
    print(f"   ✅ Миссия выполнена: {result['status']}")
    print(f"   ⏱️  Время: {result['execution_time_sec']}s")
    if result["status"] == "success":
        print(f"   📊 Данные получены: {len(str(result['data']))} символов")
    else:
        print(f"   ❌ Ошибка: {result.get('error', 'Unknown')}")
except Exception as e:
    print(f"   ❌ Ошибка выполнения: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Быстрая проверка завершена!")

