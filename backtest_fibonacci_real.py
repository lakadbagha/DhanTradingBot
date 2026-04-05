"""
Fibonacci Strategy - REAL Historical Data Backtest
Uses actual NIFTY price movements to determine trade outcomes
No simulated win rates - calculates actual results from market data
"""

from dhanhq import dhanhq
from config import CLIENT_ID, ACCESS_TOKEN
import strategy_config as cfg
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


class RealDataBacktester:
    def __init__(self):
        self.dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)
        self.trades = []
        self.daily_performance = {}
        
        # Load config
        self.trades_per_day = cfg.TRADES_PER_DAY
        self.max_loss = cfg.MAX_LOSS_PER_LOT
        self.target = cfg.TARGET_PER_LOT
        self.lot_size = cfg.LOT_SIZE
        self.lookback = cfg.LOOKBACK_PERIOD
        self.fib_level = cfg.FIB_ENTRY_LEVEL
        
    def get_intraday_data(self, date_str):
        """Get 5-minute intraday data for a specific date"""
        try:
            data = self.dhan.intraday_minute_data(
                security_id="13",
                exchange_segment="IDX_I",
                instrument_type="INDEX",
                from_date=date_str,
                to_date=date_str
            )
            
            if data and 'data' in data and len(data['data']) > 0:
                df = pd.DataFrame(data['data'])
                
                # Normalize column names
                column_mapping = {
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                }
                
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns:
                        df.rename(columns={old_col: new_col}, inplace=True)
                
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df['time'] = df['timestamp'].dt.time
                
                # Filter only market hours (9:15 to 15:30)
                df = df[(df['timestamp'].dt.hour >= 9) & (df['timestamp'].dt.hour <= 15)]
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                return df
            return None
        except Exception as e:
            print(f"Error fetching intraday data: {e}")
            return None
    
    def get_historical_dates(self, days=20):
        """Get last N trading days"""
        try:
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d')

            data = self.dhan.historical_daily_data(
                security_id="13",
                exchange_segment="NSE_EQ",
                instrument_type="INDEX",
                from_date=from_date,
                to_date=to_date
            )

            if data and 'data' in data and len(data['data']) > 0:
                df = pd.DataFrame(data['data'])

                # Handle timestamp conversion properly
                if 'timestamp' in df.columns:
                    # Convert timestamp (could be unix timestamp or string)
                    if pd.api.types.is_numeric_dtype(df['timestamp']):
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                    else:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])

                    df = df.sort_values('timestamp').tail(days)
                    dates = [d.strftime('%Y-%m-%d') for d in df['timestamp']]
                    print(f"Debug: Found dates: {dates[:3]}...{dates[-3:]}")
                    return dates
            return None
        except Exception as e:
            print(f"Error fetching dates: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def calculate_fibonacci_levels(self, df, lookback):
        """Calculate Fibonacci retracement levels"""
        if len(df) < lookback:
            return None, None, None
        
        recent_data = df.tail(lookback)
        swing_high = recent_data['High'].max()
        swing_low = recent_data['Low'].min()
        
        diff = swing_high - swing_low
        
        fib_levels = {
            '0.0': swing_high,
            '0.236': swing_high - (diff * 0.236),
            '0.382': swing_high - (diff * 0.382),
            '0.500': swing_high - (diff * 0.500),
            '0.618': swing_high - (diff * 0.618),
            '0.786': swing_high - (diff * 0.786),
            '1.0': swing_low
        }
        
        return fib_levels, swing_high, swing_low
    
    def detect_fib_entry(self, current_price, fib_levels):
        """Detect if price is at Fibonacci entry level"""
        if not fib_levels:
            return None, None
        
        fib_618 = fib_levels['0.618']
        tolerance = 50  # 50 points tolerance
        
        # Check if near 61.8% level
        if abs(current_price - fib_618) < tolerance:
            # Determine direction based on momentum
            if current_price > fib_levels['0.500']:
                return 'CALL', fib_618
            else:
                return 'PUT', fib_618
        
        return None, None
    
    def simulate_option_price(self, spot_price, strike, option_type):
        """Simplified option pricing for ITM options"""
        if option_type == "CE":
            intrinsic = max(0, spot_price - strike)
        else:  # PE
            intrinsic = max(0, strike - spot_price)
        
        # Add time value (simplified)
        time_value = spot_price * 0.015
        option_price = intrinsic + time_value
        
        return max(option_price, 30)
    
    def check_trade_outcome(self, df, entry_idx, entry_premium, option_type, strike):
        """
        Check if trade hits TARGET or SL based on actual price movements
        Returns: (exit_premium, pnl, exit_reason, exit_idx)
        """
        target_premium = entry_premium + cfg.get_target_per_contract()
        sl_premium = entry_premium - cfg.get_sl_per_contract()
        
        # Track from entry point onwards
        for i in range(entry_idx + 1, len(df)):
            current_spot = df.loc[i, 'Close']
            current_premium = self.simulate_option_price(current_spot, strike, option_type)
            
            # Check TARGET hit
            if current_premium >= target_premium:
                pnl = self.target
                return target_premium, pnl, f"Target Hit", i
            
            # Check SL hit
            if current_premium <= sl_premium:
                pnl = -self.max_loss
                return sl_premium, pnl, f"SL Hit", i
            
            # Check if market closed
            current_time = df.loc[i, 'time']
            if current_time >= pd.Timestamp('15:15:00').time():
                # Exit at market close
                pnl = (current_premium - entry_premium) * self.lot_size
                return current_premium, pnl, "Market Close", i
        
        # If loop ends, exit at last candle
        exit_premium = self.simulate_option_price(df.loc[len(df)-1, 'Close'], strike, option_type)
        pnl = (exit_premium - entry_premium) * self.lot_size
        return exit_premium, pnl, "Day End", len(df)-1
    
    def backtest_single_day(self, date_str, trade_num=1):
        """Backtest a single trading day using real intraday data"""
        
        df = self.get_intraday_data(date_str)
        
        if df is None or len(df) < 30:
            print(f"  ⚠️ Insufficient intraday data for {date_str}")
            return None
        
        # Calculate Fibonacci levels from first half of the day
        mid_idx = len(df) // 2
        fib_levels, swing_high, swing_low = self.calculate_fibonacci_levels(df.iloc[:mid_idx], self.lookback)
        
        if fib_levels is None:
            print(f"  ⚠️ Cannot calculate Fibonacci levels for {date_str}")
            return None
        
        # Look for entry signal in second half
        for idx in range(mid_idx, len(df)):
            current_price = df.loc[idx, 'Close']
            current_time = df.loc[idx, 'time']
            
            # Skip if too late in the day
            if current_time >= pd.Timestamp('14:30:00').time():
                break
            
            # Check for Fibonacci entry
            option_type, fib_price = self.detect_fib_entry(current_price, fib_levels)
            
            if option_type:
                # Calculate ITM strike
                itm_points = cfg.ITM_POINTS
                if option_type == 'CALL':
                    strike = round((current_price - itm_points) / 50) * 50
                else:
                    strike = round((current_price + itm_points) / 50) * 50
                
                # Entry premium
                entry_premium = self.simulate_option_price(current_price, strike, "CE" if option_type == "CALL" else "PE")
                
                # Check trade outcome using real price movements
                exit_premium, pnl, exit_reason, exit_idx = self.check_trade_outcome(
                    df, idx, entry_premium, "CE" if option_type == "CALL" else "PE", strike
                )
                
                # Create trade record
                trade = {
                    'date': date_str,
                    'entry_time': df.loc[idx, 'timestamp'],
                    'exit_time': df.loc[exit_idx, 'timestamp'],
                    'option_type': option_type,
                    'strike': strike,
                    'entry_spot': current_price,
                    'exit_spot': df.loc[exit_idx, 'Close'],
                    'entry_premium': entry_premium,
                    'exit_premium': exit_premium,
                    'lot_size': self.lot_size,
                    'pnl': pnl,
                    'exit_reason': exit_reason,
                    'fib_level': fib_price,
                    'swing_high': swing_high,
                    'swing_low': swing_low
                }
                
                return trade
        
        print(f"  ⚠️ No valid entry signal found for {date_str}")
        return None
    
    def run_backtest(self, days=None):
        """Run backtest on last N trading days using real data"""
        
        if days is None:
            days = cfg.BACKTEST_DAYS
        
        print("=" * 80)
        print(f"FIBONACCI STRATEGY - REAL DATA BACKTEST")
        print("=" * 80)
        print(f"Backtest Period: Last {days} trading days")
        print(f"Initial Capital: Rs.{cfg.INITIAL_CAPITAL:,}")
        print(f"SL: Rs.{self.max_loss:,} | Target: Rs.{self.target:,}")
        print(f"ITM Points: {cfg.ITM_POINTS} | Lookback: {self.lookback}")
        print(f"Lot Size: {self.lot_size}")
        print("=" * 80)
        
        # Get trading dates
        dates = self.get_historical_dates(days)
        
        if not dates:
            print("❌ Could not fetch historical dates")
            return None
        
        print(f"✅ Found {len(dates)} trading days\n")
        
        capital = cfg.INITIAL_CAPITAL
        self.trades = []
        
        for i, date_str in enumerate(dates, 1):
            print(f"Day {i}/{len(dates)}: {date_str}")
            
            # Try to execute trade for this day
            trade = self.backtest_single_day(date_str)
            
            if trade:
                self.trades.append(trade)
                capital += trade['pnl']
                
                print(f"  ✅ {trade['option_type']} @ Strike {trade['strike']}")
                print(f"     Entry: {trade['entry_time'].strftime('%H:%M')} @ Rs.{trade['entry_premium']:.2f}")
                print(f"     Exit:  {trade['exit_time'].strftime('%H:%M')} @ Rs.{trade['exit_premium']:.2f}")
                print(f"     {trade['exit_reason']} | P&L: Rs.{trade['pnl']:,.0f}")
                print(f"     Capital: Rs.{capital:,.0f}")
            
            print("-" * 80)
        
        self.generate_report(cfg.INITIAL_CAPITAL, capital)
        return self.trades
    
    def generate_report(self, initial_capital, final_capital):
        """Generate comprehensive backtest report"""
        
        if len(self.trades) == 0:
            print("\n⚠️ No trades executed")
            return
        
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        actual_win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(t['pnl'] for t in winning_trades)
        total_loss = sum(t['pnl'] for t in losing_trades)
        net_pnl = final_capital - initial_capital
        
        avg_win = total_profit / win_count if win_count > 0 else 0
        avg_loss = abs(total_loss / loss_count) if loss_count > 0 else 0
        profit_factor = abs(total_profit / total_loss) if total_loss != 0 else 0
        
        call_trades = [t for t in self.trades if t['option_type'] == 'CALL']
        put_trades = [t for t in self.trades if t['option_type'] == 'PUT']
        
        print("\n" + "=" * 80)
        print(f"🎯 REAL DATA BACKTEST RESULTS")
        print("=" * 80)
        
        print(f"\n💰 CAPITAL:")
        print(f"   Initial Capital:    Rs.{initial_capital:,.2f}")
        print(f"   Final Capital:      Rs.{final_capital:,.2f}")
        print(f"   Net P&L:            Rs.{net_pnl:,.2f} ({(net_pnl/initial_capital*100):.2f}%)")
        
        print(f"\n📈 TRADE STATISTICS:")
        print(f"   Total Trades:       {total_trades}")
        print(f"   CALL Trades:        {len(call_trades)}")
        print(f"   PUT Trades:         {len(put_trades)}")
        print(f"   Winning Trades:     {win_count}")
        print(f"   Losing Trades:      {loss_count}")
        print(f"   🎯 ACTUAL WIN RATE:  {actual_win_rate:.2f}%  ⭐")
        
        print(f"\n💵 PROFIT/LOSS:")
        print(f"   Total Profit:       Rs.{total_profit:,.2f}")
        print(f"   Total Loss:         Rs.{total_loss:,.2f}")
        print(f"   Average Win:        Rs.{avg_win:,.2f}")
        print(f"   Average Loss:       Rs.{avg_loss:,.2f}")
        print(f"   Profit Factor:      {profit_factor:.2f}")
        
        print(f"\n📊 DAILY METRICS:")
        trading_days = cfg.BACKTEST_DAYS
        print(f"   Avg Daily P&L:      Rs.{net_pnl/trading_days:,.2f}")
        print(f"   Monthly P&L (est):  Rs.{(net_pnl/trading_days)*20:,.2f}")
        print(f"   Monthly Return:     {((net_pnl/trading_days)*20/initial_capital*100):.2f}%")
        
        print("\n" + "=" * 80)
        print(f"✅ Backtest completed with REAL market data!")
        print("=" * 80)


if __name__ == "__main__":
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Print configuration
    cfg.print_config()
    
    if not cfg.validate_config():
        print("\n❌ Please fix configuration errors")
        sys.exit(1)
    
    print("\n🚀 Starting REAL DATA backtest...\n")
    
    # Run backtest
    backtester = RealDataBacktester()
    trades = backtester.run_backtest()
    
    if trades:
        print(f"\n✅ Backtest completed! {len(trades)} trades executed.")
    else:
        print("\n⚠️ No trades were executed. Check data availability.")
