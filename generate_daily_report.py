"""
Generate Better Daily Report from Backtest Results
"""

import pandas as pd

# Load the trades
df = pd.DataFrame(pd.read_csv('fibonacci_20days_all_trades.csv'))

# Group by entry_date to get daily summary
df['date'] = pd.to_datetime(df['entry_date']).dt.date

daily_summary = df.groupby('date').agg({
    'trade_number': 'count',
    'pnl': ['sum', 'mean'],
    'option_type': lambda x: f"{sum(x=='CALL')}C/{sum(x=='PUT')}P"
}).reset_index()

daily_summary.columns = ['Date', 'Trades', 'Total_PnL', 'Avg_PnL', 'CALL/PUT']

# Calculate running capital
initial_capital = 100000
daily_summary['Capital'] = initial_capital + daily_summary['Total_PnL'].cumsum()

# Add day number
daily_summary.insert(0, 'Day', range(1, len(daily_summary)+1))

# Format for display
print("=" * 90)
print("📅 DETAILED DAY-BY-DAY REPORT - FIBONACCI STRATEGY (20 TRADING DAYS)")
print("=" * 90)
print(f"\n{'Day':<4} {'Date':<12} {'Trades':>7} {'CALL/PUT':>10} {'Daily P&L':>12} {'Avg P&L':>10} {'Capital':>15}")
print("-" * 90)

for _, row in daily_summary.iterrows():
    pnl_str = f"₹{row['Total_PnL']:,.0f}" if row['Total_PnL'] >= 0 else f"-₹{abs(row['Total_PnL']):,.0f}"
    avg_str = f"₹{row['Avg_PnL']:,.0f}"
    status = "✅" if row['Total_PnL'] >= 0 else "❌"
    
    print(f"{row['Day']:<4} {row['Date']} {int(row['Trades']):>7} {row['CALL/PUT']:>10} {pnl_str:>12} {avg_str:>10} {status} ₹{row['Capital']:>13,.0f}")

print("=" * 90)

# Summary statistics
total_pnl = daily_summary['Total_PnL'].sum()
positive_days = (daily_summary['Total_PnL'] > 0).sum()
negative_days = (daily_summary['Total_PnL'] < 0).sum()
breakeven_days = (daily_summary['Total_PnL'] == 0).sum()

print(f"\n📊 SUMMARY STATISTICS:")
print(f"   Total Trading Days: {len(daily_summary)}")
print(f"   Total Trades: {daily_summary['Trades'].sum()}")
print(f"   Positive Days: {positive_days} ({positive_days/len(daily_summary)*100:.1f}%)")
print(f"   Negative Days: {negative_days} ({negative_days/len(daily_summary)*100:.1f}%)")
print(f"   Breakeven Days: {breakeven_days}")
print(f"\n   Initial Capital: ₹{initial_capital:,.0f}")
print(f"   Final Capital: ₹{daily_summary['Capital'].iloc[-1]:,.0f}")
print(f"   Total P&L: ₹{total_pnl:,.0f} ({total_pnl/initial_capital*100:.2f}%)")
print(f"   Daily Avg P&L: ₹{total_pnl/len(daily_summary):,.0f}")

# Save enhanced report
daily_summary.to_csv('fibonacci_20days_DAILY_SUMMARY.csv', index=False)
print(f"\n💾 Enhanced daily summary saved to: fibonacci_20days_DAILY_SUMMARY.csv")

# Create trade-level details
print("\n" + "=" * 90)
print("🔍 SAMPLE TRADES (First 5 Days)")
print("=" * 90)

sample_trades = df.head(10)  # First 10 trades = 5 days
for idx, trade in sample_trades.iterrows():
    day = (idx // 2) + 1
    trade_num = (idx % 2) + 1
    
    print(f"\nDay {day}, Trade {trade_num}: {trade['entry_time']} - {trade['exit_time']}")
    print(f"  {trade['option_type']} Option | Strike: {trade['strike']}")
    print(f"  Entry: ₹{trade['entry_premium']:.2f} @ NIFTY {trade['entry_spot']:.0f}")
    print(f"  Exit: ₹{trade['exit_premium']:.2f} @ NIFTY {trade['exit_spot']:.0f}")
    print(f"  P&L: ₹{trade['pnl']:,.0f} | {trade['exit_reason']}")
