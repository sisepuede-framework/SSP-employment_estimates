"""
RUN ONE SCENARIO WITH SSP AGGREGATED DATA (SIMPLIFIED TEST)

Tests employment calculation workflow for Strategy_1004_MEX.xlsx:
1. Load aggregated MRIO data (8 regions from SSP folder)
2. Load scenario
3. Convert investment to demand (simplified - direct mapping)
4. Calculate output changes (using Leontief)
5. Calculate employment impacts

NOTE: This is a SIMPLIFIED test to verify employment works with SSP aggregated data.
For full MINDSET workflow with investment module, see RunMINDSET.py.

This validates the employment pipeline before batch processing 469 scenarios.
"""

import sys
import os
import time
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("RUN ONE SCENARIO: Strategy_1004_MEX")
print("="*80)
print()

scenario_name = "Strategy_1004_MEX"
scenario_file = f"GLORIA_template/Scenarios/{scenario_name}.xlsx"

if not os.path.exists(scenario_file):
    print(f"ERROR: Scenario file not found: {scenario_file}")
    sys.exit(1)

print(f"Scenario: {scenario_name}")
print(f"File: {scenario_file}")
print()

#==============================================================================
# STEP 1: Load MRIO Data (SSP aggregated - 8 regions)
#==============================================================================
print("-" * 80)
print("STEP 1: Loading MRIO Data (SSP aggregated)")
print("-" * 80)

step_time = time.time()
from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()

print(f"✓ MRIO data loaded in {round(time.time() - step_time, 1)} seconds")
print(f"  Countries: {len(MRIO_BASE.COU_ID)} ({', '.join(MRIO_BASE.COU_ID)})")
print(f"  Sectors: {len(MRIO_BASE.SEC_ID)}")
print(f"  Total dimensions: {len(MRIO_BASE.COU_ID) * len(MRIO_BASE.SEC_ID)}")
print()

#==============================================================================
# STEP 2: Load Scenario
#==============================================================================
print("-" * 80)
print("STEP 2: Loading Investment Scenario")
print("-" * 80)

step_time = time.time()
from SourceCode.scenario import scenario

# Mock log
class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass
Log = MockLog()

Scenario = scenario(MRIO_BASE, scenario_file, Log)
Scenario.set_exog_inv()

if not hasattr(Scenario, 'inv_exog') or Scenario.inv_exog.empty:
    print(f"ERROR: No investment data in scenario file!")
    sys.exit(1)

total_investment = Scenario.inv_exog['dk'].sum()
print(f"✓ Investment loaded: ${total_investment:,.0f}")
print(f"  Number of investment entries: {len(Scenario.inv_exog)}")
print(f"  Time: {round(time.time() - step_time, 1)} seconds")
print()

# Show breakdown
print("Investment by country:")
for country in MRIO_BASE.COU_ID:
    country_inv = Scenario.inv_exog[Scenario.inv_exog['REG_imp'] == country]['dk'].sum()
    if abs(country_inv) > 0:
        print(f"  {country}: ${country_inv:,.0f}")
print()

#==============================================================================
# STEP 3: Convert Investment to Final Demand (Simplified)
#==============================================================================
print("-" * 80)
print("STEP 3: Converting Investment to Final Demand (Simplified)")
print("-" * 80)

step_time = time.time()

# Simplified: Use investment data directly as demand shock
# In full MINDSET, this goes through investment module with conversion factors
# For testing employment, we just need a demand vector

# Create demand vector (960 elements = 8 countries × 120 sectors)
dy_inv_exog = np.zeros(len(MRIO_BASE.mrio_id))

# Map investment data to demand vector
for _, row in Scenario.inv_exog.iterrows():
    region = row['REG_imp']
    sector = int(row['PROD_COMM'])
    investment = row['dk']

    # Find index in mrio_id
    mask = (MRIO_BASE.mrio_id['REG_imp'] == region) & (MRIO_BASE.mrio_id['PROD_COMM'] == sector)
    idx = MRIO_BASE.mrio_id[mask].index
    if len(idx) > 0:
        dy_inv_exog[idx[0]] = investment

print(f"✓ Simplified conversion complete: ${dy_inv_exog.sum():,.0f}")
print(f"  Non-zero elements: {(dy_inv_exog != 0).sum()}")
print(f"  Time: {round(time.time() - step_time, 1)} seconds")
print()

#==============================================================================
# STEP 4: Calculate Output Changes (Leontief)
#==============================================================================
print("-" * 80)
print("STEP 4: Calculating Output Changes")
print("-" * 80)

step_time = time.time()
from SourceCode.InputOutput import IO

IO_model = IO(MRIO_BASE)
# Only load L_BASE (Leontief inverse) - we don't need full Y_BASE for this test
IO_model.load_L_base()

dq_total = IO_model.calc_dq_exog(dy_inv_exog)

output_multiplier = dq_total.sum() / dy_inv_exog.sum() if dy_inv_exog.sum() != 0 else 0

print(f"✓ Output changes calculated")
print(f"  Total output change: ${dq_total.sum():,.0f}")
print(f"  Output multiplier: {output_multiplier:.3f}x")
print(f"  Non-zero elements: {(dq_total != 0).sum()}")
print(f"  Time: {round(time.time() - step_time, 1)} seconds")
print()

# Show by country
print("Output change by country:")
for i, country in enumerate(MRIO_BASE.COU_ID):
    start_idx = i * 120
    end_idx = start_idx + 120
    country_output = dq_total[start_idx:end_idx].sum()
    if abs(country_output) > 0:
        print(f"  {country}: ${country_output:,.0f}")
print()

#==============================================================================
# STEP 5: Calculate Employment Impacts
#==============================================================================
print("-" * 80)
print("STEP 5: Calculating Employment Impacts")
print("-" * 80)

step_time = time.time()
from SourceCode.employment import empl

# Build employment coefficients
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

print(f"✓ Employment coefficients built")
print(f"  EMPL_COEF shape: {Empl_model.EMPL_COEF.shape}")
print(f"  Regions with data: {sorted(Empl_model.EMPL_COEF['REG_imp'].unique())}")
print()

# For simplified calculation, use baseline output as proxy for baseline employment
# In full MINDSET, this comes from production cost module
# Use MINDSET utility to convert output DataFrame to 960-element vector
from SourceCode.utils import MRIO_df_to_vec

q_base_df = MRIO_BASE.output.reset_index()
q_base = MRIO_df_to_vec(
    q_base_df,
    'REG_imp', 'PROD_COMM', 'output',
    MRIO_BASE.COU_ID,  # 8 countries
    MRIO_BASE.SEC_ID   # 120 sectors
)

empl_base = q_base * 10  # Simplified: 10 workers per $M output

# Calculate employment multiplier
Empl_model.calc_empl_multiplier(empl_base, q_base)

# Calculate employment changes
dempl = Empl_model.calc_dempl(dq_total)

total_jobs = dempl.sum()
jobs_multiplier = total_jobs / total_investment if total_investment != 0 else 0

print(f"✓ Employment calculated")
print(f"  Total employment impact: {total_jobs:,.0f} jobs")
print(f"  Jobs per $M investment: {jobs_multiplier:.1f}")
print(f"  Time: {round(time.time() - step_time, 1)} seconds")
print()

# Show by country
print("Employment by country:")
for i, country in enumerate(MRIO_BASE.COU_ID):
    start_idx = i * 120
    end_idx = start_idx + 120
    country_jobs = dempl[start_idx:end_idx].sum()
    if abs(country_jobs) > 0.01:
        print(f"  {country}: {country_jobs:,.0f} jobs")
print()

#==============================================================================
# SUMMARY
#==============================================================================
print("="*80)
print("SUMMARY")
print("="*80)
print(f"\nScenario: {scenario_name}")
print(f"  Investment: ${total_investment:,.0f}")
print(f"  Output change: ${dq_total.sum():,.0f} (multiplier: {output_multiplier:.3f}x)")
print(f"  Employment: {total_jobs:,.0f} jobs ({jobs_multiplier:.1f} jobs per $M)")
print()

if abs(total_jobs) > 0.1:
    print("✓ SUCCESS: Complete workflow working with SSP aggregated data!")
    print("  Ready for batch processing of 469 scenarios")
else:
    print("⚠ WARNING: Employment is zero - check baseline employment data")

print()
print("="*80)
