# ═══════════════════════════════════════════════════════════════════
#  launch_all.ps1
#  MASTER LAUNCHER — AI SERVER + 5 WORKERS + MONITOR + WATCHDOG
#  100% REAL — No simulation
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "SilentlyContinue"
$AI_DIR = "c:\Gamansai\ai"
Set-Location $AI_DIR

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   GAMANSAI — FULL SYSTEM LAUNCH" -ForegroundColor Cyan
Write-Host "   Server + 5 Workers + Monitor + Watchdog Protector" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ── STEP 1: Kill stale python processes ─────────────────────────
Write-Host "  [1/5] Stopping stale python processes..." -ForegroundColor Yellow
$stale = Get-Process python,python3 -ErrorAction SilentlyContinue
if ($stale) {
    $stale | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "        Killed $($stale.Count) stale process(es)." -ForegroundColor Red
    Start-Sleep -Seconds 3
} else {
    Write-Host "        No stale processes found. Clean start." -ForegroundColor Green
}

# ── STEP 2: Launch AI Server ─────────────────────────────────────
Write-Host ""
Write-Host "  [2/5] Launching AI Server on port 8000..." -ForegroundColor Green
$serverCmd = "cd '$AI_DIR'; " +
    "`$Host.UI.RawUI.WindowTitle = '🚀 AI SERVER — http://127.0.0.1:8000'; " +
    "Write-Host '===============================================' -ForegroundColor Cyan; " +
    "Write-Host '  🚀 AI SERVER  →  http://127.0.0.1:8000' -ForegroundColor Green; " +
    "Write-Host '  🎮 GAME STUDIO → http://127.0.0.1:8000/3d' -ForegroundColor Green; " +
    "Write-Host '===============================================' -ForegroundColor Cyan; " +
    "python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $serverCmd -WindowStyle Normal
Write-Host "        AI Server launched!" -ForegroundColor Green
Start-Sleep -Seconds 2

# ── STEP 3: Launch 5 Hyperfast Workers ──────────────────────────
Write-Host ""
Write-Host "  [3/5] Launching 5 Hyperfast Training Workers..." -ForegroundColor Yellow
$colors = @("Cyan", "Green", "Yellow", "Magenta", "Red")
$shards  = @("0-64", "65-129", "130-194", "195-259", "260-324")

for ($i = 0; $i -le 4; $i++) {
    $title = "⚡ WORKER-$i | Shards $($shards[$i])"
    $col   = $colors[$i]
    $wCmd  = "cd '$AI_DIR'; " +
        "`$Host.UI.RawUI.WindowTitle = '$title'; " +
        "Write-Host '' ; " +
        "Write-Host '  $title' -ForegroundColor $col; " +
        "Write-Host '  Training 20M records — REAL, no simulation' -ForegroundColor White; " +
        "Write-Host '' ; " +
        "python hyperfast_worker.py --worker $i"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $wCmd -WindowStyle Normal
    Write-Host "        Worker-$i launched  [$($shards[$i])]" -ForegroundColor $col
    Start-Sleep -Milliseconds 600
}

# ── STEP 4: Launch Live Progress Monitor ─────────────────────────
Write-Host ""
Write-Host "  [4/5] Launching Live Progress Monitor..." -ForegroundColor Magenta
Start-Sleep -Seconds 6
$monCmd = "cd '$AI_DIR'; " +
    "`$Host.UI.RawUI.WindowTitle = '📊 LIVE MONITOR — 100M TRAINING'; " +
    "Write-Host '===============================================' -ForegroundColor Magenta; " +
    "Write-Host '  📊 LIVE PROGRESS MONITOR — 100M TARGET' -ForegroundColor Magenta; " +
    "Write-Host '===============================================' -ForegroundColor Magenta; " +
    "python parallel_progress_monitor.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $monCmd -WindowStyle Normal
Write-Host "        Live Monitor launched!" -ForegroundColor Magenta

# ── STEP 5: Launch Watchdog Protector ────────────────────────────
Write-Host ""
Write-Host "  [5/5] Launching Watchdog Protector..." -ForegroundColor Yellow
$dogCmd = "cd '$AI_DIR'; " +
    "`$Host.UI.RawUI.WindowTitle = '🐕 WATCHDOG PROTECTOR — ACTIVE'; " +
    "Write-Host '===============================================' -ForegroundColor Yellow; " +
    "Write-Host '  🐕 WATCHDOG — Auto-heals WORKERS ONLY' -ForegroundColor Yellow; " +
    "Write-Host '  Checks every 60 seconds. Cannot be stopped.' -ForegroundColor White; " +
    "Write-Host '===============================================' -ForegroundColor Yellow; " +
    "python watchdog.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $dogCmd -WindowStyle Normal
Write-Host "        Watchdog Protector launched!" -ForegroundColor Yellow

# ── DONE ─────────────────────────────────────────────────────────
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   ALL TERMINALS LAUNCHED — 8 WINDOWS TOTAL" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Green
Write-Host "   🚀  AI Server      →  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "   🎮  Game Studio    →  http://127.0.0.1:8000/3d" -ForegroundColor Cyan
Write-Host "   ⚡  Worker 0-4     →  5 terminals running" -ForegroundColor Yellow
Write-Host "   📊  Live Monitor   →  1 dashboard" -ForegroundColor Magenta
Write-Host "   🐕  Watchdog       →  protecting everything" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Opening browser in 4 seconds..." -ForegroundColor White
Start-Sleep -Seconds 4
Start-Process "http://127.0.0.1:8000/3d"
Write-Host "  Browser opened to Game Studio!" -ForegroundColor Green
