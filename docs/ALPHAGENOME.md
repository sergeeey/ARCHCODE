# 🔬 AlphaGenome Integration

**AlphaGenome** — это ИИ-модель от Google DeepMind для предсказания структуры и функции ДНК.

ARCHCODE интегрируется с AlphaGenome для валидации физических симуляций.

---

## 📋 Что такое AlphaGenome

| Характеристика | Описание |
|----------------|----------|
| **Разработчик** | Google DeepMind |
| **Тип** | Deep Learning (Transformer-based) |
| **Input** | До 1 Мб последовательности ДНК |
| **Output** | Contact maps, chromatin accessibility, CTCF binding, gene expression |
| **API** | REST API с rate limiting |
| **Стоимость** | Бесплатно для non-commercial research |

---

## 🔧 Настройка интеграции

### 1. Получение API ключа

1. Зайди на [deepmind.google.com/science/alphagenome](https://deepmind.google.com/science/alphagenome)
2. Нажми "Get API key"
3. Заполни форму:
   - Institution: твой университет/институт
   - Use case: "Research on chromatin loop extrusion modeling"
   - Agreement: Non-commercial use
4. Получишь ключ по email (обычно в течение 24 часов)

### 2. Настройка в приложении

#### Через Web UI:
```
1. Открой http://localhost:5173
2. В правой панели найди "🔑 AlphaGenome API Key"
3. Вставь ключ в поле ввода
4. Нажми "🔍 Validate with AlphaGenome"
```

#### Через CLI:
```bash
# Установи переменную окружения
export ALPHAGENOME_API_KEY="your-api-key-here"

# Или используй флаг
node scripts/validate-alphagenome.js -k "your-api-key-here"
```

---

## 🚀 Использование

### Вариант 1: Web Interface

1. Загрузи CTCF данные (ENCODE или свой BED)
2. Запусти симуляцию (▶ Run)
3. В панели "AlphaGenome Validation" нажми "Validate"
4. Смотри результаты:
   - **Pearson r** — корреляция матриц (-1 до 1, >0.8 отлично)
   - **Spearman ρ** — ранговая корреляция
   - **RMSE** — среднеквадратичная ошибка
   - **Difference Map** — визуализация различий

### Вариант 2: CLI Script

```bash
# Базовая валидация
node scripts/validate-alphagenome.js

# Конкретный интервал
node scripts/validate-alphagenome.js -i chr11:5000000-5500000

# Свои CTCF данные
node scripts/validate-alphagenome.js -c data/input/ctcf/my_ctcf.bed
```

---

## 📊 Интерпретация результатов

### Pearson Correlation (r)

| Значение | Интерпретация |
|----------|---------------|
| r > 0.8 | ✅ **Отлично** — симуляция точно воспроизводит предсказания ИИ |
| 0.6 < r < 0.8 | ⚠️ **Хорошо** — разумное согласие, есть отклонения |
| r < 0.6 | ❌ **Плохо** — модель требует настройки |

### Что делать при плохой корреляции?

1. **Проверь CTCF позиции** — используются ли правильные пики?
2. **Настрой скорость экструзии** — попробуй 500-2000 bp/step
3. **Проверь ориентацию** — convergent (R...F) должны формировать петли
4. **Увеличь разрешение** — попробуй 5kb bins вместо 10kb

---

## 🔍 Сравнение ARCHCODE vs AlphaGenome

| Аспект | ARCHCODE | AlphaGenome |
|--------|----------|-------------|
| **Подход** | Физическая симуляция | Машинное обучение |
| **Explainability** | ✅ White box (понятная физика) | ❌ Black box (attention maps) |
| **Скорость** | ⚡ Миллисекунды | 🌐 Секунды (API latency) |
| **Гибкость** | ✅ Меняй параметры | ❌ Фиксированная модель |
| **Ground Truth** | Модель | Экспериментальные данные |

**Синергия:** Используй AlphaGenome как "ground truth" для калибровки ARCHCODE!

---

## 🧪 Примеры использования

### Пример 1: Валидация HBB локуса
```typescript
const interval = {
    chromosome: 'chr11',
    start: 5240000,  // HBB gene
    end: 5340000     // 100kb window
};

// Твоя симуляция
const archcodeMatrix = simulate(interval, ctcfSites);

// AlphaGenome предсказание
const validation = await alphaGenome.validateArchcode(interval, archcodeMatrix);

// Ожидаем: r > 0.75 для корректной модели
console.log(`Pearson r: ${validation.pearsonCorrelation}`);
```

### Пример 2: Сравнение wild type vs deletion
```typescript
// WT
const wtMatrix = simulate(interval, wtCTCF);
const wtValidation = await validate(wtMatrix);

// DEL (удалён один CTCF)
const delMatrix = simulate(interval, delCTCF);
const delValidation = await validate(delMatrix);

// Разница должна коррелировать с экспериментом
```

---

## ⚠️ Ограничения

1. **Rate Limiting** — ~1M запросов/день (достаточно для research)
2. **Non-commercial** — нельзя использовать для коммерческих продуктов
3. **Sequence-only** — AlphaGenome не знает о CTCF ориентации напрямую
4. **Resolution** — 10kb оптимально, 1kb возможно но медленнее

---

## 📚 Полезные ссылки

- [AlphaGenome Homepage](https://deepmind.google.com/science/alphagenome)
- [API Documentation](https://deepmind.google.com/science/alphagenome/api)

---

## 💡 Советы

1. **Начни с GM12878** — стандартная клеточная линия, много данных
2. **Проверяй CTCF ориентацию** — convergent пары должны давать петли
3. **Используй разницу (diff map)** — показывает где модель отклоняется
4. **Сохраняй результаты** — сравнивай версии модели

---

**Готов к валидации?** Вставь API ключ и нажми "Validate with AlphaGenome"!
