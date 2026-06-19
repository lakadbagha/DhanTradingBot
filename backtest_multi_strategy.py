"""
MULTI-STRATEGY OPTIMIZER
Combines multiple strategies to ensure 1+ trade per day
Strategies: Fibonacci + Candlestick Patterns + EMA Bounce + S/R Bounce
"""

from dhanhq import dhanhq, DhanContext
from config import CLIENT_ID, ACCESS_TOKEN
import strategy_config as cfg
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


class MultiStrategyBacktester:
    def __init__(self):
        dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
        self.dhan = dhanhq(dhan_context)
        self.trades = []
        
        # Load config
        self.max_loss = cfg.MAX_LOSS_PER_LOT
        self.target = cfg.TARGET_PER_LOT
        self.lot_size = cfg.LOT_SIZE
        self.itm_points = cfg.ITM_POINTS
        
    def get_historical_data(self, days=120):
        """Get NIFTY historical data"""
        try:
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            print(f"📊 Fetching {days} days of data...")
            
            data = self.dhan.historical_daily_data(
                security_id="13",
                exchange_segment="NSE_EQ",
                instrument_type="INDEX",
                from_date=from_date,
                to_date=to_date
            )
            
            if data and 'data' in data:
                df = pd.DataFrame(data['data'])
                
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
                    if pd.api.types.is_numeric_dtype(df['timestamp']):
                        df['Date'] = pd.to_datetime(df['timestamp'], unit='s')
                    else:
                        df['Date'] = pd.to_datetime(df['timestamp'])
                
                df = df.sort_values('Date').reset_index(drop=True)
                
                # Add technical indicators
                df['EMA20'] = df['Close'].ewm(span=20).mean()
                df['EMA50'] = df['Close'].ewm(span=50).mean()
                df['SMA20'] = df['Close'].rolling(20).mean()
                
                print(f"✅ Loaded {len(df)} days\n")
                return df
            
            return None
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def calculate_fibonacci_levels(self, high, low):
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        return {
            '0.0': high,
            '0.236': high - (diff * 0.236),
            '0.382': high - (diff * 0.382),
            '0.500': high - (diff * 0.500),
            '0.618': high - (diff * 0.618),
            '0.786': high - (diff * 0.786),
            '1.0': low
        }
    
    def detect_candlestick_pattern(self, df, idx):
        """Detect bullish/bearish candlestick patterns"""
        if idx < 1:
            return None, None
        
        current = df.iloc[idx]
        prev = df.iloc[idx-1]
        
        o, h, l, c = current['Open'], current['High'], current['Low'], current['Close']
        prev_o, prev_c = prev['Open'], prev['Close']
        
        body = abs(c - o)
        total_range = h - l
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        
        # HAMMER (Bullish)
        # Small body at top, long lower shadow
        if lower_shadow > body * 2 and upper_shadow < body * 0.5 and c > o:
            if current['Close'] > current['EMA20']:  # In uptrend
                return 'CALL', 'Hammer'
        
        # SHOOTING STAR (Bearish)
        # Small body at bottom, long upper shadow
        if upper_shadow > body * 2 and lower_shadow < body * 0.5 and c < o:
            if current['Close'] < current['EMA20']:  # In downtrend
                return 'PUT', 'Shooting Star'
        
        # BULLISH ENGULFING
        if prev_c < prev_o and c > o:  # Previous red, current green
            if c > prev_o and o < prev_c:  # Current engulfs previous
                if current['Close'] > current['EMA20']:
                    return 'CALL', 'Bullish Engulfing'
        
        # BEARISH ENGULFING
        if prev_c > prev_o and c < o:  # Previous green, current red
            if c < prev_o and o > prev_c:  # Current engulfs previous
                if current['Close'] < current['EMA20']:
                    return 'PUT', 'Bearish Engulfing'
        
        return None, None
    
    def detect_ema_bounce(self, df, idx):
        """Detect bounce from 20 EMA"""
        if idx < 2:
            return None, None
        
        current = df.iloc[idx]
        prev = df.iloc[idx-1]
        
        ema20 = current['EMA20']
        price = current['Close']
        prev_low = prev['Low']
        
        # Bullish: Price bounced off EMA20 from below
        if prev_low <= ema20 * 1.005 and price > ema20:  # Within 0.5% and closed above
            if current['Close'] > current['EMA50']:  # Overall uptrend
                return 'CALL', '20 EMA Bounce (Bull)'
        
        # Bearish: Price rejected at EMA20 from above
        if prev['High'] >= ema20 * 0.995 and price < ema20:
            if current['Close'] < current['EMA50']:  # Overall downtrend
                return 'PUT', '20 EMA Rejection (Bear)'
        
        return None, None
    
    def detect_support_resistance(self, df, idx, lookback=10):
        """Detect bounce from support/resistance levels"""
        if idx < lookback:
            return None, None
        
        current = df.iloc[idx]
        lookback_data = df.iloc[idx-lookback:idx]
        
        # Find recent swing high/low (S/R levels)
        resistance = lookback_data['High'].max()
        support = lookback_data['Low'].min()
        
        price = current['Close']
        low = current['Low']
        high = current['High']
        
        tolerance = 50  # 50 points tolerance
        
        # Bullish: Bounced from support
        if abs(low - support) < tolerance and price > current['Open']:
            if current['Close'] > current['SMA20']:
                return 'CALL', 'Support Bounce'
        
        # Bearish: Rejected from resistance
        if abs(high - resistance) < tolerance and price < current['Open']:
            if current['Close'] < current['SMA20']:
                return 'PUT', 'Resistance Rejection'
        
        return None, None
    
    def detect_fibonacci_setup(self, df, idx, lookback=10):
        """Detect Fibonacci retracement setup"""
        if idx < lookback:
            return None, None
        
        current = df.iloc[idx]
        lookback_data = df.iloc[idx-lookback:idx]
        
        swing_high = lookback_data['High'].max()
        swing_low = lookback_data['Low'].min()
        
        fib_levels = self.calculate_fibonacci_levels(swing_high, swing_low)
        fib_618 = fib_levels['0.618']
        fib_382 = fib_levels['0.382']
        
        tolerance = 150
        
        # Bullish: Bounce from 61.8% retracement
        if abs(current['Low'] - fib_618) < tolerance and current['Close'] > current['Open']:
            if current['Close'] > current['SMA20']:
                return 'CALL', 'Fib 61.8% Bounce'
        
        # Bearish: Rejection from 38.2% retracement
        if abs(current['High'] - fib_382) < tolerance and current['Close'] < current['Open']:
            if current['Close'] < current['SMA20']:
                return 'PUT', 'Fib 38.2% Rejection'
        
        return None, None
    
    def simulate_option_price(self, spot_price, strike, option_type):
        """Simplified option pricing"""
        if option_type == "CE":
            intrinsic = max(0, spot_price - strike)
        else:
            intrinsic = max(0, strike - spot_price)
        
        time_value = spot_price * 0.015
        return max(intrinsic + time_value, 30)
    
    def check_trade_outcome(self, entry_price, next_day_high, next_day_low, next_day_close, 
                           entry_premium, option_type, strike):
        """Check if trade hits TARGET or SL"""
        sl_per_contract = self.max_loss / self.lot_size
        target_per_contract = self.target / self.lot_size
        
        target_premium = entry_premium + target_per_contract
        sl_premium = entry_premium - sl_per_contract
        
        high_premium = self.simulate_option_price(next_day_high, strike, option_type)
        low_premium = self.simulate_option_price(next_day_low, strike, option_type)
        close_premium = self.simulate_option_price(next_day_close, strike, option_type)
        
        # Check TARGET
        if high_premium >= target_premium:
            return target_premium, self.target, "Target ✅"
        
        # Check SL
        if low_premium <= sl_premium:
            return sl_premium, -self.max_loss, "SL ❌"
        
        # Close exit
        pnl = (close_premium - entry_premium) * self.lot_size
        return close_premium, pnl, "Close Exit"
    
    def backtest_day(self, df, idx):
        """Try ALL strategies for this day, take first valid signal"""
        
        if idx + 1 >= len(df) or idx < 20:
            return None
        
        current = df.iloc[idx]
        date = current['Date'].date()
        
        # Try each strategy in priority order
        strategies = [
            ('Fibonacci', lambda: self.detect_fibonacci_setup(df, idx, lookback=10)),
            ('Candlestick', lambda: self.detect_candlestick_pattern(df, idx)),
            ('EMA Bounce', lambda: self.detect_ema_bounce(df, idx)),
            ('Support/Resistance', lambda: self.detect_support_resistance(df, idx, lookback=10))
        ]
        
        for strategy_name, detect_func in strategies:
            option_type, signal_name = detect_func()
            
            if option_type:  # Found a signal!
                entry_price = current['Close']
                
                # Calculate strike
                if option_type == 'CALL':
                    strike = round((entry_price - self.itm_points) / 50) * 50
                else:
                    strike = round((entry_price + self.itm_points) / 50) * 50
                
                # Entry premium
                entry_premium = self.simulate_option_price(entry_price, strike, "CE" if option_type == "CALL" else "PE")
                
                # Next day data
                next_day = df.iloc[idx + 1]
                
                # Check outcome
                exit_premium, pnl, exit_reason = self.check_trade_outcome(
                    entry_price, next_day['High'], next_day['Low'], next_day['Close'],
                    entry_premium, "CE" if option_type == "CALL" else "PE", strike
                )
                
                return {
                    'date': date,
                    'strategy': strategy_name,
                    'signal': signal_name,
                    'option_type': option_type,
                    'strike': strike,
                    'entry_spot': entry_price,
                    'exit_spot': next_day['Close'],
                    'entry_premium': entry_premium,
                    'exit_premium': exit_premium,
                    'pnl': pnl,
                    'exit_reason': exit_reason
                }
        
        return None  # No signal from any strategy
    
    def run_backtest(self, days=60):
        """Run multi-strategy backtest"""
        
        print("=" * 80)
        print(f"🎯 MULTI-STRATEGY BACKTEST (Fibonacci + Candlestick + EMA + S/R)")
        print("=" * 80)
        print(f"Goal: At least 1 trade per day")
        print(f"Initial Capital: Rs.{cfg.INITIAL_CAPITAL:,}")
        print(f"SL: Rs.{self.max_loss:,} | Target: Rs.{self.target:,}")
        print("=" * 80)
        print()
        
        df = self.get_historical_data(days=days*2)
        
        if df is None:
            return None
        
        print(f"🔍 Scanning {days} days with 4 strategies...\n")
        print("-" * 80)
        
        capital = cfg.INITIAL_CAPITAL
        self.trades = []
        daily_trades = {}  # Track trades per day
        
        for idx in range(20, len(df) - 1):
            trade = self.backtest_day(df, idx)
            
            if trade:
                self.trades.append(trade)
                capital += trade['pnl']
                
                # Track daily
                date_str = str(trade['date'])
                daily_trades[date_str] = daily_trades.get(date_str, 0) + 1
                
                print(f"Trade #{len(self.trades)}: {trade['date']}")
                print(f"  Strategy: {trade['strategy']} | Signal: {trade['signal']}")
                print(f"  {trade['option_type']} @ Strike {trade['strike']}")
                print(f"  {trade['exit_reason']} | P&L: Rs.{trade['pnl']:,.0f}")
                print(f"  Capital: Rs.{capital:,.0f}")
                print("-" * 80)
            
            if len(self.trades) >= days:
                break
        
        self.generate_report(cfg.INITIAL_CAPITAL, capital, daily_trades)
        return self.trades
    
    def generate_report(self, initial_capital, final_capital, daily_trades):
        """Generate report"""
        
        if not self.trades:
            print("\n⚠️  No trades")
            return
        
        total_trades = len(self.trades)
        wins = sum(1 for t in self.trades if t['pnl'] > 0)
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(t['pnl'] for t in self.trades if t['pnl'] > 0)
        total_loss = sum(abs(t['pnl']) for t in self.trades if t['pnl'] <= 0)
        net_pnl = final_capital - initial_capital
        
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # Strategy breakdown
        strategy_stats = {}
        for trade in self.trades:
            strat = trade['strategy']
            if strat not in strategy_stats:
                strategy_stats[strat] = {'total': 0, 'wins': 0, 'pnl': 0}
            strategy_stats[strat]['total'] += 1
            if trade['pnl'] > 0:
                strategy_stats[strat]['wins'] += 1
            strategy_stats[strat]['pnl'] += trade['pnl']
        
        print("\n" + "=" * 80)
        print(f"📊 MULTI-STRATEGY BACKTEST RESULTS")
        print("=" * 80)
        
        print(f"\n💰 CAPITAL:")
        print(f"   Initial: Rs.{initial_capital:,}")
        print(f"   Final: Rs.{final_capital:,}")
        print(f"   Net P&L: Rs.{net_pnl:,.0f} ({(net_pnl/initial_capital*100):+.2f}%)")
        
        print(f"\n📈 OVERALL STATS:")
        print(f"   Total Trades: {total_trades}")
        print(f"   Wins: {wins} | Losses: {losses}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Profit Factor: {profit_factor:.2f}")
        print(f"   Avg P&L/Trade: Rs.{net_pnl/total_trades:,.0f}")
        
        print(f"\n🎯 STRATEGY BREAKDOWN:")
        for strat, stats in strategy_stats.items():
            strat_wr = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {strat}:")
            print(f"      Trades: {stats['total']} | Win Rate: {strat_wr:.1f}%")
            print(f"      Total P&L: Rs.{stats['pnl']:,.0f}")
        
        print(f"\n📅 DAILY COVERAGE:")
        days_with_trades = len(daily_trades)
        print(f"   Days with trades: {days_with_trades}")
        print(f"   Trades per day: {total_trades/days_with_trades:.2f}")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    backtester = MultiStrategyBacktester()
    trades = backtester.run_backtest(days=60)
    
    if trades:
        print(f"\n✅ Multi-strategy backtest complete! {len(trades)} trades")
    else:
        print("\n⚠️  No trades found")
