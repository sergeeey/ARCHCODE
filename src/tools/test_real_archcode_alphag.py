"""
Test Cross-Omics Orthogonality Detector на реальных данных ARCHCODE × AlphaGenome

Ожидаемый результат: ORTHOGONAL (ρ ≈ 0.077 из ADR-028)
"""

import json
import numpy as np
from orthogonality_detector import classify_orthogonality, print_result

# Загрузка данных
print("Загрузка реальных данных ARCHCODE × AlphaGenome...")
with open("../../results/alphagenome_pearl_vs_control.json", "r") as f:
    data = json.load(f)

# Извлечение массивов
A = []  # ARCHCODE SSIM
B = []  # AlphaGenome CAGE %
labels = []  # PEARL=1, CONTROL=0

for variant in data["results"]:
    A.append(variant["archcode_ssim"])
    B.append(variant["cage_pct"])
    labels.append(1 if variant["group"] == "PEARL" else 0)

A = np.array(A)
B = np.array(B)
labels = np.array(labels)

print(f"\nДанные загружены:")
print(f"  N = {len(A)} variants")
print(f"  PEARL (pathogenic): {sum(labels)} variants")
print(f"  CONTROL (benign): {sum(1-labels)} variants")
print(f"  ARCHCODE SSIM range: [{A.min():.4f}, {A.max():.4f}]")
print(f"  AlphaGenome CAGE % range: [{B.min():.2f}%, {B.max():.2f}%]")

# Классификация
print("\n" + "=" * 70)
print("ТЕСТ: ARCHCODE (structural) × AlphaGenome (functional)")
print("=" * 70)

result = classify_orthogonality(A, B, labels)
print_result(result)

# Проверка ожидаемого результата
print("\n" + "=" * 70)
print("ВЕРИФИКАЦИЯ ПРОТИВ ADR-028 (2026-05-08)")
print("=" * 70)

expected_rho = 0.077  # из ADR-028: concordance analysis
tolerance = 0.05

if abs(result["rho"] - expected_rho) < tolerance:
    print(
        f"✅ Корреляция СОВПАДАЕТ: {result['rho']:.3f} ≈ {expected_rho:.3f} (в пределах ±{tolerance})"
    )
else:
    print(f"⚠️  Корреляция ОТЛИЧАЕТСЯ: {result['rho']:.3f} vs ожидаемые {expected_rho:.3f}")
    print(f"   Разница: {abs(result['rho'] - expected_rho):.3f} > tolerance {tolerance}")

if result["classification"] == "ORTHOGONAL":
    print(f"✅ Классификация ПРАВИЛЬНАЯ: {result['classification']}")
    print(f"\n🎯 ВЫВОД: Детектор корректно определил ортогональность ARCHCODE × AlphaGenome!")
elif result["classification"] == "AMBIGUOUS" and abs(result["rho"]) < 0.2:
    print(f"⚠️  Классификация AMBIGUOUS (близко к ортогональности)")
    print(f"   Возможно один из методов слабее (проверьте p_diff_A, p_diff_B)")
else:
    print(f"❌ Классификация НЕВЕРНАЯ: {result['classification']}")
    print(f"   Ожидалось: ORTHOGONAL")

# Дополнительный анализ
print("\n" + "=" * 70)
print("ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ")
print("=" * 70)

print(f"\nОба метода значимо разделяют группы:")
print(
    f"  ARCHCODE: p = {result['p_diff_A']:.4f} {'✅ <0.05' if result['p_diff_A'] < 0.05 else '❌ ≥0.05'}"
)
print(
    f"  AlphaGenome: p = {result['p_diff_B']:.4f} {'✅ <0.05' if result['p_diff_B'] < 0.05 else '❌ ≥0.05'}"
)

print(f"\nКорреляция методов: ρ = {result['rho']:.3f}")
print(
    f"  Интерпретация: {'Близка к нулю — ортогональны ✅' if abs(result['rho']) < 0.3 else 'Умеренная/высокая ⚠️'}"
)

print(f"\nВывод из ADR-028:")
print(f"  'ARCHCODE structural fragility (SSIM) и AlphaGenome functional disruption (CAGE)")
print(f"   измеряют ОРТОГОНАЛЬНЫЕ механизмы патогенности — не конкурируют, а ДОПОЛНЯЮТ.'")

print("\n✅ Тест завершён!")
