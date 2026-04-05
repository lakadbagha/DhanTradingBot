"""
Final Optimization - 4 Different Approaches
-------------------------------------------
Try 4 different optimizations, keep only if better than current
"""

import subprocess
import sys
import time

# Current baseline performance
BASELINE_PNL = 236069.49
BASELINE_WIN_RATE = 58.2

class FinalOptimizer:
    def __init__(self):
        self.test_number = 0
        self.best_config = None
        self.best_pnl = BASELINE_PNL
        self.best_win_rate = BASELINE_WIN_RATE
        
    def backup_config(self):
        """Backup current config"""
        with open('strategy_config.py', 'r', encoding='utf-8') as f:
            return f.read()
    
    def restore_config(self, backup):
        """Restore config from backup"""
        with open('strategy_config.py', 'w', encoding='utf-8') as f:
            f.write(backup)
    
    def update_config(self, changes):
        """Update specific config values"""
        with open('strategy_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old_value, new_value in changes.items():
            content = content.replace(old_value, new_value)
        
        with open('strategy_config.py', 'w', encoding='utf-8') as f:
            f.write(content)
    
    def run_backtest(self):
        """Run backtest and extract results"""
        print("   Running backtest (30 seconds)...")
        
        result = subprocess.run(
            [sys.executable, 'generate_6month_excel.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Extract P&L and Win Rate
        pnl = None
        win_rate = None
        
        for line in result.stdout.split('\n'):
            if 'Total P&L:' in line and 'Rs.' in line:
                try:
                    pnl_str = line.split('Rs.')[1].strip().replace(',', '')
                    pnl = float(pnl_str)
                except:
                    pass
            if 'Win Rate:' in line and '%' in line:
                try:
                    wr_str = line.split('Win Rate:')[1].split('%')[0].strip()
                    win_rate = float(wr_str)
                except:
                    pass
        
        return pnl, win_rate
    
    def test_optimization(self, name, description, changes):
        """Test a specific optimization"""
        self.test_number += 1
        
        print("\n" + "=" * 80)
        print(f"🧪 OPTIMIZATION TEST #{self.test_number}: {name}")
        print("=" * 80)
        print(f"📝 Description: {description}")
        print(f"🔧 Changes:")
        for old, new in changes.items():
            print(f"   {old} → {new}")
        print()
        
        # Backup current config
        backup = self.backup_config()
        
        # Apply changes
        self.update_config(changes)
        
        # Run backtest
        pnl, win_rate = self.run_backtest()
        
        if pnl is None or win_rate is None:
            print("❌ Backtest failed, skipping...")
            self.restore_config(backup)
            return False
        
        # Compare results
        print(f"\n📊 RESULTS:")
        print(f"   P&L:      Rs.{pnl:,.2f}")
        print(f"   Win Rate: {win_rate:.1f}%")
        
        print(f"\n📊 COMPARISON vs BASELINE:")
        pnl_diff = pnl - self.best_pnl
        pnl_pct = (pnl_diff / self.best_pnl * 100) if self.best_pnl != 0 else 0
        wr_diff = win_rate - self.best_win_rate
        
        print(f"   P&L Difference:      Rs.{pnl_diff:,.2f} ({pnl_pct:+.1f}%)")
        print(f"   Win Rate Difference: {wr_diff:+.1f} percentage points")
        
        # Decision
        if pnl > self.best_pnl:
            improvement = ((pnl / self.best_pnl - 1) * 100)
            print(f"\n✅ BETTER! Improvement: {improvement:.1f}%")
            print(f"   💾 Keeping this configuration!")
            self.best_pnl = pnl
            self.best_win_rate = win_rate
            self.best_config = name
            return True
        else:
            decline = ((1 - pnl / self.best_pnl) * 100)
            print(f"\n❌ WORSE! Decline: {decline:.1f}%")
            print(f"   🔄 Reverting to previous configuration...")
            self.restore_config(backup)
            return False

def main():
    print("\n" + "=" * 80)
    print("🔬 FINAL OPTIMIZATION - 4 APPROACHES")
    print("=" * 80)
    print(f"\n📊 BASELINE Performance:")
    print(f"   P&L:      Rs.{BASELINE_PNL:,.2f}")
    print(f"   Win Rate: {BASELINE_WIN_RATE:.1f}%")
    print(f"\nTesting 4 different optimizations...")
    print(f"Only keeping changes that IMPROVE results!")
    
    optimizer = FinalOptimizer()
    
    # Test 1: ATM Options
    optimizer.test_optimization(
        name="ATM Options (0 ITM)",
        description="Use At-The-Money options for higher delta and better movement capture",
        changes={
            'ITM_POINTS = 50': 'ITM_POINTS = 0'
        }
    )
    
    time.sleep(2)
    
    # Test 2: 3 Trades Per Day
    optimizer.test_optimization(
        name="3 Trades Per Day",
        description="Increase daily trade limit for more opportunities",
        changes={
            'TRADES_PER_DAY = 2': 'TRADES_PER_DAY = 3'
        }
    )
    
    time.sleep(2)
    
    # Test 3: Wider Trailing After Target
    optimizer.test_optimization(
        name="Wider Trailing (15 points)",
        description="Give more room for profit extension after target hit",
        changes={
            'TRAILING_SL_AFTER_TARGET = 10': 'TRAILING_SL_AFTER_TARGET = 15'
        }
    )
    
    time.sleep(2)
    
    # Test 4: Stricter Fibonacci Entry
    optimizer.test_optimization(
        name="Stricter Fibonacci (100 tolerance)",
        description="More precise entry criteria for higher quality setups",
        changes={
            'FIBONACCI_TOLERANCE = 150': 'FIBONACCI_TOLERANCE = 100'
        }
    )
    
    # Final Summary
    print("\n" + "=" * 80)
    print("🏆 FINAL OPTIMIZATION RESULTS")
    print("=" * 80)
    
    if optimizer.best_config:
        improvement = ((optimizer.best_pnl / BASELINE_PNL - 1) * 100)
        print(f"\n✅ BEST Configuration Found: {optimizer.best_config}")
        print(f"\n📊 Final Performance:")
        print(f"   P&L:      Rs.{optimizer.best_pnl:,.2f}")
        print(f"   Win Rate: {optimizer.best_win_rate:.1f}%")
        print(f"\n🚀 Improvement: {improvement:.1f}% better than baseline!")
        print(f"   Additional Profit: Rs.{optimizer.best_pnl - BASELINE_PNL:,.2f}")
    else:
        print(f"\n✅ CURRENT Configuration is OPTIMAL!")
        print(f"   None of the 4 optimizations beat the baseline.")
        print(f"\n📊 Final Performance:")
        print(f"   P&L:      Rs.{optimizer.best_pnl:,.2f}")
        print(f"   Win Rate: {optimizer.best_win_rate:.1f}%")
        print(f"\n🔒 LOCKING current strategy as FINAL!")
    
    print("\n" + "=" * 80)
    print("✅ Optimization Complete!")
    print("=" * 80)
    
    # Generate final Excel with best config
    print("\n📊 Generating final Excel report with optimal configuration...")
    subprocess.run([sys.executable, 'generate_6month_excel.py'])
    
    print("\n✅ Done! Check 6_MONTHS_TRADING_REPORT.xlsx for final results.")

if __name__ == "__main__":
    main()
