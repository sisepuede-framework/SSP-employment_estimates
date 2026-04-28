"""
Validate that EGY and MEX labor_data matches between original and aggregated
"""
import sys
import os
import pandas as pd
import pickle as pkl

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("VALIDATING LABOR_DATA AGGREGATION")
print("="*80)
print()

# Load aggregated labor data (8 countries)
print("Loading aggregated labor_data.pkl (SSP - 8 countries)...")
labor_agg = pd.read_pickle("GLORIA_db/v57/2019/SSP/labor_data.pkl")
print(f"  Shape: {labor_agg.shape}")
print(f"  Countries: {sorted(labor_agg['REG_imp'].unique())}")
print()

# Load original labor data (164 countries)
print("Loading original labor_data.pkl (164 GLORIA countries)...")
labor_orig = pd.read_pickle("GLORIA_db/v57/2019/parsed_db_original/labor_data.pkl")
print(f"  Shape: {labor_orig.shape}")
print(f"  Countries (first 20): {sorted(labor_orig['REG_imp'].unique())[:20]}")
print()

print("="*80)
print("VALIDATION: EGY and MEX employment should match exactly")
print("="*80)
print()

# Check if EGY and MEX exist in original using correct codes
for country_code in ['EGY', 'MEX']:
    print(f"{country_code}:")
    print("-"*80)

    # Aggregated data
    agg_data = labor_agg[labor_agg['REG_imp'] == country_code]
    print(f"  Aggregated (SSP) - rows: {len(agg_data)}")

    # Original data - use same code
    orig_data = labor_orig[labor_orig['REG_imp'] == country_code]
    print(f"  Original (164) - rows: {len(orig_data)}")

    if len(orig_data) == 0:
        print(f"  [ERROR] {country_code} NOT FOUND in original data!")
        print(f"  Available countries sample: {sorted(labor_orig['REG_imp'].unique())[:30]}")
        continue

    if len(agg_data) != len(orig_data):
        print(f"  [ERROR] Row count mismatch!")
        continue

    # Compare Product 90 employment
    prod = 90
    agg_prod = agg_data[agg_data['PROD_COMM'] == prod]
    orig_prod = orig_data[orig_data['PROD_COMM'] == prod]

    if len(agg_prod) > 0 and len(orig_prod) > 0:
        agg_total = (agg_prod['vol_Fem_low'].values[0] + agg_prod['vol_Fem_high'].values[0] +
                    agg_prod['vol_Male_low'].values[0] + agg_prod['vol_Male_high'].values[0])
        orig_total = (orig_prod['vol_Fem_low'].values[0] + orig_prod['vol_Fem_high'].values[0] +
                     orig_prod['vol_Male_low'].values[0] + orig_prod['vol_Male_high'].values[0])

        print(f"  Product {prod} employment:")
        print(f"    Aggregated: {agg_total:,.0f} workers")
        print(f"    Original:   {orig_total:,.0f} workers")
        print(f"    Match: {abs(agg_total - orig_total) < 1}")

        if abs(agg_total - orig_total) >= 1:
            print(f"    [ERROR] Mismatch: {abs(agg_total - orig_total):,.0f} workers")
    print()

print("="*80)
print("CHECKING BASELINE OUTPUT (q_base) CONSISTENCY")
print("="*80)
print()

print("The issue might not be in labor_data.pkl aggregation, but in how")
print("q_base is calculated from L_BASE and Y_BASE matrices.")
print()
print("If L_BASE and Y_BASE were aggregated differently than labor_data.pkl,")
print("then empl_base/q_base ratios will be inconsistent.")
print()
print("RECOMMENDATION:")
print("1. Check if L_BASE, Y_BASE, G_BASE were created using aggregate_mat.py")
print("2. Check if labor_data.pkl was created using collapse_MRIO_SSP.py")
print("3. Verify both use the same R_grouping_SSP.xlsx mapping")
print("4. If created at different times, re-run ALL aggregation scripts together")
