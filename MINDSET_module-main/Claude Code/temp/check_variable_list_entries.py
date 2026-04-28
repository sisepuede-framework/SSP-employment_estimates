"""
Check INV_BASE and NPISH_BASE entries in Variable_list_MINDSET_SSP.xlsx
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Check Variable_list_MINDSET_SSP.xlsx entries")
print("="*80)

var_list = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx', 'variables')

print("\nAll _BASE variables:")
print("-"*80)
base_vars = var_list[var_list['Variable name (new)'].str.contains('_BASE', na=False)]
print(base_vars[['Variable name (new)', 'Location', 'Type']])

print("\n" + "="*80)
print("Check INV_BASE and NPISH_BASE specifically:")
print("="*80)

for var_name in ['INV_BASE', 'NPISH_BASE']:
    print(f"\n{var_name}:")
    print("-"*40)
    var_entry = var_list[var_list['Variable name (new)'] == var_name]

    if len(var_entry) > 0:
        location = var_entry['Location'].values[0]
        var_type = var_entry['Type'].values[0]
        print(f"  ✓ Found in Variable_list")
        print(f"  Location: {location}")
        print(f"  Type: {var_type}")

        # Check if file exists
        if pd.notna(location):
            if os.path.exists(location):
                print(f"  ✓ File exists at: {location}")
            else:
                print(f"  ✗ File NOT found at: {location}")
                print(f"  → Check path is correct")
        else:
            print(f"  ✗ Location is NaN/empty")

        # Check if Type is correct
        if pd.notna(var_type):
            if var_type == 'DataFrame':
                print(f"  ✓ Type is 'DataFrame'")
            else:
                print(f"  ✗ Type is '{var_type}' (should be 'DataFrame')")
        else:
            print(f"  ✗ Type is NaN/empty")
    else:
        print(f"  ✗ NOT found in Variable_list")
        print(f"  → You need to add this entry manually")

print("\n" + "="*80)
print("What entries should look like:")
print("="*80)
print("\nINV_BASE:")
print("  Variable name (new): INV_BASE")
print("  Location: GLORIA_db\\v57\\2019\\SSP\\inv.pkl")
print("  Type: DataFrame")
print("\nNPISH_BASE:")
print("  Variable name (new): NPISH_BASE")
print("  Location: GLORIA_db\\v57\\2019\\SSP\\npish.pkl")
print("  Type: DataFrame")
