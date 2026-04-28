"""
Check where Y_BASE points to in both Variable_list files
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Y_BASE location in ORIGINAL Variable_list")
print("="*80)
var_orig = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET.xlsx', 'variables')
y_base_orig = var_orig[var_orig['Variable name (new)'] == 'Y_BASE']
print(y_base_orig[['Variable name (new)', 'Location']])

print("\n" + "="*80)
print("Y_BASE location in SSP Variable_list")
print("="*80)
var_ssp = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx', 'variables')
y_base_ssp = var_ssp[var_ssp['Variable name (new)'] == 'Y_BASE']
print(y_base_ssp[['Variable name (new)', 'Location']])

print("\n" + "="*80)
print("Analysis:")
print("="*80)
orig_path = y_base_orig['Location'].values[0] if len(y_base_orig) > 0 else None
ssp_path = y_base_ssp['Location'].values[0] if len(y_base_ssp) > 0 else None

print(f"Original points to: {orig_path}")
print(f"SSP points to: {ssp_path}")

if orig_path == ssp_path:
    print("\n⚠ WARNING: Both point to the SAME file!")
    print("   SSP should point to SSP\\GLORIA_Y_Base_2019.mat (8 regions)")
    print("   But currently points to original (164 countries)")
elif ssp_path and 'SSP' in str(ssp_path):
    print("\n✓ SSP correctly points to SSP folder")
    if os.path.exists(ssp_path):
        print(f"  File exists: {ssp_path}")
    else:
        print(f"  ✗ File MISSING: {ssp_path}")
        print("  → Need to create Y_BASE for SSP (requires INV_BASE and NPISH_BASE)")
