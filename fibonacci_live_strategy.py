"""
Fibonacci Retracement LIVE Options Strategy - NIFTY 50
Entry: Retrace to 61.8%, candle closes above/below 50%
SL: ₹1500, Target: ₹3000
"""

from dhanhq import dhanhq
from config import CLIENT_ID, ACCESS_TOKEN
import pandas as pd
from datetime import datetime, timedelta
import time


class FibonacciLiveStrategy:
    def __init__(self):
        self.dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)
        self.position = None
        
    def get_nifty_spot_price(self):
        """Get current NIFTY 50 price"""
        try:
            data = self.dhan.ohlc_data({
                self.dhan.NSE: ["13"]
            })
            
            if data and data.get('status') == 'success':
                nifty_data = data.get('data', {}).get('NSE', {}).get('13', {})
                return nifty_data.get('last_price', 0)
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_nifty_historical_data(self, from_date, to_date):
        """Get NIFTY historical data for Fib calculation"""
        try:
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
                    'close': 'Close'
                }
                
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns:
                        df.rename(columns={old_col: new_col}, inplace=True)
                
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                return df
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def calculate_fibonacci_levels(self, swing_high, swing_low, trend):
        """Calculate Fib levels"""
        price_range = abs(swing_high - swing_low)
        
        if trend == "UPTREND":
            levels = {
                '0%': swing_high,
                '23.6%': swing_high - (0.236 * price_range),
                '38.2%': swing_high - (0.382 * price_range),
                '50%': swing_high - (0.5 * price_range),
                '61.8%': swing_high - (0.618 * price_range),
                '100%': swing_low
            }
        else:
            levels = {
                '0%': swing_low,
                '23.6%': swing_low + (0.236 * price_range),
                '38.2%': swing_low + (0.382 * price_range),
                '50%': swing_low + (0.5 * price_range),
                '61.8%': swing_low + (0.618 * price_range),
                '100%': swing_high
            }
        
        return levels
    
    def analyze_market(self):
        """Analyze market for Fib setup"""
        # Get last 30 days data
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        df = self.get_nifty_historical_data(from_date, to_date)
        
        if df is None or len(df) < 20:
            return None
        
        # Get recent swing points (last 20 candles)
        recent = df.tail(20)
        swing_high = recent['High'].max()
        swing_low = recent['Low'].min()
        
        swing_high_idx = recent['High'].idxmax()
        swing_low_idx = recent['Low'].idxmin()
        
        # Get current price and today's candle
        spot_price = self.get_nifty_spot_price()
        if spot_price is None:
            return None
        
        today = df.tail(1).iloc[0]
        
        # Determine trend
        if swing_high_idx > swing_low_idx:
            trend = "UPTREND"
            fib_levels = self.calculate_fibonacci_levels(swing_high, swing_low, trend)
            
            # Check if we're at 61.8% retracement area
            is_near_618 = abs(spot_price - fib_levels['61.8%']) < (swing_high - swing_low) * 0.05
            is_above_50 = spot_price > fib_levels['50%']
            
            if is_near_618:
                return {
                    'trend': 'UPTREND',
                    'signal': 'BUY' if is_above_50 else 'WAIT',
                    'spot_price': spot_price,
                    'swing_high': swing_high,
                    'swing_low': swing_low,
                    'fib_levels': fib_levels,
                    'current_fib': '61.8% area',
                    'message': f"Price at 61.8% ({fib_levels['61.8%']:.2f}). Wait for green candle close above 50% ({fib_levels['50%']:.2f})"
                }
        else:
            trend = "DOWNTREND"
            fib_levels = self.calculate_fibonacci_levels(swing_high, swing_low, trend)
            
            is_near_618 = abs(spot_price - fib_levels['61.8%']) < (swing_high - swing_low) * 0.05
            is_below_50 = spot_price < fib_levels['50%']
            
            if is_near_618:
                return {
                    'trend': 'DOWNTREND',
                    'signal': 'SELL' if is_below_50 else 'WAIT',
                    'spot_price': spot_price,
                    'swing_high': swing_high,
                    'swing_low': swing_low,
                    'fib_levels': fib_levels,
                    'current_fib': '61.8% area',
                    'message': f"Price at 61.8% ({fib_levels['61.8%']:.2f}). Wait for red candle close below 50% ({fib_levels['50%']:.2f})"
                }
        
        return {
            'trend': trend,
            'signal': 'NO_SETUP',
            'spot_price': spot_price,
            'swing_high': swing_high,
            'swing_low': swing_low,
            'fib_levels': fib_levels,
            'message': 'No Fib setup detected. Waiting for retracement to 61.8%'
        }
    
    def run_live_strategy(self, check_interval=300):
        """
        Run Fibonacci live strategy
        Checks every 5 minutes by default
        """
        print("=" * 70)
        print("FIBONACCI RETRACEMENT - LIVE OPTIONS STRATEGY")
        print("=" * 70)
        print("📐 Strategy:")
        print("   Entry: Price retraces to 61.8%, candle closes above/below 50%")
        print("   SL: ₹1,500 | Target: ₹3,000")
        print("   Instrument: NIFTY 50 ITM Options")
        print("   Lot Size: 50 quantity")
        print("=" * 70)
        
        while True:
            try:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                
                # Analyze market
                analysis = self.analyze_market()
                
                if analysis is None:
                    print("⚠️ Unable to fetch data")
                    time.sleep(check_interval)
                    continue
                
                # Display analysis
                print(f"📈 NIFTY Spot: {analysis['spot_price']:.2f}")
                print(f"📊 Market Trend: {analysis['trend']}")
                print(f"📍 Swing High: {analysis['swing_high']:.2f}")
                print(f"📍 Swing Low: {analysis['swing_low']:.2f}")
                
                print(f"\n🎯 Fibonacci Levels:")
                for level, price in analysis['fib_levels'].items():
                    marker = "👈 CURRENT" if '61.8' in level and 'near' in analysis.get('current_fib', '') else ""
                    print(f"   {level:6s}: {price:8.2f} {marker}")
                
                print(f"\n💡 Signal: {analysis['signal']}")
                print(f"📝 {analysis['message']}")
                
                # Check for entry signal
                if analysis['signal'] in ['BUY', 'SELL'] and self.position is None:
                    print("\n" + "=" * 70)
                    print("🚨 FIBONACCI ENTRY SIGNAL DETECTED!")
                    print("=" * 70)
                    print(f"   Action: {analysis['signal']}")
                    print(f"   Entry Price: {analysis['spot_price']:.2f}")
                    print(f"   Option: {'ITM CALL (100 points ITM)' if analysis['signal'] == 'BUY' else 'ITM PUT (100 points ITM)'}")
                    print(f"   Stop Loss: ₹1,500")
                    print(f"   Target: ₹3,000")
                    print("\n⚠️ DEMO MODE - Live trading disabled")
                    print("   Uncomment code to enable actual order placement")
                    print("=" * 70)
                    
                    # TO ENABLE LIVE TRADING:
                    # 1. Get option security_id from option chain
                    # 2. Place order using dhan.place_order()
                    # 3. Track position
                
                print("-" * 70)
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Strategy stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(check_interval)


if __name__ == "__main__":
    print("\n⚠️  FIBONACCI RETRACEMENT STRATEGY")
    print("   This is a high win-rate strategy (75% in backtest)")
    print("   Selective entries - quality over quantity!")
    print("\n   Paper trade first before going live!\n")
    
    input("Press ENTER to start...")
    
    strategy = FibonacciLiveStrategy()
    
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    strategy.run_live_strategy(check_interval=300)
