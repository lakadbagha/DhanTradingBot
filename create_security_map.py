"""
CREATE COMPLETE SECURITY ID MAPPING
Extracts all NIFTY Apr2026 options from security master CSV
"""

import pandas as pd

print("\n" + "=" * 80)
print("📊 CREATING NIFTY APR2026 SECURITY ID MAPPING")
print("=" * 80)

# Load the CSV
df = pd.read_csv('nifty_options_complete.csv')

# Filter for NIFTY Apr2026 only (not FINNIFTY, not other indices)
nifty_apr = df[
    (df['SEM_TRADING_SYMBOL'].str.match(r'^NIFTY-Apr2026-\d+-[CP]E$', na=False))
]

print(f"\n✅ Found {len(nifty_apr)} NIFTY Apr2026 contracts")

# Group by strike price
strikes = sorted(nifty_apr['SEM_STRIKE_PRICE'].unique())
print(f"📊 Strikes available: {min(strikes)} to {max(strikes)}")
print(f"   Total strikes: {len(strikes)}")

# Create mapping dictionary
security_map = {}

for strike in strikes:
    strike_data = nifty_apr[nifty_apr['SEM_STRIKE_PRICE'] == strike]
    
    ce_row = strike_data[strike_data['SEM_OPTION_TYPE'] == 'CE']
    pe_row = strike_data[strike_data['SEM_OPTION_TYPE'] == 'PE']
    
    if not ce_row.empty and not pe_row.empty:
        # Take first occurrence if duplicates
        ce_id = str(int(ce_row.iloc[0]['SEM_SMST_SECURITY_ID']))
        pe_id = str(int(pe_row.iloc[0]['SEM_SMST_SECURITY_ID']))
        
        security_map[int(strike)] = {
            'CE': ce_id,
            'PE': pe_id
        }

print(f"\n✅ Created mapping for {len(security_map)} strikes")

# Generate Python code for security_id_map.py
print("\n" + "=" * 80)
print("GENERATING security_id_map.py")
print("=" * 80)

code = '''"""
Security ID Mapping for NIFTY Options
Auto-generated from Dhan security master CSV
Expiry: 28-APR-2026
"""

# NIFTY April 2026 Expiry (28-APR-2026)
NIFTY_OPTION_IDS = {
'''

# Add all strikes
for strike in sorted(security_map.keys()):
    ce_id = security_map[strike]['CE']
    pe_id = security_map[strike]['PE']
    code += f"    {strike}: {{'CE': '{ce_id}', 'PE': '{pe_id}'}},\n"

code += '''}\n\ndef get_security_id(strike: int, option_type: str):
    """Get security_id for given strike and type"""
    if strike in NIFTY_OPTION_IDS:
        return NIFTY_OPTION_IDS[strike][option_type]
    return None

CURRENT_EXPIRY = "28-APR-2026"
TOTAL_STRIKES = ''' + str(len(security_map)) + '\n'

# Save to file
with open('security_id_map.py', 'w') as f:
    f.write(code)

print("\n✅ Created security_id_map.py")
print(f"   Total strikes: {len(security_map)}")
print(f"   Range: {min(security_map.keys())} to {max(security_map.keys())}")

# Show sample
print("\n📋 Sample mappings (around 22900):")
sample_strikes = [s for s in security_map.keys() if 22800 <= s <= 23000]
for strike in sorted(sample_strikes)[:10]:
    print(f"   {strike}: CE={security_map[strike]['CE']}, PE={security_map[strike]['PE']}")

# Verify 22900
if 22900 in security_map:
    print(f"\n✅ VERIFIED: NIFTY 22900 CE = {security_map[22900]['CE']}")
    print(f"              NIFTY 22900 PE = {security_map[22900]['PE']}")
    
    if security_map[22900]['CE'] == '40761':
        print("   🎯 Matches your security_id 40761!")

print("\n" + "=" * 80)
print("✅ COMPLETE - security_id_map.py is ready!")
print("=" * 80)
