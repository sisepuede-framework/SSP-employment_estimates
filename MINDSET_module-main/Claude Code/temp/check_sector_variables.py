"""
Check sector-related variables in Variable_list_MINDSET_SSP.xlsx
"""
import pandas as pd

var_path = "GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx"
var_data = pd.read_excel(var_path, "variables")

print("Sector-related variables in Variable_list_MINDSET_SSP.xlsx:")
print("="*80)

# Look for sid, sec, COU_ID, SEC_ID
sector_vars = var_data[var_data['Variable name (new)'].isin(['COU_ID', 'SEC_ID', 'COU_NAME', 'SEC_NAME'])]

for _, row in sector_vars.iterrows():
    var_name = row['Variable name (new)']
    location = row['Location']
    var_type = row['Type']
    print(f"\n{var_name} ({var_type}):")
    print(f"  Location: {location}")
    if pd.notna(location):
        if 'SSP' in str(location):
            print("  → Points to SSP folder")
        elif 'parsed_db_original' in str(location):
            print("  → Points to parsed_db_original folder")
