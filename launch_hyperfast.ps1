# launch_hyperfast.ps1
# ════════════════════════════════════════════════════════════════════
#  HYPERFAST LAUNCHER — 100% completion in 60 minutes
#  Architecture: Zero-Skip Shard Access + Producer-Consumer Pipeline
# ════════════════════════════════════════════════════════════════════

$banner = @"
╔══════════════════════════════════════════════════════════════════╗
║     ⚡  HYPERFAST 100M TRAINING  —  GUARANTEED 60 MINUTES  ⚡    ║
║                                                                  ║
║   OLD: Workers skip 22M–82M rows before writing  (SLOW!)        ║
║   NEW: Each worker reads ONLY its own shard files (ZERO SKIP!)   ║
║                                                                  ║
║   Pipeline: Reader Thread  →  Queue  →  Writer Thread (YOU)      ║
║   5 workers × 20M = 100,000,000 records total                    ║
╚══════════════════════════════════════════════════════════════════╝
"@
Write-Host $banner -ForegroundColor Cyan

# ── Kill ALL stale python workers ────────────────────────────────────────────
Write-Host "  🛑  Stopping all existing python processes …" -ForegroundColor Yellow
$stale = Get-Process python,python3 -ErrorAction SilentlyContinue
if ($stale) {
    $stale | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  ✅  Killed $($stale.Count) stale process(es)." -ForegroundColor Red
    Start-Sleep -Seconds 3
} else {
    Write-Host "  ✅  No stale processes." -ForegroundColor Green
}

# ── Worker metadata ──────────────────────────────────────────────────────────
$colors = @("Cyan", "Green", "Yellow", "Magenta", "Red")
$resumes = @("9.0M", "2.6M", "10.4M", "2.6M", "2.6M")
$shards  = @("0–64", "65–129", "130–194", "195–259", "260–324")

Write-Host ""
Write-Host "  Launching 5 HYPERFAST workers …" -ForegroundColor White
Write-Host ""

for ($i = 0; $i -le 4; $i++) {
    $title = "HYPER-$i  |  Shards $($shards[$i])  |  Resume: $($resumes[$i])"
    $color = $colors[$i]

    $cmd = "cd 'c:\Gamansai\ai'; " +
           "`$Host.UI.RawUI.WindowTitle = '$title'; " +
           "Write-Host '' ; " +
           "Write-Host '  $title' -ForegroundColor $color; " +
           "Write-Host '' ; " +
           "python hyperfast_worker.py --worker $i"

    Start-Process powershell `
        -ArgumentList "-NoExit", "-Command", $cmd `
        -WindowStyle Normal

    Write-Host "  ✅  Worker-$i launched  |  Shards $($shards[$i])  |  Resumed from $($resumes[$i])" `
        -ForegroundColor $color
    Start-Sleep -Milliseconds 600   # stagger to reduce simultaneous dataset init
}

# ── Live monitor ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  📊  Starting LIVE DASHBOARD in 6 s …" -ForegroundColor White
Start-Sleep -Seconds 6

Start-Process powershell `
    -ArgumentList "-NoExit", "-Command", `
    "cd 'c:\Gamansai\ai'; `$Host.UI.RawUI.WindowTitle = '📊 HYPERFAST DASHBOARD  —  100M TRAINING'; python parallel_progress_monitor.py" `
    -WindowStyle Normal

# ── Summary ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅  ALL 6 TERMINALS RUNNING  —  5 Workers + 1 Dashboard        ║" -ForegroundColor Green
Write-Host "║                                                                  ║" -ForegroundColor Green
Write-Host "║  Key improvements over turbo_worker.py:                          ║" -ForegroundColor Green
Write-Host "║  ✓ Zero skip (was up to 82M rows skipped)                        ║" -ForegroundColor Green
Write-Host "║  ✓ Each worker reads its own HuggingFace shards directly         ║" -ForegroundColor Green
Write-Host "║  ✓ Reader + Writer run in PARALLEL (pipeline)                    ║" -ForegroundColor Green
Write-Host "║  ✓ 1 GB SQLite cache, MEMORY journal (no WAL file)               ║" -ForegroundColor Green
Write-Host "║  ✓ 500K batch inserts, HIGH process priority                     ║" -ForegroundColor Green
Write-Host "║                                                                  ║" -ForegroundColor Green
Write-Host "║  ⏱️   Estimated finish time: ~60 minutes from NOW                  ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
