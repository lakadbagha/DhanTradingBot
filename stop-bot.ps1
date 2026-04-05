# 🛑 STOP TRADING BOT - Quick Stop Script
# Run this after market closes (3:30 PM)

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "🛑 STOP NIFTY TRADING BOT" -ForegroundColor Red
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location -Path "D:\dhan_algo"

# Check if container is running
Write-Host "🔍 Checking container status..." -ForegroundColor Yellow
$containerStatus = docker compose ps -q

if (-not $containerStatus) {
    Write-Host "⚠️  Container is not running" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host "✅ Container is running" -ForegroundColor Green
Write-Host ""

# Show current status
Write-Host "📊 Current Status:" -ForegroundColor Cyan
docker compose ps
Write-Host ""

# Ask user to confirm
$confirm = Read-Host "Stop the trading bot? (Y/N)"

if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "❌ Cancelled by user" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "🛑 Stopping trading bot..." -ForegroundColor Yellow

# Stop the container
docker compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host "✅ TRADING BOT STOPPED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check for today's logs
    Write-Host "📊 Today's Trading Summary:" -ForegroundColor Cyan
    Write-Host ""
    
    $today = Get-Date -Format "ddMMyy"
    $csvFile = "data\livetrading_$today.csv"
    $logFile = "logs\trading_log_$today.log"
    
    if (Test-Path $csvFile) {
        Write-Host "📈 Trade CSV: $csvFile" -ForegroundColor Green
        Write-Host ""
        $trades = Import-Csv $csvFile -ErrorAction SilentlyContinue
        if ($trades) {
            Write-Host "   Total Trades: $($trades.Count)" -ForegroundColor White
            Write-Host ""
            
            $viewCSV = Read-Host "Open trade CSV in Excel? (Y/N)"
            if ($viewCSV -eq 'Y' -or $viewCSV -eq 'y') {
                Start-Process $csvFile
            }
        }
    } else {
        Write-Host "⚠️  No trades today: $csvFile not found" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    if (Test-Path $logFile) {
        Write-Host "📝 Log File: $logFile" -ForegroundColor Green
        
        $viewLog = Read-Host "View last 20 lines of log? (Y/N)"
        if ($viewLog -eq 'Y' -or $viewLog -eq 'y') {
            Write-Host ""
            Write-Host "=================================================================================" -ForegroundColor Cyan
            Get-Content $logFile -Tail 20
            Write-Host "=================================================================================" -ForegroundColor Cyan
        }
    }
    
} else {
    Write-Host ""
    Write-Host "❌ Failed to stop trading bot" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
