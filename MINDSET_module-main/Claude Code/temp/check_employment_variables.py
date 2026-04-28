"""
Check what employment variables are in Variable_list_MINDSET_SSP.xlsx
"""
import pandas as pd

var_path = "GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx"
var_data = pd.read_excel(var_path, "variables")

print("Employment-related variables in Variable_list_MINDSET_SSP.xlsx:")
print("="*80)

empl_vars = var_data[var_data['Variable name (new)'].str.contains('EMPL|empl|LABOR|labor', na=False, case=False)]

for _, row in empl_vars.iterrows():
    var_name = row['Variable name (new)']
    location = row['Location']
    print(f"\n{var_name}:")
    print(f"  Location: {location}")
    if pd.notna(location):
        if 'parsed_db_original' in str(location):
            print("  ⚠ WARNING: Still points to parsed_db_original (164 countries)")
            print(f"  → Should be: {str(location).replace('parsed_db_original', 'SSP')}")
        elif 'SSP' in str(location):
            print("  ✓ Correctly points to SSP folder (8 regions)")
