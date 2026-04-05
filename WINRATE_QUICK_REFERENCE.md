# 📊 WIN RATE ANALYZER - QUICK REFERENCE CARD

---

## 🚀 QUICK START

**Double-click this file:**
```
run-winrate-analysis.ps1
```

**Or run manually:**
```powershell
python analyze_12month_winrate.py
```

---

## 📁 DATA STRUCTURE

### Your CSV Files Should Be In:
```
D:\dhan_algo\data\
```

### File Naming Format:
```
livetrading_DDMMYY.csv
```

**Examples:**
- `livetrading_050426.csv` = 05-Apr-2026
- `livetrading_010326.csv` = 01-Mar-2026

---

## 📊 REQUIRED COLUMNS

| Column | Example | Required |
|--------|---------|----------|
| Time | `09:30:00` | ✅ Yes |
| Instrument | `NIFTY 23400 CE` | ✅ Yes |
| Entry | `150.50` | ✅ Yes |
| Exit | `165.75` | ✅ Yes |
| Profit | `1600` | ✅ Yes |
| Strategy | `Fibonacci` | ✅ Yes |
| Signal | `CALL` | ⚠️ Recommended |
| Status | `WIN` | ⚠️ Recommended |

---

## 🧹 DUPLICATE HANDLING

### Problem:
```csv
Time,Instrument,Entry,Exit,Profit,Strategy
09:30,NIFTY 23400 CE,150,165,1600,Fibonacci
09:30,NIFTY 23400 CE,150,162,1200,Candlestick  ← Duplicate!
```

### Solution:
```csv
Time,Instrument,Entry,Exit,Profit,Strategy
09:30,NIFTY 23400 CE,150,165,1600,Fibonacci  ← Kept (highest profit)
```

**Rule:** Same time + Same instrument = Keep highest profit only

---

## 📄 OUTPUT REPORT

**File:** `12_MONTH_WIN_RATE_REPORT.xlsx`

**4 Sheets:**
1. **Monthly Win Rate** - Month-wise stats (last 12 months)
2. **Strategy Performance** - Best/worst strategies
3. **All Trades** - Cleaned data (no duplicates)
4. **Summary** - Overall statistics

---

## 🎯 USAGE EXAMPLES

### Analyze Real Data
```powershell
# 1. Put CSV files in data/ folder
# 2. Run analyzer
python analyze_12month_winrate.py

# 3. Open report
start 12_MONTH_WIN_RATE_REPORT.xlsx
```

### Test with Sample Data
```powershell
# 1. Generate sample data
python generate_sample_data.py

# 2. Run analyzer
python analyze_12month_winrate.py

# 3. Check output
start 12_MONTH_WIN_RATE_REPORT.xlsx
```

---

## 📈 WHAT YOU GET

### Monthly Win Rate (Sheet 1)
| Month | Trades | Profit | Wins | Losses | Win% |
|-------|--------|--------|------|--------|------|
| 2026-04 | 18 | 28800 | 12 | 6 | 66.67% |
| 2026-03 | 22 | 35200 | 15 | 7 | 68.18% |

### Strategy Performance (Sheet 2)
| Strategy | Trades | Profit | Win% |
|----------|--------|--------|------|
| Fibonacci | 45 | 72000 | 71.11% |
| Candlestick | 38 | 60800 | 68.42% |

---

## ❓ TROUBLESHOOTING

### No CSV files found
```powershell
# Check data folder
ls data\livetrading_*.csv

# If empty, add your CSV files
# Or generate sample data:
python generate_sample_data.py
```

### Column not found error
```
# Check your CSV columns
import pandas as pd
df = pd.read_csv('data/livetrading_050426.csv')
print(df.columns)

# Make sure columns match required names
```

### Date parsing error
```
# Check date format in CSV
# Expected: DD-MM-YYYY or YYYY-MM-DD
```

---

## 📚 DOCUMENTATION

**Full Guide:** `WIN_RATE_ANALYZER_GUIDE.md`  
**Analyzer:** `analyze_12month_winrate.py`  
**Sample Data:** `generate_sample_data.py`  
**Quick Start:** `run-winrate-analysis.ps1`

---

## ✅ CHECKLIST

Before running:
- [ ] Data folder exists (`data/`)
- [ ] CSV files present (`livetrading_*.csv`)
- [ ] Files have required columns
- [ ] File naming is correct (`DDMMYY`)
- [ ] Python packages installed (`pandas`, `openpyxl`)

---

## 🎉 READY?

**Just double-click:**
```
run-winrate-analysis.ps1
```

**Or run:**
```powershell
python analyze_12month_winrate.py
```

---

**Status:** ✅ Ready to use  
**Output:** `12_MONTH_WIN_RATE_REPORT.xlsx`  
**Duplicates:** Automatically removed  
**Win Rate:** Month-wise for last 12 months  

**Happy Analyzing! 📊**
