$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Join-Path $root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$logFile = Join-Path $logDir 'app.out.log'
$errFile = Join-Path $logDir 'app.err.log'
$pidFile = Join-Path $logDir 'app.pid'
$watchdogPidFile = Join-Path $logDir 'watchdog.pid'

if (Test-Path $pidFile) {
    $existingPid = (Get-Content $pidFile -Raw).Trim()
    if ($existingPid -and (Get-Process -Id $existingPid -ErrorAction SilentlyContinue)) {
        Write-Host "Server already running with PID $existingPid"
        exit 0
    }
}

$pythonExe = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $pythonExe)) {
    $pythonExe = 'python'
}

$watchdogPid = $PID
$watchdogPid | Set-Content $watchdogPidFile

while ($true) {
    $process = Start-Process -FilePath $pythonExe -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory $root -RedirectStandardOutput $logFile -RedirectStandardError $errFile -PassThru -WindowStyle Hidden
    $process.Id | Set-Content $pidFile
    Write-Host "Started server with PID $($process.Id)"

    while (-not $process.HasExited) {
        Start-Sleep -Seconds 5
        try {
            $health = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 5
            if ($health.StatusCode -ge 200 -and $health.StatusCode -lt 500) {
                $null = $health
            }
        } catch {
            # keep monitoring; the server may still be starting
        }
    }

    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Server exited unexpectedly. Restarting in 3 seconds..."
    Start-Sleep -Seconds 3
}
