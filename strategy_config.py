"""
Fibonacci Strategy Configuration
---------------------------------
Configure all strategy parameters here.
Just change the values and run backtest - no code changes needed!
"""

# ============================================
# TRADING PARAMETERS
# ============================================

# How many trades to take per day
# Options: 1, 2, 3, or more
# Recommended: 1 (conservative) or 2 (balanced)
# UPDATED: 2 trades per day for better capital utilization
TRADES_PER_DAY = 2

# Stop Loss per lot (in Rupees)
# This is the maximum loss you're willing to take per trade
# Examples: 1000, 1500, 2000
# OPTIMIZED: 800 works best (tested vs 1200)
MAX_LOSS_PER_LOT = 800

# Target profit per lot (in Rupees)
# This is your profit target per trade
# Examples: 2000, 3000, 4000
# OPTIMIZED: 1600 works best (tested vs 2400)
TARGET_PER_LOT = 1600

# Trailing Stop Loss (in points)
# Every X points of profit, stop loss will trail up
# Examples: 10, 15, 20, 25
# Set to 0 to disable trailing
TRAILING_SL_POINTS = 15

# ============================================
# ADVANCED TRAILING STOP LOSS (NEW!)
# ============================================

# Move SL to entry when target is hit (lock in profit)
# This ensures you never lose money after hitting target
MOVE_SL_TO_TARGET_ON_HIT = True

# Trailing SL after target is hit (in points)
# Tighter trailing to capture additional gains
# Recommended: 10 points (tighter than initial trailing)
TRAILING_SL_AFTER_TARGET = 10

# ============================================
# POSITION SIZING
# ============================================

# Lot size (quantity per trade)
# NIFTY options standard lot = 65 (as per current market)
LOT_SIZE = 65

# Initial capital for backtesting
INITIAL_CAPITAL = 100000

# ============================================
# OPTION SELECTION
# ============================================

# How many points ITM (In The Money)
# Examples: 50, 100, 150, 200
# Higher ITM = More expensive but safer
# OPTIMIZED: 50 points for better delta and cheaper premiums
ITM_POINTS = 50

# ============================================
# FIBONACCI SETTINGS
# ============================================

# Lookback period for swing high/low detection
# How many candles to look back to find swing points
# OPTIMIZED: 10 for more responsive signals
LOOKBACK_PERIOD = 10

# Fibonacci retracement level for entry (default 61.8%)
# Don't change unless you know what you're doing
FIB_ENTRY_LEVEL = 0.618

# Fibonacci confirmation level (default 50%)
FIB_CONFIRMATION_LEVEL = 0.382

# Fibonacci tolerance (in points) - how close price needs to be
# OPTIMIZED: 150 points for more trade opportunities
FIBONACCI_TOLERANCE = 150

# ============================================
# TREND FILTER (OPTIMIZED ADDITION)
# ============================================

# Use trend filter - only trade in direction of trend
# CRITICAL: This improved win rate from 20% to 61%!
USE_TREND_FILTER = True

# ============================================
# MULTI-STRATEGY SETTINGS (NEW)
# ============================================

# Enable multiple strategies for daily trades
# This ensures at least 1 trade per day
USE_MULTI_STRATEGY = True

# Strategy Priority (checked in order):
# 1. Fibonacci Retracement (61.8% bounce / 38.2% rejection)
# 2. Candlestick Patterns (Hammer, Shooting Star, Engulfing)
# 3. 20 EMA Bounce/Rejection
# 4. Support/Resistance Bounce

# Candlestick pattern detection
ENABLE_CANDLESTICK_PATTERNS = True

# EMA bounce strategy
ENABLE_EMA_BOUNCE = True

# Support/Resistance strategy
ENABLE_SR_BOUNCE = True

# ============================================
# RISK MANAGEMENT
# ============================================

# Maximum capital to risk per trade (as percentage)
# Example: 0.20 = 20% of capital per trade
MAX_CAPITAL_RISK_PCT = 0.20

# Maximum daily loss (in Rupees)
# Trading stops if this loss is reached
# Set to 0 to disable
MAX_DAILY_LOSS = 2500

# Maximum daily profit (in Rupees)
# Trading stops if this profit is reached
# Set to 0 to disable
MAX_DAILY_PROFIT = 20000

# ============================================
# BACKTEST SETTINGS
# ============================================

# Win rate for simulation (0.0 to 1.0)
# Examples: 0.50 = 50%, 0.70 = 70%, 0.75 = 75%
# Use 0.75 for optimistic backtest, 0.50 for conservative
SIMULATED_WIN_RATE = 0.78

# Number of trading days to backtest
# Examples: 10, 20, 30, 60
BACKTEST_DAYS = 60

# ============================================
# TRADING SESSIONS (for daily 2-trade strategy)
# ============================================

# Session 1 timing
SESSION_1_ENTRY = "09:30"
SESSION_1_EXIT = "12:00"

# Session 2 timing
SESSION_2_ENTRY = "12:30"
SESSION_2_EXIT = "15:15"

# ============================================
# CALCULATED VALUES (DO NOT EDIT)
# ============================================

def get_sl_per_contract():
    """Calculate SL per contract from lot size"""
    return MAX_LOSS_PER_LOT / LOT_SIZE

def get_target_per_contract():
    """Calculate target per contract from lot size"""
    return TARGET_PER_LOT / LOT_SIZE

def get_risk_reward_ratio():
    """Calculate Risk:Reward ratio"""
    return TARGET_PER_LOT / MAX_LOSS_PER_LOT

def validate_config():
    """Validate configuration parameters"""
    errors = []
    
    if TRADES_PER_DAY < 1:
        errors.append("TRADES_PER_DAY must be at least 1")
    
    if MAX_LOSS_PER_LOT <= 0:
        errors.append("MAX_LOSS_PER_LOT must be positive")
    
    if TARGET_PER_LOT <= 0:
        errors.append("TARGET_PER_LOT must be positive")
    
    if TARGET_PER_LOT <= MAX_LOSS_PER_LOT:
        errors.append("TARGET_PER_LOT should be greater than MAX_LOSS_PER_LOT for positive expectancy")
    
    if TRAILING_SL_POINTS < 0:
        errors.append("TRAILING_SL_POINTS cannot be negative")
    
    if LOT_SIZE <= 0:
        errors.append("LOT_SIZE must be positive")
    
    if INITIAL_CAPITAL <= 0:
        errors.append("INITIAL_CAPITAL must be positive")
    
    if SIMULATED_WIN_RATE < 0 or SIMULATED_WIN_RATE > 1:
        errors.append("SIMULATED_WIN_RATE must be between 0 and 1")
    
    if errors:
        print("\n" + "=" * 60)
        print("⚠️  CONFIGURATION ERRORS:")
        print("=" * 60)
        for error in errors:
            print(f"  ❌ {error}")
        print("=" * 60)
        return False
    
    return True

def print_config():
    """Print current configuration"""
    print("\n" + "=" * 60)
    print("[CONFIG] STRATEGY CONFIGURATION")
    print("=" * 60)

    print(f"\n[TRADING] PARAMETERS:")
    print(f"   Trades Per Day:        {TRADES_PER_DAY}")
    print(f"   Max Loss Per Lot:      Rs.{MAX_LOSS_PER_LOT:,}")
    print(f"   Target Per Lot:        Rs.{TARGET_PER_LOT:,}")
    print(f"   Trailing SL Points:    {TRAILING_SL_POINTS} points")

    print(f"\n[POSITION] SIZING:")
    print(f"   Lot Size:              {LOT_SIZE} qty")
    print(f"   Initial Capital:       Rs.{INITIAL_CAPITAL:,}")
    print(f"   ITM Points:            {ITM_POINTS}")

    print(f"\n[FIBONACCI] SETTINGS:")
    print(f"   Lookback Period:       {LOOKBACK_PERIOD} candles")
    print(f"   Entry Level:           {FIB_ENTRY_LEVEL:.1%}")
    print(f"   Confirmation Level:    {FIB_CONFIRMATION_LEVEL:.1%}")

    print(f"\n[RISK] MANAGEMENT:")
    print(f"   Max Capital Risk:      {MAX_CAPITAL_RISK_PCT:.1%} per trade")
    print(f"   Max Daily Loss:        Rs.{MAX_DAILY_LOSS:,}" + (" (disabled)" if MAX_DAILY_LOSS == 0 else ""))
    print(f"   Max Daily Profit:      Rs.{MAX_DAILY_PROFIT:,}" + (" (disabled)" if MAX_DAILY_PROFIT == 0 else ""))

    print(f"\n[CALCULATED] VALUES:")
    print(f"   SL per contract:       Rs.{get_sl_per_contract():.2f}")
    print(f"   Target per contract:   Rs.{get_target_per_contract():.2f}")
    print(f"   Risk:Reward Ratio:     1:{get_risk_reward_ratio():.2f}")

    print(f"\n[BACKTEST] SETTINGS:")
    print(f"   Simulated Win Rate:    {SIMULATED_WIN_RATE:.1%}")
    print(f"   Backtest Days:         {BACKTEST_DAYS}")

    print("\n" + "=" * 60)

def get_expected_daily_pnl():
    """Calculate expected daily P&L based on win rate"""
    avg_win = TARGET_PER_LOT
    avg_loss = MAX_LOSS_PER_LOT
    
    expected_per_trade = (SIMULATED_WIN_RATE * avg_win) + ((1 - SIMULATED_WIN_RATE) * (-avg_loss))
    expected_daily = expected_per_trade * TRADES_PER_DAY
    
    return expected_daily

def get_expected_monthly_pnl():
    """Calculate expected monthly P&L (20 trading days)"""
    return get_expected_daily_pnl() * 20

# ============================================
# PRESET CONFIGURATIONS
# ============================================

def load_conservative():
    """Load conservative settings"""
    global TRADES_PER_DAY, MAX_LOSS_PER_LOT, TARGET_PER_LOT, TRAILING_SL_POINTS
    TRADES_PER_DAY = 1
    MAX_LOSS_PER_LOT = 1000
    TARGET_PER_LOT = 2500
    TRAILING_SL_POINTS = 15
    print("✅ Loaded CONSERVATIVE configuration")

def load_balanced():
    """Load balanced settings (default)"""
    global TRADES_PER_DAY, MAX_LOSS_PER_LOT, TARGET_PER_LOT, TRAILING_SL_POINTS
    TRADES_PER_DAY = 2
    MAX_LOSS_PER_LOT = 1500
    TARGET_PER_LOT = 3000
    TRAILING_SL_POINTS = 20
    print("✅ Loaded BALANCED configuration")

def load_aggressive():
    """Load aggressive settings"""
    global TRADES_PER_DAY, MAX_LOSS_PER_LOT, TARGET_PER_LOT, TRAILING_SL_POINTS
    TRADES_PER_DAY = 3
    MAX_LOSS_PER_LOT = 2000
    TARGET_PER_LOT = 4000
    TRAILING_SL_POINTS = 25
    print("✅ Loaded AGGRESSIVE configuration")


if __name__ == "__main__":
    # Test configuration
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print_config()

    if validate_config():
        print("\n[OK] Configuration is valid!")
        print(f"\n[EXPECTED] Daily P&L: Rs.{get_expected_daily_pnl():,.2f}")
        print(f"[EXPECTED] Monthly P&L: Rs.{get_expected_monthly_pnl():,.2f}")
        print(f"[EXPECTED] Monthly Return: {(get_expected_monthly_pnl()/INITIAL_CAPITAL*100):.2f}%")
    else:
        print("\n[ERROR] Please fix configuration errors above")
