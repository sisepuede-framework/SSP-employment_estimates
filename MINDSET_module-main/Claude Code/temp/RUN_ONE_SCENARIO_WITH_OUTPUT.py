"""
RUN ONE SCENARIO AND SAVE OUTPUT

Runs Strategy_1004_MEX and saves results to CSV to show output format.
This demonstrates what the batch processing will produce for all 469 scenarios.

Based on: RUN_ONE_SCENARIO_SSP.py (which worked successfully)
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
print("RUN ONE SCENARIO: Strategy_1004_MEX (with output)")
print("="*80)
print()

scenario_name = "Strategy_1004_MEX"
scenario_file = f"GLORIA_template/Scenarios/{scenario_name}.xlsx"

if not os.path.exists(scenario_file):
    print(f"ERROR: Scenario file not found: {scenario_file}")
    sys.exit(1)

#==============================================================================
# STEP 1: Load MRIO Data
#==============================================================================
print("STEP 1: Loading MRIO Data (SSP aggregated)")
print("-"*80)

from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()

print(f"✓ MRIO data loaded")
print(f"  Countries: {len(MRIO_BASE.COU_ID)} ({', '.join(MRIO_BASE.COU_ID)})")
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
print()

#==============================================================================
# STEP 3: Investment Module (proper conversion)
#==============================================================================
print("STEP 3: Converting Investment to Final Demand")
print("-"*80)

from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec

# Set defaults needed by investment module
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

print(f"✓ Conversion complete: ${dy_inv_exog.sum():,.0f}")
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
print(f"  Total output change: ${dq_total.sum():,.0f}")
print(f"  Output multiplier: {output_multiplier:.3f}x")
print()

#==============================================================================
# STEP 5: Calculate Employment Impacts
#==============================================================================
print("STEP 5: Calculating Employment Impacts")
print("-"*80)

from SourceCode.employment import empl

Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

# Simplified employment baseline (employment-only approach)
q_base_df = MRIO_BASE.output.reset_index()
q_base = MRIO_df_to_vec(
    q_base_df,
    'REG_imp', 'PROD_COMM', 'output',
    MRIO_BASE.COU_ID,
    MRIO_BASE.SEC_ID
)
empl_base = q_base * 10  # Simplified: 10 workers per $M output

Empl_model.calc_empl_multiplier(empl_base, q_base)

# Calculate employment changes
dempl = Empl_model.calc_dempl(dq_total)

total_jobs = dempl.sum()
jobs_per_million = total_jobs / total_investment * 1e6 if total_investment != 0 else 0

print(f"✓ Employment calculated")
print(f"  Total employment impact: {total_jobs:,.0f} jobs")
print(f"  Jobs per $M investment: {jobs_per_million:.1f}")
print()

#==============================================================================
# STEP 6: Save Results
#==============================================================================
print("STEP 6: Saving Results")
print("-"*80)

# Create output directory
output_dir = "Claude Code/temp/output"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------------
# OUTPUT 1: Summary statistics (one row per scenario)
# -------------------------------------------------------------------
summary_results = pd.DataFrame([{
    'Scenario': scenario_name,
    'Country': 'MEX',
    'Strategy': 1004,
    'Total_Investment': total_investment,
    'Total_Output_Change': dq_total.sum(),
    'Output_Multiplier': output_multiplier,
    'Total_Jobs': total_jobs,
    'Jobs_per_Million_USD': jobs_per_million
}])

summary_file = f"{output_dir}/{scenario_name}_summary.csv"
summary_results.to_csv(summary_file, index=False)
print(f"✓ Summary saved: {summary_file}")
print(f"\nSummary data:")
print(summary_results.to_string(index=False))
print()

# -------------------------------------------------------------------
# OUTPUT 2: Country-level results
# -------------------------------------------------------------------
country_results = []
for i, country in enumerate(MRIO_BASE.COU_ID):
    start_idx = i * 120
    end_idx = start_idx + 120

    country_output = dq_total[start_idx:end_idx].sum()
    country_jobs = dempl[start_idx:end_idx].sum()

    country_results.append({
        'Scenario': scenario_name,
        'Country': country,
        'Output_Change': country_output,
        'Jobs': country_jobs
    })

country_df = pd.DataFrame(country_results)
country_file = f"{output_dir}/{scenario_name}_by_country.csv"
country_df.to_csv(country_file, index=False)
print(f"✓ Country-level results saved: {country_file}")
print(f"\nCountry-level data:")
print(country_df.to_string(index=False))
print()

# -------------------------------------------------------------------
# OUTPUT 3: Sector-level results (detailed)
# -------------------------------------------------------------------
sector_results = pd.concat([
    MRIO_BASE.mrio_list,
    pd.DataFrame({
        'Output_Change': dq_total,
        'Jobs': dempl
    })
], axis=1)

sector_results['Scenario'] = scenario_name
sector_results = sector_results[['Scenario', 'Reg_ID', 'Region', 'Sec_ID', 'Sector', 'Output_Change', 'Jobs']]

sector_file = f"{output_dir}/{scenario_name}_by_sector.csv"
sector_results.to_csv(sector_file, index=False)
print(f"✓ Sector-level results saved: {sector_file}")
print(f"  Total rows: {len(sector_results)} (8 countries × 120 sectors)")
print()

#==============================================================================
# SUMMARY
#==============================================================================
print("="*80)
print("OUTPUT FILES CREATED")
print("="*80)
print()
print("Three output files demonstrate what batch processing will produce:")
print()
print(f"1. SUMMARY (1 row per scenario):")
print(f"   {summary_file}")
print(f"   → Consolidate 469 scenarios: append rows")
print()
print(f"2. BY COUNTRY (8 rows per scenario):")
print(f"   {country_file}")
print(f"   → Consolidate 469 scenarios: append rows")
print()
print(f"3. BY SECTOR (960 rows per scenario):")
print(f"   {sector_file}")
print(f"   → Consolidate 469 scenarios: append rows")
print()
print("For batch processing:")
print("  - Run all 469 scenarios")
print("  - Each produces these 3 outputs")
print("  - Concatenate all summaries → final_summary.csv (469 rows)")
print("  - Concatenate all country data → final_by_country.csv (469×8 rows)")
print("  - Concatenate all sector data → final_by_sector.csv (469×960 rows)")
print()
print("="*80)
