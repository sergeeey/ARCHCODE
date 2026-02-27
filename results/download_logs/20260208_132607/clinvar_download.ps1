Continue = 'Continue'
Set-Location "D:\ДНК"
"[ClinVar] Downloading" | Out-File -FilePath "D:\ДНК\results\download_logs\20260208_132607\clinvar_download.log"
if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
  curl.exe -O https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz *>> "D:\ДНК\results\download_logs\20260208_132607\clinvar_download.log"
} else {
  Invoke-WebRequest -Uri https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz -OutFile "D:\ДНК\clinvar.vcf.gz" *>> "D:\ДНК\results\download_logs\20260208_132607\clinvar_download.log"
}
"[ClinVar] Done" | Out-File -FilePath "D:\ДНК\results\download_logs\20260208_132607\clinvar_download.log" -Append
