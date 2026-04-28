"""
Compare how .mat files are defined in original vs SSP Variable_list
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Compare .mat file Type definitions")
print("="*80)

var_orig = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET.xlsx', 'variables')
var_ssp = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx', 'variables')

mat_files = ['L_BASE', 'G_BASE', 'Y_BASE']

for var_name in mat_files:
    print(f"\n{var_name}:")
    print("-"*40)

    orig = var_orig[var_orig['Variable name (new)'] == var_name]
    ssp = var_ssp[var_ssp['Variable name (new)'] == var_name]

    if len(orig) > 0:
        orig_type = orig['Type'].values[0]
        print(f"  Original Type: {orig_type}")
    else:
        print(f"  Original: NOT FOUND")

    if len(ssp) > 0:
        ssp_type = ssp['Type'].values[0]
        print(f"  SSP Type: {ssp_type}")
    else:
        print(f"  SSP: NOT FOUND")

print("\n" + "="*80)
print("How exog_vars.py loads .mat files:")
print("="*80)
print("\nFrom exog_vars.py lines 60-65:")
print('  elif path_value.endswith(".mat"):')
print('      value = scipy.io.loadmat(self.IO_PATH + path_value)')
print('      # Returns a dict with all keys from .mat file')
print("\nThen line 82:")
print('  setattr(self, key, value)')
print('  # Should assign the full dict to MRIO_BASE.L_BASE')

print("\n" + "="*80)
print("PROBLEM:")
print("="*80)
print("\nMRIO_BASE.L_BASE is an ndarray, not a dict!")
print("This means the dict was loaded, but then only the array was extracted.")
print("\nPossible causes:")
print("  1. exog_vars_SSP.py has different .mat loading code")
print("  2. Type='Matrix' triggers special processing")
print("  3. Post-processing extracts the array from the dict")
