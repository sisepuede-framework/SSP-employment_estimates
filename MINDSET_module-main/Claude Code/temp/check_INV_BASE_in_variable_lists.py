"""
Check if INV_BASE is defined in Variable_list files
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("ORIGINAL Variable_list_MINDSET.xlsx")
print("="*80)
var_orig = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET.xlsx', 'variables')
base_vars_orig = var_orig[var_orig['Variable name (new)'].str.contains('_BASE', na=False)]
print(base_vars_orig[['Variable name (new)', 'Location']])

print("\n" + "="*80)
print("SSP Variable_list_MINDSET_SSP.xlsx")
print("="*80)
var_ssp = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx', 'variables')
base_vars_ssp = var_ssp[var_ssp['Variable name (new)'].str.contains('_BASE', na=False)]
print(base_vars_ssp[['Variable name (new)', 'Location']])

print("\n" + "="*80)
print("Check specifically for INV_BASE")
print("="*80)
inv_base_orig = var_orig[var_orig['Variable name (new)'] == 'INV_BASE']
inv_base_ssp = var_ssp[var_ssp['Variable name (new)'] == 'INV_BASE']

if len(inv_base_orig) > 0:
    print("✓ INV_BASE found in original:")
    print(inv_base_orig[['Variable name (new)', 'Location', 'Type']])
else:
    print("✗ INV_BASE NOT found in original Variable_list")

if len(inv_base_ssp) > 0:
    print("\n✓ INV_BASE found in SSP:")
    print(inv_base_ssp[['Variable name (new)', 'Location', 'Type']])
else:
    print("\n✗ INV_BASE NOT found in SSP Variable_list")
    print("\n→ Need to ADD INV_BASE entry pointing to SSP/inv.pkl")
