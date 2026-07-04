$ErrorActionPreference = "Continue"
$logDir = "D:\ДНК\results\download_logs\20260208_130436"

"=== START $(Get-Date) ===" | Out-File -FilePath (Join-Path $logDir "run_all_downloads.log")

# 1) FASTQ RNA-seq downloads
try {
  Set-Location "D:\ДНК\fastq_data\raw"
  "[FASTQ] Starting" | Out-File -FilePath (Join-Path $logDir "fastq_download.log")
  fastq-dump --split-files --gzip SRR12837671 SRR12837674 SRR12837675 *>> (Join-Path $logDir "fastq_download.log")
  "[FASTQ] Done" | Out-File -FilePath (Join-Path $logDir "fastq_download.log") -Append
} catch {
  $_ | Out-File -FilePath (Join-Path $logDir "fastq_download.log") -Append
}

# 2) ClinVar VCF + hg38 reference
try {
  Set-Location "D:\ДНК"
  "[ClinVar] Downloading" | Out-File -FilePath (Join-Path $logDir "clinvar_download.log")
  if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
    curl.exe -O https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz *>> (Join-Path $logDir "clinvar_download.log")
  } else {
    Invoke-WebRequest -Uri https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz -OutFile "D:\ДНК\clinvar.vcf.gz" *>> (Join-Path $logDir "clinvar_download.log")
  }

  "[hg38] Downloading" | Out-File -FilePath (Join-Path $logDir "hg38_download.log")
  if (Get-Command wget.exe -ErrorAction SilentlyContinue) {
    wget.exe http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz *>> (Join-Path $logDir "hg38_download.log")
  } else {
    Invoke-WebRequest -Uri http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz -OutFile "D:\ДНК\hg38.fa.gz" *>> (Join-Path $logDir "hg38_download.log")
  }

  "[ClinVar] Gunzip" | Out-File -FilePath (Join-Path $logDir "clinvar_download.log") -Append
  python - <<'PY'
import gzip, shutil, os
src = r"D:\ДНК\clinvar.vcf.gz"
dst = r"D:\ДНК\clinvar.vcf"
if os.path.exists(src) and not os.path.exists(dst):
    with gzip.open(src, 'rb') as f_in, open(dst, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
PY

  "[hg38] Gunzip" | Out-File -FilePath (Join-Path $logDir "hg38_download.log") -Append
  python - <<'PY'
import gzip, shutil, os
src = r"D:\ДНК\hg38.fa.gz"
dst = r"D:\ДНК\hg38.fa"
if os.path.exists(src) and not os.path.exists(dst):
    with gzip.open(src, 'rb') as f_in, open(dst, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
PY
} catch {
  $_ | Out-File -FilePath (Join-Path $logDir "clinvar_download.log") -Append
}

# 3) Hi-C loop calls download
try {
  Set-Location "D:\ДНК"
  "[HiC] Downloading loop calls" | Out-File -FilePath (Join-Path $logDir "hic_download.log")
  npx tsx scripts/validate-hic.ts --download *>> (Join-Path $logDir "hic_download.log")
  "[HiC] Done" | Out-File -FilePath (Join-Path $logDir "hic_download.log") -Append
} catch {
  $_ | Out-File -FilePath (Join-Path $logDir "hic_download.log") -Append
}

"=== END $(Get-Date) ===" | Out-File -FilePath (Join-Path $logDir "run_all_downloads.log") -Append
