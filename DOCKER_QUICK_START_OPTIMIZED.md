# ⚡ DOCKER QUICK START - OPTIMIZED WORKFLOW

**Updated:** 05-Apr-2026 11:30 AM  
**Configuration:** ✅ Optimized (No Duplicates)

---

## 🚀 DAILY TRADING WORKFLOW

### Morning - Before Market (9:10 AM)

**Double-click:**
```
start-bot.ps1
```

**Or manually:**
```powershell
cd D:\dhan_algo
docker compose up -d
docker compose logs -f
```

✅ **Starts in ~5 seconds** (no rebuilding!)

---

### During Market - Monitor (9:15 AM - 3:30 PM)

**Double-click:**
```
monitor-bot.ps1
```

**Or check manually:**
```powershell
docker compose logs -f              # Live logs
type data\livetrading_*.csv         # Today's trades
```

---

### Evening - After Market (3:35 PM)

**Double-click:**
```
stop-bot.ps1
```

**Or manually:**
```powershell
docker compose down
```

---

## 🔧 WHEN YOU CHANGE CODE

### Step 1: Edit Your Files
```
Edit: strategy_config.py, live_trading_engine_optimized.py, etc.
```

### Step 2: Rebuild Docker Image
```powershell
docker build -t nifty-trading-bot .
```

### Step 3: Restart Container
```powershell
docker compose down
docker compose up -d
```

---

## 📊 QUICK CHECKS

### Check If Running
```powershell
docker compose ps
```

### View Last 50 Log Lines
```powershell
docker compose logs --tail=50
```

### Check Today's Trades
```powershell
type data\livetrading_*.csv
```

### Check Docker Image
```powershell
docker images nifty-trading-bot
```

**Expected:**
```
REPOSITORY          TAG       SIZE
nifty-trading-bot   latest    748MB
```

---

## 🛠️ MAINTENANCE COMMANDS

### Restart Container
```powershell
docker compose restart
```

### View Container Stats (CPU/Memory)
```powershell
docker stats nifty-trading-bot
```

### Clean Up Docker
```powershell
docker system prune -a
```

### Rebuild from Scratch
```powershell
docker build -t nifty-trading-bot . --no-cache
docker compose down
docker compose up -d
```

---

## 📁 FILE LOCATIONS

### Logs
```
D:\dhan_algo\logs\trading_log_DDMMYY.log
```

### Trades
```
D:\dhan_algo\data\livetrading_DDMMYY.csv
```

### Docker Config
```
D:\dhan_algo\docker-compose.yml
D:\dhan_algo\Dockerfile
```

---

## ✅ CURRENT STATUS

**Docker Image:**
- Name: `nifty-trading-bot:latest`
- Size: `748 MB`
- Status: ✅ Ready

**Configuration:**
- ✅ No duplicate images
- ✅ Fast startup (~5 seconds)
- ✅ Auto-restart enabled
- ✅ Logs persistent

**Scripts:**
- ✅ `start-bot.ps1` - Start trading
- ✅ `stop-bot.ps1` - Stop trading
- ✅ `monitor-bot.ps1` - Monitor dashboard

---

## 🎯 TODAY'S CHECKLIST

**Before Market Opens (9:10 AM):**
- [ ] Docker Desktop running
- [ ] Internet connected
- [ ] Run `start-bot.ps1`
- [ ] Check logs: `docker compose logs -f`

**During Market:**
- [ ] Monitor: `monitor-bot.ps1`
- [ ] Watch for signals in logs
- [ ] Check trades: `type data\livetrading_*.csv`

**After Market:**
- [ ] Run `stop-bot.ps1`
- [ ] Review trades
- [ ] Check for errors in logs

---

## 💡 PRO TIPS

**Fast Startup:**
- Container starts in ~5 seconds (no rebuild needed)
- Only rebuild when you change code

**Monitor Live:**
- Use `monitor-bot.ps1` for interactive dashboard
- Or `docker compose logs -f` for live logs

**Save Disk Space:**
- Only 1 image (748 MB)
- Run `docker system prune -a` monthly

**Quick Updates:**
- Change strategy? Edit `strategy_config.py` → Rebuild
- Update security IDs? Run inside container (no rebuild)

---

## 📞 EMERGENCY COMMANDS

**Container Won't Start:**
```powershell
docker compose down
docker compose up -d
docker compose logs
```

**Reset Everything:**
```powershell
docker compose down
docker system prune -a
docker build -t nifty-trading-bot .
docker compose up -d
```

**Check What's Wrong:**
```powershell
docker compose logs --tail=100
docker ps -a
docker images
```

---

**📄 Full Guides:**
- `DOCKER_DEPLOYMENT_SUCCESS.md` - Complete deployment guide
- `DOCKER_CONFIGURATION_UPDATE.md` - Optimization details
- `DOCKER_QUICK_REFERENCE.md` - All commands

---

**✅ Status:** Optimized & Ready  
**⚡ Startup:** 5 seconds  
**💾 Disk:** 748 MB (single image)  
**🚀 Ready:** For production trading!
