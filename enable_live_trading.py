"""
🚀 ENABLE LIVE TRADING - ONE-CLICK ACTIVATION
==============================================

This script will:
1. Verify your Dhan connection
2. Check market hours
3. Enable live trading mode
4. Start the bot

⚠️ RISK ACKNOWLEDGMENT:
- You are trading with REAL MONEY
- You can LOSE your entire capital
- There are NO guarantees
- Use at your own risk

"""

from dhanhq import dhanhq
from creds import client_id, access_token
from datetime import datetime, time
import sys

print("\n" + "="*80)
print("🚀 LIVE TRADING ACTIVATION")
print("="*80)

# ============================================================================
# STEP 1: VERIFY DHAN CONNECTION
# ============================================================================

print("\n📡 Step 1: Verifying Dhan API connection...")

try:
    dhan = dhanhq(client_id, access_token)
    
    # Test connection
    funds = dhan.get_fund_limits()
    
    if funds and 'data' in funds:
        print("✅ Dhan API connected successfully!")
        print(f"   Available Balance: Rs. {funds['data'].get('availabelBalance', 0):,.2f}")
        print(f"   Margin Used: Rs. {funds['data'].get('blockedMargin', 0):,.2f}")
    else:
        print("❌ Connection failed!")
        print("   Check your credentials in creds.py")
        sys.exit(1)

except Exception as e:
    print(f"❌ Connection Error: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Check creds.py has correct client_id and access_token")
    print("   2. Verify IP is whitelisted on Dhan portal")
    print("   3. Check if access token is expired")
    sys.exit(1)

# ============================================================================
# STEP 2: CHECK MARKET HOURS
# ============================================================================

print("\n📅 Step 2: Checking market hours...")

now = datetime.now()
current_time = now.time()
market_start = time(9, 15)
market_end = time(15, 30)

is_market_hours = market_start <= current_time <= market_end

if is_market_hours:
    print(f"✅ Market is OPEN (Current time: {now.strftime('%H:%M:%S')})")
else:
    print(f"⚠️  Market is CLOSED (Current time: {now.strftime('%H:%M:%S')})")
    print(f"   Market hours: 09:15 AM - 03:30 PM")
    
    response = input("\n   Do you want to continue anyway? (yes/no): ").strip().lower()
    if response != 'yes':
        print("   Exiting...")
        sys.exit(0)

# ============================================================================
# STEP 3: RISK ACKNOWLEDGMENT
# ============================================================================

print("\n" + "="*80)
print("⚠️  RISK ACKNOWLEDGMENT")
print("="*80)

print("""
By proceeding, you acknowledge:

1. You are trading with REAL MONEY
2. You can LOSE your ENTIRE capital
3. Past backtests do NOT guarantee future profits
4. The bot may have bugs or fail
5. You are responsible for monitoring positions
6. You understand derivatives trading risks
7. This is NOT investment advice

Expected Performance (based on backtest):
- Annual Profit: Rs. 2,14,348 (with 1 lot)
- Win Rate: 69.74%
- BUT: Live trading results may differ significantly!

Recommended Starting Configuration:
- Start with 1 lot only
- Monitor closely for first week
- Have Rs. 52,000 margin available
- Keep emergency stop ready
""")

print("\n" + "="*80)
confirmation = input("Type 'I UNDERSTAND THE RISKS' to proceed: ").strip()

if confirmation != "I UNDERSTAND THE RISKS":
    print("\n❌ Activation cancelled.")
    sys.exit(0)

# ============================================================================
# STEP 4: ENABLE LIVE TRADING
# ============================================================================

print("\n🔧 Step 4: Enabling live trading mode...")

# Read current file
with open('live_trading_engine_with_trailing.py', 'r') as f:
    content = f.read()

# Check if already enabled
if 'PAPER_TRADING_MODE = False' in content:
    print("✅ Live trading is already enabled!")
else:
    # Enable live trading
    content = content.replace(
        'PAPER_TRADING_MODE = True  # ⚠️ SET TO False FOR LIVE TRADING',
        'PAPER_TRADING_MODE = False  # ✅ LIVE TRADING ENABLED!'
    )
    
    # Also disable confirmation (optional)
    response = input("\n   Disable order confirmations? (bot will trade automatically) (yes/no): ").strip().lower()
    if response == 'yes':
        content = content.replace(
            'REQUIRE_CONFIRMATION = True',
            'REQUIRE_CONFIRMATION = False  # Auto-trading enabled'
        )
    
    # Write back
    with open('live_trading_engine_with_trailing.py', 'w') as f:
        f.write(content)
    
    print("✅ Live trading ENABLED!")

# ============================================================================
# STEP 5: START THE BOT
# ============================================================================

print("\n" + "="*80)
print("🎯 READY TO START LIVE TRADING!")
print("="*80)

print("""
Next Steps:

1. Start the bot:
   python live_trading_engine_with_trailing.py

2. Monitor continuously:
   - Check logs in logs/ folder
   - Watch for trade entries/exits
   - Monitor P&L

3. Emergency Stop:
   - Press Ctrl+C to stop bot
   - Manually exit positions on Dhan app if needed

4. First Day Checklist:
   ✅ Stay near computer
   ✅ Monitor every trade
   ✅ Check SL/Target placement
   ✅ Verify trailing logic works
   ✅ Note any issues

Trading Configuration:
- Lot Size: 65 (current NIFTY lot)
- SL per lot: Rs. 800
- Target per lot: Rs. 1,600
- Trailing after target: 10 points
- Max trades/day: 2
- Strategies: Fibonacci, Candlestick, EMA, S/R
- Confluence: Enabled (multiple strategy confirmation)

""")

response = input("Start the bot now? (yes/no): ").strip().lower()

if response == 'yes':
    print("\n🚀 Starting live trading bot...")
    print("="*80)
    
    import subprocess
    subprocess.run(['python', 'live_trading_engine_with_trailing.py'])
else:
    print("\n✅ Live trading enabled. Start manually when ready:")
    print("   python live_trading_engine_with_trailing.py")

print("\n" + "="*80)
print("💰 GOOD LUCK WITH LIVE TRADING!")
print("="*80)
print("\n⚠️  Remember: Monitor continuously, especially on Day 1!")
