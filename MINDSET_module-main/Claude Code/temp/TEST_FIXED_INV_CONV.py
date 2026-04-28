"""
TEST: Fix INV_CONV to have 1.0 on diagonal, then run Strategy_1004_MEX

This tests whether changing INV_CONV from 0.19964 → 1.0 solves the problem
while keeping the "Investment by" sheet structure.
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
print("TEST: Fixed INV_CONV with Investment by Sheet")
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
# STEP 2: Fix INV_CONV (Change 0.19964 → 1.0 on diagonal)
#==============================================================================
print("STEP 2: Fixing INV_CONV Matrix")
print("-"*80)

# INV_CONV is currently 120×121 matrix with diagonal = 0.19964
INV_CONV_original = MRIO_BASE.INV_CONV.copy()
print(f"Original INV_CONV shape: {INV_CONV_original.shape}")
print(f"Original diagonal value: {INV_CONV_original.iloc[0, 1]}")  # First diagonal element

# Create fixed version: multiply diagonal by 5.009 (0.19964 × 5.009 ≈ 1.0)
INV_CONV_fixed = INV_CONV_original.copy()
for i in range(120):
    sector_col = str(i + 1)
    if sector_col in INV_CONV_fixed.columns:
        INV_CONV_fixed.iloc[i, INV_CONV_fixed.columns.get_loc(sector_col)] = 1.0

print(f"Fixed diagonal value: {INV_CONV_fixed.iloc[0, 1]}")
print(f"✓ INV_CONV diagonal changed to 1.0")
print()

# Replace in MRIO_BASE
MRIO_BASE.INV_CONV = INV_CONV_fixed

#==============================================================================
# STEP 3: Load Scenario
#==============================================================================
print("STEP 3: Loading Investment Scenario")
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
# STEP 4: Investment Module (with FIXED INV_CONV)
#==============================================================================
print("STEP 4: Converting Investment to Final Demand (FIXED)")
print("-"*80)

from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec

# Set defaults
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

conversion_ratio = dy_inv_exog.sum() / total_investment if total_investment != 0 else 0
print(f"✓ Conversion complete")
print(f"  Input investment:  ${total_investment:,.0f}")
print(f"  Output demand:     ${dy_inv_exog.sum():,.0f}")
print(f"  Preservation rate: {conversion_ratio:.1%}")
print(f"  Non-zero elements: {(dy_inv_exog != 0).sum()}")
print()

if conversion_ratio < 0.95:
    print("⚠ WARNING: Still losing >5% of investment value!")
    print("  Check if fcf_share or other factors are causing loss")
    print()

#==============================================================================
# STEP 5: Calculate Output Changes
#==============================================================================
print("STEP 5: Calculating Output Changes")
print("-"*80)

from SourceCode.InputOutput import IO

IO_model = IO(MRIO_BASE)
IO_model.load_L_base()

dq_total = IO_model.calc_dq_exog(dy_inv_exog)

output_multiplier = dq_total.sum() / dy_inv_exog.sum() if dy_inv_exog.sum() != 0 else 0

print(f"✓ Output changes calculated")
print(f"  Total output change: ${dq_total.sum():,.0f}")
print(f"  Output multiplier:   {output_multiplier:.3f}x")
print()

#==============================================================================
# STEP 6: Calculate Employment
#==============================================================================
print("STEP 6: Calculating Employment Impacts")
print("-"*80)

from SourceCode.employment import empl

Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

# Employment baseline
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
print(f"  Total jobs:         {total_jobs:,.0f}")
print(f"  Jobs per $M:        {jobs_per_million:.1f}")
print()

#==============================================================================
# STEP 7: Results by Country
#==============================================================================
print("STEP 7: Results by Country")
print("-"*80)

country_results = []
for i, country in enumerate(MRIO_BASE.COU_ID):
    start_idx = i * 120
    end_idx = start_idx + 120

    country_investment = Scenario.inv_exog[Scenario.inv_exog['REG_imp'] == country]['dk'].sum()
    country_demand = dy_inv_exog[start_idx:end_idx].sum()
    country_output = dq_total[start_idx:end_idx].sum()
    country_jobs = dempl[start_idx:end_idx].sum()

    country_results.append({
        'Country': country,
        'Investment_Input': country_investment,
        'Demand_Output': country_demand,
        'Output_Change': country_output,
        'Jobs': country_jobs
    })

    if abs(country_investment) > 1 or abs(country_demand) > 1:
        print(f"{country}:")
        print(f"  Investment input:  ${country_investment:>12,.0f}")
        print(f"  Demand output:     ${country_demand:>12,.0f}")
        print(f"  Output change:     ${country_output:>12,.0f}")
        print(f"  Jobs:              {country_jobs:>12,.0f}")

print()

#==============================================================================
# SUMMARY
#==============================================================================
print("="*80)
print("RESULTS SUMMARY")
print("="*80)
print()
print(f"Scenario: {scenario_name}")
print(f"Investment input:    ${total_investment:,.0f}")
print(f"Demand created:      ${dy_inv_exog.sum():,.0f} ({conversion_ratio:.1%} preserved)")
print(f"Output change:       ${dq_total.sum():,.0f} (multiplier: {output_multiplier:.2f}x)")
print(f"Employment:          {total_jobs:,.0f} jobs ({jobs_per_million:.1f} per $M)")
print()
print("="*80)
print("ASSESSMENT")
print("="*80)
print()

if conversion_ratio > 0.95:
    print("✓ GOOD: Investment value preserved (>95%)")
else:
    print("✗ PROBLEM: Still losing investment value")

if 1.2 <= output_multiplier <= 2.5:
    print("✓ GOOD: Output multiplier in reasonable range (1.2-2.5)")
else:
    print(f"? CHECK: Output multiplier {output_multiplier:.2f}x seems {'low' if output_multiplier < 1.2 else 'high'}")

if 5 <= jobs_per_million <= 50:
    print("✓ GOOD: Jobs per $M in reasonable range (5-50)")
else:
    print(f"? CHECK: Jobs per $M {jobs_per_million:.1f} seems {'low' if jobs_per_million < 5 else 'high'}")

print()
print("If all checks pass, we can apply this fix permanently to INV_CONV.")
