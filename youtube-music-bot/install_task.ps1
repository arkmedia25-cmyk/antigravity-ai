# Yonetici olarak calistir: Right-click -> Run as Administrator
# Bu script YouTube Music Bot'u her gece 01:00'da calistirmak uzere Task Scheduler'a ekler.

$taskName = "YouTubeMusicBot"
$scriptPath = "D:\OneDrive\Bureaublad\Antigravity\youtube-music-bot\run.ps1"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -Daily -At "01:00"

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 6) `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 30) `
    -StartWhenAvailable `
    -WakeToRun $false

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Force

Write-Host ""
Write-Host "✅ Task Scheduler'a eklendi: $taskName" -ForegroundColor Green
Write-Host "   Her gece 01:00'da otomatik calisacak." -ForegroundColor Green
Write-Host ""
Write-Host "Manuel test icin:" -ForegroundColor Cyan
Write-Host "   Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
