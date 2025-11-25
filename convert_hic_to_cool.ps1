# PowerShell script для конвертации .hic файла в .cool формат
# Требует установки hic2cool: pip install hic2cool

Write-Host "🔄 Конвертация WAPL_KO_HAP1.hic в формат .cool..." -ForegroundColor Cyan

# Проверяем наличие файла
if (-not (Test-Path "data/real/WAPL_KO_HAP1.hic")) {
    Write-Host "❌ Ошибка: Файл data/real/WAPL_KO_HAP1.hic не найден!" -ForegroundColor Red
    Write-Host "   Сначала запустите download_datasets.ps1" -ForegroundColor Yellow
    exit 1
}

# Проверяем наличие hic2cool
$hic2coolInstalled = python -c "import hic2cool" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  hic2cool не найден. Устанавливаем..." -ForegroundColor Yellow
    pip install hic2cool
}

# Конвертируем только разрешение 10kb (чтобы не раздувать файл)
Write-Host "📦 Конвертируем в разрешение 10kb..." -ForegroundColor Cyan
python -c "import hic2cool; hic2cool.convert('data/real/WAPL_KO_HAP1.hic', 'data/real/WAPL_KO_HAP1_10kb.cool', 10000)"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Конвертация успешно завершена!" -ForegroundColor Green
    Write-Host "📁 Файл сохранен: data/real/WAPL_KO_HAP1_10kb.cool" -ForegroundColor Green
} else {
    Write-Host "❌ Ошибка при конвертации!" -ForegroundColor Red
    exit 1
}








