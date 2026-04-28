"""
Compare using investment data DIRECTLY vs after INV_model conversion
to see what the transformation does
"""
import sys
import os
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("COMPARE: DIRECT vs CONVERTED INVESTMENT DATA")
print("="*80)
print()

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass

MRIO_BASE = exog_vars()
scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
Scenario.set_exog_inv()

print("Original investment data:")
print("-"*80)
print(f"Total: ${Scenario.inv_exog['dk'].sum():,.0f}")
print(f"Non-zero products: {(Scenario.inv_exog['dk'] > 0).sum()}")
print()

#==============================================================================
# APPROACH A: Use data DIRECTLY (as final demand)
#==============================================================================
print("APPROACH A: Use investment data DIRECTLY")
print("-"*80)

# Create demand vector directly from inv_exog
# This treats PROD_COMM as the product to purchase (TRAD_COMM in MRIO terms)
inv_direct = Scenario.inv_exog.copy()
inv_direct = inv_direct.rename(columns={'PROD_COMM': 'TRAD_COMM'})
inv_direct['REG_exp'] = inv_direct['REG_imp']  # Domestic purchases for simplicity
inv_direct = inv_direct.rename(columns={'dk': 'dy'})

dy_direct = MRIO_df_to_vec(
    inv_direct,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

print(f"Demand vector (direct):")
print(f"  Sum: ${dy_direct.sum():,.0f}")
print(f"  Non-zero elements: {(dy_direct != 0).sum()}")
print(f"  Shape: {dy_direct.shape}")
print()

#==============================================================================
# APPROACH B: Use INV_model conversion
#==============================================================================
print("APPROACH B: Use INV_model conversion (current approach)")
print("-"*80)

if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

dy_converted = MRIO_df_to_vec(
    INV_model.dy_inv_exog,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

print(f"Demand vector (converted):")
print(f"  Sum: ${dy_converted.sum():,.0f}")
print(f"  Non-zero elements: {(dy_converted != 0).sum()}")
print(f"  Shape: {dy_converted.shape}")
print()

#==============================================================================
# COMPARISON
#==============================================================================
print("="*80)
print("COMPARISON:")
print("="*80)
print()

print(f"Total demand:")
print(f"  Direct:    ${dy_direct.sum():,.0f}")
print(f"  Converted: ${dy_converted.sum():,.0f}")
print(f"  Difference: ${abs(dy_direct.sum() - dy_converted.sum()):,.0f}")
print()

print(f"Non-zero elements:")
print(f"  Direct:    {(dy_direct != 0).sum()}")
print(f"  Converted: {(dy_converted != 0).sum()}")
print()

print(f"Pattern difference:")
correlation = np.corrcoef(dy_direct, dy_converted)[0, 1]
print(f"  Correlation: {correlation:.4f}")
print()

# Show top 10 largest differences
diff = np.abs(dy_direct - dy_converted)
top_diff_idx = np.argsort(diff)[-10:][::-1]

print("Top 10 largest differences:")
print("-"*80)
for idx in top_diff_idx:
    country_idx = idx // 120
    sector_idx = idx % 120
    country = MRIO_BASE.COU_ID[country_idx]
    sector = sector_idx + 1

    print(f"  {country} Sector {sector:3d}: Direct=${dy_direct[idx]:10,.0f}, "
          f"Converted=${dy_converted[idx]:10,.0f}, "
          f"Diff=${diff[idx]:10,.0f}")

print()
print("="*80)
print("CONCLUSION:")
print("="*80)
print()
if np.allclose(dy_direct.sum(), dy_converted.sum(), rtol=0.01):
    print("✓ Totals are similar - conversion preserves total investment")
else:
    print("✗ Totals differ significantly - conversion changes total!")

if correlation > 0.9:
    print("✓ Patterns are similar - conversion redistributes similarly")
else:
    print("✗ Patterns differ - conversion redistributes differently")

print()
print("Based on your data structure (products already specified),")
print("you should probably use APPROACH A (direct) instead of APPROACH B (converted).")
