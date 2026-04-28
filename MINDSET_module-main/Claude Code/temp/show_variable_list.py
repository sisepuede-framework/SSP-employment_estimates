"""
Show what Variable_list_MINDSET_SSP.xlsx specifies for HH_CONS_COU and EMPL_COEF
"""
import pandas as pd

var_path = "GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx"

# Load variables sheet
var_data = pd.read_excel(var_path, "variables")

print("="*80)
print("VARIABLE_LIST_MINDSET_SSP.xlsx - variables sheet")
print("="*80)
print(f"\nTotal variables: {len(var_data)}")
print(f"\nColumns: {list(var_data.columns)}")

# Find HH_CONS_COU and EMPL_COEF
print("\n" + "="*80)
print("HH_CONS_COU entry:")
print("="*80)
hh_cons_cou_row = var_data[var_data['Variable name (new)'] == 'HH_CONS_COU']
if len(hh_cons_cou_row) > 0:
    print(hh_cons_cou_row.to_string())
    print(f"\nFile location: {hh_cons_cou_row['Location'].values[0]}")
    print(f"File type: {hh_cons_cou_row['Type'].values[0]}")
else:
    print("NOT FOUND")

print("\n" + "="*80)
print("EMPL_COEF entry:")
print("="*80)
empl_coef_row = var_data[var_data['Variable name (new)'] == 'EMPL_COEF']
if len(empl_coef_row) > 0:
    print(empl_coef_row.to_string())
    print(f"\nFile location: {empl_coef_row['Location'].values[0]}")
    print(f"File type: {empl_coef_row['Type'].values[0]}")
else:
    print("NOT FOUND")

# Show all rows related to employment
print("\n" + "="*80)
print("All employment-related entries:")
print("="*80)
empl_rows = var_data[var_data['Variable name (new)'].str.contains('EMPL|empl', na=False, case=False)]
print(empl_rows[['Variable name (new)', 'Location', 'Type']].to_string())
