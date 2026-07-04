# Download K562 BigWig files from ENCODE for Cross-Cell Validation
# Usage: .\scripts\download-k562-data.ps1

$ErrorActionPreference = "Stop"

$DATA_DIR = "data\inputs"
$MED1_DIR = "$DATA_DIR\med1"
$HISTONE_DIR = "$DATA_DIR\histone"

# Create directories
New-Item -ItemType Directory -Force -Path $MED1_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $HISTONE_DIR | Out-Null

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ARCHCODE: Downloading K562 Data" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# H3K27ac K562 (hg38) - ENCSR000AKP
$H3K27AC_URL = "https://www.encodeproject.org/files/ENCFF038HNR/@@download/ENCFF038HNR.bigWig"
$H3K27AC_FILE = "$HISTONE_DIR\H3K27ac_K562.bw"

if (Test-Path $H3K27AC_FILE) {
    Write-Host "[OK] H3K27ac_K562.bw already exists" -ForegroundColor Green
} else {
    Write-Host "Downloading H3K27ac K562..." -ForegroundColor Yellow
    Write-Host "  Source: ENCSR000AKP (Bradley Bernstein, Broad)"
    Invoke-WebRequest -Uri $H3K27AC_URL -OutFile $H3K27AC_FILE -UseBasicParsing
    Write-Host "  Saved: $H3K27AC_FILE" -ForegroundColor Green
}

# MED1 K562 (hg38) - ENCSR269BSA
$MED1_URL = "https://www.encodeproject.org/files/ENCFF341MYG/@@download/ENCFF341MYG.bigWig"
$MED1_FILE = "$MED1_DIR\MED1_K562.bw"

if (Test-Path $MED1_FILE) {
    Write-Host "[OK] MED1_K562.bw already exists" -ForegroundColor Green
} else {
    Write-Host "Downloading MED1 K562..." -ForegroundColor Yellow
    Write-Host "  Source: ENCSR269BSA (Richard Myers, HAIB)"
    Invoke-WebRequest -Uri $MED1_URL -OutFile $MED1_FILE -UseBasicParsing
    Write-Host "  Saved: $MED1_FILE" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Download complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files:"
Get-ChildItem "$HISTONE_DIR\*.bw" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  $($_.Name) - $([math]::Round($_.Length/1MB, 2)) MB"
}
Get-ChildItem "$MED1_DIR\*.bw" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  $($_.Name) - $([math]::Round($_.Length/1MB, 2)) MB"
}
Write-Host ""
Write-Host "Run validation:" -ForegroundColor Yellow
Write-Host "  npx tsx scripts/run-cross-cell-k562.ts"
