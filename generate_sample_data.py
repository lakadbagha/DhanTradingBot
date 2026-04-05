"""
SAMPLE DATA GENERATOR
=====================
Generate sample trading CSV files for testing the win rate analyzer

This creates realistic trading data with:
- Multiple strategies (Fibonacci, Candlestick, EMA Bounce)
- Some duplicate entries (same time, same instrument, different strategies)
- Win/Loss distribution
- Last 12 months data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random


class SampleDataGenerator:
    """Generate sample trading data for testing"""
    
    def __init__(self, output_folder='./data'):
        """Initialize generator"""
        self.output_folder = output_folder
        self.strategies = ['Fibonacci', 'Candlestick', 'EMA Bounce', 'Support/Resistance']
        self.signals = ['CALL', 'PUT']
        
        # Create output folder if not exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"✅ Created folder: {output_folder}")
    
    def get_lot_size(self, date):
        """Get correct lot size based on date"""
        # Before 2026: 75 quantity per lot
        # From 2026: 65 quantity per lot
        if date.year < 2026:
            return 75
        else:
            return 65

    def generate_trade(self, date, time, create_duplicate=False):
        """Generate a single trade with SL/Target/Trailing logic"""
        # Get correct lot size
        lot_size = self.get_lot_size(date)

        # Random strike prices
        strikes = [22900, 22950, 23000, 23050, 23100, 23150, 23200, 23250, 23300, 23350, 23400, 23450, 23500]
        strike = random.choice(strikes)

        signal = random.choice(self.signals)
        instrument = f"NIFTY {strike} {'CE' if signal == 'CALL' else 'PE'}"

        # Entry price (realistic range for NIFTY options)
        entry = round(random.uniform(100, 200), 2)

        # SL and Target parameters (from strategy_config.py)
        sl_points = 800 / lot_size  # Rs. 800 loss
        target_points = 1600 / lot_size  # Rs. 1600 profit

        # Determine trade outcome (70% win rate)
        is_win = random.random() < 0.70

        if is_win:
            # Winning trade - hit target or trailing stop
            outcome_type = random.choice(['TARGET', 'TRAILING', 'PARTIAL'])

            if outcome_type == 'TARGET':
                # Hit full target
                exit_price = round(entry + target_points, 2)
                profit = 1600  # Full target
                status = 'WIN'
            elif outcome_type == 'TRAILING':
                # Trailing stop - partial profit (70-90% of target)
                trailing_pct = random.uniform(0.70, 0.90)
                exit_price = round(entry + (target_points * trailing_pct), 2)
                profit = round(1600 * trailing_pct, 2)
                status = 'WIN'
            else:
                # Partial profit (50-70% of target)
                partial_pct = random.uniform(0.50, 0.70)
                exit_price = round(entry + (target_points * partial_pct), 2)
                profit = round(1600 * partial_pct, 2)
                status = 'WIN'
        else:
            # Losing trade - hit SL or partial loss
            if random.random() < 0.80:
                # Hit full SL
                exit_price = round(entry - sl_points, 2)
                profit = -800  # Full SL
                status = 'LOSS'
            else:
                # Partial loss (50-80% of SL)
                partial_pct = random.uniform(0.50, 0.80)
                exit_price = round(entry - (sl_points * partial_pct), 2)
                profit = round(-800 * partial_pct, 2)
                status = 'LOSS'

        # Random strategy
        strategy = random.choice(self.strategies)

        trade = {
            'Time': time,
            'Instrument': instrument,
            'Entry': entry,
            'Exit': exit_price,
            'Profit': profit,
            'Strategy': strategy,
            'Signal': signal,
            'Status': status,
            'OrderID': f"ORD{random.randint(100000, 999999)}",
            'LotSize': lot_size,
            'ExitType': outcome_type if is_win else 'SL'
        }

        # Create duplicate with different strategy (30% chance)
        trades = [trade]
        if create_duplicate and random.random() < 0.30:
            # Duplicate with different strategy but different outcome
            duplicate = trade.copy()
            duplicate['Strategy'] = random.choice([s for s in self.strategies if s != strategy])

            # Different exit scenario
            if random.random() < 0.60:
                # Hit target
                duplicate['Exit'] = round(entry + target_points, 2)
                duplicate['Profit'] = 1600
                duplicate['Status'] = 'WIN'
                duplicate['ExitType'] = 'TARGET'
            else:
                # Hit SL
                duplicate['Exit'] = round(entry - sl_points, 2)
                duplicate['Profit'] = -800
                duplicate['Status'] = 'LOSS'
                duplicate['ExitType'] = 'SL'

            duplicate['OrderID'] = f"ORD{random.randint(100000, 999999)}"
            trades.append(duplicate)

        return trades
    
    def generate_daily_trades(self, date, num_trades=2):
        """Generate trades for a single day"""
        all_trades = []
        
        # Trading hours: 9:30 AM to 3:00 PM
        trading_times = [
            "09:30:00", "09:45:00", "10:00:00", "10:15:00", "10:30:00",
            "11:00:00", "11:30:00", "12:00:00", "12:30:00", "13:00:00",
            "13:30:00", "14:00:00", "14:30:00", "15:00:00"
        ]
        
        # Generate specified number of trades
        selected_times = random.sample(trading_times, min(num_trades, len(trading_times)))
        
        for time in selected_times:
            trades = self.generate_trade(date, time, create_duplicate=True)
            all_trades.extend(trades)
        
        return all_trades
    
    def generate_csv_for_date(self, date):
        """Generate CSV file for a specific date"""
        # Generate 1-3 trades per day
        num_trades = random.randint(1, 3)
        
        trades = self.generate_daily_trades(date, num_trades)
        
        if trades:
            # Create DataFrame
            df = pd.DataFrame(trades)
            
            # Format filename: livetrading_DDMMYY.csv
            filename = f"livetrading_{date.strftime('%d%m%y')}.csv"
            filepath = os.path.join(self.output_folder, filename)
            
            # Save CSV
            df.to_csv(filepath, index=False)
            
            return filename, len(trades)
        
        return None, 0
    
    def generate_12_months_data(self):
        """Generate sample data for last 12 months"""
        print("\n" + "="*80)
        print("🎲 GENERATING 12 MONTHS SAMPLE DATA")
        print("="*80)
        
        # Get dates for last 12 months (only trading days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        current_date = start_date
        total_files = 0
        total_trades = 0
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                filename, num_trades = self.generate_csv_for_date(current_date)
                
                if filename:
                    total_files += 1
                    total_trades += num_trades
                    print(f"✓ {filename}: {num_trades} trades")
            
            current_date += timedelta(days=1)
        
        print("\n" + "="*80)
        print("✅ DATA GENERATION COMPLETE!")
        print("="*80)
        print(f"📁 Folder: {self.output_folder}")
        print(f"📄 Files created: {total_files}")
        print(f"📊 Total trades: {total_trades}")
        print(f"📈 Duplicates included: ~{int(total_trades * 0.15)} (for testing)")
        
        return total_files, total_trades


# ============================================================================
# USAGE
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🎲 SAMPLE DATA GENERATOR FOR WIN RATE ANALYZER")
    print("="*80)
    
    generator = SampleDataGenerator(output_folder='./data')
    
    # Generate 12 months of sample data
    files, trades = generator.generate_12_months_data()
    
    print("\n" + "="*80)
    print("🎯 NEXT STEPS:")
    print("="*80)
    print("1. Check generated files: ls data\\livetrading_*.csv")
    print("2. Run analyzer: python analyze_12month_winrate.py")
    print("3. Open report: 12_MONTH_WIN_RATE_REPORT.xlsx")
    print("\n✅ Sample data ready for testing!")
