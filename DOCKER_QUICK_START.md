# 🚀 QUICK START - WSL + Docker Deployment

**Get your trading bot running in containers in 15 minutes!**

---

## ⚡ FASTEST SETUP (Windows)

### Step 1: Install WSL + Docker

**Open PowerShell as Administrator:**

```powershell
# Navigate to project
cd D:\dhan_algo

# Run installation script
.\install-wsl.ps1
```

**This will:**
- ✅ Check Windows version
- ✅ Install WSL 2
- ✅ Install Ubuntu 22.04
- ✅ Guide you to install Docker Desktop
- ✅ Run automated setup

**Time:** 10-15 minutes (including restart)

---

### Step 2: Build & Run

**After restart, in Ubuntu terminal:**

```bash
cd /mnt/d/dhan_algo
./setup.sh
```

**Or manually:**

```bash
# Build Docker image
docker build -t nifty-trading-bot .

# Run with Docker Compose
docker compose up -d

# View logs
docker compose logs -f
```

---

## 📊 VERIFY IT'S WORKING

**Check container status:**

```bash
docker compose ps
# Should show: nifty-trading-bot    Up

docker compose logs --tail=50
# Should show: Market is closed (outside 9:15-3:30)
```

**Check files:**

```bash
ls -la logs/
# Should show: bot.log

cat logs/bot.log
# Should show: Trading engine logs
```

---

## 🎯 DAILY USAGE

### Start Bot (Morning)

```bash
cd /mnt/d/dhan_algo
docker compose up -d
```

### Monitor (During Day)

```bash
# Live logs
docker compose logs -f

# Or view file
tail -f logs/bot.log

# Check trades
cat data/livetrading_$(date +%d%m%y).csv
```

### Stop Bot (Evening)

```bash
docker compose down
```

---

## 🔄 WEEKLY UPDATES

**Update security IDs (new expiry):**

```bash
docker compose exec trading-bot python get_all_security_ids.py
docker compose exec trading-bot python create_security_map.py
docker compose restart
```

---

## ☁️ DEPLOY TO CLOUD

**After local testing works:**

```bash
# Push to Docker Hub
docker login
docker tag nifty-trading-bot your-username/nifty-trading-bot
docker push your-username/nifty-trading-bot

# Deploy on AWS EC2
ssh ubuntu@YOUR_SERVER
docker pull your-username/nifty-trading-bot
docker run -d --restart unless-stopped \
  -v ~/logs:/app/logs \
  -v ~/data:/app/data \
  your-username/nifty-trading-bot
```

**Same code runs everywhere!** 🎉

---

## 📚 COMPLETE DOCUMENTATION

### For Installation:
- **WSL_DOCKER_COMPLETE_GUIDE.md** - Full WSL + Docker guide
- **install-wsl.ps1** - Automated Windows setup
- **setup.sh** - Automated Linux setup

### For Trading:
- **COMPLETE_TRADING_SYSTEM.md** - All strategies & logic
- **DEPLOYMENT_GUIDE.md** - Cloud deployment options

### For Configuration:
- **Dockerfile** - Container definition
- **docker-compose.yml** - Service configuration
- **requirements.txt** - Python dependencies

---

## 🆘 TROUBLESHOOTING

**Container won't start:**
```bash
docker compose logs
# Check error message
```

**Can't connect to API:**
```bash
docker compose exec trading-bot python -c "from dhanhq import dhanhq; print('OK')"
# Test if dhanhq installed
```

**Files not persisting:**
```bash
docker compose down
docker compose up -d
# Recreate container
```

**Need to rebuild:**
```bash
docker compose build --no-cache
docker compose up -d
```

---

## ✅ CHECKLIST

### First Time Setup:
- [ ] Install WSL (run install-wsl.ps1)
- [ ] Restart computer
- [ ] Install Docker Desktop
- [ ] Run setup.sh in Ubuntu
- [ ] Verify container starts

### Before Live Trading:
- [ ] Test in paper mode 3-5 days
- [ ] Verify signals detected
- [ ] Check CSV logs created
- [ ] Confirm API connection works
- [ ] Update security_id_map.py

### Weekly:
- [ ] Update security IDs (new expiry)
- [ ] Check logs for errors
- [ ] Backup CSV files
- [ ] Review trade performance

---

## 🎉 ADVANTAGES

### Local Development:
- ✅ Edit code in Windows
- ✅ Test in Docker container
- ✅ Same environment as production
- ✅ Fast iteration cycle

### Cloud Deployment:
- ✅ Push Docker image
- ✅ Run anywhere (AWS, Azure, etc.)
- ✅ Guaranteed same behavior
- ✅ Easy scaling

### Maintenance:
- ✅ Update code once
- ✅ Rebuild image
- ✅ Deploy everywhere
- ✅ Version control with Git

---

## 💡 PRO TIPS

**Access container shell:**
```bash
docker compose exec trading-bot bash
# Now you're inside container
```

**Copy files in/out:**
```bash
# From container to Windows
docker cp nifty-trading-bot:/app/logs/bot.log D:/backups/

# From Windows to container
docker cp D:/dhan_algo/creds.py nifty-trading-bot:/app/
```

**View resource usage:**
```bash
docker stats nifty-trading-bot
```

**Export/Import image:**
```bash
# Save image to file
docker save nifty-trading-bot > trading-bot.tar

# Load image from file
docker load < trading-bot.tar
```

---

## 📞 SUPPORT

**WSL Issues:**
- https://docs.microsoft.com/en-us/windows/wsl/

**Docker Issues:**
- https://docs.docker.com/desktop/troubleshoot/overview/

**Trading Bot Issues:**
- Check: COMPLETE_TRADING_SYSTEM.md
- Check: logs/bot.log

---

## 🎯 SUMMARY

**What You Have:**
- ✅ Trading bot in Docker container
- ✅ Runs on Windows (WSL)
- ✅ Same image deploys to cloud
- ✅ Automatic restart on crash
- ✅ Persistent logs & data
- ✅ Professional DevOps setup

**Time Investment:**
- Setup: 15 minutes (one time)
- Daily: 2 minutes (start/stop)
- Weekly: 5 minutes (update IDs)
- Monthly: 10 minutes (maintenance)

**Cost:**
- Local: $0 (just electricity)
- AWS: $0-10/month (free tier → t3.micro)

**Get Started:**
```powershell
# Windows PowerShell (Admin)
cd D:\dhan_algo
.\install-wsl.ps1
```

**That's it!** 🚀

---

**Created:** 05-Apr-2026  
**Status:** Ready to Deploy  
**Platform:** Windows WSL + Docker  
