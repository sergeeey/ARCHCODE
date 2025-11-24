# PowerShell script для загрузки эталонных Hi-C датасетов на Windows

# Создаем директорию для данных
$dataDir = "data/real"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}

Set-Location $dataDir

Write-Host "🚀 Начинаем загрузку эталонных Hi-C датасетов..." -ForegroundColor Green
Write-Host "⚠️  Внимание: Общий объем может составить ~20-30 ГБ. Используем докачку." -ForegroundColor Yellow

# --- 1. WILD TYPE (High Processivity) ---
# Rao et al., 2014 (GM12878) from 4DNucleome
Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "⬇️  Скачивание 1/3: WT (GM12878)..." -ForegroundColor Cyan
$wtUrl = "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/4d9136c8-54b1-4eb7-a536-231a5477dc76/4DNFI1UEG1O1.mcool"
curl.exe -L -C - -o "WT_GM12878.mcool" $wtUrl

# --- 2. COHESIN LOSS / CdLS-like (Low Processivity) ---
# Rao et al., 2017 (HCT116 + Auxin treated 6h).
Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "⬇️  Скачивание 2/3: Cohesin Loss / CdLS-like (HCT116 + Auxin)..." -ForegroundColor Cyan
$cdlsUrl = "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/06a0431d-2446-4fcb-8d8e-d2ae691d786b/4DNFI2TK7L2F.mcool"
curl.exe -L -C - -o "CdLS_Like_HCT116.mcool" $cdlsUrl

# --- 3. WAPL-KO (Hyper Processivity) ---
# Haarhuis et al., 2017 (HAP1 WAPL-KO).
Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "⬇️  Скачивание 3/3: WAPL-KO (HAP1)..." -ForegroundColor Cyan
$waplUrl = "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM2496nnn/GSM2496645/suppl/GSM2496645_HAP1_WAPL_KO_inter_30.hic"
curl.exe -L -C - -o "WAPL_KO_HAP1.hic" $waplUrl

Set-Location ../..

Write-Host "✅ Загрузка завершена!" -ForegroundColor Green
Write-Host "ℹ️  Примечание: Для файла WAPL_KO_HAP1.hic потребуется конвертация в .cool" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Следующий шаг: Запустите convert_hic_to_cool.ps1 для конвертации WAPL файла" -ForegroundColor Cyan





