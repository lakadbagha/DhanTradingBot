"""
🛑 EMERGENCY STOP - HALT ALL TRADING
=====================================

Use this if you need to immediately:
- Stop the bot
- Close all open positions
- Exit the market

"""

from dhanhq import dhanhq
from creds import client_id, access_token
import sys

print("\n" + "="*80)
print("🛑 EMERGENCY STOP ACTIVATED")
print("="*80)

try:
    dhan = dhanhq(client_id, access_token)
    
    # Get all open positions
    print("\n📊 Checking for open positions...")
    positions = dhan.get_positions()
    
    if positions and 'data' in positions and len(positions['data']) > 0:
        print(f"\n⚠️  Found {len(positions['data'])} open position(s):")
        
        for pos in positions['data']:
            print(f"\n   Instrument: {pos.get('tradingSymbol', 'N/A')}")
            print(f"   Quantity: {pos.get('netQty', 0)}")
            print(f"   P&L: Rs. {pos.get('realizedProfit', 0):,.2f}")
            print(f"   Type: {pos.get('positionType', 'N/A')}")
        
        print("\n" + "="*80)
        response = input("\nClose ALL positions immediately? (yes/no): ").strip().lower()
        
        if response == 'yes':
            print("\n🔄 Closing all positions...")
            
            for pos in positions['data']:
                try:
                    qty = abs(int(pos.get('netQty', 0)))
                    if qty == 0:
                        continue
                    
                    # Determine buy/sell
                    transaction_type = dhan.BUY if pos.get('netQty', 0) < 0 else dhan.SELL
                    
                    # Place market order to close
                    order = dhan.place_order(
                        security_id=pos.get('securityId'),
                        exchange_segment=dhan.NSE_FNO,
                        transaction_type=transaction_type,
                        quantity=qty,
                        order_type=dhan.MARKET,
                        product_type=dhan.INTRA,
                        price=0
                    )
                    
                    if order and 'data' in order:
                        print(f"   ✅ Closed {pos.get('tradingSymbol')}")
                    else:
                        print(f"   ❌ Failed to close {pos.get('tradingSymbol')}")
                
                except Exception as e:
                    print(f"   ❌ Error closing position: {e}")
            
            print("\n✅ All positions closed!")
        else:
            print("\n⚠️  Positions NOT closed. Handle manually on Dhan app.")
    
    else:
        print("✅ No open positions found.")
    
    # Get pending orders
    print("\n📋 Checking for pending orders...")
    orders = dhan.get_order_list()
    
    if orders and 'data' in orders:
        pending = [o for o in orders['data'] if o.get('orderStatus') in ['PENDING', 'TRANSIT']]
        
        if pending:
            print(f"\n⚠️  Found {len(pending)} pending order(s):")
            
            for order in pending:
                print(f"\n   Order ID: {order.get('orderId')}")
                print(f"   Instrument: {order.get('tradingSymbol')}")
                print(f"   Status: {order.get('orderStatus')}")
            
            response = input("\nCancel ALL pending orders? (yes/no): ").strip().lower()
            
            if response == 'yes':
                print("\n🔄 Cancelling all pending orders...")
                
                for order in pending:
                    try:
                        result = dhan.cancel_order(order.get('orderId'))
                        if result:
                            print(f"   ✅ Cancelled order {order.get('orderId')}")
                        else:
                            print(f"   ❌ Failed to cancel {order.get('orderId')}")
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                
                print("\n✅ All pending orders cancelled!")
            else:
                print("\n⚠️  Orders NOT cancelled.")
        else:
            print("✅ No pending orders found.")
    
    print("\n" + "="*80)
    print("🛑 EMERGENCY STOP COMPLETE")
    print("="*80)
    print("\n📊 Current Status:")
    print("   ✅ Bot should be stopped")
    print("   ✅ Positions checked/closed")
    print("   ✅ Orders checked/cancelled")
    print("\n💡 Next Steps:")
    print("   1. Verify on Dhan app that everything is closed")
    print("   2. Review what happened in logs/")
    print("   3. Investigate any issues before restarting")

except Exception as e:
    print(f"\n❌ Error during emergency stop: {e}")
    print("\n⚠️  MANUAL ACTION REQUIRED:")
    print("   1. Open Dhan mobile app")
    print("   2. Go to Positions → Exit all")
    print("   3. Go to Orders → Cancel all pending")
    sys.exit(1)
