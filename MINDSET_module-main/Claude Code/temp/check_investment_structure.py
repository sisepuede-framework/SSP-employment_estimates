"""
Check the structure of investment data in Strategy_1004_MEX.xlsx
to understand if it's already a demand vector or needs conversion
"""
import sys
import os
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("CHECK INVESTMENT DATA STRUCTURE")
print("="*80)
print()

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass

MRIO_BASE = exog_vars()
scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
Scenario.set_exog_inv()

print("Investment data from Strategy_1004_MEX.xlsx:")
print("-"*80)
print(f"Shape: {Scenario.inv_exog.shape}")
print(f"Columns: {list(Scenario.inv_exog.columns)}")
print(f"\nTotal investment: ${Scenario.inv_exog['dk'].sum():,.2f}")
print(f"\nFirst 10 rows:")
print(Scenario.inv_exog.head(10))
print()

print("="*80)
print("ANALYSIS:")
print("="*80)
print()
print("Column meanings:")
print("  REG_imp: Country where investment happens")
print("  PROD_COMM: Product/sector code (1-120)")
print("  dk: Investment amount in that product")
print()
print(f"Number of products with investment: {(Scenario.inv_exog['dk'] > 0).sum()}")
print(f"These are the products you want to purchase with $1M")
print()

print("Investment by product (non-zero only):")
print("-"*80)
inv_nonzero = Scenario.inv_exog[Scenario.inv_exog['dk'] > 0].copy()
inv_nonzero = inv_nonzero.sort_values('dk', ascending=False)
for idx, row in inv_nonzero.iterrows():
    product = row['PROD_COMM']
    amount = row['dk']
    share = amount / Scenario.inv_exog['dk'].sum() * 100
    print(f"  Product {int(product):3d}: ${amount:12,.2f} ({share:5.1f}%)")

print()
print("="*80)
print("QUESTION:")
print("="*80)
print()
print("Is this data structure:")
print()
print("A) Already a final demand vector?")
print("   → Products specified, amounts sum to $1M")
print("   → Ready to use directly: dy_inv_exog = inv_exog['dk']")
print("   → Skip INV_model conversion")
print()
print("B) Investment BY SECTOR that needs conversion?")
print("   → Needs INV_CONV to map to products")
print("   → Needs fcf_share to distribute across exporters")
print("   → Use INV_model.calc_dy_inv_exog()")
print()
print("Based on your description, it sounds like (A).")
print("The investment module conversion might be transforming already-correct data.")
