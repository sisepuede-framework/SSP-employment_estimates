"""
Check the actual column names in Variable_list_MINDSET_SSP.xlsx
"""
import pandas as pd

var_path = "GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx"

print("=" * 80)
print("R SHEET")
print("=" * 80)
R = pd.read_excel(var_path, 'R')
print(f"Columns: {list(R.columns)}")
print(f"\nFirst 5 rows:")
print(R.head())
print(f"\nTotal rows: {len(R)}")

print("\n" + "=" * 80)
print("P SHEET")
print("=" * 80)
P = pd.read_excel(var_path, 'P')
print(f"Columns: {list(P.columns)}")
print(f"\nFirst 5 rows:")
print(P.head())
print(f"\nTotal rows: {len(P)}")
