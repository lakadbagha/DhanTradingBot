# 🚀 DOCKER QUICK REFERENCE CARD

**Last Updated:** 05-Apr-2026 02:15 AM  
**Status:** ✅ READY FOR PRODUCTION

---

## 🎯 ONE-CLICK COMMANDS

### Start Bot (Double-click)
```
start-bot.ps1
```

### Stop Bot (Double-click)  
```
stop-bot.ps1
```

### Monitor Bot (Double-click)
```
monitor-bot.ps1
```

---

## 📊 MANUAL COMMANDS

### Start
```powershell
cd D:\dhan_algo
docker compose up -d
```

### Stop
```powershell
docker compose down
```

### View Logs
```powershell
docker compose logs -f           # Live logs
docker compose logs --tail=50    # Last 50 lines
```

### Check Status
```powershell
docker compose ps                # Container status
docker ps                        # Detailed status
docker stats nifty-trading-bot   # CPU/Memory usage
```

### Restart
```powershell
docker compose restart
```

### Rebuild (after code changes)
```powershell
docker compose build
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

### Docker Files
```
D:\dhan_algo\Dockerfile
D:\dhan_algo\docker-compose.yml
D:\dhan_algo\.dockerignore
```

---

## 🔧 COMMON TASKS

### View Today's Trades
```powershell
type data\livetrading_*.csv
```

### View Last 20 Log Lines
```powershell
Get-Content logs\trading_log_*.log -Tail 20
```

### Execute Command in Container
```powershell
docker compose exec trading-bot ls -la /app
docker compose exec trading-bot python --version
docker compose exec trading-bot cat /app/strategy_config.py
```

### Update Security IDs
```powershell
docker compose exec trading-bot python get_all_security_ids.py
docker compose exec trading-bot python create_security_map.py
docker compose restart
```

---

## 🐛 TROUBLESHOOTING

### Container Not Starting
```powershell
docker compose logs --tail=100
docker compose down
docker compose up -d
```

### Rebuild from Scratch
```powershell
docker compose down
docker rmi nifty-trading-bot
docker compose build --no-cache
docker compose up -d
```

### Clean Everything
```powershell
docker compose down -v
docker system prune -a
docker compose build
docker compose up -d
```

---

## ⏰ DAILY ROUTINE

### Before Market (9:10 AM)
1. Run `start-bot.ps1`
2. Check logs: `docker compose logs -f`
3. Verify bot is running

### During Market (9:15 AM - 3:30 PM)
1. Monitor: `monitor-bot.ps1`
2. Check trades: `type data\livetrading_*.csv`
3. Watch for errors in logs

### After Market (3:35 PM)
1. Run `stop-bot.ps1`
2. Review trades
3. Check for errors
4. Backup important files

---

## 🔄 DOCKER IMAGE INFO

| Property | Value |
|----------|-------|
| **Name** | `nifty-trading-bot:latest` |
| **Size** | 748MB |
| **Base** | Python 3.11-slim |
| **Created** | 05-Apr-2026 02:12 AM |
| **Status** | ✅ Ready |

---

## 📞 EMERGENCY COMMANDS

### Force Stop Everything
```powershell
docker stop nifty-trading-bot
docker compose down -v
```

### Check What's Running
```powershell
docker ps -a
```

### View All Images
```powershell
docker images
```

### Clean All Docker Data
```powershell
docker system prune -a --volumes
# WARNING: This removes ALL Docker data!
```

---

## ✅ PRE-FLIGHT CHECKLIST

**Before starting bot:**
- [ ] Docker Desktop is running
- [ ] Internet connection is stable
- [ ] `PAPER_TRADING_MODE` setting is correct
- [ ] Credentials in `creds.py` are valid
- [ ] Sufficient margin in Dhan account
- [ ] Time is between 9:10 AM - 3:30 PM

---

## 🎯 CONFIGURATION FILES

| File | Purpose |
|------|---------|
| `strategy_config.py` | Trading parameters (SL, Target, Max Trades) |
| `creds.py` | Dhan API credentials |
| `security_id_map.py` | Option chain security IDs |
| `position_manager.py` | Position management logic |

**To modify:** Edit file → Run `docker compose build` → Run `docker compose up -d`

---

## 📊 MONITORING DASHBOARD

Access via: `monitor-bot.ps1`

**Available Options:**
1. Live Logs
2. Last 50 Lines
3. Container Status
4. CPU/Memory Stats
5. Today's Trades
6. Log File
7. Restart Container
8. Stop Bot
9. Execute Command
0. Exit

---

## 🌐 CLOUD DEPLOYMENT

**Your image is ready for cloud deployment!**

### AWS EC2
```bash
scp -r D:\dhan_algo ubuntu@your-ec2-ip:/home/ubuntu/
ssh ubuntu@your-ec2-ip
cd /home/ubuntu/dhan_algo
docker compose up -d
```

### Docker Hub
```powershell
docker login
docker tag nifty-trading-bot your-username/nifty-trading-bot:latest
docker push your-username/nifty-trading-bot:latest
```

---

## 📈 NEXT STEPS

1. **Test in Paper Mode**
   - Run for 2-3 days
   - Verify signals are correct
   - Check trades are logged

2. **Switch to Live Mode**
   - Set `PAPER_TRADING_MODE = False`
   - Rebuild: `docker compose build`
   - Start: `docker compose up -d`

3. **Monitor Performance**
   - Daily trade review
   - Weekly P&L analysis
   - Monthly strategy optimization

---

**Quick Access:**
- 📄 Full Guide: `DOCKER_DEPLOYMENT_SUCCESS.md`
- 🚀 Start: `start-bot.ps1`
- 🛑 Stop: `stop-bot.ps1`
- 📊 Monitor: `monitor-bot.ps1`

**Status:** ✅ DEPLOYMENT COMPLETE - READY TO TRADE! 🚀
