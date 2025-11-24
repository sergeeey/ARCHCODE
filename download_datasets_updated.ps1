# PowerShell script для загрузки эталонных Hi-C датасетов (обновленная версия)
# Включает проверку доступности и альтернативные источники

$dataDir = "data/real"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}

Write-Host "🚀 Начинаем загрузку эталонных Hi-C датасетов..." -ForegroundColor Green
Write-Host "⚠️  Внимание: Общий объем может составить ~20-30 ГБ." -ForegroundColor Yellow
Write-Host ""

# Функция для проверки доступности URL
function Test-Url {
    param([string]$url)
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10 -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Функция для загрузки с проверкой
function Download-File {
    param(
        [string]$url,
        [string]$outputFile,
        [string]$description
    )
    
    Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "⬇️  $description" -ForegroundColor Cyan
    
    if (Test-Url $url) {
        Write-Host "   URL доступен, начинаю загрузку..." -ForegroundColor Green
        try {
            curl.exe -L --progress-bar -C - -o $outputFile $url
            if (Test-Path $outputFile -PathType Leaf) {
                $size = (Get-Item $outputFile).Length
                if ($size -gt 1MB) {
                    Write-Host "   ✅ Загружено: $([math]::Round($size/1GB, 2)) GB" -ForegroundColor Green
                    return $true
                } else {
                    Write-Host "   ⚠️  Файл слишком маленький, возможно ошибка" -ForegroundColor Yellow
                    return $false
                }
            }
        } catch {
            Write-Host "   ❌ Ошибка загрузки: $_" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "   ❌ URL недоступен (404 или таймаут)" -ForegroundColor Red
        Write-Host "   💡 Используйте альтернативные источники (см. DATA_DOWNLOAD_MANUAL.md)" -ForegroundColor Yellow
        return $false
    }
}

# Список URL для попытки загрузки
$downloads = @(
    @{
        Name = "WT_GM12878.mcool"
        URLs = @(
            "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/4d9136c8-54b1-4eb7-a536-231a5477dc76/4DNFI1UEG1O1.mcool",
            "https://data.4dnucleome.org/files-processed/4DNFI1UEG1O1/"
        )
        Description = "Скачивание 1/3: WT (GM12878) - Rao et al., 2014"
        GEO = "GSE63525"
    },
    @{
        Name = "CdLS_Like_HCT116.mcool"
        URLs = @(
            "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/06a0431d-2446-4fcb-8d8e-d2ae691d786b/4DNFI2TK7L2F.mcool",
            "https://data.4dnucleome.org/files-processed/4DNFI2TK7L2F/"
        )
        Description = "Скачивание 2/3: Cohesin Loss / CdLS-like (HCT116 + Auxin) - Rao et al., 2017"
        GEO = "GSE104333"
    },
    @{
        Name = "WAPL_KO_HAP1.hic"
        URLs = @(
            "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM2496nnn/GSM2496645/suppl/GSM2496645_HAP1_WAPL_KO_inter_30.hic",
            "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE95014"
        )
        Description = "Скачивание 3/3: WAPL-KO (HAP1) - Haarhuis et al., 2017"
        GEO = "GSE95014"
    }
)

Set-Location $dataDir

$results = @()

foreach ($item in $downloads) {
    $success = $false
    foreach ($url in $item.URLs) {
        if ($url -match "data\.4dnucleome\.org|ncbi\.nih\.gov/geo/query") {
            # Это порталы, не прямые ссылки
            Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
            Write-Host "📋 $($item.Description)" -ForegroundColor Cyan
            Write-Host "   ⚠️  Требуется ручная загрузка через портал:" -ForegroundColor Yellow
            Write-Host "   🔗 $url" -ForegroundColor Cyan
            Write-Host "   📊 GEO Accession: $($item.GEO)" -ForegroundColor Gray
            Write-Host "   💡 Инструкции см. в DATA_DOWNLOAD_MANUAL.md" -ForegroundColor Yellow
            $results += @{Name = $item.Name; Status = "Manual"; URL = $url}
            break
        } else {
            $success = Download-File -url $url -outputFile $item.Name -description $item.Description
            if ($success) {
                $results += @{Name = $item.Name; Status = "Success"}
                break
            }
        }
    }
    
    if (-not $success -and -not ($url -match "data\.4dnucleome\.org|ncbi\.nih\.gov/geo/query")) {
        $results += @{Name = $item.Name; Status = "Failed"}
    }
}

Set-Location ../..

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "📊 ИТОГОВЫЙ СТАТУС" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

foreach ($result in $results) {
    $icon = switch ($result.Status) {
        "Success" { "✅" }
        "Manual" { "📋" }
        default { "❌" }
    }
    Write-Host "$icon $($result.Name): $($result.Status)" -ForegroundColor $(if ($result.Status -eq "Success") { "Green" } elseif ($result.Status -eq "Manual") { "Yellow" } else { "Red" })
}

Write-Host ""
Write-Host "💡 Для файлов со статусом 'Manual' используйте:" -ForegroundColor Yellow
Write-Host "   1. Портал 4DNucleome: https://data.4dnucleome.org/" -ForegroundColor Cyan
Write-Host "   2. GEO: https://www.ncbi.nlm.nih.gov/geo/" -ForegroundColor Cyan
Write-Host "   3. См. инструкции в DATA_DOWNLOAD_MANUAL.md" -ForegroundColor Cyan

if ($results | Where-Object { $_.Status -eq "Success" }) {
    Write-Host ""
    Write-Host "✅ Некоторые файлы успешно загружены!" -ForegroundColor Green
    Write-Host "📋 Для WAPL файла запустите: convert_hic_to_cool.ps1" -ForegroundColor Cyan
}




