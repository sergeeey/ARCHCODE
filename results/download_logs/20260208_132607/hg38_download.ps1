Continue = 'Continue'
Set-Location "D:\ДНК"
"[hg38] Downloading" | Out-File -FilePath "D:\ДНК\results\download_logs\20260208_132607\hg38_download.log"
if (Get-Command wget.exe -ErrorAction SilentlyContinue) {
  wget.exe http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz *>> "D:\ДНК\results\download_logs\20260208_132607\hg38_download.log"
} else {
  Invoke-WebRequest -Uri http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz -OutFile "D:\ДНК\hg38.fa.gz" *>> "D:\ДНК\results\download_logs\20260208_132607\hg38_download.log"
}
"[hg38] Done" | Out-File -FilePath "D:\ДНК\results\download_logs\20260208_132607\hg38_download.log" -Append
