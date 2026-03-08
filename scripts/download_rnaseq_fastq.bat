@echo off
REM ARCHCODE FASTQ Download Script (Windows)
REM Purpose: Download RNA-seq data for "Loop That Stayed" validation
REM Date: 2026-03-06
REM
REM Usage: 
REM   scripts\download_rnaseq_fastq.bat
REM
REM Samples:
REM   WT Rep1: SRR12837671
REM   D3 Rep1: SRR12837674 (3'HS1 deletion)
REM   A2 Rep1: SRR12837675 (3'HS1 inversion)

echo ============================================================
echo   ARCHCODE RNA-seq FASTQ Download
echo   'Loop That Stayed' Hypothesis Validation
echo ============================================================
echo.

REM Set output directory
set OUTPUT_DIR=%~dp0..\fastq_data\raw

REM Create directory if not exists
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo Output directory: %OUTPUT_DIR%
echo.

REM Check if fastq-dump is available
where fastq-dump >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: fastq-dump not found.
    echo.
    echo Install SRA Toolkit:
    echo   https://github.com/ncbi/sra-tools/wiki/01.-Downloading-SRA-Toolkit
    echo.
    echo Or via conda:
    echo   conda install -c bioconda sra-tools
    echo.
    pause
    exit /b 1
)

echo fastq-dump found
echo.

REM Show samples
echo Samples:
echo   1. SRR12837671 (WT Rep1)
echo   2. SRR12837674 (D3 Rep1 - 3'HS1 deletion)
echo   3. SRR12837675 (A2 Rep1 - 3'HS1 inversion)
echo.
echo Expected size: ~30 GB total
echo Estimated time: 4-6 hours
echo.

REM Get start time
echo Starting at: %DATE% %TIME%
echo.

REM Download each sample
for %%a in (SRR12837671 SRR12837674 SRR12837675) do (
    echo.
    echo Downloading %%a...
    
    REM Check if already downloaded
    if exist "%OUTPUT_DIR%\%%a_1.fastq.gz" (
        echo   Already exists, skipping...
    ) else (
        fastq-dump --split-files --gzip --progress --outdir "%OUTPUT_DIR%" %%a
        echo   Completed: %%a
    )
)

echo.
echo ============================================================
echo   Download Complete
echo ============================================================
echo.
echo Finished at: %DATE% %TIME%
echo.
echo Output files:
dir /b "%OUTPUT_DIR%\*.fastq.gz" 2>nul
echo.
echo Next step: Run RNA-seq analysis pipeline
echo   See: fastq_data\README.md
echo.
pause
