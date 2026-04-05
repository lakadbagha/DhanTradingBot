# 📊 12-MONTH WIN RATE ANALYZER - USER GUIDE

**Created:** 05-Apr-2026  
**Purpose:** Generate month-wise win rate from real trading data  
**Removes:** Duplicate entries when multiple strategies fire at same time

---

## 🎯 WHAT IT DOES

### Key Features

1. **Loads All Trading Data**
   - Reads all `livetrading_*.csv` files from `data/` folder
   - Combines data from last 12 months

2. **Removes Duplicates**
   - When 2+ strategies trigger at same time for same instrument
   - Keeps only the BEST PERFORMING strategy
   - Based on highest profit

3. **Generates Excel Report**
   - Monthly win rate (last 12 months)
   - Strategy-wise performance
   - All trades (cleaned, no duplicates)
   - Summary statistics

---

## 📁 DATA STRUCTURE

### Required CSV Columns

Your `livetrading_DDMMYY.csv` files should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| **Time** | Trade timestamp | `09:30:00` |
| **Instrument** | Option contract | `NIFTY 23400 CE` |
| **Entry** | Entry price | `150.50` |
| **Exit** | Exit price | `165.75` |
| **Profit** | P&L | `1600` |
| **Strategy** | Strategy name | `Fibonacci`, `Candlestick`, `EMA Bounce` |
| **Signal** | Signal type | `CALL`, `PUT` |
| **Status** | Trade status | `WIN`, `LOSS`, `ACTIVE` |
| **OrderID** | Order ID (optional) | `12345678` |

### File Naming Convention

```
data/livetrading_DDMMYY.csv
```

**Examples:**
- `livetrading_050426.csv` = 05-Apr-2026
- `livetrading_010326.csv` = 01-Mar-2026
- `livetrading_281224.csv` = 28-Dec-2024

---

## 🚀 HOW TO USE

### Step 1: Ensure Data Files Exist

```powershell
# Check data folder
cd D:\dhan_algo
ls data\livetrading_*.csv
```

**Expected:**
```
livetrading_050426.csv
livetrading_040426.csv
livetrading_030426.csv
...
```

---

### Step 2: Run the Analyzer

**Option A: Using Python directly**
```powershell
python analyze_12month_winrate.py
```

**Option B: Custom folder**
```python
# Edit analyze_12month_winrate.py
analyzer = WinRateAnalyzer(data_folder='./my_custom_folder')
analyzer.run_analysis()
```

---

### Step 3: Check Output

**Generated file:**
```
12_MONTH_WIN_RATE_REPORT.xlsx
```

**Contains 4 sheets:**

1. **Monthly Win Rate**
   - Month-wise statistics
   - Total trades, wins, losses
   - Win rate %
   - Total P&L

2. **Strategy Performance**
   - Strategy-wise breakdown
   - Best/worst performing strategies
   - Win rate by strategy

3. **All Trades**
   - Complete trade log (cleaned)
   - No duplicate entries
   - All columns preserved

4. **Summary**
   - Overall statistics
   - Best/worst months
   - Best/worst strategies
   - Total P&L

---

## 🧹 DUPLICATE REMOVAL LOGIC

### Problem

When multiple strategies trigger at **same time** for **same instrument**:

```csv
Time,Instrument,Entry,Exit,Profit,Strategy
09:30:00,NIFTY 23400 CE,150,165,1600,Fibonacci
09:30:00,NIFTY 23400 CE,150,162,1200,Candlestick
09:30:00,NIFTY 23400 CE,150,168,1800,EMA Bounce
```

This creates **triple counting** of the same trade!

---

### Solution

The analyzer **keeps only ONE trade**:

```csv
Time,Instrument,Entry,Exit,Profit,Strategy
09:30:00,NIFTY 23400 CE,150,168,1800,EMA Bounce
```

**Why EMA Bounce?**
- Highest profit (Rs. 1800)
- Algorithm keeps best performing strategy

---

### How It Works

1. **Create Unique Key:**
   ```python
   UniqueKey = DateTime + Instrument
   # Example: "2026-04-05 09:30:00_NIFTY 23400 CE"
   ```

2. **Find Duplicates:**
   ```python
   duplicates = df[df.duplicated(subset=['UniqueKey'], keep=False)]
   ```

3. **Keep Best:**
   ```python
   df = df.sort_values('Profit', ascending=False)
   df = df.drop_duplicates(subset=['UniqueKey'], keep='first')
   ```

4. **Result:**
   - Only highest profit strategy kept
   - No double/triple counting
   - Accurate win rate calculation

---

## 📊 SAMPLE OUTPUT

### Console Output

```
================================================================================
📂 LOADING TRADING DATA
================================================================================
✅ Found 60 CSV files
   ✓ livetrading_050426.csv: 2 trades
   ✓ livetrading_040426.csv: 3 trades
   ...

✅ Total trades loaded: 120

================================================================================
🧹 REMOVING DUPLICATE ENTRIES
================================================================================
📊 Finding duplicates...
⚠️  Found 15 duplicate entries
   Unique timestamps with duplicates: 5
✅ Removed 15 duplicate entries
✅ Remaining trades: 105

================================================================================
📊 CALCULATING MONTHLY WIN RATES
================================================================================

📈 Monthly Win Rate Summary:
Month     TotalTrades  TotalProfit  AvgProfit  Wins  Losses  WinRate%
2026-04            18     28800.00    1600.00    12       6     66.67
2026-03            22     35200.00    1600.00    15       7     68.18
2026-02            20     32000.00    1600.00    14       6     70.00
...

================================================================================
✅ ANALYSIS COMPLETE!
================================================================================

📄 Report: 12_MONTH_WIN_RATE_REPORT.xlsx
```

---

## 📋 COLUMN MAPPING GUIDE

### If Your CSV Has Different Column Names

Edit `analyze_12month_winrate.py`:

```python
# Rename columns to match expected format
df = df.rename(columns={
    'timestamp': 'Time',
    'contract': 'Instrument',
    'entry_price': 'Entry',
    'exit_price': 'Exit',
    'pnl': 'Profit',
    'strategy_name': 'Strategy'
})
```

---

## 🔧 CUSTOMIZATION OPTIONS

### 1. Change Data Folder

```python
analyzer = WinRateAnalyzer(data_folder='./custom_folder')
```

---

### 2. Change Output Filename

```python
analyzer.generate_excel_report(output_file='MY_CUSTOM_REPORT.xlsx')
```

---

### 3. Analyze Specific Date Range

```python
# Load data
analyzer.load_all_csv_files()

# Filter by date
analyzer.all_trades = analyzer.all_trades[
    (analyzer.all_trades['DateTime'] >= '2026-01-01') &
    (analyzer.all_trades['DateTime'] <= '2026-03-31')
]

# Generate report
analyzer.generate_excel_report(output_file='Q1_2026_REPORT.xlsx')
```

---

### 4. Keep Specific Strategy on Duplicates

Default behavior: **Keep highest profit**

To change:

```python
# In clean_duplicate_entries() method, replace:
self.all_trades = self.all_trades.sort_values('Profit', ascending=False)

# With (example: prioritize Fibonacci):
def priority_score(row):
    if row['Strategy'] == 'Fibonacci':
        return 3
    elif row['Strategy'] == 'Candlestick':
        return 2
    else:
        return 1

self.all_trades['Priority'] = self.all_trades.apply(priority_score, axis=1)
self.all_trades = self.all_trades.sort_values('Priority', ascending=False)
```

---

## 🎯 EXPECTED COLUMNS IN CSV

### Minimum Required

```csv
Time,Instrument,Profit
09:30:00,NIFTY 23400 CE,1600
```

### Recommended

```csv
Time,Instrument,Entry,Exit,Profit,Strategy,Signal,Status
09:30:00,NIFTY 23400 CE,150,165,1600,Fibonacci,CALL,WIN
```

### Full Format

```csv
Time,Instrument,Entry,Exit,Profit,Strategy,Signal,Status,OrderID
09:30:00,NIFTY 23400 CE,150,165,1600,Fibonacci,CALL,WIN,12345678
```

---

## ❓ TROUBLESHOOTING

### Issue 1: No CSV Files Found

```
❌ No CSV files found in: ./data
   Expected pattern: livetrading_DDMMYY.csv
```

**Fix:**
```powershell
# Check if data folder exists
ls data

# Check file naming
ls data\*.csv

# Ensure files match pattern: livetrading_DDMMYY.csv
```

---

### Issue 2: Column Not Found

```
KeyError: 'Time'
```

**Fix:**
```python
# Check your CSV columns
import pandas as pd
df = pd.read_csv('data/livetrading_050426.csv')
print(df.columns)

# Rename columns in analyzer
df = df.rename(columns={'YourTimeColumn': 'Time'})
```

---

### Issue 3: Date Parsing Error

```
ValueError: time data '...' does not match format '%d-%m-%Y %H:%M:%S'
```

**Fix:**
```python
# Check your date/time format
# Update format in analyzer:
self.all_trades['DateTime'] = pd.to_datetime(
    self.all_trades['Date'] + ' ' + self.all_trades['Time'],
    format='%Y-%m-%d %H:%M:%S',  # Change this
    errors='coerce'
)
```

---

## 📈 EXAMPLE USAGE SCENARIOS

### Scenario 1: Monthly Performance Review

```powershell
# Run analyzer
python analyze_12month_winrate.py

# Open Excel report
start 12_MONTH_WIN_RATE_REPORT.xlsx

# Check 'Monthly Win Rate' sheet
# Identify best/worst months
# Analyze trends
```

---

### Scenario 2: Strategy Optimization

```powershell
# Generate report
python analyze_12month_winrate.py

# Open 'Strategy Performance' sheet
# Find best performing strategy
# Disable underperforming strategies
```

---

### Scenario 3: Quarterly Review

```python
# Edit analyze_12month_winrate.py
analyzer = WinRateAnalyzer(data_folder='./data')
analyzer.load_all_csv_files()

# Filter Q1 2026
analyzer.all_trades = analyzer.all_trades[
    analyzer.all_trades['DateTime'].dt.quarter == 1
]

analyzer.generate_excel_report('Q1_2026_REPORT.xlsx')
```

---

## ✅ CHECKLIST

Before running analyzer:

- [ ] Data folder exists: `data/`
- [ ] CSV files present: `livetrading_*.csv`
- [ ] CSV has required columns: `Time, Instrument, Profit`
- [ ] File naming correct: `livetrading_DDMMYY.csv`
- [ ] Python packages installed: `pandas, openpyxl`

---

## 🚀 QUICK START

```powershell
# 1. Navigate to project
cd D:\dhan_algo

# 2. Check data files
ls data\livetrading_*.csv

# 3. Run analyzer
python analyze_12month_winrate.py

# 4. Open report
start 12_MONTH_WIN_RATE_REPORT.xlsx
```

---

## 📊 EXCEL REPORT SHEETS EXPLAINED

### Sheet 1: Monthly Win Rate

| Month | TotalTrades | TotalProfit | AvgProfit | Wins | Losses | WinRate% |
|-------|-------------|-------------|-----------|------|--------|----------|
| 2026-04 | 18 | 28800 | 1600 | 12 | 6 | 66.67 |
| 2026-03 | 22 | 35200 | 1600 | 15 | 7 | 68.18 |

**Use for:**
- Monthly performance tracking
- Identifying seasonal trends
- Setting monthly targets

---

### Sheet 2: Strategy Performance

| Strategy | TotalTrades | TotalProfit | WinRate% |
|----------|-------------|-------------|----------|
| Fibonacci | 45 | 72000 | 71.11 |
| Candlestick | 38 | 60800 | 68.42 |
| EMA Bounce | 22 | 35200 | 63.64 |

**Use for:**
- Strategy comparison
- Resource allocation
- Strategy optimization

---

### Sheet 3: All Trades (Cleaned)

| Date | Time | Instrument | Entry | Exit | Profit | Strategy |
|------|------|------------|-------|------|--------|----------|
| 05-04-2026 | 09:30 | NIFTY 23400 CE | 150 | 165 | 1600 | Fibonacci |

**Use for:**
- Trade-by-trade analysis
- Pattern identification
- Detailed review

---

### Sheet 4: Summary

| Metric | Value |
|--------|-------|
| Total Trades | 105 |
| Total P&L | Rs. 168000 |
| Win Rate % | 68.57% |
| Best Month | 2026-03 |
| Best Strategy | Fibonacci |

**Use for:**
- Quick overview
- Performance snapshot
- Reporting

---

**Created:** 05-Apr-2026  
**Status:** Ready to use  
**Data Required:** CSV files in `data/` folder  

**Happy Analyzing! 📊**
