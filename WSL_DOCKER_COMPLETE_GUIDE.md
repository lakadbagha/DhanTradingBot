# 🐳 DOCKER + WSL DEPLOYMENT GUIDE - Windows Local & Cloud

**Run Your Trading Bot in Docker Containers - Same Code Everywhere!**

---

## 📋 TABLE OF CONTENTS

1. [Why Docker + WSL?](#why-docker--wsl)
2. [Install WSL on Windows](#install-wsl-on-windows)
3. [Install Docker Desktop](#install-docker-desktop)
4. [Build & Run Locally](#build--run-locally)
5. [Deploy to Cloud](#deploy-to-cloud)
6. [Useful Commands](#useful-commands)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 WHY DOCKER + WSL?

### Benefits

**Docker Containers:**
- ✅ Same environment everywhere (local & cloud)
- ✅ No "works on my machine" issues
- ✅ Easy to backup/restore
- ✅ Isolated from Windows
- ✅ Deploy with one command
- ✅ Auto-restart on crash

**WSL (Windows Subsystem for Linux):**
- ✅ Full Linux environment on Windows
- ✅ Better Docker performance
- ✅ Access Windows files
- ✅ Run Linux commands
- ✅ No dual boot needed

**Combined Power:**
- ✅ Test locally in WSL/Docker
- ✅ Deploy to AWS/Azure with same Docker image
- ✅ Guaranteed identical behavior
- ✅ Professional DevOps workflow

---

## 🔧 INSTALL WSL ON WINDOWS

### Step 1: Enable WSL

**Open PowerShell as Administrator:**

```powershell
# Right-click Start → Windows PowerShell (Admin)

# Install WSL
wsl --install

# This installs:
# - WSL 2
# - Ubuntu 22.04 LTS (default)
# - Virtual Machine Platform
```

**You'll see:**
```
Installing: Windows Subsystem for Linux
Installing: Virtual Machine Platform
Installing: Ubuntu 22.04 LTS
The requested operation is successful. Changes will take effect after restart.
```

**Restart your computer when prompted.**

---

### Step 2: Setup Ubuntu

**After restart, Ubuntu will auto-launch:**

```bash
# Create Linux username
Enter new UNIX username: trading
# (Use any name you like)

# Create password
New password: ********
Retype new password: ********
# (Remember this password!)
```

**You now have Ubuntu Linux on Windows!** 🎉

---

### Step 3: Update Ubuntu

**In Ubuntu terminal:**

```bash
# Update package list
sudo apt update

# Upgrade all packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git nano
```

---

### Step 4: Access Windows Files

**Your Windows drives are mounted at `/mnt/`:**

```bash
# Navigate to your Windows drive
cd /mnt/d/dhan_algo

# List Windows files from Linux
ls -la

# You can access all Windows files!
```

---

## 🐋 INSTALL DOCKER DESKTOP

### Step 1: Download Docker Desktop

1. Go to: https://www.docker.com/products/docker-desktop
2. Click **"Download for Windows"**
3. Run the installer: `Docker Desktop Installer.exe`

### Step 2: Install Docker Desktop

**During installation:**
- ✅ Check "Use WSL 2 instead of Hyper-V"
- ✅ Check "Add shortcut to desktop"
- Click **"Ok"**
- Wait for installation (5-10 minutes)
- Click **"Close and restart"**

### Step 3: Start Docker Desktop

**After restart:**

1. **Docker Desktop** will auto-start
2. **Accept** the Docker Subscription Service Agreement
3. **Skip** the tutorial (optional)
4. Wait for **"Docker Desktop is running"** indicator

**Verify Installation:**

```powershell
# In PowerShell or Ubuntu WSL terminal
docker --version
# Should show: Docker version 24.x.x

docker compose version
# Should show: Docker Compose version 2.x.x
```

---

## 🏗️ BUILD & RUN LOCALLY

### Step 1: Prepare Project Files

**In Ubuntu WSL terminal:**

```bash
# Navigate to your Windows project folder
cd /mnt/d/dhan_algo

# Create necessary directories
mkdir -p logs data

# Verify all required files exist
ls -la

# Should see:
# - Dockerfile
# - docker-compose.yml
# - requirements.txt
# - live_trading_engine_optimized.py
# - strategy_config.py
# - security_id_map.py
# - creds.py
# - position_manager.py
```

---

### Step 2: Build Docker Image

**Still in /mnt/d/dhan_algo:**

```bash
# Build the Docker image
docker build -t nifty-trading-bot .

# This will:
# - Download Python 3.11 base image
# - Install all dependencies
# - Copy your trading files
# - Create the container image
# 
# Takes 2-5 minutes first time
```

**You'll see:**
```
[+] Building 120.5s
 => [1/6] FROM docker.io/library/python:3.11-slim
 => [2/6] WORKDIR /app
 => [3/6] COPY requirements.txt .
 => [4/6] RUN pip install --no-cache-dir -r requirements.txt
 => [5/6] COPY . .
 => [6/6] RUN mkdir -p /app/logs
 => exporting to image
 => => naming to docker.io/library/nifty-trading-bot
```

**Verify image created:**

```bash
docker images

# Should show:
# REPOSITORY            TAG       IMAGE ID       CREATED         SIZE
# nifty-trading-bot     latest    abc123def456   2 minutes ago   450MB
```

---

### Step 3: Run Container (Test Mode)

**Start the trading bot:**

```bash
# Run in foreground (see output)
docker run -it --rm \
  --name trading-bot-test \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -e TZ=Asia/Kolkata \
  nifty-trading-bot

# Flags explained:
# -it          = Interactive terminal
# --rm         = Remove container when stopped
# --name       = Container name
# -v           = Mount volumes (logs, data)
# -e           = Environment variable (timezone)
# nifty-trading-bot = Image name
```

**You should see:**
```
================================================================================
🚀 OPTIMIZED LIVE TRADING ENGINE
================================================================================
Mode: PAPER
Date: 05-Apr-2026
...
⚠️  Market is closed
   Market hours: 9:15 AM - 3:30 PM
```

**Stop with:** Ctrl+C

---

### Step 4: Run with Docker Compose (Recommended)

**Much simpler:**

```bash
# Start in background
docker compose up -d

# You'll see:
# [+] Running 1/1
#  ✔ Container nifty-trading-bot  Started
```

**Check status:**

```bash
# View running containers
docker compose ps

# CONTAINER             STATUS
# nifty-trading-bot     Up 2 minutes

# View logs (live)
docker compose logs -f

# View logs (last 50 lines)
docker compose logs --tail=50
```

**Stop the bot:**

```bash
docker compose down
```

---

### Step 5: Run During Market Hours

**Important: Only runs 9:15 AM - 3:30 PM**

**Start the bot:**

```bash
# Make sure you're in the project folder
cd /mnt/d/dhan_algo

# Start bot
docker compose up -d

# Check it's running
docker compose logs -f
```

**Expected during market hours:**

```
================================================================================
🚀 STARTING TRADING SESSION
================================================================================

🔍 Scanning for signals...
   NIFTY: Rs.23,450.50

📢 SIGNAL DETECTED: Fibonacci CALL
   Strike: 23400
   Security ID: 40752
   
📝 PAPER TRADING MODE - Order NOT placed
✅ Paper trade logged
```

**Monitor logs:**

```bash
# Live logs
docker compose logs -f trading-bot

# Or check log files
tail -f logs/bot.log
cat data/livetrading_$(date +%d%m%y).csv
```

---

## ☁️ DEPLOY TO CLOUD

### Option 1: Deploy to AWS EC2

**After testing locally, deploy same Docker image to cloud:**

**On AWS EC2 (Ubuntu):**

```bash
# Install Docker on EC2
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Upload your project
scp -r /mnt/d/dhan_algo ubuntu@YOUR_EC2_IP:/home/ubuntu/trading/

# SSH to EC2
ssh ubuntu@YOUR_EC2_IP

# Navigate and run
cd /home/ubuntu/trading
docker compose up -d

# Same commands as local!
```

---

### Option 2: Push to Docker Hub (Deploy Anywhere)

**Push image to Docker Hub:**

```bash
# Login to Docker Hub
docker login
# Username: your-docker-username
# Password: your-docker-password

# Tag your image
docker tag nifty-trading-bot your-username/nifty-trading-bot:latest

# Push to Docker Hub
docker push your-username/nifty-trading-bot:latest
```

**Deploy on any server:**

```bash
# Pull and run on any server
docker pull your-username/nifty-trading-bot:latest
docker run -d --restart unless-stopped \
  -v /path/to/logs:/app/logs \
  -v /path/to/data:/app/data \
  your-username/nifty-trading-bot:latest
```

---

### Option 3: AWS ECS (Managed Containers)

**Deploy to AWS Elastic Container Service:**

1. Push image to **AWS ECR** or Docker Hub
2. Create **ECS Cluster**
3. Create **Task Definition** using your image
4. Run **ECS Service**
5. AWS manages everything!

**Cost:** ~$10/month (Fargate)

---

## 📝 USEFUL COMMANDS

### Docker Commands

```bash
# View all containers (running + stopped)
docker ps -a

# View running containers only
docker ps

# View logs
docker logs -f nifty-trading-bot

# Execute command in running container
docker exec -it nifty-trading-bot bash

# Stop container
docker stop nifty-trading-bot

# Start stopped container
docker start nifty-trading-bot

# Remove container
docker rm nifty-trading-bot

# View images
docker images

# Remove image
docker rmi nifty-trading-bot

# Clean up unused containers/images
docker system prune -a
```

---

### Docker Compose Commands

```bash
# Start services (background)
docker compose up -d

# Start services (foreground, see logs)
docker compose up

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f trading-bot

# Restart services
docker compose restart

# Rebuild and start
docker compose up -d --build

# View running services
docker compose ps

# Execute command in service
docker compose exec trading-bot bash
```

---

### WSL Commands

```bash
# List WSL distributions
wsl --list --verbose

# Set default distribution
wsl --set-default Ubuntu-22.04

# Shutdown WSL
wsl --shutdown

# Start specific distribution
wsl -d Ubuntu-22.04

# Update WSL
wsl --update

# Access Windows drives
cd /mnt/c  # C: drive
cd /mnt/d  # D: drive

# Access Linux files from Windows
\\wsl$\Ubuntu-22.04\home\trading\
```

---

### File Management

```bash
# Copy Windows files to container
docker cp /mnt/d/dhan_algo/creds.py nifty-trading-bot:/app/

# Copy container files to Windows
docker cp nifty-trading-bot:/app/logs/bot.log /mnt/d/dhan_algo/logs/

# View container files
docker exec nifty-trading-bot ls -la /app/

# Edit file in running container
docker exec -it nifty-trading-bot nano /app/strategy_config.py

# Backup container data
docker export nifty-trading-bot > /mnt/d/backups/trading-bot-backup.tar
```

---

## 🔧 ADVANCED CONFIGURATION

### Environment Variables

**Edit docker-compose.yml:**

```yaml
services:
  trading-bot:
    environment:
      - TZ=Asia/Kolkata
      - PYTHONUNBUFFERED=1
      - PAPER_TRADING_MODE=True
      - MAX_TRADES_PER_DAY=2
      - LOG_LEVEL=INFO
```

**Or use .env file:**

```bash
# Create .env file
cat > .env << EOF
TZ=Asia/Kolkata
PAPER_TRADING_MODE=True
MAX_TRADES=2
EOF

# docker-compose.yml will auto-read .env
```

---

### Auto-Restart on Crash

**Already configured in docker-compose.yml:**

```yaml
restart: unless-stopped
```

**Options:**
- `no` - Never restart
- `always` - Always restart
- `on-failure` - Restart only if crashed
- `unless-stopped` - Restart unless manually stopped

---

### Scheduled Start/Stop

**Using Windows Task Scheduler:**

**Create start script (start-bot.ps1):**
```powershell
wsl -d Ubuntu-22.04 -e bash -c "cd /mnt/d/dhan_algo && docker compose up -d"
```

**Create stop script (stop-bot.ps1):**
```powershell
wsl -d Ubuntu-22.04 -e bash -c "cd /mnt/d/dhan_algo && docker compose down"
```

**Schedule in Task Scheduler:**
- Start: 9:10 AM daily (before market)
- Stop: 3:40 PM daily (after market)

---

### Log Rotation

**Configured in docker-compose.yml:**

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    # Max 10 MB per log file
    max-file: "3"      # Keep last 3 files
```

**Logs stored at:**
```
C:\ProgramData\Docker\containers\<container-id>\<container-id>-json.log
```

---

### Resource Limits

**Add to docker-compose.yml:**

```yaml
services:
  trading-bot:
    deploy:
      resources:
        limits:
          cpus: '0.5'      # 50% of 1 CPU
          memory: 512M     # 512 MB RAM
        reservations:
          cpus: '0.25'     # Guaranteed 25% CPU
          memory: 256M     # Guaranteed 256 MB
```

---

## 🐛 TROUBLESHOOTING

### WSL Issues

**WSL not installing:**
```powershell
# Enable Windows features manually
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer
# Then install Ubuntu from Microsoft Store
```

**WSL slow:**
```powershell
# Set WSL 2 as default
wsl --set-default-version 2

# Convert existing distribution to WSL 2
wsl --set-version Ubuntu-22.04 2
```

**Can't access Windows files:**
```bash
# Windows drives auto-mount at /mnt/
# Check if mounted
ls /mnt/c
ls /mnt/d

# If not mounted, add to /etc/wsl.conf
sudo nano /etc/wsl.conf

# Add:
[automount]
enabled = true
root = /mnt/
```

---

### Docker Issues

**Docker not starting:**
```powershell
# Restart Docker Desktop
# Or restart WSL
wsl --shutdown

# Then start Docker Desktop again
```

**Permission denied:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
# Or use newgrp
newgrp docker
```

**Port already in use:**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :80

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

**Out of disk space:**
```powershell
# Clean Docker
docker system prune -a --volumes

# Free up space: delete unused images/containers
```

---

### Container Issues

**Container not starting:**
```bash
# View container logs
docker logs nifty-trading-bot

# Check container status
docker ps -a

# View error details
docker inspect nifty-trading-bot
```

**Can't connect to API:**
```bash
# Check environment variables
docker exec nifty-trading-bot env

# Test API inside container
docker exec -it nifty-trading-bot python -c "from dhanhq import dhanhq; print('OK')"

# Check creds.py mounted correctly
docker exec nifty-trading-bot cat /app/creds.py
```

**Logs not persisting:**
```bash
# Check volume mounts
docker inspect nifty-trading-bot | grep -A 10 Mounts

# Verify local directory exists
ls -la /mnt/d/dhan_algo/logs

# Recreate with correct mounts
docker compose down
docker compose up -d
```

---

## 📊 MONITORING & MAINTENANCE

### Health Checks

**Add to Dockerfile:**

```dockerfile
HEALTHCHECK --interval=1m --timeout=10s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"
```

**Check health:**

```bash
docker ps
# Shows health status

docker inspect nifty-trading-bot | grep -A 10 Health
```

---

### Automated Backups

**Create backup script (backup.sh):**

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/mnt/d/backups"

# Backup container data
docker export nifty-trading-bot > $BACKUP_DIR/container_$DATE.tar

# Backup volumes
docker run --rm \
  -v trading-logs:/logs \
  -v $BACKUP_DIR:/backup \
  ubuntu tar czf /backup/logs_$DATE.tar.gz -C /logs .

# Backup configuration
cp /mnt/d/dhan_algo/*.py $BACKUP_DIR/config_$DATE/
cp /mnt/d/dhan_algo/*.yml $BACKUP_DIR/config_$DATE/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar*" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Schedule with cron:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 4 AM
0 4 * * * /mnt/d/dhan_algo/backup.sh
```

---

### Update Trading Bot

**After code changes:**

```bash
# Rebuild image
docker compose build

# Restart with new image
docker compose up -d

# Or in one command
docker compose up -d --build
```

**Update security IDs weekly:**

```bash
# Run update script in container
docker compose exec trading-bot python get_all_security_ids.py
docker compose exec trading-bot python create_security_map.py

# Restart to reload
docker compose restart
```

---

## 🎯 QUICK REFERENCE

### Daily Operations

**Start bot (morning):**
```bash
cd /mnt/d/dhan_algo
docker compose up -d
docker compose logs -f
```

**Check status (during day):**
```bash
docker compose ps
docker compose logs --tail=50
cat logs/bot.log
cat data/livetrading_$(date +%d%m%y).csv
```

**Stop bot (evening):**
```bash
docker compose down
```

---

### Weekly Maintenance

**Update security IDs:**
```bash
docker compose exec trading-bot python get_all_security_ids.py
docker compose exec trading-bot python create_security_map.py
docker compose restart
```

**Review logs:**
```bash
# View all logs
ls -lh logs/

# Check for errors
grep -i error logs/*.log

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

---

### Monthly Tasks

**Update Docker image:**
```bash
docker compose build --pull
docker compose up -d
```

**Clean Docker:**
```bash
docker system prune -a
```

**Backup everything:**
```bash
./backup.sh
```

---

## 🎉 SUMMARY

**You Now Have:**

✅ **WSL 2** - Full Linux on Windows
✅ **Docker** - Containerized trading bot  
✅ **Local Testing** - Test before cloud deployment  
✅ **Cloud Ready** - Deploy to AWS/Azure with same image  
✅ **Auto-Restart** - Survives crashes  
✅ **Easy Updates** - Rebuild and restart  
✅ **Persistent Logs** - Saved to Windows  
✅ **Professional Setup** - Industry standard DevOps

**Workflow:**

1. **Develop** - Edit Python files in Windows (VS Code)
2. **Build** - `docker compose build` in WSL
3. **Test Locally** - `docker compose up` in WSL
4. **Verify** - Check logs, test paper trading
5. **Deploy to Cloud** - Push same image to AWS
6. **Monitor** - View logs locally or in cloud
7. **Profit!** - Bot runs 24/7 automatically

**Next Steps:**

1. ✅ Install WSL (Done after restart)
2. ✅ Install Docker Desktop
3. ✅ Build Docker image
4. ✅ Test locally in paper mode
5. ✅ Deploy to AWS EC2
6. ✅ Switch to live trading

---

**Created:** 05-Apr-2026 02:00 AM  
**Status:** Complete WSL + Docker Guide  
**Ready:** Local & Cloud Deployment  

**Happy Containerized Trading!** 🐳🚀
