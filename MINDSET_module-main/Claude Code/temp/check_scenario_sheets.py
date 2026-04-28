"""
Check what sheets exist in Strategy_1004_MEX.xlsx
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"

print("="*80)
print(f"Sheets in {scenario_file}:")
print("="*80)

xl = pd.ExcelFile(scenario_file)
for i, sheet in enumerate(xl.sheet_names, 1):
    print(f"{i:2d}. {sheet}")

print("\n" + "="*80)
print("Sheets needed by prod_cost module:")
print("="*80)
print("  - payr_tax_split (for payroll tax split)")
print("  - rev_proportional (for revenue allocation)")

required_sheets = ['payr_tax_split', 'rev_proportional']
for sheet in required_sheets:
    if sheet in xl.sheet_names:
        print(f"\n✓ '{sheet}' exists")
    else:
        print(f"\n✗ '{sheet}' MISSING")
