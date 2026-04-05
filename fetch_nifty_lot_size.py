"""
Fetch NIFTY Option Lot Size from Dhan Security Master
This shows the ACTUAL lot size (not hardcoded!)
"""

from dhanhq import dhanhq
from creds import client_id, access_token
import pandas as pd

dhan = dhanhq(client_id, access_token)

print("\n" + "="*80)
print("🔍 FETCHING NIFTY LOT SIZE FROM DHAN SECURITY MASTER")
print("="*80)

print("\n⏳ Downloading security master CSV from Dhan...\n")

try:
    # Fetch security list (detailed version has lot size)
    df = dhan.fetch_security_list(mode='detailed', filename='security_master_detailed.csv')
    
    if df is not None:
        print("✅ Security master downloaded successfully!")
        print(f"📊 Total securities: {len(df)}")
        
        # Show column names
        print(f"\n📋 Available columns: {list(df.columns)}")
        
        # Filter for NIFTY options
        print("\n" + "="*80)
        print("🔍 FILTERING NIFTY OPTIONS")
        print("="*80)
        
        # Filter for NIFTY
        nifty_options = df[df['SYMBOL_NAME'].str.contains('NIFTY', na=False)]

        print(f"\n✅ Found {len(nifty_options)} NIFTY contracts")

        # Show sample NIFTY options
        if len(nifty_options) > 0:
            print("\n📋 Sample NIFTY Options (first 10):")
            print(nifty_options[['SYMBOL_NAME', 'LOT_SIZE', 'SM_EXPIRY_DATE', 'STRIKE_PRICE', 'OPTION_TYPE']].head(10))

            # Check lot size
            lot_sizes = nifty_options['LOT_SIZE'].unique()
            
            print("\n" + "="*80)
            print("📊 NIFTY OPTION LOT SIZES")
            print("="*80)
            
            for lot_size in lot_sizes:
                count = len(nifty_options[nifty_options['LOT_SIZE'] == lot_size])
                print(f"\n🔢 Lot Size: {lot_size}")
                print(f"   Contracts with this lot: {count}")

                # Show sample contracts
                sample = nifty_options[nifty_options['LOT_SIZE'] == lot_size].head(3)
                print(f"\n   Sample contracts:")
                for _, row in sample.iterrows():
                    print(f"   • {row['SYMBOL_NAME']} (Expiry: {row['SM_EXPIRY_DATE']})")

            # Find most common lot size
            most_common_lot = nifty_options['LOT_SIZE'].mode()[0]
            
            print("\n" + "="*80)
            print("✅ CURRENT NIFTY LOT SIZE")
            print("="*80)
            print(f"\n🎯 Most Common Lot Size: {most_common_lot}")
            print(f"\n💡 Use this in your strategy_config.py:")
            print(f"   LOT_SIZE = {most_common_lot}")
            
            # Check if it's different from hardcoded value
            hardcoded_lot = 65
            if most_common_lot != hardcoded_lot:
                print(f"\n⚠️  WARNING: Your hardcoded lot size ({hardcoded_lot}) is DIFFERENT!")
                print(f"   Actual lot size from Dhan: {most_common_lot}")
                print(f"   ❌ This could cause incorrect P&L calculations!")
            else:
                print(f"\n✅ Your hardcoded lot size ({hardcoded_lot}) matches Dhan data!")
            
            # Check for NIFTY 50 weekly options specifically
            weekly_options = nifty_options[nifty_options['SYMBOL_NAME'].str.match(r'NIFTY\d{2}[A-Z]{3}\d{5}(CE|PE)', na=False)]

            if len(weekly_options) > 0:
                weekly_lot = weekly_options['LOT_SIZE'].mode()[0]
                print(f"\n📅 NIFTY Weekly Options Lot Size: {weekly_lot}")
            
            # Save filtered data
            nifty_options.to_csv('nifty_options_with_lot_size.csv', index=False)
            print(f"\n💾 Saved NIFTY options to: nifty_options_with_lot_size.csv")
            
        else:
            print("\n❌ No NIFTY options found in security master")
            
    else:
        print("❌ Failed to download security master")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    print(traceback.format_exc())

print("\n" + "="*80)
print("📝 RECOMMENDATION")
print("="*80)
print("\nDon't hardcode lot size! It changes periodically.")
print("\nBetter approach:")
print("1. Fetch security master daily")
print("2. Extract NIFTY lot size")
print("3. Use dynamic lot size in calculations")
print("\nThis ensures accuracy even when NSE changes lot sizes!")
print("\n" + "="*80 + "\n")
