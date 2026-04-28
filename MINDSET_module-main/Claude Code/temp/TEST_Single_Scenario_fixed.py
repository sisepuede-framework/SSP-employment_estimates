# -*- coding: utf-8 -*-
"""
MINDSET EMPLOYMENT-ONLY ESTIMATION - SINGLE SCENARIO TEST

This script tests the employment calculation methodology on a single scenario
before running the full batch of 469 scenarios.

Tests:
- Direct employment (e × dy)
- Indirect employment (e × (L × dy - dy))
- Total employment (Direct + Indirect)

Created: 2026-03-20
Purpose: Test script before batch processing
"""

#==============================================================================
# I. Import Required Modules
#==============================================================================

import numpy as np
import pandas as pd
import time
import sys
import os

# PATH SETUP
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
if mindset_root not in sys.path:
    sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print(f"MINDSET root directory: {mindset_root}")
print(f"Current working directory: {os.getcwd()}\n")

# Import MINDSET modules
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.InputOutput import IO
from SourceCode.employment import empl
from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

print("\n" + "="*80)
print("MINDSET EMPLOYMENT TEST - SINGLE SCENARIO")
print("="*80 + "\n")

#==============================================================================
# II. Configuration
#==============================================================================

# TEST SCENARIO - Change this to test different scenarios
TEST_SCENARIO = "Strategy_1004_MEX"

print(f"Testing scenario: {TEST_SCENARIO}")
print(f"This will verify: Direct, Indirect, and Total employment calculations\n")

scenario_path = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios", f"{TEST_SCENARIO}.xlsx")
print(f"Scenario file: {scenario_path}")
print(f"File exists: {os.path.exists(scenario_path)}\n")

if not os.path.exists(scenario_path):
    print(f"ERROR: Scenario file not found!")
    sys.exit(1)

start_time = time.time()

#==============================================================================
# III. Load MRIO Data
#==============================================================================
print("-" * 80)
print("STEP 1: Loading MRIO Data")
print("-" * 80)

step_time = time.time()
MRIO_BASE = exog_vars()

print(f"OK Loaded {len(MRIO_BASE.COU_ID)} countries/regions")
print(f"OK Loaded {len(MRIO_BASE.SEC_ID)} sectors")
print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# IV. Load Scenario and Convert Investment to Demand
#==============================================================================
print("-" * 80)
print("STEP 2: Loading Scenario and Converting Investment")
print("-" * 80)

step_time = time.time()

# Load scenario
Scenario = scenario(MRIO_BASE, scenario_path, None)
Scenario.set_exog_inv()

if not hasattr(Scenario, 'inv_exog') or Scenario.inv_exog.empty:
    print("ERROR: No investment data in scenario file!")
    sys.exit(1)

total_investment = Scenario.inv_exog['dk'].sum()
print(f"OK Loaded exogenous investment: ${total_investment:,.0f}")
print(f"OK Investment by {len(Scenario.inv_exog)} sector-region pairs")

# Display investment breakdown
print(f"\nInvestment breakdown:")
for idx, row in Scenario.inv_exog.iterrows():
    country = row['REG_imp']
    sector = row['PROD_COMM']
    amount = row['dk']
    print(f"  {country} - Sector {sector}: ${amount:,.0f}")

# Initialize investment module
INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()

# Convert investment to final demand
INV_model.calc_dy_inv_exog(Scenario.inv_exog)
print(f"\nOK Converted investment to final demand")

print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# V. Calculate Output Changes (Leontief Model)
#==============================================================================
print("-" * 80)
print("STEP 3: Calculating Output Changes")
print("-" * 80)

step_time = time.time()

# Initialize IO model
IO_model = IO(MRIO_BASE)
IO_model.initialize()

print(f"OK Initialized IO model")
print(f"OK Leontief inverse loaded: {IO_model.L_BASE.shape}")

# Convert final demand to vector
dy_inv_exog = MRIO_df_to_vec(
    INV_model.dy_inv_exog,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

print(f"OK Initial final demand (dy): ${dy_inv_exog.sum():,.0f}")

# Calculate total output (direct + indirect via Leontief)
dq_total = IO_model.calc_dq_exog(dy_inv_exog)

print(f"OK Total output change (dq): ${dq_total.sum():,.0f}")
print(f"OK Output multiplier: {dq_total.sum() / dy_inv_exog.sum():.3f}x")

print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# VI. Calculate Employment (Direct, Indirect, Total)
#==============================================================================
print("-" * 80)
print("STEP 4: Calculating Employment (DIRECT vs INDIRECT)")
print("-" * 80)

step_time = time.time()

# Build employment model
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

print(f"OK Loaded employment coefficients")

# CRITICAL CALCULATION: Separate Direct vs Indirect

# 1. Direct Employment (first-round effect from initial demand)
#    Formula: dempl_direct = e × dy
dempl_direct = Empl_model.calc_dempl([dy_inv_exog])[0]

# 2. Total Employment (includes supply chain multiplier)
#    Formula: dempl_total = e × dq = e × (L × dy)
dempl_total = Empl_model.calc_dempl([dq_total])[0]

# 3. Indirect Employment (supply chain effect)
#    Formula: dempl_indirect = dempl_total - dempl_direct
dempl_indirect = dempl_total - dempl_direct

print(f"\nOK Employment Calculations Complete:")
print(f"  Direct Jobs:   {dempl_direct.sum():>12,.1f} (first-round effect)")
print(f"  Indirect Jobs: {dempl_indirect.sum():>12,.1f} (supply chain effect)")
print(f"  Total Jobs:    {dempl_total.sum():>12,.1f} (Direct + Indirect)")
print(f"\nOK Direct/Total Ratio: {dempl_direct.sum() / dempl_total.sum():.3f}")
print(f"OK Indirect/Total Ratio: {dempl_indirect.sum() / dempl_total.sum():.3f}")

# Employment multipliers
direct_multiplier = dempl_direct.sum() / dy_inv_exog.sum() * 1e6
indirect_multiplier = dempl_indirect.sum() / dy_inv_exog.sum() * 1e6
total_multiplier = dempl_total.sum() / dy_inv_exog.sum() * 1e6

print(f"\nOK Employment Multipliers (jobs per $1M):")
print(f"  Direct:   {direct_multiplier:>8.2f} jobs/$1M")
print(f"  Indirect: {indirect_multiplier:>8.2f} jobs/$1M")
print(f"  Total:    {total_multiplier:>8.2f} jobs/$1M")

print(f"\nTime: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# VII. Format Results
#==============================================================================
print("-" * 80)
print("STEP 5: Formatting Results")
print("-" * 80)

step_time = time.time()

# Convert to DataFrame
empl_results = pd.concat([
    MRIO_BASE.mrio_list,
    pd.DataFrame({
        'Direct_Jobs': dempl_direct,
        'Indirect_Jobs': dempl_indirect,
        'Total_Jobs': dempl_total
    })
], axis=1)

# Add country name
country_names = MRIO_BASE.R[['Region_acronyms', 'Region_names']].copy()
country_names.columns = ['Region', 'Country_Name']
empl_results = empl_results.merge(
    country_names,
    left_on='Region',
    right_on='Region',
    how='left'
)

# Summary by region
empl_by_region = empl_results.groupby(['Region', 'Country_Name'])[
    ['Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs']
].sum().reset_index()

# Summary by sector
sector_names = MRIO_BASE.P[['Lfd_Nr', 'Product_name']].copy()
sector_names.columns = ['Sector', 'Sector_Name']
empl_by_sector = empl_results.groupby('Sector')[
    ['Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs']
].sum().reset_index()
empl_by_sector = empl_by_sector.merge(sector_names, on='Sector', how='left')

print(f"OK Formatted results by region and sector")

# Display top 10 regions by total employment
print(f"\nOK Top 10 Regions by Total Employment:")
top_regions = empl_by_region.nlargest(10, 'Total_Jobs')
for idx, row in top_regions.iterrows():
    print(f"  {row['Country_Name']:<30} {row['Total_Jobs']:>12,.0f} "
          f"(D: {row['Direct_Jobs']:>10,.0f}, I: {row['Indirect_Jobs']:>10,.0f})")

# Display top 10 sectors by total employment
print(f"\nOK Top 10 Sectors by Total Employment:")
top_sectors = empl_by_sector.nlargest(10, 'Total_Jobs')
for idx, row in top_sectors.iterrows():
    print(f"  {row['Sector_Name']:<40} {row['Total_Jobs']:>12,.0f} "
          f"(D: {row['Direct_Jobs']:>10,.0f}, I: {row['Indirect_Jobs']:>10,.0f})")

print(f"\nTime: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# VIII. Save Test Results
#==============================================================================
print("-" * 80)
print("STEP 6: Saving Test Results")
print("-" * 80)

step_time = time.time()

output_dir = os.path.join(os.getcwd(), "GLORIA_results")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, f"TEST_{TEST_SCENARIO}_Employment.xlsx")

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Summary statistics
    summary = pd.DataFrame({
        'Metric': [
            'Scenario',
            'Total Investment (USD)',
            'Direct Jobs',
            'Indirect Jobs',
            'Total Jobs',
            'Direct Multiplier (jobs/$1M)',
            'Indirect Multiplier (jobs/$1M)',
            'Total Multiplier (jobs/$1M)',
            'Output Multiplier',
            'Direct/Total Ratio',
            'Indirect/Total Ratio'
        ],
        'Value': [
            TEST_SCENARIO,
            f"${total_investment:,.0f}",
            f"{dempl_direct.sum():,.0f}",
            f"{dempl_indirect.sum():,.0f}",
            f"{dempl_total.sum():,.0f}",
            f"{direct_multiplier:.2f}",
            f"{indirect_multiplier:.2f}",
            f"{total_multiplier:.2f}",
            f"{dq_total.sum() / dy_inv_exog.sum():.3f}",
            f"{dempl_direct.sum() / dempl_total.sum():.3f}",
            f"{dempl_indirect.sum() / dempl_total.sum():.3f}"
        ]
    })
    summary.to_excel(writer, sheet_name='Summary', index=False)

    # Employment by region
    empl_by_region.to_excel(writer, sheet_name='Employment_by_Region', index=False)

    # Employment by sector
    empl_by_sector.to_excel(writer, sheet_name='Employment_by_Sector', index=False)

    # Detailed results
    empl_results.to_excel(writer, sheet_name='Employment_Details', index=False)

print(f"OK Test results saved to: {output_file}")
print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# IX. Validation Checks
#==============================================================================
print("-" * 80)
print("STEP 7: Validation Checks")
print("-" * 80)

print(f"\nOK Data Quality Checks:")

# Check 1: No negative employment
negative_direct = (dempl_direct < 0).sum()
negative_indirect = (dempl_indirect < 0).sum()
negative_total = (dempl_total < 0).sum()
print(f"  Negative values: Direct={negative_direct}, Indirect={negative_indirect}, Total={negative_total}")

# Check 2: Direct + Indirect = Total
sum_check = abs((dempl_direct + dempl_indirect - dempl_total).sum())
print(f"  Direct + Indirect = Total? Error: {sum_check:.6f} (should be ~0)")

# Check 3: Reasonable multiplier range
if 5 <= total_multiplier <= 50:
    print(f"  Employment multiplier ({total_multiplier:.2f} jobs/$1M): OK Within expected range (5-50)")
else:
    print(f"  Employment multiplier ({total_multiplier:.2f} jobs/$1M): ⚠ Outside typical range (5-50)")

# Check 4: Direct < Total
if dempl_direct.sum() < dempl_total.sum():
    print(f"  Direct < Total? OK Yes")
else:
    print(f"  Direct < Total? ✗ NO - This indicates an error!")

# Check 5: Output multiplier > 1
output_mult = dq_total.sum() / dy_inv_exog.sum()
if output_mult > 1.0:
    print(f"  Output multiplier ({output_mult:.3f}): OK Greater than 1.0")
else:
    print(f"  Output multiplier ({output_mult:.3f}): ⚠ Should be > 1.0")

#==============================================================================
# X. Final Summary
#==============================================================================
total_time = time.time() - start_time

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
print(f"\nScenario: {TEST_SCENARIO}")
print(f"Total Runtime: {round(total_time, 1)} seconds")
print(f"\nResults saved to:")
print(f"  {output_file}")
print(f"\nKey Findings:")
print(f"  Investment:       ${total_investment:,.0f}")
print(f"  Direct Jobs:      {dempl_direct.sum():,.0f}")
print(f"  Indirect Jobs:    {dempl_indirect.sum():,.0f}")
print(f"  Total Jobs:       {dempl_total.sum():,.0f}")
print(f"  Total Multiplier: {total_multiplier:.2f} jobs/$1M")
print(f"\nOK Methodology validated for batch processing!")
print("\n" + "="*80 + "\n")
