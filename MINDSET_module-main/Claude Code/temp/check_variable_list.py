"""
Check Variable_list_MINDSET_SSP.xlsx structure to understand country selection
"""
import pandas as pd

var_path = "GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx"

# Check all sheets
xl = pd.ExcelFile(var_path)
print("=" * 80)
print("SHEETS IN Variable_list_MINDSET_SSP.xlsx")
print("=" * 80)
print(xl.sheet_names)
print()

# Read variables sheet
print("=" * 80)
print("VARIABLES SHEET - Shows where COU_ID and SEC_ID come from")
print("=" * 80)
var_data = pd.read_excel(var_path, "variables")
print(var_data[var_data['Variable name (new)'].str.contains('COU_ID|SEC_ID', na=False)])
print()

# Read R sheet (regions)
print("=" * 80)
print("R SHEET - Selected Regions")
print("=" * 80)
R_data = pd.read_excel(var_path, 'R')
print(R_data)
print(f"\nTotal regions: {len(R_data)}")
print()

# Read P sheet (products/sectors)
print("=" * 80)
print("P SHEET - Sectors")
print("=" * 80)
P_data = pd.read_excel(var_path, 'P')
print(f"Total sectors: {len(P_data)}")
