"""
Compare Variable_list entries between original and SSP
Identify missing entries needed for SSP version
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Comparing Variable_list files")
print("="*80)

var_orig = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET.xlsx', 'variables')
var_ssp = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx', 'variables')

print("\nAll .pkl DataFrame variables in ORIGINAL:")
pkl_df_orig = var_orig[(var_orig['Location'].str.contains('.pkl', na=False)) &
                        (var_orig['Type'] == 'DataFrame')]
print(pkl_df_orig[['Variable name (new)', 'Location']])

print("\n" + "="*80)
print("All .pkl DataFrame variables in SSP:")
pkl_df_ssp = var_ssp[(var_ssp['Location'].str.contains('.pkl', na=False)) &
                      (var_ssp['Type'] == 'DataFrame')]
print(pkl_df_ssp[['Variable name (new)', 'Location']])

print("\n" + "="*80)
print("Variables in ORIGINAL but not in SSP:")
orig_vars = set(pkl_df_orig['Variable name (new)'])
ssp_vars = set(pkl_df_ssp['Variable name (new)'])
missing = orig_vars - ssp_vars
if missing:
    print(missing)
    print("\n→ These may need to be added to SSP Variable_list")
else:
    print("None - all variables present")

print("\n" + "="*80)
print("Check if INV and NPISH files exist in SSP folder:")
import os
ssp_path = "GLORIA_db/v57/2019/SSP/"
for filename in ['inv.pkl', 'npish.pkl']:
    filepath = ssp_path + filename
    if os.path.exists(filepath):
        print(f"✓ {filename} EXISTS")
    else:
        print(f"✗ {filename} MISSING")
