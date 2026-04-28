# -*- coding: utf-8 -*-
"""
TEST ONE SCENARIO - Before running full batch

This script tests ONE strategy-country combination to verify everything works.
After successful test, run the full batch processing.

Test scenario: Strategy_1004_MEX
"""

import numpy as np
import pandas as pd
import time
import sys
import os

#------------------------------------------------------------------------------
# PATH SETUP
#------------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

if mindset_root not in sys.path:
    sys.path.insert(0, mindset_root)

os.chdir(mindset_root)

print(f"MINDSET root directory: {mindset_root}")
print(f"Current working directory: {os.getcwd()}\n")

#------------------------------------------------------------------------------
# MINDSET Modules
#------------------------------------------------------------------------------
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.InputOutput import IO
from SourceCode.employment import empl
from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

print("="*80)
print("TEST: SINGLE SCENARIO EMPLOYMENT ESTIMATION")
print("="*80)
print()

#==============================================================================
# TEST CONFIGURATION
#==============================================================================

# CHANGE THIS TO TEST DIFFERENT SCENARIOS
TEST_STRATEGY = 1004
TEST_COUNTRY = "MEX"

scenario_name = f"Strategy_{TEST_STRATEGY}_{TEST_COUNTRY}"
SCENARIOS_FOLDER = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios")
scenario_file = os.path.join(SCENARIOS_FOLDER, f"{scenario_name}.xlsx")

print(f"Test scenario: {scenario_name}")
print(f"Scenario file: {scenario_file}")
print(f"File exists: {os.path.exists(scenario_file)}")
print()

if not os.path.exists(scenario_file):
    print(f"ERROR: Scenario file not found!")
    sys.exit(1)

#==============================================================================
# STEP 1: Load MRIO Data
#==============================================================================
print("-" * 80)
print("STEP 1: Loading MRIO Data")
print("-" * 80)

step_time = time.time()
MRIO_BASE = exog_vars()
print(f"OK - MRIO data loaded in {round(time.time() - step_time, 1)} seconds")
print(f"OK - Countries: {len(MRIO_BASE.COU_ID)}, Sectors: {len(MRIO_BASE.SEC_ID)}")
print()

# Initialize logging (optional - skip if module not available)
try:
    from SourceCode.log import log as _log
    Scenario_Log = _log("Test_SingleScenario")
except:
    # Create a simple mock logger
    class MockLog:
        def log_to_csv(self, *args, **kwargs):
            pass
        def log(self, *args, **kwargs):
            pass
    Scenario_Log = MockLog()
    print("Note: Using mock logger (this is OK)")

#==============================================================================
# STEP 2: Load Scenario
#==============================================================================
print("-" * 80)
print("STEP 2: Loading Investment Scenario")
print("-" * 80)

step_time = time.time()
Scenario = scenario(MRIO_BASE, scenario_file, Scenario_Log)
Scenario.set_exog_inv()

if not hasattr(Scenario, 'inv_exog') or Scenario.inv_exog.empty:
    print(f"ERROR: No investment data in scenario file!")
    sys.exit(1)

total_investment = Scenario.inv_exog['dk'].sum()
print(f"OK - Investment loaded: ${total_investment:,.0f}")
print(f"OK - Investment entries: {len(Scenario.inv_exog)}")
print()

# Show investment breakdown
print("Investment breakdown:")
for idx, row in Scenario.inv_exog.iterrows():
    print(f"  {row['REG_imp']} - Sector {row['PROD_COMM']}: ${row['dk']:,.0f}")
print()

#==============================================================================
# STEP 3: Investment Converter
#==============================================================================
print("-" * 80)
print("STEP 3: Converting Investment to Product Demand")
print("-" * 80)

step_time = time.time()

# Set default inv_spending (needed for investment module initialization, not used in employment-only mode)
if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

# Convert to vector (MRIO_df_to_vec now handles invalid indices gracefully)
dy_inv_exog = MRIO_df_to_vec(
    INV_model.dy_inv_exog,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

print(f"OK - Investment converted to product demand")
print(f"OK - Initial final demand (dy): ${dy_inv_exog.sum():,.0f}")
print(f"OK - Time: {round(time.time() - step_time, 1)} seconds")
print()

#==============================================================================
# STEP 4: Calculate Output Changes (Leontief Model)
#==============================================================================
print("-" * 80)
print("STEP 4: Calculating Output Changes (IO Model)")
print("-" * 80)

step_time = time.time()
IO_model = IO(MRIO_BASE)

# Build Leontief inverse if not already loaded
if not hasattr(IO_model, 'L_BASE'):
    print("L_BASE not found, calculating from A matrix...")
    IO_model.build_A_base()  # Build technical coefficients matrix
    IO_model.invert_A_base()  # Calculate L = (I - A)^(-1)
    print(f"OK - L_BASE calculated")

# Apply Leontief inverse: dq = L × dy
dq_total = IO_model.calc_dq_exog(dy_inv_exog)

output_multiplier = dq_total.sum() / dy_inv_exog.sum()
print(f"OK - Total output change (dq): ${dq_total.sum():,.0f}")
print(f"OK - Output multiplier: {output_multiplier:.3f}x")
print(f"OK - Time: {round(time.time() - step_time, 1)} seconds")
print()

#==============================================================================
# STEP 5: Calculate Employment (Direct, Indirect, Total)
#==============================================================================
print("-" * 80)
print("STEP 5: Calculating Employment (Direct vs Indirect)")
print("-" * 80)

step_time = time.time()
Empl_model = empl(MRIO_BASE)

# WORKAROUND: employment.py line 32 sorts using REGIONS_list.index()
# But after merge with HH_CONS_COU, EMPL_COEF contains all countries
# Temporarily expand REGIONS_list to include all countries from HH_CONS_COU
original_regions = Empl_model.REGIONS_list.copy()
all_country_codes = MRIO_BASE.HH_CONS_COU['Country_Code'].unique().tolist()
Empl_model.REGIONS_list = all_country_codes

# Build employment coefficients (this will now work with all countries)
Empl_model.build_empl_coef()

# Filter EMPL_COEF to only our 8 selected regions
Empl_model.EMPL_COEF = Empl_model.EMPL_COEF[
    Empl_model.EMPL_COEF['REG_imp'].isin(original_regions)
].copy()

# Restore original REGIONS_list for consistency
Empl_model.REGIONS_list = original_regions

# DIAGNOSTIC: Check employment coefficient data
print(f"DIAGNOSTIC: EMPL_COEF shape: {Empl_model.EMPL_COEF.shape}")
print(f"DIAGNOSTIC: Unique regions in EMPL_COEF: {Empl_model.EMPL_COEF['REG_imp'].unique().tolist()}")
print(f"DIAGNOSTIC: EMPL_COEF non-zero values: {(Empl_model.EMPL_COEF['empl_coef'] != 0).sum()}")
print(f"DIAGNOSTIC: Sample EMPL_COEF rows:")
print(Empl_model.EMPL_COEF.head(10))
print(f"DIAGNOSTIC: mrio_id length: {len(MRIO_BASE.mrio_id)}")
print(f"DIAGNOSTIC: Unique regions in mrio_id: {MRIO_BASE.mrio_id['REG_imp'].unique().tolist()}")

# Calculate employment multipliers from base data
# Employment coefficients must match the 960-dimension structure (8 countries × 120 sectors)
# Create full employment coefficient array matching mrio_id structure
empl_coef_full = np.zeros(len(MRIO_BASE.mrio_id))

# Map employment coefficients to correct positions
matches = 0
for idx, (reg, sec) in enumerate(zip(MRIO_BASE.mrio_id['REG_imp'], MRIO_BASE.mrio_id['PROD_COMM'])):
    # Find matching employment coefficient
    mask = (Empl_model.EMPL_COEF['REG_imp'] == reg) & (Empl_model.EMPL_COEF['PROD_COMM'] == sec)
    if mask.any():
        empl_coef_full[idx] = Empl_model.EMPL_COEF.loc[mask, 'empl_coef'].values[0]
        matches += 1
    # If no employment data for this region-sector, coefficient remains 0

print(f"DIAGNOSTIC: Matched {matches} out of {len(MRIO_BASE.mrio_id)} positions")
print(f"DIAGNOSTIC: Non-zero coefficients: {(empl_coef_full != 0).sum()}")
print(f"DIAGNOSTIC: Sample empl_coef_full: {empl_coef_full[:20]}")

# Check output changes
print(f"\nDIAGNOSTIC: dq_total non-zero elements: {(dq_total != 0).sum()}")
print(f"DIAGNOSTIC: dq_total sum: ${dq_total.sum():,.0f}")
print(f"DIAGNOSTIC: dy_inv_exog non-zero elements: {(dy_inv_exog != 0).sum()}")
print(f"DIAGNOSTIC: dy_inv_exog sum: ${dy_inv_exog.sum():,.0f}")

# Check which countries have output changes
for i, (reg, sec) in enumerate(zip(MRIO_BASE.mrio_id['REG_imp'][:240], MRIO_BASE.mrio_id['PROD_COMM'][:240])):
    if dq_total[i] != 0:
        print(f"DIAGNOSTIC: dq_total[{i}] = ${dq_total[i]:.2f} for {reg}-{sec}, empl_coef={empl_coef_full[i]}")
        if i > 10:  # Just show first few
            print("...")
            break

Empl_model.empl_multiplier = empl_coef_full

# TOTAL employment (direct + indirect via Leontief)
dempl_total = list(Empl_model.calc_dempl([dq_total]))[0]

# DIRECT employment (first-round effect only)
dempl_direct = list(Empl_model.calc_dempl([dy_inv_exog]))[0]

# INDIRECT employment (supply chain)
dempl_indirect = dempl_total - dempl_direct

total_jobs = dempl_total.sum()
direct_jobs = dempl_direct.sum()
indirect_jobs = dempl_indirect.sum()

employment_multiplier = total_jobs / total_investment * 1e6

print(f"OK - Employment calculated")
print(f"OK - Direct Jobs:   {direct_jobs:>15,.0f}")
print(f"OK - Indirect Jobs: {indirect_jobs:>15,.0f}")
print(f"OK - Total Jobs:    {total_jobs:>15,.0f}")
print(f"OK - Employment Multiplier: {employment_multiplier:.2f} jobs/$1M")
print(f"OK - Time: {round(time.time() - step_time, 1)} seconds")
print()

#==============================================================================
# STEP 6: Format Results
#==============================================================================
print("-" * 80)
print("STEP 6: Formatting Results")
print("-" * 80)

step_time = time.time()

# Build results dataframe
empl_results = pd.concat([
    MRIO_BASE.mrio_list,
    pd.DataFrame({
        'Direct_Jobs': dempl_direct,
        'Indirect_Jobs': dempl_indirect,
        'Total_Jobs': dempl_total
    })
], axis=1)

# Get country name
country_name_lookup = MRIO_BASE.R[MRIO_BASE.R['Region_acronyms'] == TEST_COUNTRY]['Region_names'].values
country_name = country_name_lookup[0] if len(country_name_lookup) > 0 else TEST_COUNTRY

# Employment by region
empl_by_region = empl_results.groupby('Reg_ID').agg({
    'Direct_Jobs': 'sum',
    'Indirect_Jobs': 'sum',
    'Total_Jobs': 'sum'
}).reset_index()

empl_by_region = empl_by_region.merge(
    MRIO_BASE.R[['Region_acronyms', 'Region_names']],
    left_on='Reg_ID',
    right_on='Region_acronyms',
    how='left'
)

empl_by_region = empl_by_region[[
    'Region_acronyms', 'Region_names',
    'Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs'
]]

# Employment by sector
empl_by_sector = empl_results.groupby('Sec_ID').agg({
    'Direct_Jobs': 'sum',
    'Indirect_Jobs': 'sum',
    'Total_Jobs': 'sum'
}).reset_index()

empl_by_sector = empl_by_sector.merge(
    MRIO_BASE.P[['Lfd_Nr', 'Sector_names']],
    left_on='Sec_ID',
    right_on='Lfd_Nr',
    how='left'
)

empl_by_sector = empl_by_sector[[
    'Lfd_Nr', 'Sector_names',
    'Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs'
]]

print(f"OK - Results formatted")
print(f"OK - Time: {round(time.time() - step_time, 1)} seconds")
print()

#==============================================================================
# STEP 7: Display Summary Results
#==============================================================================
print("="*80)
print("TEST RESULTS SUMMARY")
print("="*80)
print()
print(f"Scenario: {scenario_name}")
print(f"Investing Country: {TEST_COUNTRY} ({country_name})")
print()
print(f"Investment:       ${total_investment:>15,.0f}")
print(f"Direct Jobs:      {direct_jobs:>15,.0f}")
print(f"Indirect Jobs:    {indirect_jobs:>15,.0f}")
print(f"Total Jobs:       {total_jobs:>15,.0f}")
print()
print(f"Employment Multiplier: {employment_multiplier:.2f} jobs per $1M invested")
print(f"Output Multiplier:     {output_multiplier:.3f}x")
print()

# Top 10 regions
print("Top 10 Regions by Total Employment:")
print("-" * 80)
top_regions = empl_by_region.nlargest(10, 'Total_Jobs')
for idx, row in top_regions.iterrows():
    print(f"  {row['Region_names']:<35} {row['Total_Jobs']:>12,.0f} jobs")
    print(f"    (Direct: {row['Direct_Jobs']:>10,.0f}, Indirect: {row['Indirect_Jobs']:>10,.0f})")
print()

# Top 10 sectors
print("Top 10 Sectors by Total Employment:")
print("-" * 80)
top_sectors = empl_by_sector.nlargest(10, 'Total_Jobs')
for idx, row in top_sectors.iterrows():
    sector_name = row['Sector_names'][:50]  # Truncate long names
    print(f"  {sector_name:<50} {row['Total_Jobs']:>12,.0f} jobs")
    print(f"    (Direct: {row['Direct_Jobs']:>10,.0f}, Indirect: {row['Indirect_Jobs']:>10,.0f})")
print()

#==============================================================================
# STEP 8: Save Test Results
#==============================================================================
print("-" * 80)
print("STEP 8: Saving Test Results")
print("-" * 80)

output_dir = os.path.join(os.getcwd(), "GLORIA_results")
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, f"TEST_{scenario_name}_Results.xlsx")

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Summary
    summary = pd.DataFrame({
        'Metric': [
            'Scenario',
            'Strategy',
            'Country',
            'Country Name',
            'Total Investment (USD)',
            'Direct Jobs',
            'Indirect Jobs',
            'Total Jobs',
            'Employment Multiplier (jobs/$1M)',
            'Output Multiplier',
            'Direct/Total Ratio',
            'Indirect/Total Ratio'
        ],
        'Value': [
            scenario_name,
            TEST_STRATEGY,
            TEST_COUNTRY,
            country_name,
            f"${total_investment:,.0f}",
            f"{direct_jobs:,.0f}",
            f"{indirect_jobs:,.0f}",
            f"{total_jobs:,.0f}",
            f"{employment_multiplier:.2f}",
            f"{output_multiplier:.3f}",
            f"{direct_jobs/total_jobs:.3f}",
            f"{indirect_jobs/total_jobs:.3f}"
        ]
    })
    summary.to_excel(writer, sheet_name='Summary', index=False)

    # Employment by region
    empl_by_region.to_excel(writer, sheet_name='Employment_by_Region', index=False)

    # Employment by sector
    empl_by_sector.to_excel(writer, sheet_name='Employment_by_Sector', index=False)

print(f"OK - Results saved to:")
print(f"     {output_file}")
print()

#==============================================================================
# VALIDATION CHECKS
#==============================================================================
print("="*80)
print("VALIDATION CHECKS")
print("="*80)
print()

# Check 1: No negative values
negative_direct = (dempl_direct < 0).sum()
negative_indirect = (dempl_indirect < 0).sum()
negative_total = (dempl_total < 0).sum()
print(f"1. Negative values: Direct={negative_direct}, Indirect={negative_indirect}, Total={negative_total}")
if negative_direct == 0 and negative_indirect == 0 and negative_total == 0:
    print("   OK - No negative values found")
else:
    print("   WARNING - Found negative values!")
print()

# Check 2: Direct + Indirect = Total
sum_check = abs((dempl_direct + dempl_indirect - dempl_total).sum())
print(f"2. Direct + Indirect = Total?")
print(f"   Error: {sum_check:.10f} (should be ~0)")
if sum_check < 0.01:
    print("   OK - Sum is correct")
else:
    print("   WARNING - Sum mismatch!")
print()

# Check 3: Multiplier range
print(f"3. Employment multiplier: {employment_multiplier:.2f} jobs/$1M")
if 5 <= employment_multiplier <= 50:
    print("   OK - Within typical range (5-50)")
else:
    print("   WARNING - Outside typical range!")
print()

# Check 4: Output multiplier
print(f"4. Output multiplier: {output_multiplier:.3f}")
if output_multiplier > 1.0:
    print("   OK - Greater than 1.0 (as expected)")
else:
    print("   WARNING - Should be greater than 1.0!")
print()

# Check 5: Direct < Total
print(f"5. Direct jobs ({direct_jobs:,.0f}) < Total jobs ({total_jobs:,.0f})?")
if direct_jobs < total_jobs:
    print("   OK - Direct is less than Total")
else:
    print("   WARNING - Direct should be less than Total!")
print()

#==============================================================================
# FINAL VERDICT
#==============================================================================
print("="*80)
print("TEST COMPLETE!")
print("="*80)
print()

all_checks_pass = (
    negative_direct == 0 and
    negative_indirect == 0 and
    negative_total == 0 and
    sum_check < 0.01 and
    5 <= employment_multiplier <= 50 and
    output_multiplier > 1.0 and
    direct_jobs < total_jobs
)

if all_checks_pass:
    print("STATUS: ALL CHECKS PASSED")
    print()
    print("Ready to run full batch processing (469 scenarios)!")
    print("Run: python RunMINDSET_EmploymentOnly_BATCH_FINAL.py")
else:
    print("STATUS: SOME CHECKS FAILED")
    print()
    print("Please review the warnings above before running full batch.")

print()
print("="*80)
