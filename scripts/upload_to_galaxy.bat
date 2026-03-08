@echo off
REM Galaxy FTP Upload Script
REM Быстрая загрузка FASTQ файлов через FTP

echo ============================================================
echo   Galaxy FTP Upload
echo ============================================================
echo.

REM Настройки FTP
set FTP_HOST=ftp.usegalaxy.org
set FTP_USER=YOUR_EMAIL_HERE
set FTP_PASS=YOUR_PASSWORD_HERE

REM Папка с FASTQ файлами
set FASTQ_DIR=D:\ДНК\fastq_data\raw

echo Подключение к Galaxy FTP...
echo.

REM Перейти в директорию с FASTQ
cd /d "%FASTQ_DIR%"

REM Загрузить каждый файл
echo Загрузка SRR12935486_1.fastq.gz...
curl -T SRR12935486_1.fastq.gz ftp://%FTP_USER%:%FTP_PASS%@%FTP_HOST%/

echo Загрузка SRR12935486_2.fastq.gz...
curl -T SRR12935486_2.fastq.gz ftp://%FTP_USER%:%FTP_PASS%@%FTP_HOST%/

echo Загрузка SRR12935488_1.fastq.gz...
curl -T SRR12935488_1.fastq.gz ftp://%FTP_USER%:%FTP_PASS%@%FTP_HOST%/

echo Загрузка SRR12935488_2.fastq.gz...
curl -T SRR12935488_2.fastq.gz ftp://%FTP_USER%:%FTP_PASS%@%FTP_HOST%/

echo Загрузка SRR12935490_1.fastq.gz...
curl -T SRR12935490_1.fastq.gz ftp://%FTP_USER%:%FTP_PASS%@%FTP_HOST%/

echo Загрузка SRR12935490_2.fastq.gz...
curl -T SRR12935490_2.fastq.gz ftp://%FTP_USER%:%FTP_PASS%@%FTP_HOST%/

echo.
echo ============================================================
echo   Загрузка завершена!
echo ============================================================
echo.
pause
