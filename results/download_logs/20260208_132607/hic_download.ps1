Continue = 'Continue'
Set-Location "D:\ДНК"
"[HiC] Downloading loop calls" | Out-File -FilePath "D:\ДНК\results\download_logs\20260208_132607\hic_download.log"
npx tsx scripts/validate-hic.ts --download *>> "D:\ДНК\results\download_logs\20260208_132607\hic_download.log"
"[HiC] Done" | Out-File -FilePath "D:\ДНК\results\download_logs\20260208_132607\hic_download.log" -Append
