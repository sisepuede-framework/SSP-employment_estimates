"""
Check what calc_dy_inv_exog actually produces
"""
import sys
import os
import pandas as pd
sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass

MRIO_BASE = exog_vars()
Scenario = scenario(MRIO_BASE, "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx", MockLog())
Scenario.set_exog_inv()

if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()

print("Initial investment:")
print(f"  Total: ${Scenario.inv_exog['dk'].sum():,.2f} kUSD")
print()

# Run the actual method
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

print("After calc_dy_inv_exog (before vectorization):")
print(f"  Shape: {INV_model.dy_inv_exog.shape}")
print(f"  Columns: {list(INV_model.dy_inv_exog.columns)}")
print(f"  Total dy: ${INV_model.dy_inv_exog['dy'].sum():,.2f} kUSD")
print()

# Show sample
print("First 20 rows:")
print(INV_model.dy_inv_exog.head(20))
print()

# Check by country
print("Total by country:")
for country in MRIO_BASE.COU_ID:
    country_total = INV_model.dy_inv_exog[INV_model.dy_inv_exog['REG_imp'] == country]['dy'].sum()
    if abs(country_total) > 0.01:
        print(f"  {country}: ${country_total:,.2f} kUSD")
