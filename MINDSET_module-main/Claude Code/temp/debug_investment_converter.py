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
print("DEBUG: Investment Converter")
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

print(f"Investment data loaded:")
print(f"  Total investment: ${Scenario.inv_exog['dk'].sum():,.2f}")
print(f"  Number of rows: {len(Scenario.inv_exog)}")
print(f"  Non-zero entries: {(Scenario.inv_exog['dk'] != 0).sum()}")
print()

# Set default inv_spending
if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

# Initialize investment module
print("Initializing investment module...")
INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
print(f"INV_CONV shape: {INV_CONV.shape}")
print(f"INV_CONV columns: {list(INV_CONV.columns)}")
print()

INV_model = invest(MRIO_BASE, INV_CONV, Scenario)

# Build elasticities
print("Building investment output elasticities...")
INV_model.build_inv_output_elas()
print(f"OK - INV_OUTPUT_ELAS shape: {INV_model.INV_OUTPUT_ELAS.shape}")
print()

# Calculate investment share
print("Calculating investment share...")
INV_model.calc_inv_share()
print("OK")
print()

# Convert investment to final demand
print("Converting investment to final demand...")
print(f"Input: Scenario.inv_exog")
print(f"  Shape: {Scenario.inv_exog.shape}")
print(f"  Total dk: ${Scenario.inv_exog['dk'].sum():,.2f}")
print()

INV_model.calc_dy_inv_exog(Scenario.inv_exog)

print("Output: INV_model.dy_inv_exog")
if hasattr(INV_model, 'dy_inv_exog'):
    print(f"  Shape: {INV_model.dy_inv_exog.shape}")
    print(f"  Total dy: ${INV_model.dy_inv_exog['dy'].sum():,.2f}")
    print()

    if INV_model.dy_inv_exog['dy'].sum() == 0:
        print("ERROR: Final demand is ZERO!")
        print()
        print("Checking for non-zero dy values:")
        non_zero = INV_model.dy_inv_exog[INV_model.dy_inv_exog['dy'] != 0]
        print(f"  Non-zero rows: {len(non_zero)}")

        if len(non_zero) > 0:
            print("\nFirst 10 non-zero entries:")
            print(non_zero.head(10))
        else:
            print("\nNo non-zero values found!")
            print("\nSample of dy_inv_exog:")
            print(INV_model.dy_inv_exog.head(20))
    else:
        print("SUCCESS: Final demand is non-zero!")
        print("\nTop 10 products by demand:")
        top = INV_model.dy_inv_exog.nlargest(10, 'dy')
        for idx, row in top.iterrows():
            print(f"  {row['REG_imp']} - Product {row['TRAD_COMM']}: ${row['dy']:,.2f}")
else:
    print("ERROR: dy_inv_exog attribute not created!")
