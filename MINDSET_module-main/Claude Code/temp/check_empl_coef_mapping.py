"""
Check EMPL_COEF mapping to aggregated countries
"""
import sys
import os
import pandas as pd

sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.employment import empl

print("="*80)
print("CHECKING EMPL_COEF MAPPING")
print("="*80)
print()

MRIO_BASE = exog_vars()

print("STEP 1: Check HH_CONS_COU mapping")
print("-"*80)
print(f"HH_CONS_COU shape: {MRIO_BASE.HH_CONS_COU.shape}")
print(f"Columns: {list(MRIO_BASE.HH_CONS_COU.columns)}")
print()
print("First 20 rows:")
print(MRIO_BASE.HH_CONS_COU.head(20))
print()

print("Unique aggregated countries:")
print(MRIO_BASE.HH_CONS_COU['Country_Code'].unique())
print()

print("STEP 2: Build employment coefficients")
print("-"*80)
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

print(f"After build_empl_coef:")
print(f"  Shape: {Empl_model.EMPL_COEF.shape}")
print(f"  Columns: {list(Empl_model.EMPL_COEF.columns)}")
print()
print("First 20 rows:")
print(Empl_model.EMPL_COEF.head(20))
print()

print("Countries in final EMPL_COEF:")
print(Empl_model.EMPL_COEF['REG_imp'].unique())
print()

print("STEP 3: Check coefficients for EGY and MEX")
print("-"*80)
for country in ['EGY', 'MEX']:
    country_coef = Empl_model.EMPL_COEF[Empl_model.EMPL_COEF['REG_imp'] == country]
    print(f"{country}:")
    print(f"  Number of products: {len(country_coef)}")
    print(f"  Non-zero coefficients: {(country_coef['empl_coef'] != 0).sum()}")
    print(f"  Zero coefficients: {(country_coef['empl_coef'] == 0).sum()}")
    print(f"  Min coefficient: {country_coef['empl_coef'].min():.6f}")
    print(f"  Max coefficient: {country_coef['empl_coef'].max():.6f}")
    print(f"  Mean coefficient: {country_coef['empl_coef'].mean():.6f}")
    print()
    print("  Sample products (10, 50, 90):")
    for prod in [10, 50, 90]:
        prod_coef = country_coef[country_coef['PROD_COMM'] == prod]['empl_coef'].values
        if len(prod_coef) > 0:
            print(f"    Product {prod}: {prod_coef[0]:.6f}")
        else:
            print(f"    Product {prod}: MISSING")
    print()

print("="*80)
