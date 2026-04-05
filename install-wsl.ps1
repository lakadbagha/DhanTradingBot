# NIFTY Trading Bot - WSL Installation Script
# Run this in PowerShell as Administrator

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🚀 NIFTY TRADING BOT - WSL + DOCKER SETUP" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Step 1: Check Windows version
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "📋 Step 1: Checking Windows version..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$osVersion = [System.Environment]::OSVersion.Version
Write-Host "Windows Version: $($osVersion.Major).$($osVersion.Minor) Build $($osVersion.Build)" -ForegroundColor White

if ($osVersion.Build -lt 18362) {
    Write-Host "❌ WSL 2 requires Windows 10 version 1903 or higher (Build 18362+)" -ForegroundColor Red
    Write-Host "Please update Windows and try again" -ForegroundColor Yellow
    pause
    exit
}

Write-Host "✅ Windows version compatible" -ForegroundColor Green
Write-Host ""

# Step 2: Install WSL
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🔧 Step 2: Installing WSL..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$wslInstalled = Get-Command wsl -ErrorAction SilentlyContinue

if ($wslInstalled) {
    Write-Host "⚠️  WSL already installed" -ForegroundColor Yellow
    wsl --version
} else {
    Write-Host "Installing WSL and Ubuntu..." -ForegroundColor White
    Write-Host "This will take 5-10 minutes..." -ForegroundColor Yellow
    Write-Host ""
    
    wsl --install
    
    Write-Host ""
    Write-Host "✅ WSL installation initiated" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Computer will need to restart!" -ForegroundColor Yellow
    Write-Host ""
    
    $restart = Read-Host "Restart now? (Y/N)"
    if ($restart -eq 'Y' -or $restart -eq 'y') {
        Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
        Write-Host "After restart, Ubuntu will auto-start for setup" -ForegroundColor Cyan
        Start-Sleep -Seconds 10
        Restart-Computer
        exit
    } else {
        Write-Host "Please restart manually to complete WSL installation" -ForegroundColor Yellow
        pause
        exit
    }
}

Write-Host ""

# Step 3: Check WSL version
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "📊 Step 3: Checking WSL version..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

wsl --list --verbose

Write-Host ""
Write-Host "✅ WSL is installed" -ForegroundColor Green
Write-Host ""

# Step 4: Download Docker Desktop
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🐋 Step 4: Docker Desktop Setup..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$dockerInstalled = Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe"

if ($dockerInstalled) {
    Write-Host "✅ Docker Desktop already installed" -ForegroundColor Green
    Write-Host ""
    Write-Host "Checking if Docker is running..." -ForegroundColor White
    
    $dockerRunning = docker ps 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
        docker --version
        docker compose version
    } else {
        Write-Host "⚠️  Docker Desktop not running" -ForegroundColor Yellow
        Write-Host "Please start Docker Desktop manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "Docker Desktop not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install Docker Desktop:" -ForegroundColor Cyan
    Write-Host "1. Go to: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "2. Click 'Download for Windows'" -ForegroundColor White
    Write-Host "3. Run the installer" -ForegroundColor White
    Write-Host "4. Check 'Use WSL 2 instead of Hyper-V'" -ForegroundColor White
    Write-Host "5. Restart computer after installation" -ForegroundColor White
    Write-Host ""
    
    $openBrowser = Read-Host "Open download page in browser? (Y/N)"
    if ($openBrowser -eq 'Y' -or $openBrowser -eq 'y') {
        Start-Process "https://www.docker.com/products/docker-desktop"
    }
}

Write-Host ""

# Step 5: Copy setup script to WSL
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "📁 Step 5: Preparing project files..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$projectPath = "D:\dhan_algo"
Write-Host "Project location: $projectPath" -ForegroundColor White

if (Test-Path $projectPath) {
    Write-Host "✅ Project directory found" -ForegroundColor Green
    
    # Make setup.sh executable
    $setupScript = Join-Path $projectPath "setup.sh"
    if (Test-Path $setupScript) {
        Write-Host "✅ setup.sh found" -ForegroundColor Green
        
        # Convert to Unix line endings (CRLF to LF)
        $content = Get-Content $setupScript -Raw
        $content = $content -replace "`r`n", "`n"
        Set-Content $setupScript -Value $content -NoNewline
        
        Write-Host "✅ setup.sh prepared" -ForegroundColor Green
    } else {
        Write-Host "⚠️  setup.sh not found in project directory" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Project directory not found: $projectPath" -ForegroundColor Red
    Write-Host "Please ensure project is at D:\dhan_algo" -ForegroundColor Yellow
}

Write-Host ""

# Step 6: Run setup in WSL
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🚀 Step 6: Ready to setup in WSL..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Close this window" -ForegroundColor White
Write-Host "2. Open 'Ubuntu' from Start Menu" -ForegroundColor White
Write-Host "3. Run: cd /mnt/d/dhan_algo" -ForegroundColor Yellow
Write-Host "4. Run: chmod +x setup.sh" -ForegroundColor Yellow
Write-Host "5. Run: ./setup.sh" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or run all at once:" -ForegroundColor Cyan
Write-Host "wsl -d Ubuntu-22.04 bash -c 'cd /mnt/d/dhan_algo && chmod +x setup.sh && ./setup.sh'" -ForegroundColor Green
Write-Host ""

$runNow = Read-Host "Run setup in WSL now? (Y/N)"

if ($runNow -eq 'Y' -or $runNow -eq 'y') {
    Write-Host ""
    Write-Host "Starting WSL setup..." -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    wsl -d Ubuntu-22.04 bash -c "cd /mnt/d/dhan_algo && chmod +x setup.sh && ./setup.sh"
    
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Setup script ready!" -ForegroundColor Green
    Write-Host "Run it manually when ready" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "📚 Documentation" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Complete guide: D:\dhan_algo\WSL_DOCKER_COMPLETE_GUIDE.md" -ForegroundColor White
Write-Host "Trading system: D:\dhan_algo\COMPLETE_TRADING_SYSTEM.md" -ForegroundColor White
Write-Host "Deployment:     D:\dhan_algo\DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "✨ Happy Trading! 🚀" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

pause
