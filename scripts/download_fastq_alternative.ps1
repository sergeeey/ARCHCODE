# ARCHCODE FASTQ Download Script (PowerShell)
# Alternative method - direct download without SRA Toolkit
#
# Usage: 
#   powershell -ExecutionPolicy Bypass -File scripts\download_fastq_alternative.ps1
#
# Samples:
#   WT Rep1: SRR12837671
#   D3 Rep1: SRR12837674 (3'HS1 deletion)
#   A2 Rep1: SRR12837675 (3'HS1 inversion)

Write-Host "============================================================"
Write-Host "  ARCHCODE RNA-seq FASTQ Download (PowerShell)"
Write-Host "  'Loop That Stayed' Hypothesis Validation"
Write-Host "============================================================"
Write-Host ""

# Output directory
$outputDir = Join-Path $PSScriptRoot "..\fastq_data\raw"
Write-Host "Output directory: $outputDir"
Write-Host ""

# Create directory
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

# URLs for direct download (NCBI SRA download server)
$urls = @(
    @{
        Accession = "SRR12837671"
        Description = "WT Rep1"
        Url1 = "https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos2/sra-pub-run-17/SRR12837671/SRR12837671.1.fastq.gz"
        Url2 = "https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos2/sra-pub-run-17/SRR12837671/SRR12837671.2.fastq.gz"
    },
    @{
        Accession = "SRR12837674"
        Description = "D3 Rep1 (3'HS1 deletion)"
        Url1 = "https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos2/sra-pub-run-17/SRR12837674/SRR12837674.1.fastq.gz"
        Url2 = "https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos2/sra-pub-run-17/SRR12837674/SRR12837674.2.fastq.gz"
    },
    @{
        Accession = "SRR12837675"
        Description = "A2 Rep1 (3'HS1 inversion)"
        Url1 = "https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos2/sra-pub-run-17/SRR12837675/SRR12837675.1.fastq.gz"
        Url2 = "https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos2/sra-pub-run-17/SRR12837675/SRR12837675.2.fastq.gz"
    }
)

Write-Host "Samples:"
foreach ($sample in $urls) {
    Write-Host "  $($sample.Accession) - $($sample.Description)"
}
Write-Host ""
Write-Host "Expected size: ~30 GB total"
Write-Host "Estimated time: 4-6 hours (depends on connection)"
Write-Host ""
Write-Host "Starting at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# Download each sample
$totalBytes = 0
$downloadedBytes = 0

foreach ($sample in $urls) {
    Write-Host "============================================================"
    Write-Host "  Downloading $($sample.Accession) ($($sample.Description))"
    Write-Host "============================================================"
    Write-Host ""
    
    $files = @($sample.Url1, $sample.Url2)
    
    foreach ($url in $files) {
        $filename = Split-Path -Leaf $url
        $outputPath = Join-Path $outputDir $filename
        
        # Check if already downloaded
        if (Test-Path $outputPath) {
            Write-Host "  ⚠️  Already exists: $filename"
            Write-Host "  Skipping..."
            Write-Host ""
            continue
        }
        
        Write-Host "  📥 Downloading: $filename"
        
        try {
            # Download with progress
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $url -OutFile $outputPath -UseBasicParsing
            
            # Get file size
            $fileSize = (Get-Item $outputPath).Length
            $totalBytes += $fileSize
            $downloadedBytes += $fileSize
            
            Write-Host "  ✅ Completed: $filename ($(Format-FileSize $fileSize))"
        }
        catch {
            Write-Host "  ❌ Error downloading: $_"
            Write-Host "  Retrying..."
            
            # Retry once
            try {
                Invoke-WebRequest -Uri $url -OutFile $outputPath -UseBasicParsing
                Write-Host "  ✅ Retry successful!"
            }
            catch {
                Write-Host "  ❌ Failed after retry. Continuing..."
            }
        }
        
        Write-Host ""
    }
}

# Summary
Write-Host ""
Write-Host "============================================================"
Write-Host "  Download Complete"
Write-Host "============================================================"
Write-Host ""
Write-Host "Finished at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""
Write-Host "Downloaded files:"
Get-ChildItem $outputDir -Filter "*.fastq.gz" | ForEach-Object {
    Write-Host "  $($_.Name) ($(Format-FileSize $_.Length))"
}
Write-Host ""
Write-Host "Total size: $(Format-FileSize $downloadedBytes)"
Write-Host ""
Write-Host "✅ Next step: Run RNA-seq analysis pipeline"
Write-Host "   See: fastq_data\README.md"
Write-Host ""

# Helper function
function Format-FileSize {
    param([long]$size)
    if ($size -lt 0) { return "0 B" }
    $sizes = 'B', 'KB', 'MB', 'GB', 'TB'
    $i = 0
    while ($size -ge 1KB -and $i -lt $sizes.Count) {
        $size /= 1KB
        $i++
    }
    return "{0:N2} {1}" -f $size, $sizes[$i]
}
