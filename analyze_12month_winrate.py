"""
12-MONTH WIN RATE ANALYZER
===========================
Generate month-wise win rate from real trading data (livetrading CSV files)

Features:
1. Month-wise win rate for last 12 months
2. Removes duplicate entries (same time + same instrument + different strategies)
3. Keeps only the best strategy per timestamp
4. Generates Excel report with multiple sheets

CSV Columns Used:
- Time: Timestamp of trade
- Instrument: Option contract name
- Entry: Entry price
- Exit: Exit price
- Profit: P&L
- Strategy: Strategy name (Fibonacci, Candlestick, EMA Bounce, etc.)
- Signal: Signal type (CALL/PUT)
- Status: Trade status (WIN/LOSS/ACTIVE)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob
from pathlib import Path


class WinRateAnalyzer:
    """Analyze real trading data and generate month-wise win rate"""
    
    def __init__(self, data_folder='./data'):
        """
        Initialize analyzer
        
        Args:
            data_folder: Folder containing livetrading_DDMMYY.csv files
        """
        self.data_folder = data_folder
        self.all_trades = pd.DataFrame()
        
    def load_all_csv_files(self):
        """Load all livetrading CSV files from data folder"""
        print("\n" + "="*80)
        print("📂 LOADING TRADING DATA")
        print("="*80)
        
        # Find all CSV files matching pattern: livetrading_*.csv
        csv_pattern = os.path.join(self.data_folder, 'livetrading_*.csv')
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            print(f"❌ No CSV files found in: {self.data_folder}")
            print(f"   Expected pattern: livetrading_DDMMYY.csv")
            return False
        
        print(f"✅ Found {len(csv_files)} CSV files")
        
        all_data = []
        
        for csv_file in sorted(csv_files):
            try:
                df = pd.read_csv(csv_file)
                
                # Extract date from filename: livetrading_050426.csv -> 05-04-2026
                filename = os.path.basename(csv_file)
                date_part = filename.replace('livetrading_', '').replace('.csv', '')
                
                # Parse DDMMYY format
                day = date_part[:2]
                month = date_part[2:4]
                year = '20' + date_part[4:6]
                file_date = f"{day}-{month}-{year}"
                
                # Add date column if not exists
                if 'Date' not in df.columns:
                    df['Date'] = file_date
                
                # Add file source
                df['SourceFile'] = filename
                
                all_data.append(df)
                print(f"   ✓ {filename}: {len(df)} trades")
                
            except Exception as e:
                print(f"   ✗ Error reading {csv_file}: {e}")
        
        if all_data:
            self.all_trades = pd.concat(all_data, ignore_index=True)
            print(f"\n✅ Total trades loaded: {len(self.all_trades)}")
            return True
        else:
            print("❌ No data loaded")
            return False
    
    def clean_duplicate_entries(self):
        """
        Remove duplicate entries when 2 strategies apply at same time
        Keep only one trade per timestamp per instrument
        Priority: Highest profit strategy
        """
        print("\n" + "="*80)
        print("🧹 REMOVING DUPLICATE ENTRIES")
        print("="*80)
        
        original_count = len(self.all_trades)
        
        # Combine Date and Time for grouping
        if 'Time' in self.all_trades.columns:
            self.all_trades['DateTime'] = pd.to_datetime(
                self.all_trades['Date'] + ' ' + self.all_trades['Time'],
                format='%d-%m-%Y %H:%M:%S',
                errors='coerce'
            )
        else:
            print("⚠️  'Time' column not found, using Date only")
            self.all_trades['DateTime'] = pd.to_datetime(
                self.all_trades['Date'],
                format='%d-%m-%Y',
                errors='coerce'
            )
        
        # Group by DateTime and Instrument, keep best performing strategy
        print("📊 Finding duplicates...")
        
        # Create unique key: DateTime + Instrument
        self.all_trades['UniqueKey'] = (
            self.all_trades['DateTime'].astype(str) + '_' + 
            self.all_trades['Instrument'].astype(str)
        )
        
        # Find duplicates
        duplicates = self.all_trades[self.all_trades.duplicated(subset=['UniqueKey'], keep=False)]
        
        if len(duplicates) > 0:
            print(f"⚠️  Found {len(duplicates)} duplicate entries")
            print(f"   Unique timestamps with duplicates: {duplicates['UniqueKey'].nunique()}")
            
            # Keep the trade with highest profit for each unique key
            self.all_trades = self.all_trades.sort_values('Profit', ascending=False)
            self.all_trades = self.all_trades.drop_duplicates(subset=['UniqueKey'], keep='first')
            
            removed = original_count - len(self.all_trades)
            print(f"✅ Removed {removed} duplicate entries")
            print(f"✅ Remaining trades: {len(self.all_trades)}")
        else:
            print("✅ No duplicate entries found")
        
        return self.all_trades
    
    def calculate_monthly_win_rate(self):
        """Calculate month-wise win rate for last 12 months"""
        print("\n" + "="*80)
        print("📊 CALCULATING MONTHLY WIN RATES")
        print("="*80)
        
        # Ensure DateTime column exists
        if 'DateTime' not in self.all_trades.columns:
            self.all_trades['DateTime'] = pd.to_datetime(
                self.all_trades['Date'],
                format='%d-%m-%Y',
                errors='coerce'
            )
        
        # Add Month-Year column
        self.all_trades['MonthYear'] = self.all_trades['DateTime'].dt.to_period('M')
        
        # Determine Win/Loss
        self.all_trades['Result'] = self.all_trades['Profit'].apply(
            lambda x: 'WIN' if x > 0 else 'LOSS' if x < 0 else 'BREAKEVEN'
        )
        
        # Group by Month
        monthly_stats = self.all_trades.groupby('MonthYear').agg({
            'Profit': ['count', 'sum', 'mean', 'max', 'min'],
            'Result': lambda x: (x == 'WIN').sum(),  # Count wins
        }).reset_index()
        
        # Flatten column names
        monthly_stats.columns = ['Month', 'TotalTrades', 'TotalProfit', 'AvgProfit', 
                                  'MaxProfit', 'MinProfit', 'Wins']
        
        # Calculate win rate
        monthly_stats['Losses'] = monthly_stats['TotalTrades'] - monthly_stats['Wins']
        monthly_stats['WinRate%'] = (monthly_stats['Wins'] / monthly_stats['TotalTrades'] * 100).round(2)
        
        # Format Month as string
        monthly_stats['Month'] = monthly_stats['Month'].astype(str)
        
        # Sort by month (latest first)
        monthly_stats = monthly_stats.sort_values('Month', ascending=False)
        
        # Limit to last 12 months
        monthly_stats = monthly_stats.head(12)
        
        print("\n📈 Monthly Win Rate Summary:")
        print(monthly_stats.to_string(index=False))
        
        return monthly_stats
    
    def calculate_strategy_performance(self):
        """Calculate performance by strategy"""
        print("\n" + "="*80)
        print("📊 STRATEGY-WISE PERFORMANCE")
        print("="*80)
        
        if 'Strategy' not in self.all_trades.columns:
            print("⚠️  'Strategy' column not found")
            return pd.DataFrame()
        
        # Determine Win/Loss if not already done
        if 'Result' not in self.all_trades.columns:
            self.all_trades['Result'] = self.all_trades['Profit'].apply(
                lambda x: 'WIN' if x > 0 else 'LOSS' if x < 0 else 'BREAKEVEN'
            )
        
        strategy_stats = self.all_trades.groupby('Strategy').agg({
            'Profit': ['count', 'sum', 'mean', 'max', 'min'],
            'Result': lambda x: (x == 'WIN').sum(),
        }).reset_index()
        
        strategy_stats.columns = ['Strategy', 'TotalTrades', 'TotalProfit', 'AvgProfit',
                                   'MaxProfit', 'MinProfit', 'Wins']
        
        strategy_stats['Losses'] = strategy_stats['TotalTrades'] - strategy_stats['Wins']
        strategy_stats['WinRate%'] = (strategy_stats['Wins'] / strategy_stats['TotalTrades'] * 100).round(2)
        
        # Sort by total profit
        strategy_stats = strategy_stats.sort_values('TotalProfit', ascending=False)
        
        print("\n📊 Strategy Performance:")
        print(strategy_stats.to_string(index=False))
        
        return strategy_stats
    
    def generate_excel_report(self, output_file='12_MONTH_WIN_RATE_REPORT.xlsx'):
        """Generate comprehensive Excel report"""
        print("\n" + "="*80)
        print("📄 GENERATING EXCEL REPORT")
        print("="*80)
        
        # Calculate all stats
        monthly_stats = self.calculate_monthly_win_rate()
        strategy_stats = self.calculate_strategy_performance()
        
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Sheet 1: Monthly Win Rate
            monthly_stats.to_excel(writer, sheet_name='Monthly Win Rate', index=False)
            
            # Sheet 2: Strategy Performance
            if not strategy_stats.empty:
                strategy_stats.to_excel(writer, sheet_name='Strategy Performance', index=False)
            
            # Sheet 3: All Trades (cleaned)
            trades_export = self.all_trades[[
                'Date', 'Time', 'Instrument', 'Entry', 'Exit', 'Profit',
                'Strategy', 'Signal', 'Status', 'Result'
            ]].copy() if all(col in self.all_trades.columns for col in 
                ['Date', 'Time', 'Instrument', 'Entry', 'Exit', 'Profit', 
                 'Strategy', 'Signal', 'Status']) else self.all_trades
            
            trades_export.to_excel(writer, sheet_name='All Trades', index=False)
            
            # Sheet 4: Summary Statistics
            summary_data = {
                'Metric': [
                    'Total Trades (After Dedup)',
                    'Total Profit/Loss',
                    'Average Profit per Trade',
                    'Win Rate %',
                    'Best Month',
                    'Worst Month',
                    'Best Strategy',
                    'Worst Strategy'
                ],
                'Value': [
                    len(self.all_trades),
                    f"Rs. {self.all_trades['Profit'].sum():.2f}",
                    f"Rs. {self.all_trades['Profit'].mean():.2f}",
                    f"{(self.all_trades['Result'] == 'WIN').sum() / len(self.all_trades) * 100:.2f}%",
                    monthly_stats.iloc[0]['Month'] if not monthly_stats.empty else 'N/A',
                    monthly_stats.iloc[-1]['Month'] if not monthly_stats.empty else 'N/A',
                    strategy_stats.iloc[0]['Strategy'] if not strategy_stats.empty else 'N/A',
                    strategy_stats.iloc[-1]['Strategy'] if not strategy_stats.empty else 'N/A'
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"\n✅ Excel report saved: {output_file}")
        print(f"   📊 Sheets created:")
        print(f"      1. Monthly Win Rate")
        print(f"      2. Strategy Performance")
        print(f"      3. All Trades (Cleaned)")
        print(f"      4. Summary")
        
        return output_file
    
    def run_analysis(self):
        """Run complete analysis"""
        print("\n" + "="*80)
        print("🚀 12-MONTH WIN RATE ANALYSIS")
        print("="*80)
        print(f"📅 Date: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}")
        
        # Step 1: Load data
        if not self.load_all_csv_files():
            print("\n❌ Analysis failed: No data loaded")
            return False
        
        # Step 2: Clean duplicates
        self.clean_duplicate_entries()
        
        # Step 3: Generate report
        report_file = self.generate_excel_report()
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE!")
        print("="*80)
        print(f"\n📄 Report: {report_file}")
        print("\n💡 Columns Used:")
        print("   • Time        - Trade timestamp")
        print("   • Instrument  - Option contract")
        print("   • Entry       - Entry price")
        print("   • Exit        - Exit price")
        print("   • Profit      - P&L")
        print("   • Strategy    - Strategy name")
        print("   • Signal      - CALL/PUT signal")
        print("   • Status      - Trade status")
        
        return True


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == '__main__':
    # Initialize analyzer
    analyzer = WinRateAnalyzer(data_folder='./data')
    
    # Run analysis
    analyzer.run_analysis()
    
    print("\n" + "="*80)
    print("🎯 NEXT STEPS:")
    print("="*80)
    print("1. Open: 12_MONTH_WIN_RATE_REPORT.xlsx")
    print("2. Check 'Monthly Win Rate' sheet for month-wise performance")
    print("3. Check 'Strategy Performance' sheet for best strategies")
    print("4. Review 'All Trades' sheet for cleaned data (no duplicates)")
    print("5. View 'Summary' sheet for overall statistics")
    print("\n✅ Analysis complete!")
