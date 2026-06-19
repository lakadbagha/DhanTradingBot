"""
LIVE TRADING ENGINE - Multi-Strategy NIFTY Options
==================================================
Automatic signal detection, order placement, and position management
Built with comprehensive safety features and risk management

⚠️  IMPORTANT: Start with PAPER_TRADING_MODE = True to test!
"""

from dhanhq import dhanhq, DhanContext
from creds import client_id, access_token
import strategy_config
from datetime import datetime, timedelta, time
import pandas as pd
import time as time_module
import logging
from typing import Dict, List, Optional, Tuple
import os
import threading

# ============================================================================
# CREATE DATE-WISE LOG FILE
# ============================================================================
today_date = datetime.now().strftime('%d%m%y')  # Format: DDMMYY (e.g., 060426)
log_filename = f'trading_log_{today_date}.log'
csv_filename = f'papertrading_{today_date}.csv'

# Configure logging with date-specific file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ],
    force=True  # Override any existing configuration
)

# ============================================================================
# SAFETY CONFIGURATION
# ============================================================================

PAPER_TRADING_MODE = True  # ⚠️ SET TO False ONLY AFTER TESTING!
REQUIRE_CONFIRMATION = True  # Ask before placing each order
EMERGENCY_STOP = False  # Set to True to stop all trading immediately

# ============================================================================
# LIVE TRADING ENGINE
# ============================================================================

class LiveTradingEngine:
    """
    Live Trading Engine with automatic signal detection and order management
    """
    
    def __init__(self):
        """Initialize trading engine"""
        dhan_context = DhanContext(client_id, access_token)
        self.dhan = dhanhq(dhan_context)
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.trades_per_day = strategy_config.TRADES_PER_DAY
        self.max_loss = strategy_config.MAX_LOSS_PER_LOT
        self.target = strategy_config.TARGET_PER_LOT
        self.lot_size = strategy_config.LOT_SIZE
        self.itm_points = strategy_config.ITM_POINTS
        self.max_daily_loss = strategy_config.MAX_DAILY_LOSS

        # Track daily statistics
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.active_positions = {}
        self.order_history = []

        # Threading control
        self.monitoring_active = False
        self.stop_monitoring = False

        # Date-wise CSV file
        self.csv_filename = csv_filename
        self.today_date = today_date
        self.initialize_csv_file()

        self.logger.info("=" * 80)
        self.logger.info("🚀 LIVE TRADING ENGINE INITIALIZED")
        self.logger.info("=" * 80)
        self.logger.info(f"Date: {datetime.now().strftime('%d-%b-%Y')}")
        self.logger.info(f"Log File: {log_filename}")
        self.logger.info(f"Trade Report: {self.csv_filename}")
        self.logger.info(f"Paper Trading Mode: {PAPER_TRADING_MODE}")
        self.logger.info(f"Max Trades Per Day: {self.trades_per_day}")
        self.logger.info(f"SL per lot: Rs.{self.max_loss}")
        self.logger.info(f"Target per lot: Rs.{self.target}")
        self.logger.info(f"Lot Size: {self.lot_size}")
        self.logger.info("=" * 80)

    def initialize_csv_file(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_filename):
            df = pd.DataFrame(columns=[
                'Time',
                'Instrument Name',
                'Entry Price',
                'Exit Price',
                'Profit',
                'Trade Strategy',
                'Signal',
                'Status'
            ])
            df.to_csv(self.csv_filename, index=False)
            self.logger.info(f"✅ Created new trade report: {self.csv_filename}")

    def log_trade_to_csv(self, trade_data: Dict):
        """Log trade to date-wise CSV file"""
        try:
            df = pd.read_csv(self.csv_filename)
            new_row = pd.DataFrame([trade_data])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(self.csv_filename, index=False)
            self.logger.info(f"📝 Trade logged to {self.csv_filename}")
        except Exception as e:
            self.logger.error(f"Error logging trade to CSV: {e}")

    def check_safety_limits(self) -> bool:
        """Check if we should continue trading"""
        if EMERGENCY_STOP:
            self.logger.error("🚨 EMERGENCY STOP ACTIVATED - STOPPING ALL TRADING")
            return False
        
        if self.daily_trades >= self.trades_per_day:
            self.logger.warning(f"⚠️  Daily trade limit reached ({self.trades_per_day})")
            return False
        
        if self.daily_pnl <= -self.max_daily_loss:
            self.logger.error(f"🚨 Daily loss limit reached: Rs.{self.daily_pnl}")
            return False
        
        return True
    
    def get_historical_data(self, days: int = 30) -> pd.DataFrame:
        """Fetch historical NIFTY data"""
        try:
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = self.dhan.historical_daily_data(
                security_id='13',
                exchange_segment='NSE_EQ',
                instrument_type='INDEX',
                from_date=from_date,
                to_date=to_date
            )
            
            if response['status'] == 'success':
                df = pd.DataFrame(response['data']['candles'])
                df.columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
                
                if pd.api.types.is_numeric_dtype(df['timestamp']):
                    df['Date'] = pd.to_datetime(df['timestamp'], unit='s')
                else:
                    df['Date'] = pd.to_datetime(df['timestamp'])
                
                df = df.sort_values('Date')
                
                # Calculate indicators
                df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
                df['SMA_20'] = df['Close'].rolling(window=20).mean()
                
                return df
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
        
        return None
    
    def detect_fibonacci_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """Detect Fibonacci retracement signal"""
        if len(df) < strategy_config.LOOKBACK_PERIOD + 1:
            return None
        
        lookback = strategy_config.LOOKBACK_PERIOD
        recent_data = df.iloc[-(lookback+1):]
        
        # Find swing high/low
        swing_high = recent_data['High'].max()
        swing_low = recent_data['Low'].min()
        
        # Calculate Fibonacci level
        fib_range = swing_high - swing_low
        fib_level = swing_high - (fib_range * strategy_config.FIB_ENTRY_LEVEL)
        
        current_price = df.iloc[-1]['Close']
        
        # Check if price is near Fibonacci level
        if abs(current_price - fib_level) <= strategy_config.FIBONACCI_TOLERANCE:
            # Check trend
            if current_price > df.iloc[-1]['SMA_20']:
                return {
                    'strategy': 'Fibonacci',
                    'type': 'CALL',
                    'signal': 'Fib 61.8% bounce in uptrend',
                    'confidence': 'HIGH'
                }
            elif current_price < df.iloc[-1]['SMA_20']:
                return {
                    'strategy': 'Fibonacci',
                    'type': 'PUT',
                    'signal': 'Fib 61.8% rejection in downtrend',
                    'confidence': 'HIGH'
                }
        
        return None
    
    def detect_candlestick_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """Detect candlestick pattern signal"""
        if len(df) < 2:
            return None
        
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Calculate candle metrics
        body = abs(current['Close'] - current['Open'])
        total = current['High'] - current['Low']
        
        if total == 0:
            return None
        
        # Hammer pattern (bullish)
        if body < (total * 0.3):
            lower_wick = min(current['Open'], current['Close']) - current['Low']
            if lower_wick > (body * 2):
                if current['Close'] > current['SMA_20']:
                    return {
                        'strategy': 'Candlestick',
                        'type': 'CALL',
                        'signal': 'Hammer pattern',
                        'confidence': 'MEDIUM'
                    }
        
        # Shooting Star pattern (bearish)
        if body < (total * 0.3):
            upper_wick = current['High'] - max(current['Open'], current['Close'])
            if upper_wick > (body * 2):
                if current['Close'] < current['SMA_20']:
                    return {
                        'strategy': 'Candlestick',
                        'type': 'PUT',
                        'signal': 'Shooting Star pattern',
                        'confidence': 'MEDIUM'
                    }
        
        return None
    
    def detect_ema_bounce_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """Detect EMA bounce signal"""
        if len(df) < 3:
            return None
        
        current = df.iloc[-1]
        
        # Check if price is near 20 EMA
        if abs(current['Close'] - current['EMA_20']) < 50:
            # Uptrend
            if current['Close'] > current['EMA_50']:
                return {
                    'strategy': 'EMA Bounce',
                    'type': 'CALL',
                    'signal': '20 EMA bounce in uptrend',
                    'confidence': 'HIGH'
                }
            # Downtrend
            elif current['Close'] < current['EMA_50']:
                return {
                    'strategy': 'EMA Bounce',
                    'type': 'PUT',
                    'signal': '20 EMA rejection in downtrend',
                    'confidence': 'HIGH'
                }
        
        return None
    
    def detect_signals(self) -> List[Dict]:
        """Detect all trading signals"""
        signals = []
        
        # Get historical data
        df = self.get_historical_data(30)
        if df is None:
            return signals
        
        # Check each strategy
        if strategy_config.USE_MULTI_STRATEGY:
            # Fibonacci
            fib_signal = self.detect_fibonacci_signal(df)
            if fib_signal:
                signals.append(fib_signal)
            
            # Candlestick
            if strategy_config.ENABLE_CANDLESTICK_PATTERNS:
                candle_signal = self.detect_candlestick_signal(df)
                if candle_signal:
                    signals.append(candle_signal)
            
            # EMA Bounce
            if strategy_config.ENABLE_EMA_BOUNCE:
                ema_signal = self.detect_ema_bounce_signal(df)
                if ema_signal:
                    signals.append(ema_signal)
        
        return signals
    
    def calculate_strike(self, current_price: float, option_type: str) -> int:
        """Calculate option strike price"""
        if option_type == 'CALL':
            strike = round((current_price - self.itm_points) / 50) * 50
        else:  # PUT
            strike = round((current_price + self.itm_points) / 50) * 50
        
        return strike
    
    def place_order(self, signal: Dict, current_price: float) -> Optional[str]:
        """
        Place order with SL and Target (HYBRID SYSTEM)

        Primary Protection: Broker-level SL orders (GTT/OCO)
        Secondary Protection: Script-level monitoring with trailing SL

        Returns: order_id if successful, None otherwise
        """

        # Calculate strike
        strike = self.calculate_strike(current_price, signal['type'])

        # Get option security_id (you need to implement this based on Dhan API)
        # For now, this is a placeholder
        security_id = self.get_option_security_id(strike, signal['type'])

        if security_id is None:
            self.logger.error("Could not find option security_id")
            return None

        # Prepare order details
        order_details = {
            'signal': signal,
            'strike': strike,
            'security_id': security_id,
            'quantity': self.lot_size,
            'type': signal['type']
        }

        self.logger.info("=" * 80)
        self.logger.info("📋 ORDER DETAILS")
        self.logger.info("=" * 80)
        self.logger.info(f"Strategy: {signal['strategy']}")
        self.logger.info(f"Signal: {signal['signal']}")
        self.logger.info(f"Type: {signal['type']}")
        self.logger.info(f"Strike: {strike}")
        self.logger.info(f"Quantity: {self.lot_size}")
        self.logger.info(f"SL per lot: Rs.{self.max_loss}")
        self.logger.info(f"Target per lot: Rs.{self.target}")
        self.logger.info("=" * 80)

        if PAPER_TRADING_MODE:
            self.logger.warning("📝 PAPER TRADING MODE - Order NOT placed")
            self.logger.info("✅ Paper trade logged")
            self.daily_trades += 1

            # Log to CSV file
            trade_data = {
                'Time': datetime.now().strftime('%H:%M:%S'),
                'Instrument Name': f"NIFTY {strike} {signal['type']}",
                'Entry Price': 'SIMULATED',
                'Exit Price': 'PENDING',
                'Profit': 'PENDING',
                'Trade Strategy': signal['strategy'],
                'Signal': signal['signal'],
                'Status': 'PAPER TRADE'
            }
            self.log_trade_to_csv(trade_data)

            # Add to active positions for monitoring (simulated entry at 100)
            paper_order_id = f"PAPER_{self.daily_trades}"
            self.active_positions[paper_order_id] = {
                **order_details,
                'entry_price': 100.0,  # Simulated entry price
                'pnl': 0.0,
                'target_hit': False,
                'max_ltp': 0.0,
                'trailing_sl_active': False
            }

            return paper_order_id

        if REQUIRE_CONFIRMATION:
            confirm = input("\n⚠️  Place this order? (yes/no): ").strip().lower()
            if confirm != 'yes':
                self.logger.info("❌ Order cancelled by user")
                return None

        try:
            # ================================================================
            # STEP 1: Place Main Order
            # ================================================================
            order_response = self.dhan.place_order(
                security_id=security_id,
                exchange_segment='NSE_FNO',
                transaction_type='BUY',
                quantity=self.lot_size,
                order_type='MARKET',
                product_type='INTRADAY',
                validity='DAY'
            )

            if order_response['status'] != 'success':
                self.logger.error(f"❌ Order failed: {order_response}")
                return None

            order_id = order_response['data']['orderId']
            self.logger.info(f"✅ Main order placed! Order ID: {order_id}")

            # Wait for order to execute and get entry price
            time_module.sleep(2)
            order_details_response = self.dhan.get_order_by_id(order_id)

            if order_details_response['status'] != 'success':
                self.logger.error("Failed to get order details")
                return order_id

            entry_price = order_details_response['data'].get('avgPrice', 0)
            if entry_price == 0:
                self.logger.warning("Could not get entry price, using estimate")
                entry_price = 100.0  # Placeholder

            self.logger.info(f"Entry Price: Rs.{entry_price:.2f}")

            # ================================================================
            # STEP 2: Place BROKER-LEVEL SL Order (Primary Protection)
            # ================================================================
            sl_price = entry_price - (self.max_loss / self.lot_size)

            self.logger.info(f"📍 Setting broker-level SL at Rs.{sl_price:.2f}")

            # Try to place SL order (implementation depends on Dhan API)
            try:
                sl_response = self.place_sl_order(
                    security_id=security_id,
                    quantity=self.lot_size,
                    trigger_price=sl_price
                )

                if sl_response:
                    self.logger.info(f"✅ Broker SL order placed: {sl_response}")
                    order_details['broker_sl_order_id'] = sl_response
                else:
                    self.logger.warning("⚠️  Broker SL order failed - using script monitoring only")

            except Exception as e:
                self.logger.warning(f"⚠️  Could not place broker SL: {e}")
                self.logger.warning("   Falling back to script-based SL monitoring")

            # ================================================================
            # STEP 3: Track Position for Script-Level Monitoring
            # ================================================================
            self.daily_trades += 1
            self.active_positions[order_id] = {
                **order_details,
                'entry_price': entry_price,
                'pnl': 0.0,
                'target_hit': False,
                'max_ltp': entry_price,
                'trailing_sl_active': False
            }

            self.logger.info("✅ Position added to monitoring system")

            return order_id

        except Exception as e:
            self.logger.error(f"❌ Error placing order: {e}")
            return None

    def place_sl_order(self, security_id: str, quantity: int, trigger_price: float) -> Optional[str]:
        """
        Place SL order at broker level

        NOTE: Implementation depends on Dhan API capabilities:
        - Option 1: GTT (Good Till Triggered) order
        - Option 2: OCO (One-Cancels-Other) order
        - Option 3: Regular SL-M (Stop Loss Market) order

        Args:
            security_id: Option contract security ID
            quantity: Quantity to sell
            trigger_price: SL trigger price

        Returns:
            order_id if successful, None otherwise
        """
        try:
            # ================================================================
            # METHOD 1: Try GTT Order (if Dhan supports)
            # ================================================================
            # Uncomment when Dhan API documentation is available
            # gtt_response = self.dhan.place_gtt_order(
            #     security_id=security_id,
            #     exchange_segment='NSE_FNO',
            #     transaction_type='SELL',
            #     quantity=quantity,
            #     trigger_price=trigger_price,
            #     order_type='MARKET',
            #     product_type='INTRADAY'
            # )
            # if gtt_response['status'] == 'success':
            #     return gtt_response['data']['orderId']

            # ================================================================
            # METHOD 2: Regular SL-M Order (Stop Loss Market)
            # ================================================================
            sl_response = self.dhan.place_order(
                security_id=security_id,
                exchange_segment='NSE_FNO',
                transaction_type='SELL',
                quantity=quantity,
                order_type='SL-M',  # Stop Loss Market
                trigger_price=trigger_price,
                product_type='INTRADAY',
                validity='DAY'
            )

            if sl_response['status'] == 'success':
                return sl_response['data']['orderId']
            else:
                self.logger.error(f"SL order failed: {sl_response}")
                return None

        except Exception as e:
            self.logger.error(f"Error placing SL order: {e}")
            return None
    
    def get_option_security_id(self, strike: int, option_type: str) -> Optional[str]:
        """
        Get option contract security_id

        Uses manual security_id mapping from security_id_map.py
        Update this file weekly with new expiry contracts
        """
        try:
            # Try to import security_id mapping
            from security_id_map import get_security_id
            security_id = get_security_id(strike, option_type)

            if security_id:
                self.logger.info(f"✅ Found security_id: {security_id} for {strike} {option_type}")
                return security_id
            else:
                self.logger.warning(f"⚠️  Strike {strike} not in security_id map")
                return None

        except ImportError:
            self.logger.error("❌ security_id_map.py not found! Create it first.")
            self.logger.info("   See TESTING_OUTSIDE_MARKET_HOURS.md for instructions")
            return None
        except Exception as e:
            self.logger.error(f"Error getting security_id: {e}")
            return None
    
    def monitor_positions(self):
        """
        Monitor active positions and manage SL/Target with LTP checking

        This is SCRIPT-BASED monitoring that works alongside broker-level SL.
        Features:
        - Real-time LTP tracking
        - P&L calculation
        - Advanced trailing SL after target hit
        - Automatic exit orders
        """
        if not self.active_positions:
            return

        self.logger.info("📊 Monitoring active positions...")

        # Get current positions from Dhan
        try:
            positions = self.dhan.get_positions()
            if positions['status'] != 'success':
                self.logger.error("Failed to fetch positions")
                return

            # Check each active position
            positions_to_close = []

            for order_id, position_info in self.active_positions.items():
                # Find matching position in Dhan response
                dhan_position = None
                for pos in positions['data']:
                    # Match by security_id or order details
                    if pos.get('securityId') == position_info['security_id']:
                        dhan_position = pos
                        break

                if not dhan_position:
                    self.logger.warning(f"Position {order_id} not found in Dhan positions")
                    continue

                # Get current LTP (Last Traded Price)
                ltp = dhan_position.get('ltp', 0)
                if ltp == 0:
                    self.logger.warning(f"Invalid LTP for position {order_id}")
                    continue

                # Get entry price and quantity
                entry_price = position_info.get('entry_price', dhan_position.get('avgPrice', 0))
                quantity = position_info['quantity']

                # Calculate P&L
                if position_info['type'] == 'CALL' or position_info['type'] == 'PUT':
                    # For options: (Current Price - Entry Price) * Quantity
                    pnl = (ltp - entry_price) * quantity
                else:
                    pnl = 0

                # Update position info
                position_info['current_ltp'] = ltp
                position_info['pnl'] = pnl

                self.logger.info(f"Position {order_id}: LTP={ltp:.2f}, Entry={entry_price:.2f}, P&L=Rs.{pnl:.2f}")

                # Check SL hit (LOSS)
                if pnl <= -self.max_loss:
                    self.logger.warning(f"🚨 SL HIT for {order_id}: P&L=Rs.{pnl:.2f} (Max Loss: Rs.{self.max_loss})")
                    positions_to_close.append((order_id, 'SL_HIT', ltp))
                    continue

                # Check Target hit (PROFIT)
                if pnl >= self.target:
                    if not position_info.get('target_hit', False):
                        self.logger.info(f"🎯 TARGET HIT for {order_id}: P&L=Rs.{pnl:.2f}")
                        position_info['target_hit'] = True
                        position_info['max_ltp'] = ltp
                        position_info['trailing_sl_active'] = True
                        self.logger.info(f"✅ Trailing SL activated with 10-point trail")

                    # Update max LTP for trailing
                    if ltp > position_info.get('max_ltp', 0):
                        position_info['max_ltp'] = ltp

                    # Check trailing SL (10 points from max)
                    max_ltp = position_info['max_ltp']
                    trailing_sl_price = max_ltp - 10

                    if ltp <= trailing_sl_price:
                        self.logger.info(f"📉 TRAILING SL HIT for {order_id}: LTP={ltp:.2f}, Max={max_ltp:.2f}")
                        positions_to_close.append((order_id, 'TRAILING_SL', ltp))
                        continue

            # Close positions that hit SL/Target
            for order_id, exit_reason, exit_price in positions_to_close:
                self.close_position(order_id, exit_reason, exit_price)

        except Exception as e:
            self.logger.error(f"Error monitoring positions: {e}")

    def close_position(self, order_id: str, exit_reason: str, exit_price: float):
        """
        Close a position and log the result

        Args:
            order_id: Order ID to close
            exit_reason: 'SL_HIT', 'TARGET_HIT', 'TRAILING_SL'
            exit_price: Exit price
        """
        if order_id not in self.active_positions:
            self.logger.error(f"Position {order_id} not found")
            return

        position_info = self.active_positions[order_id]

        self.logger.info("=" * 80)
        self.logger.info(f"🔴 CLOSING POSITION: {order_id}")
        self.logger.info("=" * 80)
        self.logger.info(f"Exit Reason: {exit_reason}")
        self.logger.info(f"Exit Price: Rs.{exit_price:.2f}")
        self.logger.info(f"P&L: Rs.{position_info['pnl']:.2f}")
        self.logger.info("=" * 80)

        if PAPER_TRADING_MODE:
            self.logger.warning("📝 PAPER TRADING - Exit logged (order not placed)")

            # Update CSV with exit details
            try:
                df = pd.read_csv(self.csv_filename)
                # Find the row to update (last row with matching instrument)
                instrument_name = f"NIFTY {position_info['strike']} {position_info['type']}"
                mask = df['Instrument Name'] == instrument_name
                if mask.any():
                    df.loc[mask, 'Exit Price'] = f"{exit_price:.2f}"
                    df.loc[mask, 'Profit'] = f"{position_info['pnl']:.2f}"
                    df.loc[mask, 'Status'] = exit_reason
                    df.to_csv(self.csv_filename, index=False)
                    self.logger.info(f"📝 Updated trade in {self.csv_filename}")
            except Exception as e:
                self.logger.error(f"Error updating CSV: {e}")

            # Update daily P&L
            self.daily_pnl += position_info['pnl']
        else:
            # Place exit order for real trading
            try:
                exit_response = self.dhan.place_order(
                    security_id=position_info['security_id'],
                    exchange_segment='NSE_FNO',
                    transaction_type='SELL',
                    quantity=position_info['quantity'],
                    order_type='MARKET',
                    product_type='INTRADAY',
                    validity='DAY'
                )

                if exit_response['status'] == 'success':
                    self.logger.info(f"✅ Exit order placed: {exit_response['data']['orderId']}")
                    self.daily_pnl += position_info['pnl']
                else:
                    self.logger.error(f"❌ Exit order failed: {exit_response}")

            except Exception as e:
                self.logger.error(f"❌ Error placing exit order: {e}")

        # Remove from active positions
        del self.active_positions[order_id]
        self.logger.info(f"✅ Position {order_id} closed")

    def continuous_position_monitoring(self):
        """
        FAST MONITORING THREAD - Runs every 5 seconds
        Checks SL/Target hits continuously

        NOTE: This is backup monitoring. Ideally, SL/Target should be 
        set at broker level using bracket orders or GTT orders.
        """
        self.logger.info("🔄 Starting continuous position monitoring (every 5 seconds)")

        while not self.stop_monitoring:
            try:
                if self.active_positions:
                    self.monitor_positions()

                # Wait 5 seconds before next check
                time_module.sleep(5)

            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                time_module.sleep(5)

        self.logger.info("⏹️  Stopped continuous position monitoring")
    
    def run_trading_session(self):
        """Main trading loop"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🚀 STARTING TRADING SESSION")
        self.logger.info("=" * 80)

        # Check market hours
        now = datetime.now().time()
        market_open = time(9, 15)
        market_close = time(15, 30)

        if not (market_open <= now <= market_close):
            self.logger.warning("⚠️  Market is closed")
            return

        # Start continuous position monitoring in separate thread
        monitoring_thread = threading.Thread(
            target=self.continuous_position_monitoring,
            daemon=True
        )
        monitoring_thread.start()
        self.monitoring_active = True

        while True:
            try:
                # Check safety limits
                if not self.check_safety_limits():
                    break

                # SIGNAL DETECTION (Every 5 minutes)
                self.logger.info("\n🔍 Scanning for new signals...")
                signals = self.detect_signals()

                if signals:
                    self.logger.info(f"\n🎯 Found {len(signals)} signal(s)")

                    # Take first signal (priority based)
                    for signal in signals[:self.trades_per_day - self.daily_trades]:
                        # Get current NIFTY price
                        df = self.get_historical_data(5)
                        if df is not None:
                            current_price = df.iloc[-1]['Close']

                            # Place order
                            order_id = self.place_order(signal, current_price)

                            if order_id:
                                self.logger.info(f"✅ Trade executed: {order_id}")
                else:
                    self.logger.info("ℹ️  No signals detected")

                # Wait before next scan (5 minutes)
                self.logger.info("\n⏳ Waiting 5 minutes before next signal scan...")
                self.logger.info("   (Position monitoring continues every 5 seconds)")
                time_module.sleep(300)

            except KeyboardInterrupt:
                self.logger.info("\n⚠️  Trading stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                time_module.sleep(60)

        # Stop monitoring thread
        self.stop_monitoring = True
        self.logger.info("⏹️  Stopping position monitoring...")
        time_module.sleep(2)  # Wait for thread to stop

        self.logger.info("\n" + "=" * 80)
        self.logger.info("📊 END OF DAY SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Date: {datetime.now().strftime('%d-%b-%Y')}")
        self.logger.info(f"Total Trades: {self.daily_trades}")
        self.logger.info(f"Daily P&L: Rs.{self.daily_pnl:,.2f}")
        self.logger.info(f"Trade Report: {self.csv_filename}")
        self.logger.info(f"Log File: {log_filename}")
        self.logger.info("=" * 80)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 LIVE TRADING ENGINE")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%d-%b-%Y (%A)')}")
    print(f"📁 Log File: {log_filename}")
    print(f"📊 Trade Report: {csv_filename}")
    print(f"\n⚠️  PAPER TRADING MODE: {PAPER_TRADING_MODE}")

    if not PAPER_TRADING_MODE:
        print("\n🚨 WARNING: You are about to trade with REAL MONEY!")
        print("   Have you tested with paper trading first?")
        confirm = input("\n   Type 'I UNDERSTAND THE RISKS' to proceed: ")
        if confirm != "I UNDERSTAND THE RISKS":
            print("\n❌ Exiting for safety")
            exit()

    # Create engine
    engine = LiveTradingEngine()

    # Start trading
    engine.run_trading_session()
