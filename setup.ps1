# Quick Setup script for WireGuard Gaming Manager (Windows PowerShell using uv)

Write-Host "🎮 WireGuard Gaming Manager - Quick Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing 'uv' package manager..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path += ";$env:USERPROFILE\.cargo\bin"
}

Write-Host "⚡ Syncing Python environment and dependencies with uv..." -ForegroundColor Green
uv sync

Write-Host ""
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the interactive CLI installer:" -ForegroundColor White
Write-Host "  uv run wg-gaming-installer" -ForegroundColor Yellow
Write-Host ""
Write-Host "To launch the Web UI control panel:" -ForegroundColor White
Write-Host "  uv run wg-gaming-web --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
Write-Host ""
