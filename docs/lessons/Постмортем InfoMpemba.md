---
tags:
  - lessons
  - postmortem
  - infompemba
  - neural-networks
created: '2026-04-12'
project: InfoMpemba
---
# Постмортем InfoMpemba

**Проект:** Верификация эффекта Мпемба в динамике обучения нейросетей (KL-дивергенция, метрика Фишера)
**Период:** ~2026-04 (1-2 сессии)
**Статус:** FROZEN at 80%. Pilot собран, verdict не получен.

## Что это

Гипотеза: "горячая" (дестабилизированная) инициализация нейросети сходится быстрее "холодной" (близкой к оптимуму). Аналог физического эффекта Мпемба (горячая вода замерзает быстрее). Измеряется через KL-дивергенцию к эталону в информационной геометрии Фишера.

4 модуля: initializers.py, langevin_sgd.py, fisher_metrics.py, mpemba_runner.py. RTX 5070 Ti, PyTorch nightly.

## Результат (pilot, 50 runs)

- Cold KL mean = 4.53, Hot KL mean = 8.63
- Пересечения нет — hot остаётся выше cold
- Вероятно эффект отсутствует, но формальный verdict не сделан

## Положительные уроки

1. **ТЗ промышленного уровня ДО кода** — 120+ строк формального ТЗ с H0/H1
2. **Quick-test -> pilot -> full** — не инвестируй 15 часов GPU без пилота
3. **Kill criteria в notebook** — 50-step persistence + Welch t-test, автовердикт
4. **Минимальный scope** — 4 модуля, нет UI/API/dashboard/54 markdown
5. **Воспроизводимость** — deterministic algorithms, seed control, Dockerfile

## Отрицательные уроки

6. **Pilot собран, не проанализирован** — notebook не запущен, verdict нет
7. **Нет publication target** — куда публиковать negative result?
8. **Нет baseline из литературы** — какой crossing rate ожидается?
9. **Замёрз на 80%** — всё готово, но последние 20% не сделаны

up:: [[Каталог проектов — 7 постмортемов]]
