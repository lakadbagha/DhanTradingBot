# 📊 MONITOR TRADING BOT - Real-time Monitoring Script

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "📊 TRADING BOT MONITOR" -ForegroundColor Green
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location -Path "D:\dhan_algo"

# Check if container is running
Write-Host "🔍 Checking container status..." -ForegroundColor Yellow
$containerStatus = docker compose ps -q

if (-not $containerStatus) {
    Write-Host "❌ Container is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Start the bot with: .\start-bot.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Container is running" -ForegroundColor Green
Write-Host ""

# Show menu
function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host "📊 TRADING BOT MONITOR - MENU" -ForegroundColor Green
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. View Live Logs (follow)" -ForegroundColor White
    Write-Host "2. View Last 50 Log Lines" -ForegroundColor White
    Write-Host "3. View Container Status" -ForegroundColor White
    Write-Host "4. View Container Stats (CPU/Memory)" -ForegroundColor White
    Write-Host "5. View Today's Trades (CSV)" -ForegroundColor White
    Write-Host "6. View Log File (last 30 lines)" -ForegroundColor White
    Write-Host "7. Restart Container" -ForegroundColor White
    Write-Host "8. Stop Bot" -ForegroundColor White
    Write-Host "9. Execute Command in Container" -ForegroundColor White
    Write-Host "0. Exit" -ForegroundColor White
    Write-Host ""
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host ""
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Select option (0-9)"
    Write-Host ""
    
    switch ($choice) {
        '1' {
            Write-Host "📊 Live Logs (Press Ctrl+C to stop):" -ForegroundColor Yellow
            Write-Host ""
            docker compose logs -f
        }
        '2' {
            Write-Host "📊 Last 50 Log Lines:" -ForegroundColor Yellow
            Write-Host ""
            docker compose logs --tail=50
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        '3' {
            Write-Host "📊 Container Status:" -ForegroundColor Yellow
            Write-Host ""
            docker compose ps
            Write-Host ""
            Write-Host "Detailed Info:" -ForegroundColor Cyan
            docker ps --filter "name=nifty-trading-bot" --format "table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}"
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        '4' {
            Write-Host "📊 Container Stats (Press Ctrl+C to stop):" -ForegroundColor Yellow
            Write-Host ""
            docker stats nifty-trading-bot
        }
        '5' {
            $today = Get-Date -Format "ddMMyy"
            $csvFile = "data\livetrading_$today.csv"
            
            if (Test-Path $csvFile) {
                Write-Host "📈 Today's Trades: $csvFile" -ForegroundColor Green
                Write-Host ""
                
                $trades = Import-Csv $csvFile -ErrorAction SilentlyContinue
                if ($trades) {
                    $trades | Format-Table -AutoSize
                    Write-Host ""
                    Write-Host "Total Trades: $($trades.Count)" -ForegroundColor Cyan
                } else {
                    Write-Host "No trades yet" -ForegroundColor Yellow
                }
            } else {
                Write-Host "⚠️  No trade file found: $csvFile" -ForegroundColor Yellow
            }
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        '6' {
            $today = Get-Date -Format "ddMMyy"
            $logFile = "logs\trading_log_$today.log"
            
            if (Test-Path $logFile) {
                Write-Host "📝 Last 30 lines of: $logFile" -ForegroundColor Green
                Write-Host ""
                Write-Host "=================================================================================" -ForegroundColor Cyan
                Get-Content $logFile -Tail 30
                Write-Host "=================================================================================" -ForegroundColor Cyan
            } else {
                Write-Host "⚠️  Log file not found: $logFile" -ForegroundColor Yellow
            }
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        '7' {
            Write-Host "🔄 Restarting container..." -ForegroundColor Yellow
            docker compose restart
            Write-Host "✅ Container restarted" -ForegroundColor Green
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        '8' {
            Write-Host "🛑 Stopping bot..." -ForegroundColor Red
            docker compose down
            Write-Host "✅ Bot stopped" -ForegroundColor Green
            Write-Host ""
            Read-Host "Press Enter to exit"
            exit 0
        }
        '9' {
            Write-Host "Execute Command in Container" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Examples:" -ForegroundColor Yellow
            Write-Host "  ls -la /app" -ForegroundColor White
            Write-Host "  cat /app/strategy_config.py" -ForegroundColor White
            Write-Host "  python --version" -ForegroundColor White
            Write-Host ""
            $cmd = Read-Host "Enter command"
            
            if ($cmd) {
                Write-Host ""
                docker compose exec trading-bot sh -c "$cmd"
            }
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        '0' {
            Write-Host "Exiting..." -ForegroundColor Yellow
            exit 0
        }
        default {
            Write-Host "❌ Invalid option" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
    
} while ($true)
