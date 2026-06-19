"""
Fetch NIFTY Weekly Expiries by Checking Option Chain
Since Dhan's expiry_list() only shows monthly expiries,
we'll fetch the option chain to see actual weekly expiries
"""

from dhanhq import dhanhq, DhanContext
from creds import client_id, access_token
from datetime import datetime, timedelta
import json

dhan_context = DhanContext(client_id, access_token)
dhan = dhanhq(dhan_context)

print("\n" + "="*80)
print("🔍 FETCHING NIFTY WEEKLY EXPIRIES FROM OPTION CHAIN")
print("="*80)

# NIFTY 50 for option chain
nifty_security_id = 13  # NIFTY 50 for NSE_FNO
nifty_exchange = dhan.NSE_FNO

print(f"\n📊 Querying NIFTY Options:")
print(f"   Security ID: {nifty_security_id}")
print(f"   Exchange: {nifty_exchange}")

# First, get monthly expiries from API
print("\n" + "="*80)
print("Step 1: Getting Monthly Expiries from API")
print("="*80)

try:
    monthly_response = dhan.expiry_list(nifty_security_id, nifty_exchange)
    
    if monthly_response and 'data' in monthly_response:
        monthly_data = monthly_response['data']
        if 'data' in monthly_data:
            monthly_expiries = monthly_data['data']
            print(f"\n✅ Found {len(monthly_expiries)} monthly expiries:")
            for exp in monthly_expiries:
                print(f"   • {exp}")
except Exception as e:
    print(f"❌ Error: {e}")
    monthly_expiries = []

# Now try to fetch option chain for upcoming dates to find weekly expiries
print("\n" + "="*80)
print("Step 2: Checking Option Chains for Weekly Expiries")
print("="*80)

all_expiries = set()
today = datetime.now()

# Check next 8 weeks
for weeks_ahead in range(8):
    # Check Thursday (common weekly expiry day)
    days_ahead = 3 - today.weekday() + (7 * weeks_ahead)  # Thursday
    if days_ahead <= 0:
        days_ahead += 7
    test_date = today + timedelta(days=days_ahead)
    test_date_str = test_date.strftime("%Y-%m-%d")
    
    print(f"\n🔍 Checking: {test_date.strftime('%d-%b-%Y (%A)')}")
    
    try:
        # Try to fetch option chain for this date
        chain_response = dhan.option_chain(
            under_security_id=nifty_security_id,
            under_exchange_segment=nifty_exchange,
            expiry=test_date_str
        )
        
        if chain_response and chain_response.get('status') == 'success':
            if 'data' in chain_response and chain_response['data']:
                all_expiries.add(test_date)
                print(f"   ✅ FOUND - Expiry exists!")
            else:
                print(f"   ❌ No data - Expiry doesn't exist")
        else:
            print(f"   ❌ No data")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:50]}")
    
    # Also check Tuesday (for special/adjusted expiries)
    test_tuesday = test_date - timedelta(days=2)  # Tuesday before Thursday
    test_tuesday_str = test_tuesday.strftime("%Y-%m-%d")
    
    if test_tuesday >= today:
        print(f"🔍 Checking: {test_tuesday.strftime('%d-%b-%Y (%A)')}")
        try:
            chain_response = dhan.option_chain(
                under_security_id=nifty_security_id,
                under_exchange_segment=nifty_exchange,
                expiry=test_tuesday_str
            )
            
            if chain_response and chain_response.get('status') == 'success':
                if 'data' in chain_response and chain_response['data']:
                    all_expiries.add(test_tuesday)
                    print(f"   ✅ FOUND - Special expiry!")
        except:
            pass

# Display all found expiries
if all_expiries:
    print("\n" + "="*80)
    print("📅 ALL FOUND NIFTY EXPIRIES")
    print("="*80)
    
    sorted_expiries = sorted(list(all_expiries))
    
    for i, exp in enumerate(sorted_expiries, 1):
        days_away = (exp.date() - today.date()).days
        marker = "⭐ NEAREST" if i == 1 else "  "
        print(f"{marker} {i}. {exp.strftime('%d-%b-%Y (%A)')} - {days_away} days away")
    
    print("\n" + "="*80)
    print("✅ USE THESE DATES IN YOUR CODE")
    print("="*80)
    
    # Generate Python code
    print("\n📝 Python Code:")
    print("\n```python")
    for i, exp in enumerate(sorted_expiries[:5], 1):
        month_str = exp.strftime('%b').lower()
        day_str = exp.strftime('%d')
        var_name = f"expiry_{month_str}_{day_str}"
        comment = f"# {exp.strftime('%A')}"
        if i == 1:
            comment += " - NEAREST"
        print(f"{var_name} = datetime(2026, {exp.month}, {exp.day})  {comment}")
    print("```")
else:
    print("\n⚠️  No expiries found via option chain")
    print("\n💡 This could mean:")
    print("   1. Weekly option chain data requires special permissions")
    print("   2. Data is only available during market hours")
    print("   3. Need to check NSE website directly")

print("\n" + "="*80)
print("🌐 MANUAL CHECK: NSE Website")
print("="*80)
print("\nFor accurate weekly expiries, check:")
print("https://www.nseindia.com/option-chain")
print("\nOr check your Dhan trading terminal's option chain")
print("\n" + "="*80 + "\n")
