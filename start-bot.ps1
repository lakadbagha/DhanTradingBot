# 🚀 START TRADING BOT - Quick Launch Script
# Run this before market opens (9:15 AM)

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "🚀 NIFTY TRADING BOT - DOCKER DEPLOYMENT" -ForegroundColor Green
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location -Path "D:\dhan_algo"

# Check if Docker is running
Write-Host "🔍 Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker is running: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running!" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if image exists
Write-Host "🔍 Checking Docker image..." -ForegroundColor Yellow
$imageExists = docker images nifty-trading-bot -q
if ($imageExists) {
    Write-Host "✅ Docker image exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker image not found. Building now..." -ForegroundColor Yellow
    Write-Host ""
    docker build -t nifty-trading-bot .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker image built successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""

# Check current time
$currentTime = Get-Date
$marketOpen = Get-Date "09:15"
$marketClose = Get-Date "15:30"

Write-Host "🕐 Current Time: $($currentTime.ToString('hh:mm tt'))" -ForegroundColor Cyan
Write-Host "📊 Market Hours: 9:15 AM - 3:30 PM" -ForegroundColor Cyan

if ($currentTime -lt $marketOpen) {
    $timeUntilOpen = $marketOpen - $currentTime
    Write-Host "⏰ Market opens in: $($timeUntilOpen.Hours)h $($timeUntilOpen.Minutes)m" -ForegroundColor Yellow
} elseif ($currentTime -gt $marketClose) {
    Write-Host "⚠️  Market is closed" -ForegroundColor Yellow
} else {
    Write-Host "✅ Market is open - Good time to trade!" -ForegroundColor Green
}

Write-Host ""

# Ask user to confirm
Write-Host "=================================================================================" -ForegroundColor Cyan
$confirm = Read-Host "Start the trading bot? (Y/N)"

if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "❌ Cancelled by user" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "🚀 Starting trading bot container..." -ForegroundColor Green
Write-Host ""

# Start the container
docker compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host "✅ TRADING BOT STARTED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Wait a moment for container to start
    Start-Sleep -Seconds 2
    
    # Show container status
    Write-Host "📊 Container Status:" -ForegroundColor Yellow
    docker compose ps
    
    Write-Host ""
    Write-Host "📝 Useful Commands:" -ForegroundColor Cyan
    Write-Host "   View logs:        docker compose logs -f" -ForegroundColor White
    Write-Host "   Check status:     docker compose ps" -ForegroundColor White
    Write-Host "   Stop bot:         docker compose down" -ForegroundColor White
    Write-Host "   View trade CSV:   type data\livetrading_*.csv" -ForegroundColor White
    Write-Host ""
    
    # Ask if user wants to see logs
    $showLogs = Read-Host "View live logs now? (Y/N)"
    if ($showLogs -eq 'Y' -or $showLogs -eq 'y') {
        Write-Host ""
        Write-Host "📊 Live Logs (Press Ctrl+C to exit):" -ForegroundColor Yellow
        Write-Host ""
        docker compose logs -f
    }
    
} else {
    Write-Host ""
    Write-Host "❌ Failed to start trading bot" -ForegroundColor Red
    Write-Host ""
    Write-Host "View logs for details:" -ForegroundColor Yellow
    docker compose logs --tail=50
}

Write-Host ""
