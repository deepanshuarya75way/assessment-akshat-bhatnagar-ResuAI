$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $root 'logs\app.pid'
$watchdogPidFile = Join-Path $root 'logs\watchdog.pid'

$processIds = @()
if (Test-Path $pidFile) {
    $pidValue = (Get-Content $pidFile -Raw).Trim()
    if ($pidValue) {
        $processIds += $pidValue
    }
}

if (Test-Path $watchdogPidFile) {
    $watchdogPidValue = (Get-Content $watchdogPidFile -Raw).Trim()
    if ($watchdogPidValue) {
        $processIds += $watchdogPidValue
    }
}

if ($processIds.Count -eq 0) {
    Write-Host 'No server PID found. It may already be stopped.'
    exit 0
}

foreach ($processId in ($processIds | Select-Object -Unique)) {
    if ($processId -and (Get-Process -Id $processId -ErrorAction SilentlyContinue)) {
        Stop-Process -Id $processId -Force
        Write-Host "Stopped process $processId"
    }
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
Remove-Item $watchdogPidFile -Force -ErrorAction SilentlyContinue
