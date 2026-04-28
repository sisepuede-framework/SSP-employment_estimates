"""
Update L_BASE location in Variable_list_MINDSET_SSP.xlsx
"""

import pandas as pd

var_path = 'GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx'

print("Updating Variable_list_MINDSET_SSP.xlsx...")

# Read all sheets
excel_file = pd.ExcelFile(var_path)
all_sheets = {sheet: pd.read_excel(var_path, sheet_name=sheet) for sheet in excel_file.sheet_names}

# Update variables sheet
var_data = all_sheets['variables']

# Find and update L_BASE
if 'L_BASE' in var_data['Variable name (new)'].values:
    idx = var_data[var_data['Variable name (new)'] == 'L_BASE'].index[0]
    old_loc = var_data.loc[idx, 'Location']
    new_loc = r'GLORIA_db\v57\2019\parsed_db_original\GLORIA_L_Base_2019.mat'
    var_data.loc[idx, 'Location'] = new_loc

    print(f"Updated L_BASE location:")
    print(f"  From: {old_loc}")
    print(f"  To:   {new_loc}")

    # Save all sheets back
    with pd.ExcelWriter(var_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            if sheet_name == 'variables':
                var_data.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    print("OK - File updated successfully!")
else:
    print("ERROR: L_BASE not found in variables sheet")
