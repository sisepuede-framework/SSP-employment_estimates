"""
Check EMPL_COEF data from MINDSET
"""
import sys
import os
import pandas as pd

sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars

print("="*80)
print("CHECKING EMPL_COEF DATA")
print("="*80)
print()

MRIO_BASE = exog_vars()

print("STEP 1: Check if EMPL_COEF exists")
print("-"*80)
if hasattr(MRIO_BASE, 'EMPL_COEF'):
    print(f"[OK] EMPL_COEF loaded")
    print(f"  Shape: {MRIO_BASE.EMPL_COEF.shape}")
    print(f"  Columns: {list(MRIO_BASE.EMPL_COEF.columns[:10])}...")
    print()
    print("First 10 rows:")
    print(MRIO_BASE.EMPL_COEF.head(10))
    print()

    print("Data summary:")
    print(f"  Non-zero values: {(MRIO_BASE.EMPL_COEF.select_dtypes(include='number') != 0).sum().sum()}")
    print(f"  Zero values: {(MRIO_BASE.EMPL_COEF.select_dtypes(include='number') == 0).sum().sum()}")
    print()
else:
    print("[ERROR] EMPL_COEF not found in MRIO_BASE")
    print("Available attributes:")
    attrs = [attr for attr in dir(MRIO_BASE) if not attr.startswith('_')]
    print(attrs)
print()

print("STEP 2: Check Variable_list_MINDSET_SSP.xlsx")
print("-"*80)
var_list = pd.read_excel("GLORIA_db/v57/2019/SSP/Variable_list_MINDSET_SSP.xlsx")
empl_coef_row = var_list[var_list['Variable name'] == 'EMPL_COEF']
if len(empl_coef_row) > 0:
    print("[OK] EMPL_COEF defined in Variable_list")
    print(empl_coef_row[['Variable name', 'Path', 'Type']].to_string(index=False))
else:
    print("[ERROR] EMPL_COEF not defined in Variable_list_MINDSET_SSP.xlsx")
print()

print("="*80)
