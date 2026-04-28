"""
Check if empl_data.pkl (from GLORIA parsing) has our 7 countries
"""
import pandas as pd
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("CHECKING empl_data.pkl FROM GLORIA PARSED DATABASE")
print("="*80)

# Load the raw employment data from GLORIA parsing
empl_data = pd.read_pickle("GLORIA_db/v57/2019/parsed_db_original/empl_data.pkl")

print(f"\nempl_data.pkl structure:")
print(f"Shape: {empl_data.shape}")
print(f"Columns: {list(empl_data.columns)}")
print(f"\nFirst 10 rows:")
print(empl_data.head(10))

print(f"\nUnique REG_imp values: {len(empl_data['REG_imp'].unique())}")
print(f"All regions: {sorted(empl_data['REG_imp'].unique())}")

# Check our 7 countries
print("\n" + "="*80)
print("CHECKING OUR 7 COUNTRIES")
print("="*80)

selected_countries = ['BGR', 'BLZ', 'EGY', 'LBY', 'MAR', 'MEX', 'UGA']

for country in selected_countries:
    country_data = empl_data[empl_data['REG_imp'] == country]
    if len(country_data) > 0:
        # Check if employment values are non-zero
        has_data = any([
            (country_data['Empl_Female'] != 0).any(),
            (country_data['Empl_Male'] != 0).any(),
            (country_data['Empl_low'] != 0).any(),
            (country_data['Empl_mid'] != 0).any(),
            (country_data['Empl_high'] != 0).any()
        ])
        status = "✓ HAS DATA" if has_data else "⚠ EXISTS BUT ALL ZEROS"
        print(f"{country}: {status} ({len(country_data)} sectors)")
        if has_data:
            # Show sample values
            print(f"  Sample total employment (Male+Female):")
            total_empl = country_data['Empl_Female'] + country_data['Empl_Male']
            top_3 = total_empl.nlargest(3)
            for idx in top_3.index:
                sector = country_data.loc[idx, 'PROD_COMM']
                print(f"    Sector {sector}: {top_empl.loc[idx]:,.0f} workers")
    else:
        print(f"{country}: ✗ NOT FOUND")

print("\n" + "="*80)
print("COMPARISON WITH WHAT exog_vars LOADS")
print("="*80)

# Load what exog_vars loads
from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()

print(f"\nEMPL_COEF loaded by exog_vars (before build_empl_coef):")
print(f"Type: {type(MRIO_BASE.EMPL_COEF)}")
print(f"Shape: {MRIO_BASE.EMPL_COEF.shape}")
print(f"Columns: {list(MRIO_BASE.EMPL_COEF.columns[:5])} ... (showing first 5)")
print(f"Total columns: {len(MRIO_BASE.EMPL_COEF.columns)}")

# Check if they're the same
print("\n" + "="*80)
print("DIAGNOSIS")
print("="*80)

if MRIO_BASE.EMPL_COEF.shape == empl_data.shape:
    print("\n✓ EMPL_COEF has same shape as empl_data.pkl")
    print("  Variable_list correctly points to empl_data.pkl")
    print("\n  → Employment data EXISTS for your countries!")
    print("  → The issue is in build_empl_coef() processing or HH_CONS_COU mapping")
else:
    print("\n✗ EMPL_COEF has DIFFERENT shape from empl_data.pkl")
    print(f"  EMPL_COEF: {MRIO_BASE.EMPL_COEF.shape}")
    print(f"  empl_data: {empl_data.shape}")
    print("\n  → Variable_list may point to an aggregated file instead of empl_data.pkl")
    print("  → This aggregated file might only have ROW, not individual countries")

    print("\n  RECOMMENDATION: Modify Variable_list_MINDSET_SSP.xlsx to point to:")
    print(f"    GLORIA_db\\v57\\2019\\parsed_db_original\\empl_data.pkl")
