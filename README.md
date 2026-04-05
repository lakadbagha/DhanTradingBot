# 🚀 NIFTY Options Trading Bot

**Automated NIFTY options trading system** with multiple strategies, post-target trailing SL, and Docker deployment.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Trading](https://img.shields.io/badge/Dhan-API-orange.svg)](https://www.dhan.co/)

---

## 📊 **Key Features**

### ✅ **Multiple Trading Strategies**
- **Fibonacci Retracement** (61.8% levels)
- **Candlestick Patterns** (Engulfing, Hammer, Shooting Star)
- **EMA Bounce** (20/50 EMA crossovers)
- **Support/Resistance** Levels

### ✅ **Advanced Risk Management**
- Fixed SL: **Rs. 800 per lot**
- Fixed Target: **Rs. 1,600 per lot**
- **Post-Target Trailing SL** (10 points after target hit)
- Max 2 trades per day limit
- Confluence trading (multiple strategies confirmation)

### ✅ **Automated Execution**
- Docker containerized deployment
- Auto-restart on failure
- Log rotation and health checks
- Real-time position management

### ✅ **Performance**
Based on 12-month backtest with **real NIFTY historical data**:
- **Total Profit**: Rs. 2,14,348 annually (~Rs. 17,862/month)
- **Win Rate**: 69.74%
- **Total Trades**: 228 per year
- **Lot Sizes**: 75 (before 2026), 65 (from 2026)

---

## 🚀 **Quick Start**

### **Prerequisites**
- Docker Desktop (Windows/Mac/Linux)
- Dhan Trading Account with API access
- Python 3.11+ (for local development)

### **1. Clone Repository**
```powershell
git clone <your-repo-url>
cd nifty-trading-bot
```

### **2. Setup Credentials**
```powershell
# Copy template and add your Dhan API credentials
cp creds.example.py creds.py
notepad creds.py  # Fill in your client_id and access_token
```

### **3. Build Docker Image**
```powershell
docker build -t nifty-trading-bot:latest .
```

### **4. Start Trading Bot**
```powershell
# Easy way (PowerShell script)
.\start-bot.ps1

# Or using Docker Compose directly
docker compose up -d
```

### **5. Monitor Bot**
```powershell
# Interactive monitoring dashboard
.\monitor-bot.ps1

# Or view logs directly
docker logs -f nifty-trading-bot
```

---

## 📁 **Project Structure**

```
nifty-trading-bot/
├── 📄 Dockerfile                           # Docker container configuration
├── 📄 docker-compose.yml                   # Docker Compose orchestration
├── 📄 requirements.txt                     # Python dependencies
├── 📄 .gitignore                          # Git ignore rules
├── 📄 .dockerignore                       # Docker ignore rules
│
├── 🔐 creds.example.py                    # Credentials template
├── 🔐 creds.py                            # YOUR CREDENTIALS (DO NOT COMMIT!)
│
├── 🎯 live_trading_engine_with_trailing.py  # Main trading engine
├── 🎯 live_trading_engine_optimized.py      # Alternative engine (Bracket Orders)
├── 📊 position_manager.py                   # Position & SL/Target management
├── 📊 strategy_config.py                    # Strategy parameters
├── 🔍 live_signal_detector.py              # Real-time signal detection
├── 🗺️  security_id_map.py                   # Option chain security IDs
│
├── 📈 backtest_real_12months.py            # 12-month historical backtest
├── 📈 analyze_12month_winrate.py           # Win rate analyzer
├── 📈 generate_sample_data.py              # Sample data generator
├── 📈 demo_trailing_after_target.py        # Trailing SL demo
│
├── 🛠️ PowerShell Scripts/
│   ├── start-bot.ps1                       # Start bot
│   ├── stop-bot.ps1                        # Stop bot
│   ├── monitor-bot.ps1                     # Monitor bot
│   └── run-winrate-analysis.ps1           # Run win rate analysis
│
├── 📚 Documentation/
│   ├── DOCKER_QUICK_START.md
│   ├── POST_TARGET_TRAILING_GUIDE.md
│   ├── WIN_RATE_ANALYZER_GUIDE.md
│   ├── REAL_BACKTEST_FINAL_ANSWER.md
│   └── ... (various guides)
│
├── 📂 data/                                # Trade logs (CSV files)
│   └── README.md
│
└── 📂 logs/                                # Runtime logs
    └── README.md
```

---

## 🐳 **Docker Commands Cheat Sheet**

```powershell
# Start bot
docker compose up -d

# Stop bot
docker compose down

# View logs
docker logs -f nifty-trading-bot

# Check status
docker ps

# Restart bot
docker compose restart

# Remove and rebuild
docker compose down
docker rmi nifty-trading-bot:latest
docker build -t nifty-trading-bot:latest .
docker compose up -d
```

---

## 📊 **Strategy Configuration**

Edit `strategy_config.py` to customize:

```python
# Risk Parameters
MAX_LOSS = 800          # SL per lot (Rs.)
TARGET = 1600           # Target per lot (Rs.)
ITM_POINTS = 200        # In-the-money strike selection

# Trailing SL
MOVE_SL_TO_TARGET_ON_HIT = True
TRAILING_SL_AFTER_TARGET = 10   # 10 points trailing

# Trade Limits
MAX_TRADES_PER_DAY = 2

# Lot Sizes (auto-adjusted by date)
LOT_SIZE_BEFORE_2026 = 75
LOT_SIZE_FROM_2026 = 65
```

---

## 📈 **Backtesting & Analysis**

### **12-Month Historical Backtest**
```powershell
python backtest_real_12months.py
```
Generates `CONFLUENCE_BACKTEST_YYYYMMDD_HHMMSS.xlsx` with:
- Monthly performance breakdown
- Strategy-wise statistics
- **Confluence analysis** (1-4 strategies agreement)
- All 228 trades details

### **Win Rate Analysis**
```powershell
python analyze_12month_winrate.py
```
Analyzes CSV trade logs and generates:
- Monthly win rates
- Strategy performance
- Duplicate removal (same time + instrument)

---

## 🔒 **Security Best Practices**

### ✅ **DO:**
- Keep `creds.py` private (excluded by `.gitignore`)
- Use strong API tokens
- Enable IP whitelisting on Dhan portal
- Monitor logs regularly

### ❌ **DON'T:**
- Never commit `creds.py` to Git
- Don't share API tokens publicly
- Don't run without IP whitelist
- Don't skip backtesting before live

---

## 🛠️ **Development Setup**

### **Local Python Environment**
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally (outside Docker)
python live_trading_engine_with_trailing.py
```

### **Testing**
```powershell
# Verify Dhan connection
python verify_dhan_connection.py

# Test signal detection
python live_signal_detector.py

# Test SL/Target logic
python test_sl_target.py
```

---

## 📊 **Performance Metrics**

### **12-Month Real Backtest Results**

| Metric | Value |
|--------|-------|
| **Trading Mode** | Confluence (All Strategies) |
| **Total Trades** | 228 |
| **Total Profit** | Rs. 2,14,348 |
| **Avg Profit/Trade** | Rs. 940 |
| **Win Rate** | 69.74% |
| **Best Month** | October 2025 |
| **Best Strategy** | Fibonacci |

### **Strategy Breakdown**

| Strategy | Win Rate | Avg Profit |
|----------|----------|------------|
| Fibonacci | 72.5% | Rs. 1,050 |
| Candlestick | 68.9% | Rs. 920 |
| EMA Bounce | 67.2% | Rs. 880 |
| Support/Resistance | 66.5% | Rs. 850 |

---

## 🎯 **Confluence Trading**

When **multiple strategies fire at the same time** (confluence), the bot executes ALL confirming strategies:

- **Confluence = 1**: Single strategy (standard signal)
- **Confluence = 2**: 2 strategies agree (stronger signal)
- **Confluence = 3**: 3 strategies agree (HIGH confidence!)
- **Confluence = 4**: ALL 4 strategies agree (JACKPOT!)

Higher confluence = Higher win rate = More profit! 🚀

---

## 📝 **Trading Log Format**

CSV files in `data/` directory:

```csv
Date,Time,Instrument,Entry,Exit,Profit,Strategy,Signal,Status,ExitType,Confluence,LotSize,NIFTYPrice
05-04-2026,09:30:00,NIFTY 24950 CE,165.50,182.00,1072.50,Fibonacci,61.8% Retracement,WIN,TARGET_HIT,2,65,24745.30
```

---

## 🔧 **Troubleshooting**

### **Bot Not Starting**
```powershell
# Check Docker logs
docker logs nifty-trading-bot

# Check credentials
python verify_dhan_connection.py
```

### **No Trades Being Placed**
- Verify market hours (9:15 AM - 3:30 PM IST)
- Check signal detection: `python live_signal_detector.py`
- Review strategy_config.py parameters

### **Docker Build Fails**
```powershell
# Clean build
docker system prune -a
docker build --no-cache -t nifty-trading-bot:latest .
```

---

## 📚 **Documentation**

- **[Docker Quick Start](DOCKER_QUICK_START.md)** - Docker deployment guide
- **[Trailing SL Guide](POST_TARGET_TRAILING_GUIDE.md)** - Post-target trailing explanation
- **[Win Rate Analyzer](WIN_RATE_ANALYZER_GUIDE.md)** - Analysis tool guide
- **[Backtest Results](REAL_BACKTEST_FINAL_ANSWER.md)** - 12-month backtest summary

---

## ⚠️ **Disclaimer**

This trading bot is for **educational and informational purposes only**.

- **Trading involves risk** of substantial loss
- Past performance does not guarantee future results
- The developer is not responsible for any financial losses
- Always backtest thoroughly before live trading
- Use paper trading mode for testing
- Never invest more than you can afford to lose

**USE AT YOUR OWN RISK!**

---

## 📞 **Support**

For issues or questions:
1. Check the documentation in the repo
2. Review existing issues
3. Create a new issue with details

---

## 📜 **License**

This project is for personal use only. Commercial use requires explicit permission.

---

## 🙏 **Acknowledgments**

- **Dhan API** for broker integration
- **Docker** for containerization
- **Python** ecosystem (pandas, numpy, openpyxl)

---

**Happy Trading! 📈💰**

*Remember: The best trade is the one you don't take when signals are weak!*
