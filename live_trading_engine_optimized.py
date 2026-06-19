"""
OPTIMIZED LIVE TRADING ENGINE
==============================
Based on Dhan library source code analysis
Improvements:
1. Bracket Orders (BO) for automatic SL/Target
2. Correlation IDs for order tracking
3. Proper error handling from library
4. Optimized position monitoring
5. Security ID integration from security_id_map.py
"""

from dhanhq import dhanhq, DhanContext
from creds import client_id, access_token
import strategy_config
from datetime import datetime, timedelta, time
import pandas as pd
import time as time_module
import logging
from typing import Dict, List, Optional
import os
import threading

# ============================================================================
# CONFIGURATION
# ============================================================================

today_date = datetime.now().strftime('%d%m%y')
log_filename = f'trading_log_{today_date}.log'
csv_filename = f'livetrading_{today_date}.csv'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ],
    force=True
)

# SAFETY FLAGS
PAPER_TRADING_MODE = True  # ⚠️ SET TO False FOR LIVE TRADING
REQUIRE_CONFIRMATION = True
EMERGENCY_STOP = False

# ============================================================================
# OPTIMIZED LIVE TRADING ENGINE
# ============================================================================

class OptimizedLiveTradingEngine:
    """
    Enhanced trading engine with Dhan API optimizations
    """
    
    def __init__(self):
        """Initialize engine with all optimizations"""
        dhan_context = DhanContext(client_id, access_token)
        self.dhan = dhanhq(dhan_context)
        self.logger = logging.getLogger(__name__)
        
        # Load config
        self.trades_per_day = strategy_config.TRADES_PER_DAY
        self.max_loss = strategy_config.MAX_LOSS_PER_LOT
        self.target = strategy_config.TARGET_PER_LOT
        self.lot_size = strategy_config.LOT_SIZE
        self.itm_points = strategy_config.ITM_POINTS
        
        # State tracking
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.active_positions = {}
        self.stop_monitoring = False
        
        # CSV file
        self.csv_filename = csv_filename
        self.initialize_csv()
        
        self.logger.info("=" * 80)
        self.logger.info("🚀 OPTIMIZED LIVE TRADING ENGINE")
        self.logger.info("=" * 80)
        self.logger.info(f"Mode: {'PAPER' if PAPER_TRADING_MODE else '🔴 LIVE'}")
        self.logger.info(f"Date: {datetime.now().strftime('%d-%b-%Y')}")
        self.logger.info(f"Max Trades: {self.trades_per_day}/day")
        self.logger.info(f"SL: Rs.{self.max_loss} | Target: Rs.{self.target}")
        self.logger.info("=" * 80)
    
    def initialize_csv(self):
        """Create CSV for trade logging"""
        if not os.path.exists(self.csv_filename):
            df = pd.DataFrame(columns=[
                'Time', 'Instrument', 'Entry', 'Exit', 'Profit', 
                'Strategy', 'Signal', 'Status', 'OrderID'
            ])
            df.to_csv(self.csv_filename, index=False)
    
    def get_option_security_id(self, strike: int, option_type: str) -> Optional[str]:
        """
        Get security_id from security_id_map.py
        """
        try:
            from security_id_map import get_security_id
            security_id = get_security_id(strike, option_type)
            
            if security_id:
                self.logger.info(f"✅ Found security_id: {security_id} for {strike} {option_type}")
                return security_id
            else:
                self.logger.warning(f"⚠️  Strike {strike} not in security map")
                return None
                
        except ImportError:
            self.logger.error("❌ security_id_map.py not found!")
            self.logger.info("   Run: python get_all_security_ids.py")
            self.logger.info("   Then: python create_security_map.py")
            return None
        except Exception as e:
            self.logger.error(f"Error getting security_id: {e}")
            return None
    
    def calculate_strike(self, current_price: float, option_type: str) -> int:
        """Calculate ITM strike"""
        if option_type == 'CALL':
            strike = round((current_price - self.itm_points) / 50) * 50
        else:
            strike = round((current_price + self.itm_points) / 50) * 50
        return strike
    
    def fetch_nifty_data(self) -> Optional[pd.DataFrame]:
        """Fetch NIFTY historical data"""
        try:
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            
            response = self.dhan.historical_daily_data(
                security_id='13',
                exchange_segment='NSE_EQ',
                instrument_type='INDEX',
                from_date=from_date,
                to_date=to_date
            )
            
            if response['status'] == 'success':
                df = pd.DataFrame(response['data'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                return df
            else:
                self.logger.error(f"Failed to fetch data: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return None
    
    def detect_signals(self) -> List[Dict]:
        """Detect trading signals (simplified for now)"""
        signals = []
        
        df = self.fetch_nifty_data()
        if df is None or len(df) < 20:
            return signals
        
        current_price = df.iloc[-1]['close']
        
        # Calculate indicators
        df['EMA_20'] = df['close'].ewm(span=20).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        
        # Simple trend-following signal
        if current_price > df.iloc[-1]['SMA_20']:
            # Uptrend - look for CALL
            signals.append({
                'strategy': 'Trend',
                'type': 'CALL',
                'signal': 'Price above SMA 20',
                'confidence': 'MEDIUM'
            })
        
        return signals
    
    def place_order_with_bracket(self, signal: Dict, current_price: float) -> Optional[str]:
        """
        Place order with BRACKET ORDERS (BO) for automatic SL/Target
        This uses Dhan's bo_profit_value and bo_stop_loss_Value parameters
        """
        
        # Calculate strike and get security_id
        strike = self.calculate_strike(current_price, signal['type'])
        security_id = self.get_option_security_id(strike, signal['type'])
        
        if security_id is None:
            self.logger.error("Cannot place order without security_id")
            return None
        
        # Calculate SL and Target in premium terms
        sl_value = self.max_loss / self.lot_size  # Per unit SL
        target_value = self.target / self.lot_size  # Per unit target
        
        order_details = {
            'signal': signal,
            'strike': strike,
            'security_id': security_id,
            'quantity': self.lot_size,
            'type': signal['type']
        }
        
        self.logger.info("=" * 80)
        self.logger.info("📋 ORDER PLACEMENT")
        self.logger.info("=" * 80)
        self.logger.info(f"Strategy: {signal['strategy']}")
        self.logger.info(f"Strike: {strike} {signal['type']}")
        self.logger.info(f"Security ID: {security_id}")
        self.logger.info(f"Quantity: {self.lot_size}")
        self.logger.info(f"SL Value: Rs.{sl_value:.2f}")
        self.logger.info(f"Target Value: Rs.{target_value:.2f}")
        self.logger.info("=" * 80)
        
        # PAPER TRADING MODE
        if PAPER_TRADING_MODE:
            self.logger.warning("📝 PAPER TRADING - No real order placed")
            paper_order_id = f"PAPER_{self.daily_trades + 1}"
            self.active_positions[paper_order_id] = {
                **order_details,
                'entry_price': 100.0,
                'pnl': 0.0,
                'target_hit': False
            }
            self.daily_trades += 1
            self.log_trade(order_details, 100.0, 'PAPER')
            return paper_order_id
        
        # CONFIRMATION
        if REQUIRE_CONFIRMATION:
            confirm = input("\n⚠️  Place this order? (yes/no): ").strip().lower()
            if confirm != 'yes':
                self.logger.info("❌ Order cancelled by user")
                return None
        
        try:
            # OPTIMIZED: Use Bracket Order with SL/Target
            self.logger.info("📤 Placing BRACKET order...")
            
            # Create correlation ID for tracking
            correlation_id = f"{signal['strategy']}_{datetime.now().strftime('%H%M%S')}"
            
            response = self.dhan.place_order(
                security_id=security_id,
                exchange_segment='NSE_FNO',
                transaction_type='BUY',
                quantity=self.lot_size,
                order_type='MARKET',
                product_type='INTRADAY',
                price=0,  # Required even for MARKET
                validity='DAY',
                # BRACKET ORDER PARAMETERS (from Dhan library)
                bo_profit_value=target_value,  # Target
                bo_stop_loss_Value=sl_value,  # SL
                tag=correlation_id  # Track this order
            )
            
            if response.get('status') == 'success':
                order_id = response['data']['orderId']
                self.logger.info(f"✅ BRACKET ORDER PLACED!")
                self.logger.info(f"   Order ID: {order_id}")
                self.logger.info(f"   Correlation ID: {correlation_id}")
                self.logger.info(f"   SL/Target set at broker level")
                
                # Wait and get entry price
                time_module.sleep(2)
                order_status = self.dhan.get_order_by_id(order_id)
                
                entry_price = 100.0  # Default
                if order_status.get('status') == 'success':
                    entry_price = order_status['data'].get('avgPrice', 100.0)
                
                # Track position
                self.active_positions[order_id] = {
                    **order_details,
                    'entry_price': entry_price,
                    'pnl': 0.0,
                    'target_hit': False,
                    'correlation_id': correlation_id
                }
                
                self.daily_trades += 1
                self.log_trade(order_details, entry_price, order_id)
                
                return order_id
            else:
                self.logger.error(f"❌ Order failed: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error placing order: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def log_trade(self, order_details: Dict, entry_price: float, order_id: str):
        """Log trade to CSV"""
        trade_data = {
            'Time': datetime.now().strftime('%H:%M:%S'),
            'Instrument': f"NIFTY {order_details['strike']} {order_details['type']}",
            'Entry': entry_price,
            'Exit': 'PENDING',
            'Profit': 'PENDING',
            'Strategy': order_details['signal']['strategy'],
            'Signal': order_details['signal']['signal'],
            'Status': 'ACTIVE',
            'OrderID': order_id
        }
        
        df = pd.read_csv(self.csv_filename)
        df = pd.concat([df, pd.DataFrame([trade_data])], ignore_index=True)
        df.to_csv(self.csv_filename, index=False)
    
    def monitor_positions(self):
        """Monitor positions with LTP tracking"""
        if not self.active_positions:
            return
        
        self.logger.info("📊 Monitoring positions...")
        
        try:
            positions = self.dhan.get_positions()
            
            if positions.get('status') != 'success':
                return
            
            dhan_positions = positions.get('data', [])
            
            for order_id, position_info in list(self.active_positions.items()):
                # For paper trading, simulate monitoring
                if order_id.startswith('PAPER_'):
                    continue
                
                # Find position in Dhan response
                dhan_pos = None
                for pos in dhan_positions:
                    if pos.get('drvOrderId') == order_id or pos.get('exchangeOrderId') == order_id:
                        dhan_pos = pos
                        break
                
                if dhan_pos:
                    ltp = dhan_pos.get('lastPrice', position_info['entry_price'])
                    pnl = (ltp - position_info['entry_price']) * position_info['quantity']
                    
                    self.logger.info(f"Position {order_id}: LTP={ltp}, P&L=Rs.{pnl:.2f}")
                    
                    # Update position
                    self.active_positions[order_id]['pnl'] = pnl
                    self.active_positions[order_id]['current_ltp'] = ltp
                
        except Exception as e:
            self.logger.error(f"Error monitoring: {e}")
    
    def run_trading_session(self):
        """Main trading loop"""
        self.logger.info("\n🚀 STARTING TRADING SESSION")
        
        # Check market hours
        now = datetime.now().time()
        if not (time(9, 15) <= now <= time(15, 30)):
            self.logger.warning("⚠️  Market is closed")
            self.logger.info("   Market hours: 9:15 AM - 3:30 PM")
            return
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self.continuous_monitoring,
            daemon=True
        )
        monitor_thread.start()
        
        # Main loop
        while True:
            try:
                if EMERGENCY_STOP:
                    self.logger.warning("🛑 EMERGENCY STOP ACTIVATED")
                    break
                
                if self.daily_trades >= self.trades_per_day:
                    self.logger.info(f"✅ Daily trade limit reached ({self.trades_per_day})")
                    break
                
                # Detect signals
                self.logger.info("\n🔍 Scanning for signals...")
                df = self.fetch_nifty_data()
                
                if df is not None and len(df) > 0:
                    current_price = df.iloc[-1]['close']
                    self.logger.info(f"   NIFTY: Rs.{current_price:.2f}")
                    
                    signals = self.detect_signals()
                    
                    if signals:
                        for signal in signals[:1]:  # One signal at a time
                            self.logger.info(f"\n📢 SIGNAL DETECTED: {signal['strategy']}")
                            self.place_order_with_bracket(signal, current_price)
                            time_module.sleep(5)
                    else:
                        self.logger.info("   No signals detected")
                else:
                    self.logger.warning("   Could not fetch data")
                
                # Wait before next scan
                self.logger.info("\n⏳ Waiting 5 minutes...")
                time_module.sleep(300)
                
            except KeyboardInterrupt:
                self.logger.info("\n⚠️  Stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time_module.sleep(60)
        
        self.stop_monitoring = True
        self.logger.info("\n📊 END OF SESSION")
        self.logger.info(f"Total Trades: {self.daily_trades}")
        self.logger.info(f"Daily P&L: Rs.{self.daily_pnl:,.2f}")
    
    def continuous_monitoring(self):
        """Continuous position monitoring (5-second loop)"""
        self.logger.info("🔄 Position monitoring started")
        
        while not self.stop_monitoring:
            try:
                if self.active_positions:
                    self.monitor_positions()
                time_module.sleep(5)
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time_module.sleep(5)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 OPTIMIZED LIVE TRADING ENGINE")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%d-%b-%Y (%A)')}")
    print(f"📁 Log: {log_filename}")
    print(f"📊 Trades: {csv_filename}")
    print(f"\n⚠️  PAPER MODE: {PAPER_TRADING_MODE}")
    
    if not PAPER_TRADING_MODE:
        print("\n🚨 WARNING: LIVE TRADING MODE!")
        print("   Real money will be used!")
        confirm = input("\n   Type 'I UNDERSTAND THE RISKS' to proceed: ")
        if confirm != "I UNDERSTAND THE RISKS":
            print("\n❌ Exiting for safety")
            exit()
    
    engine = OptimizedLiveTradingEngine()
    engine.run_trading_session()
