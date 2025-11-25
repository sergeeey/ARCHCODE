#!/bin/bash

# Скрипт для конвертации .hic файла в .cool формат
# Требует установки hic2cool: pip install hic2cool

echo "🔄 Конвертация WAPL_KO_HAP1.hic в формат .cool..."

# Проверяем наличие файла
if [ ! -f "data/real/WAPL_KO_HAP1.hic" ]; then
    echo "❌ Ошибка: Файл data/real/WAPL_KO_HAP1.hic не найден!"
    echo "   Сначала запустите download_datasets.sh"
    exit 1
fi

# Проверяем наличие hic2cool
if ! command -v hic2cool &> /dev/null; then
    echo "⚠️  hic2cool не найден. Устанавливаем..."
    pip install hic2cool
fi

# Конвертируем только разрешение 10kb (чтобы не раздувать файл)
echo "📦 Конвертируем в разрешение 10kb..."
hic2cool convert data/real/WAPL_KO_HAP1.hic data/real/WAPL_KO_HAP1_10kb.cool -r 10000

if [ $? -eq 0 ]; then
    echo "✅ Конвертация успешно завершена!"
    echo "📁 Файл сохранен: data/real/WAPL_KO_HAP1_10kb.cool"
else
    echo "❌ Ошибка при конвертации!"
    exit 1
fi








