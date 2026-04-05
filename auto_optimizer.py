"""
Automated Strategy Optimizer
Finds best parameters to achieve >60% win rate with real market data
"""

from dhanhq import dhanhq
from config import CLIENT_ID, ACCESS_TOKEN
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import itertools


class StrategyOptimizer:
    def __init__(self):
        self.dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)
        self.results = []
        
    def get_historical_data(self, days=60):
        """Get NIFTY historical data"""
        try:
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            data = self.dhan.historical_daily_data(
                security_id="13",
                exchange_segment="NSE_EQ",
                instrument_type="INDEX",
                from_date=from_date,
                to_date=to_date
            )
            
            if data and 'data' in data and len(data['data']) > 0:
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
                return df
            
            return None
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def calculate_fibonacci_levels(self, high, low):
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        
        fib_levels = {
            '0.0': high,
            '0.236': high - (diff * 0.236),
            '0.382': high - (diff * 0.382),
            '0.500': high - (diff * 0.500),
            '0.618': high - (diff * 0.618),
            '0.786': high - (diff * 0.786),
            '1.0': low
        }
        
        return fib_levels
    
    def simulate_option_price(self, spot_price, strike, option_type):
        """Simplified option pricing"""
        if option_type == "CE":
            intrinsic = max(0, spot_price - strike)
        else:
            intrinsic = max(0, strike - spot_price)
        
        time_value = spot_price * 0.015
        option_price = intrinsic + time_value
        
        return max(option_price, 30)
    
    def check_trade_outcome(self, entry_day, next_day_high, next_day_low, next_day_close, 
                           entry_premium, option_type, strike, sl_per_contract, target_per_contract):
        """Check if trade hits TARGET or SL"""
        target_premium = entry_premium + target_per_contract
        sl_premium = entry_premium - sl_per_contract
        
        high_premium = self.simulate_option_price(next_day_high, strike, option_type)
        low_premium = self.simulate_option_price(next_day_low, strike, option_type)
        close_premium = self.simulate_option_price(next_day_close, strike, option_type)
        
        # Check if target was hit
        if high_premium >= target_premium:
            return 1, target_per_contract * 50, "Target"
        
        # Check if SL was hit
        if low_premium <= sl_premium:
            return 0, -sl_per_contract * 50, "SL"
        
        # Exit at close
        pnl = (close_premium - entry_premium) * 50
        return 1 if pnl > 0 else 0, pnl, "Close"
    
    def backtest_with_params(self, df, params):
        """Backtest with specific parameters"""
        itm_points = params['itm_points']
        lookback = params['lookback']
        tolerance = params['tolerance']
        sl_amount = params['sl_amount']
        target_amount = params['target_amount']
        use_trend = params['use_trend']
        
        sl_per_contract = sl_amount / 50
        target_per_contract = target_amount / 50
        
        trades = []
        
        for idx in range(lookback, len(df) - 1):
            current_row = df.iloc[idx]
            date = current_row['Date'].date()
            day_open = current_row['Open']
            high = current_row['High']
            low = current_row['Low']
            close = current_row['Close']
            
            # Calculate Fibonacci
            lookback_data = df.iloc[idx-lookback:idx]
            swing_high = lookback_data['High'].max()
            swing_low = lookback_data['Low'].min()
            
            fib_levels = self.calculate_fibonacci_levels(swing_high, swing_low)
            fib_618 = fib_levels['0.618']
            fib_382 = fib_levels['0.382']
            
            # Trend filter
            if use_trend:
                sma_20 = df.iloc[max(0, idx-20):idx]['Close'].mean()
                trend_up = close > sma_20
                trend_down = close < sma_20
            else:
                trend_up = True
                trend_down = True
            
            entry_signal = False
            option_type = None
            
            # Bullish setup
            if abs(low - fib_618) < tolerance and close > day_open and trend_up:
                entry_signal = True
                option_type = 'CALL'
                entry_price = (low + close) / 2
            
            # Bearish setup
            elif abs(high - fib_382) < tolerance and close < day_open and trend_down:
                entry_signal = True
                option_type = 'PUT'
                entry_price = (high + close) / 2
            
            if not entry_signal:
                continue
            
            # Calculate strike
            if option_type == 'CALL':
                strike = round((entry_price - itm_points) / 50) * 50
            else:
                strike = round((entry_price + itm_points) / 50) * 50
            
            # Entry premium
            entry_premium = self.simulate_option_price(entry_price, strike, "CE" if option_type == "CALL" else "PE")
            
            # Next day
            next_day = df.iloc[idx + 1]
            next_high = next_day['High']
            next_low = next_day['Low']
            next_close = next_day['Close']
            
            # Check outcome
            win, pnl, exit_reason = self.check_trade_outcome(
                entry_price, next_high, next_low, next_close,
                entry_premium, "CE" if option_type == "CALL" else "PE", strike,
                sl_per_contract, target_per_contract
            )
            
            trades.append({
                'date': date,
                'win': win,
                'pnl': pnl,
                'exit_reason': exit_reason
            })
        
        return trades
    
    def calculate_metrics(self, trades):
        """Calculate performance metrics"""
        if not trades:
            return None
        
        total_trades = len(trades)
        wins = sum(1 for t in trades if t['win'] == 1)
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in trades)
        total_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        total_loss = sum(abs(t['pnl']) for t in trades if t['pnl'] < 0)
        
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': total_trades - wins,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'profit_factor': profit_factor,
            'avg_pnl_per_trade': total_pnl / total_trades if total_trades > 0 else 0
        }
    
    def optimize(self):
        """Run optimization"""
        print("=" * 80)
        print("🔧 STRATEGY OPTIMIZER - Finding Best Parameters")
        print("=" * 80)
        print("Goal: Win Rate > 60% with positive returns\n")
        
        # Get data
        print("📊 Fetching historical data...")
        df = self.get_historical_data(days=60)
        
        if df is None:
            print("❌ Failed to fetch data")
            return None
        
        print(f"✅ Loaded {len(df)} days of data\n")
        
        # Parameter combinations to test
        param_grid = {
            'itm_points': [50, 100, 150],
            'lookback': [10, 15, 20],
            'tolerance': [50, 75, 100, 150],
            'sl_amount': [800, 1000, 1200],
            'target_amount': [1600, 2000, 2400],
            'use_trend': [True, False]
        }
        
        print("🧪 Testing parameter combinations...\n")
        print(f"Total combinations to test: {np.prod([len(v) for v in param_grid.values()])}")
        print("-" * 80)
        
        best_result = None
        best_params = None
        test_count = 0
        
        # Generate all combinations
        keys = param_grid.keys()
        values = param_grid.values()
        
        for combination in itertools.product(*values):
            params = dict(zip(keys, combination))
            test_count += 1
            
            # Backtest
            trades = self.backtest_with_params(df, params)
            
            if not trades or len(trades) < 5:
                continue
            
            metrics = self.calculate_metrics(trades)
            
            if metrics and metrics['win_rate'] >= 60 and metrics['total_pnl'] > 0:
                print(f"✅ Test #{test_count}: Win Rate {metrics['win_rate']:.1f}% | P&L: Rs.{metrics['total_pnl']:,.0f}")
                print(f"   ITM:{params['itm_points']} | Lookback:{params['lookback']} | Tol:{params['tolerance']} | Trend:{params['use_trend']}")
                print(f"   SL:{params['sl_amount']} | Target:{params['target_amount']} | Trades:{metrics['total_trades']}")
                
                # Check if best so far
                if best_result is None or metrics['total_pnl'] > best_result['total_pnl']:
                    best_result = metrics
                    best_params = params
                    print(f"   ⭐ NEW BEST!")
                
                print("-" * 80)
        
        print(f"\n✅ Optimization complete! Tested {test_count} combinations\n")
        
        if best_result and best_params:
            print("=" * 80)
            print("🏆 BEST PARAMETERS FOUND")
            print("=" * 80)
            print(f"\n📊 PERFORMANCE:")
            print(f"   Win Rate:           {best_result['win_rate']:.1f}%")
            print(f"   Total Trades:       {best_result['total_trades']}")
            print(f"   Wins:               {best_result['wins']}")
            print(f"   Losses:             {best_result['losses']}")
            print(f"   Total P&L:          Rs.{best_result['total_pnl']:,.0f}")
            print(f"   Profit Factor:      {best_result['profit_factor']:.2f}")
            print(f"   Avg P&L/Trade:      Rs.{best_result['avg_pnl_per_trade']:,.0f}")
            
            print(f"\n⚙️  PARAMETERS:")
            print(f"   ITM Points:         {best_params['itm_points']}")
            print(f"   Lookback Period:    {best_params['lookback']}")
            print(f"   Tolerance:          {best_params['tolerance']}")
            print(f"   SL per Lot:         Rs.{best_params['sl_amount']:,}")
            print(f"   Target per Lot:     Rs.{best_params['target_amount']:,}")
            print(f"   Use Trend Filter:   {best_params['use_trend']}")
            
            print("\n" + "=" * 80)
            
            return best_params, best_result
        else:
            print("⚠️  Could not find parameters achieving >60% win rate")
            print("   Try expanding the parameter search range")
            return None, None


def update_config_file(params):
    """Update strategy_config.py with optimized parameters"""
    if not params:
        return
    
    config_updates = f"""
# ============================================
# OPTIMIZED PARAMETERS (Auto-generated)
# ============================================

# OPTIMIZED TRADING PARAMETERS
MAX_LOSS_PER_LOT = {params['sl_amount']}
TARGET_PER_LOT = {params['target_amount']}

# OPTIMIZED OPTION SELECTION
ITM_POINTS = {params['itm_points']}

# OPTIMIZED FIBONACCI SETTINGS
LOOKBACK_PERIOD = {params['lookback']}
FIBONACCI_TOLERANCE = {params['tolerance']}  # Add this to your strategy

# TREND FILTER
USE_TREND_FILTER = {params['use_trend']}  # Add this to your strategy
"""
    
    print("\n📝 Configuration updates ready:")
    print(config_updates)
    
    print("\n✅ Copy these to strategy_config.py or I can update it automatically")


if __name__ == "__main__":
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    optimizer = StrategyOptimizer()
    best_params, best_metrics = optimizer.optimize()
    
    if best_params:
        update_config_file(best_params)
        
        # Save results
        with open('optimization_results.txt', 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("OPTIMIZATION RESULTS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Win Rate: {best_metrics['win_rate']:.1f}%\n")
            f.write(f"Total Trades: {best_metrics['total_trades']}\n")
            f.write(f"Total P&L: Rs.{best_metrics['total_pnl']:,.0f}\n")
            f.write(f"Profit Factor: {best_metrics['profit_factor']:.2f}\n\n")
            f.write("Parameters:\n")
            for key, value in best_params.items():
                f.write(f"  {key}: {value}\n")
        
        print("\n💾 Results saved to: optimization_results.txt")
    else:
        print("\n⚠️  Optimization failed to find suitable parameters")
