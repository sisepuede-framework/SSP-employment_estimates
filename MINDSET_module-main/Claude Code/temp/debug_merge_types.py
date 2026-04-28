import pandas as pd
import numpy as np
import sys
import os

# Add MINDSET to path
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.investment import invest

# Mock logger
class MockLog:
    def log_to_csv(self, *args, **kwargs):
        pass
    def log(self, *args, **kwargs):
        pass

print("=" * 80)
print("DEBUG: Data Type Analysis in Investment Converter")
print("=" * 80)
print()

# Load MRIO data
print("Loading MRIO data...")
MRIO_BASE = exog_vars()
print(f"Loaded.\n")

# Load scenario
scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
Scenario_Log = MockLog()
Scenario = scenario(MRIO_BASE, scenario_file, Scenario_Log)
Scenario.set_exog_inv()

# Set default inv_spending
if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

# Initialize investment module
INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()

print("=" * 80)
print("ANALYZING DATA TYPES BEFORE MERGE")
print("=" * 80)
print()

# Prepare exog_inv like the function does
exog_inv = Scenario.inv_exog.loc[:,["REG_imp","PROD_COMM","dk"]]
print("1. exog_inv BEFORE type conversion:")
print(f"   Shape: {exog_inv.shape}")
print(f"   PROD_COMM dtype: {exog_inv['PROD_COMM'].dtype}")
print(f"   REG_imp dtype: {exog_inv['REG_imp'].dtype}")
print(f"   Sample PROD_COMM values: {exog_inv['PROD_COMM'].head(10).tolist()}")
print(f"   Sample REG_imp values: {exog_inv['REG_imp'].head(10).tolist()}")
print()

# Convert PROD_COMM to string (line 223)
exog_inv["PROD_COMM"] = exog_inv['PROD_COMM'].astype(str)
print("2. exog_inv AFTER converting PROD_COMM to string:")
print(f"   PROD_COMM dtype: {exog_inv['PROD_COMM'].dtype}")
print(f"   Sample PROD_COMM values: {exog_inv['PROD_COMM'].head(10).tolist()}")
print()

# Get inv_conv
inv_conv = INV_model.INV_CONV
print("3. inv_conv (INV_CONV):")
print(f"   Shape: {inv_conv.shape}")
print(f"   Columns: {list(inv_conv.columns)}")
print(f"   PROD_COMM dtype: {inv_conv['PROD_COMM'].dtype}")
print(f"   REG_imp dtype: {inv_conv['REG_imp'].dtype}")
print(f"   Sample PROD_COMM values: {inv_conv['PROD_COMM'].head(10).tolist()}")
print(f"   Sample REG_imp values: {inv_conv['REG_imp'].head(10).tolist()}")
print()

print("=" * 80)
print("CHECKING FOR MATCHES")
print("=" * 80)
print()

print("4. Unique values in exog_inv:")
print(f"   Unique PROD_COMM: {sorted(exog_inv['PROD_COMM'].unique())[:20]}")
print(f"   Unique REG_imp: {exog_inv['REG_imp'].unique()}")
print()

print("5. Unique values in inv_conv:")
print(f"   Unique PROD_COMM: {sorted(inv_conv['PROD_COMM'].unique())[:20]}")
print(f"   Unique REG_imp: {sorted(inv_conv['REG_imp'].unique())}")
print()

# Check for matching PROD_COMM values
exog_prod_set = set(exog_inv['PROD_COMM'].unique())
inv_prod_set = set(inv_conv['PROD_COMM'].astype(str).unique())
matching_prod = exog_prod_set.intersection(inv_prod_set)
print(f"6. PROD_COMM matching analysis:")
print(f"   Exog_inv unique PROD_COMM: {len(exog_prod_set)}")
print(f"   Inv_conv unique PROD_COMM: {len(inv_prod_set)}")
print(f"   Matching PROD_COMM: {len(matching_prod)}")
if len(matching_prod) > 0:
    print(f"   Sample matches: {list(matching_prod)[:10]}")
else:
    print(f"   NO MATCHES FOUND!")
print()

# Check for matching REG_imp values
exog_reg_set = set(exog_inv['REG_imp'].unique())
inv_reg_set = set(inv_conv['REG_imp'].unique())
matching_reg = exog_reg_set.intersection(inv_reg_set)
print(f"7. REG_imp matching analysis:")
print(f"   Exog_inv unique REG_imp: {len(exog_reg_set)}")
print(f"   Inv_conv unique REG_imp: {len(inv_reg_set)}")
print(f"   Matching REG_imp: {len(matching_reg)}")
if len(matching_reg) > 0:
    print(f"   Matches: {matching_reg}")
else:
    print(f"   NO MATCHES FOUND!")
print()

print("=" * 80)
print("TESTING MERGE WITH TYPE CORRECTION")
print("=" * 80)
print()

# Try merge WITHOUT type correction (what the code currently does)
print("8. Merge WITHOUT type correction:")
result_bad = exog_inv.merge(inv_conv, how='left', on=['PROD_COMM','REG_imp'])
print(f"   Result shape: {result_bad.shape}")
print(f"   Non-null input_coeff: {result_bad['input_coeff'].notna().sum()}")
print()

# Try merge WITH type correction (what it should do)
print("9. Merge WITH type correction (convert inv_conv.PROD_COMM to str):")
inv_conv_fixed = inv_conv.copy()
inv_conv_fixed['PROD_COMM'] = inv_conv_fixed['PROD_COMM'].astype(str)
result_good = exog_inv.merge(inv_conv_fixed, how='left', on=['PROD_COMM','REG_imp'])
print(f"   Result shape: {result_good.shape}")
print(f"   Non-null input_coeff: {result_good['input_coeff'].notna().sum()}")
if result_good['input_coeff'].notna().sum() > 0:
    print(f"   SUCCESS! Merge found matches.")
    print(f"   Total dk after multiplying: ${(result_good['dk'] * result_good['input_coeff']).sum():,.2f}")
else:
    print(f"   FAILED - Still no matches")
print()
