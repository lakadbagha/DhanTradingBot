"""
Fetch ACTUAL NIFTY Option Expiries from Dhan API
Uses the expiry_list() method from DhanHQ library
"""

from dhanhq import dhanhq
from creds import client_id, access_token
from datetime import datetime
import json

dhan = dhanhq(client_id, access_token)

print("\n" + "="*80)
print("🔍 FETCHING ACTUAL NIFTY EXPIRIES FROM DHAN API")
print("="*80)

# NIFTY 50 security_id and exchange segment
nifty_security_id = 25  # NIFTY 50 index
nifty_exchange = dhan.INDEX  # IDX_I

print(f"\n📊 Querying NIFTY 50:")
print(f"   Security ID: {nifty_security_id}")
print(f"   Exchange: {nifty_exchange}")
print("\n⏳ Fetching expiry list from Dhan...\n")

try:
    # Call the expiry_list API
    response = dhan.expiry_list(
        under_security_id=nifty_security_id,
        under_exchange_segment=nifty_exchange
    )
    
    print("="*80)
    print("✅ API RESPONSE RECEIVED")
    print("="*80)
    
    # Print raw response
    print(f"\n📋 Raw Response:")
    print(json.dumps(response, indent=2))
    
    # Parse and display expiries
    if response and 'data' in response:
        expiries = response['data']
        
        if isinstance(expiries, list) and len(expiries) > 0:
            print("\n" + "="*80)
            print("📅 AVAILABLE NIFTY OPTION EXPIRIES")
            print("="*80)
            
            today = datetime.now()
            
            print(f"\n📆 Today: {today.strftime('%d-%b-%Y (%A)')}\n")
            
            # Sort and display expiries
            expiry_dates = []
            for exp_str in expiries:
                try:
                    # Parse expiry date (format may vary)
                    # Common formats: "2026-04-07", "07-Apr-2026", etc.
                    exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
                    expiry_dates.append(exp_date)
                except:
                    try:
                        exp_date = datetime.strptime(exp_str, "%d-%b-%Y")
                        expiry_dates.append(exp_date)
                    except:
                        print(f"⚠️  Could not parse: {exp_str}")
            
            # Sort expiries
            expiry_dates = sorted(expiry_dates)
            
            # Display expiries
            for i, exp in enumerate(expiry_dates, 1):
                days_away = (exp.date() - today.date()).days
                
                if days_away < 0:
                    status = "❌ PAST"
                elif i == 1:
                    status = "⭐ NEAREST"
                else:
                    status = "  "
                
                print(f"{status} {i}. {exp.strftime('%d-%b-%Y (%A)')} - {days_away} days away")
            
            # Show nearest expiry clearly
            if expiry_dates:
                nearest = expiry_dates[0]
                print("\n" + "="*80)
                print("🎯 NEAREST EXPIRY CONFIRMED")
                print("="*80)
                print(f"\n📅 Nearest Expiry: {nearest.strftime('%d-%b-%Y (%A)')}")
                print(f"⏳ Days Away: {(nearest.date() - today.date()).days} days")
                
                if len(expiry_dates) > 1:
                    next_exp = expiry_dates[1]
                    print(f"\n📊 Next Expiry: {next_exp.strftime('%d-%b-%Y (%A)')}")
                    print(f"⏳ Days Away: {(next_exp.date() - today.date()).days} days")
                
                print("\n" + "="*80)
                print("✅ USE THESE DATES IN YOUR CODE!")
                print("="*80)
                
                # Generate Python code
                print("\n📝 Python Code to Use:")
                print("\n```python")
                print("# REAL NIFTY expiries from Dhan API")
                for i, exp in enumerate(expiry_dates[:5], 1):
                    var_name = f"expiry_{exp.strftime('%b_%d').lower()}"
                    print(f"{var_name} = datetime({exp.year}, {exp.month}, {exp.day})  # {exp.strftime('%A')}")
                print("```")
        else:
            print("\n⚠️  No expiry data found in response")
    else:
        print("\n❌ Unexpected response format")
        print(f"Response: {response}")
        
except Exception as e:
    print(f"\n❌ Error fetching expiries: {e}")
    import traceback
    print(traceback.format_exc())
    
    print("\n" + "="*80)
    print("💡 TROUBLESHOOTING")
    print("="*80)
    print("\n1. Check if your Dhan account has access to option chain data")
    print("2. Verify your API credentials in creds.py")
    print("3. Check if you need to whitelist your IP")
    print("4. Try using NSE_FNO exchange segment instead of IDX_I")
    
    print("\n🔄 Trying with NSE_FNO exchange segment...")
    
    try:
        response = dhan.expiry_list(
            under_security_id=nifty_security_id,
            under_exchange_segment=dhan.NSE_FNO  # Try FNO segment
        )
        print("\n✅ NSE_FNO Response:")
        print(json.dumps(response, indent=2))
    except Exception as e2:
        print(f"❌ Also failed with NSE_FNO: {e2}")

print("\n" + "="*80)
print("📝 NEXT STEPS")
print("="*80)
print("\n1. Note the expiry dates above")
print("2. Update live_trading_engine_with_trailing.py")
print("3. Replace hardcoded expiries with actual dates from API")
print("4. Use this script daily to check current expiries")
print("\n" + "="*80 + "\n")
