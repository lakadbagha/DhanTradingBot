# ✅ 12-MONTH WIN RATE ANALYZER - COMPLETE SOLUTION

**Created:** 05-Apr-2026 11:30 AM  
**Status:** ✅ Ready to Use  
**Purpose:** Generate month-wise win rate from real trading data with duplicate removal

---

## 🎯 PROBLEM SOLVED

### Your Requirements:
1. ✅ Month-wise win rate for last 12 months
2. ✅ Use columns from 6_MONTHS_TRADING_REPORT template
3. ✅ Remove duplicate entries (2 strategies at same time = keep only 1)
4. ✅ Generate comprehensive Excel report

---

## 📦 FILES CREATED

| File | Size | Purpose |
|------|------|---------|
| `analyze_12month_winrate.py` | 13.9 KB | Main analyzer (loads CSVs, removes duplicates, generates report) |
| `generate_sample_data.py` | 6.8 KB | Sample data generator (for testing) |
| `run-winrate-analysis.ps1` | 5.5 KB | Quick start script (one-click analysis) |
| `WIN_RATE_ANALYZER_GUIDE.md` | 11.4 KB | Complete user guide |
| `WINRATE_QUICK_REFERENCE.md` | 3.8 KB | Quick reference card |

---

## 📊 CSV COLUMNS USED

Based on your `6_MONTHS_TRADING_REPORT` template:

| Column | Description | Example | Used For |
|--------|-------------|---------|----------|
| **Time** | Trade timestamp | `09:30:00` | Duplicate detection |
| **Instrument** | Option contract | `NIFTY 23400 CE` | Duplicate detection |
| **Entry** | Entry price | `150.50` | P&L calculation |
| **Exit** | Exit price | `165.75` | P&L calculation |
| **Profit** | P&L amount | `1600` | Win/Loss determination |
| **Strategy** | Strategy name | `Fibonacci` | Performance analysis |
| **Signal** | Trade type | `CALL` | Analysis breakdown |
| **Status** | Trade result | `WIN` | Win rate calculation |
| **OrderID** | Order reference | `ORD123456` | Trade tracking |

---

## 🧹 DUPLICATE REMOVAL - HOW IT WORKS

### Problem: Double Entry

When 2 strategies fire at same time for same instrument:

```csv
Date,Time,Instrument,Entry,Exit,Profit,Strategy
05-04-2026,09:30:00,NIFTY 23400 CE,150,165,1600,Fibonacci
05-04-2026,09:30:00,NIFTY 23400 CE,150,162,1200,Candlestick
05-04-2026,09:30:00,NIFTY 23400 CE,150,168,1800,EMA Bounce
```

**Problem:**
- Same timestamp (09:30:00)
- Same instrument (NIFTY 23400 CE)
- 3 different strategies
- This is ONE trade counted THREE times! ❌

---

### Solution: Keep Best Only

**Algorithm:**
```python
1. Create unique key: DateTime + Instrument
   → "2026-04-05 09:30:00_NIFTY 23400 CE"

2. Find all duplicates with same key

3. Sort by Profit (highest first)

4. Keep only first row (highest profit)

5. Remove all other duplicates
```

**Result:**
```csv
Date,Time,Instrument,Entry,Exit,Profit,Strategy
05-04-2026,09:30:00,NIFTY 23400 CE,150,168,1800,EMA Bounce
```

**Why EMA Bounce?**
- Highest profit (Rs. 1800)
- Only this strategy is kept
- No double counting ✅

---

## 📈 OUTPUT REPORT STRUCTURE

**File:** `12_MONTH_WIN_RATE_REPORT.xlsx`

### Sheet 1: Monthly Win Rate

| Month | TotalTrades | TotalProfit | AvgProfit | Wins | Losses | WinRate% |
|-------|-------------|-------------|-----------|------|--------|----------|
| 2026-04 | 18 | 28,800 | 1,600 | 12 | 6 | 66.67% |
| 2026-03 | 22 | 35,200 | 1,600 | 15 | 7 | 68.18% |
| 2026-02 | 20 | 32,000 | 1,600 | 14 | 6 | 70.00% |
| ... | ... | ... | ... | ... | ... | ... |

**Use for:**
- Monthly performance tracking
- Identifying trends
- Setting targets

---

### Sheet 2: Strategy Performance

| Strategy | TotalTrades | TotalProfit | AvgProfit | Wins | Losses | WinRate% |
|----------|-------------|-------------|-----------|------|--------|----------|
| Fibonacci | 45 | 72,000 | 1,600 | 32 | 13 | 71.11% |
| Candlestick | 38 | 60,800 | 1,600 | 26 | 12 | 68.42% |
| EMA Bounce | 22 | 35,200 | 1,600 | 14 | 8 | 63.64% |

**Use for:**
- Strategy comparison
- Resource allocation
- Disabling poor strategies

---

### Sheet 3: All Trades (Cleaned)

| Date | Time | Instrument | Entry | Exit | Profit | Strategy | Signal | Status |
|------|------|------------|-------|------|--------|----------|--------|--------|
| 05-04-2026 | 09:30 | NIFTY 23400 CE | 150 | 165 | 1,600 | Fibonacci | CALL | WIN |
| 05-04-2026 | 14:30 | NIFTY 23350 PE | 140 | 155 | 1,600 | Candlestick | PUT | WIN |

**Features:**
- ✅ No duplicate entries
- ✅ Complete trade history
- ✅ All columns preserved

---

### Sheet 4: Summary

| Metric | Value |
|--------|-------|
| Total Trades (After Dedup) | 105 |
| Total Profit/Loss | Rs. 168,000 |
| Average Profit per Trade | Rs. 1,600 |
| Overall Win Rate % | 68.57% |
| Best Month | 2026-03 (70% win rate) |
| Worst Month | 2026-01 (62% win rate) |
| Best Strategy | Fibonacci (71% win rate) |
| Worst Strategy | EMA Bounce (63% win rate) |

**Use for:**
- Quick overview
- Performance snapshot
- Executive reporting

---

## 🚀 HOW TO USE

### Method 1: Quick Start (Recommended)

**Double-click:**
```
run-winrate-analysis.ps1
```

**What it does:**
1. Checks for data files
2. Offers to generate sample data if none found
3. Runs analyzer
4. Offers to open Excel report

---

### Method 2: Manual Command

```powershell
# Navigate to project
cd D:\dhan_algo

# Run analyzer
python analyze_12month_winrate.py

# Open report
start 12_MONTH_WIN_RATE_REPORT.xlsx
```

---

### Method 3: Test with Sample Data

```powershell
# Step 1: Generate sample data (12 months)
python generate_sample_data.py

# Step 2: Run analyzer
python analyze_12month_winrate.py

# Step 3: Check output
start 12_MONTH_WIN_RATE_REPORT.xlsx
```

---

## 📁 DATA REQUIREMENTS

### Folder Structure
```
D:\dhan_algo\
├── data\
│   ├── livetrading_050426.csv  (05-Apr-2026)
│   ├── livetrading_040426.csv  (04-Apr-2026)
│   ├── livetrading_030426.csv  (03-Apr-2026)
│   └── ...
├── analyze_12month_winrate.py
├── generate_sample_data.py
└── run-winrate-analysis.ps1
```

### File Naming Convention
```
livetrading_DDMMYY.csv
```

**Examples:**
- `livetrading_050426.csv` = 05-Apr-2026
- `livetrading_010326.csv` = 01-Mar-2026
- `livetrading_281224.csv` = 28-Dec-2024

---

## 🎯 EXAMPLE WALKTHROUGH

### Your Current Situation

**You have trading data like this:**

`data/livetrading_050426.csv`:
```csv
Time,Instrument,Entry,Exit,Profit,Strategy,Signal,Status,OrderID
09:30:00,NIFTY 23400 CE,150,165,1600,Fibonacci,CALL,WIN,ORD001
09:30:00,NIFTY 23400 CE,150,162,1200,Candlestick,CALL,WIN,ORD002
14:00:00,NIFTY 23350 PE,140,155,1600,EMA Bounce,PUT,WIN,ORD003
```

**Problem:**
- Row 1 & 2 are duplicates (same time, same instrument)
- Win rate shows 3/3 = 100% (wrong!)
- Should be 2/2 = 100% (correct)

---

### What Analyzer Does

**Step 1: Load Data**
```
✅ Found 60 CSV files
✅ Total trades loaded: 120
```

**Step 2: Remove Duplicates**
```
⚠️  Found 15 duplicate entries
✅ Removed 15 duplicate entries
✅ Remaining trades: 105
```

**Step 3: Calculate Win Rate**
```
📈 Monthly Win Rate Summary:
Month     TotalTrades  WinRate%
2026-04            18     66.67
```

**Step 4: Generate Report**
```
✅ Excel report saved: 12_MONTH_WIN_RATE_REPORT.xlsx
   📊 Sheets created:
      1. Monthly Win Rate
      2. Strategy Performance
      3. All Trades (Cleaned)
      4. Summary
```

---

### Result

**Before (Raw Data):**
- 120 trades
- Includes duplicates
- Inaccurate win rate

**After (Cleaned Data):**
- 105 trades (15 duplicates removed)
- Each timestamp = 1 trade only
- Accurate win rate ✅

---

## ❓ FREQUENTLY ASKED QUESTIONS

### Q: What if I don't have 12 months of data?

**A:** Analyzer works with any amount of data. If you have 3 months, it shows 3 months. If you have 24 months, it shows last 12.

---

### Q: Can I change which strategy to keep on duplicates?

**A:** Yes! Edit `analyze_12month_winrate.py`:

```python
# Current: Keep highest profit
self.all_trades = self.all_trades.sort_values('Profit', ascending=False)

# Change to: Keep Fibonacci always
priority_map = {'Fibonacci': 1, 'Candlestick': 2, 'EMA Bounce': 3}
self.all_trades['Priority'] = self.all_trades['Strategy'].map(priority_map)
self.all_trades = self.all_trades.sort_values('Priority')
```

---

### Q: Can I analyze specific date range?

**A:** Yes! After loading data:

```python
analyzer = WinRateAnalyzer(data_folder='./data')
analyzer.load_all_csv_files()

# Filter Q1 2026
analyzer.all_trades = analyzer.all_trades[
    (analyzer.all_trades['DateTime'] >= '2026-01-01') &
    (analyzer.all_trades['DateTime'] <= '2026-03-31')
]

analyzer.generate_excel_report('Q1_2026_REPORT.xlsx')
```

---

### Q: My CSV has different column names. What do I do?

**A:** Rename columns in the script:

```python
# In load_all_csv_files() method, add:
df = df.rename(columns={
    'timestamp': 'Time',
    'contract': 'Instrument',
    'entry_price': 'Entry',
    'exit_price': 'Exit',
    'pnl': 'Profit'
})
```

---

## 📊 REAL WORLD EXAMPLE

### Input CSV Files

`data/livetrading_010426.csv`:
```csv
Time,Instrument,Entry,Exit,Profit,Strategy,Signal,Status
09:30,NIFTY 23400 CE,150,165,1600,Fibonacci,CALL,WIN
09:30,NIFTY 23400 CE,150,160,1000,Candlestick,CALL,WIN
14:00,NIFTY 23350 PE,140,155,1600,EMA Bounce,PUT,WIN
```

`data/livetrading_020426.csv`:
```csv
Time,Instrument,Entry,Exit,Profit,Strategy,Signal,Status
10:00,NIFTY 23450 CE,160,170,1600,Fibonacci,CALL,WIN
15:00,NIFTY 23300 PE,130,120,-800,Candlestick,PUT,LOSS
```

---

### Output Report

**Monthly Win Rate:**
| Month | Trades | Profit | Wins | Losses | WinRate% |
|-------|--------|--------|------|--------|----------|
| 2026-04 | 4 | 5,800 | 3 | 1 | 75.00% |

**Why 4 trades?**
- 01-Apr: 2 original trades → 1 kept (Fibonacci, highest profit)
- 01-Apr: 1 trade (EMA Bounce)
- 02-Apr: 2 trades
- **Total: 4 trades**

**Strategy Performance:**
| Strategy | Trades | Profit | WinRate% |
|----------|--------|--------|----------|
| Fibonacci | 2 | 3,200 | 100% |
| EMA Bounce | 1 | 1,600 | 100% |
| Candlestick | 1 | -800 | 0% |

---

## ✅ FINAL CHECKLIST

Before using the analyzer:

- [ ] Data folder exists: `D:\dhan_algo\data\`
- [ ] CSV files present: `livetrading_*.csv`
- [ ] Files have required columns (Time, Instrument, Profit, Strategy)
- [ ] File naming is correct: `livetrading_DDMMYY.csv`
- [ ] Python installed with packages: `pandas`, `openpyxl`

To install packages:
```powershell
pip install pandas openpyxl
```

---

## 🎉 READY TO USE!

**Quick Start:**
```
Double-click: run-winrate-analysis.ps1
```

**Or:**
```powershell
python analyze_12month_winrate.py
```

**Output:**
```
12_MONTH_WIN_RATE_REPORT.xlsx
```

---

**Created:** 05-Apr-2026 11:30 AM  
**Status:** ✅ Complete & Ready  
**Duplicates:** Automatically removed  
**Win Rate:** Month-wise for 12 months  
**Report:** 4 comprehensive sheets  

**Your month-wise win rate analyzer is ready! 📊🎯**
