"""
Trace where the 2.1% investment loss occurs
"""
import sys
import os
import pandas as pd

sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.investment import invest

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass

print("="*80)
print("TRACING INVESTMENT LOSS")
print("="*80)
print()

MRIO_BASE = exog_vars()
scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
Scenario.set_exog_inv()

print("STEP 1: Initial Investment (inv_exog)")
print("-"*80)
total_start = Scenario.inv_exog['dk'].sum()
print(f"Total investment: ${total_start:,.2f} kUSD")
print(f"Non-zero products: {(Scenario.inv_exog['dk'] > 0).sum()}")
print()

# Check INV_CONV application
print("STEP 2: After INV_CONV Conversion")
print("-"*80)

if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()

# Before calc_dy_inv_exog, check what happens
exog_inv = Scenario.inv_exog.copy()
exog_inv = exog_inv.loc[:,["REG_imp","PROD_COMM","dk"]]
exog_inv["PROD_COMM"] = exog_inv['PROD_COMM'].astype(float).astype(int).astype(str)

print(f"Before conversion: ${exog_inv['dk'].sum():,.2f} kUSD")
print()

# Merge with INV_CONV
inv_conv = INV_CONV
exog_inv_after_conv = exog_inv.merge(inv_conv, how='left', on=['PROD_COMM','REG_imp'])
exog_inv_after_conv['dk_after'] = exog_inv_after_conv['dk'] * exog_inv_after_conv['input_coeff']

print(f"After INV_CONV: ${exog_inv_after_conv['dk_after'].sum():,.2f} kUSD")
print(f"Loss at INV_CONV: ${exog_inv['dk'].sum() - exog_inv_after_conv['dk_after'].sum():,.2f} kUSD")
print()

# Check for missing mappings
missing = exog_inv_after_conv[exog_inv_after_conv['input_coeff'].isna()]
if len(missing) > 0:
    print(f"⚠ Products missing from INV_CONV: {len(missing)}")
    print(missing[['REG_imp', 'PROD_COMM', 'dk']].head(10))
    print()

print("STEP 3: After fcf_share Distribution")
print("-"*80)

# Now apply fcf_share
exog_inv_after_conv = exog_inv_after_conv.drop(columns=['input_coeff', 'dk'])
exog_inv_after_conv = exog_inv_after_conv.rename(columns={'dk_after': 'dk'})

fcf_share = INV_model.fcf_share.astype({'TRAD_COMM':'str'})[['REG_exp','TRAD_COMM','REG_imp','FCF_share']]
exog_inv_after_conv = exog_inv_after_conv.astype({'TRAD_COMM':'str'})

print(f"Before fcf_share merge: ${exog_inv_after_conv['dk'].sum():,.2f} kUSD")
print(f"Unique products: {exog_inv_after_conv['TRAD_COMM'].nunique()}")
print()

# Check what happens with merge
exog_inv_final = exog_inv_after_conv.merge(fcf_share, how='inner', on=['TRAD_COMM','REG_imp'])

print(f"After fcf_share merge: ${exog_inv_final['dk'].sum():,.2f} kUSD")
print(f"Products after merge: {exog_inv_final['TRAD_COMM'].nunique()}")
print(f"Loss at fcf_share: ${exog_inv_after_conv['dk'].sum() - exog_inv_final['dk'].sum():,.2f} kUSD")
print()

# Check which products were dropped
products_before = set(exog_inv_after_conv['TRAD_COMM'].unique())
products_after = set(exog_inv_final['TRAD_COMM'].unique())
dropped_products = products_before - products_after

if dropped_products:
    print(f"⚠ Products dropped by fcf_share merge: {len(dropped_products)}")
    print(f"Dropped products: {sorted([int(p) for p in dropped_products])}")
    print()

    # Show investment amounts for dropped products
    dropped_inv = exog_inv_after_conv[exog_inv_after_conv['TRAD_COMM'].isin(dropped_products)]
    dropped_total = dropped_inv['dk'].sum()
    print(f"Total investment in dropped products: ${dropped_total:,.2f} kUSD")
    print()
    print("Dropped products detail:")
    print(dropped_inv[['REG_imp', 'TRAD_COMM', 'dk']].to_string(index=False))
    print()

print("="*80)
print("CONCLUSION")
print("="*80)
print()
print(f"Initial investment: ${total_start:,.2f} kUSD")
print(f"Final demand: ${exog_inv_final['dk'].sum():,.2f} kUSD")
print(f"Total loss: ${total_start - exog_inv_final['dk'].sum():,.2f} kUSD ({(total_start - exog_inv_final['dk'].sum())/total_start*100:.1f}%)")
print()
print("The loss occurs because fcf_share (capital formation trade data) is")
print("missing entries for some products in MEX.")
