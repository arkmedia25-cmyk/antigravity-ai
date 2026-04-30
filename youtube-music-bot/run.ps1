# YouTube Music Bot — Nightly Runner
# Task Scheduler bu scripti her gece cagiriyor
# Log: logs\queue_YYYY-MM-DD.log

$ROOT = $PSScriptRoot
$PYTHON = "python"
$LOG_DIR = Join-Path $ROOT "logs"
$DATE = Get-Date -Format "yyyy-MM-dd"
$LOG_FILE = Join-Path $LOG_DIR "queue_$DATE.log"

# Eski loglari temizle (30 gundan eski)
Get-ChildItem $LOG_DIR -Filter "queue_*.log" -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item -Force

New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

$TIMESTAMP = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content $LOG_FILE "============================================================"
Add-Content $LOG_FILE "[$TIMESTAMP] Basliyor..."
Add-Content $LOG_FILE "============================================================"

Set-Location $ROOT

& $PYTHON "-u" "queue_runner.py" 2>&1 | Tee-Object -FilePath $LOG_FILE -Append

$EXIT = $LASTEXITCODE
$TIMESTAMP = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content $LOG_FILE "[$TIMESTAMP] Tamamlandi - exit code: $EXIT"
