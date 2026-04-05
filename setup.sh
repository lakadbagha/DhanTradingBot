#!/bin/bash

# NIFTY Trading Bot - Quick Setup Script
# Run this in Ubuntu WSL to setup everything automatically

set -e  # Exit on error

echo "================================================================================"
echo "🚀 NIFTY TRADING BOT - QUICK SETUP"
echo "================================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in WSL
if ! grep -qi microsoft /proc/version; then
    echo -e "${RED}❌ This script must be run in WSL (Ubuntu)${NC}"
    echo "Please install WSL first: wsl --install"
    exit 1
fi

echo -e "${GREEN}✅ Running in WSL${NC}"
echo ""

# Step 1: Update system
echo "================================================================================"
echo "📦 Step 1: Updating Ubuntu..."
echo "================================================================================"
sudo apt update
sudo apt upgrade -y
echo -e "${GREEN}✅ System updated${NC}"
echo ""

# Step 2: Install Docker
echo "================================================================================"
echo "🐋 Step 2: Installing Docker..."
echo "================================================================================"

if command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker already installed${NC}"
    docker --version
else
    # Install Docker
    sudo apt install -y docker.io docker-compose
    
    # Start Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    echo -e "${GREEN}✅ Docker installed${NC}"
    docker --version
fi
echo ""

# Step 3: Navigate to project
echo "================================================================================"
echo "📁 Step 3: Setting up project directory..."
echo "================================================================================"

# Ask for project location
read -p "Enter project location (default: /mnt/d/dhan_algo): " PROJECT_DIR
PROJECT_DIR=${PROJECT_DIR:-/mnt/d/dhan_algo}

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Directory not found: $PROJECT_DIR${NC}"
    echo "Please create the directory first or provide correct path"
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✅ Changed to: $(pwd)${NC}"
echo ""

# Step 4: Create required directories
echo "================================================================================"
echo "📂 Step 4: Creating directories..."
echo "================================================================================"
mkdir -p logs data backups
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Step 5: Verify required files
echo "================================================================================"
echo "📄 Step 5: Checking required files..."
echo "================================================================================"

REQUIRED_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "requirements.txt"
    "live_trading_engine_optimized.py"
    "strategy_config.py"
    "security_id_map.py"
    "creds.py"
    "position_manager.py"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${RED}❌${NC} $file - MISSING!"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ Missing $MISSING_FILES required files${NC}"
    echo "Please ensure all files are in the project directory"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All required files present${NC}"
echo ""

# Step 6: Build Docker image
echo "================================================================================"
echo "🏗️  Step 6: Building Docker image..."
echo "================================================================================"
echo "This may take 5-10 minutes on first run..."
echo ""

docker build -t nifty-trading-bot .

echo ""
echo -e "${GREEN}✅ Docker image built successfully${NC}"
echo ""

# Step 7: Test run
echo "================================================================================"
echo "🧪 Step 7: Testing container..."
echo "================================================================================"

echo "Starting test container..."
docker compose up -d

echo "Waiting 10 seconds..."
sleep 10

echo "Checking container status..."
docker compose ps

echo ""
echo "Recent logs:"
docker compose logs --tail=20

echo ""
echo -e "${GREEN}✅ Container test complete${NC}"
echo ""

# Step 8: Setup complete
echo "================================================================================"
echo "🎉 SETUP COMPLETE!"
echo "================================================================================"
echo ""
echo "📊 Summary:"
echo "   ✅ WSL configured"
echo "   ✅ Docker installed"
echo "   ✅ Project located at: $PROJECT_DIR"
echo "   ✅ Docker image built: nifty-trading-bot"
echo "   ✅ Container started: nifty-trading-bot"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:       docker compose logs -f"
echo "   Stop bot:        docker compose down"
echo "   Start bot:       docker compose up -d"
echo "   Rebuild:         docker compose up -d --build"
echo "   View status:     docker compose ps"
echo ""
echo "📁 Files:"
echo "   Logs:            logs/bot.log"
echo "   Trades:          data/livetrading_DDMMYY.csv"
echo "   Configuration:   strategy_config.py"
echo ""
echo "🚀 Next Steps:"
echo "   1. Wait for market hours (9:15 AM - 3:30 PM)"
echo "   2. Monitor: docker compose logs -f"
echo "   3. Check paper trades in data/livetrading_*.csv"
echo "   4. After testing, set PAPER_TRADING_MODE = False"
echo ""
echo "📚 Documentation:"
echo "   Complete guide: WSL_DOCKER_COMPLETE_GUIDE.md"
echo ""
echo "================================================================================"
echo "✨ Happy Trading! 🚀"
echo "================================================================================"
