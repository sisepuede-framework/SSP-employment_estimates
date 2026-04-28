"""
Check LABOR_BASE structure and data quality
"""
import sys
import os
import pandas as pd
sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars

MRIO_BASE = exog_vars()

print("="*80)
print("LABOR_BASE STRUCTURE CHECK")
print("="*80)
print()

print("LABOR_BASE shape:", MRIO_BASE.LABOR_BASE.shape)
print("LABOR_BASE columns:", list(MRIO_BASE.LABOR_BASE.columns))
print()

print("Sample data (first 10 rows):")
print("-"*80)
print(MRIO_BASE.LABOR_BASE.head(10))
print()

print("Countries in LABOR_BASE:")
print(MRIO_BASE.LABOR_BASE['REG_imp'].unique())
print()

print("Products per country:")
for country in ['EGY', 'MEX']:
    n_products = len(MRIO_BASE.LABOR_BASE[MRIO_BASE.LABOR_BASE['REG_imp'] == country])
    print(f"  {country}: {n_products} products")
print()

print("="*80)
print("CHECKING PRODUCT 90 DATA")
print("="*80)
print()

for country in ['EGY', 'MEX']:
    print(f"{country} - Product 90:")
    prod_data = MRIO_BASE.LABOR_BASE[
        (MRIO_BASE.LABOR_BASE['REG_imp'] == country) &
        (MRIO_BASE.LABOR_BASE['PROD_COMM'] == 90)
    ]
    if len(prod_data) > 0:
        print(prod_data.to_string(index=False))
    else:
        print("  [MISSING]")
    print()

print("="*80)
print("CHECKING IF LABOR_BASE IS ORIGINAL GLORIA DATA OR AGGREGATED")
print("="*80)
print()
print("Expected for 8-country MRIO: 8 countries × 120 products = 960 rows")
print(f"Actual LABOR_BASE rows: {len(MRIO_BASE.LABOR_BASE)}")
print()

if len(MRIO_BASE.LABOR_BASE) == 960:
    print("[OK] LABOR_BASE matches expected 8-country structure")
elif len(MRIO_BASE.LABOR_BASE) > 960:
    print("[WARNING] LABOR_BASE has MORE rows than expected")
    print("  This might contain original GLORIA data (164 countries)")
    print("  Needs aggregation to 8 countries!")
else:
    print("[WARNING] LABOR_BASE has FEWER rows than expected")
print()

# Check if there's aggregation information
print("Checking Variable_list to see where LABOR_BASE comes from:")
try:
    var_list = pd.read_excel("GLORIA_db/Variable_list_MINDSET_SSP.xlsx")
    labor_row = var_list[var_list['Variable name'] == 'LABOR_BASE']
    if len(labor_row) > 0:
        print(labor_row[['Variable name', 'Path', 'Type']].to_string(index=False))
    else:
        print("[NOT FOUND] LABOR_BASE not in Variable_list_MINDSET_SSP.xlsx")
except Exception as e:
    print(f"[ERROR] Could not read Variable_list: {e}")
