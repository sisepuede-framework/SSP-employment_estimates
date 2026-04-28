"""
Trace through EGY employment multiplier calculation step by step
"""
import sys
import os
import numpy as np
import pandas as pd
sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.investment import invest
from SourceCode.InputOutput import IO
from SourceCode.employment import empl
from SourceCode.utils import MRIO_df_to_vec

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass

print("="*80)
print("TRACE: EGY EMPLOYMENT MULTIPLIER CALCULATION")
print("="*80)
print()

# Load data
MRIO_BASE = exog_vars()
IO_model = IO(MRIO_BASE)
IO_model.initialize()

# Load scenario
scenario_file = "GLORIA_template/Scenarios/Strategy_1004_EGY.xlsx"
Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
Scenario.set_exog_inv()

if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

dy_inv_exog = MRIO_df_to_vec(
    INV_model.dy_inv_exog,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

dq_total = IO_model.calc_dq_exog(dy_inv_exog)

# Calculate employment baseline
empl_base_df = MRIO_BASE.LABOR_BASE.copy()
empl_base_df["vol_low"] = empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"]
empl_base_df["vol_high"] = empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"]
empl_base_df["vol_total"] = empl_base_df["vol_low"] + empl_base_df["vol_high"]

empl_base = MRIO_df_to_vec(
    empl_base_df[["REG_imp", "PROD_COMM", "vol_total"]],
    "REG_imp", "PROD_COMM", "vol_total",
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

# Build employment model
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)

# Calculate employment
dempl = Empl_model.calc_dempl(dq_total)

# Focus on EGY
country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}
egy_idx = country_idx['EGY']
egy_start = egy_idx * 120
egy_end = egy_start + 120

egy_output = dq_total[egy_start:egy_end].sum()
egy_jobs = dempl[egy_start:egy_end].sum()

print(f"EGY Results:")
print(f"  Output change: ${egy_output:,.0f} kUSD")
print(f"  Jobs created: {egy_jobs:,.2f}")
print(f"  Jobs per $M output: {egy_jobs/(egy_output/1000):,.2f}")
print()

print("="*80)
print("DETAILED BREAKDOWN FOR INVESTED PRODUCTS")
print("="*80)
print()

# Products being invested in
invested_products = [65, 66, 67, 68, 69, 70, 86, 89, 90, 91]

print(f"{'Prod':<6} {'dq':<12} {'empl_coef':<12} {'intensity':<12} {'multiplier':<12} {'jobs':<12} {'jobs/$M':<12}")
print("-"*80)

for prod in invested_products:
    prod_idx = egy_start + (prod - 1)

    prod_dq = dq_total[prod_idx]
    prod_empl_coef = Empl_model.EMPL_COEF[
        (Empl_model.EMPL_COEF['REG_imp'] == 'EGY') &
        (Empl_model.EMPL_COEF['PROD_COMM'] == prod)
    ]['empl_coef'].values[0]

    prod_empl_base = empl_base[prod_idx]
    prod_q_base = IO_model.q_base[prod_idx]
    prod_intensity = prod_empl_base / prod_q_base if prod_q_base > 0 else 0

    prod_multiplier = Empl_model.empl_multiplier[prod_idx]
    prod_jobs = dempl[prod_idx]
    prod_jobs_per_m = (prod_jobs / (prod_dq/1000)) if prod_dq > 0 else 0

    print(f"{prod:<6} {prod_dq:>11.0f} {prod_empl_coef:>11.3f} {prod_intensity:>11.6f} {prod_multiplier:>11.6f} {prod_jobs:>11.2f} {prod_jobs_per_m:>11.1f}")

print()
print("="*80)
print("ANALYSIS")
print("="*80)
print()
print("Formula: empl_multiplier = empl_coef × (empl_base / q_base)")
print("Formula: jobs = empl_multiplier × dq")
print()
print("Check if: empl_multiplier ≈ empl_coef × intensity")
print()

# Sample calculation for Product 90
prod = 90
prod_idx = egy_start + 89
prod_empl_coef = Empl_model.EMPL_COEF[
    (Empl_model.EMPL_COEF['REG_imp'] == 'EGY') &
    (Empl_model.EMPL_COEF['PROD_COMM'] == prod)
]['empl_coef'].values[0]
prod_intensity = empl_base[prod_idx] / IO_model.q_base[prod_idx]
prod_multiplier = Empl_model.empl_multiplier[prod_idx]
expected_mult = prod_empl_coef * prod_intensity

print(f"Product {prod}:")
print(f"  empl_coef:           {prod_empl_coef:.6f}")
print(f"  intensity:           {prod_intensity:.6f}")
print(f"  Expected multiplier: {expected_mult:.6f}")
print(f"  Actual multiplier:   {prod_multiplier:.6f}")
print(f"  Match: {abs(expected_mult - prod_multiplier) < 0.000001}")
