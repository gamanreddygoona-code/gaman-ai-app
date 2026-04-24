# START.ps1 - Start Gaman AI

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 68) -ForegroundColor Cyan
Write-Host "🚀 GAMAN AI - SMART LOCAL CODING ASSISTANT" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 68) -ForegroundColor Cyan
Write-Host ""

# Kill any existing processes
Write-Host "🧹 Cleaning up old processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -match "uvicorn|app"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "✅ Ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Gaman AI server..." -ForegroundColor Yellow
Write-Host ""

# Start the server
uvicorn app:app --reload --host 127.0.0.1 --port 8000
