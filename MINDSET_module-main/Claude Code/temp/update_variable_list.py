"""
Add L_BASE entry to Variable_list_MINDSET_SSP.xlsx
This ensures L_BASE is loaded from the parsed_db_original folder
"""

import pandas as pd
import openpyxl

var_path = 'GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx'

print("=" * 80)
print("Updating Variable_list_MINDSET_SSP.xlsx for L_BASE")
print("=" * 80)
print()

# Read the existing variables sheet
var_data = pd.read_excel(var_path, 'variables')

print(f"Current variables: {len(var_data)} rows")
print()

# Check if L_BASE already exists
l_base_exists = 'L_BASE' in var_data['Variable name (new)'].values

if l_base_exists:
    print("OK L_BASE already exists in Variable_list")
    # Update the location
    idx = var_data[var_data['Variable name (new)'] == 'L_BASE'].index[0]
    old_location = var_data.loc[idx, 'Location']
    new_location = r'GLORIA_db\v57\2019\parsed_db_original\GLORIA_L_Base_2019.mat'

    print(f"  Old location: {old_location}")
    print(f"  New location: {new_location}")

    var_data.loc[idx, 'Location'] = new_location
    print("  OK Updated location")
else:
    print("X L_BASE not found - adding new entry")

    # Create new row for L_BASE
    new_row = {
        'Variable name (new)': 'L_BASE',
        'Location': r'GLORIA_db\v57\2019\parsed_db_original\GLORIA_L_Base_2019.mat',
        'Type': 'DataFrame',  # It's actually a matrix but loaded as dict
        'Notes': 'Leontief inverse matrix - calculated from A matrix'
    }

    # Add the new row
    var_data = pd.concat([var_data, pd.DataFrame([new_row])], ignore_index=True)
    print(f"  OK Added L_BASE entry")

print()

# Save back to Excel
try:
    # Write updated variables sheet (overwrites entire file)
    with pd.ExcelWriter(var_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        var_data.to_excel(writer, sheet_name='variables', index=False)

    print("OK Variable_list_MINDSET_SSP.xlsx updated successfully!")
    print()
    print("L_BASE will now be loaded from:")
    print("  GLORIA_db\\v57\\2019\\parsed_db_original\\GLORIA_L_Base_2019.mat")

except Exception as e:
    print(f"X Error updating Excel file: {e}")
    print()
    print("Manual update needed:")
    print("1. Open: GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx")
    print("2. Go to 'variables' sheet")
    if l_base_exists:
        print("3. Find L_BASE row")
        print("4. Update 'Location' column to:")
    else:
        print("3. Add new row:")
        print("   - Variable name (new): L_BASE")
        print("   - Location:")
    print(r"      GLORIA_db\v57\2019\parsed_db_original\GLORIA_L_Base_2019.mat")
    print("   - Type: DataFrame")
