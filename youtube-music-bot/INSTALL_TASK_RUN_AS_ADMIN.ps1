# ============================================================
# YouTubeMusicBot — Task Scheduler Kurulum
# SAG TIKLAYIP "Als administrator uitvoeren" ile calistir!
# ============================================================

$taskName   = "YouTubeMusicBot"
$scriptPath = "D:\OneDrive\Bureaublad\Antigravity\youtube-music-bot\run.ps1"
$workDir    = "D:\OneDrive\Bureaublad\Antigravity\youtube-music-bot"

# Yonetici kontrolu
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")) {
    Write-Host "HATA: Bu scripti 'Als administrator uitvoeren' ile calistir!" -ForegroundColor Red
    Write-Host "PowerShell'e sag tiklayip 'Als administrator uitvoeren' sec." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Yonetici olarak calisiliyor..." -ForegroundColor Green

# Eski task varsa sil
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Action: powershell run.ps1 calistir
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`"" `
    -WorkingDirectory $workDir

# Her gece 01:00'da tetikle
$trigger = New-ScheduledTaskTrigger -Daily -At "01:00"

# Ayarlar
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 6) `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 30) `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

# Kaydet (yuksek yetki ile)
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Force | Out-Null

# Sonucu dogrula
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
$info = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue

if ($task) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  Task basariyla kuruldu!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  Isim         : $($task.TaskName)"
    Write-Host "  Durum        : $($task.State)"
    Write-Host "  Sonraki calis: $($info.NextRunTime)"
    Write-Host "  Calisma saati: Her gece 01:00"
    Write-Host ""
    Write-Host "Manuel test icin:" -ForegroundColor Cyan
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "HATA: Task kurulamadi!" -ForegroundColor Red
}

pause
