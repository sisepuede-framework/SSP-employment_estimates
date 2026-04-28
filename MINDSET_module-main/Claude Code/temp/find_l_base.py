"""
Find where L_BASE is coming from
"""
import os
import pandas as pd

# Check Variable_list
var_path = 'GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx'
var_data = pd.read_excel(var_path, 'variables')

l_base = var_data[var_data['Variable name (new)'] == 'L_BASE']
if len(l_base) > 0:
    location = l_base['Location'].values[0]
    print(f"Variable_list says L_BASE is at:")
    print(f"  {location}")
    print()

    full_path = os.path.join(os.getcwd(), location)
    print(f"Full path:")
    print(f"  {full_path}")
    print()

    if os.path.exists(full_path):
        size = os.path.getsize(full_path)
        print(f"File EXISTS")
        print(f"  Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
    else:
        print(f"File DOES NOT EXIST")
else:
    print("L_BASE not configured in Variable_list")

# Check for any .mat files
print()
print("Searching for any GLORIA_L_Base*.mat files...")
for root, dirs, files in os.walk('GLORIA_db'):
    for file in files:
        if 'L_Base' in file and file.endswith('.mat'):
            full_path = os.path.join(root, file)
            size = os.path.getsize(full_path)
            print(f"  Found: {full_path}")
            print(f"    Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
