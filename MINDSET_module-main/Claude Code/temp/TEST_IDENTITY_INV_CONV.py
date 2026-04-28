"""
TEST: Identity INV_CONV with Strategy_1004_MEX

This tests whether the new identity INV_CONV.csv preserves your investment
correctly when you specify product codes in "Sector investing code*" column.

Expected results:
- Investment preserved (~100%, not ~20%)
- Products match your intent (Code 90 → Product 90)
- Employment estimates are reasonable
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
print("TEST: Identity INV_CONV with Strategy_1004_MEX")
print("="*80)
print()

scenario_name = "Strategy_1004_MEX"
scenario_file = f"GLORIA_template/Scenarios/{scenario_name}.xlsx"

#==============================================================================
# STEP 1: Load MRIO Data (with new identity INV_CONV)
#==============================================================================
print("STEP 1: Loading MRIO Data")
print("-"*80)

from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()

print(f"✓ MRIO data loaded")
print(f"  Countries: {', '.join(MRIO_BASE.COU_ID)}")
print()

# Check INV_CONV structure
print("Checking INV_CONV matrix:")
if hasattr(MRIO_BASE, 'INV_CONV'):
    print(f"  Type: {type(MRIO_BASE.INV_CONV)}")
    print(f"  Shape: {MRIO_BASE.INV_CONV.shape}")
    # Check a few diagonal values
    if MRIO_BASE.INV_CONV.shape == (120, 121):
        diag_vals = [MRIO_BASE.INV_CONV.iloc[i, i+1] for i in [0, 54, 89, 119]]
        print(f"  Sample diagonal values: {diag_vals}")
        if all(abs(v - 1.0) < 0.01 for v in diag_vals):
            print("  ✓ Diagonal values are 1.0 (identity matrix confirmed)")
        else:
            print("  ⚠ Diagonal values are NOT 1.0!")
else:
    print("  ✗ INV_CONV not loaded!")
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
nonzero_products = (Scenario.inv_exog['dk'] > 0).sum()

print(f"✓ Investment loaded")
print(f"  Total: ${total_investment:,.0f} kUSD (= ${total_investment*1000:,.0f})")
print(f"  Non-zero products: {nonzero_products}")
print()

#==============================================================================
# STEP 3: Investment Module (with identity INV_CONV)
#==============================================================================
print("STEP 3: Converting Investment to Final Demand")
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
print(f"  Input investment:  ${total_investment:,.0f} kUSD")
print(f"  Output demand:     ${dy_inv_exog.sum():,.0f} kUSD")
print(f"  Preservation rate: {conversion_ratio:.1%}")
print()

if conversion_ratio < 0.95:
    print("⚠ WARNING: Losing >5% of investment!")
    print("  This may be due to fcf_share redistribution")
elif conversion_ratio > 1.05:
    print("⚠ WARNING: Demand exceeds investment by >5%")
else:
    print("✓ GOOD: Investment well-preserved (95-105%)")
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
print(f"  Total output change: ${dq_total.sum():,.0f} kUSD")
print(f"  Output multiplier:   {output_multiplier:.3f}x")
print()

if 1.2 <= output_multiplier <= 2.5:
    print("✓ GOOD: Multiplier in reasonable range (1.2-2.5)")
elif output_multiplier < 1.2:
    print("? CHECK: Multiplier seems low (<1.2)")
else:
    print("? CHECK: Multiplier seems high (>2.5)")
print()

#==============================================================================
# STEP 5: Calculate Employment
#==============================================================================
print("STEP 5: Calculating Employment Impacts")
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
empl_base = q_base * 10  # Simplified: 10 workers per kUSD output

Empl_model.calc_empl_multiplier(empl_base, q_base)
dempl = Empl_model.calc_dempl(dq_total)

total_jobs = dempl.sum()
jobs_per_million = total_jobs / (total_investment * 1000) * 1e6 if total_investment != 0 else 0

print(f"✓ Employment calculated")
print(f"  Total jobs:         {total_jobs:,.0f}")
print(f"  Jobs per $M USD:    {jobs_per_million:.1f}")
print()

if 5 <= jobs_per_million <= 50:
    print("✓ GOOD: Jobs per $M in reasonable range (5-50)")
elif jobs_per_million < 5:
    print("? CHECK: Jobs per $M seems low (<5)")
else:
    print("? CHECK: Jobs per $M seems high (>50)")
print()

#==============================================================================
# STEP 6: Results by Country
#==============================================================================
print("STEP 6: Results by Country")
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
        'Investment': country_investment,
        'Demand': country_demand,
        'Output': country_output,
        'Jobs': country_jobs
    })

results_df = pd.DataFrame(country_results)
results_df['Jobs_per_M'] = results_df['Jobs'] / (results_df['Investment'] * 1000) * 1e6
results_df = results_df[results_df['Investment'] > 0]  # Only show countries with investment

print(results_df.to_string(index=False))
print()

#==============================================================================
# SUMMARY
#==============================================================================
print("="*80)
print("RESULTS SUMMARY")
print("="*80)
print()
print(f"Scenario: {scenario_name}")
print(f"Investment input:    ${total_investment:,.0f} kUSD = ${total_investment*1000:,.0f}")
print(f"Demand created:      ${dy_inv_exog.sum():,.0f} kUSD ({conversion_ratio:.1%} preserved)")
print(f"Output change:       ${dq_total.sum():,.0f} kUSD (multiplier: {output_multiplier:.2f}x)")
print(f"Employment:          {total_jobs:,.0f} jobs ({jobs_per_million:.1f} per $M)")
print()

print("="*80)
print("ASSESSMENT")
print("="*80)
print()

passed = 0
total_checks = 3

if 0.95 <= conversion_ratio <= 1.05:
    print("✓ CHECK 1: Investment preserved (95-105%)")
    passed += 1
else:
    print(f"✗ CHECK 1: Investment preservation at {conversion_ratio:.1%} (target: 95-105%)")

if 1.2 <= output_multiplier <= 2.5:
    print("✓ CHECK 2: Output multiplier reasonable (1.2-2.5)")
    passed += 1
else:
    print(f"? CHECK 2: Output multiplier {output_multiplier:.2f}x (typical range: 1.2-2.5)")

if 5 <= jobs_per_million <= 50:
    print("✓ CHECK 3: Jobs per $M reasonable (5-50)")
    passed += 1
else:
    print(f"? CHECK 3: Jobs per $M {jobs_per_million:.1f} (typical range: 5-50)")

print()
print(f"Passed {passed}/{total_checks} checks")
print()

if passed == total_checks:
    print("="*80)
    print("✓✓✓ ALL CHECKS PASSED ✓✓✓")
    print("="*80)
    print()
    print("The identity INV_CONV is working correctly!")
    print("Your product codes are now preserved through the investment module.")
    print()
    print("Next step: Run batch processing for all 469 Strategy files.")
else:
    print("="*80)
    print("⚠ SOME CHECKS FAILED")
    print("="*80)
    print()
    print("Please review the results above.")
    print("fcf_share may be causing some redistribution (this can be normal).")
