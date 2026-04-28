"""
RUN ONE SCENARIO - USING INVESTMENT DATA DIRECTLY

Your Strategy files already specify products to purchase (final demand vector).
No need for INV_model conversion - use data directly.

Based on: User confirmation that inv_exog is already a demand vector
"""

import sys
import os
import time
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("RUN ONE SCENARIO: Strategy_1004_MEX (DIRECT approach)")
print("="*80)
print()

scenario_name = "Strategy_1004_MEX"
scenario_file = f"GLORIA_template/Scenarios/{scenario_name}.xlsx"

#==============================================================================
# STEP 1: Load MRIO Data
#==============================================================================
print("STEP 1: Loading MRIO Data")
print("-"*80)

from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()

print(f"✓ MRIO data loaded")
print(f"  Countries: {', '.join(MRIO_BASE.COU_ID)}")
print()

#==============================================================================
# STEP 2: Load Scenario
#==============================================================================
print("STEP 2: Loading Investment Scenario")
print("-"*80)

from SourceCode.scenario import scenario

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass

Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
Scenario.set_exog_inv()

total_investment = Scenario.inv_exog['dk'].sum()
print(f"✓ Investment loaded: ${total_investment:,.0f}")
print(f"  Non-zero products: {(Scenario.inv_exog['dk'] > 0).sum()}")
print()

#==============================================================================
# STEP 3: Create Demand Vector DIRECTLY (no conversion)
#==============================================================================
print("STEP 3: Creating Final Demand Vector DIRECTLY")
print("-"*80)

from SourceCode.utils import MRIO_df_to_vec

# Your inv_exog already specifies products (PROD_COMM) and amounts (dk)
# Treat PROD_COMM as TRAD_COMM (product to purchase)
# Treat REG_imp as both importer and exporter (domestic purchase)

inv_demand = Scenario.inv_exog.copy()
inv_demand['REG_exp'] = inv_demand['REG_imp']  # Assuming domestic purchases
inv_demand = inv_demand.rename(columns={'PROD_COMM': 'TRAD_COMM', 'dk': 'dy'})

dy_inv_exog = MRIO_df_to_vec(
    inv_demand,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

print(f"✓ Demand vector created")
print(f"  Total demand: ${dy_inv_exog.sum():,.0f}")
print(f"  Non-zero elements: {(dy_inv_exog != 0).sum()}")
print()

#==============================================================================
# STEP 4: Calculate Output Changes
#==============================================================================
print("STEP 4: Calculating Output Changes")
print("-"*80)

from SourceCode.InputOutput import IO

IO_model = IO(MRIO_BASE)
IO_model.load_L_base()

dq_total = IO_model.calc_dq_exog(dy_inv_exog)

output_multiplier = dq_total.sum() / dy_inv_exog.sum() if dy_inv_exog.sum() != 0 else 0

print(f"✓ Output changes calculated")
print(f"  Total output: ${dq_total.sum():,.0f}")
print(f"  Multiplier: {output_multiplier:.3f}x")
print()

#==============================================================================
# STEP 5: Calculate Employment
#==============================================================================
print("STEP 5: Calculating Employment")
print("-"*80)

from SourceCode.employment import empl

Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

# Employment baseline (simplified)
q_base_df = MRIO_BASE.output.reset_index()
q_base = MRIO_df_to_vec(
    q_base_df,
    'REG_imp', 'PROD_COMM', 'output',
    MRIO_BASE.COU_ID,
    MRIO_BASE.SEC_ID
)
empl_base = q_base * 10

Empl_model.calc_empl_multiplier(empl_base, q_base)
dempl = Empl_model.calc_dempl(dq_total)

total_jobs = dempl.sum()
jobs_per_million = total_jobs / total_investment * 1e6 if total_investment != 0 else 0

print(f"✓ Employment calculated")
print(f"  Total jobs: {total_jobs:,.0f}")
print(f"  Jobs per $M: {jobs_per_million:.1f}")
print()

#==============================================================================
# STEP 6: Results by Country
#==============================================================================
print("STEP 6: Results by Country")
print("-"*80)

for i, country in enumerate(MRIO_BASE.COU_ID):
    start_idx = i * 120
    end_idx = start_idx + 120

    country_output = dq_total[start_idx:end_idx].sum()
    country_jobs = dempl[start_idx:end_idx].sum()

    if abs(country_output) > 1 or abs(country_jobs) > 1:
        print(f"{country}: Output=${country_output:,.0f}, Jobs={country_jobs:,.0f}")

print()

#==============================================================================
# SUMMARY
#==============================================================================
print("="*80)
print("RESULTS SUMMARY")
print("="*80)
print(f"\nScenario: {scenario_name}")
print(f"Investment: ${total_investment:,.0f}")
print(f"Output change: ${dq_total.sum():,.0f} (multiplier: {output_multiplier:.2f}x)")
print(f"Employment: {total_jobs:,.0f} jobs ({jobs_per_million:.1f} per $M)")
print()
print("="*80)
print()
print("Does this look more reasonable?")
print("If yes, we'll use this DIRECT approach for batch processing.")
