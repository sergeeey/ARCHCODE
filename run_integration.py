import yaml
import json
import os
import sys

# Добавляем текущую директорию в путь, чтобы видеть пакеты
sys.path.append(os.getcwd())

from src.integration.archcode_adapter import ArchcodeAdapter

def main():
    mission_path = "missions/rs11_memory_scan.yaml"
    
    if not os.path.exists(mission_path):
        print(f"❌ Mission file not found: {mission_path}")
        return

    with open(mission_path, "r") as f:
        mission_config = yaml.safe_load(f)
    
    # Инициализация
    adapter = ArchcodeAdapter(mode='fast')
    
    # Запуск
    print(f"🚀 Launching Mission: {mission_config['mission']['name']}")
    result = adapter.run_mission(mission_config)
    
    # Вывод
    print("\n✅ Mission Complete!")
    print(json.dumps(result, indent=2))
    
    # Сохранение
    os.makedirs("data/output", exist_ok=True)
    with open("data/output/RS11_integration_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()