# 📊 WIN RATE ANALYZER - QUICK START
# Generate 12-month win rate report from trading data

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "📊 12-MONTH WIN RATE ANALYZER" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location -Path "D:\dhan_algo"

# Check if data folder exists
if (!(Test-Path "data")) {
    Write-Host "📁 Creating data folder..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "data" -Force | Out-Null
    Write-Host "✅ Folder created" -ForegroundColor Green
    Write-Host ""
}

# Check for CSV files
$csvFiles = Get-ChildItem -Path "data" -Filter "livetrading_*.csv" -ErrorAction SilentlyContinue

if ($csvFiles.Count -eq 0) {
    Write-Host "⚠️  No trading data found in 'data' folder" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Would you like to:" -ForegroundColor Cyan
    Write-Host "  1. Generate sample data for testing" -ForegroundColor White
    Write-Host "  2. Exit (add your real CSV files manually)" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1 or 2)"
    
    if ($choice -eq "1") {
        Write-Host ""
        Write-Host "🎲 Generating sample data..." -ForegroundColor Yellow
        Write-Host ""
        
        python generate_sample_data.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Sample data generated!" -ForegroundColor Green
            Write-Host ""
            
            # Refresh file list
            $csvFiles = Get-ChildItem -Path "data" -Filter "livetrading_*.csv"
        } else {
            Write-Host ""
            Write-Host "❌ Failed to generate sample data" -ForegroundColor Red
            Write-Host ""
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "📋 To use your real data:" -ForegroundColor Cyan
        Write-Host "   1. Place CSV files in: D:\dhan_algo\data\" -ForegroundColor White
        Write-Host "   2. File format: livetrading_DDMMYY.csv" -ForegroundColor White
        Write-Host "   3. Example: livetrading_050426.csv (for 05-Apr-2026)" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 0
    }
}

# Show found files
Write-Host "📂 Found CSV files:" -ForegroundColor Cyan
Write-Host ""
$csvFiles | Select-Object Name, @{Name="Size";Expression={"{0:N0} KB" -f ($_.Length / 1KB)}}, LastWriteTime | Format-Table -AutoSize
Write-Host "Total files: $($csvFiles.Count)" -ForegroundColor Green
Write-Host ""

# Ask confirmation
Write-Host "================================================================================" -ForegroundColor Cyan
$confirm = Read-Host "Analyze trading data and generate report? (Y/N)"

if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "❌ Cancelled by user" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "📊 Running analysis..." -ForegroundColor Green
Write-Host ""

# Run analyzer
python analyze_12month_winrate.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "✅ ANALYSIS COMPLETE!" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if report was created
    if (Test-Path "12_MONTH_WIN_RATE_REPORT.xlsx") {
        Write-Host "📄 Report generated: 12_MONTH_WIN_RATE_REPORT.xlsx" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Report contains:" -ForegroundColor Cyan
        Write-Host "   • Monthly Win Rate (last 12 months)" -ForegroundColor White
        Write-Host "   • Strategy Performance" -ForegroundColor White
        Write-Host "   • All Trades (cleaned, no duplicates)" -ForegroundColor White
        Write-Host "   • Summary Statistics" -ForegroundColor White
        Write-Host ""
        
        $openReport = Read-Host "Open Excel report now? (Y/N)"
        if ($openReport -eq 'Y' -or $openReport -eq 'y') {
            Start-Process "12_MONTH_WIN_RATE_REPORT.xlsx"
        }
    }
    
} else {
    Write-Host ""
    Write-Host "❌ Analysis failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Common issues:" -ForegroundColor Yellow
    Write-Host "   • Missing Python packages (pip install pandas openpyxl)" -ForegroundColor White
    Write-Host "   • Invalid CSV format" -ForegroundColor White
    Write-Host "   • Missing required columns" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "📚 DOCUMENTATION" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📄 Full guide: WIN_RATE_ANALYZER_GUIDE.md" -ForegroundColor White
Write-Host "📊 Sample data: generate_sample_data.py" -ForegroundColor White
Write-Host "🔧 Analyzer: analyze_12month_winrate.py" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
