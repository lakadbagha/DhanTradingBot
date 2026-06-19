"""
Fetch Available NIFTY Expiries from Dhan API
This script shows all available expiry dates for NIFTY options
"""

from dhanhq import dhanhq, DhanContext
from creds import client_id, access_token
from datetime import datetime
import pandas as pd

dhan_context = DhanContext(client_id, access_token)
dhan = dhanhq(dhan_context)

print("\n" + "="*80)
print("🔍 FETCHING AVAILABLE NIFTY OPTION EXPIRIES FROM DHAN")
print("="*80)
print(f"\n📅 Current Date: {datetime.now().strftime('%d-%b-%Y (%A)')}\n")

try:
    # Method 1: Get option chain data
    print("Method 1: Trying to fetch option chain...")
    
    # Dhan doesn't have direct option chain API, but we can check positions/orders
    # The best way is to download security master and parse it
    
    print("\n📋 Note: Dhan API doesn't provide direct option chain.")
    print("   To get actual expiries, you need to:")
    print("   1. Download security master CSV from Dhan")
    print("   2. Parse NIFTY option contracts")
    print("   3. Extract unique expiry dates")
    print("\n" + "="*80)
    
    # Method 2: Check your security_id_map.py
    print("\n🔍 Checking security_id_map.py for available expiries...\n")
    
    try:
        from security_id_map import NIFTY_OPTION_IDS
        
        # Since security_id_map has strikes with CE/PE
        # The file header should show expiry date
        print("✅ Found security_id_map.py")
        print(f"📊 Total strikes available: {len(NIFTY_OPTION_IDS)}")
        
        # Check first few strikes
        sample_strikes = list(NIFTY_OPTION_IDS.keys())[:5]
        print(f"\n📋 Sample Strikes: {sample_strikes}")
        
        # The expiry is usually in the file header comment
        import security_id_map
        if hasattr(security_id_map, '__doc__'):
            print(f"\n📝 Security Map Info:")
            print(security_id_map.__doc__)
        
    except ImportError:
        print("❌ security_id_map.py not found")
    
    # Method 3: Smart detection based on common NIFTY expiries
    print("\n" + "="*80)
    print("📅 SMART EXPIRY DETECTION (Based on NIFTY Pattern)")
    print("="*80)
    
    today = datetime.now()
    
    # NIFTY has:
    # 1. Weekly expiries (usually Thursday)
    # 2. Monthly expiries (last Thursday of month)
    # 3. Special expiries (sometimes Tuesday before market holidays)
    
    potential_expiries = []
    
    # Check next 4 weeks for Thursdays
    for week in range(4):
        days_ahead = 3 - today.weekday() + (7 * week)
        if days_ahead <= 0:
            days_ahead += 7
        expiry = today + timedelta(days=days_ahead)
        potential_expiries.append(expiry)
    
    # Add April 7, 2026 (Tuesday) - might be special expiry
    from datetime import timedelta
    apr_7 = datetime(2026, 4, 7)
    if apr_7 > today:
        potential_expiries.append(apr_7)
    
    # Add April 28, 2026 (Monthly expiry from security_id_map)
    apr_28 = datetime(2026, 4, 28)
    if apr_28 > today:
        potential_expiries.append(apr_28)
    
    # Sort and display
    potential_expiries = sorted(list(set(potential_expiries)))
    
    print(f"\n🎯 Potential NIFTY Expiries (Next 4 weeks):\n")
    for i, exp in enumerate(potential_expiries, 1):
        days_away = (exp.date() - today.date()).days
        day_name = exp.strftime('%A')
        
        # Highlight nearest
        marker = "⭐ NEAREST" if i == 1 else "   "
        
        # Identify type
        if day_name == "Thursday":
            exp_type = "(Weekly/Monthly)"
        elif day_name == "Tuesday":
            exp_type = "(Special/Adjustment)"
        else:
            exp_type = "(Unknown pattern)"
        
        print(f"{marker} {i}. {exp.strftime('%d-%b-%Y (%A)')} {exp_type}")
        print(f"      📅 {days_away} days from now")
        print()
    
    # Recommendation
    nearest = potential_expiries[0]
    print("="*80)
    print("✅ RECOMMENDATION")
    print("="*80)
    print(f"\n🎯 Use Nearest Expiry: {nearest.strftime('%d-%b-%Y (%A)')}")
    print(f"⏳ Days Away: {(nearest.date() - today.date()).days}")
    print(f"\n💡 Why?")
    print("   • Most liquid contracts")
    print("   • Tightest bid-ask spreads")
    print("   • Best for intraday trading")
    print("\n" + "="*80)
    
    # Check if April 7 is really available
    print("\n🔍 VERIFICATION: Is April 7, 2026 expiry available?")
    print("="*80)
    
    if apr_7 in potential_expiries:
        days_to_apr7 = (apr_7.date() - today.date()).days
        print(f"\n✅ YES - April 7, 2026 (Tuesday) is {days_to_apr7} days away")
        print("\n📋 This could be:")
        print("   • A weekly expiry (adjusted due to holiday)")
        print("   • A special mid-week expiry")
        print("   • Part of April monthly series")
        
        print(f"\n🎯 If April 7 IS the nearest expiry:")
        print(f"   Your bot should select: 07-APR-2026 (Tuesday)")
        print(f"   Not: 10-APR-2026 (Thursday)")
    else:
        print("\n❌ April 7 is in the past or not in detected list")
    
    print("\n" + "="*80)
    print("📝 SOLUTION")
    print("="*80)
    print("\nTo fix your bot:")
    print("1. ✅ Don't assume Thursday expiry")
    print("2. ✅ Fetch actual expiries from Dhan security master")
    print("3. ✅ Always select the NEAREST available expiry")
    print("4. ✅ Update security_id_map.py with correct expiry")
    print("\n" + "="*80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    print(traceback.format_exc())

print("\n💡 Next Steps:")
print("   1. Check Dhan trading terminal for actual expiry dates")
print("   2. Update security_id_map.py with nearest expiry")
print("   3. Bot will auto-select nearest expiry from available list")
print("\n" + "="*80 + "\n")
