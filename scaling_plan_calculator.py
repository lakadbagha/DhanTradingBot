"""
2-YEAR SCALING PLAN CALCULATOR
===============================
Calculate realistic profit when adding 1 lot per month
"""

import pandas as pd
from datetime import datetime

# ============================================================================
# BACKTEST RESULTS (12 months, 1 lot)
# ============================================================================
BACKTEST_PROFIT_1LOT = 214348  # Rs. per year with 1 lot
MONTHLY_PROFIT_1LOT = BACKTEST_PROFIT_1LOT / 12  # Rs. 17,862 per month

# ============================================================================
# REALISTIC ADJUSTMENT (Live trading vs Backtest)
# ============================================================================
REALISTIC_MULTIPLIER = 0.75  # 75% of backtest (accounting for slippage, etc.)

# ============================================================================
# CAPITAL REQUIREMENTS
# ============================================================================
MARGIN_PER_LOT = 52000  # Rs. 800 SL × 65 qty

def calculate_scaling_plan(years=2):
    """
    Calculate profit when adding 1 lot per month
    """
    results = []
    
    for year in range(1, years + 1):
        for month in range(1, 13):
            overall_month = (year - 1) * 12 + month
            
            # Determine number of lots for this month
            if year == 1:
                lots = month  # Month 1 = 1 lot, Month 2 = 2 lots, etc.
            else:
                lots = 12  # Year 2 onwards, maintain 12 lots
            
            # Calculate monthly profit (realistic)
            monthly_profit_backtest = MONTHLY_PROFIT_1LOT * lots
            monthly_profit_realistic = monthly_profit_backtest * REALISTIC_MULTIPLIER
            
            # Capital needed for this month
            capital_needed = MARGIN_PER_LOT * lots
            
            results.append({
                'Year': year,
                'Month': month,
                'OverallMonth': overall_month,
                'Lots': lots,
                'CapitalNeeded': capital_needed,
                'BacktestProfit': round(monthly_profit_backtest, 2),
                'RealisticProfit': round(monthly_profit_realistic, 2),
            })
    
    return pd.DataFrame(results)

def calculate_summary(df):
    """Calculate yearly summaries"""
    print("\n" + "="*80)
    print("💰 2-YEAR SCALING PLAN SUMMARY")
    print("="*80)
    
    # Year 1 Summary
    year1 = df[df['Year'] == 1]
    y1_total_realistic = year1['RealisticProfit'].sum()
    y1_total_backtest = year1['BacktestProfit'].sum()
    y1_final_capital = year1.iloc[-1]['CapitalNeeded']
    
    print(f"\n📊 YEAR 1 (Scaling from 1 to 12 lots):")
    print(f"   Starting lots:           1")
    print(f"   Ending lots:             12")
    print(f"   Final capital needed:    Rs. {y1_final_capital:,.0f}")
    print(f"   Backtest profit:         Rs. {y1_total_backtest:,.2f}")
    print(f"   Realistic profit (75%):  Rs. {y1_total_realistic:,.2f}")
    print(f"   Monthly avg profit:      Rs. {y1_total_realistic/12:,.2f}")
    
    # Year 2 Summary
    year2 = df[df['Year'] == 2]
    y2_total_realistic = year2['RealisticProfit'].sum()
    y2_total_backtest = year2['BacktestProfit'].sum()
    y2_capital = year2.iloc[0]['CapitalNeeded']
    
    print(f"\n📊 YEAR 2 (Stable at 12 lots):")
    print(f"   Trading lots:            12 (all year)")
    print(f"   Capital needed:          Rs. {y2_capital:,.0f}")
    print(f"   Backtest profit:         Rs. {y2_total_backtest:,.2f}")
    print(f"   Realistic profit (75%):  Rs. {y2_total_realistic:,.2f}")
    print(f"   Monthly avg profit:      Rs. {y2_total_realistic/12:,.2f}")
    
    # 2-Year Total
    total_realistic = df['RealisticProfit'].sum()
    total_backtest = df['BacktestProfit'].sum()
    
    print(f"\n🎯 2-YEAR TOTAL:")
    print(f"   Backtest profit:         Rs. {total_backtest:,.2f}")
    print(f"   Realistic profit (75%):  Rs. {total_realistic:,.2f}")
    print(f"   Average monthly profit:  Rs. {total_realistic/24:,.2f}")
    
    print("\n" + "="*80)
    print("💡 PROFIT BREAKDOWN BY SCENARIO")
    print("="*80)
    
    scenarios = {
        'Conservative (70%)': 0.70,
        'Realistic (75%)': 0.75,
        'Optimistic (85%)': 0.85
    }
    
    for name, multiplier in scenarios.items():
        year1_profit = y1_total_backtest * multiplier
        year2_profit = y2_total_backtest * multiplier
        total_profit = total_backtest * multiplier
        
        print(f"\n{name}:")
        print(f"   Year 1:  Rs. {year1_profit:,.2f}")
        print(f"   Year 2:  Rs. {year2_profit:,.2f}")
        print(f"   Total:   Rs. {total_profit:,.2f}")

def generate_excel_report(df):
    """Generate detailed Excel report"""
    filename = f'SCALING_PLAN_2YEARS_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    # Calculate cumulative profit
    df['CumulativeBacktest'] = df['BacktestProfit'].cumsum()
    df['CumulativeRealistic'] = df['RealisticProfit'].cumsum()
    
    # Calculate monthly ROI
    df['ROI%'] = (df['RealisticProfit'] / df['CapitalNeeded'] * 100).round(2)
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: Month-by-Month Details
        df_export = df[[
            'Year', 'Month', 'OverallMonth', 'Lots', 'CapitalNeeded',
            'BacktestProfit', 'RealisticProfit', 'CumulativeRealistic', 'ROI%'
        ]].copy()
        
        df_export.columns = [
            'Year', 'Month', 'Overall Month', 'Lots Trading',
            'Capital Needed (Rs.)', 'Backtest Profit (Rs.)',
            'Realistic Profit (Rs.)', 'Cumulative Profit (Rs.)', 'Monthly ROI %'
        ]
        
        df_export.to_excel(writer, sheet_name='Monthly Details', index=False)
        
        # Sheet 2: Yearly Summary
        yearly_summary = []
        
        for year in [1, 2]:
            year_data = df[df['Year'] == year]
            yearly_summary.append({
                'Year': year,
                'Starting Lots': year_data.iloc[0]['Lots'],
                'Ending Lots': year_data.iloc[-1]['Lots'],
                'Final Capital (Rs.)': year_data.iloc[-1]['CapitalNeeded'],
                'Backtest Profit (Rs.)': year_data['BacktestProfit'].sum(),
                'Realistic Profit (Rs.)': year_data['RealisticProfit'].sum(),
                'Avg Monthly Profit (Rs.)': year_data['RealisticProfit'].mean(),
                'Total Trades': 228 * year_data['Lots'].mean()  # Approx
            })
        
        pd.DataFrame(yearly_summary).to_excel(writer, sheet_name='Yearly Summary', index=False)
        
        # Sheet 3: Capital Requirements Timeline
        capital_timeline = df[['Year', 'Month', 'Lots', 'CapitalNeeded']].copy()
        capital_timeline.columns = ['Year', 'Month', 'Lots', 'Capital Needed (Rs.)']
        capital_timeline.to_excel(writer, sheet_name='Capital Timeline', index=False)
        
        # Sheet 4: Scenario Analysis
        scenarios_data = []
        for scenario_name, multiplier in [('Conservative', 0.70), ('Realistic', 0.75), ('Optimistic', 0.85)]:
            for year in [1, 2]:
                year_data = df[df['Year'] == year]
                scenarios_data.append({
                    'Scenario': scenario_name,
                    'Year': year,
                    'Profit (Rs.)': (year_data['BacktestProfit'].sum() * multiplier),
                })
        
        scenario_df = pd.DataFrame(scenarios_data)
        scenario_pivot = scenario_df.pivot(index='Scenario', columns='Year', values='Profit (Rs.)')
        scenario_pivot['2-Year Total'] = scenario_pivot[1] + scenario_pivot[2]
        scenario_pivot.to_excel(writer, sheet_name='Scenario Analysis')
    
    print(f"\n✅ Detailed Excel report saved: {filename}")
    return filename

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 CALCULATING 2-YEAR SCALING PLAN")
    print("="*80)
    print("\n📋 Strategy: Start with 1 lot, add 1 lot per month")
    print("   Year 1: Scale from 1 lot (Month 1) to 12 lots (Month 12)")
    print("   Year 2: Trade with 12 lots all year")
    print("\n   Using realistic 75% of backtest profit")
    print("   Backtest base: Rs. 2,14,348 per year (1 lot)")
    
    # Calculate
    df = calculate_scaling_plan(years=2)
    
    # Print summary
    calculate_summary(df)
    
    # Generate Excel
    excel_file = generate_excel_report(df)
    
    # Month-by-month preview (first 6 months)
    print("\n" + "="*80)
    print("📅 FIRST 6 MONTHS PREVIEW")
    print("="*80)
    print("\n{:<6} {:<6} {:<12} {:<18} {:<18}".format(
        'Month', 'Lots', 'Capital', 'Backtest Profit', 'Realistic Profit'
    ))
    print("-" * 80)
    
    for idx, row in df.head(6).iterrows():
        print("{:<6} {:<6} Rs. {:<9,.0f} Rs. {:<15,.2f} Rs. {:<15,.2f}".format(
            row['Month'],
            row['Lots'],
            row['CapitalNeeded'],
            row['BacktestProfit'],
            row['RealisticProfit']
        ))
    
    print("\n💡 Open the Excel file for complete 24-month breakdown!")
    print("="*80)
