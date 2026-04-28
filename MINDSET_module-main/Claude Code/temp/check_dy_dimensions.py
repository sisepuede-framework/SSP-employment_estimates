"""
Check why dy_inv_exog ends up with wrong dimensions
"""
import sys
import os
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass

print("Loading MRIO and scenario...")
MRIO_BASE = exog_vars()
scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
Scenario.set_exog_inv()

if not hasattr(Scenario, 'inv_spending'):
    import pandas as pd
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

print()
print("=" * 80)
print("DIMENSION CHECK")
print("=" * 80)
print()

print(f"1. INV_model.dy_inv_exog (DataFrame):")
print(f"   Shape: {INV_model.dy_inv_exog.shape}")
print(f"   Columns: {list(INV_model.dy_inv_exog.columns)}")
print(f"   Sample rows:")
print(INV_model.dy_inv_exog.head(10))
print()

print(f"2. MRIO_BASE dimensions for MRIO_df_to_vec:")
print(f"   R list length: {len(MRIO_BASE.R['Region_acronyms'].to_list())}")
print(f"   P list length: {len(MRIO_BASE.P['Lfd_Nr'].to_list())}")
print(f"   Expected vector size: {len(MRIO_BASE.R['Region_acronyms'].to_list()) * len(MRIO_BASE.P['Lfd_Nr'].to_list())}")
print()

print(f"3. Converting to vector...")
dy_inv_exog = MRIO_df_to_vec(
    INV_model.dy_inv_exog,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

print(f"   dy_inv_exog shape: {dy_inv_exog.shape}")
print(f"   dy_inv_exog size: {len(dy_inv_exog)}")
print(f"   Non-zero elements: {(dy_inv_exog != 0).sum()}")
print(f"   Total value: ${dy_inv_exog.sum():,.0f}")
print()

print("=" * 80)
print("VERDICT")
print("=" * 80)
if len(dy_inv_exog) == 19680:
    print("OK - dy_inv_exog has correct dimensions (19680)")
    print("The test should work now!")
else:
    print(f"ERROR - dy_inv_exog has {len(dy_inv_exog)} elements, expected 19680")
    print("This will cause dimension mismatch with L_BASE")
