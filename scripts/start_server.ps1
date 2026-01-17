# Sphota Server Startup Script
# Starts the Streamlit development server for Sphota.AI

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Sphota: Cognitive Meaning Engine Server             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if venv exists
if (-Not (Test-Path ".venv")) {
    Write-Host "❌ Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
& ".\.venv\Scripts\Activate.ps1"

# Install requirements if needed
Write-Host "✓ Checking dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet 2>&1 | Out-Null

# Start server
Write-Host ""
Write-Host "✓ Starting Streamlit server..." -ForegroundColor Green
Write-Host "🌐 Access the app at: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m streamlit run app.py --server.port 8501
