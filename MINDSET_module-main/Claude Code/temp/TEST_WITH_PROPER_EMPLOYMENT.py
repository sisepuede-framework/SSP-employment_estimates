"""
TEST: Identity INV_CONV with PROPER Employment Baseline

This uses MINDSET's actual employment data (LABOR_BASE) to calculate
employment impacts correctly, following the exact methodology in RunMINDSET.py
and prod_cost.py.

NO GUESSING. Uses MINDSET's original design.
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
print("TEST: Identity INV_CONV with PROPER Employment Baseline")
print("="*80)
print()

scenario_name = "Strategy_1004_EGY"
scenario_file = f"GLORIA_template/Scenarios/{scenario_name}.xlsx"

#==============================================================================
# STEP 1: Load MRIO Data
#==============================================================================
print("STEP 1: Loading MRIO Data")
print("-"*80)

from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()

print(f"[OK] MRIO data loaded")
print(f"  Countries: {', '.join(MRIO_BASE.COU_ID)}")

# Verify LABOR_BASE exists
if hasattr(MRIO_BASE, 'LABOR_BASE'):
    print(f"[OK] LABOR_BASE loaded: {MRIO_BASE.LABOR_BASE.shape}")
else:
    print("[ERROR] LABOR_BASE not found!")
    print("  Please add LABOR_BASE to Variable_list_MINDSET_SSP.xlsx:")
    print("  Variable name: LABOR_BASE")
    print("  Path: GLORIA_db\\v57\\2019\\SSP\\labor_data.pkl")
    print("  Type: DataFrame")
    sys.exit(1)
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
print(f"[OK] Investment loaded: ${total_investment:,.0f} kUSD")
print()

#==============================================================================
# STEP 3: Investment Module
#==============================================================================
print("STEP 3: Converting Investment to Final Demand")
print("-"*80)

from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec

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

print(f"[OK] Demand created: ${dy_inv_exog.sum():,.0f} kUSD")
print(f"  Preservation: {dy_inv_exog.sum()/total_investment:.1%}")
print()

#==============================================================================
# STEP 4: Calculate Output Changes
#==============================================================================
print("STEP 4: Calculating Output Changes")
print("-"*80)

from SourceCode.InputOutput_SSP import IO

IO_model = IO(MRIO_BASE)
IO_model.initialize()  # This loads L_BASE, calculates y0, and q_base

dq_total = IO_model.calc_dq_exog(dy_inv_exog)
output_multiplier = dq_total.sum() / dy_inv_exog.sum() if dy_inv_exog.sum() != 0 else 0

print(f"[OK] Output change: ${dq_total.sum():,.0f} kUSD")
print(f"  Multiplier: {output_multiplier:.3f}x")
print()

#==============================================================================
# STEP 5: Calculate Employment Baseline (from LABOR_BASE)
#==============================================================================
print("STEP 5: Calculating Employment Baseline (from LABOR_BASE)")
print("-"*80)

# Calculate vol_total directly from LABOR_BASE (following prod_cost.py lines 59-61)
empl_base_df = MRIO_BASE.LABOR_BASE.copy()
empl_base_df["vol_low"] = empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"]
empl_base_df["vol_high"] = empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"]
empl_base_df["vol_total"] = empl_base_df["vol_low"] + empl_base_df["vol_high"]

# Keep only needed columns
empl_base_df = empl_base_df[["REG_imp", "PROD_COMM", "vol_total"]]

print(f"[OK] Employment baseline calculated from LABOR_BASE")
print(f"  Shape: {empl_base_df.shape}")
print(f"  Columns: {list(empl_base_df.columns)}")

# Convert to vector (following RunMINDSET.py line 501)
empl_base = MRIO_df_to_vec(
    empl_base_df,
    "REG_imp", "PROD_COMM", "vol_total",
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

total_baseline_employment = empl_base.sum()
print(f"  Total baseline employment: {total_baseline_employment:,.0f} workers")
print()

#==============================================================================
# STEP 6: Calculate Employment Impacts
#==============================================================================
print("STEP 6: Calculating Employment Impacts")
print("-"*80)

from SourceCode.employment import empl

Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

# Calculate employment multiplier (following RunMINDSET.py line 501)
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)

# Calculate employment changes
dempl = Empl_model.calc_dempl(dq_total)

total_jobs = dempl.sum()
jobs_per_million = total_jobs / (total_investment * 1000) * 1e6 if total_investment != 0 else 0

print(f"[OK] Employment calculated using MINDSET methodology")
print(f"  Total jobs created: {total_jobs:,.0f}")
print(f"  Jobs per $M USD: {jobs_per_million:.1f}")
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

    if abs(country_demand) > 0.1:  # Show countries with demand
        country_results.append({
            'Country': country,
            'Investment': country_investment,
            'Demand': country_demand,
            'Output': country_output,
            'Jobs': country_jobs
        })

results_df = pd.DataFrame(country_results)
if len(results_df) > 0:
    results_df['Jobs_per_M'] = results_df['Jobs'] / (results_df['Demand'] * 1000) * 1e6
    results_df = results_df.round(2)
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
print(f"Investment: ${total_investment:,.0f} kUSD = ${total_investment*1000:,.0f}")
print(f"Demand: ${dy_inv_exog.sum():,.0f} kUSD")
print(f"Output: ${dq_total.sum():,.0f} kUSD (multiplier: {output_multiplier:.2f}x)")
print(f"Employment: {total_jobs:,.0f} jobs ({jobs_per_million:.1f} per $M)")
print()
print("[OK] This uses MINDSET's actual LABOR_BASE data")
print("[OK] Following prod_cost.py and RunMINDSET.py methodology")
print("[OK] No guessing or invented assumptions")
print()
print("="*80)
