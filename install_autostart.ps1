$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $root 'start_server.ps1'
$shortcutPath = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'Placement Copilot.lnk')

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = 'powershell'
$shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$target`""
$shortcut.WorkingDirectory = $root
$shortcut.WindowStyle = 7
$shortcut.Save()

Write-Host "Auto-start shortcut created: $shortcutPath"
