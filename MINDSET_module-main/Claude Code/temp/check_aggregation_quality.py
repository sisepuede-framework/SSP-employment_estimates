"""
Check if labor_data.pkl was properly aggregated
"""
import sys
import os
import pandas as pd
import pickle as pkl

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("CHECKING LABOR DATA AGGREGATION QUALITY")
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
try:
    labor_orig = pd.read_pickle("GLORIA_db/v57/2019/parsed_db_original/labor_data.pkl")
    print(f"  Shape: {labor_orig.shape}")
    print(f"  Number of countries: {labor_orig['REG_imp'].nunique()}")
    print()

    # Check if aggregation was done correctly
    print("="*80)
    print("VALIDATION: Check if employment was summed correctly")
    print("="*80)
    print()

    # Load grouping to see which countries went into ROW
    grouping = pd.read_excel("GLORIA_template/Country_groupings/R_grouping_SSP.xlsx", sheet_name="groups")
    print(f"Grouping file loaded: {len(grouping)} countries")
    print()

    # Check total employment for Product 90
    print("Product 90 employment totals:")
    print("-"*80)

    # Aggregated data
    print("Aggregated (8 countries):")
    for country in ['ROW', 'EGY', 'MEX']:
        prod90 = labor_agg[(labor_agg['REG_imp'] == country) & (labor_agg['PROD_COMM'] == 90)]
        if len(prod90) > 0:
            total = (prod90['vol_Fem_low'].values[0] + prod90['vol_Fem_high'].values[0] +
                    prod90['vol_Male_low'].values[0] + prod90['vol_Male_high'].values[0])
            print(f"  {country}: {total:,.0f} workers")
    print()

    # Original data - check if EGY and MEX exist as individual countries
    print("Original (164 countries) - same countries:")
    for country in ['Egypt', 'Mexico']:
        prod90 = labor_orig[(labor_orig['REG_imp'] == country) & (labor_orig['PROD_COMM'] == 90)]
        if len(prod90) > 0:
            total = (prod90['vol_Fem_low'].values[0] + prod90['vol_Fem_high'].values[0] +
                    prod90['vol_Male_low'].values[0] + prod90['vol_Male_high'].values[0])
            print(f"  {country}: {total:,.0f} workers")
        else:
            print(f"  {country}: NOT FOUND")
    print()

    # Check which countries went into ROW
    row_countries = grouping[grouping['Agg_region'] == 'ROW']['Region_acronyms'].tolist()
    print(f"Countries aggregated into ROW: {len(row_countries)}")
    print(f"  Sample: {row_countries[:10]}")
    print()

    # Sum Product 90 employment for all ROW countries
    row_total = 0
    for country in row_countries:
        prod90 = labor_orig[(labor_orig['REG_imp'] == country) & (labor_orig['PROD_COMM'] == 90)]
        if len(prod90) > 0:
            total = (prod90['vol_Fem_low'].values[0] + prod90['vol_Fem_high'].values[0] +
                    prod90['vol_Male_low'].values[0] + prod90['vol_Male_high'].values[0])
            row_total += total

    print(f"Sum of all countries that became ROW (Product 90): {row_total:,.0f} workers")

    row_agg = labor_agg[(labor_agg['REG_imp'] == 'ROW') & (labor_agg['PROD_COMM'] == 90)]
    row_agg_total = (row_agg['vol_Fem_low'].values[0] + row_agg['vol_Fem_high'].values[0] +
                     row_agg['vol_Male_low'].values[0] + row_agg['vol_Male_high'].values[0])
    print(f"ROW in aggregated file (Product 90): {row_agg_total:,.0f} workers")
    print()

    if abs(row_total - row_agg_total) < 1:
        print("[OK] ROW aggregation is correct!")
    else:
        print(f"[ERROR] ROW aggregation mismatch: {abs(row_total - row_agg_total):,.0f} difference")

except FileNotFoundError:
    print("  [NOT FOUND] Original labor_data.pkl not found")
    print("  Cannot validate aggregation")

print()
print("="*80)
