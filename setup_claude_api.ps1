# setup_claude_api.ps1
# ─────────────────────
# One-click Claude API setup for Gaman AI

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  🌐 CLAUDE API SETUP FOR GAMAN AI" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Claude API gives your AI REAL GPT-quality answers." -ForegroundColor White
Write-Host ""
Write-Host "📋 Steps:" -ForegroundColor Yellow
Write-Host "  1. Go to: https://console.anthropic.com/account/keys" -ForegroundColor Cyan
Write-Host "  2. Click 'Create Key'" -ForegroundColor Cyan
Write-Host "  3. Paste it below" -ForegroundColor Cyan
Write-Host ""

$key = Read-Host "Paste your API key here (sk-ant-...)"

if ($key -like "sk-ant-*") {
    # Save to .env file
    $envContent = "ANTHROPIC_API_KEY=$key"
    Set-Content -Path "C:\Gamansai\ai\.env" -Value $envContent -Encoding UTF8

    # Also set for current session
    $env:ANTHROPIC_API_KEY = $key

    Write-Host ""
    Write-Host "✅ API key saved!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now start the app:" -ForegroundColor Yellow
    Write-Host "  cd C:\Gamansai\ai" -ForegroundColor Cyan
    Write-Host "  .\START.ps1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ That doesn't look like a valid key (should start with sk-ant-)" -ForegroundColor Red
    Write-Host "   Get yours free at: https://console.anthropic.com" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
