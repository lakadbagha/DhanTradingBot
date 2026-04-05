"""
COMPLETE SECURITY ID SOLUTION
Uses Dhan's built-in methods discovered from library source code:
1. fetch_security_list() - Downloads complete security master CSV
2. expiry_list() - Gets all available expiry dates
"""

from dhanhq import dhanhq
from creds import client_id, access_token
import pandas as pd

print("\n" + "=" * 80)
print("🎯 COMPLETE NIFTY OPTIONS SECURITY ID FINDER")
print("=" * 80)

# Connect to Dhan
dhan = dhanhq(client_id, access_token)
print("\n✅ Connected to Dhan API")

# STEP 1: Get all expiry dates
print("\n" + "=" * 80)
print("STEP 1: Getting Available Expiry Dates")
print("=" * 80)

try:
    expiry_response = dhan.expiry_list(
        under_security_id=13,  # NIFTY Index
        under_exchange_segment='NSE_EQ'
    )
    
    print(f"\nAPI Response: {expiry_response}")
    
    if expiry_response.get('status') == 'success':
        expiries = expiry_response.get('data', {}).get('expiryList', [])
        print(f"\n✅ Found {len(expiries)} available expiries:")
        for i, expiry in enumerate(expiries[:10], 1):  # Show first 10
            print(f"   {i}. {expiry}")
        if len(expiries) > 10:
            print(f"   ... and {len(expiries) - 10} more")
    else:
        print(f"❌ Failed to get expiries: {expiry_response}")
        expiries = []
        
except Exception as e:
    print(f"❌ Error getting expiries: {e}")
    expiries = []

# STEP 2: Download complete security master
print("\n" + "=" * 80)
print("STEP 2: Downloading Complete Security Master")
print("=" * 80)

try:
    print("\n📥 Downloading from Dhan servers...")
    df = dhan.fetch_security_list(mode='compact', filename='dhan_complete_security_master.csv')
    
    if df is not None:
        print(f"✅ Downloaded {len(df):,} total securities")
        print(f"💾 Saved to: dhan_complete_security_master.csv")
        
        print(f"\n📊 Available columns:")
        for col in df.columns:
            print(f"   - {col}")
        
        # STEP 3: Filter for NIFTY options
        print("\n" + "=" * 80)
        print("STEP 3: Extracting NIFTY Options")
        print("=" * 80)
        
        # Find the right columns (they might vary)
        symbol_col = None
        for col in df.columns:
            if 'SYMBOL' in col.upper() or 'TRADING' in col.upper():
                symbol_col = col
                break
        
        if symbol_col:
            print(f"\nUsing column: {symbol_col}")
            nifty_options = df[df[symbol_col].str.contains('NIFTY', na=False)]
            
            # Further filter for options only
            if 'SEM_INSTRUMENT_NAME' in df.columns:
                nifty_options = nifty_options[nifty_options['SEM_INSTRUMENT_NAME'].str.contains('OPTIDX', na=False)]
            
            print(f"✅ Found {len(nifty_options):,} NIFTY option contracts")
            
            # Show sample
            print(f"\n📋 Sample NIFTY options (first 10):")
            cols_to_show = [col for col in nifty_options.columns if any(x in col.upper() for x in ['SECURITY', 'SYMBOL', 'STRIKE', 'EXPIRY', 'OPTION'])]
            print(nifty_options[cols_to_show].head(10))
            
            # Save NIFTY options
            nifty_options.to_csv('nifty_options_complete.csv', index=False)
            print(f"\n💾 Saved all NIFTY options to: nifty_options_complete.csv")
            
            # STEP 4: Find 07-APR-2026 expiry contracts
            print("\n" + "=" * 80)
            print("STEP 4: Finding 07-APR-2026 Contracts")
            print("=" * 80)
            
            # Try to find expiry column
            expiry_col = None
            for col in nifty_options.columns:
                if 'EXPIRY' in col.upper():
                    expiry_col = col
                    break
            
            if expiry_col:
                print(f"\nUsing expiry column: {expiry_col}")
                
                # Try different date formats
                april_7_options = nifty_options[
                    nifty_options[expiry_col].astype(str).str.contains('2026-04-07|07-04-2026|07/04/2026|07APR2026', na=False, case=False)
                ]
                
                if len(april_7_options) > 0:
                    print(f"\n✅ Found {len(april_7_options)} contracts for 07-APR-2026!")
                    
                    # Show all columns for these contracts
                    print(f"\n📊 All 07-APR-2026 NIFTY options:")
                    print(april_7_options.to_string())
                    
                    # Save separately
                    april_7_options.to_csv('nifty_07apr2026_options.csv', index=False)
                    print(f"\n💾 Saved to: nifty_07apr2026_options.csv")
                    
                    # Find 22900 strike
                    strike_col = None
                    for col in april_7_options.columns:
                        if 'STRIKE' in col.upper():
                            strike_col = col
                            break
                    
                    if strike_col:
                        strike_22900 = april_7_options[april_7_options[strike_col] == 22900]
                        
                        if len(strike_22900) > 0:
                            print(f"\n🎯 Found 22900 strike contracts:")
                            print(strike_22900.to_string())
                            
                            # Extract security IDs
                            id_col = None
                            for col in strike_22900.columns:
                                if 'SECURITY' in col.upper() and 'ID' in col.upper():
                                    id_col = col
                                    break
                            
                            if id_col:
                                print(f"\n✅ SECURITY IDs for NIFTY 22900 (07-APR-2026):")
                                for idx, row in strike_22900.iterrows():
                                    print(f"   {row[symbol_col]}: {row[id_col]}")
                        else:
                            print(f"\n⚠️  No 22900 strike found")
                            print(f"   Available strikes: {sorted(april_7_options[strike_col].unique())}")
                else:
                    print(f"\n⚠️  No contracts found for 07-APR-2026")
                    print(f"   Sample expiry dates in data:")
                    print(nifty_options[expiry_col].value_counts().head(10))
            else:
                print("⚠️  Could not find expiry date column")
        else:
            print("⚠️  Could not find symbol column")
            print("Sample row:")
            print(df.head(1))
        
    else:
        print("❌ Failed to download security master")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print("\n📁 Files created:")
print("   1. dhan_complete_security_master.csv - All securities")
print("   2. nifty_options_complete.csv - All NIFTY options")
print("   3. nifty_07apr2026_options.csv - Only 07-APR-2026 expiry")
print("\n💡 Check these CSV files to find all security_ids!")
print("=" * 80)
