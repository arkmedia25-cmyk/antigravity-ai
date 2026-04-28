# Son calistirmanin ozeti
$LOG_DIR = Join-Path $PSScriptRoot "logs"

$latest = Get-ChildItem $LOG_DIR -Filter "queue_*.log" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $latest) {
    Write-Host "Hic log bulunamadi. Bot henuz calistirilmamis." -ForegroundColor Yellow
    exit
}

Write-Host "`n=== Son calistirma: $($latest.Name) ===" -ForegroundColor Cyan
Get-Content $latest.FullName | Select-Object -Last 40
