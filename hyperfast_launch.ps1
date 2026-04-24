# hyperfast_launch.ps1 - clean ASCII-safe launcher
$ErrorActionPreference = "SilentlyContinue"
Set-Location "c:\Gamansai\ai"

# Kill stale python workers
$stale = Get-Process python -ErrorAction SilentlyContinue
if ($stale) {
    $stale | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Killed $($stale.Count) stale python process(es)."
    Start-Sleep -Seconds 3
} else {
    Write-Host "No stale processes found."
}

$colors = @("Cyan","Green","Yellow","Magenta","Red")

Write-Host "Launching 5 HYPERFAST workers..." -ForegroundColor White

for ($i = 0; $i -le 9; $i++) {
    $cmd = "cd 'c:\Gamansai\ai'; python hyperfast_worker.py --worker $i"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd -WindowStyle Normal
    Write-Host "  Worker-$i launched" -ForegroundColor $colors[$i % 5]
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "Launching live dashboard in 7s..." -ForegroundColor White
Start-Sleep -Seconds 7

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Gamansai\ai'; python parallel_progress_monitor.py" -WindowStyle Normal

Write-Host ""
Write-Host "ALL 6 TERMINALS LAUNCHED!" -ForegroundColor Green
Write-Host "5 Hyperfast Workers + 1 Dashboard" -ForegroundColor Green
Write-Host "Target: 100M records in ~60 minutes" -ForegroundColor Green
